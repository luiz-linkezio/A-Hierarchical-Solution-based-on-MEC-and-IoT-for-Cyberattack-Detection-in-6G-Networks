#!/usr/bin/env python3
"""
ids_metrics.py — Compute live-run IDS metrics from log files.

Supports two log types:
  multiclass  — network_ids.py output (Phase 1 + Phase 2)
  binary      — network_binary_ids.py output (Phase 1 only)

Métrica POR FLUXO, independente de vazamento temporal
-----------------------------------------------------
O IDS grava uma linha por fluxo (ATTACK ou BENIGN) com o flow_ts — a captura do
1º pacote, tirada do cabeçalho pcap. Cada fluxo é rotulado pela janela de ataque
em que COMEÇOU, não pela hora em que foi emitido. Sob flood a VIM 4 emite fluxos
com dezenas de segundos de atraso (idle_timeout + fila); com o rótulo pela hora
de emissão esses fluxos "vazavam" para os segundos/janelas seguintes. Pelo
flow_ts eles contam para o ataque que os gerou, sem idle_slack nem gaps.

Ground truth: janelas do report JSON do attack_generator (hora local do PC,
BRT por padrão → --tz-offset), alinhadas ao relógio da VIM com --clock-offset.

Usage
-----
python3 ids_metrics.py --ids logs/.../ids_run_<ts>.log \
    --report logs/.../report_<ts>.json --mode multiclass --label-map ddos=dos \
    [--clock-offset 0.4] [--output results/metrics.json]

python3 ids_metrics.py --ids logs/.../binary_ids_run_<ts>.log \
    --report logs/.../report_<ts>.json --mode binary --label-map ddos=dos
"""

import argparse
import ipaddress
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from constants.power_telemetry import load_power_model

# ─── Attack class ordering ────────────────────────────────────────────────────
ATTACK_CLASSES_FULL    = ["recon", "dos", "ddos", "bruteforce", "web", "mitm", "spoofing", "malware"]
ATTACK_CLASSES_UNIFIED = ["recon", "dos",         "bruteforce", "web", "mitm", "spoofing", "malware"]


def build_attack_classes(label_map: dict) -> list:
    """Return the ordered class list after removing classes that were merged away."""
    merged_into = set(label_map.keys())
    seen, result = set(), []
    for c in ATTACK_CLASSES_FULL:
        canonical = label_map.get(c, c)
        if canonical not in seen:
            seen.add(canonical)
            result.append(canonical)
    return result


# ─── Helpers ─────────────────────────────────────────────────────────────────

def ts_to_seconds(ts_str: str) -> int:
    """'HH:MM:SS' → seconds since midnight."""
    h, m, s = map(int, ts_str.split(":"))
    return h * 3600 + m * 60 + s


def parse_orchestrator(path: str, tz_offset_h: int, idle_slack_s: int, label_map: dict = None):
    """
    Janelas em segundos-do-dia do relógio de emissão, estendidas por idle_slack.
    Usadas SÓ para dividir a energia em ataque × ocioso — a detecção usa
    parse_windows_epoch (por flow_ts).

    Return list of (label, start_sec, end_sec) ground-truth windows.
    Timestamps in the JSON are in local time (BRT); add tz_offset_h hours to get UTC.

    Idle slack is only added when there is a real gap to the next attack window
    (i.e., when attacks are consecutive the end of window i is capped at the start
    of window i+1 − 1 second to avoid overlap, and slack is not applied).
    For the last attack the full slack is always applied.
    """
    with open(path) as f:
        report = json.load(f)

    if label_map is None:
        label_map = {}

    attacks = report["attacks"]
    raw = []
    for atk in attacks:
        start_dt = datetime.fromisoformat(atk["start_time"]) + timedelta(hours=tz_offset_h)
        end_dt   = datetime.fromisoformat(atk["end_time"])   + timedelta(hours=tz_offset_h)
        raw_label = atk["attack"]
        canonical = label_map.get(raw_label, raw_label)
        raw.append((
            canonical,
            start_dt.hour * 3600 + start_dt.minute * 60 + int(start_dt.second),
            end_dt.hour   * 3600 + end_dt.minute   * 60 + int(end_dt.second),
        ))

    windows = []
    for i, (label, start_sec, end_sec) in enumerate(raw):
        is_last = (i == len(raw) - 1)
        if is_last:
            effective_end = end_sec + idle_slack_s
        else:
            next_start = raw[i + 1][1]
            gap = next_start - end_sec
            if gap > idle_slack_s:
                # Real gap: extend into gap but no further than slack
                effective_end = end_sec + idle_slack_s
            else:
                # Consecutive: cap at next window start − 1 to avoid overlap
                effective_end = next_start - 1
        windows.append((label, start_sec, effective_end))
    return windows


def get_true_label(ts_sec: int, windows):
    for label, start, end in windows:
        if start <= ts_sec <= end:
            return label
    return "outside"


def power_w(cpu_pct: float, p_idle: float, p_max: float) -> float:
    """Linear CPU-utilization power model: P = P_idle + (P_max - P_idle) * util."""
    return p_idle + (p_max - p_idle) * cpu_pct / 100.0


def compute_session_energy(samples, windows, p_idle: float, p_max: float,
                           max_gap_s: float = 10.0) -> dict:
    """
    Integrate power over a (ts_sec, cpu_pct) time series, splitting energy into
    attack-window vs idle using the same ground-truth windows as get_true_label.
    Each interval [t_i, t_{i+1}) is priced at the power implied by cpu_pct at t_i
    (left rectangle rule) and capped at max_gap_s to avoid inflating energy
    across large gaps in the log. Returns {} if fewer than 2 samples.
    """
    if len(samples) < 2:
        return {}
    total_j = total_s = 0.0
    attack_j = attack_s = 0.0
    idle_j = idle_s = 0.0
    for (t0, cpu0), (t1, _) in zip(samples, samples[1:]):
        dt = min(t1 - t0, max_gap_s)
        if dt <= 0:
            continue
        p = power_w(cpu0, p_idle, p_max)
        e = p * dt
        total_j += e
        total_s += dt
        if get_true_label(t0, windows) == "outside":
            idle_j += e
            idle_s += dt
        else:
            attack_j += e
            attack_s += dt
    return {
        "duration_s": total_s,
        "total_energy_j": round(total_j, 2),
        "total_energy_wh": round(total_j / 3600, 4),
        "avg_power_w": round(total_j / total_s, 3) if total_s else 0.0,
        "attack": {
            "energy_j": round(attack_j, 2),
            "duration_s": attack_s,
            "avg_power_w": round(attack_j / attack_s, 3) if attack_s else 0.0,
        },
        "idle": {
            "energy_j": round(idle_j, 2),
            "duration_s": idle_s,
            "avg_power_w": round(idle_j / idle_s, 3) if idle_s else 0.0,
        },
    }


def energy_band(samples, windows, model: dict) -> dict:
    """Energia em 3 cenários (low/central/high) usando a banda de sensibilidade
    do modelo de potência — torna a incerteza da estimativa explícita."""
    s = model.get("sensitivity", {})
    central = compute_session_energy(samples, windows, model["p_idle_w"], model["p_max_w"])
    low = compute_session_energy(samples, windows,
                                 s.get("p_idle_low", model["p_idle_w"]),
                                 s.get("p_max_low", model["p_max_w"]))
    high = compute_session_energy(samples, windows,
                                  s.get("p_idle_high", model["p_idle_w"]),
                                  s.get("p_max_high", model["p_max_w"]))
    return {"low": low, "central": central, "high": high}


# ─── Ground truth por fluxo ──────────────────────────────────────────────────

def parse_windows_epoch(path: str, tz_offset_h: float, clock_offset_s: float = 0.0,
                        label_map: dict = None):
    """
    Janelas de ataque do orquestrador como (label, start_epoch, end_epoch) no
    relógio da VIM 4 — o mesmo relógio do flow_ts gravado pelo IDS.

    Os horários do JSON são hora local do PC sem fuso (BRT); tz_offset_h é o que
    se soma para chegar a UTC. clock_offset_s = relógio da VIM − relógio do PC.
    Sem idle_slack: o fluxo é atribuído pela captura do 1º pacote, então o atraso
    de emissão (timeout do fluxo + saturação do IDS) não precisa ser absorvido.
    """
    with open(path) as f:
        report = json.load(f)
    label_map = label_map or {}
    pc_tz = timezone(timedelta(hours=-tz_offset_h))
    windows = []
    for atk in report["attacks"]:
        start = datetime.fromisoformat(atk["start_time"]).replace(tzinfo=pc_tz).timestamp()
        end = datetime.fromisoformat(atk["end_time"]).replace(tzinfo=pc_tz).timestamp()
        label = label_map.get(atk["attack"], atk["attack"])
        windows.append((label, start + clock_offset_s, end + clock_offset_s))
    return windows


def _window_index(flow_ts: float, windows):
    for i, (_, start, end) in enumerate(windows):
        if start <= flow_ts <= end:
            return i
    return None


def flow_true_label(flow_ts: float, windows) -> str:
    """Rótulo verdadeiro do fluxo: a janela em que ele COMEÇOU, ou 'benign'."""
    i = _window_index(flow_ts, windows)
    return "benign" if i is None else windows[i][0]


def make_background_filter(target_ip: str, attacker_ips, lan: str = None):
    """
    Devolve is_background(flow, window_label) -> bool. A LAN do testbed não é
    isolada: outros hosts, o roteador, multicast (mDNS/SSDP) e o próprio NTP/apt
    da VIM geram fluxos que podem COMEÇAR dentro de uma janela de ataque sem
    fazer parte dele. Um fluxo só pode ser de ataque se envolver a VIM
    (target_ip) e a outra ponta for:
      - o atacante (qualquer IP dele na LAN); ou
      - um host fora da LAN que INICIOU o fluxo (src = 1º pacote no netflower):
        fontes forjadas do ddos --rand-source e do spoofing; ou
      - um host fora da LAN contatado pela VIM, só na janela de MITM (o tráfego
        da vítima passa pelo atacante — é o que o ataque intercepta).
    Multicast/broadcast, outros hosts da LAN e fluxos que a VIM inicia para fora
    da LAN nas demais janelas (NTP, apt) são fundo.
    """
    target = ipaddress.ip_address(target_ip)
    attackers = {ipaddress.ip_address(a) for a in attacker_ips}
    net = ipaddress.ip_network(lan or f"{target_ip}/24", strict=False)

    def is_background(flow: dict, window_label: str = None) -> bool:
        try:
            src = ipaddress.ip_address(flow.get("src_ip", ""))
            dst = ipaddress.ip_address(flow.get("dst_ip", ""))
        except ValueError:
            return True
        for ip in (src, dst):
            if ip.is_multicast or ip == net.broadcast_address or str(ip) == "255.255.255.255":
                return True
        if target not in (src, dst):
            return True
        peer = dst if src == target else src
        if peer in attackers:
            return False
        if peer in net:
            return True
        inbound = dst == target
        return not (inbound or window_label == "mitm")

    return is_background


def _attack_window(flow: dict, windows, is_background=None):
    """Índice da janela de ataque a que o fluxo pertence, ou None (benigno)."""
    i = _window_index(flow["flow_ts"], windows)
    if i is not None and is_background is not None and is_background(flow, windows[i][0]):
        return None
    return i


# ─── Log parsers ─────────────────────────────────────────────────────────────

# Linha de fluxo da seção [FLOWS] (uma por fluxo, ATTACK ou BENIGN):
#   binary     : HH:MM:SS  flow_ts  verdict  P1%  src_ip  dst_ip  src_port  dst_port  protocol ...
#   multiclass : HH:MM:SS  flow_ts  verdict  P1%  p2_label  P2%  p2_low_conf  src_ip ...
# (P2 = '-' quando o verdict é BENIGN.)
_RE_FLOW = re.compile(r'^(\d{2}:\d{2}:\d{2})\t(\d+(?:\.\d+)?)\t(ATTACK|BENIGN)\t([\d.]+)%\t')


def parse_flow_log(path: str, mode: str) -> list:
    """Uma entrada por fluxo classificado. Linhas do formato antigo (só alertas,
    sem flow_ts) não casam e são ignoradas."""
    flows = []
    with open(path) as f:
        for line in f:
            m = _RE_FLOW.match(line)
            if not m:
                continue
            fields = line.rstrip("\n").split("\t")
            rec = {
                "emit_sec": ts_to_seconds(m.group(1)),
                "flow_ts": float(m.group(2)),
                "verdict": m.group(3),
                "p1": float(m.group(4)) / 100,
                "p2_label": None, "p2_conf": None, "low_conf": False,
            }
            rest = fields[4:]
            if mode == "multiclass":
                p2_label, p2_conf, low = rest[:3]
                if p2_label != "-":
                    rec["p2_label"] = p2_label
                    rec["p2_conf"] = float(p2_conf.rstrip("%")) / 100
                    rec["low_conf"] = low == "1"
                rest = rest[3:]
            for key, val in zip(("src_ip", "dst_ip", "src_port", "dst_port", "protocol"), rest):
                rec[key] = val
            flows.append(rec)
    return flows


# Periodic background sample, independent of alert lines:
#   [SYS_SNAPSHOT] HH:MM:SS  CPU x.x% | RAM ...
_RE_SNAPSHOT = re.compile(
    r'^\[SYS_SNAPSHOT\] (\d{2}:\d{2}:\d{2})\s+CPU\s+([\d.]+)%'
)


def parse_snapshot_log(path: str):
    """Yield (ts_sec, cpu_pct) for each SYS_SNAPSHOT line."""
    with open(path) as f:
        for line in f:
            m = _RE_SNAPSHOT.match(line)
            if not m:
                continue
            yield (ts_to_seconds(m.group(1)), float(m.group(2)))


# CPU% + RAM(MB) de cada SYS_SNAPSHOT (ex.: "CPU 22.5% | RAM 12.0% (1000 MB) | ...")
_RE_SNAPSHOT_FULL = re.compile(
    r'^\[SYS_SNAPSHOT\] (\d{2}:\d{2}:\d{2})\s+CPU\s+([\d.]+)%.*?\((\d+) MB\)'
)


def parse_snapshot_resources(path: str):
    """Yield (ts_sec, cpu_pct, ram_mb) por SYS_SNAPSHOT. Fonte de recursos
    independente do bloco [SUMMARY] (que pode não ser escrito se a sessão for
    encerrada à força)."""
    with open(path) as f:
        for line in f:
            m = _RE_SNAPSHOT_FULL.match(line)
            if m:
                yield (ts_to_seconds(m.group(1)), float(m.group(2)), int(m.group(3)))


def resource_summary(samples_full) -> dict:
    """Agrega CPU/RAM dos SYS_SNAPSHOT (substitui a dependência do [SUMMARY])."""
    if not samples_full:
        return {}
    cpus = [c for _, c, _ in samples_full]
    rams = [r for _, _, r in samples_full]
    return {
        "samples": len(samples_full),
        "cpu_avg_pct": round(statistics.mean(cpus), 2),
        "cpu_max_pct": round(max(cpus), 2),
        "ram_avg_mb": round(statistics.mean(rams), 1),
        "ram_max_mb": max(rams),
    }


_RE_SUMMARY_KV = re.compile(r'^(\w+)\s*=\s*(.+)$')


def parse_summary_block(path: str) -> dict:
    """Parse the '[SUMMARY] key = value' block written by _finalize_report().
    Stops at the next '[SECTION]' header. Returns {} if no [SUMMARY] found
    (e.g. the session was killed before a graceful shutdown)."""
    in_summary = False
    result = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line == "[SUMMARY]":
                in_summary = True
                continue
            if in_summary:
                if not line or line.startswith("["):
                    break
                m = _RE_SUMMARY_KV.match(line)
                if m:
                    result[m.group(1)] = m.group(2)
    return result


def compute_inference_energy(summary: dict, session_energy_j: float,
                             p_idle: float, p_max: float) -> dict:
    """Coarse approximation of total inference energy from [SUMMARY] aggregates:
    one average power figure (at cpu_avg_pct) applied to every flow's average
    e2e latency. Returns {} if the summary block is missing or incomplete."""
    try:
        flows = int(str(summary["flows_processed"]).replace(",", ""))
        avg_e2e_ms = float(summary["avg_e2e_ms"])
        cpu_avg_pct = float(summary["cpu_avg_pct"])
    except (KeyError, ValueError):
        return {}
    if flows <= 0:
        return {}
    p = power_w(cpu_avg_pct, p_idle, p_max)
    j_per_flow = p * (avg_e2e_ms / 1000.0)
    total_j = j_per_flow * flows
    pct = (total_j / session_energy_j * 100) if session_energy_j else 0.0
    return {
        "flows": flows,
        "mj_per_flow": round(j_per_flow * 1000, 4),
        "total_j": round(total_j, 4),
        "pct_of_session_energy": round(pct, 2),
    }


# ─── Metric computation (por fluxo) ──────────────────────────────────────────

def _binary_scores(tp: int, fp: int, fn: int, tn: int) -> dict:
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    total = tp + fp + fn + tn
    return {
        "TP": tp, "FP": fp, "FN": fn, "TN": tn, "total": total,
        "accuracy": (tp + tn) / total if total else 0.0,
        "precision": prec, "recall": rec, "f1": f1, "fpr": fpr,
    }


def binary_flow_metrics(flows, windows, names=None, is_background=None) -> dict:
    """
    Matriz 2×2 por fluxo (Fase 1). Verdade = o fluxo começou dentro de uma janela
    de ataque; predição = verdict do IDS. Como o rótulo vem do flow_ts, um fluxo
    emitido minutos depois (saturação sob flood) continua contando para a janela
    de onde veio — a métrica é independente do vazamento temporal.
    names: nome original de cada janela (antes do label map), só para exibição.
    is_background: filtro de endpoints (make_background_filter); fluxos de fundo
    que começam dentro de uma janela contam como benignos.
    """
    tp = fp = fn = tn = 0
    background = 0
    names = names or [lab for lab, _, _ in windows]
    per_attack = [{"attack": name, "label": lab, "flows": 0, "detected_flows": 0,
                   "first_alert_ts": None}
                  for name, (lab, _, _) in zip(names, windows)]
    for f in flows:
        i = _attack_window(f, windows, is_background)
        if i is None and _window_index(f["flow_ts"], windows) is not None:
            background += 1
        alert = f["verdict"] == "ATTACK"
        if i is None:
            fp += alert
            tn += not alert
            continue
        tp += alert
        fn += not alert
        pa = per_attack[i]
        pa["flows"] += 1
        if alert:
            pa["detected_flows"] += 1
            if pa["first_alert_ts"] is None or f["flow_ts"] < pa["first_alert_ts"]:
                pa["first_alert_ts"] = f["flow_ts"]

    per_class = {}
    for pa, (lab, start, _) in zip(per_attack, windows):
        pa["recall"] = round(pa["detected_flows"] / pa["flows"], 4) if pa["flows"] else 0.0
        pa["detected"] = pa["detected_flows"] > 0
        # tempo até o 1º fluxo detectado, medido no início do fluxo (não na emissão)
        first = pa.pop("first_alert_ts")
        pa["time_to_first_detected_flow_s"] = round(first - start, 1) if first is not None else None
        c = per_class.setdefault(lab, {"flows": 0, "detected": 0})
        c["flows"] += pa["flows"]
        c["detected"] += pa["detected_flows"]
    for c in per_class.values():
        c["recall"] = round(c["detected"] / c["flows"], 4) if c["flows"] else 0.0

    result = _binary_scores(tp, fp, fn, tn)
    result["per_class"] = per_class
    result["per_attack"] = per_attack
    result["attacks_detected"] = sum(pa["detected"] for pa in per_attack)
    result["attacks_total"] = len(per_attack)
    result["background_in_windows"] = background
    return result


def p1_threshold_sweep(flows, windows, thresholds=None, is_background=None) -> list:
    """Precisão/revocação/FPR por fluxo para vários limiares da Fase 1. Possível
    porque o IDS grava o P1 de TODO fluxo, inclusive dos classificados benignos."""
    if thresholds is None:
        thresholds = [0.5, 0.7, 0.8, 0.9, 0.95, 0.99, 0.999]
    is_attack = [_attack_window(f, windows, is_background) is not None for f in flows]
    rows = []
    for t in thresholds:
        tp = fp = fn = tn = 0
        for f, atk in zip(flows, is_attack):
            alert = f["p1"] >= t
            if atk:
                tp += alert
                fn += not alert
            else:
                fp += alert
                tn += not alert
        row = _binary_scores(tp, fp, fn, tn)
        row["threshold"] = t
        rows.append(row)
    return rows


def multiclass_flow_metrics(flows, windows, attack_classes, label_map=None,
                            is_background=None) -> dict:
    """
    Classificação hierárquica por fluxo. Verdade = rótulo da janela onde o fluxo
    começou ('benign' fora delas). Predição = rótulo da Fase 2 se a Fase 1 alertou,
    senão 'benign' — assim um ataque perdido na Fase 1 conta como erro do sistema.
    """
    label_map = label_map or {}
    classes = list(attack_classes) + ["benign"]
    y_true, y_pred = [], []
    for f in flows:
        i = _attack_window(f, windows, is_background)
        y_true.append("benign" if i is None else windows[i][0])
        if f["verdict"] == "ATTACK" and f["p2_label"]:
            y_pred.append(label_map.get(f["p2_label"], f["p2_label"]))
        else:
            y_pred.append("benign")

    cm = defaultdict(Counter)
    for t, p in zip(y_true, y_pred):
        cm[t][p] += 1

    per_class = {}
    for cls in classes:
        tp = cm[cls][cls]
        fp = sum(cm[t][cls] for t in cm if t != cls)
        support = sum(cm[cls].values())
        fn = support - tp
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / support if support else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        per_class[cls] = {"support": support, "tp": tp, "fp": fp, "fn": fn,
                          "precision": prec, "recall": rec, "f1": f1}

    present_attacks = [c for c in attack_classes if per_class[c]["support"] > 0]
    detected = [(t, p) for f, t, p in zip(flows, y_true, y_pred)
                if t != "benign" and f["verdict"] == "ATTACK"]
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    return {
        "total": len(y_true),
        "accuracy": correct / len(y_true) if y_true else 0.0,
        "macro_f1_attacks": (statistics.mean(per_class[c]["f1"] for c in present_attacks)
                             if present_attacks else 0.0),
        "macro_f1_all": statistics.mean(
            per_class[c]["f1"] for c in present_attacks + ["benign"]),
        "p2_type_accuracy_on_detected": (sum(1 for t, p in detected if t == p) / len(detected)
                                         if detected else 0.0),
        "p2_low_conf_flows": sum(1 for f in flows if f["verdict"] == "ATTACK" and f["low_conf"]),
        "per_class": per_class,
        "confusion": {t: dict(row) for t, row in cm.items()},
    }


def emission_delay_stats(flows) -> dict:
    """Atraso entre o início do fluxo (flow_ts) e a sua emissão no log (HH:MM:SS
    do relógio da VIM, assumido UTC; resolução de 1 s). Inclui o idle_timeout do
    extrator + a fila sob saturação — é exatamente o vazamento que a métrica por
    fluxo neutraliza, reportado aqui só como diagnóstico."""
    delays = []
    for f in flows:
        start = datetime.fromtimestamp(f["flow_ts"], timezone.utc)
        start_sod = start.hour * 3600 + start.minute * 60 + start.second
        delays.append((f["emit_sec"] - start_sod) % 86400)
    if not delays:
        return {}
    delays.sort()
    return {
        "n": len(delays),
        "median_s": statistics.median(delays),
        "p95_s": delays[min(len(delays) - 1, int(0.95 * len(delays)))],
        "max_s": delays[-1],
        "mean_s": round(statistics.mean(delays), 1),
    }


def conf_stats(values):
    if not values:
        return {}
    return {
        "n": len(values),
        "mean": round(statistics.mean(values), 4),
        "median": round(statistics.median(values), 4),
        "stdev": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


# ─── Pretty printers ─────────────────────────────────────────────────────────

def _print_cm2(m: dict, title: str) -> None:
    print(f"\n  ── {title} ──")
    print(f"                    Pred: Attack  Pred: Benign")
    print(f"  True: Attack       {m['TP']:>9}    {m['FN']:>9}   ({m['TP'] + m['FN']} fluxos de ataque)")
    print(f"  True: Benign       {m['FP']:>9}    {m['TN']:>9}   ({m['FP'] + m['TN']} fluxos benignos)")
    print(f"\n  Accuracy   : {m['accuracy']:.4f}  ({m['TP'] + m['TN']}/{m['total']})")
    print(f"  Precision  : {m['precision']:.4f}  ({m['TP']}/{m['TP'] + m['FP']})")
    print(f"  Recall/TPR : {m['recall']:.4f}  ({m['TP']}/{m['TP'] + m['FN']})")
    print(f"  F1-score   : {m['f1']:.4f}")
    print(f"  FPR        : {m['fpr']:.6f}  ({m['FP']}/{m['FP'] + m['TN']})")


def print_binary_report(bm: dict, sweep: list, delay: dict, p1_stats: dict,
                        title: str = "BINARY IDS METRICS (por fluxo)") -> None:
    print("\n╔══════════════════════════════════════════════════════════╗")
    print(f"║   {title:<55}║")
    print("╚══════════════════════════════════════════════════════════╝")
    print("  Rótulo de cada fluxo = janela onde ele COMEÇOU (flow_ts), não a hora")
    print("  de emissão — imune ao atraso do IDS sob flood.")
    print(f"  Fluxos de fundo dentro das janelas (contados como benignos): "
          f"{bm['background_in_windows']}")
    _print_cm2(bm, "Matriz 2×2 por fluxo (Fase 1)")

    print(f"\n  ── Detecção por ataque ({bm['attacks_detected']}/{bm['attacks_total']} ataques com ≥1 fluxo detectado) ──")
    print(f"  {'Ataque':<14} {'Fluxos':>8} {'Detect.':>8} {'Recall':>8}  {'1º fluxo detect.':>16}")
    for pa in bm["per_attack"]:
        ttd = pa["time_to_first_detected_flow_s"]
        ttd_s = f"+{ttd:.1f} s" if ttd is not None else "—"
        bar = '█' * int(20 * pa['recall']) + '░' * (20 - int(20 * pa['recall']))
        print(f"  {pa['attack']:<14} {pa['flows']:>8} {pa['detected_flows']:>8} "
              f"{pa['recall']:>7.1%}  {ttd_s:>16}  {bar}")

    if sweep:
        print(f"\n  ── Varredura do limiar P1 (por fluxo) ──")
        print(f"  {'Limiar':>8}  {'Prec':>8}  {'Recall':>8}  {'F1':>8}  {'FPR':>10}")
        for r in sweep:
            print(f"  {r['threshold']:>8.3f}  {r['precision']:>8.4f}  {r['recall']:>8.4f}  "
                  f"{r['f1']:>8.4f}  {r['fpr']:>10.6f}")

    if delay:
        print(f"\n  Atraso de emissão (diagnóstico do vazamento, não entra na métrica):")
        print(f"    mediana {delay['median_s']} s | p95 {delay['p95_s']} s | máx {delay['max_s']} s "
              f"(n={delay['n']})")
    print(f"\n  P1 dos fluxos alertados: {p1_stats}")


def print_multiclass_report(mm: dict, attack_classes: list, label_map=None) -> None:
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║   MULTICLASS IDS METRICS (por fluxo, hierárquico)        ║")
    print("╚══════════════════════════════════════════════════════════╝")
    if label_map:
        print(f"  (label map aplicado: {label_map})")
    print("  Predição = rótulo da Fase 2 se a Fase 1 alertou; senão 'benign'.")
    print(f"\n  Fluxos avaliados            : {mm['total']}")
    print(f"  Accuracy (sistema)          : {mm['accuracy']:.4f}")
    print(f"  Macro F1 (classes de ataque): {mm['macro_f1_attacks']:.4f}")
    print(f"  Macro F1 (ataque + benign)  : {mm['macro_f1_all']:.4f}")
    print(f"  Acerto do tipo (P2) nos fluxos de ataque detectados: "
          f"{mm['p2_type_accuracy_on_detected']:.4f}")
    print(f"  Fluxos com P2 de baixa confiança (→ P3): {mm['p2_low_conf_flows']}")

    classes = list(attack_classes) + ["benign"]
    print(f"\n  {'Classe':<12} {'Suporte':>8} {'TP':>7} {'FP':>7} {'FN':>7} {'Prec':>7} {'Rec':>7} {'F1':>7}")
    print("  " + "─" * 70)
    for cls in classes:
        r = mm["per_class"][cls]
        if r["support"] == 0 and r["fp"] == 0:
            continue
        print(f"  {cls:<12} {r['support']:>8} {r['tp']:>7} {r['fp']:>7} {r['fn']:>7} "
              f"{r['precision']:>7.3f} {r['recall']:>7.3f} {r['f1']:>7.3f}")

    cm = mm["confusion"]
    preds = sorted({p for row in cm.values() for p in row})
    print("\n  Matriz de confusão (linhas = verdade, colunas = predição):")
    header = f"  {'true \\ pred':<12}" + "".join(f"{c:>11}" for c in preds)
    print(header)
    print("  " + "─" * (len(header) - 2))
    for true_cls in classes:
        row = cm.get(true_cls)
        if not row:
            continue
        print(f"  {true_cls:<12}" + "".join(f"{row.get(c, 0):>11}" for c in preds))


def print_energy_report(energy: dict, inference: dict, p_idle: float, p_max: float) -> None:
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║   ENERGIA ESTIMADA (modelo linear CPU)                  ║")
    print("╚══════════════════════════════════════════════════════════╝")
    if not energy:
        print("\n  [sem linhas SYS_SNAPSHOT no log — seção de energia indisponível]")
        return
    print(f"\n  P_idle = {p_idle:.1f} W | P_max = {p_max:.1f} W")
    print(f"  Duração da sessão        : {energy['duration_s']:.0f} s")
    print(f"  Energia total            : {energy['total_energy_j']:.1f} J  "
          f"({energy['total_energy_wh']:.4f} Wh)")
    print(f"  Potência média           : {energy['avg_power_w']:.2f} W")
    a, i = energy["attack"], energy["idle"]
    print(f"    Durante ataques        : {a['energy_j']:.1f} J em {a['duration_s']:.0f} s "
          f"({a['avg_power_w']:.2f} W médio)")
    print(f"    Fora de ataques (idle) : {i['energy_j']:.1f} J em {i['duration_s']:.0f} s "
          f"({i['avg_power_w']:.2f} W médio)")
    if inference:
        print("\n  Energia de inferência (aprox., via [SUMMARY] e2e_ms agregado):")
        print(f"    {inference['mj_per_flow']:.4f} mJ/flow × {inference['flows']} flows "
              f"= {inference['total_j']:.2f} J ({inference['pct_of_session_energy']:.2f}% da energia total)")
    else:
        print("\n  Energia de inferência    : [sem bloco SUMMARY — sessão não finalizada graciosamente]")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ids",    required=True, help="IDS log file path")
    ap.add_argument("--report", required=True, help="Orchestrator JSON report path")
    ap.add_argument("--mode",   required=True, choices=["multiclass", "binary"],
                    help="Log type: 'multiclass' (Phase1+2) or 'binary' (Phase1 only)")
    ap.add_argument("--tz-offset", type=float, default=3,
                    help="Hours to add to orchestrator timestamps to get UTC (default: 3 for BRT)")
    ap.add_argument("--clock-offset", type=float, default=0.0,
                    help="Relógio da VIM − relógio do PC, em segundos (medido pelo "
                         "run_experiment.sh). Alinha as janelas ao flow_ts. Padrão: 0")
    ap.add_argument("--target-ip", default=None,
                    help="IP da VIM 4. Com --attacker-ips, liga o filtro de endpoints: "
                         "fluxos de fundo (multicast, outros hosts da LAN) que começam "
                         "numa janela contam como benignos")
    ap.add_argument("--attacker-ips", default="",
                    help="IPs do PC atacante na LAN, separados por vírgula")
    ap.add_argument("--lan", default=None,
                    help="CIDR da LAN do testbed (padrão: /24 do --target-ip)")
    ap.add_argument("--idle-slack", type=int, default=30,
                    help="Só para a divisão de ENERGIA ataque × ocioso (a carga de CPU "
                         "do dreno pós-flood é custo do ataque). Não afeta a detecção.")
    ap.add_argument("--window-guard", type=float, default=0.0,
                    help="Folga simétrica (s) nas bordas das janelas de ground-truth, "
                         "para corrigir a defasagem de registro do orquestrador: ele grava "
                         "start_time/end_time depois de a ferramenta já estar disparando, "
                         "então fluxos de ataque reais começam alguns segundos antes/depois "
                         "do intervalo anotado. Continua rotulando pelo flow_ts (sem hora de "
                         "emissão). Padrão: 0 (janela estrita, sem calibração).")
    ap.add_argument("--output", default=None,
                    help="Optional path to save JSON summary")
    ap.add_argument("--label-map", nargs="*", default=[],
                    metavar="FROM=TO",
                    help="Merge ground-truth labels before scoring, e.g. --label-map ddos=dos")
    ap.add_argument("--p-idle", type=float, default=None,
                    help="Override do P_idle (W); por padrão vem do power_model_vim4.json")
    ap.add_argument("--p-max", type=float, default=None,
                    help="Override do P_max (W); por padrão vem do power_model_vim4.json")
    ap.add_argument("--power-model", default=None,
                    help="Caminho do power_model_vim4.json (padrão: constants/power_model_vim4.json)")
    args = ap.parse_args()

    label_map = {}
    for item in (args.label_map or []):
        src, _, dst = item.partition("=")
        if src and dst:
            label_map[src.strip()] = dst.strip()

    attack_classes = build_attack_classes(label_map)
    flow_windows = parse_windows_epoch(args.report, args.tz_offset, args.clock_offset, label_map)
    window_names = [lab for lab, _, _ in
                    parse_windows_epoch(args.report, args.tz_offset, args.clock_offset)]
    if args.window_guard:
        g = args.window_guard
        flow_windows = [(lab, s - g, e + g) for lab, s, e in flow_windows]
    flows = parse_flow_log(args.ids, args.mode)
    if not flows:
        sys.exit(f"[!] Nenhuma linha de fluxo com flow_ts em {args.ids}. Logs do formato "
                 "antigo (só alertas, sem [FLOWS]) não servem para a métrica por fluxo — "
                 "rode o IDS atualizado.")

    attacker_ips = [a.strip() for a in args.attacker_ips.split(",") if a.strip()]
    is_bg = None
    if args.target_ip and attacker_ips:
        is_bg = make_background_filter(args.target_ip, attacker_ips, args.lan)
    else:
        print("[!] Sem --target-ip/--attacker-ips: todo fluxo que começa numa janela "
              "conta como ataque (inclusive tráfego de fundo da LAN).")

    # Janelas em segundos-do-dia (relógio de emissão) — só para a energia.
    energy_windows = parse_orchestrator(args.report, int(args.tz_offset), args.idle_slack,
                                        label_map=label_map)

    # Recursos (CPU/RAM) a partir dos SYS_SNAPSHOT — não dependem do bloco
    # [SUMMARY] (que pode faltar se o IDS for encerrado à força).
    snap_full = sorted(parse_snapshot_resources(args.ids))
    resources = resource_summary(snap_full)

    bm = binary_flow_metrics(flows, flow_windows, window_names, is_background=is_bg)
    sweep = p1_threshold_sweep(flows, flow_windows, is_background=is_bg)
    delay = emission_delay_stats(flows)
    p1_alerts = conf_stats([f["p1"] for f in flows if f["verdict"] == "ATTACK"])
    attack_seconds = sum(end - start for _, start, end in flow_windows)
    alerts = bm["TP"] + bm["FP"]

    print_binary_report(bm, sweep, delay, p1_alerts,
                        title="BINARY IDS METRICS (por fluxo)" if args.mode == "binary"
                        else "FASE 1 (binária) — por fluxo")
    summary = {
        "mode": args.mode,
        "metric": "per-flow, labelled by flow start (flow_ts) — leak-independent",
        "label_map": label_map,
        "ids_log": args.ids,
        "orchestrator_report": args.report,
        "clock_offset_s": args.clock_offset,
        "window_guard_s": args.window_guard,
        "ground_truth": {
            "target_ip": args.target_ip, "attacker_ips": attacker_ips, "lan": args.lan,
            "endpoint_filter": is_bg is not None,
            "background_flows_in_windows": bm["background_in_windows"],
        },
        "flows_total": len(flows),
        "binary": bm,
        "p1_threshold_sweep": sweep,
        "p1_confidence_alerts": p1_alerts,
        "emission_delay_s": delay,
        "resources": resources,
        "throughput": {
            "flows_total": len(flows),
            "alerts": alerts,
            "attack_seconds": round(attack_seconds, 1),
            "attack_flows_per_s": round((bm["TP"] + bm["FN"]) / attack_seconds, 2)
            if attack_seconds else 0.0,
        },
    }

    if args.mode == "multiclass":
        mm = multiclass_flow_metrics(flows, flow_windows, attack_classes, label_map,
                                     is_background=is_bg)
        print_multiclass_report(mm, attack_classes, label_map)
        summary["multiclass"] = mm
        summary["p2_confidence_alerts"] = conf_stats(
            [f["p2_conf"] for f in flows if f["verdict"] == "ATTACK" and f["p2_conf"] is not None])

    power_model = load_power_model(args.power_model)
    # CLI sobrepõe o modelo só se o usuário passou valores explícitos.
    if args.p_idle is not None:
        power_model["p_idle_w"] = args.p_idle
    if args.p_max is not None:
        power_model["p_max_w"] = args.p_max
    p_idle = power_model["p_idle_w"]
    p_max = power_model["p_max_w"]

    samples = sorted(parse_snapshot_log(args.ids))
    energy = compute_session_energy(samples, energy_windows, p_idle, p_max)
    band = energy_band(samples, energy_windows, power_model) if energy else {}
    summary_block = parse_summary_block(args.ids)
    inference_energy = (
        compute_inference_energy(summary_block, energy["total_energy_j"], p_idle, p_max)
        if energy else {}
    )
    print_energy_report(energy, inference_energy, p_idle, p_max)
    if band:
        lo = band["low"]["total_energy_j"]
        hi = band["high"]["total_energy_j"]
        print(f"  Banda de sensibilidade   : {lo:.1f}–{hi:.1f} J "
              f"(P_idle {power_model['sensitivity']['p_idle_low']}–{power_model['sensitivity']['p_idle_high']} W, "
              f"P_max {power_model['sensitivity']['p_max_low']}–{power_model['sensitivity']['p_max_high']} W)")
        print(f"  [estimativa — sem medição direta; ver power_model_vim4.json]")
    if energy:
        summary["energy"] = {
            "model": power_model,
            "p_idle_w": p_idle,
            "p_max_w": p_max,
            "session": energy,
            "band": band or None,
            "inference": inference_energy or None,
        }

    # ── Recursos (derivados dos SYS_SNAPSHOT, sem depender de [SUMMARY]) ────────
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║   RECURSOS (CPU/RAM) E THROUGHPUT                       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    if resources:
        print(f"\n  Amostras SYS_SNAPSHOT     : {resources['samples']}")
        print(f"  CPU média / máxima        : {resources['cpu_avg_pct']:.1f}% / {resources['cpu_max_pct']:.1f}%")
        print(f"  RAM média / máxima        : {resources['ram_avg_mb']:.0f} MB / {resources['ram_max_mb']} MB")
    else:
        print("\n  [sem SYS_SNAPSHOT no log]")
    thr = summary.get("throughput", {})
    if thr:
        print(f"  Fluxos classificados      : {thr['flows_total']:,} ({thr['alerts']:,} alertas)")
        print(f"  Fluxos de ataque          : {thr['attack_flows_per_s']} fluxos/s em "
              f"{thr['attack_seconds']:.0f} s de janelas")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\n  → Summary saved to {args.output}")

    return summary


if __name__ == "__main__":
    main()
