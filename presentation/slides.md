# NSDC Sleep Analysis: slide outline

1. **Can evening routines predict that night's sleep quality?**  
   The dataset, the primary outcome, and the two prediction settings.
2. **The analytical question**  
   Why unseen-student prediction and later-night forecasting answer different questions.
3. **What was observed**  
   Sample size, repeated records, fields, and selective wearable coverage.
4. **Data quality checks**  
   The principal quality flags and the documented treatment for each.
5. **Sleep quality was neither wholly personal nor wholly shared**  
   Distribution of the 1--10 outcome and the intraclass correlation.
6. **Pooled associations**  
   Spearman correlations with pre-specified predictors after false-discovery adjustment.
7. **Stress: pooled versus within-person signal**  
   Participant-clustered estimates separate personal change from between-student differences.
8. **Leakage-safe feature windows**  
   Inputs available before the target night, with prohibited current-night fields excluded.
9. **Two evaluation settings**  
   Grouped validation for a new student and chronological validation for a known student.
10. **Unseen-student forecasts**  
    Daytime routine models did not beat the global-mean baseline.
11. **Known-student forecasts**  
    Sleep history supported a modest forecast; the previous-night baseline was nearly as strong as the final model.
12. **Held-out feature importance**  
    Permuting sleep-history features increased error most; this is not a causal ranking.
13. **Wearable subset**  
    Secondary associations from a small, selective device-data subgroup.
14. **What the analysis cannot establish**  
    Observational, measurement, missingness, and model-complexity limitations.
15. **Conclusion**  
    Different decisions need different validation, and simple history is the practical benchmark.
