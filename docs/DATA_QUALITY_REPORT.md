# Data quality report

## Structural audit

The supplied workbook has 632 rows and 22 expected columns. There are no fully duplicate rows. The raw identifier field contains 47 distinct nonmissing cell values, including numeric/text formatting variants that normalize to 45 standardized participant IDs. Sixteen rows lack an ID.

The primary prospective dataset contains 530 participant-days from 45 standardized participants. Eligibility requires a known ID, parsed date, study day in 1-14, observed sleep quality, and a non-duplicate participant-date record. This is an analytical subset, not a claim that the excluded records are invalid.

## Duplicate and schedule issues

- 35 duplicate participant-date records appear when counting only later duplicates. The cleaned audit flags all 70 rows belonging to those pairs.
- 59 duplicate participant-study-day records appear when counting later duplicates.
- 15 records have study days outside 1-14.
- One parsed date is in 2025 rather than the main 2026 collection window. It remains in the source and analytical data because the intended correction cannot be confirmed.

## Missingness

Wearable fields show structural missingness, not zero values: sleep duration is available in 288 raw rows, resting heart rate in 140, and HRV in 56. In the primary analytical subset, 23 participants have at least one wearable sleep-duration value. Last caffeine time is often missing when caffeine servings are zero, which is logically consistent in many cases.

The report treats missingness as potentially related to device ownership, reporting behavior, and daily context. The data cannot determine whether a variable is MCAR, MAR, or MNAR. Predictive imputers fit within the training fold only.

## Range and logic flags

| Check | Records flagged | Treatment |
| --- | ---: | --- |
| Stress outside stated 1-5 range | 366 | Retained as reported. Continuous stress findings require caution because the scale is inconsistent. |
| Screen time outside stated 0-60 range | 79 | Retained, with no automatic clipping. |
| Implausible time in bed under 2 or over 16 hours | 5 | Retained and flagged. Not used as a current-night predictor. |
| Exercise duration/intensity conflict | 4 | Retained and standardized where possible. |
| Caffeine servings/time conflict | 24 | Retained. Time-based caffeine features remain missing where timing is unavailable. |
| Ambiguous slash screen-time entries | 14 | Midpoint parsed and flagged. |
| PM/midnight bedtime corrections | 64 fields | Rule applied only to 08:00-12:59 bedtime entries and retained as flags. |

The quality burden matters. Associations involving stress, screen time, times, and wearable measures should be read as estimates from imperfect observational records, not precise behavioral effects.
