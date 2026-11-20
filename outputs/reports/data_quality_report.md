# Data Quality Report

## Before and After Cleaning

| Metric | Before | After |
|---|---:|---:|
| Rows | 12000 | 12000 |
| Columns | 17 | 17 |
| Missing cells | 3749 | 3700 |
| Missing cells (%) | 1.84 | 1.81 |
| Exact duplicate rows | 0 | 0 |

## Cleaning Actions

- original_rows: 12000
- cleaned_rows: 12000
- removed_rows: 0
- invalid_ids_removed: 0
- duplicate_ids_removed: 0
- invalid_dates_removed: 0
- invalid_coordinates_set_missing: 0

## Per-Column Missing Values

| Column | Before Count | Before % | After Count | After % |
|---|---:|---:|---:|---:|
| inspection_id | 0 | 0.0 | 0 | 0.0 |
| dba_name | 0 | 0.0 | 0 | 0.0 |
| aka_name | 18 | 0.15 | 18 | 0.15 |
| license_ | 1 | 0.01 | 1 | 0.01 |
| facility_type | 45 | 0.38 | 0 | 0.0 |
| risk | 4 | 0.03 | 0 | 0.0 |
| address | 0 | 0.0 | 0 | 0.0 |
| city | 3 | 0.03 | 3 | 0.03 |
| state | 2 | 0.02 | 2 | 0.02 |
| zip | 0 | 0.0 | 0 | 0.0 |
| inspection_date | 0 | 0.0 | 0 | 0.0 |
| inspection_type | 0 | 0.0 | 0 | 0.0 |
| results | 0 | 0.0 | 0 | 0.0 |
| violations | 3544 | 29.53 | 3544 | 29.53 |
| latitude | 44 | 0.37 | 44 | 0.37 |
| longitude | 44 | 0.37 | 44 | 0.37 |
| location | 44 | 0.37 | 44 | 0.37 |

## Interpretation

The pipeline rejects invalid IDs, duplicate IDs, and invalid or out-of-range inspection dates.

Missing category values are represented by Unknown. Invalid coordinates become missing values.

Missing percentages may increase because invalid geographic values are converted into missing values. That is not necessarily a data-quality failure.

## Raw Data Integrity

SHA-256: `31c1f7279a873f0bda30a348df4159f2983234624d3779032b9398aaf81781d8`

The pipeline reads the raw file without modifying it.
