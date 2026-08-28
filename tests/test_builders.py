from pathlib import Path

from mimic_pipeline_kit.builders import build_case_profile


def test_build_case_profile_reads_jsonl(tmp_path: Path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "patients.jsonl").write_text('{"subject_id": 1, "gender": "M"}\n', encoding="utf-8")
    (raw / "admissions.jsonl").write_text(
        '{"hadm_id": 2, "admittime": "2020-01-01 00:00:00"}\n',
        encoding="utf-8",
    )
    (raw / "icustays.jsonl").write_text(
        '{"stay_id": 3, "intime": "2020-01-02 00:00:00"}\n',
        encoding="utf-8",
    )

    profile = build_case_profile(raw, {"subject_id": 1, "hadm_id": 2, "stay_id": 3})
    assert profile["subject_id"] == 1
    assert profile["hadm_id"] == 2
    assert profile["stay_id"] == 3
    assert profile["patient"]["gender"] == "M"

