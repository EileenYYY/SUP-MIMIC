#!/usr/bin/env python3
"""Build SUP-MIMIC BA/DDT/DCT case files from local authorized feature tables.

Input contract:
  input_dir/
    all.csv                # full candidate table
    <disease>.csv          # one column, stay_id, listing positive stays

The script writes one folder per disease with:
  A_class_basic_assessment.csv
  B_class_ddt_pairs.csv
  C_class_dct_pairs.csv

Do not commit outputs produced from real MIMIC records.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import LabelEncoder, StandardScaler


ID_COLUMNS = ["subject_id", "hadm_id", "stay_id", "dicom_id", "study_id"]
DEFAULT_DROP_COLUMNS = [
    "rdwsd_first",
    "rdwsd_last",
    "rdwsd_max",
    "rdwsd_min",
    "rdwsd_avg",
    "diagnosis_long_title1",
    "gender",
]


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SUP-MIMIC BA/DDT/DCT samples.")
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--all-csv", default="all.csv")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--top-k-features", type=int, default=25)
    parser.add_argument("--ba-n", type=int, default=10)
    parser.add_argument("--pair-n", type=int, default=5)
    parser.add_argument("--completeness-threshold", type=float, default=0.70)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--keep-source-ids", action="store_true")
    return parser.parse_args()


def preprocess_global_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "gender" in df.columns:
        df["gender_encoded"] = LabelEncoder().fit_transform(df["gender"].astype(str))

    for col in df.select_dtypes(include=["object"]).columns:
        if col in ID_COLUMNS or col == "stay_id":
            continue
        numeric = pd.to_numeric(df[col], errors="coerce")
        if numeric.notna().sum() > 0:
            df[col] = numeric
        else:
            df[col] = LabelEncoder().fit_transform(df[col].astype(str))
    return df


def stable_case_id(disease: str, row: pd.Series) -> str:
    raw = "|".join(str(row.get(c, "")) for c in ID_COLUMNS)
    digest = hashlib.sha256(f"{disease}|{raw}".encode("utf-8")).hexdigest()[:16]
    return f"case_{digest}"


def export_frame(df: pd.DataFrame, path: Path, disease: str, keep_source_ids: bool) -> None:
    out = df.copy()
    out.insert(0, "case_id", [stable_case_id(disease, row) for _, row in out.iterrows()])
    if not keep_source_ids:
        out = out.drop(columns=[c for c in ID_COLUMNS if c in out.columns], errors="ignore")
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False, encoding="utf-8")


def select_key_features(
    data: pd.DataFrame, top_k: int, random_state: int, drop_cols: list[str]
) -> list[str]:
    train_pool = data.drop(columns=ID_COLUMNS + ["diseased"] + drop_cols, errors="ignore")
    train_pool = train_pool.select_dtypes(include=[np.number]).dropna(axis=1, how="all")
    train_pool = train_pool.fillna(train_pool.median(numeric_only=True))
    if train_pool.empty:
        raise ValueError("No numeric features available after preprocessing.")

    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        n_jobs=-1,
        random_state=random_state,
        class_weight="balanced_subsample",
    )
    rf.fit(train_pool, data["diseased"])
    ranking = (
        pd.DataFrame({"feature": train_pool.columns, "importance": rf.feature_importances_})
        .sort_values("importance", ascending=False)
        .head(top_k)
    )
    return ranking["feature"].tolist()


def pair_rows(
    data: pd.DataFrame,
    key_features: list[str],
    pair_n: int,
    mode: str,
) -> pd.DataFrame:
    matrix = data[key_features].copy()
    matrix = matrix.fillna(matrix.median(numeric_only=True))
    scaled = StandardScaler().fit_transform(matrix)
    distances = euclidean_distances(scaled)
    labels = data["diseased"].to_numpy()
    rows: list[dict] = []
    used: set[tuple[int, int]] = set()

    if mode == "ddt":
        score = 1 / (1 + distances)
        np.fill_diagonal(score, -1)
        mask = labels[:, None] != labels[None, :]
        candidates = np.argsort(np.where(mask, score, -1).ravel())[::-1]
        metric_name = "similarity"
    elif mode == "dct":
        positive = np.where(labels == 1)[0]
        if len(positive) < 2:
            return pd.DataFrame()
        sub_dist = distances[positive][:, positive]
        np.fill_diagonal(sub_dist, -1)
        candidates = np.argsort(sub_dist.ravel())[::-1]
        metric_name = "distance"
    else:
        raise ValueError(f"Unknown pair mode: {mode}")

    for flat_idx in candidates:
        if mode == "ddt":
            r, c = divmod(int(flat_idx), len(data))
            metric = float(score[r, c])
            if metric <= 0:
                continue
        else:
            positive = np.where(labels == 1)[0]
            rr, cc = divmod(int(flat_idx), len(positive))
            if rr == cc:
                continue
            r, c = int(positive[rr]), int(positive[cc])
            metric = float(distances[r, c])

        key = tuple(sorted((r, c)))
        if key in used:
            continue
        pair_id = f"{mode.upper()}_{len(used) + 1:03d}"
        for pos in [r, c]:
            row = data.iloc[pos].to_dict()
            row["pair_id"] = pair_id
            row[metric_name] = round(metric, 6)
            row["task"] = mode.upper()
            rows.append(row)
        used.add(key)
        if len(used) >= pair_n:
            break

    return pd.DataFrame(rows)


def process_disease(
    all_df: pd.DataFrame,
    disease_csv: Path,
    output_dir: Path,
    args: argparse.Namespace,
) -> dict:
    disease = disease_csv.stem
    positives = pd.read_csv(disease_csv, usecols=["stay_id"])
    data = all_df.copy()
    data["stay_id"] = data["stay_id"].astype(str)
    positive_stays = set(positives["stay_id"].astype(str).unique())
    data["diseased"] = data["stay_id"].isin(positive_stays).astype(int)
    data = data.sort_values("stay_id").drop_duplicates(subset=["subject_id"], keep="first")
    data = data[data.notna().mean(axis=1) >= args.completeness_threshold]

    if data["diseased"].sum() < 2:
        return {"disease": disease, "status": "skipped", "reason": "fewer than two positives"}

    key_features = select_key_features(
        data, args.top_k_features, args.random_state, DEFAULT_DROP_COLUMNS
    )
    disease_dir = output_dir / disease

    ba = data[data["diseased"] == 1].head(args.ba_n).copy()
    ba["task"] = "BA"
    export_frame(ba, disease_dir / "A_class_basic_assessment.csv", disease, args.keep_source_ids)

    ddt = pair_rows(data, key_features, args.pair_n, "ddt")
    if not ddt.empty:
        export_frame(ddt, disease_dir / "B_class_ddt_pairs.csv", disease, args.keep_source_ids)

    dct = pair_rows(data, key_features, args.pair_n, "dct")
    if not dct.empty:
        export_frame(dct, disease_dir / "C_class_dct_pairs.csv", disease, args.keep_source_ids)

    pd.Series(key_features, name="feature").to_csv(
        disease_dir / "selected_features.csv", index=False, encoding="utf-8"
    )
    return {
        "disease": disease,
        "status": "ok",
        "ba_rows": int(len(ba)),
        "ddt_rows": int(len(ddt)),
        "dct_rows": int(len(dct)),
    }


def main() -> None:
    args = build_args()
    all_path = args.input_dir / args.all_csv
    all_df = preprocess_global_data(pd.read_csv(all_path, low_memory=False))
    disease_files = sorted(p for p in args.input_dir.glob("*.csv") if p.name != args.all_csv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    reports = [
        process_disease(all_df, disease_csv, args.output_dir, args) for disease_csv in disease_files
    ]
    pd.DataFrame(reports).to_csv(args.output_dir / "build_manifest.csv", index=False)
    for report in reports:
        print(report)


if __name__ == "__main__":
    main()
