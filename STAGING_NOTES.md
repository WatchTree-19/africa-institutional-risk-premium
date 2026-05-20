# Staging notes — for the next GitHub push

*Generated at the end of the session. Sandeep to commit and push manually from his machine when ready.*

The sandbox could not commit/push because of git index permissions. All file changes are on disk; only the git operations need to happen locally.

## What changed this session

### New Python code (3 files)

- `code/python/data_collection.py` — pulls WGI, CPI (OWID mirror), WDI macros, PWT 10.01, FRED US 10Y + select country yields, IMF DataMapper rltir.
- `code/python/data_cleaning.py` — assembles the 15-country balanced panel.
- `code/python/analysis.py` — runs panel FE regressions, six DiD event studies, growth accounting decomposition, TFP-on-corruption regression.

### New dataset (paper contribution)

- `data/raw/follow_through_dataset.csv` — 22 anti-corruption reform events with four sub-scores (speed, depth, survival, coalition) and composite index.
- `data/raw/follow_through_codebook.md` — coding rules and source-tier hierarchy.

### Processed data (regeneratable from code but worth tracking)

- `data/processed/panel.csv` — 15-country balanced panel 1998-2023, all variables merged.
- `data/processed/panel_expanded.csv` — extended panel with the 12 additional countries needed for the follow-through analysis.
- `data/processed/pwt.csv` — PWT 10.01 extract for the 15-country sample.
- `data/processed/follow_through_dataset.csv` — coded events with composite scores.
- `data/processed/follow_through_analysis.csv` — coded events with composite scores and computed spread responses.

### Output tables (regression results)

- `output/tables/panel_fe.json` — five panel FE specifications.
- `output/tables/did_events.json` — six DiD event-study results.
- `output/tables/growth_accounting.json` — levels and growth-rate decompositions, TFP-on-corruption regression.
- `output/tables/table2_headline_regs.json` — headline regression table data.
- `output/tables/follow_through_results.json` — cross-event regressions for the follow-through dataset.
- `output/tables/headline_results.json` — consolidated headline results.
- `output/tables/descriptive_stats.csv` — region means table.

### Updated files

- `.gitignore` — added exceptions for `follow_through_dataset.csv` and `follow_through_codebook.md` (these are hand-coded, not API-pulled, so they belong in the repo).
- `README.md` — dropped the Stata mention, updated the workflow to reflect the single-language Python pipeline.

### Removed (or to remove)

- `code/stata/` — the Stata `.do` files were never written. The directory can be removed entirely; or left with its README if you prefer to keep the option open for a future Stata replication.

## Suggested commands for the local push

From the code-repo directory on your machine:

```bash
# Recover from any index issues from the sandbox session
git reset

# Stage the new code
git add code/python/data_collection.py
git add code/python/data_cleaning.py
git add code/python/analysis.py

# Stage the new dataset (paper contribution)
git add data/raw/follow_through_dataset.csv
git add data/raw/follow_through_codebook.md

# Stage the processed panel and the follow-through analysis output
git add data/processed/panel.csv
git add data/processed/panel_expanded.csv
git add data/processed/pwt.csv
git add data/processed/follow_through_dataset.csv
git add data/processed/follow_through_analysis.csv

# Stage the results JSONs
git add output/tables/*.json
git add output/tables/descriptive_stats.csv

# Stage README + gitignore updates
git add .gitignore README.md

# Optional cleanup: remove the unused stata directory
git rm -rf code/stata

# Commit
git commit -m "Add empirical pipeline, follow-through dataset, regression results

- Python pipeline: data_collection.py, data_cleaning.py, analysis.py
- Follow-through dataset: 22 anti-corruption reform events coded across
  four continents, 1991-2019, with composite index (speed + depth +
  survival + coalition).
- Headline cross-country result: corruption coefficient 0.53 on log
  spread (p = 0.014, N = 246, pooled OLS with country-clustered SE).
- Growth-accounting decomposition: 55.6% of Africa-Asia gap traces to
  TFP; TFP-on-corruption regression coef -0.137 (p = 0.010, N = 250)
  surviving country and year FE.
- Cross-event follow-through regression: each composite-index point
  associated with 3.5% larger post-reform lending-rate compression
  (p = 0.035, N = 18 raw spec; p = 0.19 macro-adjusted).
- README updated to reflect single-language Python pipeline.
- Stata directory dropped (.do files never written)."

# Push
git push origin main
```

## What does NOT get pushed

- `data/raw/*.csv` and `*.xlsx` (large API-pulled raw files; gitignored). Documented in `data/README.md` with source URLs.
- `output/figures/*.png` (regeneratable from analysis code; gitignored).
- The manuscript PDF (lives outside the repo per `paper/README.md`).
