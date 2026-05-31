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
`training.ipynb` is organised into sections: **Imports**, **Configuration** (a single section combining data-source inputs — `DB_PATH`, `TABLE`, sampling params — and algorithm constants such as thresholds and fixed LightGBM params), followed by the three training phases. Keeping inputs and constants in one place makes it faster to adjust a run without scrolling between sections.

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
- **Sampling**: `BINARY_SAMPLING = (615 317, 615 317)` — 615 317 benign rows + 615 317 attack rows (distributed evenly across the 8 attack classes from the SQLite database via `ORDER BY RANDOM() LIMIT n`). The cap is set to `SAMPLES_PER_CLASS` (also 615 317), meaning the notebook pulls as many rows as it can up to that limit per class.
- **Split**: 80% train / 20% test, stratified
- **Class weights**: none (balanced by sampling)

### Hyperparameter optimization (Optuna)

20 trials with a 1 800 s timeout using 3-fold `StratifiedKFold` cross-validation. **The decision threshold is tuned jointly with the model hyperparameters**, which is a deliberate design choice.

**Objective function: maximize F2-score (beta=2) on the attack class.**

The rationale: this is a detection system, not a prevention system (IDS, not IPS). A false negative (missed attack) is more costly than a false positive (benign traffic flagged as attack). The F2-score weights recall 4× more than precision, aggressively prioritising attack detection. Tuning the threshold as part of Optuna means the model can accept lower precision in exchange for catching real attacks.

### Best result (training run 2026-05-18 13:00:14)

| Metric | Attack class | Benign class |
|--------|-------------|-------------|
| Precision | 0.73 | 0.95 |
| Recall | 0.94 | 0.76 |
| F1 | 0.82 | 0.85 |
| Accuracy (overall) | — | **0.84** |

| Class | Recall |
|-------|--------|
| Attack | 0.9386 |
| Benign | 0.7647 |

Best F2-score (Optuna): `0.8840`. Optimized threshold: `0.19976531434163686` (flows with attack probability above this are flagged).

The lower attack precision (0.73) is intentional: the F2 objective aggressively favours recall, accepting more false positives in exchange for catching 94% of real attacks. In practice this means roughly 1 in 4 flows classified as attack will be benign — expected and acceptable for an IDS (vs. IPS) deployment.

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
- **Sampling**: **fresh `load_dataset_from_db` call** with `samples_per_class=PHASE2_SAMPLES_PER_CLASS` (615 317), no `binary_sampling`. Each class gets up to 615 317 rows drawn directly from the DB. Classes with fewer rows (e.g., `bruteforce` with ~16 k in the DB) return all they have. This replaces the previous approach of subsampling Phase 1's `df` (which was binary-sampled and therefore had a biased benign-vs-attack distribution).
- **Why a fresh query**: reusing `df` meant Phase 2 saw a distribution skewed by Phase 1's `BINARY_SAMPLING=(604k, 604k)` — benign was overrepresented relative to individual attack classes. A fresh per-class query gives each attack type equal sampling priority from the start.
- **Class weights**: `balanced` — automatically compensates for `bruteforce` having fewer available rows than the 50 k-capped classes.
- **Split**: 80% train / 20% test, stratified
- **Optimization**: Optuna, 20 trials, 1 800 s timeout, 3-fold `StratifiedKFold`, **objective: maximize macro F1**

Macro F1 is used (rather than F2 as in Phase 1) because at this stage all classes should be treated symmetrically — there is no single "most important" class to bias towards.

### Confidence routing to Phase 3

After prediction, `model.predict_proba()` returns a probability vector over all classes. If `max(proba) < PHASE2_CONFIDENCE_THRESHOLD` (default `0.4`), the flow is forwarded to Phase 3 rather than committed to a label. This handles truly novel attacks that don't match any trained pattern well enough to assign confidently. The threshold was lowered from 0.6 to 0.4 to reduce the Phase 3 input volume and route only genuinely ambiguous flows — with 0.6, roughly 30% of flows were forwarded, which is too many for the clustering stage to be meaningful.

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

## Real-Time IDS Scripts

Two scripts handle live traffic classification. They share the same capture infrastructure (`netflower.capture_live`) but differ in which phases are executed.

### `scripts/network_binary_ids.py` — Phase 1 only (lightweight edge deployment)

This is the minimal deployment intended for resource-constrained edge nodes (VIM 4). It runs only the binary classifier and does not load the Phase 2 model, keeping memory footprint and startup time low.

**How it works:**

1. At startup, loads the Phase 1 binary classifier (`MODEL_PATH`). The feature list is read from `model.feature_names_in_` when available, falling back to `FINAL_FEATURES` from `constants/features.py`.
2. Calls `netflower.capture_live()` on the network interface (`INTERFACE`, default `eth0`), registering an `on_flow` callback. Each flow is emitted by netflower the moment it completes — either on TCP FIN/RST or after `IDLE_TIMEOUT` seconds of inactivity (default 30 s), up to a maximum of `FLOW_TIMEOUT` seconds (default 120 s).
3. **Phase 1** — For each completed flow, aligns the flow dict to the model's expected feature set (fills missing keys with 0) and runs `model.predict_proba()`. Flows below `THRESHOLD` are discarded as benign.
4. Logs an `[ALERT]` for every flagged flow with Phase 1 confidence and inference latency. `VERBOSE_ALERTS=1` prints all flow features.
5. A background stats thread logs every 3 seconds: total flows, alerts, avg/max inference latency.
6. Creates a timestamped log in `docs/results/binary_ids_run_<YYYYMMDD_HHMMSS>.log` at startup; appends a runtime summary at shutdown.

**Why a Phase-1-only variant exists:** The two-phase script (`network_ids.py`) loads two models and runs two inference passes per flagged flow. For edge nodes where memory or latency is constrained, this is unnecessary when the only required output is a binary benign/attack decision. `network_binary_ids.py` is also easier to validate in isolation before deploying the full pipeline.

The script reads `constants/features.py` and `constants/labels.py` at startup. `training.ipynb` auto-updates `MODEL_PATH` and `THRESHOLD` via regex after each Phase 1 training run.

---

### `scripts/network_ids.py` — Phase 1 + Phase 2 (full hierarchical deployment)

This script runs both phases in sequence for every flagged flow.

**How it works:**

1. At startup, loads both the Phase 1 binary classifier (`MODEL_PATH`) and the Phase 2 multi-class classifier (`P2_MODEL_PATH`).
2. Same `netflower.capture_live()` setup as the binary script.
3. **Phase 1** — Binary gate: benign vs. attack. Flows below `THRESHOLD` are discarded.
4. **Phase 2** — Flows that pass Phase 1 are classified into a specific attack type (ddos, dos, malware, bruteforce, mitm, web, recon, spoofing, or benign as fallback). If `max(proba) < PHASE2_CONFIDENCE_THRESHOLD` (default `0.4`), the flow is tagged `LOW_CONF→P3` — a routing marker for Phase 3 once implemented.
5. Logs `[ALERT]` with Phase 1 confidence, Phase 2 label and confidence, and per-phase latency.
6. Background stats thread logs per-phase avg/max inference and low-confidence count every 3 seconds.
7. Creates a timestamped log in `docs/results/ids_run_<YYYYMMDD_HHMMSS>.log`; appends a Phase 2 attack-type breakdown at shutdown.

**Note on auto-update by `training.ipynb`:** The notebook currently updates `MODEL_PATH` and `THRESHOLD` via regex after Phase 1 training. The same substitution should be extended to rewrite `P2_MODEL_PATH` after Phase 2 training so the script always points to the latest model without a manual step.

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
│   ├── artigo-TCC.docx      # TCC article (ABNT format) — pre-filled from project_overview.md
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
│   ├── network_binary_ids.py     # live Phase-1-only IDS for VIM 4 (binary: benign vs attack)
│   ├── network_ids.py            # live Phase-1 + Phase-2 IDS (binary gate + attack-type classification)
│   ├── attack_orchestrator.py    # orchestrates attacks + quantifies flows for IDS validation
│   ├── evaluate_ids.py           # cross-correlates orchestrator report with IDS alert log
│   ├── fill_artigo.py            # one-off script that populated docs/artigo-TCC.docx
│   ├── benign_trafic_simulator.sh  # captures real personal traffic as benign pcap
│   └── trafic_capturer.sh          # generic tcpdump capture helper
└── requirements.txt
```

---

## Real-World Deployment Observations

`scripts/network_binary_ids.py` was deployed live on the VIM 4 (`eth0`, IP `192.168.100.5`) on 2026-05-18. The session revealed several patterns worth documenting.

### Distribution shift on benign traffic

All real flows in the session were flagged as attacks, including SSH handshakes and a plain HTTP request to an external server. This is a known consequence of how the training datasets were captured: the "benign" class in the CIC datasets consists of scripted background traffic with regular inter-packet timing, which differs from actual interactive traffic in two key ways:

- **`flow_iat_min`** (second-most important feature): real TCP bursts produce inter-arrival times in the 1–10 µs range; training benign flows are in the ms range. Any burst on the real network is therefore anomalous to the model.
- **`flow_byts_s`** (most important feature): short flows (< 1 s) over a fast LAN produce apparent throughput far above what the training distribution saw for benign traffic.

Short-lived TCP flows — SSH handshakes, HTTP requests — are the most affected. Long, sustained downloads (30+ s, stable throughput) are expected to score below the threshold because their temporal features resemble the training distribution more closely.

### Single-packet FIN/ACK artifact

Every TCP connection close produced a second "flow" with `flow_duration = 0`, `tot_fwd_pkts = 1`, `totlen_fwd_pkts = 52` bytes, only FIN + ACK flags, and consistently 84% attack confidence. This is a netflower artifact: when the final FIN/ACK arrives after the main flow is already emitted, netflower creates a second micro-flow for it. The model has never seen this pattern as benign (it does not exist in the training captures), so it always scores it as an attack. This is a false positive by design and should be filtered out in post-processing or suppressed via a minimum packet-count guard in the IDS script.

### Nmap recon attempt

A port scan with `nmap -sS 192.168.100.5` was initiated from `192.168.100.232` to verify that the IDS correctly detects reconnaissance traffic. Nmap SYN scans produce flows with characteristics that strongly match the `recon` class in the training data: high `flow_pkts_s`, very short `flow_duration`, near-zero `bwd_pkts_s` (most probes receive no response or a RST), and `syn_flag_cnt > 0` with no matching ACK completion. The full validation test (see below) confirmed that recon-type flows are detected reliably at the 90% threshold.

### Attack orchestrator validation (2026-05-18)

A full-scale live validation was run on VIM 4 by pairing `scripts/network_binary_ids.py` (IDS) with `scripts/attack_orchestrator.py` (traffic generator). The orchestrator fired all eight attack categories against `192.168.100.5` while the IDS monitored `eth0` in real time.

| Metric | Value |
|--------|-------|
| Total flows seen | 17,357 |
| Alerts raised | 12,216 |
| Overall detection rate | **~70%** (±1%) |
| Decision threshold | 90% (`THRESHOLD = 0.9`) |
| Traffic composition | 100% attack (no benign traffic during the test window) |

**Key finding — spoofing is the primary miss.** The ~30% of flows that were not flagged are concentrated almost entirely in the `spoofing` attack type (hping3 with a fixed spoofed source IP). Excluding spoofing, the detection rate across the remaining seven attack classes (recon, dos, ddos, bruteforce, web, mitm, malware) is close to 100%.

**Why spoofing is harder to detect at 90%.** Spoofed-source flows generated by `hping3 -a <fixed-IP>` differ from the training distribution for spoofing in one key way: a fixed spoofed source produces flows whose IP-level statistics (e.g., consistent backward-path silence) differ subtly from the randomized spoofing patterns in the CIC training captures. The model assigns these flows attack probabilities that cluster just below 0.9, so they are flagged at lower thresholds but missed at 0.9. This is a threshold calibration effect, not a feature blindness problem — the Phase 2 multi-classifier would still classify them correctly if Phase 1 had passed them through.

**Implication for threshold selection.** The 0.9 threshold was chosen to minimize false positives on genuinely benign traffic (where the distribution shift already causes high false-positive rates at lower thresholds). Lowering the threshold to, say, 0.5 would recover most spoofing misses but would also inflate false positives on real benign traffic significantly. The right tradeoff depends on the deployment scenario; 0.9 is conservative and favours precision over recall for the binary gate.

---

## Attack Orchestrator (`scripts/attack_orchestrator.py`)

`scripts/attack_orchestrator.py` is a Python script that runs multiple attack types against VIM 4 in sequence, captures each attack's traffic with `tcpdump`, and quantifies the generated flows using `tshark` + `capinfos`. It is designed to produce labeled, measurable traffic for IDS validation and dataset augmentation.

### Why a dedicated orchestrator?

Running attacks manually one at a time makes it difficult to correlate traffic to attack types after the fact — the timing boundaries between attacks are not recorded, and there is no structured output to annotate which pcap windows correspond to which label. The orchestrator solves this by:

1. Assigning each attack type its own timestamped `.pcap` file, so flow extraction and labeling can be done per attack with no ambiguity.
2. Automatically analyzing each pcap after the attack completes, producing concrete counts (TCP flows, UDP flows, ICMP flows, forward/backward packet split, total bytes) that tell you exactly how many flows each attack generated.
3. Outputting a timestamped `report_<ts>.json` + `report_<ts>.csv` under `/home/linkezio/Datasets/attack_testing/` that can be directly used to decide how much traffic to extract and how to balance a new dataset.

### Covered attack types

| Name | Label | Tools | Time-bounded |
|------|-------|-------|-------------|
| `recon` | Recon | nmap, masscan | No (runs to completion) |
| `dos` | DoS | hping3 | Yes (`--duration`) |
| `ddos` | DDoS | hping3 `--rand-source` | Yes |
| `bruteforce` | Brute Force | medusa (SSH, HTTP, Telnet) | Yes |
| `web` | Web Attacks | nikto, gobuster, curl flood | Yes |
| `mitm` | MITM | arpspoof | Yes |
| `spoofing` | Spoofing | hping3 `-a` (fixed spoofed src) | No (packet count limited) |
| `malware` | Malware (C2/Mirai) | nmap, nc (beacon simulation) | No |

### Fallback behavior

The script does not require wordlists to be installed. When `/usr/share/wordlists/rockyou.txt` or the dirbuster wordlists are absent, it writes a minimal 17-entry password list and 18-entry path list to a temporary file, uses them, and deletes them afterward. This means brute-force and web attacks always run, but with negligible coverage — useful for flow generation even without the full wordlists.

### Per-attack metrics (captured in report)

| Field | Source |
|-------|--------|
| `total_packets` | `capinfos -c` |
| `total_bytes` | `capinfos -s` |
| `capture_duration` | `capinfos -u` |
| `tcp_flows` | `tshark -z conv,tcp` (unique `<->` pairs) |
| `udp_flows` | `tshark -z conv,udp` |
| `icmp_flows` | `tshark -z conv,icmp` |
| `total_flows` | sum of above |
| `fwd_packets` | `tshark -Y "ip.dst == <target>"` frame count |
| `bwd_packets` | `total_packets - fwd_packets` |

### Usage

```bash
# All attacks, default 30s time-bound, default target 192.168.100.5
sudo python3 scripts/attack_orchestrator.py

# Only recon + dos + spoofing, 60s time-bound
sudo python3 scripts/attack_orchestrator.py --attacks recon,dos,spoofing --duration 60

# Different target / interface
sudo python3 scripts/attack_orchestrator.py --target 192.168.100.10 --iface ens3

# Dry run — print commands without executing
python3 scripts/attack_orchestrator.py --dry-run

# Custom wordlist (faster brute-force with real wordlist)
sudo python3 scripts/attack_orchestrator.py --wordlist /usr/share/wordlists/rockyou.txt
```

Output files land in `/home/linkezio/Datasets/attack_testing/`:
- `<attack>_<timestamp>.pcap` — raw traffic capture per attack type
- `report_<timestamp>.json` — structured metrics per attack (full)
- `report_<timestamp>.csv` — same data in flat CSV (ready to import into pandas)

---

## IDS Real-World Evaluation (2026-05-23)

### Setup

Attacks were sent from a PC (BRT, UTC-3) using `attack_orchestrator.py` against the VIM 4 (UTC) running `network_binary_ids.py`. The evaluation script `scripts/evaluate_ids.py` cross-correlates both reports by shifting PC timestamps by +3h and assigning each IDS alert to whichever attack window was active at that moment (plus a 30s idle-slack to catch flows emitted after the attack ended due to netflower's idle timeout).

### Results — 2026-05-23 (report `evaluation_20260523.json`)

| Attack | Duration | Alerts | Phase 2 correct | Phase 2 % |
|--------|----------|--------|-----------------|-----------|
| recon | 74 s | 3,075 | 950 | 30.9% ⚠️ |
| dos | 90 s | 4,938 | 4,938 | 100.0% ✅ |
| ddos | 60 s | 3,124 | 0 | 0.0% ❌ |
| bruteforce | 19 s | 533 | 0 | 0.0% ❌ |
| web | 0.65 s | 0 | — | FN ❌ |
| mitm | 0.53 s | 0 | — | FN ❌ |
| spoofing | 2.7 s | 0 | — | FN ❌ |
| malware | 7.0 s | 0 | — | FN ❌ |

**Phase 1 (binary):** 11,670 / 11,674 alerts fell within real attack windows — FP rate 0.03%. Excellent.

**Phase 2 (type):** 50.5% overall accuracy across detected flows (5,888 / 11,670).

### Root causes

**"DoS dominance" in Phase 2:** `ddos` (99.7% → classified as `dos`) and `bruteforce` (84.2% → `dos`) are systematically misclassified as `dos`. The `dos` class is over-represented in the training data (largest per-class sample count), so the Phase 2 classifier learns a decision boundary biased toward `dos` for any high-rate, high-packet-count flow — which is exactly what `ddos` and `bruteforce` look like in raw netflow features. The fix is either stronger class-weight balancing in the Phase 2 model or feature engineering to distinguish these classes (e.g., source diversity for DDoS, failed-auth counters for brute-force).

**Short attacks → FN:** `web` (0.65 s), `mitm` (0.53 s), `spoofing` (2.7 s), and `malware` (7 s) all produced zero alerts. netflower only emits a flow after `idle_timeout=30s` of inactivity or a TCP FIN/RST. Attacks shorter than ~10 s do not generate enough sustained traffic to cross that threshold before they end, and the resulting flows are emitted 30 s later — after the evaluation window has closed. This is a real-time detection gap for short-burst attacks; the evaluation script accounts for it with `--idle-slack` but the attacks were too brief even for that. The solution in production is to lower `idle_timeout` (at the cost of fewer features per flow) or to use a sliding-window approach for micro-flows.

**Timezone mismatch:** PC runs BRT (UTC-3), VIM 4 runs UTC. This is handled automatically by `evaluate_ids.py --tz-offset 3` but should be fixed at the OS level to avoid confusion in future logs.

### How to re-run the evaluation

```bash
python3 scripts/evaluate_ids.py \
    --orchestrator results/report_<timestamp>.csv \
    --ids          results/ids_run_<timestamp>.md \
    --tz-offset    3 \
    --idle-slack   30 \
    --output       results/evaluation_<timestamp>.json
```

---

## What Is Still Pending

| Phase | Status |
|-------|--------|
| Phase 1 — Binary classifier | Done. Model trained and deployed. Available in both `network_binary_ids.py` (Phase 1 only) and `network_ids.py` (Phase 1 + 2). |
| Phase 2 — Multi-classifier | Done. Model trained and saved. Integrated into `network_ids.py` — runs sequentially after Phase 1 for every flagged flow. Low-confidence flows are tagged `LOW_CONF→P3` and counted, ready for Phase 3 routing once implemented. |
| Phase 3 — Clustering (UMAP + HDBSCAN) | Done in `training.ipynb`. Models saved to `models/`. Real-time routing from Phase 2 low-confidence flows not yet implemented in `network_ids.py`. |
| `training.ipynb` P2 model auto-update | The notebook updates `MODEL_PATH` and `THRESHOLD` via regex after Phase 1 training. The same substitution should be extended to also rewrite `P2_MODEL_PATH` in `network_ids.py` after Phase 2 training so the script always points to the latest model without a manual step. |
