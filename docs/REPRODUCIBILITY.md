# Reproducibility guide

## Requirements

- Python 3.11 or later
- The supplied workbook copied to `data/raw/openProj_masterF26.xlsx`
- Dependencies from `requirements.txt`

## Commands

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m sleep_analysis.run_analysis
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\jupyter.exe nbconvert --to notebook --execute notebooks/NSDC_Sleep_Analysis.ipynb --output NSDC_Sleep_Analysis.ipynb
```

## Determinism

The analysis uses seed 2026 for model estimators, permutation diagnostics, and ICC bootstrap resampling. The workflow uses fixed chronological and grouped splits derived from the supplied data. Minor differences can arise from library-version changes, which is why the project records a bounded dependency specification.

## Expected outputs

Running the pipeline creates `data/processed/sleep_cleaned.csv`, aggregate CSV files in `reports/tables/`, and figures in `reports/figures/`. The raw and processed participant-level files stay out of Git. The notebook, report, and presentation read the aggregate outputs.
