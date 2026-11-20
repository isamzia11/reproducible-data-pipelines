# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 20, 2026


"""Functions for cleaning food inspection records."""

import pandas as pd


def standardize_categories(df):
    """Standardize selected text categories in a DataFrame."""

    cleaned = df.copy()

    # Standardize common categorical fields.
    for column in ["risk", "facility_type", "inspection_type"]:
        cleaned[column] = (
            cleaned[column]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .str.title()
            .fillna("Unknown")
        )

        # Treat empty strings as unknown.
        cleaned[column] = cleaned[column].replace("", "Unknown")

    # Standardize known inspection outcomes.
    cleaned["results"] = (
        cleaned["results"]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
        .fillna("Unknown")
    )

    cleaned["results"] = cleaned["results"].replace(
        {
            "": "Unknown",
            "Pass W/ Conditions": "Pass w/ Conditions",
        }
    )

    return cleaned


def clean_data(df):
    """Clean inspection records and return cleaning statistics."""

    cleaned = df.copy()

    # Record original row count.
    original_rows = len(cleaned)

    # Convert inspection IDs to numeric values.
    cleaned["inspection_id"] = pd.to_numeric(
        cleaned["inspection_id"],
        errors="coerce"
    )

    # Reject missing or non-integer inspection IDs.
    invalid_id = (
        cleaned["inspection_id"].isna()
        | (cleaned["inspection_id"] % 1 != 0)
    )

    invalid_id_count = int(invalid_id.sum())

    cleaned = cleaned.loc[~invalid_id].copy()

    cleaned["inspection_id"] = cleaned["inspection_id"].astype("int64")

    # Remove records with repeated inspection IDs.
    duplicate_count = int(
        cleaned.duplicated(subset=["inspection_id"]).sum()
    )

    cleaned = cleaned.drop_duplicates(
        subset=["inspection_id"],
        keep="first"
    ).copy()

    # Convert inspection dates to datetime values.
    cleaned["inspection_date"] = pd.to_datetime(
        cleaned["inspection_date"],
        errors="coerce"
    )

    # Keep records within the selected historical period.
    valid_date = cleaned["inspection_date"].between(
        "2022-01-01",
        "2023-12-31 23:59:59"
    )

    invalid_date_count = int((~valid_date).sum())

    cleaned = cleaned.loc[valid_date].copy()

    # Standardize categorical columns.
    cleaned = standardize_categories(cleaned)

    # Convert geographic coordinates to numeric values.
    cleaned["latitude"] = pd.to_numeric(
        cleaned["latitude"],
        errors="coerce"
    )

    cleaned["longitude"] = pd.to_numeric(
        cleaned["longitude"],
        errors="coerce"
    )

    # Detect invalid non-missing coordinates.
    invalid_latitude = (
        cleaned["latitude"].notna()
        & ~cleaned["latitude"].between(-90, 90)
    )

    invalid_longitude = (
        cleaned["longitude"].notna()
        & ~cleaned["longitude"].between(-180, 180)
    )

    invalid_coordinate_count = int(
        (invalid_latitude | invalid_longitude).sum()
    )

    # Replace impossible coordinates with missing values.
    cleaned.loc[invalid_latitude, "latitude"] = float("nan")
    cleaned.loc[invalid_longitude, "longitude"] = float("nan")

    # Convert dates into a consistent YYYY-MM-DD format.
    cleaned["inspection_date"] = (
        cleaned["inspection_date"].dt.strftime("%Y-%m-%d")
    )

    # Remove old row indexes from the original DataFrame.
    cleaned = cleaned.reset_index(drop=True)

    # Record how many rows were excluded.
    removed_rows = original_rows - len(cleaned)

    statistics = {
        "original_rows": original_rows,
        "cleaned_rows": len(cleaned),
        "removed_rows": removed_rows,
        "invalid_ids_removed": invalid_id_count,
        "duplicate_ids_removed": duplicate_count,
        "invalid_dates_removed": invalid_date_count,
        "invalid_coordinates_set_missing": invalid_coordinate_count,
    }

    return cleaned, statistics
