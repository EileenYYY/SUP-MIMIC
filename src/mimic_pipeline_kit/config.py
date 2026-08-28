from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import json

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class DatabaseConfig:
    dsn: str
    schemas: Dict[str, str] = field(default_factory=dict)


@dataclass
class PathConfig:
    sql_dir: Path
    output_dir: Path
    raw_dir: Path
    case_dir: Path
    manifest_dir: Path


@dataclass
class JobConfig:
    name: str
    sql: Path
    output: Path
    format: str = "jsonl"
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScreeningConfig:
    age_min: int | None = None
    require_icu: bool = False
    min_admissions: int | None = None
    excluded_admission_types: List[str] = field(default_factory=list)
    required_outputs: List[str] = field(default_factory=list)


@dataclass
class PipelineConfig:
    root: Path
    database: DatabaseConfig
    paths: PathConfig
    defaults: Dict[str, Any]
    jobs: List[JobConfig]
    screening: ScreeningConfig


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_mapping(path: Path) -> Dict[str, Any]:
    if path.suffix.lower() in {".json"}:
        return json.loads(_load_text(path))
    if yaml is None:
        raise RuntimeError("PyYAML is required to read YAML configuration files.")
    data = yaml.safe_load(_load_text(path))
    if not isinstance(data, dict):
        raise ValueError("Configuration file must contain a mapping at the top level.")
    return data


def _resolve_path(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def load_config(path: str | Path) -> PipelineConfig:
    config_path = Path(path).resolve()
    root = config_path.parent.parent
    data = _load_mapping(config_path)

    database = DatabaseConfig(
        dsn=str(data["database"]["dsn"]),
        schemas=dict(data.get("database", {}).get("schemas", {})),
    )

    paths_raw = data["paths"]
    paths = PathConfig(
        sql_dir=_resolve_path(root, paths_raw["sql_dir"]),
        output_dir=_resolve_path(root, paths_raw["output_dir"]),
        raw_dir=_resolve_path(root, paths_raw["raw_dir"]),
        case_dir=_resolve_path(root, paths_raw["case_dir"]),
        manifest_dir=_resolve_path(root, paths_raw["manifest_dir"]),
    )

    defaults = dict(data.get("defaults", {}))
    jobs: List[JobConfig] = []
    for row in data.get("jobs", []):
        jobs.append(
            JobConfig(
                name=row["name"],
                sql=_resolve_path(root, row["sql"]),
                output=_resolve_path(root, row["output"]),
                format=row.get("format", "jsonl"),
                params=dict(row.get("params", {})),
            )
        )

    screening_raw = data.get("screening", {})
    screening = ScreeningConfig(
        age_min=screening_raw.get("age_min"),
        require_icu=bool(screening_raw.get("require_icu", False)),
        min_admissions=screening_raw.get("min_admissions"),
        excluded_admission_types=list(screening_raw.get("excluded_admission_types", [])),
        required_outputs=list(screening_raw.get("required_outputs", [])),
    )

    return PipelineConfig(
        root=root,
        database=database,
        paths=paths,
        defaults=defaults,
        jobs=jobs,
        screening=screening,
    )

