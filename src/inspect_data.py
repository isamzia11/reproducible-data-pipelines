
# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 20, 2026

"""Inspect the raw food inspection dataset."""

from pathlib import Path

import pandas as pd


def inspect_dataset():
    """Load raw data and print its basic information."""

    # Find the root folder of the project.
    project_root = Path(__file__).resolve().parent.parent

    # Build the path to the raw CSV file.
    file_path = project_root / "data" / "raw" / "food_inspections.csv"

    # Check whether the CSV file exists.
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Raw dataset not found: {file_path}"
        )

    # Load the CSV without changing the source file.
    df = pd.read_csv(file_path, low_memory=False)

    # Print the number of rows and columns.
    print("Dataset shape:", df.shape)

    # Print the column names.
    print("\nColumn names:")
    print(df.columns.tolist())

    # Print the first five records.
    print("\nFirst five rows:")
    print(df.head())

    # Print the data types.
    print("\nData types:")
    print(df.dtypes)

    # Print missing values per column.
    print("\nMissing values:")
    print(df.isnull().sum())

    # Count the number of missing values.
    missing_count = df.isnull().sum()

# Calculate the percentage of missing values.
    missing_percentage = (missing_count / len(df)) * 100

# Print the missing percentages.
    print("\nMissing percentages:")
    print(missing_percentage.round(2))

    # Count completely duplicated rows.
    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    # Count duplicated inspection IDs if present.
    if "inspection_id" in df.columns:
        print("\nDuplicate inspection IDs:")
        print(df["inspection_id"].duplicated().sum())

    # Count inspection outcome categories.
    if "results" in df.columns:
        print("\nInspection result counts:")
        print(df["results"].value_counts(dropna=False))

    # Print a numerical summary.
    print("\nNumerical summary:")
    print(df.describe())

    # List categorical columns to inspect.
    categorical_columns = [
    "risk",
    "facility_type",
    "inspection_type",
    "results",
    ]

# Check each categorical column.
    for column in categorical_columns:

    # Confirm that the column exists.
        if column in df.columns:

            print(f"\nValues in {column}:")

        # Show the number of unique categories.
            print("Unique categories:", df[column].nunique())

        # Show the ten most frequent values.
            print(df[column].value_counts(dropna=False).head(10))

    return df


if __name__ == "__main__":
    inspect_dataset()
