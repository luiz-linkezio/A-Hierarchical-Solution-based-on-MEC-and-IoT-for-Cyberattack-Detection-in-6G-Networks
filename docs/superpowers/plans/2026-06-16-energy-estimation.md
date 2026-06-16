# Energy Estimation in ids_metrics.py Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an energy-estimation section to `scripts/ids_metrics.py` that replaces the manual back-of-envelope estimate in the article/session report with a number computed from the real `SYS_SNAPSHOT` CPU time series already in the IDS run logs, split into "during attack windows" vs "idle".

**Architecture:** A linear CPU-utilization power model (`P = P_idle + (P_max - P_idle) * cpu_pct/100`) is integrated over the `SYS_SNAPSHOT` time series already present in the log file passed via `--ids`. Energy is split into attack/idle using the same ground-truth `windows` already parsed from the orchestrator `--report` JSON. A secondary, coarser figure (per-inference energy) is derived from the `[SUMMARY]` aggregate block when present.

**Tech Stack:** Python 3 stdlib only (`re`, `statistics`) — same as the rest of `ids_metrics.py`. No test framework exists in this repo; validation is done with small throwaway scripts in `/tmp` run against synthetic data, then against the two real log files.

**Spec:** `docs/superpowers/specs/2026-06-16-energy-estimation-design.md`

**Important constraint (CLAUDE.md):** Do NOT commit any change unless the user has explicitly granted permission in this session. Do not delete or edit anything under a directory named `old`.

---

### Task 1: Parse `SYS_SNAPSHOT` lines

**Files:**
- Modify: `scripts/ids_metrics.py` (near the existing `_RE_MULTI`/`_RE_BINARY` regexes, around line 136, and near `parse_binary_log`, around line 156)

- [ ] **Step 1: Write a throwaway validation script**

```bash
cat > /tmp/test_snapshot_parse.py << 'EOF'
import sys
sys.path.insert(0, "scripts")
from ids_metrics import parse_snapshot_log

import tempfile, os
sample = (
    "[SYS_SNAPSHOT] 17:59:56  CPU 0.3% | RAM 12.6% (985 MB)\n"
    "not a snapshot line\n"
    "[SYS_SNAPSHOT] 18:00:02  CPU 27.5% | RAM 13.3% (1036 MB) | Net stuff\n"
)
with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
    f.write(sample)
    path = f.name

result = list(parse_snapshot_log(path))
os.unlink(path)
assert result == [(64796, 0.3), (64802, 27.5)], result
print("OK:", result)
EOF
python3 /tmp/test_snapshot_parse.py
```

Expected: `ImportError: cannot import name 'parse_snapshot_log'` (function doesn't exist yet).

- [ ] **Step 2: Add the regex and parser function**

Add the regex near the other `_RE_*` patterns (after the `_RE_BINARY` definition, around line 138):

```python
# Periodic background sample, independent of alert lines:
#   [SYS_SNAPSHOT] HH:MM:SS  CPU x.x% | RAM ...
_RE_SNAPSHOT = re.compile(
    r'^\[SYS_SNAPSHOT\] (\d{2}:\d{2}:\d{2})\s+CPU\s+([\d.]+)%'
)
```

Add the parser function near `parse_binary_log` (after it, around line 167):

```python
def parse_snapshot_log(path: str):
    """Yield (ts_sec, cpu_pct) for each SYS_SNAPSHOT line."""
    with open(path) as f:
        for line in f:
            m = _RE_SNAPSHOT.match(line)
            if not m:
                continue
            yield (ts_to_seconds(m.group(1)), float(m.group(2)))
```

- [ ] **Step 3: Run the validation script again**

```bash
python3 /tmp/test_snapshot_parse.py
```

Expected: `OK: [(64796, 0.3), (64802, 27.5)]`

---

### Task 2: Linear power model + session energy split (attack vs idle)

**Files:**
- Modify: `scripts/ids_metrics.py` (new section after `get_true_label`, around line 124, before the log-parser section)

- [ ] **Step 1: Write a throwaway validation script**

```bash
cat > /tmp/test_session_energy.py << 'EOF'
import sys
sys.path.insert(0, "scripts")
from ids_metrics import compute_session_energy

# 10 samples, 1 Hz, all idle (cpu 0%) for first 5s, then "attack" (cpu 100%) for next 5s.
samples = [(0, 0.0), (1, 0.0), (2, 0.0), (3, 0.0), (4, 0.0),
           (5, 100.0), (6, 100.0), (7, 100.0), (8, 100.0), (9, 100.0)]
windows = [("dos", 5, 9)]  # attack window covers t=5..9

result = compute_session_energy(samples, windows, p_idle=2.0, p_max=11.0)

# idle stretch: dt total 4s (5 intervals -> 4 gaps before the 5th sample at t=4->5 is attack-labeled by t0=4 which is idle)
# at p_idle=2W for 5 idle-labeled intervals (t0 in 0..4) of 1s each = 5 * 2 = 10 J
# at p_max=11W for 4 attack-labeled intervals (t0 in 5..8) of 1s each = 4 * 11 = 44 J
assert abs(result["total_energy_j"] - 54.0) < 0.01, result
assert abs(result["idle"]["energy_j"] - 10.0) < 0.01, result
assert abs(result["attack"]["energy_j"] - 44.0) < 0.01, result
print("OK:", result)

assert compute_session_energy([(0, 0.0)], windows, 2.0, 11.0) == {}
print("OK: <2 samples returns {}")
EOF
python3 /tmp/test_session_energy.py
```

Expected: `ImportError: cannot import name 'compute_session_energy'`.

- [ ] **Step 2: Implement `power_w` and `compute_session_energy`**

Add after `get_true_label` (around line 124):

```python
def power_w(cpu_pct: float, p_idle: float, p_max: float) -> float:
    """Linear CPU-utilization power model: P = P_idle + (P_max - P_idle) * util."""
    return p_idle + (p_max - p_idle) * cpu_pct / 100.0


def compute_session_energy(samples, windows, p_idle: float, p_max: float,
                           max_gap_s: float = 10.0) -> dict:
    """
    Integrate power over a (ts_sec, cpu_pct) time series, splitting energy into
    attack-window vs idle using the same ground-truth windows as get_true_label.
    Each interval [t_i, t_{i+1}) is priced at the power implied by cpu_pct at t_i
    (left rectangle rule) and capped at max_gap_s to avoid inflating energy
    across large gaps in the log. Returns {} if fewer than 2 samples.
    """
    if len(samples) < 2:
        return {}
    total_j = total_s = 0.0
    attack_j = attack_s = 0.0
    idle_j = idle_s = 0.0
    for (t0, cpu0), (t1, _) in zip(samples, samples[1:]):
        dt = min(t1 - t0, max_gap_s)
        if dt <= 0:
            continue
        p = power_w(cpu0, p_idle, p_max)
        e = p * dt
        total_j += e
        total_s += dt
        if get_true_label(t0, windows) == "outside":
            idle_j += e
            idle_s += dt
        else:
            attack_j += e
            attack_s += dt
    return {
        "duration_s": total_s,
        "total_energy_j": round(total_j, 2),
        "total_energy_wh": round(total_j / 3600, 4),
        "avg_power_w": round(total_j / total_s, 3) if total_s else 0.0,
        "attack": {
            "energy_j": round(attack_j, 2),
            "duration_s": attack_s,
            "avg_power_w": round(attack_j / attack_s, 3) if attack_s else 0.0,
        },
        "idle": {
            "energy_j": round(idle_j, 2),
            "duration_s": idle_s,
            "avg_power_w": round(idle_j / idle_s, 3) if idle_s else 0.0,
        },
    }
```

- [ ] **Step 3: Run the validation script again**

```bash
python3 /tmp/test_session_energy.py
```

Expected: both `OK:` lines print, no `AssertionError`.

---

### Task 3: Parse the `[SUMMARY]` block

**Files:**
- Modify: `scripts/ids_metrics.py` (near `parse_snapshot_log`)

- [ ] **Step 1: Write a throwaway validation script**

```bash
cat > /tmp/test_summary_parse.py << 'EOF'
import sys
sys.path.insert(0, "scripts")
from ids_metrics import parse_summary_block
import tempfile, os

sample = (
    "[ALERTS]\n"
    "# header\n"
    "18:00:02\t100.0%\t...\n"
    "\n[SUMMARY]\n"
    "end_time             = 2026-06-01 18:07:09\n"
    "flows_processed      = 1,234\n"
    "avg_e2e_ms           = 0.42\n"
    "\n[SYSTEM_METRICS]\n"
    "cpu_avg_pct          = 11.8\n"
)
with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
    f.write(sample)
    path = f.name
result = parse_summary_block(path)
os.unlink(path)
assert result == {
    "end_time": "2026-06-01 18:07:09",
    "flows_processed": "1,234",
    "avg_e2e_ms": "0.42",
}, result
print("OK:", result)

with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
    f.write("[ALERTS]\nno summary here\n")
    path2 = f.name
assert parse_summary_block(path2) == {}
os.unlink(path2)
print("OK: missing block returns {}")
EOF
python3 /tmp/test_summary_parse.py
```

Expected: `ImportError: cannot import name 'parse_summary_block'`.

- [ ] **Step 2: Implement `parse_summary_block`**

Add near `parse_snapshot_log`:

```python
_RE_SUMMARY_KV = re.compile(r'^(\w+)\s*=\s*(.+)$')


def parse_summary_block(path: str) -> dict:
    """Parse the '[SUMMARY] key = value' block written by _finalize_report().
    Stops at the next '[SECTION]' header. Returns {} if no [SUMMARY] found
    (e.g. the session was killed before a graceful shutdown)."""
    in_summary = False
    result = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line == "[SUMMARY]":
                in_summary = True
                continue
            if in_summary:
                if not line or line.startswith("["):
                    break
                m = _RE_SUMMARY_KV.match(line)
                if m:
                    result[m.group(1)] = m.group(2)
    return result
```

- [ ] **Step 3: Run the validation script again**

```bash
python3 /tmp/test_summary_parse.py
```

Expected: both `OK:` lines print.

---

### Task 4: Approximate per-inference energy

**Files:**
- Modify: `scripts/ids_metrics.py` (near `compute_session_energy`)

- [ ] **Step 1: Write a throwaway validation script**

```bash
cat > /tmp/test_inference_energy.py << 'EOF'
import sys
sys.path.insert(0, "scripts")
from ids_metrics import compute_inference_energy

summary = {"flows_processed": "1,000", "avg_e2e_ms": "1.0", "cpu_avg_pct": "10.0"}
# power at 10% util: 2.0 + (11.0-2.0)*0.10 = 2.9 W
# energy per flow: 2.9 W * 0.001 s = 0.0029 J = 2.9 mJ
# total: 1000 * 0.0029 J = 2.9 J
result = compute_inference_energy(summary, session_energy_j=100.0, p_idle=2.0, p_max=11.0)
assert abs(result["mj_per_flow"] - 2.9) < 0.001, result
assert abs(result["total_j"] - 2.9) < 0.001, result
assert abs(result["pct_of_session_energy"] - 2.9) < 0.01, result
print("OK:", result)

assert compute_inference_energy({}, 100.0, 2.0, 11.0) == {}
print("OK: missing summary returns {}")
EOF
python3 /tmp/test_inference_energy.py
```

Expected: `ImportError: cannot import name 'compute_inference_energy'`.

- [ ] **Step 2: Implement `compute_inference_energy`**

```python
def compute_inference_energy(summary: dict, session_energy_j: float,
                             p_idle: float, p_max: float) -> dict:
    """Coarse approximation of total inference energy from [SUMMARY] aggregates:
    one average power figure (at cpu_avg_pct) applied to every flow's average
    e2e latency. Returns {} if the summary block is missing or incomplete."""
    try:
        flows = int(str(summary["flows_processed"]).replace(",", ""))
        avg_e2e_ms = float(summary["avg_e2e_ms"])
        cpu_avg_pct = float(summary["cpu_avg_pct"])
    except (KeyError, ValueError):
        return {}
    if flows <= 0:
        return {}
    p = power_w(cpu_avg_pct, p_idle, p_max)
    j_per_flow = p * (avg_e2e_ms / 1000.0)
    total_j = j_per_flow * flows
    pct = (total_j / session_energy_j * 100) if session_energy_j else 0.0
    return {
        "flows": flows,
        "mj_per_flow": round(j_per_flow * 1000, 4),
        "total_j": round(total_j, 4),
        "pct_of_session_energy": round(pct, 2),
    }
```

- [ ] **Step 3: Run the validation script again**

```bash
python3 /tmp/test_inference_energy.py
```

Expected: both `OK:` lines print.

---

### Task 5: Printer and CLI wiring

**Files:**
- Modify: `scripts/ids_metrics.py`:
  - Add `print_energy_report` near the other `print_*` functions (after `print_binary_report`, around line 366).
  - Add `--p-idle`/`--p-max` CLI args in `main()` (near the other `ap.add_argument` calls, around line 380).
  - Call the new pipeline at the end of `main()`, right before `if args.output:` (around line 534).

- [ ] **Step 1: Add the printer**

```python
def print_energy_report(energy: dict, inference: dict, p_idle: float, p_max: float) -> None:
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║   ENERGIA ESTIMADA (modelo linear CPU)                  ║")
    print("╚══════════════════════════════════════════════════════════╝")
    if not energy:
        print("\n  [sem linhas SYS_SNAPSHOT no log — seção de energia indisponível]")
        return
    print(f"\n  P_idle = {p_idle:.1f} W | P_max = {p_max:.1f} W")
    print(f"  Duração da sessão        : {energy['duration_s']:.0f} s")
    print(f"  Energia total            : {energy['total_energy_j']:.1f} J  "
          f"({energy['total_energy_wh']:.4f} Wh)")
    print(f"  Potência média           : {energy['avg_power_w']:.2f} W")
    a, i = energy["attack"], energy["idle"]
    print(f"    Durante ataques        : {a['energy_j']:.1f} J em {a['duration_s']:.0f} s "
          f"({a['avg_power_w']:.2f} W médio)")
    print(f"    Fora de ataques (idle) : {i['energy_j']:.1f} J em {i['duration_s']:.0f} s "
          f"({i['avg_power_w']:.2f} W médio)")
    if inference:
        print(f"\n  Energia de inferência (aprox., via [SUMMARY] e2e_ms agregado):")
        print(f"    {inference['mj_per_flow']:.4f} mJ/flow × {inference['flows']} flows "
              f"= {inference['total_j']:.2f} J ({inference['pct_of_session_energy']:.2f}% da energia total)")
    else:
        print(f"\n  Energia de inferência    : [sem bloco SUMMARY — sessão não finalizada graciosamente]")
```

- [ ] **Step 2: Add CLI args**

In `main()`, after the `--label-map` argument:

```python
    ap.add_argument("--p-idle", type=float, default=2.0,
                    help="Idle power in watts for the linear CPU power model (default: 2.0)")
    ap.add_argument("--p-max", type=float, default=11.0,
                    help="Max-load power in watts for the linear CPU power model (default: 11.0)")
```

- [ ] **Step 3: Wire it into `main()`**

Immediately before `if args.output:` (the final block of `main()`):

```python
    samples = sorted(parse_snapshot_log(args.ids))
    energy = compute_session_energy(samples, windows, args.p_idle, args.p_max)
    summary_block = parse_summary_block(args.ids)
    inference_energy = (
        compute_inference_energy(summary_block, energy["total_energy_j"], args.p_idle, args.p_max)
        if energy else {}
    )
    print_energy_report(energy, inference_energy, args.p_idle, args.p_max)
    if energy:
        summary["energy"] = {
            "p_idle_w": args.p_idle,
            "p_max_w": args.p_max,
            "session": energy,
            "inference": inference_energy or None,
        }
```

- [ ] **Step 4: Sanity-check the script still runs standalone**

```bash
python3 scripts/ids_metrics.py --help
```

Expected: argparse help text prints, including the new `--p-idle`/`--p-max` flags, no traceback.

---

### Task 6: Validate against the real logs

**Files:**
- None (read-only validation run)

- [ ] **Step 1: Run against the binary IDS log**

```bash
python3 scripts/ids_metrics.py \
  --ids     logs/binary_ids_run_20260601_175953.log \
  --report  logs/report_20260601_150417.json \
  --mode    binary \
  --output  /tmp/energy_binary_check.json
```

Expected: report prints normally (existing sections unchanged) plus a new
"ENERGIA ESTIMADA" block at the end with `avg_power_w` between 2.0 and 11.0 W,
and "Energia de inferência" showing the `[sem bloco SUMMARY ...]` message
(confirmed in the design doc that this real log has no `[SUMMARY]` block).
If the `--report` timestamp doesn't match this run, check
`docs/results/session_report_20260601.md` section 5.1 for the correct
orchestrator report filename pairing and substitute it.

- [ ] **Step 2: Run against the multiclass IDS log**

```bash
python3 scripts/ids_metrics.py \
  --ids     logs/ids_run_20260601_175451.log \
  --report  logs/report_20260601_145906.json \
  --mode    multiclass \
  --output  /tmp/energy_multiclass_check.json
```

Expected: same shape of output, energy block present, inference block shows
the missing-`[SUMMARY]` message. Again check the matching report filename in
the session report if this pairing is wrong.

- [ ] **Step 3: Inspect the JSON output**

```bash
python3 -c "import json; d = json.load(open('/tmp/energy_binary_check.json')); print(json.dumps(d['energy'], indent=2))"
```

Expected: a dict with `p_idle_w`, `p_max_w`, `session` (with `total_energy_j`,
`attack`, `idle` sub-dicts), and `inference: null`.

- [ ] **Step 4: Validate the inference-energy path with a synthetic `[SUMMARY]` block**

Confirms Task 4's code path actually fires when a session does shut down
gracefully (neither real log exercises it):

```bash
cp logs/binary_ids_run_20260601_175953.log /tmp/binary_with_summary.log
cat >> /tmp/binary_with_summary.log << 'EOF'

[SUMMARY]
flows_processed      = 5,000
avg_e2e_ms           = 0.50
cpu_avg_pct          = 11.8
EOF
python3 scripts/ids_metrics.py \
  --ids     /tmp/binary_with_summary.log \
  --report  logs/report_20260601_150417.json \
  --mode    binary
```

Expected: the "Energia de inferência" line now prints real `mJ/flow`,
`total_j`, and `% da energia total` numbers instead of the missing-block
message.

- [ ] **Step 5: Clean up the temp files**

```bash
rm -f /tmp/test_snapshot_parse.py /tmp/test_session_energy.py \
      /tmp/test_summary_parse.py /tmp/test_inference_energy.py \
      /tmp/energy_binary_check.json /tmp/energy_multiclass_check.json \
      /tmp/binary_with_summary.log
```

---

### Task 7: Commit (only with explicit permission)

CLAUDE.md for this project states changes should only be committed when the
user explicitly allows it. Do not run `git commit` as part of executing this
plan — instead, once Task 6 passes, summarize what changed and ask the user
whether to commit. If they say yes, then run:

```bash
git add scripts/ids_metrics.py docs/superpowers/specs/2026-06-16-energy-estimation-design.md docs/superpowers/plans/2026-06-16-energy-estimation.md
git commit -m "$(cat <<'EOF'
Add CPU-utilization-based energy estimate to ids_metrics.py

Replaces the manual ~2.3-2.8W back-of-envelope estimate in the article with
a number computed from the real SYS_SNAPSHOT CPU time series, split into
attack-window vs idle energy using the existing ground-truth windows.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

Do not update `docs/artigo.tex` or `docs/results/session_report_20260601.md`
with the new numbers as part of this plan — that's a follow-up decision once
the user has seen the real output from Task 6 and decided on final
`--p-idle`/`--p-max` values.
