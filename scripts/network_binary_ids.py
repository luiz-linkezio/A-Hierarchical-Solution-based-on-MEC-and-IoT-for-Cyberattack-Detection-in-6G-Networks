"""
network_binary_ids.py — Real-time Phase-1-only binary IDS for VIM 4.

Captures live traffic via netflower's capture_live, emitting each flow the
moment it completes (TCP FIN/RST or idle timeout), and runs a pre-trained
sklearn binary classifier per flow:

  Phase 1 — Binary classifier: benign vs. attack

Model format: scikit-learn pipeline saved as .pkl (joblib)
"""

import datetime
import logging
import os
import sys
import threading
import time

import joblib
import pandas as pd
from netflower import capture_live

# Allow importing from the project root (constants package)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from constants.features import FINAL_FEATURES
from constants.labels import BENIGN_LABELS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INTERFACE = "eth0"

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "binary_classifier_20260518_130014.pkl")

REPORT_DIR = os.path.join(os.path.dirname(__file__), "docs", "results")

# Seconds of inactivity before a flow is forcibly emitted.
IDLE_TIMEOUT = 30.0

# Absolute maximum flow duration before forced emit.
FLOW_TIMEOUT = 120.0

# Minimum probability assigned to the attack class to raise a Phase 1 alert.
# Optimised by Optuna; auto-updated by notebooks/training.ipynb.
THRESHOLD = 0.9

# When True, logs all flow features on every alert.
VERBOSE_ALERTS = os.environ.get("VERBOSE_ALERTS", "0") == "1"

_FALLBACK_INPUT_FEATURES = [f for f in FINAL_FEATURES if f != "label"]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

_stats_lock = threading.Lock()
_stats = {
    "flows": 0,
    "alerts": 0,
    "total_inference_ms": 0.0,
    "max_inference_ms": 0.0,
}

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

_report_path: str = ""
_run_start: float = 0.0

_ALERT_COLS = ["src_ip", "dst_ip", "src_port", "dst_port", "protocol",
               "flow_byts_s", "flow_pkts_s", "flow_duration"]


def _report_append(text: str) -> None:
    if _report_path:
        with open(_report_path, "a") as _f:
            _f.write(text)


def _init_report(model, input_features: list[str], attack_idx: int) -> None:
    global _report_path, _run_start
    _run_start = time.time()
    os.makedirs(REPORT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    _report_path = os.path.join(REPORT_DIR, f"binary_ids_run_{ts}.log")
    dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _report_append(
        f"=== Binary IDS Run — {dt_str} ===\n\n"
        f"[CONFIG]\n"
        f"interface            = {INTERFACE}\n"
        f"model                = {MODEL_PATH}\n"
        f"threshold            = {THRESHOLD}\n"
        f"idle_timeout         = {IDLE_TIMEOUT} s\n"
        f"flow_timeout         = {FLOW_TIMEOUT} s\n\n"
        f"[MODEL]\n"
        f"classes              = {list(model.classes_)}\n"
        f"attack_idx           = {attack_idx}\n"
        f"input_features       = {len(input_features)}\n\n"
        f"[ALERTS]\n"
        f"# timestamp\tp1_conf\t" + "\t".join(_ALERT_COLS) + "\n"
    )
    log.info("Report initialized → %s", _report_path)


def _finalize_report() -> None:
    elapsed = time.time() - _run_start
    h, rem = divmod(int(elapsed), 3600)
    m, s = divmod(rem, 60)
    with _stats_lock:
        flows = _stats["flows"]
        alerts = _stats["alerts"]
        avg_ms = _stats["total_inference_ms"] / flows if flows else 0.0
        max_ms = _stats["max_inference_ms"]
    dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _report_append(
        f"\n[SUMMARY]\n"
        f"end_time             = {dt_str}\n"
        f"duration             = {h:02d}:{m:02d}:{s:02d}\n"
        f"flows_processed      = {flows:,}\n"
        f"alerts_raised        = {alerts:,}\n"
        f"avg_inference_ms     = {avg_ms:.2f}\n"
        f"max_inference_ms     = {max_ms:.2f}\n"
    )
    log.info("Report finalized → %s", _report_path)


# ---------------------------------------------------------------------------
# Stats printer
# ---------------------------------------------------------------------------

def _stats_printer(stop_event: threading.Event) -> None:
    while not stop_event.wait(3.0):
        with _stats_lock:
            flows = _stats["flows"]
            alerts = _stats["alerts"]
            avg_ms = _stats["total_inference_ms"] / flows if flows else 0.0
            max_ms = _stats["max_inference_ms"]
        log.info(
            "[STATS] Flows: %d | Alerts: %d | avg %.2f ms max %.2f ms",
            flows, alerts, avg_ms, max_ms,
        )


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_model(path: str):
    if not os.path.exists(path):
        log.error("Model file not found: %s", path)
        sys.exit(1)
    model = joblib.load(path)
    log.info("Model loaded from %s", path)
    log.info("Classes: %s", list(model.classes_))
    return model


def get_input_features(model) -> list[str]:
    if hasattr(model, "feature_names_in_"):
        return list(model.feature_names_in_)
    log.warning("Model has no feature_names_in_; falling back to FINAL_FEATURES from constants.")
    return _FALLBACK_INPUT_FEATURES


def get_attack_class_index(model) -> int:
    benign_set = {str(l) for l in BENIGN_LABELS}
    attack_indices = [
        i for i, c in enumerate(model.classes_) if str(c) not in benign_set
    ]
    if not attack_indices:
        log.error("Could not identify an attack class among model classes: %s", list(model.classes_))
        sys.exit(1)
    return attack_indices[0]


# ---------------------------------------------------------------------------
# Per-flow inference
# ---------------------------------------------------------------------------

def make_flow_handler(model, input_features: list[str], attack_idx: int):
    def _align(df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
        missing = [c for c in features if c not in df.columns]
        if missing:
            log.debug("Filling %d missing feature column(s) with 0: %s", len(missing), missing)
            for col in missing:
                df[col] = 0
        return df[features]

    def on_flow(flow: dict) -> None:
        with _stats_lock:
            _stats["flows"] += 1

        try:
            df = pd.DataFrame([flow])
            X = _align(df.copy(), input_features)

            t0 = time.perf_counter()
            prob = model.predict_proba(X)[0, attack_idx]
            p1_ms = (time.perf_counter() - t0) * 1000

            with _stats_lock:
                _stats["total_inference_ms"] += p1_ms
                if p1_ms > _stats["max_inference_ms"]:
                    _stats["max_inference_ms"] = p1_ms

            if prob < THRESHOLD:
                return

            with _stats_lock:
                _stats["alerts"] += 1

            row = pd.Series(flow)
            if VERBOSE_ALERTS:
                log.warning(
                    "[ALERT] Attack detected — conf %.1f%% | %.2f ms\n%s",
                    prob * 100, p1_ms, row.to_string(),
                )
            else:
                log.warning(
                    "[ALERT] Attack detected — conf %.1f%% | %.2f ms",
                    prob * 100, p1_ms,
                )

            cols_tsv = "\t".join(
                str(row.get(c, "")) if not isinstance(row.get(c), float)
                else f"{row.get(c):.4g}"
                for c in _ALERT_COLS
            )
            _report_append(
                f"{datetime.datetime.now().strftime('%H:%M:%S')}\t"
                f"{prob:.1%}\t"
                f"{cols_tsv}\n"
            )

        except Exception as e:
            log.error("Inference failed on flow: %s", e)

    return on_flow


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    model = load_model(MODEL_PATH)
    input_features = get_input_features(model)
    attack_idx = get_attack_class_index(model)

    log.info(
        "Watching interface %s | threshold %.0f%% | idle timeout %.0fs",
        INTERFACE, THRESHOLD * 100, IDLE_TIMEOUT,
    )

    _init_report(model, input_features, attack_idx)

    on_flow = make_flow_handler(model, input_features, attack_idx)

    stop_printer = threading.Event()
    printer_thread = threading.Thread(target=_stats_printer, args=(stop_printer,), daemon=True)
    printer_thread.start()

    handle = capture_live(
        INTERFACE,
        on_flow=on_flow,
        idle_timeout=IDLE_TIMEOUT,
        flow_timeout=FLOW_TIMEOUT,
    )
    try:
        handle.start()
        log.info("Live capture started.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        handle.stop()
        log.info("Interrupted — stopping capture.")
        stop_printer.set()
        printer_thread.join(timeout=3)
        _finalize_report()


if __name__ == "__main__":
    main()
