from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class ScreenResult:
    passed: bool
    reasons: List[str] = field(default_factory=list)


def _contains_any(value: str, needles: List[str]) -> bool:
    upper = value.upper()
    return any(needle.upper() in upper for needle in needles)


def screen_profile(profile: Dict[str, Any], rules: Dict[str, Any]) -> ScreenResult:
    reasons: List[str] = []

    age_min = rules.get("age_min")
    if age_min is not None:
        age = profile.get("patient", {}).get("anchor_age")
        if age is None or age < age_min:
            reasons.append(f"anchor_age<{age_min}")

    if rules.get("require_icu"):
        if not profile.get("icu_stays"):
            reasons.append("missing ICU stay")

    min_admissions = rules.get("min_admissions")
    if min_admissions is not None and profile.get("admissions_total", 0) < min_admissions:
        reasons.append(f"admissions_total<{min_admissions}")

    excluded = list(rules.get("excluded_admission_types", []))
    if excluded:
        admissions = profile.get("admissions", [])
        for row in admissions:
            admission_type = str(row.get("admission_type", ""))
            if _contains_any(admission_type, excluded):
                reasons.append(f"excluded admission_type={admission_type}")
                break

    required_outputs = list(rules.get("required_outputs", []))
    for name in required_outputs:
        value = profile.get(name)
        if value in (None, [], {}):
            reasons.append(f"missing output={name}")

    return ScreenResult(passed=not reasons, reasons=reasons)

