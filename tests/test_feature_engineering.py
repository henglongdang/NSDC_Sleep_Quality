from __future__ import annotations

import pandas as pd

from sleep_analysis.cleaning import clean_sleep_data
from sleep_analysis.feature_engineering import add_features


def test_lag_features_respect_participant_and_calendar_gaps(raw_rows) -> None:
    raw = raw_rows(
        [
            {"Participant Anonymised ID": "P1", "Date": "2026-10-01", "Day of the Study (Day 1, 2)": 1, "Sleep Quality": 6},
            {"Participant Anonymised ID": "P1", "Date": "2026-10-02", "Day of the Study (Day 1, 2)": 2, "Sleep Quality": 8},
            {"Participant Anonymised ID": "P1", "Date": "2026-10-04", "Day of the Study (Day 1, 2)": 4, "Sleep Quality": 5},
            {"Participant Anonymised ID": "P2", "Date": "2026-10-01", "Day of the Study (Day 1, 2)": 1, "Sleep Quality": 9},
        ]
    )
    cleaned, _ = clean_sleep_data(raw)
    featured = add_features(cleaned).set_index(["participant_id", "date"])
    assert pd.isna(featured.loc[("P1", pd.Timestamp("2026-10-01")), "previous_sleep_quality"])
    assert featured.loc[("P1", pd.Timestamp("2026-10-02")), "previous_sleep_quality"] == 6
    assert pd.isna(featured.loc[("P1", pd.Timestamp("2026-10-04")), "previous_sleep_quality"])
    assert pd.isna(featured.loc[("P2", pd.Timestamp("2026-10-01")), "previous_sleep_quality"])
