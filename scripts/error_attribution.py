#!/usr/bin/env python3
"""Classify model errors into SUP-MIMIC failure modes.

This script reads model result JSONL and a private local case directory. It
does not require publishing patient features. For restricted data, run it in
the same controlled environment as the benchmark.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from tqdm import tqdm


FAILURE_MODES = [
    "combinatorial_neglect",
    "feature_misweighting",
    "comorbidity_conflation",
    "biomarker_omission",
    "format_or_unclear_output",
]


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Attribute SUP-MIMIC diagnostic errors.")
    parser.add_argument("--results-jsonl", type=Path, required=True)
    parser.add_argument("--case-root", type=Path, required=True)
    parser.add_argument("--output-jsonl", type=Path, required=True)
    parser.add_argument("--base-url", default="https://api.openai.com/v1/chat/completions")
    parser.add_argument("--model", default="gpt-4o")
    parser.add_argument("--api-key-env", default="SUP_MIMIC_API_KEY")
    parser.add_argument("--timeout", type=int, default=90)
    return parser.parse_args()


def normalize_prediction(value: Any) -> int | None:
    text = str(value).strip().lower()
    if text in {"yes", "y", "true", "1", "是"}:
        return 1
    if text in {"no", "n", "false", "0", "否"}:
        return 0
    return None


def iter_errors(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("correct") is False:
            yield record


def load_case_features(case_root: Path, record: dict) -> str:
    disease = record["disease"]
    cls = record.get("class", "")
    disease_dir = case_root / disease
    candidates = sorted(disease_dir.glob(f"{cls}*.csv")) or sorted(disease_dir.glob("*.csv"))
    case_id = str(record.get("case_id", ""))
    for path in candidates:
        df = pd.read_csv(path)
        if "case_id" in df.columns:
            hit = df[df["case_id"].astype(str) == case_id]
            if not hit.empty:
                row = hit.iloc[0]
                return "\n".join(
                    f"{k}: {v}"
                    for k, v in row.items()
                    if pd.notna(v) and k not in {"subject_id", "hadm_id", "stay_id", "dicom_id"}
                )
    return "case features unavailable"


def build_messages(record: dict, features: str) -> list[dict[str, str]]:
    system = (
        "You are auditing a diagnostic model's error. Classify the error into one "
        "failure mode and return JSON only."
    )
    user = {
        "disease": record.get("disease"),
        "ground_truth": record.get("ground_truth"),
        "model_prediction": record.get("model_prediction"),
        "model_rationale": record.get("rationale") or record.get("explanation"),
        "features": features[:6000],
        "allowed_failure_modes": FAILURE_MODES,
        "json_schema": {
            "error_type": "one allowed failure mode",
            "analysis": "brief evidence-grounded explanation",
        },
    }
    return [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(user)}]


def call_api(args: argparse.Namespace, messages: list[dict[str, str]]) -> dict:
    key = os.getenv(args.api_key_env)
    if not key:
        raise SystemExit(f"Missing API key environment variable: {args.api_key_env}")
    payload = {
        "model": args.model,
        "messages": messages,
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
    }
    response = requests.post(
        args.base_url,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload,
        timeout=args.timeout,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content[content.find("{") : content.rfind("}") + 1])


def main() -> None:
    args = build_args()
    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if args.output_jsonl.exists():
        for line in args.output_jsonl.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(line).get("row_unique_id"))
            except Exception:
                continue

    with args.output_jsonl.open("a", encoding="utf-8") as out:
        for record in tqdm(list(iter_errors(args.results_jsonl)), desc="errors"):
            uid = record.get("row_unique_id")
            if uid in done:
                continue
            features = load_case_features(args.case_root, record)
            result = call_api(args, build_messages(record, features))
            output = {
                "row_unique_id": uid,
                "case_id": record.get("case_id"),
                "disease": record.get("disease"),
                "class": record.get("class"),
                "ground_truth": record.get("ground_truth"),
                "model_prediction": record.get("model_prediction"),
                "error_type": result.get("error_type"),
                "attribution_analysis": result.get("analysis"),
            }
            out.write(json.dumps(output, ensure_ascii=False) + "\n")
            out.flush()
            time.sleep(0.5)
    print(f"Wrote {args.output_jsonl}")


if __name__ == "__main__":
    main()
