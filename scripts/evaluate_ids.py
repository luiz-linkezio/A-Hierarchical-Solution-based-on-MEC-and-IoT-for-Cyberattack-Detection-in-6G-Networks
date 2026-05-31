#!/usr/bin/env python3
"""
evaluate_ids.py — Cross-correlate attack orchestrator ground truth with IDS alerts.

Usage:
    python3 scripts/evaluate_ids.py \
        --orchestrator results/report_20260523_175636.csv \
        --ids          results/ids_run_20260523_205116.md \
        [--tz-offset   3]        # hours to ADD to PC timestamps to reach VIM UTC (default: 3)
        [--idle-slack  30]       # seconds of grace after attack ends for late flows (default: 30)
        [--output      results/evaluation_20260523.json]

The orchestrator CSV has start_time/end_time in local time (BRT, UTC-3).
The IDS markdown has HH:MM:SS in UTC.
--tz-offset 3 converts PC timestamps → UTC so both are comparable.
"""

import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


# ── Parsing ───────────────────────────────────────────────────────────────────

def load_orchestrator(path: str, tz_offset_h: float) -> list[dict]:
    """Return list of {name, start, end} with times shifted to VIM timezone."""
    shift = timedelta(hours=tz_offset_h)
    windows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("skipped", "").lower() == "true":
                continue
            start = datetime.fromisoformat(row["start_time"]) + shift
            end   = datetime.fromisoformat(row["end_time"])   + shift
            windows.append({"name": row["attack"], "label": row["label"],
                             "start": start, "end": end})
    return windows


# Alert line (TSV): HH:MM:SS \t P1% \t p2_label \t P2% \t ...
# Supports both new .log format (TSV) and old .md format (pipe-delimited).
_ROW_TSV_RE = re.compile(
    r"^(\d{2}:\d{2}:\d{2})\t([\d.]+)%\t(\S+)\t([\d.]+)%"
)
_ROW_MD_RE = re.compile(
    r"^\| (\d{2}:\d{2}:\d{2}) \| ([\d.]+)% \| (\S+?) \| ([\d.]+)% \|"
)
_LOW_CONF_RE = re.compile(r"best: (\w+)")


def parse_ids(path: str, date_str: str) -> list[dict]:
    """Return list of {time, p1_conf, p2_label, p2_conf, low_conf}.
    Accepts both the new .log (TSV) and legacy .md (pipe-delimited) formats.
    """
    alerts = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            m = _ROW_TSV_RE.match(line) or _ROW_MD_RE.match(line)
            if not m:
                continue
            hms, p1_pct, p2_raw, p2_pct = m.groups()
            low_conf = p2_raw.startswith("LOW_CONF")
            if low_conf:
                inner = _LOW_CONF_RE.search(p2_raw)
                p2_label = inner.group(1) if inner else "unknown"
            else:
                p2_label = p2_raw
            t = datetime.strptime(f"{date_str} {hms}", "%Y-%m-%d %H:%M:%S")
            alerts.append({
                "time":     t,
                "p1_conf":  float(p1_pct) / 100,
                "p2_label": p2_label,
                "p2_conf":  float(p2_pct) / 100,
                "low_conf": low_conf,
            })
    return alerts


# ── Correlation ───────────────────────────────────────────────────────────────

def label_at(t: datetime, windows: list[dict], idle_slack: timedelta) -> str:
    for w in windows:
        if w["start"] <= t <= w["end"] + idle_slack:
            return w["name"]
    return "benign"


def correlate(alerts: list[dict], windows: list[dict], idle_slack: timedelta) -> dict:
    """Return confusion[real_label][pred_label] = count."""
    confusion: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for a in alerts:
        real = label_at(a["time"], windows, idle_slack)
        pred = a["p2_label"] if not a["low_conf"] else f"LOW_CONF({a['p2_label']})"
        confusion[real][pred] += 1
    return {k: dict(v) for k, v in confusion.items()}


# ── Reporting ─────────────────────────────────────────────────────────────────

def print_report(confusion: dict, windows: list[dict]) -> None:
    attack_names = [w["name"] for w in windows]
    all_preds    = sorted({p for preds in confusion.values() for p in preds})

    total_alerts = sum(sum(v.values()) for v in confusion.values())
    fp_total     = sum(confusion.get("benign", {}).values())
    fn_attacks   = [n for n in attack_names if not confusion.get(n)]
    tp_p1        = total_alerts - fp_total

    tp_p2  = sum(confusion.get(n, {}).get(n, 0) for n in attack_names)
    tot_p2 = sum(sum(v.values()) for k, v in confusion.items() if k != "benign")
    p2_acc = tp_p2 / tot_p2 * 100 if tot_p2 else 0.0

    W = 65
    print(f"\n{'═'*W}")
    print(f"  IDS EVALUATION REPORT")
    print(f"{'═'*W}")
    print(f"  Total alerts    : {total_alerts:>8,}")
    print(f"  During attacks  : {tp_p1:>8,}  (Phase 1 TPs)")
    print(f"  False positives : {fp_total:>8,}  ({fp_total/total_alerts*100:.2f}%)")
    print(f"  FN attacks      : {len(fn_attacks):>8}  {fn_attacks}")
    print(f"\n  Phase 2 accuracy: {p2_acc:.1f}%  ({tp_p2:,} / {tot_p2:,})")
    print(f"{'─'*W}")
    print(f"  {'Real':<14} {'Predicted':<22} {'Count':>7}  {'%':>6}  Result")
    print(f"{'─'*W}")

    for real in attack_names + ["benign"]:
        preds = confusion.get(real, {})
        total = sum(preds.values())
        if not preds and real in attack_names:
            print(f"  {real:<14} {'—':<22} {'0':>7}  {'  —':>6}  ❌ FN")
            continue
        if not preds:
            continue
        first = True
        for pred, cnt in sorted(preds.items(), key=lambda x: -x[1]):
            pct = cnt / total * 100
            if real == "benign":
                verdict = "❌ FP"
            elif pred == real:
                verdict = "✅ TP"
            elif pred.startswith("LOW_CONF"):
                verdict = "⚠️  LOW_CONF→P3"
            else:
                verdict = "⚠️  wrong type"
            label_col = real if first else ""
            print(f"  {label_col:<14} {pred:<22} {cnt:>7,}  {pct:>5.1f}%  {verdict}")
            first = False
        print(f"  {'':14} {'TOTAL':<22} {total:>7,}")
        print()

    print(f"{'═'*W}\n")

    # Per-class Phase-2 summary
    print(f"  Phase 2 — per-class accuracy:")
    print(f"{'─'*W}")
    for name in attack_names:
        preds = confusion.get(name, {})
        total = sum(preds.values())
        if not total:
            print(f"  {name:<14} FN — no flows detected (attack too short?)")
            continue
        tp = preds.get(name, 0)
        acc = tp / total * 100
        bar = "█" * int(acc / 5) + "░" * (20 - int(acc / 5))
        print(f"  {name:<14} {bar}  {acc:5.1f}%  ({tp:,}/{total:,})")
    print(f"{'═'*W}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="IDS vs orchestrator evaluation")
    ap.add_argument("--orchestrator", required=True, help="Orchestrator CSV report")
    ap.add_argument("--ids",          required=True, help="IDS markdown report")
    ap.add_argument("--tz-offset",    type=float, default=3.0,
                    help="Hours to add to PC timestamps to match VIM UTC (default: 3)")
    ap.add_argument("--idle-slack",   type=float, default=30.0,
                    help="Grace seconds after attack end for late flows (default: 30)")
    ap.add_argument("--output",       default=None,
                    help="Optional JSON output path")
    args = ap.parse_args()

    windows = load_orchestrator(args.orchestrator, args.tz_offset)
    if not windows:
        print("[!] No (non-skipped) attacks found in orchestrator CSV.")
        return

    # Derive the date string from the first window (VIM UTC)
    date_str = windows[0]["start"].strftime("%Y-%m-%d")

    alerts = parse_ids(args.ids, date_str)
    print(f"  Loaded {len(alerts):,} alerts from IDS report.")
    print(f"  Loaded {len(windows)} attack windows from orchestrator.")

    idle_slack = timedelta(seconds=args.idle_slack)
    confusion  = correlate(alerts, windows, idle_slack)

    print_report(confusion, windows)

    if args.output:
        data = {
            "orchestrator": args.orchestrator,
            "ids":          args.ids,
            "tz_offset_h":  args.tz_offset,
            "idle_slack_s": args.idle_slack,
            "confusion":    confusion,
        }
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"  JSON saved → {args.output}")


if __name__ == "__main__":
    main()
