"""Deterministic cleaning while retaining raw-field provenance and quality flags."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from sleep_analysis.data_loading import standardize_columns
from sleep_analysis.validation import (
    MISSING_TOKENS,
    circular_difference_hours,
    normalize_bedtime,
    overnight_duration_hours,
    parse_clock_time,
    parse_screen_time,
)

NUMERIC_COLUMNS = [
    "caffeine_servings",
    "exercise_minutes",
    "study_hours",
    "class_hours",
    "nap_minutes",
    "times_woken",
    "hrv_ms",
]


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype("string").str.strip().str.lower().replace(list(MISSING_TOKENS), np.nan), errors="coerce")


def _normalize_exercise(value: Any) -> str | float:
    if pd.isna(value):
        return np.nan
    text = str(value).strip().lower()
    if text in MISSING_TOKENS:
        return np.nan
    if "walk" in text or text == "low":
        return "low"
    if text in {"medium", "moderate"}:
        return "medium"
    if text == "high":
        return "high"
    if text in {"none", "no", "0"}:
        return "none"
    return np.nan


def _normalize_nap(value: Any) -> str | float:
    if pd.isna(value):
        return np.nan
    text = str(value).strip().lower()
    if text in MISSING_TOKENS:
        return np.nan
    if text in {"yes", "true", "1"}:
        return "yes"
    if text in {"no", "false", "0"}:
        return "no"
    return np.nan


def _sleep_quality(value: Any) -> tuple[float, str]:
    """Parse ratings and map the four written labels to transparent ordinal anchors."""
    if pd.isna(value):
        return np.nan, "missing"
    text = str(value).strip().lower()
    if text in MISSING_TOKENS:
        return np.nan, "missing"
    try:
        parsed = float(text)
        return (parsed if 1 <= parsed <= 10 else np.nan), "numeric"
    except ValueError:
        labels = {"bad": 3.0, "medium": 5.0, "good": 7.0}
        return labels.get(text, np.nan), "label_mapped" if text in labels else "invalid"


def clean_sleep_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Return a cleaned, analysis-ready frame and an auditable transformation summary."""
    data = standardize_columns(raw)
    data.insert(0, "source_row", np.arange(2, len(data) + 2))
    data["participant_id"] = data["participant_id"].astype("string").str.strip().replace("", pd.NA)
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["study_day"] = _numeric(data["study_day"])

    for column in NUMERIC_COLUMNS:
        data[column] = _numeric(data[column])

    data["screen_time_before_bed_min"], data["screen_time_ambiguous"] = zip(
        *data["screen_time_raw"].map(parse_screen_time)
    )
    data["sleep_duration_hours"] = _numeric(data["sleep_duration_raw"])
    data["resting_heart_rate_bpm"] = _numeric(data["resting_heart_rate_raw"])
    data["stress_numeric"] = _numeric(data["stress_level_raw"])
    data["exercise_intensity"] = data["exercise_intensity_raw"].map(_normalize_exercise)
    data["nap"] = data["nap_raw"].map(_normalize_nap)

    quality_parsed = data["sleep_quality_raw"].map(_sleep_quality)
    data["sleep_quality"] = quality_parsed.map(lambda pair: pair[0])
    data["sleep_quality_source"] = quality_parsed.map(lambda pair: pair[1])

    for source, target in [
        ("last_caffeine_time_raw", "last_caffeine_hour"),
        ("last_meal_time_raw", "last_meal_hour"),
        ("planned_bedtime_raw", "planned_bedtime_clock_hour"),
        ("actual_bedtime_raw", "actual_bedtime_clock_hour"),
        ("wake_time_raw", "wake_hour"),
    ]:
        data[target] = data[source].map(parse_clock_time)

    planned_normalized = data["planned_bedtime_clock_hour"].map(normalize_bedtime)
    actual_normalized = data["actual_bedtime_clock_hour"].map(normalize_bedtime)
    data["planned_bedtime_hour"] = planned_normalized.map(lambda pair: pair[0])
    data["actual_bedtime_hour"] = actual_normalized.map(lambda pair: pair[0])
    data["planned_bedtime_meridiem_corrected"] = planned_normalized.map(lambda pair: pair[1])
    data["actual_bedtime_meridiem_corrected"] = actual_normalized.map(lambda pair: pair[1])
    data["time_in_bed_hours"] = [
        overnight_duration_hours(bed, wake)
        for bed, wake in zip(data["actual_bedtime_hour"], data["wake_hour"], strict=True)
    ]
    data["bedtime_vs_plan_minutes"] = [
        circular_difference_hours(actual, planned) * 60
        for actual, planned in zip(
            data["actual_bedtime_hour"], data["planned_bedtime_hour"], strict=True
        )
    ]
    data["caffeine_to_planned_bedtime_hours"] = [
        (planned - caffeine) % 24 if not pd.isna(planned) and not pd.isna(caffeine) else np.nan
        for planned, caffeine in zip(
            data["planned_bedtime_hour"], data["last_caffeine_hour"], strict=True
        )
    ]
    data["meal_to_planned_bedtime_hours"] = [
        (planned - meal) % 24 if not pd.isna(planned) and not pd.isna(meal) else np.nan
        for planned, meal in zip(
            data["planned_bedtime_hour"], data["last_meal_hour"], strict=True
        )
    ]

    data["weekend"] = data["date"].dt.dayofweek.ge(5)
    data["day_of_week"] = data["date"].dt.day_name().str.lower()
    data["total_academic_hours"] = data["study_hours"] + data["class_hours"]
    data["nap_occurred"] = np.nan
    data.loc[data["nap"].eq("yes").fillna(False), "nap_occurred"] = 1.0
    data.loc[data["nap"].eq("no").fillna(False), "nap_occurred"] = 0.0

    data["study_day_out_of_range"] = ~data["study_day"].between(1, 14)
    data["sleep_quality_invalid"] = data["sleep_quality"].isna()
    data["time_in_bed_implausible"] = ~data["time_in_bed_hours"].between(2, 16)
    data["screen_time_out_of_range"] = ~data["screen_time_before_bed_min"].between(0, 60)
    data["stress_outside_expected_1_to_5"] = ~data["stress_numeric"].between(1, 5)
    data.loc[data["stress_numeric"].isna(), "stress_outside_expected_1_to_5"] = False
    data["nap_logic_inconsistent"] = (
        ((data["nap"] == "no") & data["nap_minutes"].gt(0))
        | ((data["nap"] == "yes") & data["nap_minutes"].eq(0))
    )
    data["exercise_logic_inconsistent"] = (
        (data["exercise_minutes"].eq(0) & data["exercise_intensity"].isin(["medium", "high"]))
        | (data["exercise_minutes"].gt(0) & data["exercise_intensity"].eq("none"))
    )
    data["caffeine_time_inconsistent"] = (
        (data["caffeine_servings"].gt(0) & data["last_caffeine_hour"].isna())
        | (data["caffeine_servings"].eq(0) & data["last_caffeine_hour"].notna())
    )
    data["duplicate_participant_date"] = data.duplicated(["participant_id", "date"], keep=False)
    data.loc[data["participant_id"].isna() | data["date"].isna(), "duplicate_participant_date"] = False
    data["prediction_eligible"] = (
        data["participant_id"].notna()
        & data["date"].notna()
        & data["study_day"].between(1, 14)
        & data["sleep_quality"].notna()
        & ~data["duplicate_participant_date"]
    )

    audit = {
        "input_rows": int(len(raw)),
        "rows_with_known_participant": int(data["participant_id"].notna().sum()),
        "rows_with_mapped_sleep_quality": int(data["sleep_quality_source"].eq("label_mapped").sum()),
        "ambiguous_screen_entries": int(data["screen_time_ambiguous"].sum()),
        "bedtime_meridiem_corrections": int(
            data["planned_bedtime_meridiem_corrected"].sum()
            + data["actual_bedtime_meridiem_corrected"].sum()
        ),
        "out_of_range_study_days": int(data["study_day_out_of_range"].sum()),
        "duplicate_participant_date_rows": int(data["duplicate_participant_date"].sum()),
        "prediction_eligible_rows": int(data["prediction_eligible"].sum()),
    }
    return data, audit
