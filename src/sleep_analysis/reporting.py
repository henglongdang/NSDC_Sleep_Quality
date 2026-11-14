"""Small helpers for tabular analytical outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def save_table(frame: pd.DataFrame, destination: Path) -> None:
    """Write a UTF-8 CSV with a stable, named index policy."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False)


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value


def save_json(payload: dict[str, Any], destination: Path) -> None:
    """Save metrics in an inspectable, JSON-safe format."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(_json_safe(payload), indent=2), encoding="utf-8")
