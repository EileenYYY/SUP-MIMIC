#!/usr/bin/env python3
"""Run SUP-MIMIC inference through an OpenAI-compatible chat completions API.

For real MIMIC-derived inputs, use this script only when your data-use approval
and provider contract allow the transfer. Prefer local models for restricted data.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from tqdm import tqdm


ID_COLUMNS = {"subject_id", "hadm_id", "stay_id", "dicom_id", "study_id"}


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate SUP-MIMIC cases with an API model.")
    parser.add_argument("--root-dir", type=Path, required=True)
    parser.add_argument("--save-dir", type=Path, required=True)
    parser.add_argument("--base-url", default="https://api.openai.com/v1/chat/completions")
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key-env", default="SUP_MIMIC_API_KEY")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=600)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--max-retries", type=int, default=5)
    return parser.parse_args()


def build_prompt(disease: str, row: pd.Series) -> list[dict[str, str]]:
    system = (
        "You are a clinical diagnostic assistant. Use only the provided structured "
        "features. Return exactly one JSON object with fields disease, prediction, "
        "confidence, rationale, and explanation."
    )
    items = []
    for col, val in row.items():
        if col in ID_COLUMNS or col in {"case_id", "pair_id"} or pd.isna(val):
            continue
        items.append(f"{col}: {val}")
    user = (
        f"Decide whether the patient has [{disease}].\n"
        "prediction must be either yes or no.\n\n"
        "Structured features:\n"
        + "\n".join(items[:80])
        + '\n\nReturn JSON only, for example: '
        + json.dumps(
            {
                "disease": disease,
                "prediction": "yes",
                "confidence": 0.73,
                "rationale": "short clinical rationale",
                "explanation": "brief evidence-based explanation",
            }
        )
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def extract_json(text: str) -> dict[str, Any]:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("model output does not contain a JSON object")
    return json.loads(text[start : end + 1])


def call_api(args: argparse.Namespace, messages: list[dict[str, str]]) -> dict[str, Any]:
    key = os.getenv(args.api_key_env)
    if not key:
        raise SystemExit(f"Missing API key environment variable: {args.api_key_env}")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": args.model,
        "messages": messages,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "response_format": {"type": "json_object"},
    }
    last_error = None
    for attempt in range(args.max_retries):
        try:
            response = requests.post(args.base_url, headers=headers, json=payload, timeout=args.timeout)
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                return extract_json(content)
            last_error = f"HTTP {response.status_code}: {response.text[:300]}"
        except Exception as exc:
            last_error = str(exc)
        time.sleep(min(2**attempt, 20))
    raise RuntimeError(last_error or "API call failed")


def iter_case_files(root: Path):
    patterns = ["A_class*.csv", "B_class*.csv", "C_class*.csv", "*病历详细信息.csv"]
    for disease_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for pattern in patterns:
            for path in sorted(disease_dir.glob(pattern)):
                task = "A" if path.name.startswith("A") or "A类" in path.name else (
                    "B" if path.name.startswith("B") or "B类" in path.name else "C"
                )
                yield disease_dir.name, task, path


def normalize_prediction(value: Any) -> int | None:
    text = str(value).strip().lower()
    if text in {"yes", "y", "true", "1", "是"}:
        return 1
    if text in {"no", "n", "false", "0", "否"}:
        return 0
    return None


def main() -> None:
    args = build_args()
    args.save_dir.mkdir(parents=True, exist_ok=True)
    stream_path = args.save_dir / "results_stream.jsonl"
    summary_path = args.save_dir / "summary.csv"
    done = set()
    if stream_path.exists():
        for line in stream_path.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(line)["row_unique_id"])
            except Exception:
                continue

    records = []
    with stream_path.open("a", encoding="utf-8") as out:
        for disease, task, csv_path in iter_case_files(args.root_dir):
            df = pd.read_csv(csv_path)
            for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"{disease}-{task}"):
                row_uid = f"{args.model}|{disease}|{task}|{csv_path.name}|{idx}"
                if row_uid in done:
                    continue
                result = call_api(args, build_prompt(disease, row))
                gt = normalize_prediction(row.get("diseased", row.get("label")))
                pred = normalize_prediction(result.get("prediction"))
                record = {
                    "row_unique_id": row_uid,
                    "case_id": row.get("case_id", f"row_{idx}"),
                    "model_name": args.model,
                    "disease": disease,
                    "class": task,
                    "model_prediction": result.get("prediction"),
                    "model_confidence": result.get("confidence"),
                    "ground_truth": gt,
                    "correct": None if gt is None or pred is None else bool(gt == pred),
                    "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                    "rationale": result.get("rationale"),
                    "explanation": result.get("explanation"),
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                out.flush()
                records.append(record)

    if records:
        df = pd.DataFrame(records)
        df.groupby(["model_name", "disease", "class"], dropna=False).agg(
            samples=("row_unique_id", "count"),
            correct=("correct", "sum"),
            accuracy=("correct", "mean"),
        ).reset_index().to_csv(summary_path, index=False)
        print(f"Wrote {stream_path} and {summary_path}")


if __name__ == "__main__":
    main()
