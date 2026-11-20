# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 20, 2026


"""Tests for model pipeline construction."""

import pandas as pd

from src.train import build_models, build_preprocessor


def test_three_models_exist():
    """Check that the baseline and two candidates exist."""

    models = build_models()

    assert "Dummy Baseline" in models
    assert "Logistic Regression" in models
    assert "Random Forest" in models
    assert len(models) == 3


def test_pipeline_contains_preprocessing():
    """Check that each model includes the required pipeline."""

    models = build_models()

    for model in models.values():
        assert "preprocessor" in model.named_steps
        assert "classifier" in model.named_steps


def test_preprocessor_fits_on_training_data():
    """Check that the preprocessor handles missing coordinates."""

    X = pd.DataFrame(
        {
            "risk": [
                "Risk 1 (High)",
                "Risk 2 (Medium)",
                "Risk 1 (High)",
            ],
            "facility_type": [
                "Restaurant",
                "Bakery",
                "Restaurant",
            ],
            "latitude": [41.8, None, 41.9],
            "longitude": [-87.6, -87.7, -87.8],
            "inspection_month": [1, 2, 3],
            "inspection_weekday": [0, 1, 2],
        }
    )

    preprocessor = build_preprocessor()

    transformed = preprocessor.fit_transform(X)

    assert transformed.shape[0] == 3
    assert pd.notna(transformed).all()
