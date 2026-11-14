"""Load the supplied workbook without changing the source file."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS = [
    "Participant Anonymised ID",
    "Date",
    "Day of the Study (Day 1, 2)",
    "Caffeine Servings",
    "Last Caffeine Time",
    "Exercise Minutes",
    "Exercise Intensity",
    "Screen Time Before Bed (min)",
    "Study Hours",
    "Class Hours",
    "Nap",
    "Nap Minutes",
    "Last Meal Time",
    "Stress Level",
    "Planned Bedtime",
    "Actual Bedtime",
    "Wake Time",
    "Sleep Quality",
    "Times Woken",
    "Sleep Duration (hours)",
    "Resting Heart Rate (bpm)",
    "HRV (ms)",
]

COLUMN_MAP = {
    "Participant Anonymised ID": "participant_id",
    "Date": "date",
    "Day of the Study (Day 1, 2)": "study_day",
    "Caffeine Servings": "caffeine_servings",
    "Last Caffeine Time": "last_caffeine_time_raw",
    "Exercise Minutes": "exercise_minutes",
    "Exercise Intensity": "exercise_intensity_raw",
    "Screen Time Before Bed (min)": "screen_time_raw",
    "Study Hours": "study_hours",
    "Class Hours": "class_hours",
    "Nap": "nap_raw",
    "Nap Minutes": "nap_minutes",
    "Last Meal Time": "last_meal_time_raw",
    "Stress Level": "stress_level_raw",
    "Planned Bedtime": "planned_bedtime_raw",
    "Actual Bedtime": "actual_bedtime_raw",
    "Wake Time": "wake_time_raw",
    "Sleep Quality": "sleep_quality_raw",
    "Times Woken": "times_woken",
    "Sleep Duration (hours)": "sleep_duration_raw",
    "Resting Heart Rate (bpm)": "resting_heart_rate_raw",
    "HRV (ms)": "hrv_ms",
}


def load_raw_data(path: str | Path) -> pd.DataFrame:
    """Read the first worksheet while preserving identifiers and raw strings."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Raw data file not found: {source}")
    frame = pd.read_excel(source, sheet_name=0, dtype={"Participant Anonymised ID": "string"})
    if frame.empty:
        raise ValueError("Raw workbook contains no observations.")
    return frame


def standardize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Rename expected source fields to stable snake_case names."""
    unexpected = sorted(set(frame.columns) - set(EXPECTED_COLUMNS))
    missing = sorted(set(EXPECTED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Workbook is missing expected columns: {missing}")
    result = frame.rename(columns=COLUMN_MAP).copy()
    result.attrs["unexpected_columns"] = unexpected
    result.attrs["original_columns"] = list(frame.columns)
    return result
