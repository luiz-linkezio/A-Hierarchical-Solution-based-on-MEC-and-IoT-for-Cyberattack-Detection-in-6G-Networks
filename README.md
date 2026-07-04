# A Hierarchical MEC and IoT Solution for Cyber-Attack Detection in 6G Networks

Research code and experiments on **cyber-attack detection** in **IoT** environments where **Multi-access Edge Computing (MEC)** is used alongside constrained devices. The setting is motivated by **6G-oriented** network evolution: massive IoT, tight latency and energy goals, and growing use of **AI** for management and security—which also widens the threat surface.

IoT deployments are heterogeneous and resource-limited, while many high-accuracy detectors assume ample compute. **MEC** moves processing closer to the data source than a central cloud, which supports stronger analytics next to the edge while still calling for lightweight logic where devices are weakest. **Hierarchical** designs—lighter processing on devices and heavier analysis on an edge host—are a natural way to balance accuracy, latency, and feasibility.

This repository holds the **data pipeline**, **exploratory analysis**, and **modeling notebooks** used in that line of work (public CIC IoT/IIoT-style datasets, SQLite storage, flow features from PCAPs via **[netflower](https://pypi.org/project/netflower/)**, and gradient-boosting experiments with interpretability and exploratory clustering tools).

See **[`docs/project_overview.md`](docs/project_overview.md)** for a full description of the architecture, design decisions, and current status.

---

## Architecture

The IDS is divided into three hierarchical phases:

| Phase | Location | Task |
|-------|----------|------|
| 1 — Binary classifier | VIM (edge node) | Benign vs. attack — minimizes false negatives |
| 2 — Multi-classifier | Edge / MEC host | Attack type (DDoS, DoS, malware, brute-force, …) |
| 3 — Clustering | Edge / MEC host | Unknown / zero-day threats not covered by Phase 2 |

Phases 1 and 2 are implemented and **validated live on the VIM 4 edge node**
(Khadas VIM4, Amlogic A311D2) against eight scripted attack categories — see
**[`docs/experimentos/2026-06-19-vim4-revalidacao.md`](docs/experimentos/2026-06-19-vim4-revalidacao.md)**.
Phase 3 (clustering / zero-day) is future work.

---

---

## Files and directories

### Root

- **`README.md`** — Project overview, file map, setup, and bibliography.
- **`requirements.txt`** — Pinned Python packages for the Jupyter workflow (e.g., pandas, NumPy, matplotlib, seaborn, ipykernel). Does **not** list everything `training.ipynb` imports; install extras such as `lightgbm`, `xgboost`, `optuna`, `shap`, `umap-learn`, `hdbscan`, and `scikit-learn` when you run that notebook.
- **`links.txt`** — Curated links: shared storage (e.g., Google Drive), conference pages, and **official dataset download URLs** (CIC IoT Dataset 2023 and CIC IIoT 2025). Use it to fetch raw data that is too large for Git.
- **`LICENSE`** — Terms under which this repository’s materials may be used or redistributed.
- **`.gitignore`** — Keeps `venv/`, local **`data/`**, SQLite **`*.db`**, and **`*.log`** out of commits so binaries, secrets, and huge artifacts never enter history.
- **`.gitmodules`** — When present, records each **Git submodule** (path + upstream URL). New vendored dependencies should be added here so `git clone --recurse-submodules` stays sufficient as the repository grows.

### `notebooks/`

See **[`notebooks/README.md`](notebooks/README.md)** for step-by-step usage of the pipeline notebooks.

- **`data_preprocessing.ipynb`** — **PCAP → flow features.** Runs **[netflower](https://pypi.org/project/netflower/)** on folders of capture files and produces merged CSVs (flow-level columns). You set which PCAP directories to process and where CSVs are written; this is the bridge between raw network captures and tabular ML inputs.
- **`database_creation.ipynb`** — **CSV → SQLite.** Walks `data/raw/` (and nested folders), infers column types from a sample, creates one table per dataset, and loads data in chunks so large files fit in memory. Produces a single DB file (default `data/sqlite/data.db`) shared by analysis and training notebooks.
- **`dataset_analysis.ipynb`** — **Exploratory data analysis (EDA).** Reads tables from the SQLite database (CIC IoT Dataset 2023 and CIC IIoT 2025). Covers data quality, missing values, distributions, class balance, correlations, and plots; results are saved under `results/`.
- **`training.ipynb`** — **Supervised and exploratory modeling.** Loads labeled data from SQLite, trains **LightGBM** / **XGBoost**, uses **Optuna** for search, **SHAP** for explanations, and **UMAP** / **HDBSCAN** for structure checks. This is where detection performance and model behavior are studied on the engineered feature tables.

### `notebooks/old/`

- Snapshots of earlier workflows (**`data_preprocessing.ipynb`**, **`model_training.ipynb`**) kept for comparison or rollback. Prefer the notebooks in `notebooks/` unless you need a historical variant.

### `results/`

- **`results/images/`** — Figures exported from EDA (per-dataset filenames, e.g. `CIC_*_class_distribution_*.png`, correlation heatmaps, boxplots, missing-value summaries). These document what each table looks like before modeling.
- **`results/dataset_analysis/`** — Markdown **reports** (`*_analysis_report.md`) that summarize the same analyses in prose-friendly form, one file per major dataset.

### `data/` (local only, not in Git)

Expected layout is driven by the notebooks (see `links.txt` and path constants inside each notebook):

- **`data/raw/`** — Downloaded CSVs, PCAPs, and generated flow CSVs from CICFlowMeter.
- **`data/sqlite/`** — `data.db` (or similar) produced by `database_creation.ipynb`.

Because **`.gitignore`** excludes `data/`, each clone must populate this tree locally after cloning.

### `scripts/`

Real-time IDS and the live-validation toolchain (run on the VIM 4 edge node and on the attacker PC):

- **`scripts/run_experiment.sh`** — **One-command live validation.** Runs on the PC and orchestrates the whole experiment over SSH: deploys scripts/models to the VIM 4, brings up an HTTP service, runs Session A (binary IDS) and Session B (binary+multiclass IDS) under an identical attack script with idle baselines and inter-attack gaps, tears everything down, and computes the metrics. No secrets in the file (sudo password read from `$VIM4_PASS`).
- **`scripts/network_binary_ids.py`** — Real-time **Phase 1** IDS for VIM 4. Captures live flows via `netflower`'s `capture_live` (emitting each flow on TCP FIN/RST or idle timeout) and runs the binary classifier to flag attack traffic. Logs per-flow alerts and periodic system snapshots (CPU/RAM/net/power/temp/DVFS).
- **`scripts/network_ids.py`** — Real-time **Phase 1+2** IDS: same capture path, plus the multiclass classifier to label the attack type for flagged flows.
- **`scripts/attack_generator.py`** — Generates the eight attack categories (recon, dos, ddos, brute-force, web, mitm, spoofing, malware) against the target, with configurable per-attack duration and idle `--gap`, and writes a JSON report with per-attack time windows (the ground truth for scoring).
- **`scripts/ids_metrics.py`** — Computes detection metrics (binary per-second confusion matrix; multiclass per-class TP/FP/FN/F1), resource usage (CPU/RAM/throughput), and a **calibrated energy estimate with an uncertainty band**, all from the IDS log + attack-generator report.
- **`scripts/calibrate_power.py`** — Calibrates the energy model on the VIM 4 (idle vs. `stress` benchmark + literature-anchored power envelope), writing `constants/power_model_vim4.json`. The board exposes no power sensor, so energy is an estimate, not a direct measurement.
- **`scripts/benign_trafic_simulator.sh`**, **`scripts/trafic_capturer.sh`**, **`scripts/evaluate_ids.py`** — earlier helpers for benign-traffic generation, capture, and CSV-based evaluation.

### `constants/`

- **`constants/features.py`**, **`constants/labels.py`** — final feature list and label taxonomy shared by training and the live IDS.
- **`constants/power_telemetry.py`** — shared telemetry helpers (temperature, per-cluster CPU frequency, calibrated power model) used by the IDS scripts, the calibrator, and the analyzer.
- **`constants/power_model_vim4.json`** — calibrated energy-model parameters (generated by `calibrate_power.py`).

### `tests/`

- Lightweight standalone tests (`python3 tests/test_*.py`, no pytest needed) for the power model, energy band, calibration, and attack-generator command builders.

---

## Quick start

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install netflower      # PCAP-to-flow conversion tool
   ```

   Install extra libraries for `training.ipynb` as needed (`lightgbm`, `optuna`, `shap`, `umap-learn`, `hdbscan`).

2. Download the chosen CIC datasets (links in `links.txt`), arrange them under `data/raw/` with one subfolder per traffic class (the folder name becomes the label).

3. Run the notebooks in order: `data_preprocessing.ipynb` → `database_creation.ipynb` → `dataset_analysis.ipynb` → `training.ipynb`.

---

## Live validation on the VIM 4

The trained models are validated live on the edge node by replaying eight attack
categories from the attacker PC and scoring the IDS output. The whole run is
reproducible from the PC with a single command:

```bash
export VIM4_PASS=<vim4 sudo password>     # never committed; read from the env
./scripts/run_experiment.sh --skip-calibration
```

It runs two sequential sessions (binary, then binary+multiclass) under the same
attack script, with clean benign baselines and 120 s idle gaps between attacks,
then writes `results/session_{a,b}_metrics_<ts>.json`. Drop `--skip-calibration`
to (re)calibrate the energy model first. Login to the VIM 4 uses an SSH key; the
sudo password is only read from `$VIM4_PASS` and never stored in the repo.

Full methodology, artifact descriptions, results, and the issues found during
execution are documented in
**[`docs/experimentos/2026-06-19-vim4-revalidacao.md`](docs/experimentos/2026-06-19-vim4-revalidacao.md)**.

Headline results (run `20260619_230219`): binary IDS with **0 % false positives**
on a clean benign baseline; multiclass classifies *recon* at **F1 = 0.976** while
the remaining categories largely collapse onto *dos* in the 55 per-flow features
(a feature-space limitation); Phase 2 adds only **+50 MB RAM** over the binary
pipeline, with no CPU or energy overhead.