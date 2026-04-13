# A Hierarchical MEC and IoT Solution for Cyber-Attack Detection in 6G Networks

Research code and experiments on **cyber-attack detection** in **IoT** environments where **Multi-access Edge Computing (MEC)** is used alongside constrained devices. The setting is motivated by **6G-oriented** network evolution: massive IoT, tight latency and energy goals, and growing use of **AI** for management and security—which also widens the threat surface.

IoT deployments are heterogeneous and resource-limited, while many high-accuracy detectors assume ample compute. **MEC** moves processing closer to the data source than a central cloud, which supports stronger analytics next to the edge while still calling for lightweight logic where devices are weakest. **Hierarchical** designs—lighter processing on devices and heavier analysis on an edge host—are a natural way to balance accuracy, latency, and feasibility.

This repository holds the **data pipeline**, **exploratory analysis**, and **modeling notebooks** used in that line of work (public CIC IoT/IIoT-style datasets, SQLite storage, flow features from PCAPs, and gradient-boosting experiments with interpretability and exploratory clustering tools).

---

## Cloning and submodules

Vendored tools and third-party trees live in **Git submodules** (declared in **`.gitmodules`**). A default clone only downloads the **parent** repository; submodule directories stay **empty** until you initialize them, so scripts and notebooks that expect those paths will fail on a fresh checkout.

**Recommended (all submodules, present and future)**

```bash
git clone --recurse-submodules <repository-url>
cd IC-temp
```

**Repository already cloned without submodules**

```bash
cd IC-temp
git submodule update --init --recursive
```

As more submodules are added to this project, the same commands keep pulling everything: `--recurse-submodules` on clone, or `update --init --recursive` afterward. Check **`.gitmodules`** for the authoritative list of paths and remotes.

### `tools/cicflowmeter/`

Hosts **[CICFlowMeter](https://github.com/hieulw/cicflowmeter)** (also on [PyPI](https://pypi.org/project/cicflowmeter/)). Pinning it as a submodule fixes the **flow-extraction** implementation everyone uses, enables **editable installs** from source, and avoids silent drift from the latest PyPI release.

If `tools/cicflowmeter/` is still empty after `git submodule update`, the parent repo may not yet record this path in **`.gitmodules`**—clone [hieulw/cicflowmeter](https://github.com/hieulw/cicflowmeter) into `tools/cicflowmeter/` manually until the submodule is published.

**CLI on your `PATH`:** from `tools/cicflowmeter/`, follow the upstream README (e.g. `pip install -e .`), or install `cicflowmeter` from PyPI if you accept version drift. `data_preprocessing.ipynb` invokes the **`cicflowmeter`** executable.

---

## Files and directories

### Root

- **`README.md`** — Project overview, file map, setup, and bibliography.
- **`requirements.txt`** — Pinned Python packages for the Jupyter workflow (e.g., pandas, NumPy, matplotlib, seaborn, ipykernel). Does **not** list everything `training.ipynb` imports; install extras such as `lightgbm`, `xgboost`, `optuna`, `shap`, `umap-learn`, `hdbscan`, and `scikit-learn` when you run that notebook.
- **`links.txt`** — Curated links: shared storage (e.g., Google Drive), conference pages, and **official dataset download URLs** (CIC APT IIoT 2024, CIC IoT-DIAD 2024, etc.). Use it to fetch raw data that is too large for Git.
- **`LICENSE`** — Terms under which this repository’s materials may be used or redistributed.
- **`.gitignore`** — Keeps `venv/`, local **`data/`**, SQLite **`*.db`**, and **`*.log`** out of commits so binaries, secrets, and huge artifacts never enter history.
- **`.gitmodules`** — When present, records each **Git submodule** (path + upstream URL). New vendored dependencies should be added here so `git clone --recurse-submodules` stays sufficient as the repository grows.

### `notebooks/`

- **`data_preprocessing.ipynb`** — **PCAP → flow features.** Runs **[CICFlowMeter](https://pypi.org/project/cicflowmeter/)** on folders of capture files and produces merged CSVs (flow-level columns used in many CIC IDS datasets). You set which PCAP directories to process and where CSVs are written; this is the bridge between raw network captures and tabular ML inputs.
- **`database_creation.ipynb`** — **CSV → SQLite.** Walks `data/raw/` (and nested folders), infers column types from a sample, creates one table per dataset, and loads data in chunks so large files fit in memory. Produces a single DB file (default `data/sqlite/data.db`) shared by analysis and training notebooks.
- **`dataset_analysis.ipynb`** — **Exploratory data analysis (EDA).** Reads tables from the SQLite database (e.g., CIC APT IIoT 2024, CIC IoT-DIAD 2024, CIC IoT 2023, CIC IIoT 2025, CIC BCCC NRC IoMT 2024). Covers data quality, missing values, distributions, class balance, correlations, and plots; results are saved under `results/`.
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

### `tools/`

- **`tools/cicflowmeter/`** — CICFlowMeter source (see **[Cloning and submodules](#cloning-and-submodules)**). Additional tooling may appear under `tools/` over time; treat **`.gitmodules`** as the checklist when cloning.

---

## Quick start

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Follow **[Cloning and submodules](#cloning-and-submodules)** so `tools/` (including CICFlowMeter) is populated; install the **`cicflowmeter`** CLI or use `pip install cicflowmeter`. Install any extra libraries for `training.ipynb` as needed.

3. Download the chosen CIC (or other) datasets, arrange them under `data/raw/` as in the notebooks, then run `database_creation.ipynb` → `dataset_analysis.ipynb` → `training.ipynb` in order as appropriate.