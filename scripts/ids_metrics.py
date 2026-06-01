#!/usr/bin/env python3
"""
ids_metrics.py — Compute live-run IDS metrics from log files.

Supports two log types:
  multiclass  — network_ids.py output (Phase 1 + Phase 2, two confidence columns)
  binary      — network_binary_ids.py output (Phase 1 only)

Ground truth windows come from an attack_orchestrator JSON report.
PC timestamps in the JSON are assumed to be in BRT (UTC-3) by default;
pass --tz-offset to adjust.

Usage
-----
# Multiclass IDS run against its orchestrator report
python3 ids_metrics.py \
    --ids     logs/ids_run_20260601_170411.log \
    --report  logs/report_20260601_140921.json \
    --mode    multiclass

# Binary IDS run against its orchestrator report
python3 ids_metrics.py \
    --ids     logs/binary_ids_run_20260601_171127.log \
    --report  logs/report_20260601_141629.json \
    --mode    binary

# Change timezone offset (default 3 = BRT → UTC)
python3 ids_metrics.py ... --tz-offset 3

# Save output to a JSON summary file
python3 ids_metrics.py ... --output results/metrics_20260601.json

# Disable 30s post-attack idle slack
python3 ids_metrics.py ... --idle-slack 0
# Apply label merges to ground truth (e.g. ddos=dos for unified taxonomy)
python3 ids_metrics.py ... --label-map ddos=dos
"""

import argparse
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta

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


# ─── Log parsers ─────────────────────────────────────────────────────────────

# Multiclass alert line (Phase 1 + Phase 2):
#   HH:MM:SS<TAB>P1%<TAB>p2_label<TAB>P2%<TAB>src_ip<TAB>...
_RE_MULTI = re.compile(
    r'^(\d{2}:\d{2}:\d{2})\t([\d.]+)%\t(\w[\w→]*)\t([\d.]+)%'
)

# Binary alert line (Phase 1 only):
#   HH:MM:SS<TAB>P1%<TAB>src_ip<TAB>...
_RE_BINARY = re.compile(
    r'^(\d{2}:\d{2}:\d{2})\t([\d.]+)%\t(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\t'
)


def parse_multiclass_log(path: str):
    """Yield (ts_sec, p1, p2_label, p2_conf) for each alert line."""
    with open(path) as f:
        for line in f:
            m = _RE_MULTI.match(line)
            if not m:
                continue
            yield (
                ts_to_seconds(m.group(1)),
                float(m.group(2)),
                m.group(3),
                float(m.group(4)),
            )


def parse_binary_log(path: str):
    """Yield (ts_sec, p1) for each alert line."""
    with open(path) as f:
        for line in f:
            m = _RE_BINARY.match(line)
            if not m:
                continue
            yield (
                ts_to_seconds(m.group(1)),
                float(m.group(2)),
            )


# ─── Metric computation ───────────────────────────────────────────────────────

def confusion_matrix(true_labels, pred_labels, classes):
    """Returns dict[true][pred] = count."""
    cm = defaultdict(Counter)
    for t, p in zip(true_labels, pred_labels):
        cm[t][p] += 1
    return cm


def per_class_metrics(true_labels, pred_labels, classes):
    results = {}
    for cls in classes:
        tp = sum(1 for t, p in zip(true_labels, pred_labels) if t == cls and p == cls)
        fp = sum(1 for t, p in zip(true_labels, pred_labels) if t != cls and p == cls)
        fn = sum(1 for t, p in zip(true_labels, pred_labels) if t == cls and p != cls)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1   = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        results[cls] = {"tp": tp, "fp": fp, "fn": fn,
                        "precision": prec, "recall": rec, "f1": f1}
    total = len(true_labels)
    correct = sum(1 for t, p in zip(true_labels, pred_labels) if t == p)
    results["__accuracy__"] = correct / total if total > 0 else 0.0
    results["__total__"] = total
    results["__correct__"] = correct
    valid = [v for k, v in results.items() if k not in ("__accuracy__", "__total__", "__correct__")]
    results["__macro_precision__"] = statistics.mean(v["precision"] for v in valid)
    results["__macro_recall__"]    = statistics.mean(v["recall"]    for v in valid)
    mp = results["__macro_precision__"]
    mr = results["__macro_recall__"]
    results["__macro_f1__"] = 2 * mp * mr / (mp + mr) if (mp + mr) > 0 else 0.0
    return results


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


def threshold_sweep(scores, thresholds=None):
    if thresholds is None:
        thresholds = [0.90, 0.92, 0.95, 0.97, 0.99, 0.995, 0.999]
    total = len(scores)
    return [
        {
            "threshold": t,
            "kept": sum(1 for v in scores if v / 100 >= t),
            "tpr": sum(1 for v in scores if v / 100 >= t) / total if total else 0.0,
        }
        for t in thresholds
    ]


# ─── Pretty printers ─────────────────────────────────────────────────────────

def print_multiclass_report(metrics, cm, p1_stats, p2_stats, threshold_data, outside, label_map=None):
    lm_note = f"  (label map applied: {label_map})" if label_map else ""
    classes = build_attack_classes(label_map or {})
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║   MULTICLASS IDS METRICS                                ║")
    print("╚══════════════════════════════════════════════════════════╝")
    if lm_note:
        print(lm_note)
    print(f"\n  Alerts in attack windows : {metrics['__total__']}")
    print(f"  Alerts outside windows   : {outside}")
    print(f"  Correctly classified     : {metrics['__correct__']}")
    print(f"  Accuracy                 : {metrics['__accuracy__']:.4f}")
    print(f"  Macro Precision          : {metrics['__macro_precision__']:.4f}")
    print(f"  Macro Recall             : {metrics['__macro_recall__']:.4f}")
    print(f"  Macro F1                 : {metrics['__macro_f1__']:.4f}")

    print(f"\n  {'Class':<14} {'TP':>6} {'FP':>6} {'FN':>6} {'Prec':>8} {'Rec':>8} {'F1':>8}")
    print("  " + "─" * 62)
    for cls in classes:
        r = metrics[cls]
        print(f"  {cls:<14} {r['tp']:>6} {r['fp']:>6} {r['fn']:>6} "
              f"{r['precision']:>8.4f} {r['recall']:>8.4f} {r['f1']:>8.4f}")

    print("\n  Confusion matrix (rows=true, cols=predicted):")
    pred_seen = sorted(set(p for row in cm.values() for p in row))
    header = f"  {'true \\ pred':<14}" + "".join(f"{c:>12}" for c in pred_seen)
    print(header)
    print("  " + "─" * len(header.rstrip()))
    for true_cls in classes:
        row = cm.get(true_cls, {})
        total_row = sum(row.values())
        if total_row == 0:
            continue
        cells = "".join(f"{row.get(c, 0):>12}" for c in pred_seen)
        print(f"  {true_cls:<14}{cells}")

    print(f"\n  P1 confidence stats : {p1_stats}")
    print(f"  P2 confidence stats : {p2_stats}")

    if threshold_data:
        print(f"\n  P1 threshold sweep:")
        print(f"  {'Threshold':>12}  {'TPR':>8}  {'Alerts kept':>12}")
        for row in threshold_data:
            print(f"  {row['threshold']*100:>11.1f}%  {row['tpr']:>8.4f}  {row['kept']:>12}")


def precision_curve(tp_scores, fp_scores, thresholds=None):
    """Precision and relative TPR at each threshold (from live data)."""
    if thresholds is None:
        thresholds = [0.90, 0.91, 0.92, 0.93, 0.95, 0.97, 0.99, 0.995, 0.999, 1.0]
    total_tp = len(tp_scores)
    rows = []
    for t in thresholds:
        tp_k = sum(1 for v in tp_scores if v / 100 >= t)
        fp_k = sum(1 for v in fp_scores if v / 100 >= t)
        prec = tp_k / (tp_k + fp_k) if (tp_k + fp_k) > 0 else 1.0
        tpr_rel = tp_k / total_tp if total_tp > 0 else 0.0
        rows.append({"threshold": t, "tp_kept": tp_k, "fp_kept": fp_k,
                     "precision": prec, "tpr_relative": tpr_rel})
    return rows


def p1_histogram(scores, bins=10):
    """Histogram of P1 scores grouped into integer % bins."""
    from collections import Counter
    counts = Counter(int(v) for v in scores)
    lo, hi = int(min(scores)), int(max(scores)) + 1
    return [(b, counts.get(b, 0)) for b in range(lo, hi + 1)]


def print_binary_report(per_window, p1_stats, threshold_data, outside,
                        label_map=None, tp_scores=None, fp_scores=None,
                        per_sec_cm=None):
    classes = build_attack_classes(label_map or {})
    total_in = sum(v["n"] for v in per_window.values())
    tp_n = len(tp_scores) if tp_scores else total_in
    fp_n = len(fp_scores) if fp_scores else outside
    precision_at_thr = tp_n / (tp_n + fp_n) if (tp_n + fp_n) > 0 else 1.0

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║   BINARY IDS METRICS                                    ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Per-second confusion matrix (primary metrics)
    if per_sec_cm:
        cm = per_sec_cm
        print(f"\n  ── 2×2 Confusion Matrix (per-second granularity) ──")
        print(f"                    Pred: Attack  Pred: Benign")
        print(f"  True: Attack       {cm['TP']:>9}    {cm['FN']:>9}   ({cm['TP']+cm['FN']} attack secs)")
        print(f"  True: Benign       {cm['FP']:>9}    {cm['TN']:>9}   ({cm['FP']+cm['TN']} benign secs)")
        print(f"\n  Accuracy   : {cm['accuracy']:.4f}  ({cm['TP']+cm['TN']}/{cm['total']})")
        print(f"  Precision  : {cm['precision']:.4f}  ({cm['TP']}/{cm['TP']+cm['FP']})")
        print(f"  Recall/TPR : {cm['recall']:.4f}  ({cm['TP']}/{cm['TP']+cm['FN']})")
        print(f"  F1-score   : {cm['f1']:.4f}")
        print(f"  FPR        : {cm['fpr']:.6f}  ({cm['FP']}/{cm['FP']+cm['TN']})")
        print(f"  FNR        : {1-cm['recall']:.4f}  ({cm['FN']}/{cm['TP']+cm['FN']})")

        if "per_attack_window" in cm:
            print(f"\n  ── Per-window detection rate ──")
            print(f"  {'Window':<14} {'Secs':>5}  {'Alerted':>8}  {'Rate':>8}")
            for lbl, v in cm["per_attack_window"].items():
                bar = '█' * int(20 * v['detection_rate']) + '░' * (20 - int(20 * v['detection_rate']))
                print(f"  {lbl:<14} {v['total_secs']:>5}  {v['alerted_secs']:>8}  {v['detection_rate']:>7.1%}  {bar}")
    else:
        print(f"\n  ── Per-flow counts ──")
        print(f"  TP (alerts in attack windows) : {tp_n}")
        print(f"  FP (alerts outside windows)   : {fp_n}")
        print(f"  Precision @ threshold: {precision_at_thr:.6f}  ({tp_n}/{tp_n+fp_n})")

    print(f"\n  ── Detection coverage per attack window ──")
    print(f"  {'Window':<14} {'Alerts':>8} {'Mean P1':>10} {'Min P1':>8} {'Max P1':>8}")
    print("  " + "─" * 52)
    for cls in classes:
        w = per_window.get(cls, {"n": 0, "mean": 0, "min": 0, "max": 0})
        print(f"  {cls:<14} {w.get('n',0):>8} {w.get('mean',0):>9.3f}% "
              f"{w.get('min',0):>7.1f}% {w.get('max',0):>7.1f}%")

    print(f"\n  Global P1 stats : {p1_stats}")

    if tp_scores and fp_scores is not None:
        pc = precision_curve(tp_scores, fp_scores)
        print(f"\n  ── Precision / Relative-TPR curve (live data) ──")
        print(f"  {'Threshold':>12}  {'TP kept':>8}  {'FP kept':>6}  {'Precision':>10}  {'Rel. TPR':>10}")
        for row in pc:
            print(f"  {row['threshold']*100:>11.1f}%  {row['tp_kept']:>8}  "
                  f"{row['fp_kept']:>6}  {row['precision']:>10.6f}  {row['tpr_relative']:>10.4f}")

        hist = p1_histogram(tp_scores)
        print(f"\n  ── P1 score histogram (TP flows) ──")
        max_bar = max(c for _, c in hist) if hist else 1
        for b, c in hist:
            bar = '█' * int(40 * c / max_bar) if c else ''
            print(f"  {b:3d}–{b+1:3d}%: {c:>6}  {bar}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ids",    required=True, help="IDS log file path")
    ap.add_argument("--report", required=True, help="Orchestrator JSON report path")
    ap.add_argument("--mode",   required=True, choices=["multiclass", "binary"],
                    help="Log type: 'multiclass' (Phase1+2) or 'binary' (Phase1 only)")
    ap.add_argument("--tz-offset", type=int, default=3,
                    help="Hours to add to orchestrator timestamps to get UTC (default: 3 for BRT)")
    ap.add_argument("--idle-slack", type=int, default=30,
                    help="Seconds to extend each attack window after its end time (default: 30)")
    ap.add_argument("--output", default=None,
                    help="Optional path to save JSON summary")
    ap.add_argument("--label-map", nargs="*", default=[],
                    metavar="FROM=TO",
                    help="Merge ground-truth labels before scoring, e.g. --label-map ddos=dos")
    args = ap.parse_args()

    label_map = {}
    for item in (args.label_map or []):
        src, _, dst = item.partition("=")
        if src and dst:
            label_map[src.strip()] = dst.strip()

    windows = parse_orchestrator(args.report, args.tz_offset, args.idle_slack,
                                 label_map=label_map)
    attack_classes = build_attack_classes(label_map)

    summary = {}

    # ── MULTICLASS ────────────────────────────────────────────────────────────
    if args.mode == "multiclass":
        true_labels, pred_labels = [], []
        p1_all, p2_all = [], []
        outside = 0

        for ts, p1, p2_label, p2_conf in parse_multiclass_log(args.ids):
            true = get_true_label(ts, windows)
            if true == "outside":
                outside += 1
                continue
            true_labels.append(true)
            pred_labels.append(p2_label)
            p1_all.append(p1)
            p2_all.append(p2_conf)

        metrics = per_class_metrics(true_labels, pred_labels, attack_classes)
        cm = confusion_matrix(true_labels, pred_labels, attack_classes)
        p1_stats = conf_stats(p1_all)
        p2_stats = conf_stats(p2_all)
        td = threshold_sweep(p1_all)

        print_multiclass_report(metrics, cm, p1_stats, p2_stats, td, outside, label_map)

        summary = {
            "mode": "multiclass",
            "label_map": label_map,
            "ids_log": args.ids,
            "orchestrator_report": args.report,
            "alerts_in_windows": metrics["__total__"],
            "alerts_outside_windows": outside,
            "accuracy": metrics["__accuracy__"],
            "macro_precision": metrics["__macro_precision__"],
            "macro_recall": metrics["__macro_recall__"],
            "macro_f1": metrics["__macro_f1__"],
            "per_class": {cls: metrics[cls] for cls in attack_classes},
            "p1_confidence": p1_stats,
            "p2_confidence": p2_stats,
            "threshold_sweep": td,
        }

    # ── BINARY ────────────────────────────────────────────────────────────────
    else:
        per_window_raw = defaultdict(list)
        fp_raw = []
        all_parsed = []  # (ts_sec, p1, label)

        for ts_sec, p1 in parse_binary_log(args.ids):
            true = get_true_label(ts_sec, windows)
            all_parsed.append((ts_sec, p1, true))
            if true == "outside":
                fp_raw.append(p1)
            else:
                per_window_raw[true].append(p1)

        outside = len(fp_raw)
        all_tp = [v for vals in per_window_raw.values() for v in vals]
        per_window_stats = {cls: conf_stats(per_window_raw[cls]) for cls in attack_classes
                            if per_window_raw[cls]}
        td = threshold_sweep(all_tp)
        global_stats = conf_stats(all_tp)

        # ── Per-second confusion matrix ────────────────────────────────────────
        log_start = min(t for t,_,_ in all_parsed)
        log_end   = max(t for t,_,_ in all_parsed)
        # windows include all attack types; attack_start/end is the full session span
        all_w_starts = [s for _,s,_ in windows]
        all_w_ends   = [e for _,_,e in windows]
        attack_start = min(all_w_starts)
        attack_end   = max(all_w_ends)

        alerted_secs = set(t for t,_,_ in all_parsed)

        psCM = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}
        per_attack_secs = defaultdict(lambda: {"total": 0, "alerted": 0})
        for sec in range(log_start, log_end + 1):
            is_atk = (attack_start <= sec <= attack_end)
            alerted = (sec in alerted_secs)
            if is_atk and alerted:      psCM["TP"] += 1
            elif is_atk and not alerted: psCM["FN"] += 1
            elif not is_atk and alerted: psCM["FP"] += 1
            else:                        psCM["TN"] += 1
            # per-attack window breakdown
            for label, ws, we in windows:
                if ws <= sec <= we:
                    per_attack_secs[label]["total"] += 1
                    if alerted:
                        per_attack_secs[label]["alerted"] += 1

        tp_s, fp_s, fn_s, tn_s = psCM["TP"], psCM["FP"], psCM["FN"], psCM["TN"]
        total_s = tp_s + fp_s + fn_s + tn_s
        acc_s   = (tp_s + tn_s) / total_s if total_s > 0 else 0.0
        prec_s  = tp_s / (tp_s + fp_s) if (tp_s + fp_s) > 0 else 1.0
        rec_s   = tp_s / (tp_s + fn_s) if (tp_s + fn_s) > 0 else 1.0
        f1_s    = 2 * prec_s * rec_s / (prec_s + rec_s) if (prec_s + rec_s) > 0 else 0.0
        fpr_s   = fp_s / (fp_s + tn_s) if (fp_s + tn_s) > 0 else 0.0

        psCM_result = {
            "TP": tp_s, "FP": fp_s, "FN": fn_s, "TN": tn_s, "total": total_s,
            "accuracy": round(acc_s, 4), "precision": round(prec_s, 4),
            "recall": round(rec_s, 4), "f1": round(f1_s, 4), "fpr": round(fpr_s, 6),
            "per_attack_window": {
                label: {"total_secs": v["total"], "alerted_secs": v["alerted"],
                        "detection_rate": round(v["alerted"]/v["total"], 4) if v["total"] > 0 else 0}
                for label, v in per_attack_secs.items()
            }
        }

        print_binary_report(per_window_stats, global_stats, td, outside, label_map,
                            tp_scores=all_tp, fp_scores=fp_raw, per_sec_cm=psCM_result)

        pc = precision_curve(all_tp, fp_raw) if all_tp else []
        prec_live = len(all_tp) / (len(all_tp) + outside) if (len(all_tp) + outside) > 0 else 1.0
        summary = {
            "mode": "binary",
            "label_map": label_map,
            "ids_log": args.ids,
            "orchestrator_report": args.report,
            "tp_flows": len(all_tp),
            "fp_flows": outside,
            "precision_per_flow": round(prec_live, 6),
            "per_second_cm": psCM_result,
            "offline_reference": {
                "threshold": 0.15688148228460247,
                "attack_precision": 0.68, "attack_recall": 0.96, "attack_f1": 0.80,
                "benign_precision": 0.96, "benign_recall": 0.69, "benign_f1": 0.80,
                "accuracy": 0.80, "note": "evaluated at Optuna threshold, NOT at deployed 0.9"
            },
            "per_window": per_window_stats,
            "p1_confidence_global": global_stats,
            "threshold_sweep": td,
            "precision_curve": pc,
        }

    if args.output:
        with open(args.output, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\n  → Summary saved to {args.output}")

    return summary


if __name__ == "__main__":
    main()
