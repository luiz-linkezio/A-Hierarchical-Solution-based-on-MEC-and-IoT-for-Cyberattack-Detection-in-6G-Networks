"""
network_binary_ids.py — Real-time two-phase hierarchical IDS for VIM 4.

Captures live traffic via netflower's capture_live, emitting each flow the
moment it completes (TCP FIN/RST or idle timeout), and runs two pre-trained
sklearn classifiers in sequence per flagged flow:

  Phase 1 — Binary classifier:    benign vs. attack
  Phase 2 — Multi-class classifier: attack type (ddos, dos, malware, …)
             Flows whose max Phase-2 probability falls below
             PHASE2_CONFIDENCE_THRESHOLD are marked as low-confidence
             candidates for Phase 3 (clustering / zero-day detection),
             which is not yet implemented in the real-time script.

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

from constants.features import ALL_EXCLUDED_FEATURES, EXCLUDED_FEATURES, FINAL_FEATURES
from constants.labels import ALL_LABELS, BENIGN_LABELS, MALICIOUS_LABELS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INTERFACE = "eth0"

# Phase 1 — Binary classifier (benign vs. attack)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "binary_classifier_20260518_130014.pkl")

# Phase 2 — Multi-class classifier (attack type)
# Auto-updated by notebooks/training.ipynb after each training run.
P2_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "multiclass_classifier_20260518_130014.pkl")

REPORT_DIR = os.path.join(os.path.dirname(__file__), "docs", "results")

# Seconds of inactivity before a flow is forcibly emitted.
IDLE_TIMEOUT = 30.0

# Absolute maximum flow duration before forced emit.
FLOW_TIMEOUT = 120.0

# Minimum probability assigned to the attack class to raise a Phase 1 alert.
# Optimised by Optuna; auto-updated by notebooks/training.ipynb.
THRESHOLD = 0.9

# Phase 2 flows whose max predicted probability is below this value are
# considered low-confidence and marked as candidates for Phase 3 (clustering).
# Lowered from 0.6 to 0.4 to route only genuinely ambiguous flows.
PHASE2_CONFIDENCE_THRESHOLD = 0.4

# When True, logs all flow features on every alert — useful for debugging but
# very noisy in production.  Set to True via env var VERBOSE_ALERTS=1 or edit
# this constant directly.
VERBOSE_ALERTS = os.environ.get("VERBOSE_ALERTS", "0") == "1"

# Input features expected by the models: everything in the final feature set
# except the target column.  At runtime this is overridden by each model's own
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
_stats = {
    "flows": 0,
    "alerts": 0,
    # Phase 1 inference timing
    "total_inference_ms": 0.0,
    "max_inference_ms": 0.0,
    # Phase 2 inference timing
    "p2_total_inference_ms": 0.0,
    "p2_max_inference_ms": 0.0,
    # Phase 2 classification counts per label
    "p2_classifications": {},
    # Flows forwarded to Phase 3 (low Phase-2 confidence)
    "p2_low_confidence": 0,
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


def _init_report(model, input_features: list[str], attack_idx: int,
                 model_p2, p2_input_features: list[str]) -> None:
    global _report_path, _run_start
    _run_start = time.time()
    os.makedirs(REPORT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    _report_path = os.path.join(REPORT_DIR, f"ids_run_{ts}.log")
    dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _report_append(
        f"=== IDS Run — {dt_str} ===\n\n"
        f"[CONFIG]\n"
        f"interface            = {INTERFACE}\n"
        f"p1_model             = {MODEL_PATH}\n"
        f"p2_model             = {P2_MODEL_PATH}\n"
        f"p1_threshold         = {THRESHOLD}\n"
        f"p2_confidence_thresh = {PHASE2_CONFIDENCE_THRESHOLD}\n"
        f"idle_timeout         = {IDLE_TIMEOUT} s\n"
        f"flow_timeout         = {FLOW_TIMEOUT} s\n\n"
        f"[MODEL]\n"
        f"p1_classes           = {list(model.classes_)}\n"
        f"p1_attack_idx        = {attack_idx}\n"
        f"p1_input_features    = {len(input_features)}\n"
        f"p2_classes           = {list(model_p2.classes_)}\n"
        f"p2_input_features    = {len(p2_input_features)}\n\n"
        f"[ALERTS]\n"
        f"# timestamp\tp1_conf\tp2_label\tp2_conf\t"
        + "\t".join(_ALERT_COLS) + "\n"
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
        p2_avg_ms = _stats["p2_total_inference_ms"] / alerts if alerts else 0.0
        p2_max_ms = _stats["p2_max_inference_ms"]
        p2_classifications = dict(_stats["p2_classifications"])
        p2_low_conf = _stats["p2_low_confidence"]
    dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    p2_breakdown = ""
    if p2_classifications:
        rows = "\n".join(
            f"  {label:<20} {count:,}"
            for label, count in sorted(p2_classifications.items(), key=lambda x: -x[1])
        )
        p2_breakdown = (
            f"\n[P2_BREAKDOWN]\n"
            f"{rows}\n"
            f"  {'low_confidence->p3':<20} {p2_low_conf:,}\n"
        )

    _report_append(
        f"\n[SUMMARY]\n"
        f"end_time             = {dt_str}\n"
        f"duration             = {h:02d}:{m:02d}:{s:02d}\n"
        f"flows_processed      = {flows:,}\n"
        f"alerts_raised        = {alerts:,}\n"
        f"p1_avg_inference_ms  = {avg_ms:.2f}\n"
        f"p1_max_inference_ms  = {max_ms:.2f}\n"
        f"p2_avg_inference_ms  = {p2_avg_ms:.2f}\n"
        f"p2_max_inference_ms  = {p2_max_ms:.2f}\n"
        f"p2_low_confidence    = {p2_low_conf:,}\n"
        f"{p2_breakdown}"
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
            p2_avg_ms = _stats["p2_total_inference_ms"] / alerts if alerts else 0.0
            p2_max_ms = _stats["p2_max_inference_ms"]
            p2_low_conf = _stats["p2_low_confidence"]
        log.info(
            "[STATS] Flows: %d | Alerts: %d | "
            "P1 avg %.2f ms max %.2f ms | "
            "P2 avg %.2f ms max %.2f ms | P2 low-conf: %d",
            flows, alerts, avg_ms, max_ms, p2_avg_ms, p2_max_ms, p2_low_conf,
        )


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

def make_flow_handler(model, input_features: list[str], attack_idx: int,
                      model_p2, p2_input_features: list[str]):
    """Return an on_flow callback that runs Phase 1 → Phase 2 in sequence."""

    def _align(df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
        """Fill any feature columns missing from the flow dict with 0."""
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

            # ------------------------------------------------------------------
            # Phase 1 — Binary: benign vs. attack
            # ------------------------------------------------------------------
            X1 = _align(df.copy(), input_features)

            t0 = time.perf_counter()
            prob = model.predict_proba(X1)[0, attack_idx]
            p1_ms = (time.perf_counter() - t0) * 1000

            with _stats_lock:
                _stats["total_inference_ms"] += p1_ms
                if p1_ms > _stats["max_inference_ms"]:
                    _stats["max_inference_ms"] = p1_ms

            if prob < THRESHOLD:
                return  # benign — nothing more to do

            # ------------------------------------------------------------------
            # Phase 2 — Multi-class: attack type classification
            # ------------------------------------------------------------------
            with _stats_lock:
                _stats["alerts"] += 1

            X2 = _align(df.copy(), p2_input_features)

            t0 = time.perf_counter()
            p2_proba = model_p2.predict_proba(X2)[0]
            p2_ms = (time.perf_counter() - t0) * 1000

            p2_conf = float(p2_proba.max())
            p2_label = str(model_p2.classes_[p2_proba.argmax()])
            low_conf = p2_conf < PHASE2_CONFIDENCE_THRESHOLD

            with _stats_lock:
                _stats["p2_total_inference_ms"] += p2_ms
                if p2_ms > _stats["p2_max_inference_ms"]:
                    _stats["p2_max_inference_ms"] = p2_ms
                if low_conf:
                    _stats["p2_low_confidence"] += 1
                else:
                    _stats["p2_classifications"][p2_label] = (
                        _stats["p2_classifications"].get(p2_label, 0) + 1
                    )

            # ------------------------------------------------------------------
            # Logging
            # ------------------------------------------------------------------
            row = pd.Series(flow)
            p2_label_display = f"{p2_label}" if not low_conf else f"LOW_CONF→P3 (best: {p2_label})"

            if VERBOSE_ALERTS:
                log.warning(
                    "[ALERT] Attack detected — P1 conf %.1f%% | P2 label: %s (%.1f%%) | "
                    "P1 %.2f ms | P2 %.2f ms\n%s",
                    prob * 100, p2_label_display, p2_conf * 100, p1_ms, p2_ms,
                    row.to_string(),
                )
            else:
                log.warning(
                    "[ALERT] Attack detected — P1 conf %.1f%% | P2 label: %s (%.1f%%) | "
                    "P1 %.2f ms | P2 %.2f ms",
                    prob * 100, p2_label_display, p2_conf * 100, p1_ms, p2_ms,
                )

            cols_tsv = "\t".join(
                str(row.get(c, "")) if not isinstance(row.get(c), float)
                else f"{row.get(c):.4g}"
                for c in _ALERT_COLS
            )
            _report_append(
                f"{datetime.datetime.now().strftime('%H:%M:%S')}\t"
                f"{prob:.1%}\t"
                f"{p2_label_display}\t"
                f"{p2_conf:.1%}\t"
                f"{cols_tsv}\n"
            )

        except Exception as e:
            log.error("Inference failed on flow: %s", e)

    return on_flow


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    # Phase 1
    model = load_model(MODEL_PATH)
    input_features = get_input_features(model)
    attack_idx = get_attack_class_index(model)

    # Phase 2
    model_p2 = load_model(P2_MODEL_PATH)
    p2_input_features = get_input_features(model_p2)

    log.info(
        "Watching interface %s | P1 threshold %.0f%% | P2 conf threshold %.0f%% | idle timeout %.0fs",
        INTERFACE, THRESHOLD * 100, PHASE2_CONFIDENCE_THRESHOLD * 100, IDLE_TIMEOUT,
    )

    _init_report(model, input_features, attack_idx, model_p2, p2_input_features)

    on_flow = make_flow_handler(model, input_features, attack_idx, model_p2, p2_input_features)

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
