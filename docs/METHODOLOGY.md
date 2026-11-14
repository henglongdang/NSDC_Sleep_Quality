# Methodology

## Cleaning principles

The original workbook remains immutable. The pipeline retains raw fields, standardized analytical fields, and explicit flags. It does not delete unusual values simply because they are extreme.

String placeholders such as `na` become missing values. Numeric zero stays zero. Exercise intensity and nap labels are standardized. Slash-delimited screen-time entries are represented by their midpoint and receive an ambiguity flag. Written sleep-quality labels receive transparent ordinal anchors: Good = 7, Medium = 5, and Bad = 3. A numeric-only sensitivity analysis checks whether that choice changes model performance.

For likely 12-hour bedtime entries, 08:00-11:59 is treated as evening and 12:00-12:59 as midnight. Each correction receives a flag. Overnight time in bed uses modular 24-hour arithmetic.

## Feature availability

| Feature group | Available before the target sleep period? | Used for unseen-student model? | Used for known-student forecast? |
| --- | --- | --- | --- |
| Study day and weekday | Yes | Yes | Yes |
| Planned bedtime and meal/caffeine timing | Yes | Yes | Yes |
| Caffeine, exercise, screen time, academic hours, nap, stress | Yes | Yes | Yes |
| Prior sleep quality, duration, and time in bed | Yes, only with earlier logs | No | Yes |
| Prior participant averages and prior behavioural deviations | Yes, only with earlier logs | No | Yes |
| Actual bedtime, wake time, awakenings, wearable measures | No | No | No |

## Models

The pipeline uses train-only median imputation and one-hot categorical encoding inside each model pipeline. Candidate models are a mean DummyRegressor, Ridge regression, and Extra Trees. The staged feature sets test whether sleep history, daytime routines, and prior-only individualized deviations add incremental value.

## Interpretation controls

Feature importance uses held-out permutation importance. A five-run target-label permutation check provides a negative control. The permuted-model MAE was 1.78 (SD 0.06), substantially worse than the final chronological model's MAE of 1.30. This does not prove no leakage is possible, but it makes a spurious high-performing target mapping less plausible.
