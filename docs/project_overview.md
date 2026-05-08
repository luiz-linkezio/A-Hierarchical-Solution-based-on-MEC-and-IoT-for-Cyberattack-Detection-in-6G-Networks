# Project Overview — Hierarchical MEC/IoT IDS for 6G Networks

## Objective

Build a three-phase hierarchical Intrusion Detection System (IDS) tailored for IoT environments backed by Multi-access Edge Computing (MEC), motivated by 6G network evolution: massive IoT density, tight latency budgets, and growing AI use for management and security.

The hierarchy distributes workload by capability:

| Phase | Where it runs | What it decides |
|-------|--------------|-----------------|
| 1 — Binary classifier | VIM (edge node) | Benign vs. attack |
| 2 — Multi-classifier | Edge / MEC host | Attack type (DDoS, DoS, malware, …) |
| 3 — Clustering | Edge / MEC host | Unknown / zero-day threats not recognized by Phase 2 |

Phases 2 and 3 are still in development; Phase 1 is complete and deployed as `scripts/network_binary_ids.py`.

---

## Design Decisions

### Why PCAP-only datasets?

Public IDS datasets usually ship as pre-computed CSVs with inconsistent column names, different feature sets, and no common schema — making cross-dataset training impractical without extensive per-dataset adapters.

PCAPs are a universal network capture format: every packet is recorded identically regardless of the tool that captured it. The label information comes from how the captures are organized — folders are named after the traffic type (e.g., `benign/`, `ddos/`, `bruteforce/`), so no per-row label column is needed in the raw capture.

**Only datasets that ship with separately labeled PCAPs were selected.** This makes the pipeline fully reproducible with any PCAP-to-flow tool and avoids schema inconsistency across datasets.

### Datasets used

| Dataset | Source |
|---------|--------|
| CIC APT IIoT 2024 | Canadian Institute for Cybersecurity |
| CIC IoT Dataset 2023 | Canadian Institute for Cybersecurity |
| CIC IoT DIAD 2024 | Canadian Institute for Cybersecurity |
| CIC IIoT Dataset 2025 | Canadian Institute for Cybersecurity |
| CIC BCCC NRC IoMT 2024 | Canadian Institute for Cybersecurity |

### Attack taxonomy

After unification across datasets, the label set is:

- **Benign**: `benign`
- **Malicious**: `ddos`, `dos`, `malware`, `bruteforce`, `mitm`, `web`, `spoofing`, `recon`

---

## Data Pipeline

### The memory and randomization problem

Raw PCAPs across all datasets total roughly **1 TB**. Reading that much data as CSV into RAM to build a balanced training set is infeasible on any single machine:

- Full CSVs cannot be loaded into memory.
- CSVs do not support random-access row sampling without reading sequentially.
- Class imbalance across datasets would produce a skewed training set if files are taken in order.

### Solution: PCAP → labeled CSV → SQLite

```
Dataset download
        ↓  manual: rename folders to match project taxonomy
PCAPs organized in labeled folders (benign/, ddos/, malware/, …)
        ↓  data_preprocessing.ipynb + pcapflower
Labeled CSVs (one per folder, `label` column = folder name)
        ↓  database_creation.ipynb (chunked streaming insert)
Unified SQLite database  ←  ~190 GB  (was ~1 TB as PCAPs)
```

SQLite's `ORDER BY RANDOM() LIMIT n` allows truly random, memory-bounded sampling of any class at query time — solving both the memory and the randomization problems simultaneously. The ~5× compression from PCAP to SQLite is a side benefit.

### Step-by-step

**1. Download a dataset with labeled PCAPs.**  
Only datasets that ship with PCAPs separated by category are considered (a folder per traffic type). Datasets that only provide pre-computed CSVs are excluded because their feature schemas are inconsistent across sources.

**2. Rename folders to match the project taxonomy (manual).**  
Dataset authors use their own naming conventions. Before running any notebook, folder names are manually aligned to the project label set:

| Original folder name | Renamed to | Reason |
|----------------------|-----------|--------|
| `web-app`, `web_attack` | `web` | Same attack family |
| `mirai`, `bot` | `malware` | Mirai is a malware variant |
| `syn-flood` | `dos` | Syn flood is a DoS technique |
| *(etc.)* | | |

This is the only manual step in the pipeline. The folder name becomes the row-level `label` in the final database, so getting it right here propagates cleanly through the rest.

**3. Convert each folder's PCAPs into a single labeled CSV (`data_preprocessing.ipynb`).**  
The notebook walks the PCAP folder tree, calls `pcapflower` on each folder, injects the folder name as the `label` column, and writes one `merged_<folder>.csv` per folder.

**4. Load the CSV into the unified SQLite database (`database_creation.ipynb`).**  
Streams every `merged_*.csv` into `data/sqlite/data.db` in 50 000-row chunks, one SQLite table per top-level dataset directory. Datasets added later are simply appended — the same database accumulates all traffic over time. An index on `label` enables fast class-level queries.

**5. Analyze (`dataset_analysis.ipynb`) and train (`training.ipynb`).**  
Both notebooks query the database directly, never touching raw CSVs or PCAPs again.

---

## pcapflower — Custom PCAP-to-Flow Tool

The standard tool for PCAP→flow conversion in the IDS research community is **CICFlowMeter** (used in the early stages of this project). It was replaced by **[pcapflower](https://pypi.org/project/pcapflower/)**, a tool we developed and published to PyPI for this project.

Key improvements over CICFlowMeter:

- **Parallelism** — can process multiple PCAP files concurrently; CICFlowMeter is sequential.
- **Performance** — significantly faster throughput per file.
- **Pip-installable** — `pip install pcapflower`; no Java dependency.

The preprocessing notebook and the live IDS script both invoke `pcapflower` as a subprocess.

---

## Feature Engineering & Selection

Starting from 83 raw flow-level columns produced by pcapflower, the training notebook applies the following cleaning steps:

| Step | Removed features | Rationale |
|------|-----------------|-----------|
| Useless features | `timestamp` | Leaks capture order, not generalizable |
| High correlation (> 0.95) | 15 features | Redundant information; e.g., `ack_flag_cnt`, `pkt_size_avg`, `fwd_seg_size_avg` |
| Near-zero variance (< 1e-4) | `fwd_urg_flags`, `bwd_urg_flags`, `urg_flag_cnt` | Carry almost no signal |
| Duplicate rows | 25 049 rows removed | Exact duplicates from overlapping dataset captures |
| Inf / NaN rows | 0 removed (clean after sampling) | Defensive step |

Final feature count after cleaning: **63 numeric features** (excluding the `label` column). The authoritative list is in `constants/features.py`.

---

## Phase 1 — Binary Classifier

### Training setup

- **Algorithm**: LightGBM (`LGBMClassifier`)
- **Sampling**: 400 000 benign rows + 400 000 attack rows (distributed evenly across the 8 attack classes from the SQLite database via `ORDER BY RANDOM() LIMIT n`)
- **Split**: 80% train / 20% test, stratified
- **Class weights**: `balanced` (mitigates residual imbalance inside the attack pool)

### Hyperparameter optimization (Optuna)

20 trials with a 1 800 s timeout using 3-fold `StratifiedKFold` cross-validation. **The decision threshold is tuned jointly with the model hyperparameters**, which is a deliberate design choice.

**Objective function: maximize attack recall.**

The rationale: this is a detection system, not a prevention system (IDS, not IPS). A false negative (missed attack) is more costly than a false positive (benign traffic flagged as attack). Tuning the threshold as part of Optuna means the model can accept lower precision on the attack class in exchange for catching every real attack it can.

### Best result

| Metric | Attack class | Benign class |
|--------|-------------|-------------|
| Precision | 0.97 | 0.85 |
| Recall | 0.82 | 0.97 |
| F1 | 0.89 | 0.91 |
| Accuracy (overall) | — | **0.90** |

Optimized threshold: `~0.011` (very low — the model flags anything with even a small attack probability).

Model saved at `models/binary_classifier.pkl` (joblib format).

---

## Real-Time IDS Script (VIM 4)

`scripts/network_binary_ids.py` is the edge-deployment component for Phase 1.

**How it works:**

1. Launches `tcpdump` in the background on a configurable network interface, rotating capture files every `CHUNK_SIZE_MB` MB.
2. Picks up completed PCAP chunks (all but the file currently being written).
3. Calls `pcapflower` on each chunk to produce a flow-level CSV.
4. Aligns the CSV columns to the model's expected feature set (fills missing columns with 0).
5. Runs `model.predict_proba()` on the flows.
6. Logs an `[ALERT]` for any flow where the attack-class probability exceeds `THRESHOLD` (default 0.8).
7. Deletes the PCAP and CSV after processing to avoid disk accumulation.

The script is self-contained and reads the model path and feature names at startup.

---

## Repository Structure

```
.
├── constants/
│   ├── features.py        # FINAL_FEATURES and EXCLUDED_FEATURES lists
│   └── labels.py          # BENIGN_LABELS, MALICIOUS_LABELS
├── data/                  # local only — not in Git
│   ├── raw/               # downloaded PCAPs and generated flow CSVs
│   └── sqlite/data.db     # unified SQLite database
├── docs/
│   ├── features_report.txt  # last feature cleaning summary from training
│   ├── labels_list.txt      # human-readable label taxonomy
│   └── project_overview.md  # this file
├── models/
│   └── binary_classifier.pkl  # Phase 1 LightGBM model (joblib)
├── notebooks/
│   ├── data_preprocessing.ipynb   # PCAP → labeled CSV
│   ├── database_creation.ipynb    # CSV → SQLite
│   ├── dataset_analysis.ipynb     # EDA
│   └── training.ipynb             # model training (all three phases)
├── results/
│   ├── dataset_analysis/  # per-dataset Markdown reports
│   └── images/            # EDA plots
├── scripts/
│   └── network_binary_ids.py  # live binary IDS for VIM 4
└── requirements.txt
```

---

## What Is Still Pending

| Phase | Status |
|-------|--------|
| Phase 1 — Binary classifier | Done. Model trained, script deployed. |
| Phase 2 — Multi-classifier | In progress (section scaffolded in `training.ipynb`). |
| Phase 3 — Clustering (UMAP + HDBSCAN) | In progress (section scaffolded in `training.ipynb`). |
