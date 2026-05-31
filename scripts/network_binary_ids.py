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
import psutil
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

REPORT_DIR = os.path.join(os.path.dirname(__file__), "logs")

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
    # E2E latency: on_flow entry → classification done (every flow)
    "total_e2e_ms": 0.0,
    "max_e2e_ms": 0.0,
    # System metrics — accumulated from periodic samples
    "sys_samples": 0,
    "cpu_total_pct": 0.0,
    "cpu_max_pct": 0.0,
    "ram_total_pct": 0.0,
    "ram_max_mb": 0.0,
    "net_total_recv_bs": 0.0,
    "net_total_sent_bs": 0.0,
    "power_total_w": 0.0,
    "power_max_w": 0.0,
    "power_samples": 0,
}

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

_report_path: str = ""
_run_start: float = 0.0


def _find_rapl_path() -> str:
    for p in (
        "/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj",
        "/sys/class/powercap/intel-rapl:0/energy_uj",
    ):
        if os.path.exists(p):
            return p
    return ""

_RAPL_PATH = _find_rapl_path()
_rapl_state: dict  = {"uj": None, "t": None}
_net_state: dict   = {"bytes_recv": 0, "bytes_sent": 0, "t": None}
_last_sys_m: dict  = {}   # last sample; read by on_flow at alert time


def _sample_system_metrics(iface: str) -> dict:
    """Sample CPU, RAM, net throughput, and RAPL power. Returns only keys that succeeded."""
    result: dict = {}
    try:
        result["cpu_pct"] = psutil.cpu_percent(interval=None)
        vm = psutil.virtual_memory()
        result["ram_pct"] = vm.percent
        result["ram_mb"]  = vm.used / 1024 / 1024
    except Exception:
        pass
    try:
        c = psutil.net_io_counters(pernic=True).get(iface)
        t = time.monotonic()
        if c and _net_state["t"] is not None:
            dt = t - _net_state["t"]
            if dt > 0:
                result["recv_bs"] = (c.bytes_recv - _net_state["bytes_recv"]) / dt
                result["sent_bs"] = (c.bytes_sent - _net_state["bytes_sent"]) / dt
        if c:
            _net_state.update(bytes_recv=c.bytes_recv, bytes_sent=c.bytes_sent, t=t)
    except Exception:
        pass
    if _RAPL_PATH:
        try:
            with open(_RAPL_PATH) as f:
                uj = int(f.read())
            t = time.monotonic()
            if _rapl_state["uj"] is not None:
                dt = t - _rapl_state["t"]
                if dt > 0:
                    result["power_w"] = (uj - _rapl_state["uj"]) / (dt * 1e6)
            _rapl_state.update(uj=uj, t=t)
        except Exception:
            pass
    return result


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
        f"# timestamp\tp1_conf\t" + "\t".join(_ALERT_COLS)
        + "\tcpu_pct\tram_mb\tnet_recv_kbs\tnet_sent_kbs\tpower_w\n"
    )
    log.info("Report initialized → %s", _report_path)


def _finalize_report() -> None:
    elapsed = time.time() - _run_start
    h, rem = divmod(int(elapsed), 3600)
    m, s = divmod(rem, 60)
    with _stats_lock:
        flows    = _stats["flows"]
        alerts   = _stats["alerts"]
        avg_ms   = _stats["total_inference_ms"] / flows if flows else 0.0
        max_ms   = _stats["max_inference_ms"]
        avg_e2e  = _stats["total_e2e_ms"] / flows if flows else 0.0
        max_e2e  = _stats["max_e2e_ms"]
        n        = _stats["sys_samples"]
        cpu_avg  = _stats["cpu_total_pct"] / n if n else 0.0
        cpu_max  = _stats["cpu_max_pct"]
        ram_avg  = _stats["ram_total_pct"] / n if n else 0.0
        ram_max  = _stats["ram_max_mb"]
        net_recv = _stats["net_total_recv_bs"] / n if n else 0.0
        net_sent = _stats["net_total_sent_bs"] / n if n else 0.0
        pw       = _stats["power_samples"]
        pow_avg  = _stats["power_total_w"] / pw if pw else None
        pow_max  = _stats["power_max_w"]     if pw else None
    dt_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    power_lines = (
        f"power_avg_w          = {pow_avg:.2f}\n"
        f"power_max_w          = {pow_max:.2f}\n"
        if pow_avg is not None
        else "power_w              = unavailable (no RAPL interface found)\n"
    )
    _report_append(
        f"\n[SUMMARY]\n"
        f"end_time             = {dt_str}\n"
        f"duration             = {h:02d}:{m:02d}:{s:02d}\n"
        f"flows_processed      = {flows:,}\n"
        f"alerts_raised        = {alerts:,}\n"
        f"avg_inference_ms     = {avg_ms:.2f}\n"
        f"max_inference_ms     = {max_ms:.2f}\n"
        f"avg_e2e_ms           = {avg_e2e:.2f}\n"
        f"max_e2e_ms           = {max_e2e:.2f}\n"
        f"\n[SYSTEM_METRICS]\n"
        f"cpu_avg_pct          = {cpu_avg:.1f}\n"
        f"cpu_max_pct          = {cpu_max:.1f}\n"
        f"ram_avg_pct          = {ram_avg:.1f}\n"
        f"ram_max_mb           = {ram_max:.0f}\n"
        f"net_avg_recv_kbs     = {net_recv / 1024:.2f}\n"
        f"net_avg_sent_kbs     = {net_sent / 1024:.2f}\n"
        f"{power_lines}"
    )
    log.info("Report finalized → %s", _report_path)


# ---------------------------------------------------------------------------
# Stats printer
# ---------------------------------------------------------------------------

def _stats_printer(stop_event: threading.Event) -> None:
    try:
        psutil.cpu_percent(interval=None)  # prime the rolling counter
    except Exception:
        pass
    while not stop_event.wait(3.0):
        with _stats_lock:
            flows  = _stats["flows"]
            alerts = _stats["alerts"]
            avg_ms  = _stats["total_inference_ms"] / flows if flows else 0.0
            max_ms  = _stats["max_inference_ms"]
            avg_e2e = _stats["total_e2e_ms"] / flows if flows else 0.0
            max_e2e = _stats["max_e2e_ms"]
        log.info(
            "[STATS] Flows: %d | Alerts: %d | P1 avg %.2f ms max %.2f ms | E2E avg %.2f ms max %.2f ms",
            flows, alerts, avg_ms, max_ms, avg_e2e, max_e2e,
        )
        sys_m = _sample_system_metrics(INTERFACE)
        with _stats_lock:
            _last_sys_m.clear()
            _last_sys_m.update(sys_m)
            _stats["sys_samples"] += 1
            if "cpu_pct" in sys_m:
                _stats["cpu_total_pct"] += sys_m["cpu_pct"]
                _stats["cpu_max_pct"] = max(_stats["cpu_max_pct"], sys_m["cpu_pct"])
            if "ram_pct" in sys_m:
                _stats["ram_total_pct"] += sys_m["ram_pct"]
                _stats["ram_max_mb"] = max(_stats["ram_max_mb"], sys_m.get("ram_mb", 0))
            if "recv_bs" in sys_m:
                _stats["net_total_recv_bs"] += sys_m["recv_bs"]
                _stats["net_total_sent_bs"] += sys_m.get("sent_bs", 0)
            if "power_w" in sys_m:
                _stats["power_total_w"] += sys_m["power_w"]
                _stats["power_max_w"] = max(_stats["power_max_w"], sys_m["power_w"])
                _stats["power_samples"] += 1
        parts = []
        if "cpu_pct" in sys_m:
            parts.append(f"CPU {sys_m['cpu_pct']:.1f}%")
        if "ram_pct" in sys_m:
            parts.append(f"RAM {sys_m['ram_pct']:.1f}% ({sys_m.get('ram_mb', 0):.0f} MB)")
        if "recv_bs" in sys_m:
            parts.append(f"Net ↓{sys_m['recv_bs']/1024:.1f} KB/s ↑{sys_m.get('sent_bs', 0)/1024:.1f} KB/s")
        if "power_w" in sys_m:
            parts.append(f"Power {sys_m['power_w']:.1f} W")
        if parts:
            sys_line = " | ".join(parts)
            log.info("[SYS]   %s", sys_line)
            _report_append(
                f"[SYS_SNAPSHOT] {datetime.datetime.now().strftime('%H:%M:%S')}  {sys_line}\n"
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
        t_entry = time.perf_counter()
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
            with _stats_lock:
                _snap = dict(_last_sys_m)
            sys_tsv = "\t".join([
                f"{_snap['cpu_pct']:.1f}"              if "cpu_pct"  in _snap else "",
                f"{_snap['ram_mb']:.0f}"               if "ram_mb"   in _snap else "",
                f"{_snap['recv_bs'] / 1024:.2f}"       if "recv_bs"  in _snap else "",
                f"{_snap.get('sent_bs', 0) / 1024:.2f}" if "recv_bs" in _snap else "",
                f"{_snap['power_w']:.2f}"              if "power_w"  in _snap else "",
            ])
            _report_append(
                f"{datetime.datetime.now().strftime('%H:%M:%S')}\t"
                f"{prob:.1%}\t"
                f"{cols_tsv}\t"
                f"{sys_tsv}\n"
            )

        except Exception as e:
            log.error("Inference failed on flow: %s", e)
        finally:
            e2e_ms = (time.perf_counter() - t_entry) * 1000
            with _stats_lock:
                _stats["total_e2e_ms"] += e2e_ms
                if e2e_ms > _stats["max_e2e_ms"]:
                    _stats["max_e2e_ms"] = e2e_ms

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
