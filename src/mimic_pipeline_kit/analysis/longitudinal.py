from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List


def bucket_time_series(
    records: Iterable[Dict[str, Any]],
    id_key: str,
    time_key: str,
    value_key: str,
    bucket_key: str | None = None,
) -> Dict[str, Any]:
    grouped = defaultdict(list)
    for row in records:
        grouped[str(row.get(id_key))].append(row)

    output: Dict[str, Any] = {}
    for entity_id, rows in grouped.items():
        ordered = sorted(rows, key=lambda row: str(row.get(time_key, "")))
        series = []
        for row in ordered:
            series.append(
                {
                    "time": row.get(time_key),
                    "value": row.get(value_key),
                    "bucket": row.get(bucket_key) if bucket_key else None,
                }
            )
        output[entity_id] = series
    return output

