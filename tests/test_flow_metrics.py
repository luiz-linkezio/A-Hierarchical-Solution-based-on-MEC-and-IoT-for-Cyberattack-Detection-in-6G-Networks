import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from ids_metrics import (
    binary_flow_metrics, emission_delay_stats, flow_true_label, make_background_filter,
    multiclass_flow_metrics, p1_threshold_sweep, parse_flow_log, parse_windows_epoch,
)

# Janela de ataque do orquestrador em hora local do PC (BRT = UTC-3).
BRT = timezone(timedelta(hours=-3))


def _epoch(iso_local: str) -> float:
    return datetime.fromisoformat(iso_local).replace(tzinfo=BRT).timestamp()


def _report(attacks) -> str:
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump({"attacks": [{"attack": a, "start_time": s, "end_time": e}
                               for a, s, e in attacks]}, f)
    return path


def _log(lines) -> str:
    fd, path = tempfile.mkstemp(suffix=".log")
    with os.fdopen(fd, "w") as f:
        f.write("=== IDS Run ===\n\n[FLOWS]\n# header\n")
        f.write("[SYS_SNAPSHOT] 02:00:00  CPU 1.0% | RAM 13.6% (1062 MB)\n")
        for ln in lines:
            f.write(ln + "\n")
    return path


def test_windows_are_absolute_epochs_with_label_map_and_clock_offset():
    rep = _report([("dos", "2026-06-19T23:34:00", "2026-06-19T23:35:00"),
                   ("ddos", "2026-06-19T23:37:00", "2026-06-19T23:38:00")])
    w = parse_windows_epoch(rep, tz_offset_h=3, clock_offset_s=2.0, label_map={"ddos": "dos"})
    assert [lab for lab, _, _ in w] == ["dos", "dos"]
    assert w[0][1] == _epoch("2026-06-19T23:34:00") + 2.0
    assert w[1][2] == _epoch("2026-06-19T23:38:00") + 2.0


def test_label_uses_flow_start_not_emission():
    w = [("dos", 1000.0, 1060.0)]
    assert flow_true_label(1000.0, w) == "dos"
    assert flow_true_label(1060.0, w) == "dos"
    # fluxo que começou depois da janela é benigno, mesmo se emitido "dentro" dela
    assert flow_true_label(1060.5, w) == "benign"
    assert flow_true_label(999.9, w) == "benign"


def test_parse_multiclass_and_binary_rows():
    t = _epoch("2026-06-19T23:34:10")
    multi = _log([
        f"02:35:30\t{t:.6f}\tATTACK\t99.987%\tdos\t88.0%\t0\t192.168.100.232\t192.168.100.5\t4000\t80\t6\t1e5\t10\t0.1\t9.0\t1066\t1\t1\t3.0",
        f"02:35:31\t{t + 1:.6f}\tBENIGN\t12.500%\t-\t-\t-\t192.168.100.5\t8.8.8.8\t5353\t53\t17\t1e3\t2\t0.5\t9.0\t1066\t1\t1\t3.0",
    ])
    rows = parse_flow_log(multi, "multiclass")
    assert len(rows) == 2
    a, b = rows
    assert a["verdict"] == "ATTACK" and a["p2_label"] == "dos" and a["low_conf"] is False
    assert abs(a["p1"] - 0.99987) < 1e-9 and abs(a["flow_ts"] - t) < 1e-6
    assert a["emit_sec"] == 2 * 3600 + 35 * 60 + 30 and a["dst_port"] == "80"
    assert b["verdict"] == "BENIGN" and b["p2_label"] is None

    binary = _log([f"02:35:30\t{t:.6f}\tATTACK\t95.000%\t192.168.100.232\t192.168.100.5\t4000\t80\t6\t1e5\t10\t0.1\t9.0\t1066\t1\t1\t3.0"])
    (r,) = parse_flow_log(binary, "binary")
    assert r["verdict"] == "ATTACK" and r["src_ip"] == "192.168.100.232" and r["p2_label"] is None


def _flow(ts, verdict, p1=None, p2=None, emit_sec=0):
    return {"flow_ts": ts, "verdict": verdict, "emit_sec": emit_sec,
            "p1": p1 if p1 is not None else (0.99 if verdict == "ATTACK" else 0.1),
            "p2_label": p2, "p2_conf": None, "low_conf": False}


def test_binary_confusion_is_per_flow_and_ignores_emission_lag():
    w = [("dos", 100.0, 200.0), ("web", 500.0, 600.0)]
    flows = [
        # emitidos muito depois (lag de 80 s) — contam para a janela onde COMEÇARAM
        _flow(150.0, "ATTACK", emit_sec=230), _flow(199.0, "ATTACK", emit_sec=280),
        _flow(120.0, "BENIGN"),                      # FN
        _flow(550.0, "BENIGN"),                      # FN (web não detectado)
        _flow(300.0, "ATTACK"),                      # FP (fora de janela)
        _flow(50.0, "BENIGN"), _flow(700.0, "BENIGN"),   # TN
    ]
    m = binary_flow_metrics(flows, w)
    assert (m["TP"], m["FP"], m["FN"], m["TN"]) == (2, 1, 2, 2)
    assert abs(m["precision"] - 2 / 3) < 1e-9
    assert abs(m["recall"] - 0.5) < 1e-9
    assert abs(m["fpr"] - 1 / 3) < 1e-9
    assert m["per_class"]["dos"] == {"flows": 3, "detected": 2, "recall": round(2 / 3, 4)}
    assert m["per_class"]["web"]["detected"] == 0
    assert [a["detected"] for a in m["per_attack"]] == [True, False]


def test_threshold_sweep_uses_logged_p1_of_every_flow():
    w = [("dos", 100.0, 200.0)]
    flows = [_flow(150.0, "ATTACK", p1=0.95), _flow(160.0, "BENIGN", p1=0.60),
             _flow(300.0, "BENIGN", p1=0.70), _flow(310.0, "BENIGN", p1=0.10)]
    rows = {r["threshold"]: r for r in p1_threshold_sweep(flows, w, [0.5, 0.9])}
    assert (rows[0.5]["TP"], rows[0.5]["FP"], rows[0.5]["FN"]) == (2, 1, 0)
    assert (rows[0.9]["TP"], rows[0.9]["FP"], rows[0.9]["FN"]) == (1, 0, 1)


def test_multiclass_prediction_is_benign_when_p1_says_benign():
    w = [("recon", 100.0, 200.0), ("dos", 300.0, 400.0)]
    flows = [
        _flow(110.0, "ATTACK", p2="recon"),
        _flow(120.0, "BENIGN"),              # recon → benign (perdido na Fase 1)
        _flow(310.0, "ATTACK", p2="dos"),
        _flow(320.0, "ATTACK", p2="recon"),  # dos → recon
        _flow(500.0, "ATTACK", p2="dos"),    # benign → dos (FP)
        _flow(510.0, "BENIGN"),
    ]
    m = multiclass_flow_metrics(flows, w, ["recon", "dos"])
    cm = m["confusion"]
    assert cm["recon"] == {"recon": 1, "benign": 1}
    assert cm["dos"] == {"dos": 1, "recon": 1}
    assert cm["benign"] == {"dos": 1, "benign": 1}
    assert m["per_class"]["recon"]["tp"] == 1 and m["per_class"]["recon"]["fp"] == 1
    assert abs(m["accuracy"] - 3 / 6) < 1e-9
    # tipo, só entre fluxos de ataque que a Fase 1 detectou
    assert abs(m["p2_type_accuracy_on_detected"] - 2 / 3) < 1e-9


def test_emission_delay_handles_midnight_wrap():
    # fluxo começa 23:59:50 UTC, emitido 00:00:40 UTC → 50 s
    ts = datetime(2026, 6, 19, 23, 59, 50, tzinfo=timezone.utc).timestamp()
    d = emission_delay_stats([_flow(ts, "ATTACK", emit_sec=40)])
    assert d["median_s"] == 50


def _ipflow(ts, verdict, src, dst):
    f = _flow(ts, verdict)
    f.update(src_ip=src, dst_ip=dst)
    return f


def test_background_filter_keeps_attack_endpoints_only():
    bg = make_background_filter("192.168.100.13", ["192.168.100.2", "192.168.100.245"])
    atk = lambda s, d, lab="dos": not bg(_ipflow(0, "BENIGN", s, d), lab)
    assert atk("192.168.100.2", "192.168.100.13")        # atacante → VIM
    assert atk("192.168.100.13", "192.168.100.245")      # VIM → 2ª interface do atacante
    assert atk("1.2.3.4", "192.168.100.13")              # spoofing / ddos rand-source (entrada)
    assert atk("192.168.100.13", "8.8.8.8", "mitm")      # vítima do MITM → internet (interceptado)
    assert not atk("192.168.100.13", "185.125.190.58")   # NTP da própria VIM (saída, fora do MITM)
    assert not atk("192.168.100.7", "224.0.0.251")       # mDNS de outro host
    assert not atk("192.168.100.13", "239.255.255.250")  # SSDP
    assert not atk("192.168.100.13", "192.168.100.255")  # broadcast da LAN
    assert not atk("192.168.100.4", "192.168.100.13")    # outro host da LAN
    assert not atk("192.168.100.13", "192.168.100.1")    # DNS/gateway (fundo)
    assert not atk("192.168.100.2", "192.168.100.7")     # não envolve a VIM


def test_background_flow_in_window_counts_as_benign():
    w = [("dos", 100.0, 200.0)]
    bg = make_background_filter("192.168.100.13", ["192.168.100.2"])
    flows = [
        _ipflow(150.0, "ATTACK", "192.168.100.2", "192.168.100.13"),  # TP
        _ipflow(160.0, "BENIGN", "192.168.100.7", "224.0.0.251"),     # TN (não é FN)
        _ipflow(170.0, "ATTACK", "192.168.100.4", "192.168.100.13"),  # FP (não é TP)
    ]
    m = binary_flow_metrics(flows, w, is_background=bg)
    assert (m["TP"], m["FP"], m["FN"], m["TN"]) == (1, 1, 0, 1)
    assert m["background_in_windows"] == 2
    mm = multiclass_flow_metrics(
        [dict(f, p2_label="dos") for f in flows], w, ["dos"], is_background=bg)
    assert mm["per_class"]["dos"]["support"] == 1
    rows = p1_threshold_sweep(flows, w, [0.5], is_background=bg)
    assert (rows[0]["TP"], rows[0]["FP"]) == (1, 1)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); print(f"  ok: {name}")
    print("ALL TESTS PASSED")
