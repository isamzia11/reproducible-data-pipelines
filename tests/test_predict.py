# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 20, 2026

"""Tests for saved-model inference."""

import joblib
import pandas as pd
import pytest

from src.features import prepare_features
from src.predict import predict_file
from src.train import build_models


def test_predict_file(tmp_path):
    """Check that saved-model inference writes predictions."""

    historical = pd.DataFrame(
        {
            "risk": [
                "Risk 1 (High)",
                "Risk 2 (Medium)",
                "Risk 1 (High)",
                "Risk 3 (Low)",
            ],
            "facility_type": [
                "Restaurant",
                "Bakery",
                "Restaurant",
                "Grocery Store",
            ],
            "latitude": [41.8, 41.9, 41.85, 41.88],
            "longitude": [-87.6, -87.7, -87.65, -87.66],
            "inspection_date": [
                "2022-01-01",
                "2022-02-01",
                "2022-03-01",
                "2022-04-01",
            ],
        }
    )

    labels = [0, 1, 0, 1]

    # Fit a tiny baseline for a fast inference test.
    model = build_models()["Dummy Baseline"]

    model.fit(prepare_features(historical), labels)

    model_path = tmp_path / "test_model.joblib"

    joblib.dump(model, model_path)

    # Prepare one new record.
    new_data = historical.iloc[[0]].copy()
    new_data["inspection_date"] = "2024-01-10"

    input_path = tmp_path / "new.csv"
    output_path = tmp_path / "predictions.csv"

    new_data.to_csv(input_path, index=False)

    result = predict_file(
        input_path,
        output_path,
        model_path,
    )

    assert output_path.is_file()
    assert len(result) == 1
    assert "predicted_result" in result.columns
    assert "failure_probability" in result.columns


def test_missing_inference_column(tmp_path):
    """Check that incomplete prediction input is rejected."""

    data = pd.DataFrame(
        {
            "risk": ["Risk 1 (High)"],
            "inspection_date": ["2024-01-10"],
        }
    )

    input_path = tmp_path / "incomplete.csv"
    model_path = tmp_path / "placeholder.joblib"

    data.to_csv(input_path, index=False)
    model_path.write_bytes(b"placeholder")

    with pytest.raises(ValueError):
        predict_file(
            input_path,
            tmp_path / "output.csv",
            model_path,
        )
