import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import attack_orchestrator as ao


def _attacks():
    return ao.build_attacks("10.9.9.5", 60, None, "eth9", "10.9.9.1",
                            "ssh -i /k luiz_henrique@10.9.9.5")


def test_bruteforce_no_early_stop():
    cmds = _attacks()["bruteforce"]["cmds"]
    assert len(cmds) == 3
    assert all(not c.rstrip().endswith("-f") and " -f " not in c for c in cmds)
    assert all("medusa" in c for c in cmds)


def test_spoofing_floods_with_forged_source():
    cmds = _attacks()["spoofing"]["cmds"]
    assert all("--flood" in c for c in cmds)
    assert all("-a " in c for c in cmds)
    assert all("--faster" not in c for c in cmds)


def test_mitm_bidirectional_with_gateway_and_vim_traffic():
    cmd = _attacks()["mitm"]["cmds"][0]
    assert cmd.count("arpspoof") == 2
    assert "10.9.9.1" in cmd  # gateway
    assert "ip_forward=1" in cmd and "ip_forward=0" in cmd
    assert "ssh -i /k luiz_henrique@10.9.9.5" in cmd  # tráfego real via SSH
    assert "-i eth9" in cmd  # usa a iface passada, não 'eth0' fixo


def test_detect_gateway_returns_string():
    assert isinstance(ao.detect_gateway(), str)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); print(f"  ok: {name}")
    print("ALL TESTS PASSED")
