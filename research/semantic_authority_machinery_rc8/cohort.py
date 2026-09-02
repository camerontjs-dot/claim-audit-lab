from __future__ import annotations

from copy import deepcopy
from typing import Any


def _field(status: str, value: Any, start: int = 10, end: int = 20) -> dict[str, Any]:
    return {"status": status, "value": value, "span": [start, end]}


def base_case(family: str = "population") -> dict[str, Any]:
    fields = {
        "entity": _field("established", "alice"),
        "population": _field("established", "reviewers"),
        "predicate": _field("established", "approve"),
        "polarity": _field("established", "positive"),
        "role_direction": _field("established", "alice->approve"),
        "subclass_direction": _field("established", "reviewers<=staff"),
        "quantifier": _field("established", "all"),
        "permission_status": _field("established", "permitted"),
        "exception_attachment": _field("established", "except_contractors"),
        "temporal_attachment": _field("established", "before_release"),
        "numeric_value": _field("established", 5),
        "unit": _field("established", "business_day"),
        "comparison_direction": _field("established", "less_equal"),
        "necessity_direction": _field("established", "necessary"),
    }
    proposal_fields = {k: v["value"] for k, v in fields.items()}
    return {
        "case_id": "BASE",
        "mutation_axis": "none",
        "expected_authority": "WARRANTED",
        "expected_reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
        "raw_source_id": "source:fixture-001",
        "evidence_admitted": True,
        "proposal": {
            "family": family,
            "source_span": [10, 20],
            "fields": proposal_fields,
            "extra_modifiers": [],
        },
        "assertion": {"state": "asserted", "scope_path": ["narrator"]},
        "operator": {
            "operator_id": f"operator:{family}:v1",
            "domain": family,
            "applicability": "applicable",
            "governed_span": [10, 20],
            "jurisdiction_fields": sorted(fields),
        },
        "field_warrants": fields,
        "required_fields": sorted(fields),
        "composition": {"required": False, "state": "not_applicable", "basis": []},
        "aperture": {"required": False, "state": "not_applicable"},
        "execution_state": "completed",
        "measurement": {
            "instrument": f"measurement:{family}:frozen-v1",
            "value": "frozen-proposal",
        },
        "instrument_ids": [f"measurement:{family}:frozen-v1"],
        "reader_agreement_count": 1,
    }


def mutate(case: dict[str, Any], case_id: str, axis: str, expected: str, reason: str) -> dict[str, Any]:
    out = deepcopy(case)
    out["case_id"] = case_id
    out["mutation_axis"] = axis
    out["expected_authority"] = expected
    out["expected_reason"] = reason
    return out


def build_cases() -> list[dict[str, Any]]:
    b = base_case()
    cases = [b]

    c = mutate(b, "M-SPAN", "source_span", "REJECTED", "SOURCE_SPAN_OUTSIDE_OPERATOR_GOVERNANCE")
    c["proposal"]["source_span"] = [21, 30]
    cases.append(c)

    c = mutate(b, "M-ASSERT-NO", "narrator_assertion_scope", "REJECTED", "SOURCE_ASSERTION_NOT_ESTABLISHED")
    c["assertion"] = {"state": "not_asserted", "scope_path": ["parenthetical", "evidential"]}
    cases.append(c)

    c = mutate(b, "M-ASSERT-UNK", "narrator_assertion_scope_unknown", "UNRESOLVED", "SOURCE_ASSERTION_UNRESOLVED")
    c["assertion"] = {"state": "unknown", "scope_path": ["unresolved_wrapper"]}
    cases.append(c)

    for idx, field in enumerate([
        "entity", "population", "predicate", "polarity", "role_direction",
        "subclass_direction", "quantifier", "permission_status", "exception_attachment",
        "temporal_attachment", "numeric_value", "unit", "comparison_direction",
        "necessity_direction",
    ], start=1):
        c = mutate(b, f"M-FIELD-{idx:02d}", field, "REJECTED", f"FIELD_VALUE_MISMATCH:{field}")
        old = c["proposal"]["fields"][field]
        c["proposal"]["fields"][field] = f"mutated:{old}"
        cases.append(c)

    c = mutate(b, "M-EXTRA", "unsupported_extra_modifier", "REJECTED", "UNSUPPORTED_EXTRA_MODIFIER")
    c["proposal"]["extra_modifiers"] = ["only_during_night_shift"]
    cases.append(c)

    c = mutate(b, "M-OOD", "out_of_jurisdiction_semantic_family", "REJECTED", "OPERATOR_DOMAIN_MISMATCH")
    c["proposal"]["family"] = "causal_counterfactual"
    cases.append(c)

    c = mutate(b, "M-APP-UNK", "operator_applicability_unknown", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    cases.append(c)

    c = mutate(b, "M-APP-NO", "operator_inapplicable", "REJECTED", "OPERATOR_INAPPLICABLE")
    c["operator"]["applicability"] = "inapplicable"
    cases.append(c)

    c = mutate(b, "M-EXTRACT", "extraction_unresolved", "UNRESOLVED", "FIELD_EXTRACTION_UNRESOLVED:entity")
    c["field_warrants"]["entity"] = _field("extraction_unresolved", None)
    cases.append(c)

    c = mutate(b, "M-INSUFF", "insufficient_interpretation_authority", "UNRESOLVED", "FIELD_INSUFFICIENT_AUTHORITY:entity")
    c["field_warrants"]["entity"] = _field("insufficient_authority", None)
    cases.append(c)

    c = mutate(b, "M-SEMUNK-GOOD", "source_established_semantic_unknown", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["field_warrants"]["permission_status"] = _field("semantic_unknown", "unknown")
    c["proposal"]["fields"]["permission_status"] = "unknown"
    cases.append(c)

    c = mutate(b, "M-SEMUNK-LAUNDER", "semantic_unknown_laundering", "REJECTED", "FIELD_VALUE_MISMATCH:permission_status")
    c["field_warrants"]["permission_status"] = _field("semantic_unknown", "unknown")
    c["proposal"]["fields"]["permission_status"] = "permitted"
    cases.append(c)

    c = mutate(b, "M-ABSENT", "required_field_absent", "REJECTED", "FIELD_REQUIRED_ABSENT:entity")
    c["field_warrants"]["entity"] = _field("absent_not_applicable", None)
    cases.append(c)

    c = mutate(b, "M-COMP-UNK", "composition_unresolved", "UNRESOLVED", "COMPOSITION_UNRESOLVED")
    c["composition"] = {"required": True, "state": "unresolved", "basis": ["atom:a", "atom:b"]}
    cases.append(c)

    c = mutate(b, "M-COMP-REJ", "composition_rejected", "REJECTED", "COMPOSITION_REJECTED")
    c["composition"] = {"required": True, "state": "rejected", "basis": ["atom:a", "atom:b"]}
    cases.append(c)

    c = mutate(b, "M-COMP-GOOD", "composition_warranted", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["composition"] = {"required": True, "state": "warranted", "basis": ["atom:a", "atom:b"]}
    cases.append(c)

    c = mutate(b, "M-APER", "aperture_dependent", "UNRESOLVED", "APERTURE_UNRESOLVED")
    c["aperture"] = {"required": True, "state": "unknown"}
    cases.append(c)

    c = mutate(b, "M-EXEC", "execution_failure", "NO_ASSESSMENT", "EXECUTION_FAILED")
    c["execution_state"] = "failed"
    cases.append(c)

    c = mutate(b, "M-EVIDENCE", "evidence_not_admitted", "REJECTED", "EVIDENCE_NOT_ADMITTED")
    c["evidence_admitted"] = False
    cases.append(c)

    c = mutate(b, "BANK-2", "irrelevant_instrument_addition", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["instrument_ids"].append("measurement:irrelevant:v1")
    c["reader_agreement_count"] = 2
    cases.append(c)

    c = mutate(b, "BANK-8", "instrument_bank_growth", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["instrument_ids"].extend([f"measurement:irrelevant:{i}" for i in range(1, 8)])
    c["reader_agreement_count"] = 8
    cases.append(c)

    c = mutate(b, "BANK-UNK-1", "agreement_on_unresolved", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    cases.append(c)
    c2 = deepcopy(c)
    c2["case_id"] = "BANK-UNK-8"
    c2["instrument_ids"].extend([f"measurement:agree:{i}" for i in range(1, 8)])
    c2["reader_agreement_count"] = 8
    cases.append(c2)

    return cases
