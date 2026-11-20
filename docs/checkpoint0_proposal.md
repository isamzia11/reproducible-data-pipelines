# Checkpoint 0 — Dataset Proposal

**Student:** Isam Zia  
**Roll Number:** TRN-2026-000346
**Date:** November 20, 2026  
**Assignment:** Reproducible Data Pipelines, Tabular ML & Systems Exploration

### Proposed Dataset: Chicago Food Inspections

**Source:** City of Chicago Data Portal, Chicago Department of Public Health  
**Dataset URL:** https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5  
**Access Date:** November 20, 2026  
**Usage Terms:** City of Chicago Data Terms of Use; educational reuse subject to verification and TA approval.

### Dataset Description

The dataset contains real inspection records for food establishments in Chicago. The published dataset contains approximately 318,000 rows and 17 columns. For this assignment, I propose extracting a fixed historical sample of 12,000 inspections from 2022–2023, with the actual record count verified after downloading.

The data includes inspection dates, establishment information, facility categories, inspection types, risk levels, inspection outcomes and geographic attributes.

### Data Quality Objectives

I will inspect the dataset for missing values, duplicated records, inconsistent categorical labels, invalid dates and unusual numerical values. I will implement reusable cleaning and validation functions, document every rule, and produce a before-and-after data-quality report.

### Machine Learning Objective

The prediction task will be binary classification: predicting whether an establishment passes or fails an inspection using information available before the inspection. The target column is `Results`.

I will exclude fields that contain information discovered during or after the inspection, particularly `Violations`, to prevent data leakage. I will compare a simple baseline with at least two machine-learning models.

### Why This Dataset Fits

The dataset originates from an operational government source, has more than the required number of rows and columns, includes numerical, categorical and date fields, and supports meaningful data-quality analysis, visualizations, SQL queries and classification.

I will preserve the raw data, make the workflow reproducible, document limitations, and request TA approval before beginning Part A.