# Name: Isam Zia
# Roll Number: TRN-2026-000346
# Date: November 20, 2026


"""Train, compare, evaluate and save inspection classifiers."""

import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)

from src.features import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    make_date_cv_splits,
    prepare_features,
    select_binary_records,
    split_by_date,
)

RANDOM_STATE = 42


def build_preprocessor():
    """Create training-only numeric and categorical transformations."""

    # Numerical processing.
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    # Categorical processing.
    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            ),
        ]
    )

    # Apply different processing to each column type.
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
    )

    return preprocessor


def build_models():
    """Create three complete preprocessing-plus-model pipelines."""

    estimators = {
        "Dummy Baseline": DummyClassifier(
            strategy="most_frequent"
        ),
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    # Wrap each estimator with its own preprocessing pipeline.
    models = {}

    for name, estimator in estimators.items():
        models[name] = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                ("classifier", estimator),
            ]
        )

    return models


def check_binary_classes(labels, description):
    """Require both classes for a valid binary evaluation."""

    classes = set(labels)

    if classes != {0, 1}:
        raise ValueError(
            f"{description} must contain both Pass and Fail. "
            f"Found classes: {classes}"
        )


def compare_models(models, X_train, y_train, cv_folds):
    """Compare pipelines using training-only cross-validation."""

    scoring = {
        "ap": "average_precision",
        "f1": "f1",
        "precision": "precision",
        "recall": "recall",
    }

    rows = []

    for name, model in models.items():
        print(f"\nCross-validating: {name}")

        scores = cross_validate(
            model,
            X_train,
            y_train,
            cv=cv_folds,
            scoring=scoring,
            error_score="raise",
            n_jobs=1,
        )

        row = {
            "model": name,
            "cv_ap_mean": scores["test_ap"].mean(),
            "cv_ap_std": scores["test_ap"].std(),
            "cv_f1_mean": scores["test_f1"].mean(),
            "cv_precision_mean": scores["test_precision"].mean(),
            "cv_recall_mean": scores["test_recall"].mean(),
        }

        rows.append(row)

    comparison = pd.DataFrame(rows)

    comparison = comparison.sort_values(
        "cv_ap_mean",
        ascending=False
    ).reset_index(drop=True)

    return comparison


def calculate_test_metrics(model, X_test, y_test):
    """Evaluate a fitted model on the held-out test data."""

    predictions = model.predict(X_test)

    # Find the position of the Fail class.
    classes = list(model.named_steps["classifier"].classes_)
    fail_column = classes.index(1)

    probabilities = model.predict_proba(X_test)[:, fail_column]

    metrics = {
        "average_precision": float(
            average_precision_score(y_test, probabilities)
        ),
        "precision": float(
            precision_score(
                y_test, predictions, zero_division=0
            )
        ),
        "recall": float(
            recall_score(
                y_test, predictions, zero_division=0
            )
        ),
        "f1": float(
            f1_score(
                y_test, predictions, zero_division=0
            )
        ),
    }

    return predictions, probabilities, metrics


def save_error_analysis(
    test_df,
    predictions,
    probabilities,
    reports_dir
):
    """Save misclassified records and subgroup performance."""

    reports_dir = Path(reports_dir)

    results = test_df.copy().reset_index(drop=True)

    results["predicted_target"] = predictions
    results["failure_probability"] = probabilities

    # Make each prediction easy to interpret.
    results["prediction_correct"] = (
        results["target"] == results["predicted_target"]
    )

    # Name the error type.
    results["error_type"] = "Correct"

    false_positive = (
        (results["target"] == 0)
        & (results["predicted_target"] == 1)
    )

    false_negative = (
        (results["target"] == 1)
        & (results["predicted_target"] == 0)
    )

    results.loc[false_positive, "error_type"] = (
        "False Positive"
    )

    results.loc[false_negative, "error_type"] = (
        "False Negative"
    )

    # Save individual prediction outcomes.
    results[
        [
            "inspection_id",
            "inspection_date",
            "risk",
            "facility_type",
            "results",
            "target",
            "predicted_target",
            "failure_probability",
            "error_type",
        ]
    ].to_csv(
        reports_dir / "test_predictions.csv",
        index=False
    )

    # Save all incorrect predictions.
    mistakes = results[
        results["error_type"] != "Correct"
    ].copy()

    mistakes.to_csv(
        reports_dir / "misclassified_rows.csv",
        index=False
    )

    # Compare performance across risk groups.
    subgroup_rows = []

    for group_name, group in results.groupby("risk"):
        group_precision = precision_score(
            group["target"],
            group["predicted_target"],
            zero_division=0,
        )

        group_recall = recall_score(
            group["target"],
            group["predicted_target"],
            zero_division=0,
        )

        subgroup_rows.append(
            {
                "risk": group_name,
                "records": len(group),
                "actual_failures": int(group["target"].sum()),
                "precision": group_precision,
                "recall": group_recall,
            }
        )

    subgroup_table = pd.DataFrame(subgroup_rows)

    subgroup_table.to_csv(
        reports_dir / "subgroup_performance.csv",
        index=False
    )

    error_counts = {
        "false_positives": int(false_positive.sum()),
        "false_negatives": int(false_negative.sum()),
        "correct_predictions": int(
            results["prediction_correct"].sum()
        ),
        "total_test_records": len(results),
    }

    return mistakes, subgroup_table, error_counts


def main():
    """Run the complete Part B training workflow."""

    root = Path(__file__).resolve().parent.parent

    data_path = (
        root / "data/cleaned/food_inspections_cleaned.csv"
    )

    reports_dir = root / "outputs/reports"
    models_dir = root / "outputs/models"
    figures_dir = root / "outputs/figures"

    for folder in [reports_dir, models_dir, figures_dir]:
        folder.mkdir(parents=True, exist_ok=True)

    if not data_path.is_file():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {data_path}"
        )

    print("Step 1: Loading cleaned data...")

    raw = pd.read_csv(data_path, low_memory=False)

    print("Step 2: Selecting Pass/Fail records...")

    data = select_binary_records(raw)

    print("Class balance:")
    print(data["target"].value_counts())

    class_balance = (
        data["target"]
        .value_counts()
        .sort_index()
        .rename_axis("class")
        .reset_index(name="count")
    )

    class_balance.to_csv(
        reports_dir / "target_distribution.csv",
        index=False
    )

    print("Step 3: Creating chronological split...")

    train_df, test_df = split_by_date(data)

    X_train = prepare_features(train_df)
    X_test = prepare_features(test_df)

    y_train = train_df["target"].reset_index(drop=True)
    y_test = test_df["target"].reset_index(drop=True)

    check_binary_classes(y_train, "Training data")
    check_binary_classes(y_test, "Test data")

    print("Training rows:", len(X_train))
    print("Test rows:", len(X_test))

    print(
        "Training date range:",
        train_df["inspection_date"].min(),
        train_df["inspection_date"].max(),
    )

    print(
        "Test date range:",
        test_df["inspection_date"].min(),
        test_df["inspection_date"].max(),
    )

    print("Step 4: Building chronological CV folds...")

    cv_folds = make_date_cv_splits(train_df, n_splits=3)

    # Ensure every fold supports binary classification.
    for fold_number, (train_idx, valid_idx) in enumerate(
        cv_folds, start=1
    ):
        check_binary_classes(
            y_train.iloc[train_idx],
            f"Fold {fold_number} training"
        )

        check_binary_classes(
            y_train.iloc[valid_idx],
            f"Fold {fold_number} validation"
        )

    print("Step 5: Comparing models...")

    models = build_models()

    comparison = compare_models(
        models,
        X_train,
        y_train,
        cv_folds,
    )

    comparison.to_csv(
        reports_dir / "model_comparison.csv",
        index=False
    )

    print("\nCross-validation comparison:")
    print(comparison)

    # Select the highest cross-validated AP.
    best_name = comparison.iloc[0]["model"]
    best_model = models[best_name]

    print("\nSelected model:", best_name)

    print("Step 6: Fitting selected model on training data...")

    best_model.fit(X_train, y_train)

    print("Step 7: Final held-out test evaluation...")

    predictions, probabilities, metrics = (
        calculate_test_metrics(
            best_model,
            X_test,
            y_test,
        )
    )

    metrics["selected_model"] = best_name
    metrics["train_rows"] = len(X_train)
    metrics["test_rows"] = len(X_test)
    metrics["train_end_date"] = str(
        train_df["inspection_date"].max().date()
    )
    metrics["test_start_date"] = str(
        test_df["inspection_date"].min().date()
    )

    with open(
        reports_dir / "test_metrics.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(metrics, file, indent=4)

    # Confusion matrix with explicit class order.
    cm = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1],
    )

    fig, ax = plt.subplots(figsize=(6, 5))

    ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Pass", "Fail"],
    ).plot(ax=ax, cmap="Blues", colorbar=False)

    ax.set_title("Held-Out Test Confusion Matrix")

    fig.tight_layout()

    fig.savefig(
        figures_dir / "confusion_matrix.png",
        dpi=150,
    )

    plt.close(fig)

    print("Step 8: Analyzing model errors...")

    mistakes, subgroups, error_counts = (
        save_error_analysis(
            test_df,
            predictions,
            probabilities,
            reports_dir,
        )
    )

    print("Error counts:", error_counts)
    print("Misclassified rows:", len(mistakes))
    print("Subgroup results:")
    print(subgroups)

    with open(
        reports_dir / "error_counts.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(error_counts, file, indent=4)

    print("Step 9: Saving fitted pipeline...")

    model_path = models_dir / "best_pipeline.joblib"

    joblib.dump(best_model, model_path)

    # Verify the saved model can be loaded.
    loaded_model = joblib.load(model_path)

    check_predictions = loaded_model.predict(X_test.head(3))

    print("Reloaded model predictions:", check_predictions)

    print("\nPart B completed successfully.")
    print("Selected model:", best_name)
    print("Test metrics:", metrics)
    print("Saved model:", model_path)


if __name__ == "__main__":
    main()
