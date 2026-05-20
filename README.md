# Corruption and Growth: Replication code and data

*Replication materials for the working paper "Does the presence of corruption inhibit a nation's growth prospects? An investigatory comparative economic literature between post colonization Africa vs Asia" by Sandeep Rai.*

*Working paper position: late 2023. All data, literature, and reform events analysed in this repository are dated late 2023 or earlier.*

---

## Overview

This repository contains the data sources, cleaning code, regression code, and output for the working paper. The full pipeline is implemented in Python and reproduces the analysis from raw data through to the regression tables that feed the manuscript.

The paper itself lives outside this repository as a PDF. This repository contains everything needed to reproduce the empirics.

---

## Repository structure

```
.
├── README.md                  This file
├── .gitignore                 Files excluded from version control
├── requirements.txt           Python package dependencies
│
├── data/
│   ├── README.md              Data source documentation with URLs and access dates
│   ├── raw/                   Raw data files as downloaded (some files gitignored if large)
│   └── processed/             Cleaned data ready for analysis
│
├── code/
│   └── python/
│       ├── README.md          Python scripts overview
│       ├── data_collection.py Pull WGI, CPI, WDI, PWT 10.01, FRED, IMF DataMapper
│       ├── data_cleaning.py   Merge sources, handle missing data, build the panel
│       └── analysis.py        Panel FE, DiD event studies, growth accounting
│
├── output/
│   └── tables/                Regression results (JSON) and descriptive stats
│
└── paper/
    └── README.md              Pointer to the manuscript PDF (lives outside the repo)
```

The analysis is implemented entirely in Python (linearmodels, statsmodels, pandas).
The original plan included parallel Stata .do files; that line was dropped in favour
of a single-language pipeline for reproducibility and to remove the Stata licence
dependency.

---

## Software requirements

- Python 3.11 or later
- Git

Install Python packages:

```
pip install -r requirements.txt
```

---

## Replication workflow

1. Clone the repository.
2. Install Python packages.
3. Run `python code/python/data_collection.py` to pull raw data from public sources.
4. Run `python code/python/data_cleaning.py` to produce `data/processed/panel.csv` and `pwt.csv`.
5. Run `python code/python/analysis.py` to produce the panel FE regressions, the six DiD event studies, and the growth-accounting decomposition. Results write to `output/tables/` as JSON.

---

## Sample

15 countries by region:

- **Africa (8).** Nigeria, Senegal, Ghana, Zambia, Zimbabwe, Rwanda, Botswana, Mauritius.
- **Asia (5).** Singapore, India, South Korea, Indonesia, Malaysia.
- **Latin America controls (2).** Brazil, Chile.

Zimbabwe excluded from the sovereign-spread analysis (no continuous yield series due to hyperinflation 2007-09 plus sovereign default). Retained in growth accounting and policy case-study sections.

Time period: 1998 to late 2023.

---

## Reform events (DiD analysis)

Six anti-corruption reform events used as natural experiments:

1. Indonesia KPK 2003
2. Nigeria EFCC 2003
3. Brazil Lava Jato 2014
4. India Lokpal 2014
5. Rwanda post-1994 institutional rebuild
6. South Korea post-1987 democratization reforms

---

## Citation

If you use this code or data, please cite the working paper:

Rai, Sandeep. (2024). "Does the presence of corruption inhibit a nation's growth prospects? An investigatory comparative economic literature between post colonization Africa vs Asia." Working paper.

---

## Author

Sandeep Rai. Independent Researcher (Columbia University, alumnus).
