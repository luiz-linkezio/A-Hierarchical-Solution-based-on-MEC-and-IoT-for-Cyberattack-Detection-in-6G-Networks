# Notebooks

This directory contains the data pipeline and modeling notebooks for the project. Run them in the order listed below.

---

## Prerequisites

Create and activate a virtual environment from the repo root, then install the base dependencies:

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

The preprocessing notebook also requires **flowmeter**, vendored under `tools/flowmeter/`. Install it once as an editable package:

```bash
pip install -e tools/flowmeter/
```

---

## 1. `data_preprocessing.ipynb` — PCAP → flow CSVs

Walks a directory tree of PCAP/PCAPNG capture files, converts each capture to network-flow features using **flowmeter**, and writes one merged CSV per folder.

### How it works

| Step | What happens |
|------|-------------|
| `find_pcap_folders(root, exclude)` | Recursively finds every folder under `DATA_ROOT` that contains at least one `.pcap` / `.pcapng` file, skipping any folder whose **basename** appears in `EXCLUDE_FOLDERS`. |
| `generate_merged_csv_from_pcaps(folder, filename)` | Converts each capture in the folder to flows, appends a `label` column equal to the folder name, and streams all chunks into a single `merged_<folder_name>.csv` inside that same folder. |

### Configuration (Inputs cell)

```python
DATA_ROOT        = "../data"          # root searched for PCAP folders
EXCLUDE_FOLDERS  = ["CIC_IIoT_dataset_2025"]  # folder basenames to skip
```

Change `DATA_ROOT` to point at where your captures live. Add any folder name to `EXCLUDE_FOLDERS` to skip it entirely (useful while a dataset is still downloading or for datasets already converted).

### Output

For each PCAP folder a file is created at:

```
<folder_path>/merged_<folder_name>.csv
```

Each row is one network flow. All flows from the same folder share the same `label` value (the folder's basename).

### Expected data layout

```
data/
└── raw/
    ├── Aposemat_IoT_23/
    │   └── .../CTU-IoT-Malware-Capture-1-1/
    │       ├── 2018-05-09-192.168.100.103.pcap
    │       └── merged_CTU-IoT-Malware-Capture-1-1.csv  ← generated
    └── UNSW_Bot-IoT/
        └── ...
```

> **Tip:** The notebook skips folders that produce zero flows and raises an error for folders that contain no PCAP files at all, so you can safely re-run it after adding new captures.

---

## 2. `database_creation.ipynb` — flow CSVs → SQLite

Loads every `merged_*.csv` produced by the preprocessing step into a single SQLite database, one table per top-level dataset directory.

### How it works

The notebook walks `DATA_ROOT` at the **top level** (one subdirectory = one dataset = one table). For each dataset it:

1. Searches recursively for any file matching `merged_*.csv`.
2. Creates (or reuses) the SQLite database at `DB_PATH`.
3. Skips the table entirely if it already exists — safe to re-run.
4. Streams each CSV into the table in 50 000-row chunks.
5. Creates an index on the `label` column for fast filtering.

### Configuration (Inputs cell)

```python
DB_PATH            = "../data/sqlite/data.db"
DATA_ROOT          = "../data/raw"
EXCLUDED_DATASETS  = ["CIC_IIoT_dataset_2025"]   # top-level dirs to skip
```

- **`DB_PATH`** — path to the SQLite file (created automatically if it does not exist).
- **`DATA_ROOT`** — should match the `data/raw/` subtree populated by the preprocessing step.
- **`EXCLUDED_DATASETS`** — top-level directory names to ignore (same idea as `EXCLUDE_FOLDERS` above).

### Table naming

Each top-level directory name is sanitised for SQL: hyphens and spaces become underscores. For example, `Aposemat_IoT_23` → table `Aposemat_IoT_23`, `UNSW_Bot-IoT` → table `UNSW_Bot_IoT`.

### Output

A single SQLite file at `DB_PATH` (default `data/sqlite/data.db`) that is shared by the analysis and training notebooks downstream.

### Expected data layout before running

```
data/
└── raw/
    ├── Aposemat_IoT_23/
    │   └── .../merged_CTU-IoT-Malware-Capture-1-1.csv
    ├── UNSW_Bot-IoT/
    │   └── .../merged_<scenario>.csv
    └── UNSW_NB15/
        └── .../merged_<scenario>.csv
```

> **Tip:** Datasets whose top-level folder contains no `merged_*.csv` files are skipped with a warning; they will not cause the notebook to fail.

---

## Recommended run order

```
data_preprocessing.ipynb   →   database_creation.ipynb   →   dataset_analysis.ipynb   →   training.ipynb
```

The first two notebooks build the data assets; the last two consume the SQLite database.
