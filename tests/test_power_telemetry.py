import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from constants.power_telemetry import (
    load_power_model, estimate_power_w, read_soc_temp_c, read_cluster_freqs_mhz,
)


def test_estimate_endpoints():
    m = {"p_idle_w": 2.0, "p_max_w": 10.0}
    assert estimate_power_w(0, m) == 2.0
    assert estimate_power_w(100, m) == 10.0
    assert estimate_power_w(50, m) == 6.0
    # clamp
    assert estimate_power_w(-5, m) == 2.0
    assert estimate_power_w(150, m) == 10.0


def test_load_model_fallback_when_missing():
    m = load_power_model("/nonexistent/path/model.json")
    assert "p_idle_w" in m and "p_max_w" in m and "sensitivity" in m


def test_load_model_from_file():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"p_idle_w": 3.0, "p_max_w": 9.0,
                   "sensitivity": {"p_idle_low": 2.0, "p_idle_high": 4.0,
                                   "p_max_low": 7.0, "p_max_high": 11.0}}, f)
        path = f.name
    m = load_power_model(path)
    assert m["p_idle_w"] == 3.0 and m["p_max_w"] == 9.0


def test_read_temp_and_freq_from_fake_sysfs():
    d = tempfile.mkdtemp()
    # fake thermal
    z = os.path.join(d, "thermal_zone0"); os.makedirs(z)
    open(os.path.join(z, "type"), "w").write("soc_thermal\n")
    open(os.path.join(z, "temp"), "w").write("43300\n")
    assert read_soc_temp_c(base=d) == 43.3
    # fake cpufreq
    c = tempfile.mkdtemp()
    p0 = os.path.join(c, "policy0"); os.makedirs(p0)
    open(os.path.join(p0, "scaling_cur_freq"), "w").write("1392000\n")
    freqs = read_cluster_freqs_mhz(base=c)
    assert freqs["policy0"] == 1392


def test_read_temp_missing_returns_none():
    assert read_soc_temp_c(base="/nonexistent") is None
    assert read_cluster_freqs_mhz(base="/nonexistent") == {}


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); print(f"  ok: {name}")
    print("ALL TESTS PASSED")
