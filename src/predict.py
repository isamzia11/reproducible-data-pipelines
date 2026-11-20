# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 20, 2026


"""Predict inspection outcomes using a saved ML pipeline."""

import argparse
from pathlib import Path

import joblib
import pandas as pd

from src.features import INPUT_COLUMNS, prepare_features


def predict_file(input_path, output_path, model_path):
    """Load new records, predict outcomes and save a CSV."""

    input_path = Path(input_path)
    output_path = Path(output_path)
    model_path = Path(model_path)

    if not input_path.is_file():
        raise FileNotFoundError(
            f"Input CSV not found: {input_path}"
        )

    if not model_path.is_file():
        raise FileNotFoundError(
            f"Saved model not found: {model_path}"
        )

    # Read new inspection records.
    new_data = pd.read_csv(input_path)

    if new_data.empty:
        raise ValueError("Input CSV contains no records.")

    # Require all input columns.
    missing = []

    for column in INPUT_COLUMNS:
        if column not in new_data.columns:
            missing.append(column)

    if missing:
        raise ValueError(
            f"Missing prediction columns: {missing}"
        )

    # Prevent accidental use of known outcomes.
    if "results" in new_data.columns:
        raise ValueError(
            "Remove the results column from inference input."
        )

    # Apply only deterministic feature engineering.
    features = prepare_features(new_data)

    # Load the complete fitted preprocessing + model pipeline.
    model = joblib.load(model_path)

    predictions = model.predict(features)

    # Identify the probability column representing Fail.
    classes = list(model.named_steps["classifier"].classes_)
    fail_column = classes.index(1)

    probabilities = model.predict_proba(features)[:, fail_column]

    # Preserve the original supplied input columns.
    output = new_data.copy()

    output["predicted_label"] = predictions

    output["predicted_result"] = output[
        "predicted_label"
    ].map(
        {
            0: "Pass",
            1: "Fail",
        }
    )

    output["failure_probability"] = probabilities

    # Create the output directory if necessary.
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output.to_csv(output_path, index=False)

    return output


def main():
    """Read command-line arguments and run inference."""

    parser = argparse.ArgumentParser(
        description="Predict Chicago food inspection outcomes."
    )

    parser.add_argument(
        "input_csv",
        help="Path to CSV containing new inspection records."
    )

    parser.add_argument(
        "output_csv",
        help="Path where predictions will be saved."
    )

    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent

    model_path = root / "outputs/models/best_pipeline.joblib"

    predictions = predict_file(
        args.input_csv,
        args.output_csv,
        model_path,
    )

    print("Predictions saved successfully.")
    print(predictions)


if __name__ == "__main__":
    main()
