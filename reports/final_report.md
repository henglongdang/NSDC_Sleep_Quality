# Can Daily Routines Predict Sleep Quality Tonight?

## 1. Executive summary

This study examined whether daily routines recorded before sleep can predict that night's self-reported sleep quality. The main result is conditional on who the model has already observed. Daytime behavior models did not improve over a global mean for students held out entirely from training. For students with earlier logs, prior sleep quality and personal sleep history were informative. A personalized Extra Trees model produced MAE 1.30 on a 1-10 scale, but the previous-night sleep-quality baseline achieved MAE 1.31. That narrow difference matters. The data support modest, personalized forecasting from sleep history more clearly than broad claims about daytime habits.

## 2. Research question

To what extent can a student's daily behaviours and routines predict their sleep quality that night?

The primary outcome was self-reported sleep quality, recorded on a 1-10 scale. The prediction point was after the evening behavior log and before the target night's sleep. Actual bedtime, wake time, nighttime awakenings, wearable sleep duration, resting heart rate, HRV, and all other target-night outcomes were excluded from primary model features.

## 3. Motivation and analytical angle

Many ordinary sleep analyses pool all records and report a correlation between a behavior and sleep quality. That approach can confuse two questions. Students who usually differ in stress or bedtime may differ for reasons that have little to do with a change in behavior on a particular day. The central angle here was therefore whether a deviation from a student's own routine added useful evidence beyond stable differences between students.

This distinction also shaped model validation. A model for a student who has never appeared in training should not use their personal history. A later-night forecast for a student who has already logged several days can use earlier, shifted history. Reporting those settings separately avoids treating an easy, participant-leaking random split as generalizable performance.

## 4. Dataset and participants

The raw workbook contains 632 rows and 22 fields covering daily routines, self-reported sleep, and optional wearable data. It has 16 rows without a participant ID. The raw ID field has 47 distinct nonmissing cell values, but numeric/text formatting variants resolve to 45 standardized IDs after text normalization. The primary prospective analysis contains 530 eligible participant-days from those 45 IDs, with a mean of 13.7 observations per known participant.

Sleep quality in the primary subset averaged 6.64, with median 7, standard deviation 2.08, interquartile range 3, and observed range 1-10. Ratings of 7 and 8 were most common. Wearable sleep duration was available in 239 primary-analysis records, resting heart rate in 116, and HRV in 56. The wearable analyses are therefore secondary and selective.

## 5. Data quality and cleaning

The cleaning pipeline preserved the source workbook unchanged and retained raw fields alongside standardized fields and flags. There were no fully duplicated rows, but 35 duplicate participant-date records when counting only later duplicates. The processed audit flags all 70 records in those repeated pairs. Fifteen records had study days outside the intended 1-14 window. A parsed 2025 date appears amid the 2026 collection dates. The analysis kept source evidence visible rather than guessing a correction.

Several response-format issues affected interpretation. The raw workbook had 366 stress values outside the stated 1-5 scale, 79 screen-time values outside the stated 0-60 minute window, 24 caffeine-serving/time conflicts, and 14 slash-delimited screen-time ranges. The pipeline parsed an ambiguous range such as `50 / 60` to its midpoint and retained an ambiguity flag. It used a narrow, documented PM/midnight correction for 64 bedtime fields. Five time-in-bed values fell below two hours or above 16 hours and were flagged rather than deleted.

Written sleep-quality labels created another judgment call. Good, Medium, and Bad were mapped to 7, 5, and 3 and recorded with a source flag. The final model's numeric-only held-out sensitivity analysis had MAE 1.34 on 175 records, close to 1.30 in the primary test. This does not prove the mapping is perfect, but it suggests it does not drive the model comparison.

## 6. Exploratory data analysis

Figure 1 shows field-level missingness. Wearable measures have a clear structural pattern because they were optional. Missing wearable data were never treated as zero. Figures 2 through 5 show the outcome distribution, routine relationships, stress at within- and between-person levels, and study-day patterns.

Pooled Spearman correlations were generally small. Prior sleep quality had the strongest correlation with the next reported sleep-quality score (rho 0.49, n=480). Screen time had rho -0.16 (n=529, FDR-adjusted p=0.001), planned bedtime had rho 0.15 (n=528, adjusted p=0.003), and reported stress had rho -0.11 (n=527, adjusted p=0.034). These estimates use repeated participant-days and describe marginal, pooled relationships. They are not causal effects.

Sleep quality varied materially by participant. The one-way intraclass correlation was 0.44, with bootstrap 95% CI 0.27 to 0.57. This supports the choice to test personalized historical baselines. Mean sleep quality also varied across reported study days, from 5.59 on day 1 to 7.43 on day 6, but daily coverage changed over the period. The study-day pattern is descriptive and does not establish adaptation, improvement, or a calendar effect.

## 7. Within-person and between-person analysis

The retrospective stress decomposition separated each day's stress from a participant's full-period average stress. The within-person estimate was -0.09 sleep-quality points per one within-person stress SD, with 95% CI -0.26 to 0.09 and participant-clustered p=0.326. The between-person standardized estimate was -0.16, with 95% CI -0.61 to 0.29 and p=0.484.

Neither estimate gives strong evidence that the stress-sleep association remains after accounting for participant clustering and the observed data quality. The direction is consistent with the pooled correlation, but the intervals include no association. This is a useful negative result: the simple pooled pattern should not become a confident within-person behavioral claim.

## 8. Feature engineering

The predictive pipeline created weekday and weekend indicators, circular planned-bedtime features, caffeine and meal timing relative to planned bedtime, total academic hours, prior-night sleep measures, prior three-day sleep-quality mean, and prior-only participant means and deviations. Every historical predictive feature shifts within participant before expansion. A calendar gap removes a previous-night feature rather than treating a nonconsecutive record as yesterday.

Retrospective full-period centering was used only for explanatory within-person analysis. It never entered the prospective model. The model code explicitly rejects current-night outcome fields. Unit tests cover missing values, zero versus missing, time handling across midnight, participant grouping, calendar gaps, and leakage guards.

## 9. Predictive modeling methodology

Two validation scenarios answer different questions.

**Unseen-student generalization** used five-fold GroupKFold, holding out whole participants. The models received only pre-sleep target-night variables and calendar context. They did not receive participant IDs, lagged sleep, or any held-out student's full-period average.

**Known-student forecasting** used earlier records for training and the latest 30% of eligible records for testing within each participant. This produced 339 training and 183 test records across 40 participants with sufficient history. Median imputation, categorical encoding, and scaling were fit inside each training pipeline.

The candidates were a global mean baseline, prior-sleep baselines, Ridge models, and Extra Trees. Performance was reported as MAE, RMSE, R-squared, median absolute error, Spearman rank correlation, and percentage within one sleep-quality point. MAE is especially readable here because it measures average error directly in rating points.

## 10. Model evaluation

For unseen students, the baseline won. Its MAE was 1.69. Daytime Ridge had MAE 1.82 and daytime Extra Trees had MAE 1.75. Neither behavioral model delivered useful out-of-sample improvement for a new participant.

For later observations of known students, the global mean baseline had MAE 1.71. Previous-night sleep quality improved to 1.31 on 180 applicable records. The prior participant mean reached 1.34. The best observed model, personalized Extra Trees, reached MAE 1.30, RMSE 1.69, R-squared 0.37, Spearman rho 0.56, and 44% of predictions within one point.

The best model's improvement over previous-night sleep quality was about 0.01 MAE points. That is too small to justify a strong claim that a complex behavioral model materially outperforms a simple lag baseline. The target-label permutation check produced mean MAE 1.78 across five shuffled-target fits, which is worse than the real-label model and provides a negative-control check against an obviously spurious target relationship.

## 11. Important features and secondary outcomes

Held-out permutation importance ranked prior three-day sleep quality, prior participant mean sleep quality, and previous-night sleep quality first. Permuting the prior three-day mean increased MAE by 0.16 on average, while current stress increased it by 0.01. Importance reflects predictive contribution in this dataset and model. It does not identify a causal mechanism.

In the wearable subset, reported sleep duration correlated positively with subjective sleep quality (rho 0.32, n=239). Resting heart rate correlated negatively (rho -0.52, n=116), and HRV correlated positively (rho 0.79, n=56). The HRV result has a very small and selective sample. It should be treated as a descriptive signal for further study, not a population claim.

## 12. Additional discoveries

The contrast between validation scenarios is the most informative discovery. The data contain enough stable participant structure to help forecast a later night for a known student, but the target-night routine fields do not transfer well to unseen students. This points to heterogeneity and limited sample size rather than a universal behavioral rule.

The other notable result is restraint. Screen time and stress show small pooled negative correlations, yet the clustered within-person stress analysis is inconclusive and behavioral models did not improve unseen-student prediction. The analysis therefore does not convert correlations into recommendations.

## 13. Limitations

The study covers a short period with a modest, nonrandom sample. It uses self-reported behavior and subjective sleep quality, and optional wearable measures are selective. The raw data include substantial format inconsistency, missingness, duplicate participant-day labels, and a stress scale that conflicts with the stated instrument. Important contextual variables are absent. The model comparison can still overfit despite grouped and chronological evaluation. Most importantly, observational prediction does not identify causal effects.

## 14. Conclusion

Student routines contain limited generalizable information about sleep quality in this dataset. A model trained on other students did not beat a global mean for unseen participants. For students with earlier records, prior sleep quality and personal history were useful, while the more complex model only slightly surpassed a previous-night baseline. The practical analytical lesson is to match validation to the decision setting and to value a transparent baseline when complexity adds little.

## 15. References

1. National Statistics and Data Club. *NSDC Open Project: Can Data Predict How You'll Sleep Tonight?* Supplied project handout, Fall 2026.
2. National Statistics and Data Club. *NSDC Open Project Rubric: Sleep Analysis and Prediction.* Supplied rubric, Fall 2026.
3. NSDC pooled student sleep dataset. `openProj_masterF26.xlsx`, supplied for this project.

Supporting tables are in [`reports/tables/`](tables/) and figures are in [`reports/figures/`](figures/).
