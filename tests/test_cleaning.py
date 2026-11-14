from __future__ import annotations

import pandas as pd

from sleep_analysis.cleaning import clean_sleep_data


def test_cleaning_preserves_zero_and_missing_distinction(raw_rows) -> None:
    raw = raw_rows(
        [
            {
                "Caffeine Servings": 0,
                "Exercise Minutes": 0,
                "Nap Minutes": 0,
                "Sleep Duration (hours)": "na",
            }
        ]
    )
    cleaned, _ = clean_sleep_data(raw)
    row = cleaned.iloc[0]
    assert row["caffeine_servings"] == 0
    assert row["exercise_minutes"] == 0
    assert row["nap_minutes"] == 0
    assert pd.isna(row["sleep_duration_hours"])


def test_category_normalization_and_label_mapping(raw_rows) -> None:
    raw = raw_rows(
        [
            {
                "Exercise Intensity": "Low (Walking)",
                "Nap": "True",
                "Sleep Quality": "Good",
                "Screen Time Before Bed (min)": "50 / 60",
            }
        ]
    )
    cleaned, audit = clean_sleep_data(raw)
    row = cleaned.iloc[0]
    assert row["exercise_intensity"] == "low"
    assert row["nap"] == "yes"
    assert row["sleep_quality"] == 7
    assert row["screen_time_before_bed_min"] == 55
    assert bool(row["screen_time_ambiguous"])
    assert audit["rows_with_mapped_sleep_quality"] == 1


def test_cleaning_flags_duplicate_participant_date(raw_rows) -> None:
    raw = raw_rows([{}, {"Sleep Quality": 8}])
    cleaned, _ = clean_sleep_data(raw)
    assert cleaned["duplicate_participant_date"].all()
    assert not cleaned["prediction_eligible"].any()
