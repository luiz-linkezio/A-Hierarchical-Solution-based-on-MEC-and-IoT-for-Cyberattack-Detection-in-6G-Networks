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
import signal
import sys
import threading
import time

import joblib
import pandas as pd
import psutil
from netflower import capture_live

# Allow importing from the project root (constants package)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from _ids_worker import FlowInferenceWorker
from constants.features import ALL_EXCLUDED_FEATURES, EXCLUDED_FEATURES, FINAL_FEATURES
from constants.labels import ALL_LABELS, BENIGN_LABELS, MALICIOUS_LABELS
from constants.power_telemetry import (
    load_power_model, estimate_power_w, read_soc_temp_c, read_cluster_freqs_mhz,
)

_POWER_MODEL = load_power_model()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INTERFACE = "eth0"

# Phase 1 — Binary classifier (benign vs. attack)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "binary_classifier_20260601_001154.pkl")

# Phase 2 — Multi-class classifier (attack type)
# Auto-updated by notebooks/training.ipynb after each training run.
P2_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "multiclass_classifier_20260601_001154.pkl")

REPORT_DIR = os.path.join(os.path.dirname(__file__), "logs")

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
    # E2E latency: on_flow entry → final classification (every flow)
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
_worker: "FlowInferenceWorker | None" = None


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
    # Fallback de potência para ARM (sem RAPL): modelo de CPU calibrado.
    if "power_w" not in result and "cpu_pct" in result:
        result["power_w"] = estimate_power_w(result["cpu_pct"], _POWER_MODEL)
    # Telemetria extra (estimativa de energia + DVFS/térmica).
    t = read_soc_temp_c()
    if t is not None:
        result["temp_c"] = t
    freqs = read_cluster_freqs_mhz()
    if freqs:
        result["freqs"] = freqs
    return result


_ALERT_COLS = ["src_ip", "dst_ip", "src_port", "dst_port", "protocol",
               "flow_byts_s", "flow_pkts_s", "flow_duration"]


def _report_append(text: str) -> None:
    if _report_path:
        with open(_report_path, "a") as _f:
            _f.write(text)


def _append_flow_row(flow: dict, verdict_fields: list[str]) -> None:
    """Grava a linha TSV de um fluxo (ATTACK ou BENIGN) na seção [FLOWS].
    flow['timestamp'] é a captura do 1º pacote (netflower) — é ela, e não a hora
    de emissão, que a métrica usa para atribuir o fluxo à janela de ataque."""
    flow_ts = flow.get("timestamp")
    flow_ts_str = f"{float(flow_ts):.6f}" if flow_ts is not None else ""
    cols_tsv = "\t".join(
        str(flow.get(c, "")) if not isinstance(flow.get(c), float)
        else f"{flow.get(c):.4g}"
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
        f"{flow_ts_str}\t"
        + "\t".join(verdict_fields)
        + f"\t{cols_tsv}\t{sys_tsv}\n"
    )


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
        f"[FLOWS]\n"
        f"# timestamp = hora de emissão (VIM, HH:MM:SS); flow_ts = captura do 1º pacote\n"
        f"# (epoch, s) — base da métrica, imune ao atraso de processamento/timeout.\n"
        f"# Uma linha por fluxo: verdict ATTACK (p1 >= threshold) ou BENIGN (sem P2: '-').\n"
        f"# timestamp\tflow_ts\tverdict\tp1_conf\tp2_label\tp2_conf\tp2_low_conf\t"
        + "\t".join(_ALERT_COLS)
        + "\tcpu_pct\tram_mb\tnet_recv_kbs\tnet_sent_kbs\tpower_w\n"
    )
    log.info("Report initialized → %s", _report_path)


def _finalize_report() -> None:
    elapsed = time.time() - _run_start
    h, rem = divmod(int(elapsed), 3600)
    m, s = divmod(rem, 60)
    with _stats_lock:
        flows            = _stats["flows"]
        alerts           = _stats["alerts"]
        avg_ms           = _stats["total_inference_ms"] / flows if flows else 0.0
        max_ms           = _stats["max_inference_ms"]
        p2_avg_ms        = _stats["p2_total_inference_ms"] / alerts if alerts else 0.0
        p2_max_ms        = _stats["p2_max_inference_ms"]
        p2_classifications = dict(_stats["p2_classifications"])
        p2_low_conf      = _stats["p2_low_confidence"]
        avg_e2e          = _stats["total_e2e_ms"] / flows if flows else 0.0
        max_e2e          = _stats["max_e2e_ms"]
        q_max            = _worker.max_queue_depth if _worker else 0
        q_resid          = _worker.queue_depth() if _worker else 0
        n                = _stats["sys_samples"]
        cpu_avg          = _stats["cpu_total_pct"] / n if n else 0.0
        cpu_max          = _stats["cpu_max_pct"]
        ram_avg          = _stats["ram_total_pct"] / n if n else 0.0
        ram_max          = _stats["ram_max_mb"]
        net_recv         = _stats["net_total_recv_bs"] / n if n else 0.0
        net_sent         = _stats["net_total_sent_bs"] / n if n else 0.0
        pw               = _stats["power_samples"]
        pow_avg          = _stats["power_total_w"] / pw if pw else None
        pow_max          = _stats["power_max_w"]     if pw else None
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
        f"p1_avg_inference_ms  = {avg_ms:.2f}\n"
        f"p1_max_inference_ms  = {max_ms:.2f}\n"
        f"p2_avg_inference_ms  = {p2_avg_ms:.2f}\n"
        f"p2_max_inference_ms  = {p2_max_ms:.2f}\n"
        f"p2_low_confidence    = {p2_low_conf:,}\n"
        f"avg_e2e_ms           = {avg_e2e:.2f}\n"
        f"max_e2e_ms           = {max_e2e:.2f}\n"
        f"queue_max_depth      = {q_max:,}\n"
        f"queue_residual       = {q_resid:,}\n"
        f"\n[SYSTEM_METRICS]\n"
        f"cpu_avg_pct          = {cpu_avg:.1f}\n"
        f"cpu_max_pct          = {cpu_max:.1f}\n"
        f"ram_avg_pct          = {ram_avg:.1f}\n"
        f"ram_max_mb           = {ram_max:.0f}\n"
        f"net_avg_recv_kbs     = {net_recv / 1024:.2f}\n"
        f"net_avg_sent_kbs     = {net_sent / 1024:.2f}\n"
        f"{power_lines}"
        f"{p2_breakdown}"
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
            flows       = _stats["flows"]
            alerts      = _stats["alerts"]
            avg_ms      = _stats["total_inference_ms"] / flows if flows else 0.0
            max_ms      = _stats["max_inference_ms"]
            p2_avg_ms   = _stats["p2_total_inference_ms"] / alerts if alerts else 0.0
            p2_max_ms   = _stats["p2_max_inference_ms"]
            p2_low_conf = _stats["p2_low_confidence"]
            avg_e2e     = _stats["total_e2e_ms"] / flows if flows else 0.0
            max_e2e     = _stats["max_e2e_ms"]
        log.info(
            "[STATS] Flows: %d | Alerts: %d | "
            "P1 avg %.2f ms max %.2f ms | "
            "P2 avg %.2f ms max %.2f ms | P2 low-conf: %d | "
            "E2E avg %.2f ms max %.2f ms",
            flows, alerts, avg_ms, max_ms, p2_avg_ms, p2_max_ms, p2_low_conf,
            avg_e2e, max_e2e,
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
        if "temp_c" in sys_m:
            parts.append(f"Temp {sys_m['temp_c']:.1f}C")
        if "freqs" in sys_m:
            fr = "/".join(f"{v}" for v in sys_m["freqs"].values())
            parts.append(f"Freq {fr}MHz")
        if _worker is not None:
            # Backlog da fila de inferência, gravado a cada tick: sobrevive a um
            # kill que impeça o [SUMMARY], preservando o pico de backlog.
            parts.append(f"Queue {_worker.queue_depth()} (max {_worker.max_queue_depth})")
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

def _align_batch(flows: list[dict], features: list[str]) -> pd.DataFrame:
    """Um DataFrame por LOTE, com as colunas do modelo (faltantes viram 0)."""
    df = pd.DataFrame(flows)
    for col in features:
        if col not in df.columns:
            df[col] = 0
    return df[features]


def make_batch_processor(model, input_features: list[str], attack_idx: int,
                         model_p2, p2_input_features: list[str]):
    """Processa um lote de fluxos em duas fases, cada uma em batch (lotes por
    fase): P1 no lote inteiro, P2 só no subconjunto que alertou. Chamado pelo
    worker, fora da thread de captura."""

    def process_batch(batch: list) -> None:
        flows = [flow for _, flow in batch]
        n = len(flows)

        # ------------------------------------------------------------------
        # Fase 1 — binária, no lote inteiro
        # ------------------------------------------------------------------
        X1 = _align_batch(flows, input_features)
        t0 = time.perf_counter()
        probs = model.predict_proba(X1)[:, attack_idx]
        p1_ms = (time.perf_counter() - t0) * 1000
        p1_per_flow_ms = p1_ms / n if n else 0.0

        alert_idx = [i for i, p in enumerate(probs) if p >= THRESHOLD]

        # ------------------------------------------------------------------
        # Fase 2 — multiclasse, só nos fluxos que a Fase 1 marcou
        # ------------------------------------------------------------------
        p2_labels: dict = {}   # índice no lote -> (label, conf, low_conf)
        p2_ms = 0.0
        if alert_idx:
            X2 = _align_batch([flows[i] for i in alert_idx], p2_input_features)
            t0 = time.perf_counter()
            p2_proba = model_p2.predict_proba(X2)
            p2_ms = (time.perf_counter() - t0) * 1000
            for row_i, i in enumerate(alert_idx):
                pr = p2_proba[row_i]
                conf = float(pr.max())
                label = str(model_p2.classes_[pr.argmax()])
                p2_labels[i] = (label, conf, conf < PHASE2_CONFIDENCE_THRESHOLD)
        p2_per_flow_ms = p2_ms / len(alert_idx) if alert_idx else 0.0

        now = time.perf_counter()
        with _stats_lock:
            _stats["flows"] += n
            _stats["alerts"] += len(alert_idx)
            _stats["total_inference_ms"] += p1_ms
            if p1_per_flow_ms > _stats["max_inference_ms"]:
                _stats["max_inference_ms"] = p1_per_flow_ms
            _stats["p2_total_inference_ms"] += p2_ms
            if p2_per_flow_ms > _stats["p2_max_inference_ms"]:
                _stats["p2_max_inference_ms"] = p2_per_flow_ms
            for label, _conf, low in p2_labels.values():
                if low:
                    _stats["p2_low_confidence"] += 1
                else:
                    _stats["p2_classifications"][label] = (
                        _stats["p2_classifications"].get(label, 0) + 1
                    )
            for t_arrival, _ in batch:
                e2e_ms = (now - t_arrival) * 1000
                _stats["total_e2e_ms"] += e2e_ms
                if e2e_ms > _stats["max_e2e_ms"]:
                    _stats["max_e2e_ms"] = e2e_ms

        for i, (_, flow) in enumerate(batch):
            if i in p2_labels:
                label, conf, low = p2_labels[i]
                _append_flow_row(flow, [
                    "ATTACK", f"{probs[i]:.3%}", label, f"{conf:.1%}", str(int(low)),
                ])
            else:
                # Benigno também vai para o log: sem ele não há FN/TN por fluxo.
                _append_flow_row(flow, ["BENIGN", f"{probs[i]:.3%}", "-", "-", "-"])

        if VERBOSE_ALERTS:
            for i in alert_idx:
                label, conf, low = p2_labels[i]
                disp = label if not low else f"LOW_CONF→P3 (best: {label})"
                log.warning("[ALERT] P1 %.1f%% | P2 %s (%.1f%%)\n%s",
                            probs[i] * 100, disp, conf * 100, pd.Series(flows[i]).to_string())
        elif alert_idx:
            log.warning("[BATCH] %d fluxos, %d alertas | P1 %.2f ms (%.3f/fluxo) "
                        "P2 %.2f ms (%.3f/fluxo) | fila %d",
                        n, len(alert_idx), p1_ms, p1_per_flow_ms, p2_ms, p2_per_flow_ms,
                        _worker.queue_depth() if _worker else 0)

    return process_batch


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    global _worker
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

    # Worker de inferência: o callback de captura só enfileira; a inferência em
    # lote (P1 no lote, P2 nos alertas) roda nesta thread separada.
    process_batch = make_batch_processor(
        model, input_features, attack_idx, model_p2, p2_input_features
    )
    _worker = FlowInferenceWorker(process_batch)
    _worker.start()

    stop_printer = threading.Event()
    printer_thread = threading.Thread(target=_stats_printer, args=(stop_printer,), daemon=True)
    printer_thread.start()

    handle = capture_live(
        INTERFACE,
        on_flow=_worker.submit,
        idle_timeout=IDLE_TIMEOUT,
        flow_timeout=FLOW_TIMEOUT,
    )
    try:
        handle.start()
        log.info("Live capture started.")
        # netflower's capture_live pode sequestrar o SIGINT; reinstalamos os
        # handlers APÓS o start para garantir shutdown gracioso (grava [SUMMARY])
        # e encerramento confiável entre sessões via SIGINT ou SIGTERM.
        def _graceful_stop(signum, frame):
            raise KeyboardInterrupt
        signal.signal(signal.SIGINT, _graceful_stop)
        signal.signal(signal.SIGTERM, _graceful_stop)
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # Ordem importa: parar a captura primeiro faz flush_all enfileirar os
        # últimos fluxos; só então drenamos o worker, para não perder nada.
        handle.stop()
        log.info("Interrupted — stopping capture, draining inference queue.")
        # Dreno limitado: sob flood o backlog pode levar minutos para esvaziar.
        # Drenamos por até 60s e gravamos o [SUMMARY] com o residual, em vez de
        # travar o encerramento (e ser morto sem [SUMMARY]).
        residual = _worker.stop(join_timeout=60.0)
        if residual:
            log.warning("Encerrado com %d fluxos ainda na fila (backlog residual, não logados).", residual)
        stop_printer.set()
        printer_thread.join(timeout=3)
        _finalize_report()


if __name__ == "__main__":
    main()
