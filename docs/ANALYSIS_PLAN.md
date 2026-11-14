# Analysis plan

## Pre-specified questions

- H1: Higher-than-usual stress relates to lower sleep quality within a student.
- H2: Caffeine consumed closer to planned bedtime relates to sleep quality.
- H3: Deviation from a student's habitual planned bedtime relates to sleep quality.
- H4: Exercise duration may have a nonlinear relationship with sleep quality.
- H5: Prior sleep information predicts later sleep quality.

## Primary outcome

Sleep quality is a 1-10 self-reported rating. Regression models use the rating as an approximately ordinal outcome. The report treats it as a subjective, bounded measure and does not claim clinical precision.

## Primary prediction point

The model acts after the evening log and before the target night's sleep. It may use date, planned bedtime, daytime behaviour, and properly constructed prior-night features. It may not use target-night actual bedtime, wake time, awakenings, wearable sleep duration, resting heart rate, HRV, time in bed, or target sleep quality.

## Evaluation plan

- **Unseen-student generalization:** five-fold GroupKFold by participant. Historical participant features and participant identifiers are omitted.
- **Known-student forecasting:** for each eligible participant with at least four records, train on the earlier 70% and test on the latest 30%. Historical features use shifted, earlier observations only.
- **Metrics:** MAE, RMSE, R-squared, median absolute error, Spearman rank correlation, and share of predictions within one rating point.

## Statistical plan

The analysis reports descriptive distributions, Spearman correlations with Benjamini-Hochberg adjustment, an ICC with participant bootstrap confidence interval, and a within-person/between-person stress decomposition with participant-clustered standard errors. The within-person analysis is retrospective and uses full-period participant centering. It is not used as a prospective feature.
