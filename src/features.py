# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 20, 2026

"""Prepare features and target for inspection prediction."""

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

CATEGORICAL_FEATURES = [
    "risk",
    "facility_type",
]

NUMERIC_FEATURES = [
    "latitude",
    "longitude",
    "inspection_month",
    "inspection_weekday",
]

MODEL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

INPUT_COLUMNS = [
    "risk",
    "facility_type",
    "latitude",
    "longitude",
    "inspection_date",
]


def select_binary_records(df):
    """Keep Pass/Fail records and create the binary target."""

    if "results" not in df.columns:
        raise ValueError("Missing target column: results")

    selected = df[
        df["results"].isin(["Pass", "Fail"])
    ].copy()

    if selected.empty:
        raise ValueError("No Pass/Fail records found.")

    selected["target"] = (
        selected["results"] == "Fail"
    ).astype(int)

    return selected


def split_by_date(df, train_fraction=0.80):
    """Split records into earlier training and later test dates."""

    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1.")

    data = df.copy()

    data["inspection_date"] = pd.to_datetime(
        data["inspection_date"],
        errors="coerce"
    )

    if data["inspection_date"].isna().any():
        raise ValueError("Invalid inspection dates found.")

    data = data.sort_values(
        ["inspection_date", "inspection_id"]
    ).reset_index(drop=True)

    unique_dates = sorted(data["inspection_date"].unique())

    if len(unique_dates) < 5:
        raise ValueError("At least five distinct dates are required.")

    # Choose the approximate 80% date boundary.
    cutoff_index = int(len(unique_dates) * train_fraction)

    cutoff_date = unique_dates[cutoff_index]

    train = data[
        data["inspection_date"] < cutoff_date
    ].copy()

    test = data[
        data["inspection_date"] >= cutoff_date
    ].copy()

    if train.empty or test.empty:
        raise ValueError("Train or test split is empty.")

    return train, test


def prepare_features(df):
    """Create model inputs without fitting learned statistics."""

    missing = []

    for column in INPUT_COLUMNS:
        if column not in df.columns:
            missing.append(column)

    if missing:
        raise ValueError(f"Missing input columns: {missing}")

    features = df[INPUT_COLUMNS].copy()

    # Parse the supplied inspection date.
    dates = pd.to_datetime(
        features["inspection_date"],
        errors="coerce"
    )

    if dates.isna().any():
        raise ValueError("Invalid inspection date in model input.")

    # Extract numerical calendar features.
    features["inspection_month"] = dates.dt.month
    features["inspection_weekday"] = dates.dt.dayofweek

    # Convert coordinates to numbers.
    for column in ["latitude", "longitude"]:
        features[column] = pd.to_numeric(
            features[column],
            errors="coerce"
        )

    # Check impossible coordinate values.
    latitude_valid = (
        features["latitude"].isna()
        | features["latitude"].between(-90, 90)
    )

    longitude_valid = (
        features["longitude"].isna()
        | features["longitude"].between(-180, 180)
    )

    if not latitude_valid.all():
        raise ValueError("Latitude outside valid range.")

    if not longitude_valid.all():
        raise ValueError("Longitude outside valid range.")

    # Select only the six approved model features.
    return features[MODEL_FEATURES].copy()


def make_date_cv_splits(train_df, n_splits=3):
    """Create chronological CV folds using distinct dates."""

    dates = pd.to_datetime(train_df["inspection_date"])

    # Keep as a NumPy array so it can be indexed by fold index arrays.
    unique_dates = np.sort(dates.unique())

    if len(unique_dates) < n_splits + 1:
        raise ValueError("Not enough distinct dates for CV.")

    splitter = TimeSeriesSplit(n_splits=n_splits)

    folds = []

    for train_dates_idx, valid_dates_idx in splitter.split(
        unique_dates
    ):
        fold_train_dates = unique_dates[train_dates_idx]
        fold_valid_dates = unique_dates[valid_dates_idx]

        # Find all rows belonging to each set of dates.
        train_rows = np.flatnonzero(
            dates.isin(fold_train_dates).to_numpy()
        )

        valid_rows = np.flatnonzero(
            dates.isin(fold_valid_dates).to_numpy()
        )

        folds.append((train_rows, valid_rows))

    return folds
