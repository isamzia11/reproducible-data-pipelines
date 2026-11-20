# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 20, 2026


"""Unit tests for data cleaning functions."""

import pandas as pd

from src.cleaning import clean_data, standardize_categories


def make_sample_data():
    """Create a small inspection dataset for testing."""

    data = {
        "inspection_id": [101, 102, 102, 103],
        "inspection_date": [
            "2022-03-01",
            "2022-04-01",
            "2022-04-01",
            "bad-date",
        ],
        "risk": [
            " risk 1 (HIGH) ",
            "Risk 2 (Medium)",
            "Risk 2 (Medium)",
            None,
        ],
        "facility_type": [
            " restaurant ",
            "GROCERY STORE",
            "GROCERY STORE",
            None,
        ],
        "inspection_type": [
            "canvass",
            "Canvass",
            "Canvass",
            None,
        ],
        "results": [
            " pass ",
            "FAIL",
            "FAIL",
            None,
        ],
        "latitude": [41.8, 41.9, 41.9, 120.0],
        "longitude": [-87.6, -87.7, -87.7, -87.6],
    }

    return pd.DataFrame(data)


def test_standardize_categories():
    """Check that category formatting is standardized."""

    df = make_sample_data()

    result = standardize_categories(df)

    assert result.loc[0, "risk"] == "Risk 1 (High)"
    assert result.loc[0, "facility_type"] == "Restaurant"
    assert result.loc[0, "results"] == "Pass"
    assert result.loc[1, "results"] == "Fail"


def test_remove_duplicate_ids():
    """Check that repeated inspection IDs are removed."""

    df = make_sample_data()

    cleaned, stats = clean_data(df)

    assert cleaned["inspection_id"].is_unique
    assert stats["duplicate_ids_removed"] == 1


def test_remove_invalid_dates():
    """Check that records with invalid dates are removed."""

    df = make_sample_data()

    cleaned, stats = clean_data(df)

    assert len(cleaned) == 2
    assert stats["invalid_dates_removed"] == 1


def test_original_dataframe_unchanged():
    """Check that cleaning does not change the input DataFrame."""

    df = make_sample_data()
    original = df.copy(deep=True)

    clean_data(df)

    pd.testing.assert_frame_equal(df, original)


def test_invalid_coordinates_become_missing():
    """Check that impossible coordinates become missing."""

    df = make_sample_data()

    # Make one retained row contain an impossible latitude.
    df.loc[0, "latitude"] = 120.0

    cleaned, stats = clean_data(df)

    assert pd.isna(cleaned.loc[0, "latitude"])
    assert stats["invalid_coordinates_set_missing"] == 1


def test_missing_categories():
    """Check that missing categories become Unknown."""

    df = make_sample_data()
    df.loc[0, "facility_type"] = None

    cleaned, _stats = clean_data(df)

    assert cleaned.loc[0, "facility_type"] == "Unknown"


def test_missing_inspection_id():
    """Check that missing inspection IDs are removed."""

    df = make_sample_data()
    df.loc[0, "inspection_id"] = None

    cleaned, stats = clean_data(df)

    assert stats["invalid_ids_removed"] == 1
    assert cleaned["inspection_id"].notna().all()


def test_out_of_range_date():
    """Check that dates outside 2022-2023 are removed."""

    df = make_sample_data()
    df.loc[0, "inspection_date"] = "2020-01-01"

    cleaned, stats = clean_data(df)

    assert stats["invalid_dates_removed"] == 2
    assert 101 not in cleaned["inspection_id"].tolist()


def test_results_are_preserved():
    """Check that Pass w/ Conditions is not changed to Pass."""

    df = make_sample_data()
    df.loc[0, "results"] = "pass w/ conditions"

    cleaned, _stats = clean_data(df)

    assert cleaned.loc[0, "results"] == "Pass w/ Conditions"

