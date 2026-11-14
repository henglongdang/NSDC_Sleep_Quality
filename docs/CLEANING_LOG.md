# Cleaning log

| Transformation | Reason | Records affected | Missing values introduced? | Exclusions |
| --- | --- | ---: | --- | --- |
| Copy workbook to `data/raw/` and checksum verify | Preserve an immutable source | 632 | No | None |
| Standardize column names | Use stable, readable code fields | 22 columns | No | None |
| Parse dates, numbers, and clock times | Convert mixed storage formats to analytical types | All relevant fields | Invalid strings become missing | None |
| Standardize nap and exercise categories | Resolve capitalization and synonymous labels | Category fields | Unrecognized values become missing | None |
| Parse slash screen-time ranges to midpoint | Retain information while flagging ambiguity | 14 | No | None |
| Map Good/Medium/Bad sleep labels to 7/5/3 | Retain ordinal outcome records transparently | 32 raw rows, 17 eligible rows | No | None |
| Correct probable 12-hour bedtime entries | Avoid treating 11:00 as morning when paired with a next-morning wake time | 64 time fields | No | None |
| Calculate overnight intervals modularly | Handle midnight transitions | Parsed bedtime/wake pairs | Missing source times remain missing | None |
| Add duplicate, range, and logic flags | Preserve questionable records for review | All records | No | None |
| Define prediction eligibility | Avoid unknown participant history, out-of-range study days, absent target, and duplicate day labels | 530 retained for primary prediction | No | 102 rows excluded only from primary prediction |

No raw observations are overwritten. The processed dataset retains source fields and transformation flags.
