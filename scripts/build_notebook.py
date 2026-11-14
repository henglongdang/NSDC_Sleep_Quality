"""Create the NSDC notebook from the reusable analysis pipeline and aggregate outputs."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "NSDC_Sleep_Analysis.ipynb"


def markdown(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


def main() -> None:
    notebook = nbf.v4.new_notebook()
    notebook.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    }
    notebook.cells = [
        markdown(
            """
            # NSDC Sleep Quality Analysis

            ## Can daily routines predict sleep quality tonight?

            This notebook runs the reusable pipeline and presents the findings. The central question is whether a student's day-to-day deviation from their usual routine adds useful predictive information beyond their sleep history.

            The data are observational and self-reported. All statements below describe associations or forecasting performance, not causal effects.
            """
        ),
        code(
            """
            import importlib
            import sys
            from pathlib import Path

            import pandas as pd
            from IPython.display import Image, display

            PROJECT_ROOT = Path.cwd().resolve()
            if not (PROJECT_ROOT / "src").exists():
                PROJECT_ROOT = PROJECT_ROOT.parent
            sys.path.insert(0, str(PROJECT_ROOT / "src"))

            run = importlib.import_module("sleep_analysis.run_analysis").run

            results = run(PROJECT_ROOT, PROJECT_ROOT / "config" / "config.yaml")
            TABLES = PROJECT_ROOT / "reports" / "tables"
            FIGURES = PROJECT_ROOT / "reports" / "figures"
            pd.set_option("display.float_format", lambda value: f"{value:,.3f}")
            """
        ),
        markdown(
            """
            ## Dataset and data quality

            The source workbook has 632 rows and 22 expected fields. The primary prospective subset has known participant IDs, valid study-day values, an observed target, and no repeated participant-date pair. It is an analytical subset, not a replacement for the source data.
            """
        ),
        code(
            """
            display(pd.read_csv(TABLES / "dataset_summary.csv").T.rename(columns={0: "value"}))
            display(pd.read_csv(TABLES / "quality_flags.csv"))
            display(Image(filename=str(FIGURES / "01_missingness.png")))
            """
        ),
        markdown(
            """
            ## Sleep-quality distribution

            Sleep quality is a bounded self-reported outcome. The distribution and participant-level averages show why a single pooled mean cannot fully represent every participant.
            """
        ),
        code(
            """
            display(pd.read_csv(TABLES / "target_descriptives.csv").T.rename(columns={0: "value"}))
            display(pd.read_csv(TABLES / "sleep_quality_distribution.csv"))
            display(Image(filename=str(FIGURES / "02_sleep_quality_distribution.png")))
            """
        ),
        markdown(
            """
            ## Routine relationships and temporal patterns

            Pooled relationships provide a starting point, but repeated measurements require caution. The association table includes sample sizes and Benjamini-Hochberg adjusted p-values for the defined family of correlations.
            """
        ),
        code(
            """
            display(pd.read_csv(TABLES / "spearman_associations.csv").round(3))
            display(Image(filename=str(FIGURES / "03_behavior_relationships.png")))
            display(Image(filename=str(FIGURES / "05_temporal_pattern.png")))
            """
        ),
        markdown(
            """
            ## Within-person versus between-person stress

            This retrospective model distinguishes a day's stress relative to the participant's own average from a student's typical stress relative to other participants. It uses participant-clustered standard errors. The result is inconclusive, so the notebook does not turn the weak pooled stress association into a behavioral claim.
            """
        ),
        code(
            """
            display(pd.read_csv(TABLES / "stress_mixed_model.csv").round(3))
            print("Sleep-quality ICC:", results["icc"])
            display(Image(filename=str(FIGURES / "04_within_between_stress.png")))
            """
        ),
        markdown(
            """
            ## Prediction design

            The pipeline evaluates two different settings. GroupKFold holds out whole students and only uses target-night pre-sleep routines. Chronological forecasting holds out each known student's later records and permits only prior, shifted history. Current-night outcomes are prohibited by code-level leakage checks.
            """
        ),
        code(
            """
            comparison = pd.read_csv(TABLES / "model_comparison.csv")
            display(comparison.round(3))
            display(Image(filename=str(FIGURES / "06_model_comparison.png")))
            """
        ),
        markdown(
            """
            ## Model interpretation and diagnostics

            The best later-night forecast is only narrowly better than previous-night sleep quality. Feature importance is evaluated on held-out records. It identifies predictive contribution in this model, not a causal mechanism.
            """
        ),
        code(
            """
            display(pd.read_csv(TABLES / "permutation_importance.csv").head(10).round(3))
            print("Target-permutation check:", results["permutation_leakage_check"])
            print("Numeric-outcome sensitivity:", results["numeric_target_sensitivity"])
            display(Image(filename=str(FIGURES / "07_final_model_predictions.png")))
            display(Image(filename=str(FIGURES / "08_feature_importance.png")))
            """
        ),
        markdown(
            """
            ## Wearable subset

            Wearable values were optional. The table and figure describe only participants with observed wearable sleep duration, not the entire sample.
            """
        ),
        code(
            """
            display(pd.read_csv(TABLES / "wearable_summary.csv").round(3))
            display(Image(filename=str(FIGURES / "09_wearable_sleep_duration.png")))
            """
        ),
        markdown(
            """
            ## Conclusion

            The strongest evidence supports individualized forecasting from earlier sleep history. Daytime routine models did not improve prediction for unseen students. The study does not show that changing any logged behavior will cause a change in sleep quality. See `reports/final_report.md` and `docs/LIMITATIONS.md` for the full interpretation.
            """
        ),
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
