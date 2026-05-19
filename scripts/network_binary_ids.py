"""
network_binary_ids.py — Real-time binary IDS for VIM 4.

Captures live traffic via netflower's capture_live, emitting each flow the
moment it completes (TCP FIN/RST or idle timeout), and runs a pre-trained
sklearn binary classifier to flag attack traffic.

Classification mode: binary  (benign vs. attack)
Model format:        scikit-learn pipeline saved as .pkl (joblib)
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

from constants.features import ALL_EXCLUDED_FEATURES, EXCLUDED_FEATURES, FINAL_FEATURES
from constants.labels import ALL_LABELS, BENIGN_LABELS, MALICIOUS_LABELS

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

# Minimum probability assigned to the attack class to raise an alert.
# Optimised by Optuna; auto-updated by notebooks/training.ipynb.
THRESHOLD = 0.9

# When True, logs all flow features on every alert — useful for debugging but
# very noisy in production.  Set to True via env var VERBOSE_ALERTS=1 or edit
# this constant directly.
VERBOSE_ALERTS = os.environ.get("VERBOSE_ALERTS", "0") == "1"

# Input features expected by the model: everything in the final feature set
# except the target column.  At runtime this is overridden by the model's own
# feature_names_in_ attribute when available, which is more reliable.
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
_stats = {"flows": 0, "alerts": 0, "total_inference_ms": 0.0, "max_inference_ms": 0.0}

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
    _report_path = os.path.join(REPORT_DIR, f"ids_run_{ts}.md")
    dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header_cols = " | ".join(_ALERT_COLS)
    sep_cols = " | ".join("---" for _ in _ALERT_COLS)
    _report_append(
        f"# IDS Run — {dt_str}\n\n"
        f"## Configuration\n\n"
        f"| Parameter | Value |\n"
        f"|-----------|-------|\n"
        f"| Interface | `{INTERFACE}` |\n"
        f"| Model | `{MODEL_PATH}` |\n"
        f"| Threshold | `{THRESHOLD}` |\n"
        f"| Idle timeout | `{IDLE_TIMEOUT}` s |\n"
        f"| Flow timeout | `{FLOW_TIMEOUT}` s |\n\n"
        f"## Model Info\n\n"
        f"| Property | Value |\n"
        f"|----------|-------|\n"
        f"| Classes | `{list(model.classes_)}` |\n"
        f"| Attack class index | `{attack_idx}` |\n"
        f"| Input features | `{len(input_features)}` |\n\n"
        f"## Alerts\n\n"
        f"| Detection time | Confidence | {header_cols} |\n"
        f"|----------------|------------|{sep_cols}|\n"
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
        f"\n## Runtime Summary\n\n"
        f"| Metric | Value |\n"
        f"|--------|-------|\n"
        f"| End time | `{dt_str}` |\n"
        f"| Duration | `{h:02d}:{m:02d}:{s:02d}` |\n"
        f"| Flows processed | `{flows:,}` |\n"
        f"| Alerts raised | `{alerts:,}` |\n"
        f"| Avg inference time | `{avg_ms:.2f} ms` |\n"
        f"| Max inference time | `{max_ms:.2f} ms` |\n\n"
        f"*Generated by `scripts/network_binary_ids.py`*\n"
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
        log.info("[STATS] Flows: %d | Alerts: %d | Inference avg %.2f ms | max %.2f ms",
                 flows, alerts, avg_ms, max_ms)


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_model(path: str):
    """Load the binary sklearn classifier from a .pkl file (joblib format)."""
    if not os.path.exists(path):
        log.error("Model file not found: %s", path)
        sys.exit(1)

    model = joblib.load(path)
    log.info("Model loaded from %s", path)
    log.info("Classes: %s", list(model.classes_))
    return model


def get_input_features(model) -> list[str]:
    """
    Return the ordered feature list the model was trained on.

    Prefers model.feature_names_in_ (set automatically when the model is fit
    on a DataFrame) over the project-level constant, so the script stays
    consistent with the training pipeline even if constants.py drifts.
    """
    if hasattr(model, "feature_names_in_"):
        return list(model.feature_names_in_)
    log.warning(
        "Model has no feature_names_in_; falling back to FINAL_FEATURES from constants."
    )
    return _FALLBACK_INPUT_FEATURES


def get_attack_class_index(model) -> int:
    """
    Return the column index in predict_proba output that corresponds to an
    attack class (i.e. any class not listed in BENIGN_LABELS).

    Works regardless of whether the model uses string labels ("benign", "attack")
    or integer labels (0, 1).
    """
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
    """Return an on_flow callback bound to the loaded model."""

    def on_flow(flow: dict) -> None:
        with _stats_lock:
            _stats["flows"] += 1

        try:
            df = pd.DataFrame([flow])

            # Align dataframe to the exact feature set the model expects.
            # Columns present in input_features but missing from the flow dict
            # are filled with 0 — can happen for short or incomplete flows.
            missing_cols = [c for c in input_features if c not in df.columns]
            if missing_cols:
                log.debug("Filling %d missing feature column(s) with 0: %s", len(missing_cols), missing_cols)
                for col in missing_cols:
                    df[col] = 0

            X = df[input_features]

            # predict_proba returns shape (1, n_classes);
            # attack_idx selects the attack-class column.
            t0 = time.perf_counter()
            prob = model.predict_proba(X)[0, attack_idx]
            inference_ms = (time.perf_counter() - t0) * 1000

            with _stats_lock:
                _stats["total_inference_ms"] += inference_ms
                if inference_ms > _stats["max_inference_ms"]:
                    _stats["max_inference_ms"] = inference_ms

            if prob >= THRESHOLD:
                with _stats_lock:
                    _stats["alerts"] += 1
                row = pd.Series(flow)
                if VERBOSE_ALERTS:
                    log.warning("[ALERT] Attack detected — confidence %.1f%% | inference %.2f ms\n%s",
                                prob * 100, inference_ms, row.to_string())
                else:
                    log.warning("[ALERT] Attack detected — confidence %.1f%% | inference %.2f ms",
                                prob * 100, inference_ms)
                _alert_cols_vals = " | ".join(
                    str(row.get(c, "—")) if not isinstance(row.get(c), float)
                    else f"{row.get(c):.4g}"
                    for c in _ALERT_COLS
                )
                _report_append(
                    f"| {datetime.datetime.now().strftime('%H:%M:%S')} "
                    f"| {prob:.1%} "
                    f"| {_alert_cols_vals} |\n"
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

    log.info("Watching interface %s | threshold %.0f%% | idle timeout %.0fs",
             INTERFACE, THRESHOLD * 100, IDLE_TIMEOUT)

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
