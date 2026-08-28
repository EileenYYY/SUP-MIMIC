from mimic_pipeline_kit.filters import screen_profile


def test_screen_profile_passes_basic_case():
    profile = {
        "patient": {"anchor_age": 52},
        "admissions_total": 3,
        "icu_stays": [{"stay_id": 1}],
        "admissions": [{"admission_type": "EW EMER."}],
    }
    rules = {
        "age_min": 18,
        "require_icu": True,
        "min_admissions": 1,
        "excluded_admission_types": ["NEWBORN"],
        "required_outputs": ["icu_stays"],
    }
    result = screen_profile(profile, rules)
    assert result.passed is True
    assert result.reasons == []


def test_screen_profile_rejects_newborn():
    profile = {
        "patient": {"anchor_age": 2},
        "admissions_total": 1,
        "icu_stays": [],
        "admissions": [{"admission_type": "NEWBORN"}],
    }
    rules = {
        "age_min": 18,
        "require_icu": True,
        "excluded_admission_types": ["NEWBORN"],
    }
    result = screen_profile(profile, rules)
    assert result.passed is False
    assert any("anchor_age" in reason for reason in result.reasons)

