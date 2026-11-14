# Project overview

## Question

To what extent can a student's daily behaviours and routines predict their sleep quality that night?

The project treats this as two separate questions.

1. Can routine information collected before sleep predict the outcome for a student never seen during training?
2. For a student with earlier logs, does personal sleep history and a change from usual behaviour improve a later-night forecast?

## Analytical angle

The second question is the project's distinctive focus. Population differences and within-person deviations are not interchangeable. A student who generally reports more stress may differ from other students for many reasons. A day that is more stressful than that same student's usual day addresses a different pattern.

## Deliverables

The project includes a deterministic pipeline, cleaned analytical data, quality tables, nine figures, an executed notebook, final report, executive summary, presentation, tests, and rubric evidence. The source workbook remains unchanged in `data/raw/`.

## Main finding

The analysis found moderate participant-to-participant persistence in sleep quality (ICC 0.44, bootstrap 95% CI 0.27 to 0.57). For later records of already observed students, prior sleep quality and participant-specific historical averages were more useful than contemporaneous daytime behaviours. Under group-based validation for unseen students, neither behavioral model improved on the global mean.
