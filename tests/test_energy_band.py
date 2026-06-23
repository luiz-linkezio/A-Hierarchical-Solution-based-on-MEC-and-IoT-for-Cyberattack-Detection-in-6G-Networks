import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from ids_metrics import energy_band


def test_band_orders_low_central_high():
    # 100s de "ataque" a 100% CPU, janela cobrindo tudo
    samples = [(t, 100.0) for t in range(0, 101)]
    windows = [("dos", 0, 200)]
    model = {"p_idle_w": 2.0, "p_max_w": 10.0,
             "sensitivity": {"p_idle_low": 1.5, "p_idle_high": 2.5,
                             "p_max_low": 8.0, "p_max_high": 12.0}}
    b = energy_band(samples, windows, model)
    assert b["low"]["total_energy_j"] < b["central"]["total_energy_j"] < b["high"]["total_energy_j"]
    # a 100% CPU, central = p_max * duração ≈ 10 W * 100 s = 1000 J
    assert abs(b["central"]["total_energy_j"] - 1000.0) < 20.0


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); print(f"  ok: {name}")
    print("ALL TESTS PASSED")
