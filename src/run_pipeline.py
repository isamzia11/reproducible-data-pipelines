# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 20, 2026 


"""Run the complete Part A data quality pipeline."""

import hashlib
import json
from pathlib import Path

import pandas as pd

from src.analysis import (
    create_figures,
    create_summaries,
    run_sql_analysis,
)
from src.cleaning import clean_data
from src.validation import (
    validate_cleaned_data,
    validate_columns,
)


def get_quality_metrics(df):
    """Calculate basic quality metrics for a DataFrame."""

    total_rows = len(df)
    total_columns = len(df.columns)
    total_cells = total_rows * total_columns

    missing_cells = int(df.isna().sum().sum())

    if total_cells > 0:
        missing_percentage = (
            missing_cells / total_cells
        ) * 100
    else:
        missing_percentage = 0.0

    # Calculate missing values for every column.
    missing_by_column = {}

    for column in df.columns:
        missing_count = int(df[column].isna().sum())

        if total_rows > 0:
            column_percentage = (
                missing_count / total_rows
            ) * 100
        else:
            column_percentage = 0.0

        missing_by_column[column] = {
            "count": missing_count,
            "percentage": round(column_percentage, 2),
        }

    return {
        "rows": total_rows,
        "columns": total_columns,
        "missing_cells": missing_cells,
        "missing_percentage": round(missing_percentage, 2),
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "missing_by_column": missing_by_column,
    }


def get_file_hash(file_path):
    """Calculate a SHA-256 checksum of a file."""

    hasher = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            hasher.update(chunk)

    return hasher.hexdigest()


def save_quality_report(
    before,
    after,
    cleaning_stats,
    raw_hash,
    reports_dir
):
    """Save before-and-after metrics as JSON and Markdown."""

    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    metrics = {
        "raw_sha256": raw_hash,
        "before": before,
        "after": after,
        "cleaning": cleaning_stats,
    }

    # Save machine-readable metrics.
    metrics_path = reports_dir / "data_quality_metrics.json"

    with open(metrics_path, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)

    # Build a readable Markdown report.
    lines = [
        "# Data Quality Report",
        "",
        "## Before and After Cleaning",
        "",
        "| Metric | Before | After |",
        "|---|---:|---:|",
        f"| Rows | {before['rows']} | {after['rows']} |",
        f"| Columns | {before['columns']} | {after['columns']} |",
        f"| Missing cells | {before['missing_cells']} | {after['missing_cells']} |",
        f"| Missing cells (%) | {before['missing_percentage']} | {after['missing_percentage']} |",
        f"| Exact duplicate rows | {before['exact_duplicate_rows']} | {after['exact_duplicate_rows']} |",
        "",
        "## Cleaning Actions",
        "",
    ]

    for name, value in cleaning_stats.items():
        lines.append(f"- {name}: {value}")

    lines.extend(
        [
            "",
            "## Per-Column Missing Values",
            "",
            "| Column | Before Count | Before % | After Count | After % |",
            "|---|---:|---:|---:|---:|",
        ]
    )

    for column in before["missing_by_column"]:
        old = before["missing_by_column"][column]
        new = after["missing_by_column"][column]

        lines.append(
            f"| {column} | "
            f"{old['count']} | {old['percentage']} | "
            f"{new['count']} | {new['percentage']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The pipeline rejects invalid IDs, duplicate IDs, "
                "and invalid or out-of-range inspection dates."
            ),
            "",
            (
                "Missing category values are represented by Unknown. "
                "Invalid coordinates become missing values."
            ),
            "",
            (
                "Missing percentages may increase because invalid "
                "geographic values are converted into missing values. "
                "That is not necessarily a data-quality failure."
            ),
            "",
            "## Raw Data Integrity",
            "",
            f"SHA-256: `{raw_hash}`",
            "",
            "The pipeline reads the raw file without modifying it.",
        ]
    )

    report_path = reports_dir / "data_quality_report.md"

    report_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )


def main():
    """Execute cleaning, validation, reporting and analysis."""

    # Find the project root.
    project_root = Path(__file__).resolve().parent.parent

    raw_path = project_root / "data/raw/food_inspections.csv"
    cleaned_path = (
        project_root / "data/cleaned/food_inspections_cleaned.csv"
    )

    figures_dir = project_root / "outputs/figures"
    reports_dir = project_root / "outputs/reports"
    sql_dir = project_root / "outputs/sql"

    # Create output folders if necessary.
    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    sql_dir.mkdir(parents=True, exist_ok=True)

    # Fail clearly if the raw CSV does not exist.
    if not raw_path.is_file():
        raise FileNotFoundError(
            f"Raw dataset not found: {raw_path}"
        )

    print("Step 1: Reading raw dataset...")

    # Preserve identifiers such as ZIP codes as strings.
    raw_df = pd.read_csv(
        raw_path,
        dtype={
            "zip": "string",
            "license_": "string",
        },
        low_memory=False
    )

    validate_columns(raw_df)

    raw_hash_before = get_file_hash(raw_path)

    before_metrics = get_quality_metrics(raw_df)

    print("Step 2: Cleaning data...")

    cleaned_df, cleaning_stats = clean_data(raw_df)

    print("Step 3: Validating cleaned data...")

    validate_cleaned_data(cleaned_df)

    # Save the cleaned CSV.
    cleaned_df.to_csv(cleaned_path, index=False)

    # Calculate quality metrics after cleaning.
    after_metrics = get_quality_metrics(cleaned_df)

    print("Step 4: Saving data quality reports...")

    save_quality_report(
        before_metrics,
        after_metrics,
        cleaning_stats,
        raw_hash_before,
        reports_dir
    )

    print("Step 5: Creating Pandas and NumPy summaries...")

    result_counts, risk_summary, monthly_counts = (
        create_summaries(cleaned_df, reports_dir)
    )

    print("Step 6: Creating visualizations...")

    takeaways = create_figures(
        result_counts,
        risk_summary,
        monthly_counts,
        figures_dir
    )

    # Save the visualization descriptions.
    summary_lines = [
        "# Part A Analysis Summary",
        "",
        "## Visualization Takeaways",
        "",
    ]

    for number, takeaway in enumerate(takeaways, start=1):
        summary_lines.append(f"{number}. {takeaway}")

    (reports_dir / "analysis_summary.md").write_text(
        "\n".join(summary_lines) + "\n",
        encoding="utf-8"
    )

    print("Step 7: Running SQLite analysis...")

    sql_result = run_sql_analysis(cleaned_df, sql_dir)

    print(sql_result)

    # Confirm that the raw dataset was not modified.
    raw_hash_after = get_file_hash(raw_path)

    if raw_hash_before != raw_hash_after:
        raise RuntimeError(
            "Raw dataset changed during pipeline execution!"
        )

    print("\nPipeline completed successfully.")
    print("Cleaned data:", cleaned_path)
    print("Figures:", figures_dir)
    print("Reports:", reports_dir)
    print("SQL outputs:", sql_dir)


if __name__ == "__main__":
    main()
