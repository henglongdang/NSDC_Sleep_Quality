"""Validation and time-parsing helpers used by cleaning and tests."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any

import numpy as np
import pandas as pd

MISSING_TOKENS = {"", "na", "n/a", "nan", "none", "null", "missing", "-"}


def parse_clock_time(value: Any) -> float:
    """Return decimal clock hours in [0, 24), or NaN for absent or invalid input."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, time):
        return value.hour + value.minute / 60 + value.second / 3600
    if isinstance(value, datetime):
        return value.hour + value.minute / 60 + value.second / 3600
    if isinstance(value, (int, float, np.number)):
        numeric = float(value)
        if 0 <= numeric < 1:
            return numeric * 24
        if 0 <= numeric < 24 and numeric.is_integer():
            return numeric
        return np.nan

    text = str(value).strip().lower()
    if text in MISSING_TOKENS:
        return np.nan
    for fmt in ("%H:%M", "%H:%M:%S", "%H"):
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.hour + parsed.minute / 60 + parsed.second / 3600
        except ValueError:
            continue
    return np.nan


def normalize_bedtime(clock_hour: float) -> tuple[float, bool]:
    """Resolve likely 12-hour bedtime entries while retaining an audit flag.

    Bedtimes entered as 8:00 through 11:59 are interpreted as evening times.
    Entries at 12:00 through 12:59 are interpreted as midnight times. This narrow
    rule handles implausible morning/noon bedtimes without changing 00:00--07:59.
    """
    if pd.isna(clock_hour):
        return np.nan, False
    if 8 <= clock_hour < 12:
        return clock_hour + 12, True
    if 12 <= clock_hour < 13:
        return clock_hour - 12, True
    return float(clock_hour), False


def overnight_duration_hours(bedtime_hour: float, wake_hour: float) -> float:
    """Compute a wake-after-bed interval across midnight without naive subtraction."""
    if pd.isna(bedtime_hour) or pd.isna(wake_hour):
        return np.nan
    duration = (float(wake_hour) - float(bedtime_hour)) % 24
    return np.nan if duration == 0 else duration


def circular_difference_hours(observed: float, reference: float) -> float:
    """Signed shortest-path difference on a 24-hour clock."""
    if pd.isna(observed) or pd.isna(reference):
        return np.nan
    return ((float(observed) - float(reference) + 12) % 24) - 12


def parse_screen_time(value: Any) -> tuple[float, bool]:
    """Parse a screen-time entry, flagging slash-delimited ranges as ambiguous.

    For entries such as ``50 / 60``, the midpoint is used only after preserving an
    ambiguity flag. Non-numeric text is left missing rather than guessed.
    """
    if pd.isna(value):
        return np.nan, False
    text = str(value).strip().lower()
    if text in MISSING_TOKENS:
        return np.nan, False
    if "/" in text:
        pieces = text.replace(" ", "").split("/")
        try:
            values = [float(piece) for piece in pieces]
        except ValueError:
            return np.nan, True
        return float(np.mean(values)), True
    try:
        return float(text), False
    except ValueError:
        return np.nan, False


def validate_raw_structure(frame: pd.DataFrame) -> dict[str, int | float]:
    """Return compact structural checks before any cleaning transformation."""
    id_column = "Participant Anonymised ID"
    date_column = "Date"
    day_column = "Day of the Study (Day 1, 2)"
    known_id = frame[id_column].notna()
    return {
        "rows": int(len(frame)),
        "columns": int(frame.shape[1]),
        "unique_participants_known_id": int(frame.loc[known_id, id_column].nunique()),
        "rows_without_participant_id": int((~known_id).sum()),
        "complete_duplicate_rows": int(frame.duplicated().sum()),
        "duplicate_participant_date_known_id": int(
            frame.loc[known_id].duplicated([id_column, date_column]).sum()
        ),
        "duplicate_participant_study_day_known_id": int(
            frame.loc[known_id].duplicated([id_column, day_column]).sum()
        ),
        "missing_cells": int(frame.isna().sum().sum()),
    }
