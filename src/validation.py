# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 20, 2026


"""Functions for validating food inspection data."""

import pandas as pd

REQUIRED_COLUMNS = [
    "inspection_id",
    "inspection_date",
    "risk",
    "facility_type",
    "inspection_type",
    "results",
    "latitude",
    "longitude",
]


def validate_columns(df):
    """Raise an error when a required column is missing."""

    missing_columns = []

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            missing_columns.append(column)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return True


def validate_cleaned_data(df):
    """Check important quality rules after cleaning."""

    # Make sure required columns exist.
    validate_columns(df)

    # An empty dataset is not a valid pipeline result.
    if df.empty:
        raise ValueError("The cleaned dataset is empty.")

    # Every inspection needs an ID.
    if df["inspection_id"].isna().any():
        raise ValueError("Missing inspection IDs found.")

    # IDs must be integer values.
    if not pd.api.types.is_integer_dtype(df["inspection_id"]):
        raise ValueError("Inspection IDs must be integers.")

    # Each inspection ID must be unique.
    if df["inspection_id"].duplicated().any():
        raise ValueError("Duplicate inspection IDs found.")

    # Inspection dates must be valid and within the period.
    dates = pd.to_datetime(
        df["inspection_date"],
        errors="coerce"
    )

    if dates.isna().any():
        raise ValueError("Invalid inspection dates found.")

    if not dates.between(
        "2022-01-01",
        "2023-12-31 23:59:59"
    ).all():
        raise ValueError("Inspection date outside expected period.")

    # Results must not contain missing or empty values.
    if df["results"].isna().any():
        raise ValueError("Missing result labels found.")

    if df["results"].astype("string").str.strip().eq("").any():
        raise ValueError("Empty result labels found.")

    # Geographic values must be valid when provided.
    if not df["latitude"].dropna().between(-90, 90).all():
        raise ValueError("Latitude outside valid range.")

    if not df["longitude"].dropna().between(-180, 180).all():
        raise ValueError("Longitude outside valid range.")

    return True
