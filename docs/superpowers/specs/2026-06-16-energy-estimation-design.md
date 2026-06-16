# Energy Estimation in ids_metrics.py — Design

## Context

The IDS scripts (`network_binary_ids.py`, `network_ids.py`) attempted direct
power measurement via Intel RAPL (`power_w` column), but this field is empty
in real runs — the VIM4 (Amlogic A311D2, ARM big.LITTLE) has no RAPL support.
`docs/results/session_report_20260601.md` (section 5.5) and `docs/artigo.tex`
currently report a manual back-of-envelope estimate (~2.3–2.8 W) assuming
~10–12 W full load and using only the mean CPU% during attacks. This design
replaces that manual calculation with a script-computed estimate driven by
the actual CPU time series already present in the IDS run logs.

## Power model

```
P(t) = P_idle + (P_max - P_idle) * cpu_pct(t) / 100
Energy = Σ P(t_i) * Δt_i   (Joules; also reported in Wh)
```

Defaults: `P_idle = 2.0 W`, `P_max = 11.0 W` — the same full-load assumption
already used in the article for the VIM4, with idle picked as a typical
ARM big.LITTLE idle draw. Both configurable via `--p-idle` / `--p-max` CLI
flags so they can be tightened later (datasheet value or USB-C wattmeter
measurement).

## Data source

IDS run logs already contain periodic lines of the form:

```
[SYS_SNAPSHOT] HH:MM:SS  CPU 0.3% | RAM 12.6% (985 MB) | Net ...
```

emitted by both `network_ids.py` and `network_binary_ids.py` on the same
cadence (~3s), covering the whole session (idle + attack periods). A new
regex in `ids_metrics.py` parses these into a `(ts_sec, cpu_pct)` time series.

## Integration point

Extend `scripts/ids_metrics.py` (not a new standalone script) so the energy
section reuses the ground-truth attack `windows` already parsed from the
`--report` JSON via `parse_orchestrator()` / `get_true_label()`. This lets
energy be split into "during attack windows" vs "idle/benign", mirroring the
split already done by hand in session_report.md section 5.3.

Applies to both `--mode binary` and `--mode multiclass` since the
`SYS_SNAPSHOT` format is identical in both log types.

## Computation

For each pair of consecutive samples `(t_i, t_{i+1})`:
- `dt = t_{i+1} - t_i`, capped at 10s to avoid inflating energy across large
  gaps (e.g. a paused process or log rotation).
- Power for that interval uses `cpu_pct` from sample `t_i` (left rectangle
  rule).
- The interval is attributed to "attack" or "idle" via `get_true_label(t_i,
  windows)`.

Outputs: total session energy (J, Wh), average power, energy/duration during
attack windows, energy/duration outside attack windows.

## Bonus: per-inference energy

`e2e_ms` is not logged per flow — only as a session aggregate, in the
`[SUMMARY]` block written by `_finalize_report()`:

```
flows_processed      = 1234
avg_e2e_ms           = 0.42
max_e2e_ms           = 3.10
...
cpu_avg_pct          = 11.8
```

Parse this block (simple `key = value` lines) and approximate total inference
energy as `flows_processed * (avg_e2e_ms / 1000) * P(cpu_avg_pct)`, reporting
mean energy per inference (mJ) and its share of total session energy. This
is a coarse approximation (one average power figure applied to every flow)
but uses only data that already exists — it answers the "medição parcial,
por etapa" question without new instrumentation.

## Output format

A new printed block (same ASCII-report style as the rest of the script),
e.g.:

```
── Energia estimada (modelo linear CPU, P_idle=2.0W, P_max=11.0W) ──
  Duração da sessão        : 457 s
  Energia total            : 1234.5 J  (0.343 Wh)
  Potência média           : 2.70 W
    Durante ataques        : 645.2 J em 285 s (2.26 W médio)
    Fora de ataques (idle) : 589.3 J em 172 s (3.43 W médio)
  Energia de inferência (e2e): 12.3 J total, 0.66 mJ/flow (1.0% da energia total)
```

Also added to the `--output` JSON summary under `summary["energy"]`, so the
two pipelines (binary vs multiclass) can be diffed across separate runs the
same way the rest of the report already is.

## Edge cases

- No `SYS_SNAPSHOT` lines found in the log (older log format): the energy
  section is skipped with a warning; the rest of the report still runs.
- No `[SUMMARY]` block found (session didn't shut down gracefully —
  confirmed true for both existing real logs, which were killed before
  `_finalize_report()` ran): the per-inference energy bonus is skipped with
  a warning; the main session/attack-window energy split still runs from
  `SYS_SNAPSHOT` data alone.
- Large gaps between samples: `dt` capped at 10s.

## Validation

The project has no automated test suite — analysis scripts are validated by
running them against real data. Validate by running the new energy section
against the two existing real logs (`logs/binary_ids_run_20260601_175953.log`,
`logs/ids_run_20260601_175451.log`) and sanity-checking the numbers (e.g.
average power should land between `P_idle` and `P_max`, roughly tracking the
already-known mean CPU% from section 5.3 of the session report). Both real
logs lack a `[SUMMARY]` block, so the per-inference bonus will report
"not available" on them — verify it degrades gracefully rather than
crashing, and confirm it would work by manually appending a synthetic
`[SUMMARY]` block to a copy of one log.
