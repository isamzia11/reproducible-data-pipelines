
# Raw Dataset Schema

## 1. Dataset Information

Dataset: Chicago Food Inspections
Publisher: Chicago Department of Public Health
Source: https://data.cityofchicago.org/d/4ijn-s7e5
Access Date: November 20, 2026
Usage Terms: City of Chicago Data Terms of Use
Licence Status: Educational reuse and redistribution
subject to verification and TA approval.

Raw File: data/raw/food_inspections.csv

## 2. Dataset Dimensions

Number of Rows: [Insert actual row count]
Number of Columns: [Insert actual column count]

Unit of Observation:
One recorded food establishment inspection.

Time Period:
2022-01-01 through 2023-12-31,
subject to actual extracted dates.

## 3. Column Definitions

| Column | Expected Type | Description |
|---|---|---|
| inspection_id | Integer | Unique inspection identifier |
| dba_name | String | Business name |
| aka_name | String | Alternative business name |
| license_ | Identifier | Business licence number |
| facility_type | Category | Establishment category |
| risk | Category | Risk classification |
| address | String | Street address |
| city | String | City |
| state | String | State |
| zip | Identifier | Postal code |
| inspection_date | Date | Inspection date |
| inspection_type | Category | Type of inspection |
| results | Category | Recorded inspection outcome |
| violations | String | Inspection findings |
| latitude | Float | Latitude in degrees |
| longitude | Float | Longitude in degrees |
| location | Spatial/JSON | Geographic location |

## 4. Allowed Values and Validation Rules

inspection_id:
- Must not be missing.
- Must identify one inspection uniquely.

inspection_date:
- Must be a valid date.
- Expected historical extraction period: 2022-2023.

risk:
- Expected values include Risk 1 (High),
  Risk 2 (Medium), and Risk 3 (Low).
- Missing or unusual values must be inspected.

results:
- Possible values include Pass, Fail,
  and Pass w/ Conditions.
- Record all other observed categories.

latitude:
- Must be between -90 and 90 degrees.

longitude:
- Must be between -180 and 180 degrees.

zip:
- Treat as a categorical identifier.
- Do not calculate averages of ZIP codes.

## 5. Missing Value Analysis

Fill using the actual Pandas inspection output.

| Column | Missing Count | Missing Percentage |
|---|---|---|
| aka_name | TBD | TBD |
| facility_type | TBD | TBD |
| risk | TBD | TBD |
| violations | TBD | TBD |
| latitude | TBD | TBD |
| longitude | TBD | TBD |

Extend this table to cover every source column,
including those with zero missing values.

## 6. Duplicate Analysis

Exact duplicate rows: [Insert count]
Duplicate inspection IDs: [Insert count]

Do not remove duplicates at this stage.

## 7. Target Variable

Column: results

Problem: Binary classification

Planned labels:
- Pass = 0
- Fail = 1

Other inspection statuses require a documented
exclusion or mapping rule.

## 8. Data Leakage

The violations column describes findings recorded
during an inspection.

It should not be used to predict that same inspection
outcome before the inspection occurs.

Other unavailable-at-prediction-time fields will
also be reviewed during Part B.

## 9. Known Limitations

- Some establishment information may be missing.
- The source may contain duplicate inspection reports.
- Reporting procedures changed during the source's
  historical coverage.
- Inspection results represent findings at a particular
  point in time.
- Some source records may be revised later.
- The data is specific to Chicago establishments.

## 10. Raw Data Integrity

Raw SHA-256: [Insert checksum]

The raw CSV must not be modified by the
cleaning or ML pipeline.
