from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import re

from .db import fetch_all
from .exporters import dump_csv, dump_json, dump_jsonl, ensure_parent


PLACEHOLDER_RE = re.compile(r"^\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}$")


def _resolve_value(value: Any, context: Dict[str, Any]) -> Any:
    if isinstance(value, str):
        match = PLACEHOLDER_RE.match(value.strip())
        if match:
            return context.get(match.group(1))
        return value
    if isinstance(value, dict):
        return {key: _resolve_value(inner, context) for key, inner in value.items()}
    if isinstance(value, list):
        return [_resolve_value(item, context) for item in value]
    return value


@dataclass
class ExtractionResult:
    name: str
    output: Path
    rows: int
    sql: Path


def run_job(conn, job, context: Dict[str, Any]) -> ExtractionResult:
    sql_text = job.sql.read_text(encoding="utf-8")
    params = _resolve_value(job.params, context)
    rows = fetch_all(conn, sql_text, params)
    ensure_parent(job.output)

    fmt = job.format.lower()
    if fmt == "jsonl":
        count = dump_jsonl(job.output, rows)
    elif fmt == "json":
        dump_json(job.output, rows)
        count = len(rows)
    elif fmt == "csv":
        count = dump_csv(job.output, rows)
    else:
        raise ValueError(f"Unsupported output format: {job.format}")

    return ExtractionResult(name=job.name, output=job.output, rows=count, sql=job.sql)

