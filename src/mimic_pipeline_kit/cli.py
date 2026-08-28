from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import yaml

from .builders import build_case_profile
from .analysis.descriptive import group_summary, summarize_records, value_counts
from .config import load_config
from .db import connect
from .exporters import build_manifest, dump_json
from .extractor import run_job
from .filters import screen_profile
from .ml.evaluate import evaluate_model
from .ml.features import build_feature_rows, load_profiles
from .ml.io import load_feature_table, write_feature_table
from .ml.train import load_model, save_model, train_binary_classifier
from .utils import read_jsonl


def _load_rules(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _validate_config(cfg) -> list[str]:
    issues: list[str] = []
    if not cfg.database.dsn:
        issues.append("missing database.dsn")
    for job in cfg.jobs:
        if not job.sql.exists():
            issues.append(f"missing sql: {job.sql}")
        if not job.name:
            issues.append("job without name")
    return issues


def cmd_validate(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    issues = _validate_config(cfg)
    payload = {
        "root": str(cfg.root),
        "jobs": [job.name for job in cfg.jobs],
        "output_dir": str(cfg.paths.output_dir),
        "valid": not issues,
        "issues": issues,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_run(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    context = {
        "subject_id": args.subject_id or cfg.defaults.get("subject_id"),
        "hadm_id": args.hadm_id or cfg.defaults.get("hadm_id"),
        "stay_id": args.stay_id or cfg.defaults.get("stay_id"),
    }

    conn = connect(cfg.database.dsn)
    results = []
    try:
        for job in cfg.jobs:
            result = run_job(conn, job, context)
            results.append(
                {
                    "name": result.name,
                    "output": str(result.output),
                    "rows": result.rows,
                    "sql": str(result.sql),
                }
            )
    finally:
        conn.close()

    cfg.paths.manifest_dir.mkdir(parents=True, exist_ok=True)
    cfg.paths.raw_dir.mkdir(parents=True, exist_ok=True)
    cfg.paths.case_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(results, source="mimic-pipeline-kit")
    dump_json(cfg.paths.manifest_dir / "extraction_manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def cmd_build_case(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    context = {
        "subject_id": args.subject_id or cfg.defaults.get("subject_id"),
        "hadm_id": args.hadm_id or cfg.defaults.get("hadm_id"),
        "stay_id": args.stay_id or cfg.defaults.get("stay_id"),
    }
    profile = build_case_profile(args.input_dir, context)
    dump_json(args.output, profile)
    print(json.dumps({"output": str(args.output)}, ensure_ascii=False, indent=2))


def cmd_screen(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    rules = _load_rules(args.rules) if args.rules else cfg.screening.__dict__
    profile = json.loads(args.input.read_text(encoding="utf-8"))
    result = screen_profile(profile, rules)
    payload = {
        "passed": result.passed,
        "reasons": result.reasons,
        "subject_id": profile.get("subject_id"),
    }
    dump_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_build_features(args: argparse.Namespace) -> None:
    profiles = load_profiles(args.input)
    rows = build_feature_rows(
        profiles,
        label_key=args.label_key,
        drop_keys=args.drop_keys or [],
    )
    write_feature_table(args.output, rows)
    print(json.dumps({"output": str(args.output), "rows": len(rows)}, ensure_ascii=False, indent=2))


def _load_records_for_stats(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix in {".jsonl"}:
        return read_jsonl(path)
    if suffix in {".json"}:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [row for row in data if isinstance(row, dict)]
        if isinstance(data, dict):
            return [data]
        return []
    if suffix in {".csv"}:
        return load_feature_table(path)
    raise ValueError(f"Unsupported input: {path}")


def cmd_stats_summary(args: argparse.Namespace) -> None:
    records = _load_records_for_stats(args.input)
    if args.group_key:
        payload = group_summary(records, args.group_key, args.fields or None)
    elif args.field:
        payload = {args.field: value_counts(records, args.field)}
    else:
        payload = summarize_records(records, args.fields or None)
    dump_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_train_model(args: argparse.Namespace) -> None:
    rows = load_feature_table(args.input)
    model, metrics = train_binary_classifier(rows, label_key=args.label_key, test_size=args.test_size)
    save_model(args.model_output, model)
    dump_json(args.metrics_output, metrics)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


def cmd_evaluate_model(args: argparse.Namespace) -> None:
    rows = load_feature_table(args.input)
    model = load_model(args.model)
    metrics = evaluate_model(model, rows, label_key=args.label_key)
    dump_json(args.output, metrics)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mimic-pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate-config", help="Validate config and show a summary.")
    p.add_argument("--config", type=Path, required=True)
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("run", help="Run extraction jobs.")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--subject-id", type=int, default=None)
    p.add_argument("--hadm-id", type=int, default=None)
    p.add_argument("--stay-id", type=int, default=None)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("build-case", help="Build one case profile from raw outputs.")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--input-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--subject-id", type=int, default=None)
    p.add_argument("--hadm-id", type=int, default=None)
    p.add_argument("--stay-id", type=int, default=None)
    p.set_defaults(func=cmd_build_case)

    p = sub.add_parser("screen", help="Screen a case profile with rules.")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--rules", type=Path, default=None)
    p.set_defaults(func=cmd_screen)

    p = sub.add_parser("build-features", help="Flatten case profiles into a feature table.")
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--label-key", type=str, default="label")
    p.add_argument("--drop-keys", nargs="*", default=[])
    p.set_defaults(func=cmd_build_features)

    p = sub.add_parser("stats-summary", help="Summarize a JSON/JSONL/CSV record file.")
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--group-key", type=str, default=None)
    p.add_argument("--field", type=str, default=None)
    p.add_argument("--fields", nargs="*", default=[])
    p.set_defaults(func=cmd_stats_summary)

    p = sub.add_parser("train-model", help="Train a baseline binary classifier.")
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--model-output", type=Path, required=True)
    p.add_argument("--metrics-output", type=Path, required=True)
    p.add_argument("--label-key", type=str, default="__label__")
    p.add_argument("--test-size", type=float, default=0.2)
    p.set_defaults(func=cmd_train_model)

    p = sub.add_parser("evaluate-model", help="Evaluate a saved model on a feature table.")
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--label-key", type=str, default="__label__")
    p.set_defaults(func=cmd_evaluate_model)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
