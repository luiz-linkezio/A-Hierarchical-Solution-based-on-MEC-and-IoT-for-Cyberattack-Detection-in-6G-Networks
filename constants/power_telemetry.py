"""Telemetria de energia para o nó de borda (VIM 4).

A VIM 4 (Amlogic A311D2) NÃO expõe RAPL/INA226/hwmon/power_supply, então a
potência é ESTIMADA por um modelo linear de utilização de CPU, com endpoints
(P_idle/P_max) ancorados em literatura + benchmark on-board (ver
scripts/calibrate_power.py e docs/experimentos/2026-06-19-vim4-revalidacao.md).
Não é medição direta.
"""
import glob
import json
import os

# Fallback usado quando constants/power_model_vim4.json ainda não existe.
_DEFAULT_MODEL = {
    "soc": "Amlogic A311D2 (assumed)",
    "method": "linear CPU-utilization model (uncalibrated fallback)",
    "p_idle_w": 2.0,
    "p_max_w": 11.0,
    "sensitivity": {"p_idle_low": 1.5, "p_idle_high": 2.5,
                    "p_max_low": 8.0, "p_max_high": 12.0},
    "calibrated_at": None,
    "notes": "fallback — VIM 4 não expõe RAPL/INA226/hwmon",
}


def _default_model_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "power_model_vim4.json")


def load_power_model(path: str | None = None) -> dict:
    p = path or os.environ.get("POWER_MODEL_PATH") or _default_model_path()
    try:
        with open(p) as f:
            m = json.load(f)
        float(m["p_idle_w"]); float(m["p_max_w"])  # valida
        m.setdefault("sensitivity", dict(_DEFAULT_MODEL["sensitivity"]))
        return m
    except Exception:
        return dict(_DEFAULT_MODEL)


def estimate_power_w(cpu_pct: float, model: dict) -> float:
    pi = float(model["p_idle_w"])
    pm = float(model["p_max_w"])
    cpu = max(0.0, min(100.0, float(cpu_pct)))
    return pi + (pm - pi) * cpu / 100.0


def read_soc_temp_c(base: str = "/sys/class/thermal") -> float | None:
    try:
        for zone in sorted(glob.glob(os.path.join(base, "thermal_zone*"))):
            try:
                with open(os.path.join(zone, "type")) as f:
                    if f.read().strip() == "soc_thermal":
                        with open(os.path.join(zone, "temp")) as ft:
                            return int(ft.read().strip()) / 1000.0
            except Exception:
                continue
    except Exception:
        pass
    return None


def read_cluster_freqs_mhz(base: str = "/sys/devices/system/cpu/cpufreq") -> dict:
    out: dict = {}
    try:
        for pol in sorted(glob.glob(os.path.join(base, "policy*"))):
            try:
                with open(os.path.join(pol, "scaling_cur_freq")) as f:
                    out[os.path.basename(pol)] = int(f.read().strip()) // 1000
            except Exception:
                continue
    except Exception:
        pass
    return out
