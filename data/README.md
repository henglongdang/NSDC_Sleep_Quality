# Data handling

`data/raw/` contains the supplied workbook and is excluded from Git. It remains unchanged.

`data/processed/` contains the cleaned participant-day dataset produced by
`python -m sleep_analysis.run_analysis`. It is also excluded from Git because it retains
anonymized but participant-level records.

All reported tables and figures aggregate data and avoid publishing participant identifiers.
