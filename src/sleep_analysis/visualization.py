"""Publication-quality figures with consistent, accessible styling."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PALETTE = {
    "navy": "#1f3b5b",
    "blue": "#3f78a8",
    "teal": "#208c8c",
    "orange": "#dd7a2b",
    "red": "#c84d4d",
    "gray": "#718096",
    "light": "#edf2f7",
}


def configure_style() -> None:
    sns.set_theme(style="whitegrid", context="notebook", font_scale=1.05)
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "axes.titleweight": "bold",
            "axes.labelcolor": "#233042",
            "xtick.color": "#4a5568",
            "ytick.color": "#4a5568",
            "figure.facecolor": "white",
        }
    )


def _save(figure: plt.Figure, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    figure.savefig(destination, bbox_inches="tight")
    plt.close(figure)


def plot_missingness(data: pd.DataFrame, destination: Path) -> None:
    missing = (data.isna().mean().mul(100).sort_values(ascending=False).head(16)).sort_values()
    figure, axis = plt.subplots(figsize=(9, 7))
    axis.barh(missing.index.str.replace("_", " ").str.title(), missing, color=PALETTE["blue"])
    axis.set(xlabel="Missing values (%)", title="Missingness by analytical field")
    axis.set_xlim(0, max(10, missing.max() * 1.15))
    for index, value in enumerate(missing):
        axis.text(value + 0.8, index, f"{value:.0f}%", va="center", fontsize=9)
    _save(figure, destination)


def plot_sleep_quality(data: pd.DataFrame, destination: Path) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.25, 1]})
    sns.histplot(data=data, x="sleep_quality", discrete=True, color=PALETTE["navy"], ax=axes[0])
    axes[0].set(title="Sleep-quality ratings", xlabel="Sleep quality (1 to 10)", ylabel="Participant-days")
    participant = data.groupby("participant_id", as_index=False)["sleep_quality"].mean()
    sns.boxplot(data=participant, y="sleep_quality", color=PALETTE["teal"], width=0.45, ax=axes[1])
    sns.stripplot(data=participant, y="sleep_quality", color=PALETTE["navy"], alpha=0.55, size=4, ax=axes[1])
    axes[1].set(title="Participant average ratings", xlabel="", ylabel="Mean sleep quality")
    _save(figure, destination)


def plot_behavior_relationships(data: pd.DataFrame, destination: Path) -> None:
    fields = [
        ("stress_numeric", "Stress level"),
        ("caffeine_servings", "Caffeine servings"),
        ("screen_time_before_bed_min", "Screen time before bed (min)"),
        ("total_academic_hours", "Academic hours"),
    ]
    figure, axes = plt.subplots(2, 2, figsize=(11, 8))
    rng = np.random.default_rng(2026)
    for axis, (column, label) in zip(axes.flat, fields, strict=True):
        subset = data[[column, "sleep_quality"]].dropna()
        x = subset[column].to_numpy() + rng.normal(0, 0.04, len(subset))
        axis.scatter(x, subset["sleep_quality"], alpha=0.25, s=24, color=PALETTE["blue"])
        if subset[column].nunique() > 2:
            sns.regplot(
                data=subset,
                x=column,
                y="sleep_quality",
                scatter=False,
                ci=95,
                color=PALETTE["red"],
                line_kws={"linewidth": 2},
                ax=axis,
            )
        axis.set(title=f"{label} and sleep quality (n={len(subset)})", xlabel=label, ylabel="Sleep quality")
    _save(figure, destination)


def plot_within_between_stress(data: pd.DataFrame, destination: Path) -> None:
    person = (
        data.groupby("participant_id", as_index=False)
        .agg(mean_stress=("stress_numeric", "mean"), mean_sleep_quality=("sleep_quality", "mean"))
        .dropna()
    )
    within = data[["stress_numeric_within_person_z", "sleep_quality"]].dropna()
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    sns.regplot(
        data=person,
        x="mean_stress",
        y="mean_sleep_quality",
        scatter_kws={"alpha": 0.6, "color": PALETTE["navy"]},
        line_kws={"color": PALETTE["red"], "linewidth": 2},
        ax=axes[0],
    )
    axes[0].set(
        title=f"Between participants (n={len(person)})",
        xlabel="Participant average reported stress",
        ylabel="Participant average sleep quality",
    )
    sns.regplot(
        data=within,
        x="stress_numeric_within_person_z",
        y="sleep_quality",
        scatter_kws={"alpha": 0.17, "color": PALETTE["teal"]},
        line_kws={"color": PALETTE["red"], "linewidth": 2},
        ax=axes[1],
    )
    axes[1].set(
        title=f"Within participant-days (n={len(within)})",
        xlabel="Daily stress relative to personal average (SD units)",
        ylabel="Sleep quality",
    )
    figure.suptitle("Stress and sleep quality at two levels of analysis", y=1.02, fontsize=15, fontweight="bold")
    _save(figure, destination)


def plot_temporal_pattern(data: pd.DataFrame, destination: Path) -> None:
    summary = data.groupby("study_day", as_index=False).agg(
        mean_sleep_quality=("sleep_quality", "mean"), n=("sleep_quality", "count")
    )
    figure, axis = plt.subplots(figsize=(10, 4.8))
    axis.plot(summary["study_day"], summary["mean_sleep_quality"], marker="o", color=PALETTE["navy"], linewidth=2)
    for _, row in summary.iterrows():
        axis.annotate(f"n={int(row.n)}", (row.study_day, row.mean_sleep_quality), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=8, color=PALETTE["gray"])
    axis.set(
        title="Mean sleep quality across reported study days",
        xlabel="Study day",
        ylabel="Mean sleep quality",
        xticks=summary["study_day"],
    )
    _save(figure, destination)


def plot_model_comparison(metrics: pd.DataFrame, destination: Path) -> None:
    display = metrics.loc[metrics["scenario"].eq("Known-participant chronological forecast")].copy()
    display = display.sort_values("mae", ascending=True)
    figure, axis = plt.subplots(figsize=(10, 5.5))
    colors = [PALETTE["orange"] if "Extra Trees" in item else PALETTE["blue"] for item in display["model"]]
    axis.barh(display["model"], display["mae"], color=colors)
    for index, row in display.reset_index(drop=True).iterrows():
        axis.text(row.mae + 0.015, index, f"{row.mae:.2f}", va="center", fontsize=10)
    axis.set(title="Chronological forecasting error", xlabel="Mean absolute error in sleep-quality points", ylabel="")
    axis.set_xlim(0, display["mae"].max() * 1.18)
    _save(figure, destination)


def plot_predictions(scored: pd.DataFrame, destination: Path) -> None:
    figure, axis = plt.subplots(figsize=(6.5, 6))
    axis.scatter(scored["sleep_quality"], scored["prediction"], alpha=0.48, color=PALETTE["teal"], s=34)
    low = min(scored["sleep_quality"].min(), scored["prediction"].min()) - 0.3
    high = max(scored["sleep_quality"].max(), scored["prediction"].max()) + 0.3
    axis.plot([low, high], [low, high], linestyle="--", color=PALETTE["red"], linewidth=1.5, label="Perfect prediction")
    axis.set(
        title="Held-out predictions from the final model",
        xlabel="Observed sleep quality",
        ylabel="Predicted sleep quality",
        xlim=(low, high),
        ylim=(low, high),
    )
    axis.legend(frameon=False)
    _save(figure, destination)


def plot_feature_importance(importance: pd.DataFrame, destination: Path) -> None:
    display = importance.head(10).sort_values("mae_increase_mean")
    figure, axis = plt.subplots(figsize=(10, 5.5))
    axis.barh(
        display["feature"].str.replace("_", " "),
        display["mae_increase_mean"],
        xerr=display["mae_increase_sd"],
        color=PALETTE["navy"],
        capsize=3,
    )
    axis.set(
        title="Held-out permutation importance",
        xlabel="Increase in MAE after permuting the feature",
        ylabel="",
    )
    _save(figure, destination)


def plot_wearable_relationship(data: pd.DataFrame, destination: Path) -> None:
    subset = data[["sleep_duration_hours", "sleep_quality"]].dropna()
    figure, axis = plt.subplots(figsize=(7, 5))
    sns.regplot(
        data=subset,
        x="sleep_duration_hours",
        y="sleep_quality",
        scatter_kws={"alpha": 0.45, "color": PALETTE["blue"]},
        line_kws={"color": PALETTE["red"], "linewidth": 2},
        ax=axis,
    )
    axis.set(
        title=f"Wearable sleep duration and subjective sleep quality (n={len(subset)})",
        xlabel="Wearable sleep duration (hours)",
        ylabel="Sleep quality",
    )
    _save(figure, destination)
