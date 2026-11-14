"""Run the full reproducible NSDC sleep analysis from the project root."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from sleep_analysis.cleaning import clean_sleep_data
from sleep_analysis.data_loading import load_raw_data
from sleep_analysis.eda import sleep_quality_distribution, target_descriptives
from sleep_analysis.feature_engineering import add_features, feature_sets, prediction_frame
from sleep_analysis.modeling import (
    chronological_evaluation,
    chronological_split,
    group_kfold_evaluation,
    historical_baseline,
    model_feature_importance,
    permutation_leakage_check,
    regression_metrics,
)
from sleep_analysis.reporting import save_json, save_table
from sleep_analysis.statistical_analysis import (
    intraclass_correlation,
    spearman_associations,
    stress_within_between_model,
    wearable_summary,
)
from sleep_analysis.validation import validate_raw_structure
from sleep_analysis.visualization import (
    configure_style,
    plot_behavior_relationships,
    plot_feature_importance,
    plot_missingness,
    plot_model_comparison,
    plot_predictions,
    plot_sleep_quality,
    plot_temporal_pattern,
    plot_wearable_relationship,
    plot_within_between_stress,
)


def _load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _model_record(name: str, scenario: str, metrics: dict) -> dict:
    return {"model": name, "scenario": scenario, **metrics}


def _global_mean_baseline(data: pd.DataFrame, split) -> tuple[dict, pd.DataFrame]:
    train = data.loc[split.train_index]
    test = data.loc[split.test_index]
    scored = test[["participant_id", "date", "study_day", "sleep_quality", "sleep_quality_source"]].copy()
    scored["prediction"] = train["sleep_quality"].mean()
    return regression_metrics(scored["sleep_quality"], scored["prediction"]), scored


def run(project_root: Path, config_path: Path) -> dict:
    """Execute cleaning, EDA outputs, statistics, predictive models, and diagnostics."""
    config = _load_config(config_path)
    paths = {key: project_root / value for key, value in config["paths"].items()}
    figures_dir = paths["figures"]
    tables_dir = paths["tables"]
    random_seed = config["analysis"]["random_seed"]

    print("Loading and cleaning data...", flush=True)
    raw = load_raw_data(paths["raw_data"])
    raw_validation = validate_raw_structure(raw)
    cleaned, cleaning_audit = clean_sleep_data(raw)
    featured = add_features(cleaned)
    prediction = prediction_frame(featured)
    paths["processed_data"].parent.mkdir(parents=True, exist_ok=True)
    featured.to_csv(paths["processed_data"], index=False)

    raw_missingness = (
        raw.isna()
        .sum()
        .rename("missing_count")
        .to_frame()
        .assign(missing_percent=lambda x: x["missing_count"] / len(raw) * 100)
        .rename_axis("source_column")
        .reset_index()
    )
    cleaned_missingness = (
        featured.isna()
        .sum()
        .rename("missing_count")
        .to_frame()
        .assign(missing_percent=lambda x: x["missing_count"] / len(featured) * 100)
        .rename_axis("analytical_column")
        .reset_index()
    )
    quality_flags = pd.DataFrame(
        {
            "flag": [
                "Study day outside 1-14",
                "Duplicate participant-date record",
                "Implausible time in bed (<2 or >16 hours)",
                "Screen time outside stated 0-60 range",
                "Stress outside stated 1-5 range",
                "Nap response inconsistent with nap minutes",
                "Exercise response inconsistent with duration",
                "Caffeine response inconsistent with time",
            ],
            "records_flagged": [
                int(featured["study_day_out_of_range"].sum()),
                int(featured["duplicate_participant_date"].sum()),
                int(featured["time_in_bed_implausible"].sum()),
                int(featured["screen_time_out_of_range"].sum()),
                int(featured["stress_outside_expected_1_to_5"].sum()),
                int(featured["nap_logic_inconsistent"].sum()),
                int(featured["exercise_logic_inconsistent"].sum()),
                int(featured["caffeine_time_inconsistent"].sum()),
            ],
        }
    )
    observation_distribution = (
        featured.loc[featured["participant_id"].notna()]
        .groupby("participant_id")
        .size()
        .value_counts()
        .sort_index()
        .rename_axis("observations_per_participant")
        .rename("participant_count")
        .reset_index()
    )
    dataset_summary = pd.DataFrame(
        [
            {
                "raw_rows": len(raw),
                "cleaned_rows": len(featured),
                "known_participants": featured["participant_id"].nunique(),
                "prediction_eligible_rows": len(prediction),
                "prediction_eligible_participants": prediction["participant_id"].nunique(),
                "mean_observations_per_known_participant": featured.groupby("participant_id").size().mean(),
                "wearable_sleep_duration_rows": featured["sleep_duration_hours"].notna().sum(),
                "resting_heart_rate_rows": featured["resting_heart_rate_bpm"].notna().sum(),
                "hrv_rows": featured["hrv_ms"].notna().sum(),
            }
        ]
    )
    save_table(raw_missingness, tables_dir / "raw_missingness.csv")
    save_table(cleaned_missingness, tables_dir / "cleaned_missingness.csv")
    save_table(quality_flags, tables_dir / "quality_flags.csv")
    save_table(observation_distribution, tables_dir / "observation_distribution.csv")
    save_table(dataset_summary, tables_dir / "dataset_summary.csv")
    save_table(target_descriptives(prediction), tables_dir / "target_descriptives.csv")
    save_table(sleep_quality_distribution(prediction), tables_dir / "sleep_quality_distribution.csv")

    print("Writing data-quality tables...", flush=True)
    associations = spearman_associations(prediction)
    icc = intraclass_correlation(prediction, seed=random_seed)
    stress_model = stress_within_between_model(prediction)
    wearables = wearable_summary(prediction)
    save_table(associations, tables_dir / "spearman_associations.csv")
    save_table(stress_model, tables_dir / "stress_mixed_model.csv")
    save_table(wearables, tables_dir / "wearable_summary.csv")

    print("Running repeated-measures statistics...", flush=True)
    sets = feature_sets()
    model_rows: list[dict] = []
    print("Evaluating unseen-participant models...", flush=True)
    scenario_a = "Unseen-participant group CV"
    for name, model_name in [
        ("Global mean baseline", "dummy"),
        ("Daytime Ridge", "ridge"),
        ("Daytime Extra Trees", "extra_trees"),
    ]:
        metrics, _ = group_kfold_evaluation(
            prediction, sets["unseen_daytime"], model_name, config["analysis"]["group_cv_splits"]
        )
        model_rows.append(_model_record(name, scenario_a, metrics))

    print("Evaluating chronological forecasts...", flush=True)
    split = chronological_split(prediction)
    scenario_b = "Known-participant chronological forecast"
    global_metrics, _ = _global_mean_baseline(prediction, split)
    model_rows.append(_model_record("Global mean baseline", scenario_b, global_metrics))
    prior_metrics, _ = historical_baseline(
        prediction, split, "previous_sleep_quality", "Previous-night sleep quality"
    )
    model_rows.append(_model_record("Previous-night sleep quality", scenario_b, prior_metrics))
    historical_metrics, _ = historical_baseline(
        prediction, split, "prior_sleep_quality_mean", "Prior participant mean"
    )
    model_rows.append(_model_record("Prior participant mean", scenario_b, historical_metrics))

    final_scored = pd.DataFrame()
    final_model = None
    for label, feature_key, model_name in [
        ("Sleep-history Ridge", "sleep_history", "ridge"),
        ("Behavioral Ridge", "daytime_behaviors", "ridge"),
        ("Personalized Ridge", "personalized", "ridge"),
        ("Personalized Extra Trees", "personalized", "extra_trees"),
    ]:
        metrics, scored, fitted = chronological_evaluation(prediction, sets[feature_key], model_name, split)
        model_rows.append(_model_record(label, scenario_b, metrics))
        if label == "Personalized Extra Trees":
            final_scored, final_model = scored, fitted
    model_metrics = pd.DataFrame(model_rows)
    save_table(model_metrics, tables_dir / "model_comparison.csv")
    save_table(final_scored, tables_dir / "final_model_predictions.csv")

    print("Running importance and leakage checks...", flush=True)
    importance = model_feature_importance(final_model, prediction.loc[split.test_index], sets["personalized"])
    save_table(importance, tables_dir / "permutation_importance.csv")
    permutation = permutation_leakage_check(prediction, sets["personalized"], split, n_permutations=5)
    numeric_only = final_scored.loc[final_scored["sleep_quality_source"].eq("numeric")]
    numeric_sensitivity = regression_metrics(numeric_only["sleep_quality"], numeric_only["prediction"])

    print("Rendering figures...", flush=True)
    configure_style()
    plot_missingness(featured, figures_dir / "01_missingness.png")
    plot_sleep_quality(prediction, figures_dir / "02_sleep_quality_distribution.png")
    plot_behavior_relationships(prediction, figures_dir / "03_behavior_relationships.png")
    plot_within_between_stress(prediction, figures_dir / "04_within_between_stress.png")
    plot_temporal_pattern(prediction, figures_dir / "05_temporal_pattern.png")
    plot_model_comparison(model_metrics, figures_dir / "06_model_comparison.png")
    plot_predictions(final_scored, figures_dir / "07_final_model_predictions.png")
    plot_feature_importance(importance, figures_dir / "08_feature_importance.png")
    plot_wearable_relationship(prediction, figures_dir / "09_wearable_sleep_duration.png")

    print("Saving final metrics...", flush=True)
    output = {
        "raw_validation": raw_validation,
        "cleaning_audit": cleaning_audit,
        "dataset_summary": dataset_summary.iloc[0].to_dict(),
        "icc": icc,
        "permutation_leakage_check": permutation,
        "numeric_target_sensitivity": numeric_sensitivity,
        "chronological_split": {
            "training_rows": int(len(split.train_index)),
            "test_rows": int(len(split.test_index)),
            "participants": int(split.participants),
        },
    }
    save_json(output, paths["metrics"])
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the NSDC sleep-quality analysis.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, default=Path("config/config.yaml"))
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    config_path = args.config if args.config.is_absolute() else project_root / args.config
    output = run(project_root, config_path)
    print("Analysis completed")
    print(f"Prediction-eligible records: {output['dataset_summary']['prediction_eligible_rows']}")
    print(f"Chronological test records: {output['chronological_split']['test_rows']}")


if __name__ == "__main__":
    main()
