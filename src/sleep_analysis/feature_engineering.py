"""Leakage-aware temporal and participant-specific feature construction."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from sleep_analysis.validation import circular_difference_hours

BEHAVIOR_COLUMNS = [
    "stress_numeric",
    "caffeine_servings",
    "exercise_minutes",
    "screen_time_before_bed_min",
    "total_academic_hours",
    "nap_minutes",
    "caffeine_to_planned_bedtime_hours",
]


def _prior_expanding_mean(series: pd.Series) -> pd.Series:
    return series.shift(1).expanding(min_periods=1).mean()


def _prior_expanding_std(series: pd.Series) -> pd.Series:
    return series.shift(1).expanding(min_periods=2).std(ddof=1)


def _retrospective_zscore(series: pd.Series) -> pd.Series:
    mean = series.mean()
    std = series.std(ddof=1)
    if pd.isna(std) or std == 0:
        return pd.Series(np.nan, index=series.index, dtype=float)
    return (series - mean) / std


def _prior_circular_mean_hour(series: pd.Series) -> pd.Series:
    angle = 2 * np.pi * series / 24
    sin_sum = np.sin(angle).shift(1).expanding(min_periods=1).sum()
    cos_sum = np.cos(angle).shift(1).expanding(min_periods=1).sum()
    mean_angle = np.arctan2(sin_sum, cos_sum)
    return (mean_angle % (2 * np.pi)) * 24 / (2 * np.pi)


def add_features(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Add features using only a participant's earlier observations for prediction.

    The input frame remains intact. Grouped operations run after chronological sorting and
    all historical values are shifted by one row, preventing same-day or future leakage.
    """
    data = cleaned.copy()
    data = data.sort_values(["participant_id", "date", "source_row"], na_position="last").reset_index(
        drop=True
    )
    data["planned_bedtime_sin"] = np.sin(2 * np.pi * data["planned_bedtime_hour"] / 24)
    data["planned_bedtime_cos"] = np.cos(2 * np.pi * data["planned_bedtime_hour"] / 24)
    data["late_caffeine_within_6h"] = np.nan
    no_caffeine = data["caffeine_servings"].eq(0).fillna(False)
    late_caffeine = (
        data["caffeine_servings"].gt(0).fillna(False)
        & data["caffeine_to_planned_bedtime_hours"].lt(6).fillna(False)
    )
    data.loc[no_caffeine, "late_caffeine_within_6h"] = 0.0
    data.loc[late_caffeine, "late_caffeine_within_6h"] = 1.0

    grouped = data.groupby("participant_id", group_keys=False, dropna=False)
    previous_date = grouped["date"].shift(1)
    data["previous_observation_consecutive"] = data["date"].sub(previous_date).dt.days.eq(1)

    for source, target in [
        ("sleep_quality", "previous_sleep_quality"),
        ("sleep_duration_hours", "previous_sleep_duration_hours"),
        ("time_in_bed_hours", "previous_time_in_bed_hours"),
        ("actual_bedtime_hour", "previous_actual_bedtime_hour"),
        ("wake_hour", "previous_wake_hour"),
    ]:
        data[target] = grouped[source].shift(1)
        data.loc[~data["previous_observation_consecutive"], target] = np.nan

    data["prior_sleep_quality_mean"] = grouped["sleep_quality"].transform(_prior_expanding_mean)
    data["prior_sleep_quality_sd"] = grouped["sleep_quality"].transform(_prior_expanding_std)
    data["prior_3day_sleep_quality_mean"] = grouped["sleep_quality"].transform(
        lambda series: series.shift(1).rolling(3, min_periods=1).mean()
    )
    data["prior_planned_bedtime_hour"] = grouped["planned_bedtime_hour"].transform(
        _prior_circular_mean_hour
    )
    data["planned_bedtime_deviation_minutes"] = [
        circular_difference_hours(current, prior) * 60
        for current, prior in zip(
            data["planned_bedtime_hour"], data["prior_planned_bedtime_hour"], strict=True
        )
    ]

    for column in BEHAVIOR_COLUMNS:
        prior_mean = f"prior_{column}_mean"
        prior_std = f"prior_{column}_sd"
        deviation = f"{column}_deviation_prior"
        zscore = f"{column}_z_prior"
        data[prior_mean] = grouped[column].transform(_prior_expanding_mean)
        data[prior_std] = grouped[column].transform(_prior_expanding_std)
        data[deviation] = data[column] - data[prior_mean]
        data[zscore] = data[deviation] / data[prior_std]
        data.loc[data[prior_std].le(0), zscore] = np.nan

        retrospective_mean = f"retrospective_{column}_mean"
        data[retrospective_mean] = grouped[column].transform("mean")
        data[f"{column}_within_person_z"] = grouped[column].transform(_retrospective_zscore)

    data["retrospective_sleep_quality_mean"] = grouped["sleep_quality"].transform("mean")
    data["day_of_week"] = data["day_of_week"].astype("string")
    return data


def prediction_frame(features: pd.DataFrame) -> pd.DataFrame:
    """Select records suitable for the primary prospective prediction setting."""
    return features.loc[features["prediction_eligible"]].copy()


def feature_sets() -> dict[str, list[str]]:
    """Model feature blocks, grouped to test incremental predictive value."""
    calendar = ["study_day", "weekend", "day_of_week"]
    routines = calendar + [
        "planned_bedtime_sin",
        "planned_bedtime_cos",
        "meal_to_planned_bedtime_hours",
    ]
    sleep_history = routines + [
        "previous_sleep_quality",
        "previous_sleep_duration_hours",
        "previous_time_in_bed_hours",
        "prior_sleep_quality_mean",
        "prior_3day_sleep_quality_mean",
        "planned_bedtime_deviation_minutes",
    ]
    daytime_behaviors = sleep_history + [
        "caffeine_servings",
        "caffeine_to_planned_bedtime_hours",
        "late_caffeine_within_6h",
        "exercise_minutes",
        "exercise_intensity",
        "screen_time_before_bed_min",
        "total_academic_hours",
        "nap_occurred",
        "nap_minutes",
        "stress_numeric",
    ]
    personalized = daytime_behaviors + [
        "stress_numeric_z_prior",
        "caffeine_servings_z_prior",
        "exercise_minutes_z_prior",
        "screen_time_before_bed_min_z_prior",
        "total_academic_hours_z_prior",
        "nap_minutes_z_prior",
        "caffeine_to_planned_bedtime_hours_z_prior",
    ]
    unseen_daytime = calendar + [
        "planned_bedtime_sin",
        "planned_bedtime_cos",
        "meal_to_planned_bedtime_hours",
        "caffeine_servings",
        "caffeine_to_planned_bedtime_hours",
        "late_caffeine_within_6h",
        "exercise_minutes",
        "exercise_intensity",
        "screen_time_before_bed_min",
        "total_academic_hours",
        "nap_occurred",
        "nap_minutes",
        "stress_numeric",
    ]
    return {
        "unseen_daytime": unseen_daytime,
        "sleep_history": sleep_history,
        "daytime_behaviors": daytime_behaviors,
        "personalized": personalized,
    }


def assert_no_current_night_outcomes(columns: Iterable[str]) -> None:
    """Fail loudly if prohibited current-night outcome fields enter model features."""
    prohibited = {
        "actual_bedtime_hour",
        "wake_hour",
        "sleep_quality",
        "times_woken",
        "sleep_duration_hours",
        "resting_heart_rate_bpm",
        "hrv_ms",
        "time_in_bed_hours",
        "bedtime_vs_plan_minutes",
    }
    overlap = prohibited.intersection(columns)
    if overlap:
        raise ValueError(f"Current-night outcomes cannot be predictive features: {sorted(overlap)}")
