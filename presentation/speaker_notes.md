# Speaker notes

## 1. Opening
Frame this as a comparison of two useful but different prediction decisions. Do not treat an association as a recommendation to change behavior.

## 2. The analytical question
Clarify that a random row split would leak participant-specific patterns into evaluation. The central question is whether a night that departs from a student's own routine adds usable information.

## 3. Dataset
State the analytical sample and wearable counts before discussing device results. The wearable subset is not assumed representative of the full sample.

## 4. Data quality
Point out the stress-scale mismatch, duplicate participant-date records, and mixed time entries. Emphasize that each treatment is documented and reproducible.

## 5. Outcome variation
The ICC supports testing personal-history baselines. It does not say any individual student's sleep is fixed.

## 6. Pooled associations
Prior sleep quality has the clearest pooled association. Screen time and stress are small negative correlations after multiplicity adjustment, not behavioral effects.

## 7. Stress decomposition
The within-person interval includes zero. This is an inconclusive result, not proof that stress has no effect under every design.

## 8. Leakage prevention
Only information available before the target night enters a model. Current-night sleep duration, wearable measures, heart rate, and wake information are excluded.

## 9. Validation design
Use grouped validation for a first encounter with a new student. Use a chronological split only when the student has earlier records available.

## 10. New-student result
Neither daytime behavioral model improves on the global mean. That result prevents the deck from presenting correlation as a broadly useful prediction tool.

## 11. Known-student result
The final Extra Trees model has the lowest MAE, but its advantage over the simple previous-night baseline is about 0.01 points. Keep the claim modest.

## 12. Feature importance
Permutation importance describes predictive dependence in the held-out data; it does not identify a mechanism or an intervention target.

## 13. Wearables
State the sample sizes with the correlations. Avoid physiological or clinical interpretation from this selective subgroup.

## 14. Limitations
The study is short, observational, and based partly on self-report. Scale inconsistencies, missing device data, and unmeasured context limit causal and general claims.

## 15. Close
The practical lesson is to match validation to the decision, preserve transparent baselines, and collect more consistent longitudinal data before making prescriptions.
