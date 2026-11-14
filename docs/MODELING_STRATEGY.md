# Modeling strategy

## Baselines first

The comparison starts with a global mean, then adds previous-night sleep quality and a prior participant mean before considering machine-learning models. This matters because a complex model should earn its added complexity.

## Scenario A: unseen students

Five GroupKFold splits hold out whole students. The behavioral Ridge and Extra Trees models use only target-night pre-sleep variables. They do not receive a participant ID, target-night outcome, or held-out student's full-period history.

## Scenario B: later nights for known students

Each participant contributes earlier records to training and later records to testing. The feature pipeline computes lagged and expanding features after sorting within participant. A calendar gap prevents a prior-night feature from crossing a missing day.

## Results to compare

| Scenario | Best candidate | MAE | Interpretation |
| --- | ---: | ---: | --- |
| Unseen students | Global mean baseline | 1.69 | The daytime models did not generalize beyond the baseline. |
| Known students | Personalized Extra Trees | 1.30 | Earlier sleep history improved later-night forecasts. |
| Known students | Previous-night sleep quality | 1.31 | A simple lag was nearly as useful as the best model. |

The small difference between the final model and the lag baseline argues for restraint. The model is useful as an incremental forecast, not as a precise behavioural prescription.
