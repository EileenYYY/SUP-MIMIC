from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean, median
from typing import Any, Dict, Iterable, List

from ..utils import coerce_number


def _is_number(value: Any) -> bool:
    coerced = coerce_number(value)
    return isinstance(coerced, (int, float)) and not isinstance(coerced, bool)


def summarize_records(records: Iterable[Dict[str, Any]], fields: List[str] | None = None) -> Dict[str, Any]:
    rows = list(records)
    if not rows:
        return {"n": 0, "fields": {}}

    if fields is None:
        sample = rows[0]
        fields = [key for key, value in sample.items() if _is_number(value)]

    summary: Dict[str, Any] = {"n": len(rows), "fields": {}}
    for field in fields:
        values = [coerce_number(row.get(field)) for row in rows]
        numeric = [float(v) for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
        missing = sum(1 for value in values if value in (None, ""))
        summary["fields"][field] = {
            "n": len(values),
            "missing": missing,
            "non_missing": len(values) - missing,
            "mean": mean(numeric) if numeric else None,
            "median": median(numeric) if numeric else None,
            "min": min(numeric) if numeric else None,
            "max": max(numeric) if numeric else None,
        }
    return summary


def group_summary(
    records: Iterable[Dict[str, Any]],
    group_key: str,
    numeric_fields: List[str] | None = None,
) -> Dict[str, Any]:
    rows = list(records)
    buckets: Dict[Any, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[row.get(group_key)].append(row)

    return {
        "n": len(rows),
        "groups": {
            str(group): summarize_records(group_rows, numeric_fields)
            for group, group_rows in buckets.items()
        },
    }


def value_counts(records: Iterable[Dict[str, Any]], field: str) -> Dict[str, int]:
    counter = Counter()
    for row in records:
        counter[str(row.get(field))] += 1
    return dict(counter)

