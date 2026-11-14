# Rubric alignment

| Rubric category | Evidence in this project |
| --- | --- |
| Insight and findings | The project separates unseen-student generalization from known-student forecasting. It shows that prior sleep history, rather than a broad daytime routine model, accounts for the most useful predictive signal. See `reports/tables/model_comparison.csv`, `reports/tables/permutation_importance.csv`, and final report sections 7-11. |
| Creativity and originality | The central question distinguishes within-person deviations from between-person differences and uses prior-only individualized features. See `docs/ANALYSIS_PLAN.md`, `reports/figures/04_within_between_stress.png`, and section 7 of the final report. |
| Exploratory data analysis | The project audits missingness, duplicates, range conflicts, distribution, temporal coverage, wearable subset, and behavior relationships. See `docs/DATA_QUALITY_REPORT.md`, `reports/figures/01` through `05`, and aggregate tables. |
| Technical quality and modeling | Deterministic modules, tests, time parsing, leakage guards, train-only preprocessing, GroupKFold, chronological holdout, baselines, multiple metrics, importance, and label permutation are implemented. See `src/`, `tests/`, `docs/METHODOLOGY.md`, and `docs/MODELING_STRATEGY.md`. |
| Interpretation and limitations | The report distinguishes association from causation, treats weak evidence as weak, and documents data and design limitations. See `docs/LIMITATIONS.md` and sections 7, 11, and 13 of the final report. |
| Deliverables | The repository contains a runnable notebook, report, executive summary, aggregate tables, figures, presentation with speaker notes, tests, and reproducibility guide. |
