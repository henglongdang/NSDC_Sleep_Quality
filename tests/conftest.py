"""Fixtures shared by the analytical test suite."""

from __future__ import annotations

import pandas as pd
import pytest

from sleep_analysis.data_loading import EXPECTED_COLUMNS


@pytest.fixture
def raw_rows() -> callable:
    """Build compact raw-format records with sensible defaults."""

    def _build(overrides: list[dict]) -> pd.DataFrame:
        base = {
            "Participant Anonymised ID": "P1",
            "Date": "2026-10-01",
            "Day of the Study (Day 1, 2)": 1,
            "Caffeine Servings": 0,
            "Last Caffeine Time": pd.NA,
            "Exercise Minutes": 0,
            "Exercise Intensity": "none",
            "Screen Time Before Bed (min)": "30",
            "Study Hours": 2,
            "Class Hours": 1,
            "Nap": "No",
            "Nap Minutes": 0,
            "Last Meal Time": "19:00",
            "Stress Level": 3,
            "Planned Bedtime": "23:00",
            "Actual Bedtime": "23:30",
            "Wake Time": "07:30",
            "Sleep Quality": 7,
            "Times Woken": 1,
            "Sleep Duration (hours)": "7.5",
            "Resting Heart Rate (bpm)": "60",
            "HRV (ms)": 55,
        }
        rows = []
        for update in overrides:
            row = base | update
            rows.append({column: row[column] for column in EXPECTED_COLUMNS})
        return pd.DataFrame(rows)

    return _build
