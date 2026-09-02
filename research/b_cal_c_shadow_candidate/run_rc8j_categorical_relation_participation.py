"""Research-only scalar-free categorical relation participation candidate.

The candidate assumes proposition-relative relation has already been established.
It does not infer that relation from text and it does not modify production CAL.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Literal

from authority_consumption_rc1 import consume_external_authority
from run_authority_consumption_rc1 import (
    _load_rc8j,
    _typed_seam_control,
    _validated_b_coordinates,
)

Relation = Literal["support", "refutation"]


def _contribution(
    contribution_id: str,
    authority_result: dict[str, Any],
    *,
    relation_state: Literal["established", "unresolved"],
    relation: Relation | None,
    diagnostic_score: float | None = None,
    reader_count: int = 1,
    instrument_count: int = 1,
    admitted: bool = True,
    eligible: bool = True,
) -> dict[str, Any]:
    if relation_state == "established" and relation not in {"support", "refutation"}:
        raise ValueError("established proposition relation requires support or refutation")
    if relation_state == "unresolved" and relation is not None:
        raise ValueError("unresolved proposition relation must not invent polarity")
    return {
        "contribution_id": contribution_id,
        "authority": deepcopy(authority_result["authority"]),
        "proposition_relation": {
            "state": relation_state,
            "relation": relation,
            "fixture_only": True,
            "authority_semantics": "not_established_for_real_text",
        },
        "admitted": admitted,
        "eligible": eligible,
        "diagnostic_only": {
            "scalar_score": diagnostic_score,
            "reader_count": reader_count,
            "instrument_count": instrument_count,
        },
    }


def categorical_decide(
    contributions: list[dict[str, Any]],
    *,
    scope_status: str = "in_scope",
    support_aperture: str = "complete",
    refutation_aperture: str = "complete",
) -> dict[str, Any]:
    if scope_status != "in_scope":
        return {"disposition": "abstained", "verdict": None, "reason": "scope_unresolved", "basis": []}

    if support_aperture != "complete" or refutation_aperture != "complete":
        return {"disposition": "abstained", "verdict": None, "reason": "aperture_unresolved", "basis": []}

    relevant = [item for item in contributions if item["admitted"] and item["eligible"]]

    unresolved_authority = [
        item
        for item in relevant
        if item["authority"]["status"] in {"UNRESOLVED", "NO_ASSESSMENT"}
    ]
    if unresolved_authority:
        return {
            "disposition": "abstained",
            "verdict": None,
            "reason": "semantic_authority_unresolved",
            "basis": sorted(item["contribution_id"] for item in unresolved_authority),
        }

    warranted = [item for item in relevant if item["authority"]["status"] == "WARRANTED"]
    unresolved_relation = [
        item for item in warranted if item["proposition_relation"]["state"] != "established"
    ]
    if unresolved_relation:
        return {
            "disposition": "abstained",
            "verdict": None,
            "reason": "proposition_relation_unresolved",
            "basis": sorted(item["contribution_id"] for item in unresolved_relation),
        }

    deciding = [
        item
        for item in warranted
        if item["proposition_relation"]["state"] == "established"
        and item["proposition_relation"]["relation"] in {"support", "refutation"}
    ]
    support = [item for item in deciding if item["proposition_relation"]["relation"] == "support"]
    refutation = [
        item for item in deciding if item["proposition_relation"]["relation"] == "refutation"
    ]

    if support and refutation:
        return {
            "disposition": "abstained",
            "verdict": None,
            "reason": "mixed_warranted_relations",
            "basis": sorted(item["contribution_id"] for item in support + refutation),
        }
    if support:
        return {
            "disposition": "decided",
            "verdict": "supported",
            "reason": "warranted_support_relation",
            "basis": sorted(item["contribution_id"] for item in support),
        }
    if refutation:
        return {
            "disposition": "decided",
            "verdict": "contradicted",
            "reason": "warranted_refutation_relation",
            "basis": sorted(item["contribution_id"] for item in refutation),
        }
    return {
        "disposition": "abstained",
        "verdict": None,
        "reason": "no_warranted_established_relation",
        "basis": [],
    }


def _assert(case_id: str, observed: dict[str, Any], disposition: str, verdict: str | None, reason: str) -> dict[str, Any]:
    expected = {"disposition": disposition, "verdict": verdict, "reason": reason}
    for key, value in expected.items():
        if observed[key] != value:
            raise AssertionError(f"{case_id}: {key}={observed[key]!r}, expected {value!r}")
    return {"case_id": case_id, "observed": observed}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-output", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    args = parser.parse_args()

    run_output = args.run_output.resolve()
    evaluator = _load_rc8j(args.rc8j_root.resolve())
    coords = _validated_b_coordinates(run_output)
    seam = _typed_seam_control(coords)

    positive = consume_external_authority(seam, evaluator, fixture_only=True)
    if positive["authority"]["status"] != "WARRANTED":
        raise AssertionError("positive frozen RC8J seam control no longer warrants")

    unresolved_case = deepcopy(seam)
    unresolved_case["authority_subject_bundle_id"] = None
    unresolved = consume_external_authority(unresolved_case, evaluator, fixture_only=True)
    if unresolved["authority"]["status"] != "UNRESOLVED":
        raise AssertionError("unresolved RC8J control did not remain unresolved")

    rejected_case = deepcopy(seam)
    rejected_case["authority_subject_source_id"] = "source:explicit-mismatch"
    rejected = consume_external_authority(rejected_case, evaluator, fixture_only=True)
    if rejected["authority"]["status"] != "REJECTED":
        raise AssertionError("rejected RC8J control did not remain rejected")

    support = _contribution(
        "cat:support:1", positive, relation_state="established", relation="support"
    )
    refute = _contribution(
        "cat:refutation:1", positive, relation_state="established", relation="refutation"
    )
    relation_unknown = _contribution(
        "cat:relation-unresolved", positive, relation_state="unresolved", relation=None
    )
    authority_unknown = _contribution(
        "cat:authority-unresolved", unresolved, relation_state="established", relation="support"
    )
    rejected_refute = _contribution(
        "cat:rejected-refutation", rejected, relation_state="established", relation="refutation"
    )
    unresolved_refute = _contribution(
        "cat:unresolved-refutation", unresolved, relation_state="established", relation="refutation"
    )

    rows = [
        _assert("C1-WARRANTED-SUPPORT", categorical_decide([support]), "decided", "supported", "warranted_support_relation"),
        _assert("C2-WARRANTED-REFUTATION", categorical_decide([refute]), "decided", "contradicted", "warranted_refutation_relation"),
        _assert("C3-MIXED-WARRANTED", categorical_decide([support, refute]), "abstained", None, "mixed_warranted_relations"),
        _assert("C4-RELATION-UNRESOLVED", categorical_decide([relation_unknown]), "abstained", None, "proposition_relation_unresolved"),
        _assert("C5-AUTHORITY-UNRESOLVED", categorical_decide([authority_unknown]), "abstained", None, "semantic_authority_unresolved"),
        _assert("C6-REJECTED-COMPETITOR", categorical_decide([support, rejected_refute]), "decided", "supported", "warranted_support_relation"),
        _assert("C7-UNRESOLVED-COMPETITOR", categorical_decide([support, unresolved_refute]), "abstained", None, "semantic_authority_unresolved"),
        _assert(
            "C8-APERTURE-UNKNOWN",
            categorical_decide([support], refutation_aperture="unknown"),
            "abstained",
            None,
            "aperture_unresolved",
        ),
    ]

    diagnostic_score_results = []
    for score in (0.01, 0.70, 0.99):
        item = _contribution(
            f"cat:diag-score:{score}",
            positive,
            relation_state="established",
            relation="support",
            diagnostic_score=score,
        )
        observed = categorical_decide([item])
        _assert(f"C9-DIAGNOSTIC-SCORE-{score}", observed, "decided", "supported", "warranted_support_relation")
        diagnostic_score_results.append({"score": score, "decision": observed})

    bank_results = []
    for count in (1, 32):
        item = _contribution(
            f"cat:bank:{count}",
            positive,
            relation_state="established",
            relation="support",
            reader_count=count,
            instrument_count=count,
        )
        observed = categorical_decide([item])
        _assert(f"C10-BANK-{count}", observed, "decided", "supported", "warranted_support_relation")
        bank_results.append({"count": count, "decision": observed})

    support_two = _contribution(
        "cat:support:2", positive, relation_state="established", relation="support"
    )
    duplicate_result = categorical_decide([support, support_two])
    rows.append(
        _assert(
            "C11-DUPLICATE-SAME-POLARITY",
            duplicate_result,
            "decided",
            "supported",
            "warranted_support_relation",
        )
    )

    result = {
        "experiment": "RC8J scalar-free categorical relation participation RC1",
        "rc8j_controls": {
            "positive": {
                "status": positive["authority"]["status"],
                "reason": positive["authority"]["reason"],
            },
            "unresolved": {
                "status": unresolved["authority"]["status"],
                "reason": unresolved["authority"]["reason"],
            },
            "rejected": {
                "status": rejected["authority"]["status"],
                "reason": rejected["authority"]["reason"],
            },
        },
        "proposition_relation": {
            "real_text_authority_established": False,
            "fixture_only": True,
            "states_under_test": ["established/support", "established/refutation", "unresolved"],
        },
        "cases": rows,
        "diagnostic_scalar_invariance": diagnostic_score_results,
        "reader_instrument_bank_invariance": bank_results,
        "scalar_decision_score_consumed": False,
        "all_controls_passed": True,
        "terminal_disposition": (
            "SCALAR_FREE_CATEGORICAL_PARTICIPATION_IS_COHERENT_GIVEN_SEPARATELY_ESTABLISHED_PROPOSITION_RELATION; "
            "REAL_TEXT_REMAINS_BLOCKED_ON_PROPOSITION_RELATION_AUTHORITY"
        ),
        "next_blocker": "PROPOSITION_RELATION_AUTHORITY_FOR_REAL_TEXT",
        "default_owner": "parallel_semantic_authority_programme",
    }

    out = run_output / "RC8J-CATEGORICAL-RELATION-RECEIPT.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
