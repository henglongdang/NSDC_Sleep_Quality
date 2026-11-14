# NSDC Sleep Analysis

This project examines whether a student's recorded daytime routines can predict that night's self-reported sleep quality. Its central question is whether a change from a student's own usual routine adds more useful information than differences between students.

The analysis uses 632 raw participant-day records from the supplied pooled workbook. It keeps the raw workbook unchanged, documents quality issues, separates explanatory and prospective analyses, and evaluates two distinct prediction settings.

## Main result

For a student with prior observations, sleep history carried the clearest predictive signal. The final chronological Extra Trees model achieved MAE 1.30 on the 1-10 sleep-quality scale, versus 1.71 for a global-mean baseline. The previous night's sleep-quality rating alone achieved MAE 1.31. Daytime routines did not improve prediction for entirely unseen students. The strongest conclusion is about personalization and history, not a general rule that a particular daytime behavior causes better sleep.

## Repository map

- `data/raw/`: immutable copy of the supplied workbook. Excluded from Git.
- `data/processed/`: reproducibly generated participant-level analytical data. Excluded from Git.
- `src/sleep_analysis/`: loading, validation, cleaning, feature engineering, statistics, modeling, figures, and reporting.
- `tests/`: unit tests for data handling, time calculations, feature leakage, and modeling safeguards.
- `notebooks/NSDC_Sleep_Analysis.ipynb`: executed analytical narrative.
- `reports/`: final report, executive summary, figures, and aggregate tables.
- `presentation/`: final presentation, outline, and speaker notes.
- `docs/`: methodology, data quality, reproducibility, and rubric evidence.

## Reproduce

Create the environment and run the full analysis from the project root.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m sleep_analysis.run_analysis
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src tests
```

The analysis script regenerates participant-level data, aggregate tables, and figures. The notebook reads those same outputs and does not duplicate the analytical logic.

## Data protection

The raw and processed participant-level files are excluded from Git. Reports and slides use aggregate statistics and do not display participant identifiers.

## Scope

The data are short-run, self-reported, observational records. Results describe associations and predictive performance under the specified validation designs. They do not establish causal effects or clinical claims.
