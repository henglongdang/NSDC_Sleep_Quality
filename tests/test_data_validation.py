from __future__ import annotations

import pytest

from sleep_analysis.data_loading import EXPECTED_COLUMNS, load_raw_data, standardize_columns
from sleep_analysis.validation import validate_raw_structure


def test_loads_supplied_workbook() -> None:
    frame = load_raw_data("data/raw/openProj_masterF26.xlsx")
    assert frame.shape == (632, 22)
    assert list(frame.columns) == EXPECTED_COLUMNS
    assert validate_raw_structure(frame)["rows"] == 632


def test_missing_file_has_clear_error() -> None:
    with pytest.raises(FileNotFoundError, match="Raw data file not found"):
        load_raw_data("data/raw/not_present.xlsx")


def test_standardization_rejects_missing_expected_field(raw_rows) -> None:
    frame = raw_rows([{}]).drop(columns="Sleep Quality")
    with pytest.raises(ValueError, match="missing expected columns"):
        standardize_columns(frame)
