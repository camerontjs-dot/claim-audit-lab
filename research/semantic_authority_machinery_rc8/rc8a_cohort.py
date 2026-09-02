from __future__ import annotations

from copy import deepcopy
from typing import Any


SUBJECT_A = "authority-subject:source-a:proposal-comparison-001"
SUBJECT_B = "authority-subject:source-b:proposal-comparison-001"

VALUES: dict[str, Any] = {
    "lhs_entity": "batch_a",
    "rhs_entity": "batch_b",
    "property": "hold_time",
    "numeric_value": 8,
    "unit": "hour",
    "comparison_direction": "less_than",
    "temporal_attachment": "before_packaging",
}


def _w(value: Any, subject: str = SUBJECT_A, span: tuple[int, int] = (100, 140)) -> dict[str, Any]:
    return {
        "status": "established",
        "value": value,
        "span": list(span),
        "authority_subject_id": subject,
    }


def make_bound_case() -> dict[str, Any]:
    return {
        "case_id": "RC8A-BOUND-POSITIVE",
        "mutation_axis": "fully_bound_positive_control",
        "expected_authority": "WARRANTED",
        "expected_reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
        "raw_source_id": "source:rc8a:a",
        "authority_subject_id": SUBJECT_A,
        "evidence_admitted": True,
        "proposal": {
            "family": "comparison",
            "source_span": [100, 140],
            "fields": deepcopy(VALUES),
            "extra_modifiers": [],
            "authority_subject_id": SUBJECT_A,
        },
        "assertion": {
            "state": "asserted",
            "scope_path": ["narrator", "main_clause"],
            "authority_subject_id": SUBJECT_A,
        },
        "operator": {
            "operator_id": "operator:comparison:rc8a-v1",
            "domain": "comparison",
            "applicability": "applicable",
            "governed_span": [90, 150],
            "jurisdiction_fields": sorted(VALUES),
            "authority_subject_id": SUBJECT_A,
        },
        "field_warrants": {name: _w(value) for name, value in VALUES.items()},
        "required_fields": sorted(VALUES),
        "composition": {
            "required": True,
            "state": "warranted",
            "basis": ["atom:comparison", "atom:temporal"],
            "authority_subject_id": SUBJECT_A,
        },
        "aperture": {
            "required": True,
            "state": "sufficient",
            "authority_subject_id": SUBJECT_A,
        },
        "execution_state": "completed",
        "measurement": {"instrument": "measurement:comparison:rc8a-v1", "value": "frozen"},
        "instrument_ids": ["measurement:comparison:rc8a-v1"],
        "reader_agreement_count": 1,
    }


def _mutated(case_id: str, axis: str, reason: str) -> dict[str, Any]:
    case = deepcopy(make_bound_case())
    case["case_id"] = case_id
    case["mutation_axis"] = axis
    case["expected_authority"] = "REJECTED"
    case["expected_reason"] = reason
    return case


def build_rc8a_cases() -> list[dict[str, Any]]:
    cases = [make_bound_case()]

    c = _mutated(
        "RC8A-ASSERTION-SUBJECT-B",
        "assertion_authority_subject_substitution",
        "AUTHORITY_SUBJECT_MISMATCH:assertion",
    )
    c["assertion"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = _mutated(
        "RC8A-OPERATOR-SUBJECT-B",
        "operator_authority_subject_substitution",
        "AUTHORITY_SUBJECT_MISMATCH:operator",
    )
    c["operator"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    field = "comparison_direction"
    c = _mutated(
        "RC8A-FIELD-SUBJECT-B",
        "field_authority_subject_substitution",
        f"AUTHORITY_SUBJECT_MISMATCH:field:{field}",
    )
    c["field_warrants"][field]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = _mutated(
        "RC8A-FIELD-SPAN-DISJOINT",
        "field_support_span_outside_operator_governance",
        f"FIELD_SUPPORT_OUTSIDE_OPERATOR_GOVERNANCE:{field}",
    )
    c["field_warrants"][field]["span"] = [160, 170]
    cases.append(c)

    c = _mutated(
        "RC8A-COMPOSITION-SUBJECT-B",
        "composition_authority_subject_substitution",
        "AUTHORITY_SUBJECT_MISMATCH:composition",
    )
    c["composition"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = _mutated(
        "RC8A-APERTURE-SUBJECT-B",
        "aperture_authority_subject_substitution",
        "AUTHORITY_SUBJECT_MISMATCH:aperture",
    )
    c["aperture"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    return cases
