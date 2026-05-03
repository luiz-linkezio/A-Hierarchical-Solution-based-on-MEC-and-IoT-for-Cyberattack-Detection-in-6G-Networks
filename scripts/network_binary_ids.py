"""
network_binary_ids.py — Real-time binary IDS for VIM 4.

Captures live traffic via tcpdump, converts each rotated chunk to
flow-level features with pcapflower, and runs a pre-trained sklearn
binary classifier to flag attack traffic.

Classification mode: binary  (benign vs. attack)
Model format:        scikit-learn pipeline saved as .pkl (joblib)
"""

import glob
import logging
import os
import subprocess
import sys
import time

import joblib
import pandas as pd

# Allow importing from the project root (constants package)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from constants import BENIGN_LABELS, FINAL_FEATURES

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INTERFACE = "eth0"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "binary_classifier.pkl")
PCAPFLOWER_CMD = "pcapflower"

# tcpdump rotates to a new file every CHUNK_SIZE_MB megabytes.
# Smaller chunks → lower detection latency; larger → fewer conversions.
CHUNK_SIZE_MB = 50

# Base name used by tcpdump: capture.pcap, capture.pcap1, capture.pcap2, ...
CAPTURE_PREFIX = "capture"

# Minimum probability assigned to the attack class to raise an alert.
THRESHOLD = 0.8

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
    # Binary classifier has exactly one attack class
    return attack_indices[0]


# ---------------------------------------------------------------------------
# Traffic capture
# ---------------------------------------------------------------------------

def start_capture() -> subprocess.Popen:
    """
    Launch tcpdump in the background.

    Uses -C to rotate capture files every CHUNK_SIZE_MB MB, which lets the
    main loop process completed chunks while capture continues uninterrupted.
    Broadcast and multicast traffic is excluded to reduce noise.
    """
    cmd = [
        "tcpdump",
        "-i", INTERFACE,
        "-w", f"{CAPTURE_PREFIX}.pcap",
        "-C", str(CHUNK_SIZE_MB),
        "not", "broadcast",
        "and", "not", "multicast",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log.info("tcpdump started on interface %s (PID %d)", INTERFACE, proc.pid)
    return proc


# ---------------------------------------------------------------------------
# Per-chunk inference
# ---------------------------------------------------------------------------

def process_pcap(pcap_file: str, model, input_features: list[str], attack_idx: int) -> None:
    """
    Convert one .pcap chunk to flows, run binary inference, and log alerts.

    pcapflower is called to produce a flow-level CSV.  The CSV is then aligned
    to the exact feature columns the model expects before calling predict_proba.
    Cleanup (pcap + csv removal) happens in a finally block so files are never
    left behind, even when inference raises an exception.
    """
    csv_file = pcap_file + ".csv"

    # Convert packet capture to flow-level feature vectors
    result = subprocess.run(
        [PCAPFLOWER_CMD, pcap_file, "-o", csv_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        log.warning("pcapflower exited with code %d for %s", result.returncode, pcap_file)

    if not os.path.exists(csv_file):
        log.warning("pcapflower produced no output for %s", pcap_file)
        _cleanup(pcap_file, csv_file)
        return

    try:
        df = pd.read_csv(csv_file)

        if df.empty:
            return

        # Align dataframe to the exact feature set the model expects.
        # Columns present in input_features but missing from the CSV are filled
        # with 0 — this can happen for short or incomplete flows where pcapflower
        # omits optional statistics.
        missing_cols = [c for c in input_features if c not in df.columns]
        if missing_cols:
            log.debug("Filling %d missing feature column(s) with 0: %s", len(missing_cols), missing_cols)
            for col in missing_cols:
                df[col] = 0

        X = df[input_features]

        # predict_proba returns shape (n_flows, n_classes);
        # attack_idx selects the attack-class column.
        probs = model.predict_proba(X)
        attack_probs = probs[:, attack_idx]

        for prob in attack_probs:
            if prob >= THRESHOLD:
                log.warning("[ALERT] Attack detected — confidence %.1f%%", prob * 100)

    except Exception as e:
        log.error("Inference failed on %s: %s", pcap_file, e)

    finally:
        # Always remove processed files to avoid disk accumulation
        _cleanup(pcap_file, csv_file)


def _cleanup(pcap_file: str, csv_file: str) -> None:
    """Remove a pcap/csv pair, logging a warning if either removal fails."""
    for path in (pcap_file, csv_file):
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError as e:
            log.warning("Could not remove %s: %s", path, e)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    model = load_model(MODEL_PATH)
    input_features = get_input_features(model)
    attack_idx = get_attack_class_index(model)

    log.info("Watching interface %s | threshold %.0f%% | chunk %d MB",
             INTERFACE, THRESHOLD * 100, CHUNK_SIZE_MB)

    tcpdump_proc = start_capture()

    try:
        while True:
            # tcpdump with -C names files: capture.pcap, capture.pcap1, capture.pcap2, ...
            # After lexicographic sort the last entry is always the file currently
            # being written.  Skip it to avoid reading a partial capture.
            pcaps = sorted(glob.glob(f"{CAPTURE_PREFIX}.pcap*"))

            for pcap in pcaps[:-1]:
                if os.path.getsize(pcap) == 0:
                    continue
                process_pcap(pcap, model, input_features, attack_idx)

            time.sleep(2)

    except KeyboardInterrupt:
        log.info("Interrupted — shutting down tcpdump.")
        tcpdump_proc.terminate()
        tcpdump_proc.wait()


if __name__ == "__main__":
    main()
