"""Leakage-resistant model evaluation for the two defined prediction scenarios."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from sleep_analysis.feature_engineering import assert_no_current_night_outcomes

RANDOM_SEED = 2026


@dataclass(frozen=True)
class ChronologicalSplit:
    """Row positions for a per-participant, earlier-to-later evaluation split."""

    train_index: np.ndarray
    test_index: np.ndarray
    participants: int


def regression_metrics(actual: pd.Series | np.ndarray, predicted: np.ndarray) -> dict[str, float | int]:
    """Metrics suited to a noisy 1--10 sleep-quality scale."""
    actual_array = np.asarray(actual, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)
    valid = np.isfinite(actual_array) & np.isfinite(predicted_array)
    actual_array = actual_array[valid]
    predicted_array = predicted_array[valid]
    if len(actual_array) == 0:
        return {key: np.nan for key in ["mae", "rmse", "r2", "median_ae", "spearman_r", "spearman_p", "within_1"]} | {"n": 0}
    if np.unique(actual_array).size < 2 or np.unique(predicted_array).size < 2:
        rho, rho_p = np.nan, np.nan
    else:
        rho, rho_p = spearmanr(actual_array, predicted_array)
    return {
        "n": int(len(actual_array)),
        "mae": float(mean_absolute_error(actual_array, predicted_array)),
        "rmse": float(np.sqrt(mean_squared_error(actual_array, predicted_array))),
        "r2": float(r2_score(actual_array, predicted_array)) if len(actual_array) > 1 else np.nan,
        "median_ae": float(median_absolute_error(actual_array, predicted_array)),
        "spearman_r": float(rho) if np.isfinite(rho) else np.nan,
        "spearman_p": float(rho_p) if np.isfinite(rho_p) else np.nan,
        "within_1": float(np.mean(np.abs(actual_array - predicted_array) <= 1)),
    }


def _column_groups(frame: pd.DataFrame) -> tuple[list[str], list[str]]:
    categorical = [
        column
        for column in frame.columns
        if pd.api.types.is_object_dtype(frame[column])
        or pd.api.types.is_string_dtype(frame[column])
        or pd.api.types.is_bool_dtype(frame[column])
    ]
    numeric = [column for column in frame.columns if column not in categorical]
    return numeric, categorical


def make_model(feature_frame: pd.DataFrame, model_name: str) -> Pipeline:
    """Build preprocessing inside the estimator so imputers never see held-out rows."""
    numeric, categorical = _column_groups(feature_frame)
    preprocess = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("impute", SimpleImputer(strategy="median", add_indicator=True)),
                        ("scale", StandardScaler()),
                    ]
                ),
                numeric,
            ),
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical,
            ),
        ],
        remainder="drop",
    )
    estimators = {
        "dummy": DummyRegressor(strategy="mean"),
        "ridge": Ridge(alpha=10.0),
        "extra_trees": ExtraTreesRegressor(
            n_estimators=50,
            min_samples_leaf=4,
            max_features=0.8,
            random_state=RANDOM_SEED,
            n_jobs=1,
        ),
    }
    if model_name not in estimators:
        raise ValueError(f"Unknown model: {model_name}")
    return Pipeline(steps=[("preprocess", preprocess), ("model", estimators[model_name])])


def group_kfold_evaluation(
    data: pd.DataFrame,
    features: list[str],
    model_name: str,
    n_splits: int = 5,
) -> tuple[dict[str, float | int], pd.DataFrame]:
    """Assess generalization to entirely held-out participants."""
    assert_no_current_night_outcomes(features)
    modeling_data = data.loc[data["sleep_quality"].notna()].copy()
    groups = modeling_data["participant_id"].astype(str)
    unique_groups = groups.nunique()
    if unique_groups < 2:
        raise ValueError("At least two participants are required for group validation.")
    splitter = GroupKFold(n_splits=min(n_splits, unique_groups))
    predictions = np.full(len(modeling_data), np.nan)
    folds = np.full(len(modeling_data), -1, dtype=int)
    x = modeling_data[features]
    y = modeling_data["sleep_quality"]
    for fold, (train, test) in enumerate(splitter.split(x, y, groups)):
        model = make_model(x.iloc[train], model_name)
        model.fit(x.iloc[train], y.iloc[train])
        predictions[test] = model.predict(x.iloc[test])
        folds[test] = fold + 1
    scored = modeling_data[["participant_id", "date", "sleep_quality"]].copy()
    scored["prediction"] = predictions
    scored["fold"] = folds
    return regression_metrics(scored["sleep_quality"], scored["prediction"]), scored


def chronological_split(data: pd.DataFrame, min_rows: int = 4) -> ChronologicalSplit:
    """Reserve each qualifying participant's latest 30% of records for forecasting."""
    train_rows: list[int] = []
    test_rows: list[int] = []
    included = 0
    for _, person in data.groupby("participant_id", sort=False):
        person = person.sort_values(["date", "source_row"])
        if len(person) < min_rows:
            continue
        cut = max(2, int(np.floor(len(person) * 0.7)))
        if cut >= len(person):
            continue
        train_rows.extend(person.index[:cut].tolist())
        test_rows.extend(person.index[cut:].tolist())
        included += 1
    if not test_rows:
        raise ValueError("No participant has enough records for chronological forecasting.")
    return ChronologicalSplit(np.array(train_rows), np.array(test_rows), included)


def chronological_evaluation(
    data: pd.DataFrame,
    features: list[str],
    model_name: str,
    split: ChronologicalSplit,
) -> tuple[dict[str, float | int], pd.DataFrame, Pipeline]:
    """Fit on earlier records and evaluate only on later records from known participants."""
    assert_no_current_night_outcomes(features)
    train = data.loc[split.train_index]
    test = data.loc[split.test_index]
    x_train, y_train = train[features], train["sleep_quality"]
    model = make_model(x_train, model_name)
    model.fit(x_train, y_train)
    scored = test[["participant_id", "date", "study_day", "sleep_quality", "sleep_quality_source"]].copy()
    scored["prediction"] = model.predict(test[features])
    return regression_metrics(scored["sleep_quality"], scored["prediction"]), scored, model


def historical_baseline(
    data: pd.DataFrame,
    split: ChronologicalSplit,
    column: str,
    label: str,
) -> tuple[dict[str, float | int], pd.DataFrame]:
    """Score a transparent historical predictor on the same later-period test rows."""
    test = data.loc[split.test_index]
    scored = test[["participant_id", "date", "study_day", "sleep_quality", "sleep_quality_source"]].copy()
    scored["prediction"] = test[column]
    metrics = regression_metrics(scored["sleep_quality"], scored["prediction"])
    metrics["model"] = label
    return metrics, scored


def permutation_leakage_check(
    data: pd.DataFrame,
    features: list[str],
    split: ChronologicalSplit,
    n_permutations: int = 20,
) -> dict[str, float | int]:
    """Check that a model cannot retain performance after target-label permutation."""
    train = data.loc[split.train_index]
    test = data.loc[split.test_index]
    generator = np.random.default_rng(RANDOM_SEED)
    maes: list[float] = []
    for _ in range(n_permutations):
        model = make_model(train[features], "extra_trees")
        shuffled = generator.permutation(train["sleep_quality"].to_numpy())
        model.fit(train[features], shuffled)
        maes.append(regression_metrics(test["sleep_quality"], model.predict(test[features]))["mae"])
    return {
        "permutations": n_permutations,
        "permuted_mae_mean": float(np.mean(maes)),
        "permuted_mae_sd": float(np.std(maes, ddof=1)) if len(maes) > 1 else 0.0,
    }


def model_feature_importance(
    model: Pipeline, test: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    """Use held-out permutation importance; importance does not imply causality."""
    result = permutation_importance(
        model,
        test[features],
        test["sleep_quality"],
        n_repeats=3,
        random_state=RANDOM_SEED,
        scoring="neg_mean_absolute_error",
        n_jobs=1,
    )
    return (
        pd.DataFrame(
            {
                "feature": features,
                "mae_increase_mean": result.importances_mean,
                "mae_increase_sd": result.importances_std,
            }
        )
        .sort_values("mae_increase_mean", ascending=False)
        .reset_index(drop=True)
    )
