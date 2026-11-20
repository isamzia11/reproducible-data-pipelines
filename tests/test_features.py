# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 20, 2026


"""Tests for ML feature preparation and splitting."""

import pandas as pd
import pytest

from src.features import (
    MODEL_FEATURES,
    prepare_features,
    select_binary_records,
    split_by_date,
)


def sample_data():
    """Create a small historical inspection dataset."""

    return pd.DataFrame(
        {
            "inspection_id": [1, 2, 3, 4, 5, 6],
            "inspection_date": [
                "2022-01-01",
                "2022-02-01",
                "2022-03-01",
                "2022-04-01",
                "2022-05-01",
                "2022-06-01",
            ],
            "risk": ["Risk 1 (High)"] * 6,
            "facility_type": ["Restaurant"] * 6,
            "latitude": [41.8] * 6,
            "longitude": [-87.6] * 6,
            "results": [
                "Pass",
                "Fail",
                "Pass w/ Conditions",
                "Fail",
                "Pass",
                "Fail",
            ],
        }
    )


def test_binary_target():
    """Verify that only Pass and Fail become model labels."""

    data = select_binary_records(sample_data())

    assert len(data) == 5
    assert set(data["target"]) == {0, 1}
    assert "Pass w/ Conditions" not in data["results"].values


def test_feature_columns():
    """Verify that the target and leaking columns are excluded."""

    data = sample_data()

    features = prepare_features(data)

    assert list(features.columns) == MODEL_FEATURES
    assert "results" not in features.columns
    assert "violations" not in features.columns
    assert "inspection_id" not in features.columns


def test_calendar_features():
    """Check month and weekday extraction."""

    features = prepare_features(sample_data())

    assert features.loc[0, "inspection_month"] == 1
    assert features.loc[0, "inspection_weekday"] == 5


def test_time_split():
    """Ensure training dates precede test dates."""

    train, test = split_by_date(sample_data())

    assert (
        train["inspection_date"].max()
        < test["inspection_date"].min()
    )


def test_missing_feature_fails():
    """Check that missing input columns raise an error."""

    data = sample_data().drop(columns=["risk"])

    with pytest.raises(ValueError):
        prepare_features(data)


def test_invalid_coordinate_fails():
    """Check that impossible coordinate values are rejected."""

    data = sample_data()
    data.loc[0, "latitude"] = 120.0

    with pytest.raises(ValueError):
        prepare_features(data)
