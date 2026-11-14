from __future__ import annotations

import numpy as np
import pytest

from sleep_analysis.feature_engineering import assert_no_current_night_outcomes
from sleep_analysis.modeling import regression_metrics


def test_current_night_target_leakage_is_rejected() -> None:
    with pytest.raises(ValueError, match="Current-night outcomes"):
        assert_no_current_night_outcomes(["study_day", "sleep_duration_hours"])


def test_regression_metrics_reports_expected_values() -> None:
    metrics = regression_metrics(np.array([4.0, 6.0, 8.0]), np.array([5.0, 6.0, 7.0]))
    assert metrics["n"] == 3
    assert metrics["mae"] == pytest.approx(2 / 3)
    assert metrics["within_1"] == 1.0
