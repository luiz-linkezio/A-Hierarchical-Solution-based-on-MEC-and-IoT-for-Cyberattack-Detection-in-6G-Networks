#!/usr/bin/env python3
"""Time-series figures per testbed experiment (Session A: binary, Session B: multiclass).
X axis = experiment time. Panels: alert rate, CPU%, RAM, temperature.
Attack windows shaded from the orchestrator ground-truth report (BRT+3h -> UTC,
matching the VIM-4 UTC clock in the IDS log)."""
import json, re, sys
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

BASE = "/home/linkezio/Projects/A Hierarchical MEC and IoT Solution for Cyber-Attack Detection in 6G Networks"
TZ_OFFSET_H = 3  # BRT -> UTC, same convention as scripts/ids_metrics.py

# ---- design tokens (dataviz reference palette, light surface) ----
INK   = "#0b0b0b"; INK2 = "#52514e"; MUTED = "#898781"; GRID = "#e1e0d9"
SURF  = "#ffffff"
C_ALERT = "#2a78d6"; C_CPU = "#eb6834"; C_RAM = "#1baf7a"; C_TEMP = "#4a3aa7"
ATTACK_SHADE = "#e34948"
# categorical slots for predicted attack types (validated CVD-safe order)
CAT = {"recon":"#2a78d6","dos":"#1baf7a","malware":"#eda100","bruteforce":"#4a3aa7",
       "web":"#e34948","mitm":"#e87ba4","spoofing":"#eb6834","ddos":"#008300"}

def sod(dt):  # seconds of day
    return dt.hour*3600 + dt.minute*60 + dt.second + dt.microsecond/1e6

def to_sec(hms):
    h,m,s = hms.split(":"); return int(h)*3600+int(m)*60+int(s)

def load_windows(report_path):
    rep = json.load(open(report_path))
    out = []
    for atk in rep["attacks"]:
        st = datetime.fromisoformat(atk["start_time"]) + timedelta(hours=TZ_OFFSET_H)
        en = datetime.fromisoformat(atk["end_time"])   + timedelta(hours=TZ_OFFSET_H)
        out.append((atk["attack"], sod(st), sod(en)))
    return out

_SNAP = re.compile(r'^\[SYS_SNAPSHOT\] (\d{2}:\d{2}:\d{2})\s+CPU\s+([\d.]+)%')
_RAM  = re.compile(r'\((\d+) MB\)')
_PWR  = re.compile(r'Power\s+([\d.]+)\s*W')
_TMP  = re.compile(r'Temp\s+([\d.]+)C')

def load_snapshots(ids_log):
    t, cpu, ram, temp = [], [], [], []
    for line in open(ids_log, errors="ignore"):
        m = _SNAP.match(line)
        if not m: continue
        ts = to_sec(m.group(1))
        rm = _RAM.search(line); tm = _TMP.search(line)
        t.append(ts); cpu.append(float(m.group(2)))
        ram.append(int(rm.group(1)) if rm else np.nan)
        temp.append(float(tm.group(1)) if tm else np.nan)
    return (np.array(t,float), np.array(cpu,float), np.array(ram,float), np.array(temp,float))

def load_alerts(ids_log, multiclass):
    """Return dict: label -> {sec: count}. Binary => single 'attack' series."""
    per = defaultdict(lambda: defaultdict(int))
    for line in open(ids_log, errors="ignore"):
        if not re.match(r'^\d{2}:\d{2}:\d{2}\t', line): continue
        f = line.rstrip("\n").split("\t")
        if len(f) > 2 and f[2] in ("ATTACK", "BENIGN"):
            # formato [FLOWS]: posiciona o alerta no início do fluxo (flow_ts, UTC)
            if f[2] != "ATTACK": continue
            sec = int(sod(datetime.fromtimestamp(float(f[1]), timezone.utc)))
            lab = f[4] if multiclass else "attack"
            per[lab][sec] += 1
            continue
        sec = to_sec(f[0])
        lab = f[2] if multiclass and len(f) > 2 else "attack"
        lab = lab.split("→")[-1].strip() if multiclass else lab
        per[lab][sec] += 1
    return per

def render(session_report, ids_log, multiclass, title, out_png):
    windows = load_windows(session_report)
    t, cpu, ram, temp = load_snapshots(ids_log)
    alerts = load_alerts(ids_log, multiclass)

    t0 = t.min()
    span_end = t.max() - t0
    def rel(x): return x - t0

    fig, allax = plt.subplots(5, 1, figsize=(11, 9.6), sharex=True,
                              gridspec_kw={"height_ratios":[0.34,1.5,1,1,1], "hspace":0.16})
    ribbon = allax[0]; axes = allax[1:]
    fig.patch.set_facecolor(SURF)
    for ax in axes:
        ax.set_facecolor(SURF)
        for s in ("top","right"): ax.spines[s].set_visible(False)
        for s in ("left","bottom"):
            ax.spines[s].set_color("#c3c2b7"); ax.spines[s].set_linewidth(1)
        ax.grid(True, axis="y", color=GRID, linewidth=0.8, zorder=0)
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.margins(x=0)

    # --- attack ribbon (dedicated strip) + shading across metric panels ---
    for s in ("top","right","left","bottom"): ribbon.spines[s].set_visible(False)
    ribbon.set_yticks([]); ribbon.margins(x=0)
    ribbon.tick_params(bottom=False, labelbottom=False)  # don't touch shared xticks
    ribbon.set_ylim(0,1)
    ribbon.set_ylabel("Ataques", color=INK2, fontsize=9.5, rotation=0,
                      ha="right", va="center", labelpad=14)
    for lab, st, en in windows:
        a, b = rel(st), rel(en)
        ribbon.axvspan(a, b, ymin=0.12, ymax=0.88, color=ATTACK_SHADE, alpha=0.16, lw=0)
        ribbon.text((a+b)/2, 0.5, lab.upper(), ha="center", va="center",
                    fontsize=7.2, color="#b5322f", fontweight="bold", rotation=0)
        for ax in axes:
            ax.axvspan(a, b, color=ATTACK_SHADE, alpha=0.06, zorder=0, lw=0)

    ax_top = axes[0]
    # --- Panel 1: alert rate ---
    if multiclass:
        secs = sorted({s for d in alerts.values() for s in d})
        grid = np.arange(int(min(secs)), int(max(secs))+1) if secs else np.array([])
        order = [k for k in ["recon","dos","malware","bruteforce","web","mitm","spoofing","ddos"]
                 if k in alerts]
        stacks = [np.array([alerts[k].get(int(s),0) for s in grid]) for k in order]
        ax_top.stackplot([rel(s) for s in grid], *stacks,
                         colors=[CAT.get(k,"#888") for k in order],
                         labels=[k for k in order], zorder=3, edgecolor=SURF, linewidth=0.15)
        handles, labels = ax_top.get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", ncol=len(order), fontsize=8.5,
                   frameon=False, labelcolor=INK2, handlelength=1.1, columnspacing=1.3,
                   handletextpad=0.4, bbox_to_anchor=(0.5, 0.008),
                   title="Tipo de ataque predito pela Fase 2", title_fontsize=8.5)
        ax_top.set_ylabel("Alertas/s\n(por tipo predito)", color=INK2, fontsize=9.5)
    else:
        secs = alerts["attack"]
        grid = np.arange(int(min(secs)), int(max(secs))+1) if secs else np.array([])
        y = np.array([secs.get(int(s),0) for s in grid])
        xs = np.array([rel(s) for s in grid])
        ax_top.fill_between(xs, y, color=C_ALERT, alpha=0.18, zorder=2)
        ax_top.plot(xs, y, color=C_ALERT, lw=1.4, zorder=3)
        ax_top.set_ylabel("Alertas/s", color=INK2, fontsize=9.5)
    fig.suptitle(title, color=INK, fontsize=13.5, fontweight="bold", x=0.062, ha="left", y=0.968)

    # --- Panels 2-4: CPU, RAM, Temp ---
    for ax, y, col, lbl in [
        (axes[1], cpu,  C_CPU,  "CPU (%)"),
        (axes[2], ram,  C_RAM,  "RAM (MB)"),
        (axes[3], temp, C_TEMP, "Temperatura (°C)")]:
        xs = rel(t)
        ax.plot(xs, y, color=col, lw=1.5, zorder=3)
        ax.fill_between(xs, y, np.nanmin(y), color=col, alpha=0.12, zorder=2)
        ax.set_ylabel(lbl, color=INK2, fontsize=9.5)

    axes[-1].set_xlabel("Tempo decorrido do experimento (mm:ss)", color=INK2, fontsize=10, labelpad=6)
    axes[-1].xaxis.set_major_formatter(FuncFormatter(
        lambda v,_: f"{int(v//60):02d}:{int(v%60):02d}"))
    axes[-1].tick_params(labelbottom=True)
    axes[-1].set_xlim(0, span_end)

    bottom = 0.145 if multiclass else 0.075
    fig.subplots_adjust(bottom=bottom, top=0.93, left=0.09, right=0.985)
    fig.text(0.985, 0.004,
             "Faixas vermelhas = janelas de ataque (ground truth). Fonte: log do IDS na VIM-4 + relatório do orquestrador.",
             ha="right", va="bottom", fontsize=7.3, color=MUTED)
    fig.savefig(out_png, dpi=160, facecolor=SURF)
    print(f"wrote {out_png}  | snapshots={len(t)}  windows={len(windows)}  span={span_end:.0f}s")

if __name__ == "__main__":
    render(f"{BASE}/logs/session_a_20260930_014420/report_20260930_021128.json",
           f"{BASE}/logs/session_a_20260930_014420/binary_ids_run_20260930_044432.log",
           multiclass=False,
           title="Experimento A — IDS binário (Fase 1) no nó de borda VIM-4",
           out_png=f"{sys.argv[1]}/timeseries_session_a_binary.png")
    render(f"{BASE}/logs/session_b_20260930_014420/report_20260930_023949.json",
           f"{BASE}/logs/session_b_20260930_014420/ids_run_20260930_051303.log",
           multiclass=True,
           title="Experimento B — IDS hierárquico (Fases 1+2) no nó de borda VIM-4",
           out_png=f"{sys.argv[1]}/timeseries_session_b_multiclass.png")
