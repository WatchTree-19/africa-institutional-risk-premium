# Python scripts

*Python handles data collection, cleaning, and visualisation. Stata handles the regressions. Sequential workflow: Python first, then Stata.*

---

## Scripts

### `data_collection.py`

Pulls raw data from public sources to `data/raw/`. Sources documented in `data/README.md`. Each variable has its own function. Logs URL and access date for replication.

### `data_cleaning.py`

Cleans raw data, merges sources, handles missing data, splices Penn World Table (1950-2019) with World Bank WDI (2020-2023). Outputs cleaned files to `data/processed/` ready for Stata. Documents every transformation in the script header.

### `plots.py`

Generates visualisations for the manuscript and presentation. Uses matplotlib and seaborn. Exports PNG and PDF to `output/figures/`.

---

## Running

```
pip install -r requirements.txt
python code/python/data_collection.py
python code/python/data_cleaning.py
```

Then move to Stata for the regressions. Run `plots.py` last, after regression outputs are available.

---

## Conventions

- One function per data source.
- Functions log their access date to a sidecar file.
- Cleaning decisions documented in the script header.
- No hard-coded paths; use relative paths from repo root.
- Random seeds set where relevant.
