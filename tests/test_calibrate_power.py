import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from calibrate_power import build_power_model


def test_build_model_shape():
    m = build_power_model(
        idle_cpu_pct=3.1, load_cpu_pct=99.4,
        p_idle_w=2.5, p_max_w=9.0,
        telemetry={"idle_temp_c": 43.0, "load_temp_c": 61.0,
                   "idle_freqs": {"policy0": 1000}, "load_freqs": {"policy0": 2208}},
    )
    assert m["p_idle_w"] == 2.5 and m["p_max_w"] == 9.0
    for k in ("p_idle_low", "p_idle_high", "p_max_low", "p_max_high"):
        assert k in m["sensitivity"]
    assert m["sensitivity"]["p_idle_low"] <= m["p_idle_w"] <= m["sensitivity"]["p_idle_high"]
    assert m["sensitivity"]["p_max_low"] <= m["p_max_w"] <= m["sensitivity"]["p_max_high"]
    assert m["provenance"]["idle_cpu_pct"] == 3.1
    assert m["provenance"]["load_cpu_pct"] == 99.4
    assert m["calibrated_at"]  # iso string não vazia


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); print(f"  ok: {name}")
    print("ALL TESTS PASSED")
