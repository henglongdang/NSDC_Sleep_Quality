# Decision log

| Decision | Rationale | Consequence |
| --- | --- | --- |
| Preserve all raw rows | The data contain unusual but not provably erroneous observations. | Flags and eligibility rules replace silent deletion. |
| Use 45 standardized text IDs for longitudinal analysis | The source mixes numeric and text storage for otherwise identical identifiers. | Two raw formatting variants collapse after text normalization. |
| Exclude duplicate participant-date records from primary prediction | A repeated participant-day makes chronology and target assignment ambiguous. | 70 rows are excluded from the main prediction subset but retained in processed data. |
| Retain out-of-range screen and stress entries | Their intended correction is unknown. | They remain in descriptive and model data with strong caveats. |
| Map written sleep labels to ordinal anchors | The labels otherwise discard observed outcome data. | Numeric-only sensitivity analysis checks the impact. |
| Use circular time features | Midnight is adjacent to 23:00, not 23 hours away. | Planned bedtime enters models as sine/cosine features. |
| Use prior-only personalized features | Full-period participant averages would leak future observations in forecasting. | Predictive deviations use shifted expanding history. |
| Separate unseen and known-student validation | A random row split would leak participant-specific patterns across train and test. | Results are reported by scenario rather than selecting the flattering split. |
| Use participant-clustered standard errors for stress decomposition | The random-intercept specification produced unstable group-level uncertainty. | The final retrospective decomposition accounts for clustering without an unstable variance estimate. |
| Prefer the lag baseline in interpretation | The final Extra Trees model only slightly improves MAE over previous-night sleep quality. | The report emphasizes the simple, transparent baseline. |
