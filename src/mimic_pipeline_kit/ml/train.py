from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from ..utils import coerce_number


@dataclass
class TrainingResult:
    model_path: Path
    metrics: Dict[str, Any]


def _require_sklearn():
    try:
        from sklearn.feature_extraction import DictVectorizer
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import (
            accuracy_score,
            f1_score,
            precision_score,
            recall_score,
            roc_auc_score,
        )
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import Pipeline
        return {
            "DictVectorizer": DictVectorizer,
            "SimpleImputer": SimpleImputer,
            "LogisticRegression": LogisticRegression,
            "accuracy_score": accuracy_score,
            "f1_score": f1_score,
            "precision_score": precision_score,
            "recall_score": recall_score,
            "roc_auc_score": roc_auc_score,
            "train_test_split": train_test_split,
            "Pipeline": Pipeline,
        }
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install the 'ml' extra: pip install -e .[ml]") from exc


def _prepare_xy(rows: List[Dict[str, Any]], label_key: str) -> tuple[list[dict], list[int]]:
    features: list[dict] = []
    labels: list[int] = []
    for row in rows:
        raw_label = row.get(label_key)
        if raw_label is None and label_key != "__label__":
            raw_label = row.get("__label__")
        label = coerce_number(raw_label)
        if label is None:
            raise ValueError(f"Missing label key: {label_key}")
        labels.append(int(label))
        feature_row = {key: value for key, value in row.items() if key not in {label_key, "__label__"}}
        features.append(feature_row)
    return features, labels


def train_binary_classifier(
    rows: List[Dict[str, Any]],
    label_key: str = "__label__",
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[Any, Dict[str, Any]]:
    sk = _require_sklearn()
    X, y = _prepare_xy(rows, label_key)
    if len(rows) < 2:
        raise ValueError("At least two labeled rows are required for train/test split.")
    class_counts = {label: y.count(label) for label in set(y)}
    stratify = y if len(class_counts) > 1 and min(class_counts.values()) >= 2 else None

    X_train, X_test, y_train, y_test = sk["train_test_split"](
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify,
    )

    pipeline = sk["Pipeline"](
        steps=[
            ("vectorizer", sk["DictVectorizer"](sparse=False)),
            ("imputer", sk["SimpleImputer"](strategy="median")),
            ("model", sk["LogisticRegression"](max_iter=1000)),
        ]
    )
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    probas = pipeline.predict_proba(X_test)[:, 1] if hasattr(pipeline, "predict_proba") else None

    metrics = {
        "accuracy": float(sk["accuracy_score"](y_test, preds)),
        "precision": float(sk["precision_score"](y_test, preds, zero_division=0)),
        "recall": float(sk["recall_score"](y_test, preds, zero_division=0)),
        "f1": float(sk["f1_score"](y_test, preds, zero_division=0)),
        "roc_auc": float(sk["roc_auc_score"](y_test, probas))
        if probas is not None and len(set(y_test)) > 1
        else None,
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
    return pipeline, metrics


def save_model(path: Path, model: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        pickle.dump(model, f)


def load_model(path: Path) -> Any:
    with path.open("rb") as f:
        return pickle.load(f)
