from __future__ import annotations

from typing import Any, Dict, List

from ..utils import coerce_number


def evaluate_model(model: Any, rows: List[Dict[str, Any]], label_key: str = "__label__") -> Dict[str, Any]:
    try:
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install the 'ml' extra: pip install -e .[ml]") from exc

    X = [{k: v for k, v in row.items() if k not in {label_key, "__label__"}} for row in rows]
    y = []
    for row in rows:
        raw_label = row.get(label_key)
        if raw_label is None and label_key != "__label__":
            raw_label = row.get("__label__")
        label = coerce_number(raw_label)
        if label is None:
            raise ValueError(f"Missing label key: {label_key}")
        y.append(int(label))
    preds = model.predict(X)
    probas = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else None
    return {
        "accuracy": float(accuracy_score(y, preds)),
        "precision": float(precision_score(y, preds, zero_division=0)),
        "recall": float(recall_score(y, preds, zero_division=0)),
        "f1": float(f1_score(y, preds, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, probas)) if probas is not None and len(set(y)) > 1 else None,
        "n": len(rows),
    }
