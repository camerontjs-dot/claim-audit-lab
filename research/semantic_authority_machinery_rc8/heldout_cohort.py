from __future__ import annotations

from copy import deepcopy
from typing import Any


def _w(value: Any, status: str = "established", span: tuple[int, int] = (100, 140)) -> dict[str, Any]:
    return {"status": status, "value": value, "span": list(span)}


FAMILIES: dict[str, dict[str, Any]] = {
    "population_membership": {
        "entity": "mira",
        "population": "release_officers",
        "membership_status": "member",
        "predicate": "sign_certificate",
        "quantifier": "all",
        "subclass_direction": "release_officers<=authorized_staff",
    },
    "comparison": {
        "lhs_entity": "batch_a",
        "rhs_entity": "batch_b",
        "property": "hold_time",
        "numeric_value": 8,
        "unit": "hour",
        "comparison_direction": "less_than",
        "temporal_attachment": "before_packaging",
    },
    "event_ordering": {
        "event_a": "inspection",
        "event_b": "release",
        "ordering_direction": "before",
        "polarity": "positive",
        "temporal_attachment": "same_batch",
    },
    "permission_composition": {
        "entity": "noah",
        "population": "licensed_inspectors",
        "predicate": "release_batch",
        "permission_status": "permitted",
        "exception_attachment": "except_quarantine",
        "temporal_attachment": "while_license_current",
        "necessity_direction": "necessary",
    },
}


def make_base(family: str) -> dict[str, Any]:
    values = FAMILIES[family]
    return {
        "case_id": f"H-{family}-BASE",
        "family": family,
        "mutation_axis": "none",
        "expected_authority": "WARRANTED",
        "expected_reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
        "raw_source_id": f"source:heldout:{family}",
        "evidence_admitted": True,
        "proposal": {
            "family": family,
            "source_span": [100, 140],
            "fields": deepcopy(values),
            "extra_modifiers": [],
        },
        "assertion": {"state": "asserted", "scope_path": ["narrator", "main_clause"]},
        "operator": {
            "operator_id": f"operator:{family}:heldout-v1",
            "domain": family,
            "applicability": "applicable",
            "governed_span": [90, 150],
            "jurisdiction_fields": sorted(values),
        },
        "field_warrants": {name: _w(value) for name, value in values.items()},
        "required_fields": sorted(values),
        "composition": {"required": False, "state": "not_applicable", "basis": []},
        "aperture": {"required": False, "state": "not_applicable"},
        "execution_state": "completed",
        "measurement": {"instrument": f"measurement:{family}:heldout-v1", "value": "frozen"},
        "instrument_ids": [f"measurement:{family}:heldout-v1"],
        "reader_agreement_count": 1,
    }


def mutated(base: dict[str, Any], suffix: str, axis: str, status: str, reason: str) -> dict[str, Any]:
    case = deepcopy(base)
    case["case_id"] = f"{base['case_id']}-{suffix}"
    case["mutation_axis"] = axis
    case["expected_authority"] = status
    case["expected_reason"] = reason
    return case


def build_heldout_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    for family, values in FAMILIES.items():
        b = make_base(family)
        cases.append(b)
        first_field = sorted(values)[0]
        second_field = sorted(values)[1]

        c = mutated(b, "FIELD", f"field_mismatch:{first_field}", "REJECTED", f"FIELD_VALUE_MISMATCH:{first_field}")
        c["proposal"]["fields"][first_field] = f"mutated:{values[first_field]}"
        cases.append(c)

        c = mutated(b, "EXTRACT", f"extraction_unresolved:{second_field}", "UNRESOLVED", f"FIELD_EXTRACTION_UNRESOLVED:{second_field}")
        c["field_warrants"][second_field] = _w(None, "extraction_unresolved")
        cases.append(c)

        c = mutated(b, "ASSERT", "embedded_nonasserted", "REJECTED", "SOURCE_ASSERTION_NOT_ESTABLISHED")
        c["assertion"] = {"state": "not_asserted", "scope_path": ["parenthetical", "evidential", "embedded_clause"]}
        cases.append(c)

        c = mutated(b, "APPUNK", "applicability_unknown", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
        c["operator"]["applicability"] = "unknown"
        cases.append(c)

        c = mutated(b, "SPAN", "source_span", "REJECTED", "SOURCE_SPAN_OUTSIDE_OPERATOR_GOVERNANCE")
        c["proposal"]["source_span"] = [151, 170]
        cases.append(c)

        c = mutated(b, "EXTRA", "unsupported_extra_modifier", "REJECTED", "UNSUPPORTED_EXTRA_MODIFIER")
        c["proposal"]["extra_modifiers"] = ["unsupported:night_shift_only"]
        cases.append(c)

        c = mutated(b, "BANK8", "irrelevant_bank_growth", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
        c["instrument_ids"].extend([f"measurement:irrelevant:{family}:{i}" for i in range(7)])
        c["reader_agreement_count"] = 8
        cases.append(c)

        c = mutated(b, "APPUNK-BANK8", "agreement_on_unresolved", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
        c["operator"]["applicability"] = "unknown"
        c["instrument_ids"].extend([f"measurement:agree:{family}:{i}" for i in range(7)])
        c["reader_agreement_count"] = 8
        cases.append(c)

        c = mutated(b, "SEMUNK", f"semantic_unknown:{second_field}", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
        c["field_warrants"][second_field] = _w("unknown", "semantic_unknown")
        c["proposal"]["fields"][second_field] = "unknown"
        cases.append(c)

        c = mutated(b, "SEMUNK-LAUNDER", f"semantic_unknown_launder:{second_field}", "REJECTED", f"FIELD_VALUE_MISMATCH:{second_field}")
        c["field_warrants"][second_field] = _w("unknown", "semantic_unknown")
        cases.append(c)

        c = mutated(b, "INSUFF", f"insufficient_authority:{first_field}", "UNRESOLVED", f"FIELD_INSUFFICIENT_AUTHORITY:{first_field}")
        c["field_warrants"][first_field] = _w(None, "insufficient_authority")
        cases.append(c)

        c = mutated(b, "INAPP", "operator_inapplicable", "REJECTED", "OPERATOR_INAPPLICABLE")
        c["operator"]["applicability"] = "inapplicable"
        cases.append(c)

        c = mutated(b, "OOD", "domain_mismatch", "REJECTED", "OPERATOR_DOMAIN_MISMATCH")
        c["operator"]["domain"] = "other_semantic_family"
        cases.append(c)

        c = mutated(b, "ABSENT", f"required_absent:{second_field}", "REJECTED", f"FIELD_REQUIRED_ABSENT:{second_field}")
        c["field_warrants"][second_field] = _w(None, "absent_not_applicable")
        cases.append(c)

    p = make_base("permission_composition")
    c = mutated(p, "COMP-GOOD", "composition_warranted", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["composition"] = {"required": True, "state": "warranted", "basis": ["atom:permission", "atom:exception", "atom:temporal"]}
    cases.append(c)

    c = mutated(p, "COMP-UNK", "composition_unresolved", "UNRESOLVED", "COMPOSITION_UNRESOLVED")
    c["composition"] = {"required": True, "state": "unresolved", "basis": ["atom:permission", "atom:exception", "atom:temporal"]}
    cases.append(c)

    c = mutated(p, "COMP-REJ", "composition_rejected", "REJECTED", "COMPOSITION_REJECTED")
    c["composition"] = {"required": True, "state": "rejected", "basis": ["atom:permission", "atom:exception", "atom:temporal"]}
    cases.append(c)

    a = make_base("comparison")
    c = mutated(a, "APER-GOOD", "aperture_sufficient", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["aperture"] = {"required": True, "state": "sufficient"}
    cases.append(c)

    c = mutated(a, "APER-UNK", "aperture_unknown", "UNRESOLVED", "APERTURE_UNRESOLVED")
    c["aperture"] = {"required": True, "state": "unknown"}
    cases.append(c)

    e = make_base("event_ordering")
    c = mutated(e, "EXEC", "execution_failure", "NO_ASSESSMENT", "EXECUTION_FAILED")
    c["execution_state"] = "failed"
    cases.append(c)

    e = make_base("population_membership")
    c = mutated(e, "EVIDENCE", "evidence_not_admitted", "REJECTED", "EVIDENCE_NOT_ADMITTED")
    c["evidence_admitted"] = False
    cases.append(c)

    e = make_base("event_ordering")
    c = mutated(e, "ASSERT-UNK", "source_assertion_unresolved", "UNRESOLVED", "SOURCE_ASSERTION_UNRESOLVED")
    c["assertion"] = {"state": "unknown", "scope_path": ["nested_wrapper", "unresolved"]}
    cases.append(c)

    return cases
