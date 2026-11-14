from __future__ import annotations

import numpy as np

from sleep_analysis.validation import (
    circular_difference_hours,
    normalize_bedtime,
    overnight_duration_hours,
    parse_clock_time,
)


def test_time_parser_handles_before_and_after_midnight() -> None:
    assert parse_clock_time("23:30") == 23.5
    assert parse_clock_time("00:30") == 0.5
    assert np.isnan(parse_clock_time("not a time"))


def test_normalize_bedtime_and_overnight_duration() -> None:
    bedtime, corrected = normalize_bedtime(11.5)
    assert corrected and bedtime == 23.5
    assert overnight_duration_hours(23.5, 7.5) == 8
    assert overnight_duration_hours(0.5, 8.5) == 8


def test_circular_bedtime_difference_crosses_midnight() -> None:
    assert circular_difference_hours(0.5, 23.5) == 1
    assert circular_difference_hours(23.5, 0.5) == -1
