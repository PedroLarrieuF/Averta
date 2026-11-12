#!/usr/bin/env python
"""Train Isolation Forest model for anomaly detection on historical discrepancies."""

import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, precision_recall_fscore_support
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

# Feature columns in the exact order used during feature extraction
FEATURE_COLUMNS = [
    "rule_type_hash",
    "carrier_id_hash",
    "client_id_hash",
    "value",
    "weight",
    "volume",
    "uf_origem_encoded",
    "uf_destino_encoded",
    "diff_pct",
    "severity_encoded",
    "document_type_encoded",
    "distance_km",
    "eixos",
    "has_icms",
    "has_freight_value",
]


def load_dataset(data_path: str = "data/discrepancies_history.parquet") -> pd.DataFrame:
    """Load the prepared dataset."""
    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {data_path}. Run prepare_ml_dataset.py first."
        )

    df = pd.read_parquet(path)
    return df


def prepare_features(df: pd.DataFrame) -> tuple:
    """Prepare features and labels for training."""
    # Ensure all feature columns exist
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = 0.0

    X = df[FEATURE_COLUMNS].values
    y = df["label"].values  # 1 = normal, -1 = anomaly

    # Handle any NaN/Inf values
    X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)

    return X, y


def train_isolation_forest(
    X: np.ndarray,
    contamination: float = 0.05,
    n_estimators: int = 200,
    max_samples: int = 256,
    random_state: int = 42,
) -> tuple:
    """Train Isolation Forest model with given hyperparameters."""

    model = IsolationForest(
        contamination=contamination,
        n_estimators=n_estimators,
        max_samples=max_samples,
        random_state=random_state,
        n_jobs=-1,
        verbose=1,
    )

    model.fit(X)

    # Get anomaly scores (negative = anomaly)
    scores = model.decision_function(X)
    predictions = model.predict(X)  # 1 = normal, -1 = anomaly

    return model, scores, predictions


def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray, scores: np.ndarray) -> dict:
    """Evaluate model performance on labeled data."""
    # Convert to binary: 1 = normal, 0 = anomaly (for sklearn metrics)
    y_true_bin = (y_true == 1).astype(int)
    y_pred_bin = (y_pred == 1).astype(int)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true_bin, y_pred_bin, average="binary", zero_division=0
    )

    # Also get per-class metrics
    report = classification_report(
        y_true_bin, y_pred_bin, target_names=["Anomaly", "Normal"], output_dict=True
    )

    metrics = {
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "anomaly_rate_true": float((y_true == -1).mean()),
        "anomaly_rate_pred": float((y_pred == -1).mean()),
        "classification_report": report,
    }

    return metrics


def temporal_cross_validation(X: np.ndarray, y: np.ndarray, n_splits: int = 5) -> list:
    """Perform temporal cross-validation for time series data."""
    tscv = TimeSeriesSplit(n_splits=n_splits)
    cv_results = []

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_train, X_test = X[train_idx], X[test_idx]
        _y_train, y_test = y[train_idx], y[test_idx]

        # Train on fold
        model, _, _ = train_isolation_forest(X_train)
        scores = model.decision_function(X_test)
        preds = model.predict(X_test)

        # Evaluate
        metrics = evaluate_model(y_test, preds, scores)
        metrics["fold"] = fold
        metrics["train_size"] = len(train_idx)
        metrics["test_size"] = len(test_idx)
        cv_results.append(metrics)

    # Aggregate
    np.mean([r["precision"] for r in cv_results])
    np.mean([r["recall"] for r in cv_results])
    np.mean([r["f1_score"] for r in cv_results])

    return cv_results


def save_model(model: IsolationForest, scaler: StandardScaler, metrics: dict, version: str = None):
    """Save trained model and metadata."""
    if version is None:
        version = datetime.utcnow().strftime("v%Y%m%d_%H%M%S")

    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)

    model_path = models_dir / f"isolation_forest_{version}.joblib"
    scaler_path = models_dir / f"scaler_{version}.joblib"
    metadata_path = models_dir / f"metadata_{version}.json"

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    metadata = {
        "version": version,
        "trained_at": datetime.utcnow().isoformat(),
        "feature_columns": FEATURE_COLUMNS,
        "model_params": {
            "contamination": model.contamination,
            "n_estimators": model.n_estimators,
            "max_samples": model.max_samples,
            "random_state": model.random_state,
        },
        "metrics": metrics,
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    # Also save as "latest" for easy loading
    latest_model = models_dir / "isolation_forest_latest.joblib"
    latest_scaler = models_dir / "scaler_latest.joblib"
    latest_metadata = models_dir / "metadata_latest.json"

    joblib.dump(model, latest_model)
    joblib.dump(scaler, latest_scaler)
    with open(latest_metadata, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    return version


def hyperparameter_tuning(X: np.ndarray, y: np.ndarray) -> dict:
    """Simple hyperparameter search for Isolation Forest."""
    param_grid = {
        "contamination": [0.01, 0.03, 0.05, 0.08, 0.1],
        "n_estimators": [100, 200, 300],
        "max_samples": [128, 256, 512],
    }

    best_score = -1
    best_params = {}

    for contamination in param_grid["contamination"]:
        for n_estimators in param_grid["n_estimators"]:
            for max_samples in param_grid["max_samples"]:
                if max_samples > len(X):
                    continue

                model = IsolationForest(
                    contamination=contamination,
                    n_estimators=n_estimators,
                    max_samples=max_samples,
                    random_state=42,
                    n_jobs=-1,
                )
                model.fit(X)
                preds = model.predict(X)

                # Use F1 on anomaly class
                y_bin = (y == 1).astype(int)
                p_bin = (preds == 1).astype(int)
                _, _, f1, _ = precision_recall_fscore_support(
                    y_bin, p_bin, average="binary", zero_division=0
                )

                if f1 > best_score:
                    best_score = f1
                    best_params = {
                        "contamination": contamination,
                        "n_estimators": n_estimators,
                        "max_samples": max_samples,
                    }

    return best_params


def main():
    """Main training pipeline."""

    # Load dataset
    df = load_dataset()

    # Prepare features
    X, y = prepare_features(df)

    # Scale features (important for Isolation Forest with mixed scales)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Hyperparameter tuning (optional, comment out for speed)
    # best_params = hyperparameter_tuning(X_scaled, y)
    # For now, use reasonable defaults
    best_params = {
        "contamination": 0.05,
        "n_estimators": 200,
        "max_samples": min(256, len(X_scaled)),
    }

    # Temporal cross-validation
    cv_results = temporal_cross_validation(X_scaled, y)

    # Train final model on all data
    model, scores, predictions = train_isolation_forest(X_scaled, **best_params)

    # Final evaluation
    metrics = evaluate_model(y, predictions, scores)
    metrics["cv_results"] = cv_results

    # Save model
    version = save_model(model, scaler, metrics)

    # Print threshold info

    return version


if __name__ == "__main__":
    main()
