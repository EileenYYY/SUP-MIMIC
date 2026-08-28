from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _latest_by(rows: List[Dict[str, Any]], key: str, time_field: str) -> Dict[str, Any] | None:
    candidates = [row for row in rows if row.get(key) is not None]
    if not candidates:
        return None
    return sorted(candidates, key=lambda row: str(row.get(time_field, "")))[-1]


def build_case_profile(raw_dir: Path, context: Dict[str, Any]) -> Dict[str, Any]:
    patients = _read_jsonl(raw_dir / "patients.jsonl")
    admissions = _read_jsonl(raw_dir / "admissions.jsonl")
    icustays = _read_jsonl(raw_dir / "icustays.jsonl")
    first_day_labs = _read_jsonl(raw_dir / "first_day_labs.jsonl")
    first_day_vitals = _read_jsonl(raw_dir / "first_day_vitals.jsonl")
    icu_inputevents = _read_jsonl(raw_dir / "icu_inputevents.jsonl")
    icu_outputevents = _read_jsonl(raw_dir / "icu_outputevents.jsonl")
    icu_procedureevents = _read_jsonl(raw_dir / "icu_procedureevents.jsonl")
    icu_chartevents = _read_jsonl(raw_dir / "icu_chartevents.jsonl")
    icu_scores = _read_jsonl(raw_dir / "icu_scores.jsonl")
    edstays = _read_jsonl(raw_dir / "edstays.jsonl")
    triage = _read_jsonl(raw_dir / "triage.jsonl")
    ed_vitals = _read_jsonl(raw_dir / "ed_vitals.jsonl")
    ed_medrecon = _read_jsonl(raw_dir / "ed_medrecon.jsonl")
    cxr = _read_jsonl(raw_dir / "cxr.jsonl")
    ecg = _read_jsonl(raw_dir / "ecg.jsonl")
    diagnoses = _read_jsonl(raw_dir / "diagnoses.jsonl")
    procedures = _read_jsonl(raw_dir / "procedures.jsonl")
    prescriptions = _read_jsonl(raw_dir / "prescriptions.jsonl")
    notes = _read_jsonl(raw_dir / "notes.jsonl")

    patient = patients[0] if patients else {}
    latest_admission = _latest_by(admissions, "hadm_id", "admittime") or {}
    latest_stay = _latest_by(icustays, "stay_id", "intime") or {}
    latest_prescription = _latest_by(prescriptions, "drug", "starttime") or {}

    return {
        "subject_id": context.get("subject_id", patient.get("subject_id")),
        "hadm_id": context.get("hadm_id", latest_admission.get("hadm_id")),
        "stay_id": context.get("stay_id", latest_stay.get("stay_id")),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "patient": patient,
        "admissions_total": len(admissions),
        "admissions": admissions,
        "icu_stays": icustays,
        "icustays": icustays,
        "first_day_labs": first_day_labs[0] if first_day_labs else {},
        "first_day_vitals": first_day_vitals[0] if first_day_vitals else {},
        "icu_inputevents": icu_inputevents,
        "icu_outputevents": icu_outputevents,
        "icu_procedureevents": icu_procedureevents,
        "icu_chartevents": icu_chartevents,
        "icu_scores": icu_scores,
        "edstays": edstays,
        "triage": triage,
        "ed_vitals": ed_vitals,
        "ed_medrecon": ed_medrecon,
        "cxr": cxr,
        "ecg": ecg,
        "diagnoses": diagnoses,
        "procedures": procedures,
        "prescriptions": prescriptions,
        "notes": notes,
        "latest_admission": latest_admission,
        "latest_stay": latest_stay,
        "latest_prescription": latest_prescription,
    }
