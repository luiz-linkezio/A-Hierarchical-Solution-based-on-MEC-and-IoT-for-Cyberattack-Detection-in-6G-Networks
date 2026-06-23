#!/usr/bin/env python3
"""calibrate_power.py — Calibra o modelo de energia da VIM 4 (estimativa).

A VIM 4 não mede potência por SW. Este script mede a UTILIZAÇÃO de CPU em dois
regimes (idle e carga total via `stress`), registra temperatura/frequência por
cluster como proveniência, e fixa os endpoints de potência (P_idle/P_max)
ancorados na literatura do Amlogic A311D2 / Khadas VIM 4 (faixa board-level por
USB-C PD). NÃO é medição direta — os watts vêm da literatura, não de sensor.

Rodar NA VIM 4:
    python3 scripts/calibrate_power.py --out constants/power_model_vim4.json
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from constants.power_telemetry import read_soc_temp_c, read_cluster_freqs_mhz

# Âncoras de literatura (board-level, sem periféricos), Khadas VIM 4 / A311D2.
# Faixa conservadora; reportada com banda de sensibilidade. Ver doc de metodologia.
DEFAULT_P_IDLE_W = 2.5
DEFAULT_P_MAX_W = 9.0
SENS = {"p_idle_low": 2.0, "p_idle_high": 3.0, "p_max_low": 7.0, "p_max_high": 11.0}


def _mean_cpu(seconds: int) -> float:
    import psutil
    psutil.cpu_percent(interval=None)
    samples = []
    t_end = time.time() + seconds
    while time.time() < t_end:
        time.sleep(2.0)
        samples.append(psutil.cpu_percent(interval=None))
    return round(sum(samples) / len(samples), 2) if samples else 0.0


def build_power_model(idle_cpu_pct, load_cpu_pct, p_idle_w, p_max_w, telemetry):
    return {
        "soc": "Amlogic A311D2",
        "method": ("linear CPU-utilization model; P_idle/P_max anchored to "
                   "Khadas VIM 4 board-level power envelope (literature) + "
                   "on-board idle/stress CPU benchmark"),
        "p_idle_w": p_idle_w,
        "p_max_w": p_max_w,
        "sensitivity": dict(SENS),
        "provenance": {
            "idle_cpu_pct": idle_cpu_pct,
            "load_cpu_pct": load_cpu_pct,
            **telemetry,
        },
        "calibrated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "notes": ("ESTIMATIVA — VIM 4 não expõe RAPL/INA226/hwmon; watts ancorados "
                  "em literatura, não medidos. Reportar com banda de sensibilidade."),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..",
                                                  "constants", "power_model_vim4.json"))
    ap.add_argument("--p-idle", type=float, default=DEFAULT_P_IDLE_W)
    ap.add_argument("--p-max", type=float, default=DEFAULT_P_MAX_W)
    ap.add_argument("--seconds", type=int, default=60)
    ap.add_argument("--cores", type=int, default=os.cpu_count() or 8)
    args = ap.parse_args()

    print(f"[1/2] Medindo idle por {args.seconds}s (não use a máquina)...")
    idle_temp = read_soc_temp_c()
    idle_freqs = read_cluster_freqs_mhz()
    idle_cpu = _mean_cpu(args.seconds)

    print(f"[2/2] Medindo carga total (stress --cpu {args.cores}) por {args.seconds}s...")
    stress = subprocess.Popen(["stress", "--cpu", str(args.cores)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        load_cpu = _mean_cpu(args.seconds)
        load_temp = read_soc_temp_c()
        load_freqs = read_cluster_freqs_mhz()
    finally:
        stress.terminate()
        try:
            stress.wait(timeout=5)
        except Exception:
            stress.kill()

    model = build_power_model(
        idle_cpu, load_cpu, args.p_idle, args.p_max,
        {"idle_temp_c": idle_temp, "load_temp_c": load_temp,
         "idle_freqs": idle_freqs, "load_freqs": load_freqs},
    )
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(model, f, indent=2)
    print(f"\nModelo salvo em {out}")
    print(json.dumps(model, indent=2))


if __name__ == "__main__":
    main()
