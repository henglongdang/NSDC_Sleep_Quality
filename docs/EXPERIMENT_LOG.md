# Experiment log

| Experiment | Validation | Result | Decision |
| --- | --- | --- | --- |
| Global mean baseline | Grouped and chronological | MAE 1.69 unseen, 1.71 known later nights | Retained as reference. |
| Daytime Ridge | GroupKFold by participant | MAE 1.82 | Did not improve unseen-student prediction. |
| Daytime Extra Trees | GroupKFold by participant | MAE 1.75 | Did not improve unseen-student prediction. |
| Previous-night sleep quality | Participant chronology | MAE 1.31 on 180 valid later records | Strong, transparent baseline. |
| Prior participant mean | Participant chronology | MAE 1.34 | Shows meaningful individual persistence. |
| Sleep-history Ridge | Participant chronology | MAE 1.33 | Comparable to simple history baselines. |
| Behavioral Ridge | Participant chronology | MAE 1.40 | Adding routines did not improve the ridge model. |
| Personalized Ridge | Participant chronology | MAE 1.56 | Prior-only individualized deviations did not help this linear specification. |
| Personalized Extra Trees | Participant chronology | MAE 1.30, RMSE 1.69, R² 0.37 | Best observed model, but only a small MAE improvement over the lag baseline. |
| Numeric-outcome sensitivity | Held-out test rows with numeric target | MAE 1.34, n=175 | Label mapping does not appear to drive the conclusion. |
| Target permutation negative control | Chronological split, five permutations | Mean MAE 1.78, SD 0.06 | No implausibly strong performance after target scrambling. |
