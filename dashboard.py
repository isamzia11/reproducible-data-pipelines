# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 21, 2026

"""Local Streamlit dashboard for the Chicago Food Inspections assignment.

Put this file in the root of the existing reproducible-data-pipelines repo.
The dashboard reads generated project artifacts without changing source data.
"""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/food_inspections.csv"
CLEAN = ROOT / "data/cleaned/food_inspections_cleaned.csv"
REPORTS = ROOT / "outputs/reports"
FIGURES = ROOT / "outputs/figures"
SQL = ROOT / "outputs/sql"
MODEL = ROOT / "outputs/models/best_pipeline.joblib"

st.set_page_config(
    page_title="Inspection Intelligence | Pipeline Studio",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .stApp {background: #0b1220; color: #f1f5f9;}
      [data-testid="stSidebar"] {background: #121e30; border-right: 1px solid #26364c;}
      h1,h2,h3 {letter-spacing: -0.035em;}
      h1 {font-size: 2.25rem !important;}
      .stMetric {background: #142237; border: 1px solid #2b3f55; padding: 16px;
                 border-radius: 13px;}
      .stMetric label {color: #a6b7cd !important;}
      .section-hint {color: #9eb0c8; font-size: 0.94rem; margin-bottom: 1rem;}
      .step {background: #142237; border: 1px solid #294057; padding: 15px;
             border-radius: 12px; margin: 6px 0;}
      .step strong {color: #ecf5fc;}
      .step small {color: #a7bacd;}
      div[data-testid="stAlert"] {border-radius: 10px;}
    </style>
    """,
    unsafe_allow_html=True,
)


def read_csv(path):
    """Return an existing CSV as a DataFrame, or None if it is absent."""
    if not path.is_file():
        return None
    try:
        return pd.read_csv(path, low_memory=False)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        st.error(f"Couldn't read {path.name}: {exc}")
        return None


def read_json(path):
    """Read saved JSON without fabricating missing results."""
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        st.error(f"Couldn't read {path.name}: {exc}")
        return None


def show_missing(path):
    """Tell the user which existing command creates an absent artifact."""
    st.info(f"Not generated yet: `{path.relative_to(ROOT)}`. Run the relevant pipeline first.")


def display_artifact(path, caption=None):
    """Display an existing figure at readable width."""
    if path.is_file():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        show_missing(path)


def safe_download(path, label):
    """Offer a download of a real local artifact."""
    if path.is_file():
        st.download_button(label, data=path.read_bytes(), file_name=path.name,
                           key=f"dl_{path.name}")


def run_project_command(module, title):
    """Run only hard-coded local project modules and show command output."""
    if module not in {"src.run_pipeline", "src.train"}:
        raise ValueError("Unsupported command")
    with st.spinner(f"Running {title}..."):
        try:
            completed = subprocess.run(
                [sys.executable, "-m", module],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )
        except subprocess.TimeoutExpired:
            st.error("Command exceeded 10 minutes. Run it in Terminal to investigate.")
            return
        except OSError as exc:
            st.error(f"Unable to run command: {exc}")
            return
    if completed.returncode == 0:
        st.success(f"{title} finished successfully.")
    else:
        st.error(f"{title} failed (exit code {completed.returncode}).")
    with st.expander("Full execution log", expanded=True):
        st.code((completed.stdout + "\n" + completed.stderr)[-30000:], language="text")


def label_status(path):
    """Return a status label based on whether the file exists."""
    return "✅ Ready" if path.is_file() else "○ Missing"


quality = read_json(REPORTS / "data_quality_metrics.json")
test_metrics = read_json(REPORTS / "test_metrics.json")
error_metrics = read_json(REPORTS / "error_counts.json")
comparison = read_csv(REPORTS / "model_comparison.csv")
clean_data = read_csv(CLEAN)

with st.sidebar:
    st.markdown("### ◈ PIPELINE STUDIO")
    st.caption("Chicago Food Inspections · Coursework demo")
    page = st.radio(
        "Explore",
        ["Overview", "Data Quality", "Insights & SQL", "Machine Learning",
         "Live Prediction", "Run Pipelines"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("ARTIFACT STATUS")
    for name, path in [
        ("Raw CSV", RAW), ("Cleaned CSV", CLEAN),
        ("Quality report", REPORTS / "data_quality_metrics.json"),
        ("Model scores", REPORTS / "model_comparison.csv"),
        ("Saved model", MODEL),
    ]:
        st.caption(f"{label_status(path)} · {name}")
    st.divider()
    st.caption("Reads only files in this repository. All metrics come from saved outputs.")

st.title("Inspection Intelligence")
st.markdown('<div class="section-hint">Reproducible Data Pipelines · Data Quality · Tabular Machine Learning</div>',
            unsafe_allow_html=True)


if page == "Overview":
    st.subheader("Pipeline overview")
    before = (quality or {}).get("before", {})
    after = (quality or {}).get("after", {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Raw records", f"{before.get('rows', '—'):,}" if isinstance(before.get('rows'), int) else "—")
    c2.metric("Cleaned records", f"{after.get('rows', '—'):,}" if isinstance(after.get('rows'), int) else "—")
    c3.metric("Missing after", f"{after['missing_percentage']:.2f}%" if 'missing_percentage' in after else "—")
    c4.metric("Selected ML model", (test_metrics or {}).get("selected_model", "—"))
    st.markdown("#### End-to-end execution flow")
    steps = [
        ("01", "Ingest", RAW, "Preserve the raw government dataset"),
        ("02", "Clean and validate", CLEAN, "Normalize categories, validate IDs and dates"),
        ("03", "Data-quality report", REPORTS / "data_quality_metrics.json", "Before/after quality metrics"),
        ("04", "Analyze and visualize", FIGURES / "inspection_results.png", "Pandas, NumPy and saved charts"),
        ("05", "Query with SQLite", SQL / "inspection_query_results.csv", "Aggregated inspection report"),
        ("06", "Model comparison", REPORTS / "model_comparison.csv", "Chronological CV of three models"),
        ("07", "Evaluate and save", MODEL, "Holdout evaluation and fitted Joblib pipeline"),
        ("08", "Predict new cases", REPORTS / "new_predictions.csv", "Inference without retraining"),
    ]
    progress = sum(p.is_file() for _, _, p, _ in steps) / len(steps)
    st.progress(progress, text=f"{int(progress * 100)}% of expected pipeline artifacts available")
    for num, name, path, desc in steps:
        st.markdown(
            f'<div class="step"><strong>{num} · {name}</strong> &nbsp; '
            f'<span>{label_status(path)}</span><br/><small>{desc}</small></div>',
            unsafe_allow_html=True,
        )
    st.caption("The dashboard visualizes the real saved results; it does not claim that upstream steps ran unless their files exist.")

elif page == "Data Quality":
    st.subheader("Raw → cleaned quality comparison")
    if quality:
        before, after = quality.get("before", {}), quality.get("after", {})
        a, b, c = st.columns(3)
        a.metric("Records removed", (quality.get("cleaning") or {}).get("removed_rows", "—"))
        b.metric("Missing cells · before", before.get("missing_cells", "—"))
        c.metric("Missing cells · after", after.get("missing_cells", "—"))
        st.markdown("#### Quality metrics")
        quality_table = pd.DataFrame([
            {"Metric": "Rows", "Before": before.get("rows"), "After": after.get("rows")},
            {"Metric": "Columns", "Before": before.get("columns"), "After": after.get("columns")},
            {"Metric": "Missing cells", "Before": before.get("missing_cells"), "After": after.get("missing_cells")},
            {"Metric": "Missing %", "Before": before.get("missing_percentage"), "After": after.get("missing_percentage")},
            {"Metric": "Exact duplicates", "Before": before.get("exact_duplicate_rows"), "After": after.get("exact_duplicate_rows")},
        ])
        st.dataframe(quality_table, hide_index=True, use_container_width=True)
        st.markdown("#### Cleaning actions")
        st.dataframe(pd.DataFrame(list((quality.get("cleaning") or {}).items()),
                                 columns=["Action", "Count"]), hide_index=True, use_container_width=True)
        cols = before.get("missing_by_column", {})
        if cols:
            missing_df = pd.DataFrame([
                {"Column": col, "Before %": item.get("percentage", 0),
                 "After %": after.get("missing_by_column", {}).get(col, {}).get("percentage", 0)}
                for col, item in cols.items()
            ]).sort_values("Before %", ascending=False)
            st.markdown("#### Missingness by column")
            st.bar_chart(missing_df.set_index("Column")[["Before %", "After %"]])
        safe_download(REPORTS / "data_quality_report.md", "Download quality report")
    else:
        show_missing(REPORTS / "data_quality_metrics.json")
    if clean_data is not None:
        st.markdown("#### Explore the cleaned data")
        st.dataframe(clean_data.head(30), use_container_width=True, hide_index=True)

elif page == "Insights & SQL":
    st.subheader("Exploratory analysis")
    first, second = st.tabs(["Visualizations", "SQLite results"])
    with first:
        for fname, label in [
            ("inspection_results.png", "Inspection outcome distribution"),
            ("risk_failure_rates.png", "Failure rate among Pass/Fail inspections"),
            ("monthly_inspections.png", "Inspection volume over time"),
        ]:
            st.markdown(f"#### {label}")
            display_artifact(FIGURES / fname)
        st.caption("The monthly plot reflects the historical source extract, which may cover only part of a calendar year.")
    with second:
        sql_results = read_csv(SQL / "inspection_query_results.csv")
        if sql_results is None:
            show_missing(SQL / "inspection_query_results.csv")
        else:
            st.dataframe(sql_results, use_container_width=True, hide_index=True)
            safe_download(SQL / "inspection_query_results.csv", "Download SQL results")
        query_path = SQL / "inspection_query.sql"
        if query_path.is_file():
            with st.expander("View SQL query"):
                st.code(query_path.read_text(encoding="utf-8"), language="sql")

elif page == "Machine Learning":
    st.subheader("Model training and evaluation")
    a, b, c, d = st.columns(4)
    a.metric("Best model", (test_metrics or {}).get("selected_model", "—"))
    b.metric("Test AP", f"{test_metrics['average_precision']:.3f}" if test_metrics and 'average_precision' in test_metrics else "—")
    c.metric("Test recall", f"{test_metrics['recall']:.1%}" if test_metrics and 'recall' in test_metrics else "—")
    d.metric("Test F1", f"{test_metrics['f1']:.3f}" if test_metrics and 'f1' in test_metrics else "—")
    if test_metrics:
        st.info(f"Train: {test_metrics.get('train_rows', '—')} records through {test_metrics.get('train_end_date', '—')}  ·  "
                f"Test: {test_metrics.get('test_rows', '—')} records from {test_metrics.get('test_start_date', '—')}")
    st.markdown("#### Cross-validated model comparison")
    if comparison is not None:
        st.dataframe(comparison, use_container_width=True, hide_index=True)
        if {'model', 'cv_ap_mean'}.issubset(comparison.columns):
            st.bar_chart(comparison.set_index('model')['cv_ap_mean'])
    else:
        show_missing(REPORTS / "model_comparison.csv")
    st.markdown("#### Held-out confusion matrix")
    display_artifact(FIGURES / "confusion_matrix.png")
    if error_metrics:
        e1, e2, e3 = st.columns(3)
        e1.metric("False positives", error_metrics.get("false_positives", "—"))
        e2.metric("False negatives", error_metrics.get("false_negatives", "—"))
        e3.metric("Correct predictions", error_metrics.get("correct_predictions", "—"))
    with st.expander("Actual mistakes and subgroup breakdown"):
        mistakes = read_csv(REPORTS / "misclassified_rows.csv")
        subgroups = read_csv(REPORTS / "subgroup_performance.csv")
        if subgroups is not None:
            st.markdown("**Performance by risk group**")
            st.dataframe(subgroups, use_container_width=True, hide_index=True)
        if mistakes is not None:
            st.markdown("**Misclassified records (first 30)**")
            st.dataframe(mistakes.head(30), use_container_width=True, hide_index=True)

elif page == "Live Prediction":
    st.subheader("Predict an inspection outcome")
    st.caption("Educational demo only. Features must be known before inspection. Probabilities are not guaranteed calibrated.")
    if MODEL.is_file():
        with st.form("predict_form"):
            left, right = st.columns(2)
            with left:
                risk = st.selectbox("Risk category", ["Risk 1 (High)", "Risk 2 (Medium)", "Risk 3 (Low)"])
                facility_type = st.selectbox("Facility type", ["Restaurant", "Grocery Store", "Bakery", "Other"])
                inspection_date = st.date_input("Scheduled inspection date", value=date(2024, 2, 12))
            with right:
                latitude = st.number_input("Latitude (degrees)", min_value=-90.0, max_value=90.0, value=41.88, format="%.5f")
                longitude = st.number_input("Longitude (degrees)", min_value=-180.0, max_value=180.0, value=-87.63, format="%.5f")
            submitted = st.form_submit_button("Run prediction", type="primary")
        if submitted:
            try:
                from src.features import prepare_features
                row = pd.DataFrame([{
                    "risk": risk, "facility_type": facility_type,
                    "latitude": latitude, "longitude": longitude,
                    "inspection_date": inspection_date.isoformat(),
                }])
                model = joblib.load(MODEL)  # Only load the model saved by this trusted project.
                x = prepare_features(row)
                predicted = int(model.predict(x)[0])
                classes = list(model.named_steps["classifier"].classes_)
                probability = float(model.predict_proba(x)[0][classes.index(1)])
                st.success(f"Predicted outcome: {'Fail' if predicted == 1 else 'Pass'}")
                st.metric("Estimated Fail score", f"{probability:.1%}")
                st.progress(min(max(probability, 0.0), 1.0))
                st.dataframe(row.assign(predicted_result="Fail" if predicted else "Pass",
                                            failure_probability=probability), hide_index=True, use_container_width=True)
            except (OSError, ValueError, KeyError, IndexError, ImportError) as exc:
                st.error(f"Prediction could not complete: {exc}")
        st.markdown("#### Previously saved predictions")
        saved = read_csv(REPORTS / "new_predictions.csv")
        if saved is not None:
            st.dataframe(saved, use_container_width=True, hide_index=True)
    else:
        show_missing(MODEL)

elif page == "Run Pipelines":
    st.subheader("Execute your project from the dashboard")
    st.warning("These buttons run project code locally and regenerate output files. Commit important outputs before rerunning training. Do not expose this control on a public deployment.")
    one, two = st.columns(2)
    with one:
        st.markdown("#### Part A · Data quality")
        st.caption("Load raw CSV, clean, validate, summarize, plot, and run SQL.")
        if st.button("Run Part A pipeline", use_container_width=True):
            run_project_command("src.run_pipeline", "Part A pipeline")
    with two:
        st.markdown("#### Part B · Machine learning")
        st.caption("Cross-validate, compare, evaluate, and save a fitted pipeline.")
        if st.button("Train and evaluate models", use_container_width=True):
            if not CLEAN.is_file():
                st.error("Run Part A first: the cleaned dataset is missing.")
            else:
                run_project_command("src.train", "Part B training")
    if st.button("Refresh displayed artifacts"):
        st.rerun()
    st.markdown("#### Test the project in Terminal")
    st.code("python -m pytest tests/ -v\npython -m ruff check src/ tests/", language="bash")

st.divider()
st.caption("Built for the Reproducible Data Pipelines, Tabular ML & Systems Exploration assignment · Isam Zia")
