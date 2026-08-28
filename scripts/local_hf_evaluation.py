#!/usr/bin/env python3
"""Run SUP-MIMIC inference with a local Hugging Face chat model."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer


ID_COLUMNS = {"subject_id", "hadm_id", "stay_id", "dicom_id", "study_id"}


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate SUP-MIMIC with a local HF model.")
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--root-dir", type=Path, required=True)
    parser.add_argument("--save-dir", type=Path, required=True)
    parser.add_argument("--max-new-tokens", type=int, default=160)
    parser.add_argument("--do-sample", action="store_true")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--repetition-penalty", type=float, default=1.05)
    parser.add_argument("--auto-pick-gpu", action="store_true")
    return parser.parse_args()


def auto_pick_best_gpu() -> int | None:
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=index,memory.free", "--format=csv,noheader,nounits"],
            text=True,
        )
        pairs = []
        for line in output.strip().splitlines():
            idx, free = [x.strip() for x in line.split(",")]
            pairs.append((int(idx), int(free)))
        pairs.sort(key=lambda x: x[1], reverse=True)
        return pairs[0][0] if pairs else None
    except Exception:
        return None


def load_model(model_dir: str, auto_pick_gpu: bool):
    if auto_pick_gpu:
        gpu = auto_pick_best_gpu()
        if gpu is not None:
            os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)
    tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        device_map="auto",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        trust_remote_code=True,
    )
    model.eval()
    return tokenizer, model


def build_messages(disease: str, row: pd.Series) -> list[dict[str, str]]:
    system = (
        "You are a clinical diagnostic assistant. Use only the provided structured "
        "features. Return exactly one JSON object."
    )
    features = []
    for col, value in row.items():
        if col in ID_COLUMNS or col in {"case_id", "pair_id"} or pd.isna(value):
            continue
        features.append(f"{col}: {value}")
    user = (
        f"Does the patient have [{disease}]?\n"
        "Return fields: disease, prediction, confidence, rationale, explanation.\n"
        "prediction must be yes or no.\n\n"
        + "\n".join(features[:80])
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def apply_template(tokenizer, messages: list[dict[str, str]]) -> str:
    try:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    except Exception:
        return (
            f"System: {messages[0]['content']}\n"
            f"User: {messages[1]['content']}\n"
            "Assistant:"
        )


def extract_json(text: str) -> dict[str, Any]:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {"prediction": "invalid", "confidence": None, "raw_text": text}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {"prediction": "invalid", "confidence": None, "raw_text": text[start : end + 1]}


def normalize_prediction(value: Any) -> int | None:
    text = str(value).strip().lower()
    if text in {"yes", "y", "true", "1", "是"}:
        return 1
    if text in {"no", "n", "false", "0", "否"}:
        return 0
    return None


def iter_case_files(root: Path):
    for disease_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for csv_path in sorted(disease_dir.glob("*.csv")):
            if csv_path.name == "selected_features.csv":
                continue
            task = "A" if csv_path.name.startswith("A") else (
                "B" if csv_path.name.startswith("B") else "C"
            )
            yield disease_dir.name, task, csv_path


def run_one(tokenizer, model, disease: str, row: pd.Series, args: argparse.Namespace) -> dict:
    prompt = apply_template(tokenizer, build_messages(disease, row))
    inputs = tokenizer([prompt], return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            do_sample=args.do_sample,
            temperature=args.temperature if args.do_sample else None,
            top_p=args.top_p,
            repetition_penalty=args.repetition_penalty,
            max_new_tokens=args.max_new_tokens,
            eos_token_id=tokenizer.eos_token_id,
        )
    full_text = tokenizer.decode(output[0], skip_special_tokens=True)
    source_text = tokenizer.decode(inputs["input_ids"][0].to("cpu"), skip_special_tokens=True)
    return extract_json(full_text[len(source_text) :])


def main() -> None:
    args = build_args()
    args.save_dir.mkdir(parents=True, exist_ok=True)
    stream_path = args.save_dir / "local_results.jsonl"
    tokenizer, model = load_model(args.model_dir, args.auto_pick_gpu)

    with stream_path.open("a", encoding="utf-8") as out:
        for disease, task, csv_path in iter_case_files(args.root_dir):
            df = pd.read_csv(csv_path)
            for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"{disease}-{task}"):
                result = run_one(tokenizer, model, disease, row, args)
                gt = normalize_prediction(row.get("diseased", row.get("label")))
                pred = normalize_prediction(result.get("prediction"))
                record = {
                    "row_unique_id": f"{Path(args.model_dir).name}|{disease}|{task}|{idx}",
                    "case_id": row.get("case_id", f"row_{idx}"),
                    "disease": disease,
                    "class": task,
                    "model_prediction": result.get("prediction"),
                    "model_confidence": result.get("confidence"),
                    "ground_truth": gt,
                    "correct": None if gt is None or pred is None else bool(gt == pred),
                    "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                    "raw_model_json": result,
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                out.flush()
    print(f"Wrote {stream_path}")


if __name__ == "__main__":
    main()
