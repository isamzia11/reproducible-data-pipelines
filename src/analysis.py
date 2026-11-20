# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 20, 2026


"""Create analysis tables, visualizations and SQLite outputs."""

from pathlib import Path
import sqlite3

import matplotlib

# Allow figures to be generated without a graphical display.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def create_summaries(df, reports_dir):
    """Analyze inspection results and save summary tables."""

    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Count all inspection outcomes.
    result_counts = (
        df["results"]
        .value_counts(dropna=False)
        .rename_axis("result")
        .reset_index(name="inspection_count")
    )

    result_counts.to_csv(
        reports_dir / "result_counts.csv",
        index=False
    )

    # 2. Select Pass and Fail records for failure analysis.
    binary = df[
        df["results"].isin(["Pass", "Fail"])
    ].copy()

    # NumPy operation 1: create a failure indicator.
    binary["failure_flag"] = np.where(
        binary["results"] == "Fail",
        1,
        0
    )

    # 3. Summarize failures by risk group.
    risk_summary = (
        binary.groupby("risk")["failure_flag"]
        .agg(
            total="count",
            failures="sum"
        )
        .reset_index()
    )

    # NumPy operation 2: calculate percentage.
    if not risk_summary.empty:
        risk_summary["failure_rate_pct"] = np.divide(
            risk_summary["failures"],
            risk_summary["total"]
        ) * 100
    else:
        risk_summary["failure_rate_pct"] = pd.Series(
            dtype="float64"
        )

    risk_summary.to_csv(
        reports_dir / "risk_summary.csv",
        index=False
    )

    # 4. Count inspections by month.
    monthly = df.copy()

    monthly["inspection_date"] = pd.to_datetime(
        monthly["inspection_date"]
    )

    monthly["month"] = (
        monthly["inspection_date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_counts = (
        monthly.groupby("month")
        .size()
        .reset_index(name="inspection_count")
        .sort_values("month")
    )

    monthly_counts.to_csv(
        reports_dir / "monthly_counts.csv",
        index=False
    )

    return result_counts, risk_summary, monthly_counts


def create_figures(
    result_counts,
    risk_summary,
    monthly_counts,
    figures_dir
):
    """Save three inspection charts and their takeaways."""

    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    takeaways = []

    # Chart 1: Count of inspection outcomes.
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(
        result_counts["result"].astype(str),
        result_counts["inspection_count"]
    )

    ax.set_title("Chicago Food Inspection Outcomes")
    ax.set_xlabel("Inspection outcome (category)")
    ax.set_ylabel("Number of inspections (count)")

    ax.tick_params(axis="x", labelrotation=35)

    chart1_text = (
        "This chart compares the number of inspections "
        "recorded under each outcome category."
    )

    fig.text(0.02, 0.02, chart1_text, fontsize=9)
    fig.tight_layout(rect=[0, 0.10, 1, 1])

    fig.savefig(
        figures_dir / "inspection_results.png",
        dpi=150
    )

    plt.close(fig)
    takeaways.append(chart1_text)

    # Chart 2: Failure rates by risk group.
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(
        risk_summary["risk"].astype(str),
        risk_summary["failure_rate_pct"]
    )

    ax.set_title("Failure Rate by Risk Category")
    ax.set_xlabel("Risk category")
    ax.set_ylabel("Failed inspections (%)")
    ax.set_ylim(0, 100)

    ax.tick_params(axis="x", labelrotation=30)

    chart2_text = (
        "Failure percentages show the share of Fail "
        "outcomes among Pass/Fail records in each risk group."
    )

    fig.text(0.02, 0.02, chart2_text, fontsize=9)
    fig.tight_layout(rect=[0, 0.10, 1, 1])

    fig.savefig(
        figures_dir / "risk_failure_rates.png",
        dpi=150
    )

    plt.close(fig)
    takeaways.append(chart2_text)

    # Chart 3: Monthly inspection volume.
    fig, ax = plt.subplots(figsize=(11, 5))

    ax.plot(
        monthly_counts["month"],
        monthly_counts["inspection_count"],
        marker="o"
    )

    ax.set_title("Monthly Food Inspection Activity")
    ax.set_xlabel("Inspection month (YYYY-MM)")
    ax.set_ylabel("Number of inspections (count)")

    ax.tick_params(axis="x", labelrotation=60)

    chart3_text = (
        "Monthly counts show how inspection activity "
        "varied across the historical extraction period."
    )

    fig.text(0.02, 0.02, chart3_text, fontsize=9)
    fig.tight_layout(rect=[0, 0.12, 1, 1])

    fig.savefig(
        figures_dir / "monthly_inspections.png",
        dpi=150
    )

    plt.close(fig)
    takeaways.append(chart3_text)

    return takeaways
def run_sql_analysis(df, sql_dir):
    """Save a SQLite database, query, and query result."""

    sql_dir = Path(sql_dir)
    sql_dir.mkdir(parents=True, exist_ok=True)

    database_path = sql_dir / "inspections.db"

    # Create a small lookup table for risk categories.
    risk_lookup = pd.DataFrame(
        {
            "risk": [
                "Risk 1 (High)",
                "Risk 2 (Medium)",
                "Risk 3 (Low)",
                "Unknown",
            ],
            "description": [
                "High priority",
                "Medium priority",
                "Low priority",
                "Unspecified",
            ],
        }
    )

    # Define a meaningful SQL join and aggregation.
    query = """
    SELECT
        i.risk,
        COALESCE(r.description, 'Unmapped') AS description,
        COUNT(*) AS total_inspections,
        SUM(
            CASE
                WHEN i.results = 'Fail' THEN 1
                ELSE 0
            END
        ) AS failed_inspections
    FROM inspections AS i
    LEFT JOIN risk_lookup AS r
        ON i.risk = r.risk
    GROUP BY i.risk, r.description
    ORDER BY total_inspections DESC;
    """

    # Save the SQL code for inspection by the TA.
    query_path = sql_dir / "inspection_query.sql"
    query_path.write_text(query, encoding="utf-8")

    # Connect to the SQLite database.
    with sqlite3.connect(database_path) as connection:

        # Load cleaned data into the inspections table.
        df.to_sql(
            "inspections",
            connection,
            if_exists="replace",
            index=False
        )

        # Load the lookup table.
        risk_lookup.to_sql(
            "risk_lookup",
            connection,
            if_exists="replace",
            index=False
        )

        # Execute SQL and retrieve a Pandas DataFrame.
        result = pd.read_sql_query(query, connection)

    # Save the query result to CSV.
    result.to_csv(
        sql_dir / "inspection_query_results.csv",
        index=False
    )

    return result
