from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from ..utils import read_jsonl


def load_profiles(path: Path) -> List[Dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        return read_jsonl(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        return [data]
    raise ValueError(f"Unsupported profile file: {path}")


def _flatten_value(value: Any, prefix: str, out: Dict[str, Any]) -> None:
    if isinstance(value, dict):
        for key, inner in value.items():
            child = f"{prefix}_{key}" if prefix else str(key)
            _flatten_value(inner, child, out)
        return

    if isinstance(value, list):
        out[f"{prefix}_count"] = len(value)
        scalar_values = [item for item in value if not isinstance(item, (dict, list))]
        if scalar_values:
            out[f"{prefix}_unique"] = len({str(item) for item in scalar_values})
            out[f"{prefix}_sample"] = "|".join(sorted({str(item) for item in scalar_values})[:5])
        elif value and isinstance(value[0], dict):
            common_keys = ("icd_code", "drug", "itemid", "item_name", "long_title", "code")
            for key in common_keys:
                values = [item.get(key) for item in value if isinstance(item, dict) and item.get(key) is not None]
                if values:
                    out[f"{prefix}_{key}_unique"] = len({str(item) for item in values})
        return

    out[prefix] = value


def flatten_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    flat: Dict[str, Any] = {}
    for key, value in profile.items():
        _flatten_value(value, str(key), flat)
    return flat


def build_feature_rows(
    profiles: Iterable[Dict[str, Any]],
    label_key: str = "label",
    drop_keys: Sequence[str] | None = None,
) -> List[Dict[str, Any]]:
    drop = set(drop_keys or [])
    rows: List[Dict[str, Any]] = []
    for profile in profiles:
        flat = flatten_profile(profile)
        if label_key in flat:
            flat["__label__"] = flat.pop(label_key)
        elif label_key in profile:
            flat["__label__"] = profile[label_key]
        for key in list(flat):
            if key in drop or key.startswith("generated_at"):
                flat.pop(key, None)
        rows.append(flat)
    return rows

