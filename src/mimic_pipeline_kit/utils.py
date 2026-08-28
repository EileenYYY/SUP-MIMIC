from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def flatten_dict(data: Dict[str, Any], prefix: str = "", sep: str = "_") -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, value in data.items():
        new_key = f"{prefix}{sep}{key}" if prefix else str(key)
        if isinstance(value, dict):
            out.update(flatten_dict(value, new_key, sep=sep))
        else:
            out[new_key] = value
    return out


def coerce_number(value: Any) -> Any:
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            if "." in text:
                return float(text)
            return int(text)
        except ValueError:
            try:
                return float(text)
            except ValueError:
                return value
    return value

