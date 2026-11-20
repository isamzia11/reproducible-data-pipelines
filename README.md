# Reproducible Data Pipelines, Tabular ML & Systems Exploration

**Student:** Isam Zia
**Roll Number:** TRN-2026-000346
**Assignment:** Data Engineering and Machine Learning
**Python Version:** 3.14.10

## Project Overview

This project uses historical Chicago Food Inspections data to demonstrate reproducible data engineering and tabular machine-learning workflows.

The project is divided into three parts:

- **Part A:** Data cleaning, validation, quality analysis, visualizations and SQLite queries.
- **Part B:** Binary classification of inspection outcomes using a leakage-free scikit-learn pipeline.
- **Part C:** Systems exploration involving database optimization, GitHub Actions, code review and system design.

## Dataset

Source: City of Chicago Data Portal
Dataset: Chicago Food Inspections
URL: [https://data.cityofchicago.org/d/4ijn-s7e5](https://data.cityofchicago.org/d/4ijn-s7e5)
Access Date: November 20, 2026
Usage Terms: City of Chicago Data Terms of Use; TA approval pending.

Raw data file: `data/raw/food_inspections.csv`

The raw dataset must not be modified.

## Environment Setup

This project uses Python 3.14.10

On macOS:

```bash
python3.14.10 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Phase 1 — Inspect Data

Run:

```bash
python src/inspect_data.py
```

To save the inspection report:

```bash
python src/inspect_data.py > outputs/reports/raw_inspection.txt
```

The report contains data dimensions, column types, missing values, duplicates, category counts and numerical summaries.

## Dataset Schema

See `docs/schema.md` for descriptions, expected types, allowed values and quality observations.

## Assumptions and Limitations

See `docs/assumptions.md`.

## Reproducibility

The repository preserves the accepted raw dataset snapshot. Later phases will provide documented commands for regenerating cleaned data, charts, reports and model artifacts.

## Current Status

- [✅] Checkpoint 0 — Proposal approved
- [✅] Checkpoint 1 — Dataset inspected and repository ready
- [✅] Checkpoint 2 — Cleaning and validation
- [✅] Checkpoint 3 — Part A completed
- [✅] Checkpoint 4 — ML preprocessing pipeline
- [✅] Checkpoint 5 — Model comparison
- [✅] Checkpoint 6 — Saved model and Part C


## AI Tools Used

**ChatGPT (OpenAI):** Used as a learning and debugging aid for understanding project setup, Python concepts, dataset selection, documentation and engineering decisions.

All submitted code and analysis will be reviewed, tested and explained by the student.

## Findings Summary

To be completed after Part A and Part B.

## References

- City of Chicago Food Inspections dataset: [https://data.cityofchicago.org/d/4ijn-s7e5](https://data.cityofchicago.org/d/4ijn-s7e5)
- Pandas documentation: [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)
- Scikit-learn documentation: [https://scikit-learn.org/stable/](https://scikit-learn.org/stable/)


## Part A — Data Quality and Insights Pipeline

### Run the Complete Pipeline

From the repository root, activate the virtual environment:

```bash
source .venv/bin/activate
```

Install pinned dependencies if necessary:

```bash
python -m pip install -r requirements.txt
```

Run the complete data-quality pipeline:

```bash
python -m src.run_pipeline
```

### Run Unit Tests

```bash
python -m pytest tests/ -v
```

### Run the Code Quality Check

```bash
python -m ruff check src/ tests/
```

### Main Pipeline Steps

1. Load the untouched raw dataset.
2. Verify the required columns.
3. Measure initial data quality.
4. Clean and standardize records.
5. Validate the cleaned dataset.
6. Save the cleaned CSV.
7. Save before-and-after quality metrics.
8. Create Pandas and NumPy summaries.
9. Generate and save three visualizations.
10. Run the SQLite query and save its results.
11. Verify that the raw CSV has not changed.

### Part A Output Files

Cleaned dataset:

- `data/cleaned/food_inspections_cleaned.csv`

Figures:

- `outputs/figures/inspection_results.png`
- `outputs/figures/risk_failure_rates.png`
- `outputs/figures/monthly_inspections.png`

Reports:

- `outputs/reports/data_quality_report.md`
- `outputs/reports/data_quality_metrics.json`
- `outputs/reports/analysis_summary.md`
- `outputs/reports/result_counts.csv`
- `outputs/reports/risk_summary.csv`
- `outputs/reports/monthly_counts.csv`

SQLite:

- `outputs/sql/inspections.db`
- `outputs/sql/inspection_query.sql`
- `outputs/sql/inspection_query_results.csv`

### Part A Findings

Complete this section using the actual generated reports.

- Raw inspection records: [actual count]
- Cleaned inspection records: [actual count]
- Duplicate inspection IDs removed: [actual count]
- Invalid dates removed: [actual count]
- Missing-cell percentage before cleaning: [actual %]
- Missing-cell percentage after cleaning: [actual %]
- Most common inspection outcome: [actual category]
- Highest observed risk-group failure rate: [category and %]
- Highest-volume inspection month: [month and count]

### Known Limitations

The cleaning pipeline follows documented rules and does not
guarantee that all source errors have been detected.

Inspection outcomes are descriptive observations, not
proof of causal relationships.

See `docs/assumptions.md` for the complete discussion.


## Part B — Tabular Machine Learning Baseline

### Prediction Objective

Predict whether a Chicago food inspection will result
in Pass or Fail, using information assumed to be
available before the inspection.

The positive class is Fail (1).

Other outcomes are excluded from this binary task.

### Features

The model uses:
- Risk category
- Facility type
- Latitude
- Longitude
- Inspection month
- Inspection weekday

Post-inspection fields, including violations,
are excluded to prevent target leakage.

See docs/assumptions.md for the full feature policy.

### Models

Three pipelines are compared:

1. Dummy Classifier
2. Logistic Regression
3. Random Forest

Each pipeline contains a ColumnTransformer with
numerical and categorical preprocessing.

### Validation Strategy

The data is split chronologically.

The training portion is evaluated using three
chronological validation folds.

Models are selected using mean cross-validated
Average Precision.

The later held-out test set is evaluated only
after selecting and fitting the winning model.

### Train Models

```bash
python -m src.train
```

### Run Inference

```bash
python -m src.predict \
  data/new_inspections.csv \
  outputs/reports/new_predictions.csv
```

### Run Tests

```bash
python -m pytest tests/ -v
```

### Model Artifacts

- outputs/models/best_pipeline.joblib
- outputs/reports/model_comparison.csv
- outputs/reports/test_metrics.json
- outputs/reports/test_predictions.csv
- outputs/reports/misclassified_rows.csv
- outputs/reports/subgroup_performance.csv
- outputs/reports/target_distribution.csv
- outputs/reports/error_counts.json
- outputs/figures/confusion_matrix.png

### Model Comparison Findings

Selected model: [Insert model]

Mean cross-validation AP: [Insert value]

Final test AP: [Insert value]
Final test precision: [Insert value]
Final test recall: [Insert value]
Final test F1: [Insert value]

False positives: [Insert count]
False negatives: [Insert count]

### Error Analysis Findings

[Describe actual misclassified inspection examples.]

[Describe performance differences across risk groups.]

### Limitations

The model is an educational prototype.

It is not suitable for automated regulatory decisions.

Historical data, feature availability, repeated
establishments and group-level performance differences
limit generalization.

See the model card in docs/assumptions.md.

## Streamlit Dashboard

Install dependencies using `python -m pip install -r requirements.txt`.
Launch the local interactive dashboard with:

```bash
python -m streamlit run dashboard.py
```

The dashboard visualizes saved Part A and Part B artifacts and provides local model inference.
