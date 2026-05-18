# Project Overview — Hierarchical MEC/IoT IDS for 6G Networks

## Objective

Build a three-phase hierarchical Intrusion Detection System (IDS) tailored for IoT environments backed by Multi-access Edge Computing (MEC), motivated by 6G network evolution: massive IoT density, tight latency budgets, and growing AI use for management and security.

The hierarchy distributes workload by capability:

| Phase | Where it runs | What it decides |
|-------|--------------|-----------------|
| 1 — Binary classifier | VIM (edge node) | Benign vs. attack |
| 2 — Multi-classifier | Edge / MEC host | Attack type across all known classes |
| 3 — Clustering | Edge / MEC host | Potential zero-day threats (low-confidence flows from Phase 2) |

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
`training.ipynb` runs all three phases end-to-end and saves all models to `models/`. After each run it also writes a timestamped Markdown results document to `docs/results/training_<YYYYMMDD_HHMMSS>.md`, capturing the full training configuration, feature set, Optuna results, classification reports, model paths, and **inline plot images** for every phase. The three plots — Phase 1 feature importance, Phase 2 feature importance, and the Phase 3 UMAP cluster scatter — are saved as PNGs under `docs/results/images/` (named with the same timestamp as the report) and referenced by relative Markdown image links inside the report, so the document is self-contained and renders correctly in any Markdown viewer.

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
| Useless / identity features | `timestamp`, `src_ip`, `dst_ip`, `src_port`, `dst_port` | `timestamp` leaks capture order; IP/port columns are flow identifiers, not statistical signals, and cause the model to memorize specific hosts/services rather than learn traffic patterns |
| Init window sentinel | `init_fwd_win_byts`, `init_bwd_win_byts` | netflower writes `-1` when the TCP handshake window size is unavailable. This `-1` sentinel does not appear in real traffic; the model learns to trigger on it, producing false positives on normal flows where the field is genuinely missing |
| Bulk rate features | `fwd_byts_b_avg`, `bwd_byts_b_avg`, `fwd_pkts_b_avg`, `bwd_pkts_b_avg`, `fwd_blk_rate_avg`, `bwd_blk_rate_avg` | These are zero for virtually all real-world flows (they require bulk-detection heuristics not applied by netflower in live mode). They are non-zero only in the training datasets, creating a distribution shift between training and deployment |
| High correlation (> 0.95) | 11 features | Redundant information; e.g., `psh_flag_cnt`, `idle_mean`, `pkt_size_avg` |
| Near-zero variance (< 1e-4) | `fwd_urg_flags`, `bwd_urg_flags`, `urg_flag_cnt` | Carry almost no signal |
| Duplicate rows | eliminated at query time | `SELECT DISTINCT *` is applied directly in the SQLite query, so duplicate rows from overlapping dataset captures never reach pandas. This is more efficient than dropping duplicates in-memory after loading |
| Inf / NaN rows | 0 removed (clean after sampling) | Defensive step |

The authoritative feature list is in `constants/features.py`:
- **`FINAL_FEATURES`** — 68 entries including `label`, `src_ip`, `dst_ip`; the 65 numeric entries are used directly by Phase 2.
- **`EXCLUDED_FEATURES`** — grouped by removal reason.

`constants/features.py` is kept in sync automatically: the cell in `training.ipynb` that writes `docs/features_report.txt` is immediately followed by a cell that regenerates `constants/features.py` from the same in-memory variables (`final_features`, `removed_features`). Running the training notebook always leaves both files consistent.

Phase 1 uses a slightly different set (65 numeric features) because it recomputes cleaning on its own sample and the correlation results differ slightly from the constants snapshot. Phase 2 skips recomputation and reads `FINAL_FEATURES` directly for consistency.

---

## Phase 1 — Binary Classifier

### Training setup

- **Algorithm**: LightGBM (`LGBMClassifier`)
- **Sampling**: 400 000 benign rows + 400 000 attack rows (distributed evenly across the 8 attack classes from the SQLite database via `ORDER BY RANDOM() LIMIT n`)
- **Split**: 80% train / 20% test, stratified
- **Class weights**: none (balanced by sampling)

### Hyperparameter optimization (Optuna)

20 trials with a 1 800 s timeout using 3-fold `StratifiedKFold` cross-validation. **The decision threshold is tuned jointly with the model hyperparameters**, which is a deliberate design choice.

**Objective function: maximize F2-score (beta=2) on the attack class.**

The rationale: this is a detection system, not a prevention system (IDS, not IPS). A false negative (missed attack) is more costly than a false positive (benign traffic flagged as attack). The F2-score weights recall 4× more than precision, aggressively prioritising attack detection. Tuning the threshold as part of Optuna means the model can accept lower precision in exchange for catching real attacks.

### Best result

| Metric | Attack class | Benign class |
|--------|-------------|-------------|
| Precision | 0.81 | 0.94 |
| Recall | 0.94 | 0.79 |
| F1 | 0.87 | 0.86 |
| Accuracy (overall) | — | **0.87** |

Optimized threshold: `~0.19` (flows with attack probability above this are flagged).

After saving the model, the notebook automatically updates two constants in `scripts/network_binary_ids.py` via regex substitution: `THRESHOLD` (the decision threshold optimised by Optuna) and `MODEL_PATH` (the path to the newly trained model file). Both constants are rewritten in a single cell, ensuring the live IDS script always points to the exact model produced by the last training run, with no manual step required.

A **feature importance bar chart** (top 20 features by LightGBM `gain`) is displayed immediately after the evaluation cell, using `model.feature_importances_`. This gives a quick visual of which flow statistics drive the binary decision.

Model saved at `models/binary_classifier_<YYYYMMDD_HHMMSS>.pkl` (joblib format). Each run produces a new file so no previous model is overwritten.

---

## Phase 2 — Multi-class Classifier

### Problem setup

Receives flows flagged as "attack" by Phase 1 (plus a small benign fallback path for flows Phase 1 misclassified). Classifies each flow into one of the following label categories:

| Label | Description |
|-------|-------------|
| `benign` | Fallback — benign flows Phase 1 incorrectly flagged as attack |
| `bruteforce` | Brute-force attacks |
| `ddos` | DDoS attacks |
| `dos` | DoS attacks |
| `malware` | Malware traffic |
| `mitm` | Man-in-the-middle attacks |
| `recon` | Reconnaissance traffic |
| `spoofing` | Spoofing attacks |
| `web` | Web-based attacks |

The model is trained on all 8 attack classes without relabelling. Low-confidence predictions are forwarded to Phase 3 for unsupervised analysis.

### Training setup

- **Algorithm**: LightGBM (`LGBMClassifier`, `objective='multiclass'`)
- **Feature set**: re-computed independently from a fresh balanced query (see Sampling below). The same cleaning pipeline as Phase 1 is applied to `df2` — correlation and variance filters are recomputed on the balanced distribution rather than on Phase 1's binary sample, which could yield slightly different dropped features.
- **Sampling**: **fresh `load_dataset_from_db` call** with `samples_per_class=PHASE2_SAMPLES_PER_CLASS` (50 000), no `binary_sampling`. Each class gets up to 50 000 rows drawn directly from the DB. Classes with fewer rows (e.g., `bruteforce` with ~16 k in the DB) return all they have. This replaces the previous approach of subsampling Phase 1's `df` (which was binary-sampled and therefore had a biased benign-vs-attack distribution).
- **Why a fresh query**: reusing `df` meant Phase 2 saw a distribution skewed by Phase 1's `BINARY_SAMPLING=(604k, 604k)` — benign was overrepresented relative to individual attack classes. A fresh per-class query gives each attack type equal sampling priority from the start.
- **Class weights**: `balanced` — automatically compensates for `bruteforce` having fewer available rows than the 50 k-capped classes.
- **Split**: 80% train / 20% test, stratified
- **Optimization**: Optuna, 20 trials, 1 800 s timeout, 3-fold `StratifiedKFold`, **objective: maximize macro F1**

Macro F1 is used (rather than F2 as in Phase 1) because at this stage all classes should be treated symmetrically — there is no single "most important" class to bias towards.

### Confidence routing to Phase 3

After prediction, `model.predict_proba()` returns a probability vector over all classes. If `max(proba) < PHASE2_CONFIDENCE_THRESHOLD` (default `0.6`), the flow is forwarded to Phase 3 rather than committed to a label. This handles truly novel attacks that don't match any trained pattern well enough to assign confidently.

A **feature importance bar chart** (top 20 features by LightGBM `gain`) is displayed after the evaluation cell, using `model_p2.feature_importances_`. Phase 3 (UMAP + HDBSCAN) does not have a feature importance chart because it is unsupervised and there is no direct notion of feature contribution to cluster membership.

Model saved at `models/multiclass_classifier_<YYYYMMDD_HHMMSS>.pkl` (joblib format). Each run produces a new file so no previous model is overwritten.

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

Models are saved at `models/umap_reducer_<YYYYMMDD_HHMMSS>.pkl` and `models/hdbscan_clusterer_<YYYYMMDD_HHMMSS>.pkl`. Each run produces new files so no previous models are overwritten.

---

## Real-Time IDS Script (VIM 4)

`scripts/network_binary_ids.py` is the edge-deployment component for Phase 1.

**How it works:**

1. Launches `tcpdump` in the background on a configurable network interface (`INTERFACE`, default `eth0`), rotating capture files every `CHUNK_SIZE_MB` MB (default 1 MB).
2. Picks up completed PCAP chunks (all but the file currently being written).
3. Calls `netflower` on each chunk to produce a flow-level CSV.
4. Aligns the CSV columns to the model's expected feature set (fills missing columns with 0; reads `model.feature_names_in_` when available, falls back to `FINAL_FEATURES` from constants).
5. Runs `model.predict_proba()` on the flows.
6. Logs an `[ALERT]` for any flow where the attack-class probability exceeds `THRESHOLD` (auto-updated by `training.ipynb` after each Optuna run via regex substitution; no longer the old default of 0.5).
7. Deletes the PCAP and CSV after processing to avoid disk accumulation.
8. A background stats thread logs packet count, total flows processed, and alert count every 3 seconds.
9. At startup, creates a timestamped Markdown report in `docs/results/ids_run_<YYYYMMDD_HHMMSS>.md` with configuration, model info, and an alert table. Each detected alert is appended to the table immediately (detection time, confidence, and key flow identifiers). At shutdown (Ctrl+C), a runtime summary is appended (end time, duration, total flows, total alerts).

The script reads `constants/features.py` and `constants/labels.py` at startup to determine input features and benign class labels.

---

## Repository Structure

```
.
├── constants/
│   ├── features.py        # FINAL_FEATURES (68 entries) and EXCLUDED_FEATURES — auto-updated by training.ipynb
│   └── labels.py          # BENIGN_LABELS, MALICIOUS_LABELS
├── data/                  # local only — not in Git
│   ├── raw/               # downloaded PCAPs and generated flow CSVs
│   └── sqlite/data.db     # unified SQLite database (~190 GB)
├── docs/
│   ├── features_report.txt  # last feature cleaning summary from training
│   ├── labels_list.txt      # human-readable label taxonomy
│   ├── project_overview.md  # this file
│   └── results/
│       ├── training_<YYYYMMDD_HHMMSS>.md  # per-run results (auto-generated by training.ipynb)
│       └── images/
│           ├── <ts>_p1_feature_importance.png   # Phase 1 top-20 feature importance bar chart
│           ├── <ts>_p2_feature_importance.png   # Phase 2 top-20 feature importance bar chart
│           └── <ts>_p3_umap_clusters.png        # Phase 3 UMAP + HDBSCAN cluster scatter plot
├── models/
│   ├── binary_classifier_<ts>.pkl       # Phase 1 LightGBM model (joblib) — one file per training run
│   ├── multiclass_classifier_<ts>.pkl  # Phase 2 LightGBM model (joblib) — one file per training run
│   ├── umap_reducer_<ts>.pkl           # Phase 3 UMAP reducer (joblib) — one file per training run
│   └── hdbscan_clusterer_<ts>.pkl      # Phase 3 HDBSCAN clusterer (joblib) — one file per training run
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
