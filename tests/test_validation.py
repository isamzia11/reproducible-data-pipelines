# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 20, 2026

"""Unit tests for dataset validation."""

import pandas as pd
import pytest

from src.validation import (
    validate_columns,
    validate_cleaned_data,
)


def make_valid_data():
    """Create a small valid DataFrame for testing."""

    return pd.DataFrame(
        {
            "inspection_id": [101, 102],
            "inspection_date": [
                "2022-01-10",
                "2022-02-15",
            ],
            "risk": [
                "Risk 1 (High)",
                "Risk 2 (Medium)",
            ],
            "facility_type": [
                "Restaurant",
                "Grocery Store",
            ],
            "inspection_type": [
                "Canvass",
                "Canvass",
            ],
            "results": ["Pass", "Fail"],
            "latitude": [41.8, 41.9],
            "longitude": [-87.6, -87.7],
        }
    )


def test_required_columns_present():
    """Check that a complete schema is accepted."""

    df = make_valid_data()

    assert validate_columns(df) is True


def test_missing_column_raises_error():
    """Check that a missing required column causes an error."""

    df = make_valid_data()
    df = df.drop(columns=["results"])

    with pytest.raises(ValueError):
        validate_columns(df)


def test_valid_data_passes():
    """Check that valid cleaned data is accepted."""

    df = make_valid_data()

    assert validate_cleaned_data(df) is True


def test_duplicate_ids_fail():
    """Check that duplicated IDs are rejected."""

    df = make_valid_data()
    df.loc[1, "inspection_id"] = 101

    with pytest.raises(ValueError):
        validate_cleaned_data(df)


def test_invalid_latitude_fails():
    """Check that impossible latitude values are rejected."""

    df = make_valid_data()
    df.loc[0, "latitude"] = 120.0

    with pytest.raises(ValueError):
        validate_cleaned_data(df)


def test_invalid_date_fails():
    """Check that invalid inspection dates are rejected."""

    df = make_valid_data()
    df.loc[0, "inspection_date"] = "not-a-date"

    with pytest.raises(ValueError):
        validate_cleaned_data(df)


def test_empty_dataframe_fails():
    """Check that an empty dataset is rejected."""

    df = make_valid_data()
    df = df.iloc[0:0]

    with pytest.raises(ValueError):
        validate_cleaned_data(df)
