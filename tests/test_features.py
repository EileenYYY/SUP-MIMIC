from mimic_pipeline_kit.ml.features import build_feature_rows, flatten_profile


def test_flatten_profile_counts_lists():
    profile = {
        "patient": {"gender": "M", "anchor_age": 52},
        "diagnoses": [{"icd_code": "001"}, {"icd_code": "002"}],
        "notes": ["alpha", "beta", "alpha"],
    }
    flat = flatten_profile(profile)
    assert flat["patient_gender"] == "M"
    assert flat["patient_anchor_age"] == 52
    assert flat["diagnoses_count"] == 2
    assert flat["diagnoses_icd_code_unique"] == 2
    assert flat["notes_count"] == 3
    assert flat["notes_unique"] == 2


def test_build_feature_rows_adds_label():
    rows = build_feature_rows(
        [{"patient": {"gender": "M"}, "label": 1}],
        label_key="label",
    )
    assert rows[0]["__label__"] == 1
    assert "label" not in rows[0]

