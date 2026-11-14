# Data dictionary

The raw source names remain in the workbook. The pipeline uses the standardized names below.

| Source field | Standardized field | Type and unit | Role | Available at prediction time | Missingness and transformation |
| --- | --- | --- | --- | --- | --- |
| Participant Anonymised ID | `participant_id` | identifier | Context | Yes | Blank IDs remain missing. Text normalization resolves numeric/text ID formatting. |
| Date | `date` | date | Context | Yes | Parsed as calendar date. One date outside the 2026 collection window is retained and flagged in the quality report. |
| Day of the Study (Day 1, 2) | `study_day` | integer, 1-14 | Context | Yes | Values outside 1-14 remain visible and are excluded from primary prediction eligibility. |
| Caffeine Servings | `caffeine_servings` | count | Predictor | Yes | Zero means no caffeine. Missing remains missing. |
| Last Caffeine Time | `last_caffeine_hour` | clock hour | Predictor | Yes | Parsed to decimal hours. `na` becomes missing. |
| Exercise Minutes | `exercise_minutes` | minutes | Predictor | Yes | Zero means no exercise. |
| Exercise Intensity | `exercise_intensity` | category | Predictor | Yes | Low/medium/high/none standardized. Walking maps to low. |
| Screen Time Before Bed (min) | `screen_time_before_bed_min` | minutes | Predictor | Yes | Numeric strings parsed. Slash ranges use midpoint plus `screen_time_ambiguous`. |
| Study Hours | `study_hours` | hours | Predictor | Yes | Numeric parsing. |
| Class Hours | `class_hours` | hours | Predictor | Yes | Numeric parsing. |
| Nap | `nap` | yes/no | Predictor | Yes | Yes/no/true/false/0 normalized. |
| Nap Minutes | `nap_minutes` | minutes | Predictor | Yes | Zero means no nap. |
| Last Meal Time | `last_meal_hour` | clock hour | Predictor | Yes | Parsed to decimal hours. |
| Stress Level | `stress_numeric` | reported ordinal scale | Predictor | Yes | Numeric responses retained as entered. Non-numeric labels remain missing in continuous analysis. The observed scale conflicts with the stated 1-5 scale. |
| Planned Bedtime | `planned_bedtime_hour` | clock hour | Predictor | Yes | Parsed, with narrow PM/midnight correction and flag. |
| Actual Bedtime | `actual_bedtime_hour` | clock hour | Retrospective outcome | No | Used only for explanatory time-in-bed calculation. |
| Wake Time | `wake_hour` | clock hour | Retrospective outcome | No | Used only for explanatory time-in-bed calculation. |
| Sleep Quality | `sleep_quality` | 1-10 rating | Primary outcome | No | Numeric ratings retained. Good/Medium/Bad map to 7/5/3 with source flag. |
| Times Woken | `times_woken` | count | Secondary outcome | No | Zero means no awakenings. |
| Sleep Duration (hours) | `sleep_duration_hours` | hours | Secondary wearable outcome | No | `na` becomes missing. Prior-night lag can be used for known-student forecasting. |
| Resting Heart Rate (bpm) | `resting_heart_rate_bpm` | bpm | Secondary wearable outcome | No | Wearable-only structural missingness retained. |
| HRV (ms) | `hrv_ms` | milliseconds | Secondary wearable outcome | No | Wearable-only structural missingness retained. |

Derived fields include overnight `time_in_bed_hours`, planned-versus-actual bedtime difference, caffeine/meal timing relative to planned bedtime, circular planned-bedtime features, prior sleep measures, and prior-only participant-specific deviations.
