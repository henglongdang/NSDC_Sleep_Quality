"""Compact descriptive summaries used in the report and notebook."""

from __future__ import annotations

import pandas as pd


def target_descriptives(data: pd.DataFrame) -> pd.DataFrame:
    """Summarize the primary ordinal outcome without treating rows as independent people."""
    target = data["sleep_quality"].dropna()
    return pd.DataFrame(
        [
            {
                "n": int(len(target)),
                "mean": target.mean(),
                "median": target.median(),
                "sd": target.std(ddof=1),
                "q1": target.quantile(0.25),
                "q3": target.quantile(0.75),
                "iqr": target.quantile(0.75) - target.quantile(0.25),
                "minimum": target.min(),
                "maximum": target.max(),
                "skewness": target.skew(),
            }
        ]
    )


def sleep_quality_distribution(data: pd.DataFrame) -> pd.DataFrame:
    """Return the observed frequency for each reported sleep-quality rating."""
    return (
        data["sleep_quality"]
        .value_counts(dropna=True)
        .sort_index()
        .rename_axis("sleep_quality")
        .rename("participant_days")
        .reset_index()
    )
