from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.frozen import FrozenEstimator
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from maintai_ml.artifact import ModelArtifact
from maintai_ml.data import FAILURE_MODE_COLUMNS, load_dataset, validate_dataset
from maintai_ml.features import ENGINEERED_FEATURES, RAW_FEATURES, PhysicalFeatureEngineer

SEED = 42
NUMERIC_FEATURES = [name for name in RAW_FEATURES if name != "type"] + ENGINEERED_FEATURES


def make_pipeline(estimator: object) -> Pipeline:
    preprocess = ColumnTransformer(
        [
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("type", OneHotEncoder(handle_unknown="ignore"), ["type"]),
        ]
    )
    return Pipeline(
        [("features", PhysicalFeatureEngineer()), ("preprocess", preprocess), ("model", estimator)]
    )


def candidate_models() -> dict[str, object]:
    return {
        "logistic_regression": LogisticRegression(
            class_weight="balanced", max_iter=2_000, random_state=SEED
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=350,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=SEED,
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=350,
            min_samples_leaf=2,
            class_weight="balanced",
            n_jobs=-1,
            random_state=SEED,
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            learning_rate=0.07,
            max_iter=250,
            max_leaf_nodes=21,
            class_weight="balanced",
            random_state=SEED,
        ),
    }


def select_threshold(
    y_true: pd.Series, probabilities: np.ndarray
) -> tuple[float, dict[str, float]]:
    precision, recall, thresholds = precision_recall_curve(y_true, probabilities)
    # F2 gives missed failures four times the weight of false alerts.
    # The precision floor keeps the resulting maintenance queue useful.
    beta_sq = 4.0
    f2 = (
        (1 + beta_sq)
        * precision[:-1]
        * recall[:-1]
        / (beta_sq * precision[:-1] + recall[:-1] + 1e-12)
    )
    eligible = np.where(precision[:-1] >= 0.25, f2, -1)
    index = int(np.argmax(eligible)) if eligible.max() >= 0 else int(np.argmax(f2))
    return float(thresholds[index]), {
        "selection_metric": "F2 with validation precision >= 0.25",
        "validation_precision": float(precision[index]),
        "validation_recall": float(recall[index]),
        "validation_f2": float(f2[index]),
    }


def metrics(y_true: pd.Series, probabilities: np.ndarray, threshold: float) -> dict[str, object]:
    predictions = probabilities >= threshold
    return {
        "precision": float(precision_score(y_true, predictions, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, zero_division=0)),
        "f1": float(f1_score(y_true, predictions, zero_division=0)),
        "pr_auc": float(average_precision_score(y_true, probabilities)),
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "brier_score": float(brier_score_loss(y_true, probabilities)),
        "confusion_matrix": confusion_matrix(y_true, predictions).tolist(),
    }


def train(data_path: Path, artifact_path: Path, report_dir: Path) -> dict[str, object]:
    frame = load_dataset(data_path)
    quality = validate_dataset(frame)
    X, y = frame[RAW_FEATURES], frame["machine_failure"]
    X_development, X_test, y_development, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED
    )
    X_train, X_validation, y_train, y_validation = train_test_split(
        X_development, y_development, test_size=0.25, stratify=y_development, random_state=SEED
    )

    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    comparisons: dict[str, dict[str, float]] = {}
    for name, estimator in candidate_models().items():
        scores = cross_validate(
            make_pipeline(estimator),
            X_train,
            y_train,
            cv=folds,
            scoring={"pr_auc": "average_precision", "roc_auc": "roc_auc", "recall": "recall"},
            n_jobs=-1,
        )
        comparisons[name] = {
            metric: float(np.mean(scores[f"test_{metric}"]))
            for metric in ("pr_auc", "roc_auc", "recall")
        }
        comparisons[name]["pr_auc_std"] = float(np.std(scores["test_pr_auc"]))

    selected_name = max(comparisons, key=lambda name: comparisons[name]["pr_auc"])
    raw_pipeline = make_pipeline(candidate_models()[selected_name])
    raw_pipeline.fit(X_train, y_train)
    calibrated = CalibratedClassifierCV(FrozenEstimator(raw_pipeline), method="sigmoid")
    calibrated.fit(X_validation, y_validation)
    validation_probabilities = calibrated.predict_proba(X_validation)[:, 1]
    threshold, threshold_details = select_threshold(y_validation, validation_probabilities)
    test_probabilities = calibrated.predict_proba(X_test)[:, 1]
    test_metrics = metrics(y_test, test_probabilities, threshold)

    permutation = permutation_importance(
        calibrated,
        X_test,
        y_test,
        scoring="average_precision",
        n_repeats=12,
        random_state=SEED,
        n_jobs=-1,
    )
    importance = sorted(
        [
            {"feature": feature, "importance": float(mean), "std": float(std)}
            for feature, mean, std in zip(
                RAW_FEATURES, permutation.importances_mean, permutation.importances_std, strict=True
            )
        ],
        key=lambda item: item["importance"],
        reverse=True,
    )
    calibration_true, calibration_pred = calibration_curve(
        y_test, test_probabilities, n_bins=6, strategy="quantile"
    )
    created_at = datetime.now(UTC).isoformat()
    version = f"ai4i-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    metadata = {
        "model_version": version,
        "trained_at": created_at,
        "algorithm": selected_name,
        "dataset": "UCI AI4I 2020 (ID 601)",
        "dataset_is_synthetic": True,
        "features": RAW_FEATURES,
        "excluded_leakage_columns": FAILURE_MODE_COLUMNS,
        "decision_threshold": threshold,
        "risk_mapping": {
            "HEALTHY": f"p < {threshold * 0.25:.4f}",
            "LOW": f"{threshold * 0.25:.4f} <= p < {threshold * 0.6:.4f}",
            "MEDIUM": f"{threshold * 0.6:.4f} <= p < {threshold:.4f}",
            "HIGH": f"{threshold:.4f} <= p < {min(1, threshold * 1.5):.4f}",
            "CRITICAL": f"p >= {min(1, threshold * 1.5):.4f}",
        },
        "failure_mode_prediction_supported": False,
        "test_metrics": test_metrics,
        "model_comparison": comparisons,
        "threshold_selection": threshold_details,
        "feature_importance": importance,
        "calibration_curve": {
            "mean_predicted_probability": calibration_pred.tolist(),
            "observed_failure_rate": calibration_true.tolist(),
        },
        "split": {"train": len(X_train), "validation": len(X_validation), "test": len(X_test)},
        "data_quality": quality,
    }
    reference_values = {
        "type": str(X_train["type"].mode().iloc[0]),
        **{name: float(X_train[name].median()) for name in RAW_FEATURES if name != "type"},
    }
    training_ranges = {
        name: {"min": float(X_train[name].min()), "max": float(X_train[name].max())}
        for name in RAW_FEATURES
        if name != "type"
    }
    artifact = ModelArtifact(calibrated, metadata, reference_values, training_ranges)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, artifact_path)
    (report_dir / "model_report.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (report_dir / "data_quality.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and evaluate the MaintAI model")
    parser.add_argument("--data", type=Path, default=Path("ml/data/raw/ai4i2020.csv"))
    parser.add_argument("--artifact", type=Path, default=Path("ml/artifacts/model.joblib"))
    parser.add_argument("--reports", type=Path, default=Path("ml/reports"))
    args = parser.parse_args()
    report = train(args.data, args.artifact, args.reports)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
