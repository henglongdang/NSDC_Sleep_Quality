"""Repeated-measures descriptive and inferential analyses."""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr
from statsmodels.stats.multitest import multipletests


def spearman_associations(data: pd.DataFrame) -> pd.DataFrame:
    """Estimate target associations and control false discovery across this family."""
    candidates = {
        "Stress level": "stress_numeric",
        "Caffeine servings": "caffeine_servings",
        "Caffeine-to-bedtime hours": "caffeine_to_planned_bedtime_hours",
        "Exercise minutes": "exercise_minutes",
        "Screen time before bed": "screen_time_before_bed_min",
        "Total academic hours": "total_academic_hours",
        "Nap minutes": "nap_minutes",
        "Planned bedtime": "planned_bedtime_hour",
        "Prior sleep quality": "previous_sleep_quality",
        "Prior sleep duration": "previous_sleep_duration_hours",
    }
    rows: list[dict[str, float | int | str]] = []
    for label, column in candidates.items():
        subset = data[["sleep_quality", column]].dropna()
        if len(subset) < 10 or subset[column].nunique() < 2:
            continue
        rho, p_value = spearmanr(subset["sleep_quality"], subset[column])
        rows.append(
            {
                "predictor": label,
                "column": column,
                "n": int(len(subset)),
                "spearman_rho": float(rho),
                "p_value": float(p_value),
            }
        )
    result = pd.DataFrame(rows)
    if result.empty:
        return result
    result["p_value_fdr_bh"] = multipletests(result["p_value"], method="fdr_bh")[1]
    return result.sort_values("spearman_rho", key=lambda series: series.abs(), ascending=False).reset_index(
        drop=True
    )


def intraclass_correlation(data: pd.DataFrame, n_bootstrap: int = 500, seed: int = 2026) -> dict[str, float | int]:
    """Estimate one-way random-effects ICC for sleep quality with a participant bootstrap."""
    usable = data[["participant_id", "sleep_quality"]].dropna()

    def _icc(frame: pd.DataFrame) -> float:
        group_sizes = frame.groupby("participant_id").size()
        if len(group_sizes) < 2 or len(frame) <= len(group_sizes):
            return np.nan
        grand_mean = frame["sleep_quality"].mean()
        means = frame.groupby("participant_id")["sleep_quality"].mean()
        ms_between = (group_sizes * (means - grand_mean).pow(2)).sum() / (len(group_sizes) - 1)
        within_ss = frame.join(means.rename("group_mean"), on="participant_id").assign(
            squared=lambda x: (x["sleep_quality"] - x["group_mean"]).pow(2)
        )["squared"].sum()
        ms_within = within_ss / (len(frame) - len(group_sizes))
        effective_size = (len(frame) - (group_sizes.pow(2).sum() / len(frame))) / (len(group_sizes) - 1)
        return float((ms_between - ms_within) / (ms_between + (effective_size - 1) * ms_within))

    point = _icc(usable)
    group_summary = usable.groupby("participant_id")["sleep_quality"].agg(["count", "mean"])
    group_ss = usable.join(group_summary["mean"].rename("group_mean"), on="participant_id").assign(
        squared=lambda x: (x["sleep_quality"] - x["group_mean"]).pow(2)
    ).groupby("participant_id")["squared"].sum()
    counts = group_summary["count"].to_numpy(dtype=float)
    means = group_summary["mean"].to_numpy(dtype=float)
    within_ss = group_ss.reindex(group_summary.index).to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    estimates: list[float] = []
    for _ in range(n_bootstrap):
        sampled = rng.integers(0, len(counts), size=len(counts))
        sampled_counts = counts[sampled]
        sampled_means = means[sampled]
        total_rows = sampled_counts.sum()
        group_count = len(sampled_counts)
        grand_mean = np.average(sampled_means, weights=sampled_counts)
        ms_between = (
            sampled_counts * np.square(sampled_means - grand_mean)
        ).sum() / (group_count - 1)
        ms_within = within_ss[sampled].sum() / (total_rows - group_count)
        effective_size = (
            total_rows - np.square(sampled_counts).sum() / total_rows
        ) / (group_count - 1)
        value = (ms_between - ms_within) / (ms_between + (effective_size - 1) * ms_within)
        if np.isfinite(value):
            estimates.append(float(value))
    lower, upper = np.quantile(estimates, [0.025, 0.975]) if estimates else (np.nan, np.nan)
    return {
        "icc": float(point),
        "ci_low": float(lower),
        "ci_high": float(upper),
        "observations": int(len(usable)),
        "participants": int(usable["participant_id"].nunique()),
        "bootstrap_replicates": int(len(estimates)),
    }


def stress_within_between_model(data: pd.DataFrame) -> pd.DataFrame:
    """Separate daily stress deviations from typical stress with clustered uncertainty."""
    model_data = data[
        [
            "participant_id",
            "sleep_quality",
            "stress_numeric_within_person_z",
            "retrospective_stress_numeric_mean",
        ]
    ].dropna()
    if model_data["participant_id"].nunique() < 5 or len(model_data) < 30:
        return pd.DataFrame()
    participant_means = (
        model_data[["participant_id", "retrospective_stress_numeric_mean"]]
        .drop_duplicates()
        .set_index("participant_id")["retrospective_stress_numeric_mean"]
    )
    mean_center = participant_means.mean()
    mean_scale = participant_means.std(ddof=1)
    model_data = model_data.copy()
    model_data["stress_between_person_z"] = model_data["participant_id"].map(
        (participant_means - mean_center) / mean_scale
    )
    try:
        fitted = smf.ols(
            "sleep_quality ~ stress_numeric_within_person_z + stress_between_person_z",
            data=model_data,
        ).fit(cov_type="cluster", cov_kwds={"groups": model_data["participant_id"]})
        intervals = fitted.conf_int()
        terms = ["stress_numeric_within_person_z", "stress_between_person_z"]
        return pd.DataFrame(
            {
                "term": terms,
                "estimate": [float(fitted.params[term]) for term in terms],
                "ci_low": [float(intervals.loc[term, 0]) for term in terms],
                "ci_high": [float(intervals.loc[term, 1]) for term in terms],
                "p_value": [float(fitted.pvalues[term]) for term in terms],
                "observations": len(model_data),
                "participants": model_data["participant_id"].nunique(),
                "model": "OLS with participant-clustered standard errors",
            }
        )
    except (ValueError, np.linalg.LinAlgError):
        return pd.DataFrame()


def wearable_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Describe wearable measures only among rows where each measure exists."""
    measures = {
        "Wearable sleep duration (hours)": "sleep_duration_hours",
        "Resting heart rate (bpm)": "resting_heart_rate_bpm",
        "HRV (ms)": "hrv_ms",
    }
    rows: list[dict[str, float | int | str]] = []
    for label, column in measures.items():
        subset = data[["sleep_quality", column]].dropna()
        rho, p_value = (spearmanr(subset["sleep_quality"], subset[column]) if len(subset) >= 10 else (np.nan, np.nan))
        rows.append(
            {
                "measure": label,
                "n": int(len(subset)),
                "mean": float(subset[column].mean()) if len(subset) else np.nan,
                "sd": float(subset[column].std(ddof=1)) if len(subset) > 1 else np.nan,
                "sleep_quality_spearman_rho": float(rho) if np.isfinite(rho) else np.nan,
                "p_value": float(p_value) if np.isfinite(p_value) else np.nan,
            }
        )
    return pd.DataFrame(rows)
