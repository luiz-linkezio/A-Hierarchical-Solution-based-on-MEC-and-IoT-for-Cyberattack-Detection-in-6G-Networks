# Project Overview — Hierarchical MEC/IoT IDS for 6G Networks

## Objective

Build a three-phase hierarchical Intrusion Detection System (IDS) tailored for IoT environments backed by Multi-access Edge Computing (MEC), motivated by 6G network evolution: massive IoT density, tight latency budgets, and growing AI use for management and security.

The hierarchy distributes workload by capability:

| Phase | Where it runs | What it decides |
|-------|--------------|-----------------|
| 1 — Binary classifier | VIM (edge node) | Benign vs. attack |
| 2 — Multi-classifier | Edge / MEC host | Attack type (known classes + unknown proxy) |
| 3 — Clustering | Edge / MEC host | Unknown / zero-day threats forwarded from Phase 2 |

Phases 1, 2, and 3 are fully implemented in `training.ipynb`.

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
        ↓  data_preprocessing.ipynb + netflower
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
The notebook walks the PCAP folder tree, calls `netflower` on each folder, injects the folder name as the `label` column, and writes one `merged_<folder>.csv` per folder.

**4. Load the CSV into the unified SQLite database (`database_creation.ipynb`).**  
Streams every `merged_*.csv` into `data/sqlite/data.db` in 50 000-row chunks, one SQLite table per top-level dataset directory. Datasets added later are simply appended — the same database accumulates all traffic over time. An index on `label` enables fast class-level queries.

**5. Analyse (`dataset_analysis.ipynb`) and train (`training.ipynb`).**  
Both notebooks query the database directly, never touching raw CSVs or PCAPs again.
`training.ipynb` runs all three phases end-to-end and saves all models to `models/`.

---

## netflower — Custom PCAP-to-Flow Tool

The standard tool for PCAP→flow conversion in the IDS research community is **CICFlowMeter** (used in the early stages of this project). It was replaced by **[netflower](https://pypi.org/project/netflower/)**, a tool we developed and published to PyPI for this project.

Key improvements over CICFlowMeter:

- **Parallelism** — can process multiple PCAP files concurrently; CICFlowMeter is sequential.
- **Performance** — significantly faster throughput per file.
- **Pip-installable** — `pip install netflower`; no Java dependency.

The preprocessing notebook and the live IDS script both invoke `netflower` as a subprocess.

---

## Feature Engineering & Selection

Starting from 83 raw flow-level columns produced by netflower, the training notebook applies the following cleaning steps (Phase 1 cleaning run, on the binary-sampled dataset):

| Step | Removed features | Rationale |
|------|-----------------|-----------|
| Useless features | `timestamp` | Leaks capture order, not generalizable |
| High correlation (> 0.95) | 14 features | Redundant information; e.g., `bwd_pkts_b_avg`, `psh_flag_cnt`, `idle_mean` |
| Near-zero variance (< 1e-4) | `fwd_urg_flags`, `bwd_urg_flags`, `urg_flag_cnt` | Carry almost no signal |
| Duplicate rows | ~25 000 rows removed | Exact duplicates from overlapping dataset captures |
| Inf / NaN rows | 0 removed (clean after sampling) | Defensive step |

The authoritative feature list is in `constants/features.py`:
- **`FINAL_FEATURES`** — 64 entries including `label`, `src_ip`, `dst_ip`; the 61 numeric entries are used directly by Phase 2.
- **`EXCLUDED_FEATURES`** — grouped by removal reason.

Phase 1 uses a slightly different set (62 numeric features) because it recomputes cleaning on its own sample and the correlation results differ slightly from the constants snapshot. Phase 2 skips recomputation and reads `FINAL_FEATURES` directly for consistency.

---

## Phase 1 — Binary Classifier

### Training setup

- **Algorithm**: LightGBM (`LGBMClassifier`)
- **Sampling**: 400 000 benign rows + 400 000 attack rows (distributed evenly across the 8 attack classes from the SQLite database via `ORDER BY RANDOM() LIMIT n`)
- **Split**: 80% train / 20% test, stratified
- **Class weights**: none (balanced by sampling)

### Hyperparameter optimization (Optuna)

20 trials with a 1 800 s timeout using 3-fold `StratifiedKFold` cross-validation. **The decision threshold is tuned jointly with the model hyperparameters**, which is a deliberate design choice.

**Objective function: maximize F2-score on the attack class.**

The rationale: this is a detection system, not a prevention system (IDS, not IPS). A false negative (missed attack) is more costly than a false positive (benign traffic flagged as attack). The F2-score weights recall 4× more than precision. Tuning the threshold as part of Optuna means the model can accept lower precision in exchange for catching every real attack it can.

### Best result

| Metric | Attack class | Benign class |
|--------|-------------|-------------|
| Precision | 0.81 | 0.94 |
| Recall | 0.94 | 0.79 |
| F1 | 0.87 | 0.86 |
| Accuracy (overall) | — | **0.87** |

Optimized threshold: `~0.19` (flows with attack probability above this are flagged).

Model saved at `models/binary_classifier.pkl` (joblib format).

---

## Phase 2 — Multi-class Classifier

### Problem setup

Receives flows flagged as "attack" by Phase 1 (plus a small benign fallback path for flows Phase 1 misclassified). Classifies each flow into one of the following label categories:

| Label | Description |
|-------|-------------|
| `benign` | Fallback — benign flows Phase 1 incorrectly flagged as attack |
| `ddos` | DDoS attacks |
| `dos` | DoS attacks |
| `malware` | Malware traffic |
| `recon` | Reconnaissance traffic |
| `unknown` | Proxy for unknown / zero-day attacks (see below) |

### The "unknown" class

Half of the 8 attack classes (4 classes) are relabeled as `unknown` during training. `bruteforce` is always among them (fewest samples — ~16k rows in the database). The full set is `["bruteforce", "mitm", "spoofing", "web"]`.

**Why this works as a novelty proxy:** the model learns to output `unknown` when it encounters traffic patterns from those four families. In production, a truly novel attack whose flow profile resembles any of the four relabeled families will tend to be classified as `unknown` rather than being forced into a wrong known class — making the routing to Phase 3 more reliable.

Controlled by `PHASE2_UNKNOWN_CLASSES` in the Config cell of `training.ipynb`.

### Training setup

- **Algorithm**: LightGBM (`LGBMClassifier`, `objective='multiclass'`)
- **Feature set**: same 62 numeric features as Phase 1 — derived directly from the already-cleaned `df` via `drop(select_dtypes(exclude="number"))`, avoiding a second database query
- **Sampling**: `df` is subsampled to `PHASE2_SAMPLES_PER_CLASS` (50 000) rows per class using `groupby + sample`; classes with fewer available rows (e.g., `unknown`) return what's available
- **Class weights**: `balanced` — automatically compensates for `unknown` having fewer samples than the 50k-capped classes
- **Split**: 80% train / 20% test, stratified
- **Optimization**: Optuna, 20 trials, 1 800 s timeout, 3-fold `StratifiedKFold`, **objective: maximize macro F1**

Macro F1 is used (rather than F2 as in Phase 1) because at this stage all classes should be treated symmetrically — there is no single "most important" class to bias towards.

### Confidence routing to Phase 3

After prediction, `model.predict_proba()` returns a probability vector over all classes. If `max(proba) < PHASE2_CONFIDENCE_THRESHOLD` (default `0.6`), the flow is forwarded to Phase 3 rather than committed to a label. This handles truly novel attacks that don't match any trained pattern well enough to assign confidently.

Model saved at `models/multiclass_classifier.pkl` (joblib format).

---

## Phase 3 — Clustering (UMAP + HDBSCAN)

Receives flows whose Phase 2 maximum predicted probability is below
`PHASE2_CONFIDENCE_THRESHOLD` (default `0.6`) — i.e., flows that could not be
confidently assigned to any known attack class.

### Pipeline

1. **UMAP** (`n_components=10`, `n_neighbors=30`, `min_dist=0.0`) compresses the
   feature space into a dense embedding that preserves local structure. A low
   `min_dist` produces tighter clusters, which helps HDBSCAN find density peaks.
2. **HDBSCAN** (`min_cluster_size=100`, `min_samples=50`) identifies clusters of
   similar flows. Points that do not belong to any cluster receive label `-1`
   (noise). Each non-noise cluster is a candidate novel attack category.
3. A 2-D UMAP embedding (separate, for visualisation only) is plotted to give an
   intuitive view of the cluster structure.

Models are saved at `models/umap_reducer.pkl` and `models/hdbscan_clusterer.pkl`.

---

## Real-Time IDS Script (VIM 4)

`scripts/network_binary_ids.py` is the edge-deployment component for Phase 1.

**How it works:**

1. Launches `tcpdump` in the background on a configurable network interface (`INTERFACE`, default `eth0`), rotating capture files every `CHUNK_SIZE_MB` MB (default 1 MB).
2. Picks up completed PCAP chunks (all but the file currently being written).
3. Calls `netflower` on each chunk to produce a flow-level CSV.
4. Aligns the CSV columns to the model's expected feature set (fills missing columns with 0; reads `model.feature_names_in_` when available, falls back to `FINAL_FEATURES` from constants).
5. Runs `model.predict_proba()` on the flows.
6. Logs an `[ALERT]` for any flow where the attack-class probability exceeds `THRESHOLD` (default 0.5).
7. Deletes the PCAP and CSV after processing to avoid disk accumulation.
8. A background stats thread logs packet count, total flows processed, and alert count every 3 seconds.

The script reads `constants/features.py` and `constants/labels.py` at startup to determine input features and benign class labels.

---

## Repository Structure

```
.
├── constants/
│   ├── features.py        # FINAL_FEATURES (64 entries) and EXCLUDED_FEATURES
│   └── labels.py          # BENIGN_LABELS, MALICIOUS_LABELS
├── data/                  # local only — not in Git
│   ├── raw/               # downloaded PCAPs and generated flow CSVs
│   └── sqlite/data.db     # unified SQLite database (~190 GB)
├── docs/
│   ├── features_report.txt  # last feature cleaning summary from training
│   ├── labels_list.txt      # human-readable label taxonomy
│   └── project_overview.md  # this file
├── models/
│   ├── binary_classifier.pkl       # Phase 1 LightGBM model (joblib)
│   ├── multiclass_classifier.pkl  # Phase 2 LightGBM model (joblib)
│   ├── umap_reducer.pkl           # Phase 3 UMAP reducer (joblib)
│   └── hdbscan_clusterer.pkl      # Phase 3 HDBSCAN clusterer (joblib)
├── notebooks/
│   ├── data_preprocessing.ipynb   # PCAP → labeled CSV
│   ├── database_creation.ipynb    # CSV → SQLite
│   ├── dataset_analysis.ipynb     # EDA
│   └── training.ipynb             # model training (all three phases)
├── results/
│   ├── dataset_analysis/  # per-dataset Markdown reports
│   └── images/            # EDA plots
├── scripts/
│   └── network_binary_ids.py  # live binary IDS for VIM 4 (Phase 1)
└── requirements.txt
```

---

## What Is Still Pending

| Phase | Status |
|-------|--------|
| Phase 1 — Binary classifier | Done. Model trained, script deployed. |
| Phase 2 — Multi-classifier | Done. Model trained and saved. Real-time script not yet implemented. |
| Phase 3 — Clustering (UMAP + HDBSCAN) | Done. UMAP + HDBSCAN pipeline implemented in `training.ipynb`. Models saved to `models/`. Real-time script not yet implemented. |
