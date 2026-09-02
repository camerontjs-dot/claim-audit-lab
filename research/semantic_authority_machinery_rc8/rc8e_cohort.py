from __future__ import annotations

from copy import deepcopy
from typing import Any

from .rc8d_heldout_cohort import anchored_base


SOURCE = "source:rc8e:shared"
ATOM_A = "atom:rc8e:shared:A"
ATOM_B = "atom:rc8e:shared:B"
SUBJECT_A = "authority-subject:rc8e:shared:A"
SUBJECT_B = "authority-subject:rc8e:shared:B"


def _bind_internal_subject(case: dict[str, Any], subject: str) -> None:
    case["authority_subject_id"] = subject
    case["proposal"]["authority_subject_id"] = subject
    case["assertion"]["authority_subject_id"] = subject
    case["operator"]["authority_subject_id"] = subject
    for receipt in case["field_warrants"].values():
        receipt["authority_subject_id"] = subject
    if case["composition"]["required"]:
        case["composition"]["authority_subject_id"] = subject
    if case["aperture"]["required"]:
        case["aperture"]["authority_subject_id"] = subject


def atom_base(atom_id: str = ATOM_A, subject: str = SUBJECT_A) -> dict[str, Any]:
    case = deepcopy(anchored_base())
    case["case_id"] = "E-BASE"
    case["mutation_axis"] = "same_source_atom_identity_positive"
    case["expected_authority"] = "WARRANTED"
    case["expected_reason"] = "ALL_REQUIRED_WARRANT_ESTABLISHED"
    case["raw_source_id"] = SOURCE
    case["authority_subject_source_id"] = SOURCE
    case["target_atom_id"] = atom_id
    case["authority_subject_atom_id"] = atom_id
    _bind_internal_subject(case, subject)
    case["reader_agreement_count"] = 2
    case["instrument_ids"] = ["measurement:rc8e:shared:1"]
    return case


def mutate(case_id: str, axis: str, expected: str, reason: str) -> dict[str, Any]:
    case = deepcopy(atom_base())
    case["case_id"] = case_id
    case["mutation_axis"] = axis
    case["expected_authority"] = expected
    case["expected_reason"] = reason
    return case


def build_rc8e_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = [atom_base()]

    # Whole receipt bundle belongs to B, but the consumer target remains A.
    # Semantic values and admitted source are intentionally unchanged.
    c = mutate("E-TRANSPLANT", "same_source_whole_atom_bundle_transplanted", "REJECTED", "AUTHORITY_ATOM_IDENTITY_MISMATCH")
    c["target_atom_id"] = ATOM_A
    c["authority_subject_atom_id"] = ATOM_B
    _bind_internal_subject(c, SUBJECT_B)
    cases.append(c)

    c = mutate("E-TARGET-MISSING", "target_atom_identity_missing", "UNRESOLVED", "AUTHORITY_ATOM_IDENTITY_BINDING_UNRESOLVED")
    c.pop("target_atom_id")
    cases.append(c)

    c = mutate("E-SUBJECT-ATOM-MISSING", "authority_subject_atom_identity_missing", "UNRESOLVED", "AUTHORITY_ATOM_IDENTITY_BINDING_UNRESOLVED")
    c.pop("authority_subject_atom_id")
    cases.append(c)

    c = mutate("E-ATOM-PRECEDENCE", "atom_mismatch_precedes_subreceipt_mismatch", "REJECTED", "AUTHORITY_ATOM_IDENTITY_MISMATCH")
    c["authority_subject_atom_id"] = ATOM_B
    c["proposal"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = mutate("E-SOURCE-PRECEDENCE", "source_mismatch_precedes_atom_mismatch", "REJECTED", "AUTHORITY_EVIDENCE_SOURCE_MISMATCH")
    c["raw_source_id"] = "source:rc8e:other"
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("E-EXEC", "execution_precedes_missing_atom_binding", "NO_ASSESSMENT", "EXECUTION_FAILED")
    c["execution_state"] = "failed"
    c.pop("target_atom_id")
    c.pop("authority_subject_atom_id")
    cases.append(c)

    c = mutate("E-EVIDENCE", "evidence_rejection_precedes_missing_atom_binding", "REJECTED", "EVIDENCE_NOT_ADMITTED")
    c["evidence_admitted"] = False
    c.pop("target_atom_id")
    c.pop("authority_subject_atom_id")
    cases.append(c)

    c = mutate("E-BANK-WARRANTED", "atom_binding_bank_growth_warranted", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["reader_agreement_count"] = 16
    c["instrument_ids"].extend([f"measurement:rc8e:irrelevant:{i}" for i in range(2, 17)])
    cases.append(c)

    c = mutate("E-BANK-UNRESOLVED", "atom_binding_bank_growth_unresolved", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    c["reader_agreement_count"] = 16
    c["instrument_ids"].extend([f"measurement:rc8e:agree:{i}" for i in range(2, 17)])
    cases.append(c)

    return cases
