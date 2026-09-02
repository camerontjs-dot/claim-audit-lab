"""Falsify RC8J warrant -> arbitrary scalar -> threshold decision shortcuts.

The runner uses the real frozen RC8J evaluator and the unchanged CAL v1
relation-preserving decision model. It deliberately does not invent a replacement
semantic-operator decision rule.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from claim_audit_lab.v1.decision_model import (
    CANONICAL_STAGE_ORDER,
    ChannelApertureAssessment,
    ChannelMeasurement,
    EligibilityAssessment,
    EvidenceContribution,
    EvidenceDecisionInput,
    StageReceipt,
    ValidityAssessment,
    evaluate_evidence,
)

from authority_consumption_rc1 import consume_external_authority
from run_authority_consumption_rc1 import (
    _load_rc8j,
    _typed_seam_control,
    _validated_b_coordinates,
)


PARENT_PROJECTION_HEAD = "57e59d8e5c565ff5e280357b322980e5c86b4cf2"
DECISION_MODEL_BLOB = "f0d9d3bc061d966ed9c8c16b3424b3dd5c3bb339"
_SIGNAL_FLOOR = 0.20
_SUPPORT_THRESHOLD = 0.70
_REFUTATION_THRESHOLD = 0.70


def _receipt(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def _stage_receipts() -> tuple[StageReceipt, ...]:
    return tuple(
        StageReceipt(
            stage=stage,
            evidence_path=f"rc8j-score-falsifier/{stage}",
            receipt_sha256=_receipt(f"stage:{stage}"),
        )
        for stage in CANONICAL_STAGE_ORDER
    )


def _apertures() -> tuple[ChannelApertureAssessment, ...]:
    return (
        ChannelApertureAssessment(
            channel="support",
            status="complete",
            reason="fixture stipulation: support aperture complete",
            evidence_path="rc8j-score-falsifier/aperture/support",
            receipt_sha256=_receipt("aperture:support"),
        ),
        ChannelApertureAssessment(
            channel="refutation",
            status="complete",
            reason="fixture stipulation: refutation aperture complete",
            evidence_path="rc8j-score-falsifier/aperture/refutation",
            receipt_sha256=_receipt("aperture:refutation"),
        ),
    )


def _require_warranted(authority_result: dict[str, Any]) -> None:
    authority = authority_result["authority"]
    if authority["status"] != "WARRANTED":
        raise ValueError(
            "semantic-operator valid contribution requires positive fixture authority; "
            f"got {authority['status']}/{authority['reason']}"
        )


def _semantic_operator(
    *,
    contribution_id: str,
    passage_id: str,
    channel: Literal["support", "refutation"],
    authority_result: dict[str, Any],
    score: float | None,
) -> EvidenceContribution:
    _require_warranted(authority_result)
    score_method = None if score is None else "caller_supplied_unowned_scalar"
    score_receipt = None if score is None else _receipt(f"unowned-score:{score:.6f}")
    return EvidenceContribution(
        contribution_id=contribution_id,
        channel=channel,
        passage_ids=(passage_id,),
        score=score,
        score_method=score_method,
        score_receipt_sha256=score_receipt,
        origin="semantic_operator",
        eligibility=EligibilityAssessment(
            status="eligible",
            reason="fixture stipulation: eligibility held fixed to isolate score semantics",
            evidence_path="rc8j-score-falsifier/eligibility",
            receipt_sha256=_receipt("eligibility:fixture-eligible"),
        ),
        validity=ValidityAssessment(
            status="valid",
            reason=(
                "fixture bridge for downstream falsifier only: exact frozen RC8J result was "
                "WARRANTED; this does not define a production validity mapping"
            ),
            evidence_path="rc8j-score-falsifier/authority/warranted",
            receipt_sha256=_receipt(
                authority_result["authority"]["status"]
                + ":"
                + authority_result["authority"]["reason"]
            ),
            operator="frozen_rc8j_fixture_bridge",
        ),
    )


def _decision(
    *,
    claim_id: str,
    passage_id: str,
    contributions: tuple[EvidenceContribution, ...],
):
    return evaluate_evidence(
        EvidenceDecisionInput(
            claim_id=claim_id,
            scope_status="in_scope",
            stage_receipts=_stage_receipts(),
            admitted_passage_ids=(passage_id,),
            measurements=(
                ChannelMeasurement(
                    passage_id=passage_id,
                    support_score=0.01,
                    refutation_score=0.01,
                    evidence_path="rc8j-score-falsifier/direct-channels-below-floor",
                    receipt_sha256=_receipt("channels:below-floor"),
                ),
            ),
            apertures=_apertures(),
            signal_floor=_SIGNAL_FLOOR,
            support_threshold=_SUPPORT_THRESHOLD,
            refutation_threshold=_REFUTATION_THRESHOLD,
            policy_id="rc8j-semantic-operator-score-falsifier-v1",
            policy_receipt_sha256=_receipt("policy:rc8j-score-falsifier-v1"),
            contributions=contributions,
        )
    )


def _stable_semantic_operator_surface(contribution: EvidenceContribution) -> dict[str, Any]:
    row = contribution.model_dump(mode="json")
    row.pop("score", None)
    row.pop("score_method", None)
    row.pop("score_receipt_sha256", None)
    return row


def _row(case_id: str, trace: Any, expected_disposition: str, expected_verdict: str | None, expected_reason: str) -> dict[str, Any]:
    observed = trace.decision
    if observed.disposition != expected_disposition:
        raise AssertionError(f"{case_id}: disposition {observed.disposition} != {expected_disposition}")
    if observed.verdict != expected_verdict:
        raise AssertionError(f"{case_id}: verdict {observed.verdict} != {expected_verdict}")
    if observed.reason_code != expected_reason:
        raise AssertionError(f"{case_id}: reason {observed.reason_code} != {expected_reason}")
    return {
        "case_id": case_id,
        "valid_state": trace.valid.state,
        "decision": observed.model_dump(mode="json"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-output", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    args = parser.parse_args()

    run_output = args.run_output.resolve()
    evaluator = _load_rc8j(args.rc8j_root.resolve())
    coords = _validated_b_coordinates(run_output)
    seam_case = _typed_seam_control(coords)

    positive = consume_external_authority(seam_case, evaluator, fixture_only=True)
    if positive["authority"]["status"] != "WARRANTED":
        raise AssertionError(f"positive frozen RC8J fixture is no longer warranted: {positive}")

    passage_id = coords["passage_id"]
    claim_id = coords["claim_id"]

    no_score = _semantic_operator(
        contribution_id="semantic-operator:support:fixed",
        passage_id=passage_id,
        channel="support",
        authority_result=positive,
        score=None,
    )
    score_069 = _semantic_operator(
        contribution_id="semantic-operator:support:fixed",
        passage_id=passage_id,
        channel="support",
        authority_result=positive,
        score=0.69,
    )
    score_070 = _semantic_operator(
        contribution_id="semantic-operator:support:fixed",
        passage_id=passage_id,
        channel="support",
        authority_result=positive,
        score=0.70,
    )
    score_095 = _semantic_operator(
        contribution_id="semantic-operator:support:fixed",
        passage_id=passage_id,
        channel="support",
        authority_result=positive,
        score=0.95,
    )

    stable_surfaces = {
        json.dumps(_stable_semantic_operator_surface(item), sort_keys=True)
        for item in (no_score, score_069, score_070, score_095)
    }
    if len(stable_surfaces) != 1:
        raise AssertionError("support score series changed a non-score contribution field")

    rows = [
        _row(
            "F1-NO-SCORE",
            _decision(claim_id=claim_id, passage_id=passage_id, contributions=(no_score,)),
            "abstained",
            None,
            "contribution_score_unmeasured",
        ),
        _row(
            "F2-SCORE-0.69",
            _decision(claim_id=claim_id, passage_id=passage_id, contributions=(score_069,)),
            "abstained",
            None,
            "support_below_decision_threshold",
        ),
        _row(
            "F3-SCORE-0.70",
            _decision(claim_id=claim_id, passage_id=passage_id, contributions=(score_070,)),
            "decided",
            "supported",
            "support_above_threshold",
        ),
        _row(
            "F4-SCORE-0.95",
            _decision(claim_id=claim_id, passage_id=passage_id, contributions=(score_095,)),
            "decided",
            "supported",
            "support_above_threshold",
        ),
    ]

    refute = _semantic_operator(
        contribution_id="semantic-operator:refutation:fixed",
        passage_id=passage_id,
        channel="refutation",
        authority_result=positive,
        score=0.70,
    )
    rows.append(
        _row(
            "F5-REFUTATION-CHANNEL-SCORE-0.70",
            _decision(claim_id=claim_id, passage_id=passage_id, contributions=(refute,)),
            "decided",
            "contradicted",
            "refutation_above_threshold",
        )
    )

    support_high = _semantic_operator(
        contribution_id="semantic-operator:mixed:support",
        passage_id=passage_id,
        channel="support",
        authority_result=positive,
        score=0.95,
    )
    refute_high = _semantic_operator(
        contribution_id="semantic-operator:mixed:refutation",
        passage_id=passage_id,
        channel="refutation",
        authority_result=positive,
        score=0.95,
    )
    mixed_trace = _decision(
        claim_id=claim_id,
        passage_id=passage_id,
        contributions=(support_high, refute_high),
    )
    mixed_row = _row(
        "F6-MIXED-HIGH-SCORES",
        mixed_trace,
        "abstained",
        None,
        "mixed_valid_evidence",
    )
    if mixed_row["valid_state"] != "mixed":
        raise AssertionError("mixed semantic-operator control did not preserve conflict")
    rows.append(mixed_row)

    unresolved_case = deepcopy(seam_case)
    unresolved_case["case_id"] = "F7-UNRESOLVED-AUTHORITY"
    unresolved_case["authority_subject_bundle_id"] = None
    unresolved = consume_external_authority(unresolved_case, evaluator, fixture_only=True)
    if unresolved["authority"] != {
        "status": "UNRESOLVED",
        "reason": "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED",
        "research_dependency": unresolved["authority"]["research_dependency"],
    }:
        raise AssertionError(f"directed unresolved authority control changed: {unresolved}")

    refused_valid_construction = False
    refused_error = None
    try:
        _semantic_operator(
            contribution_id="semantic-operator:unsafe-unresolved",
            passage_id=passage_id,
            channel="support",
            authority_result=unresolved,
            score=0.95,
        )
    except ValueError as exc:
        refused_valid_construction = True
        refused_error = str(exc)
    if not refused_valid_construction:
        raise AssertionError("unresolved authority was allowed to become valid semantic-operator evidence")

    result = {
        "experiment": "RC8J warranted semantic-operator score falsifier RC1",
        "parent_projection_head": PARENT_PROJECTION_HEAD,
        "decision_model_blob": DECISION_MODEL_BLOB,
        "rc8j_positive": {
            "status": positive["authority"]["status"],
            "reason": positive["authority"]["reason"],
            "supplies_channel": False,
            "supplies_scalar_decision_score": False,
        },
        "fixed_decision_policy": {
            "signal_floor": _SIGNAL_FLOOR,
            "support_threshold": _SUPPORT_THRESHOLD,
            "refutation_threshold": _REFUTATION_THRESHOLD,
        },
        "support_scalar_series_non_score_surface_identical": True,
        "cases": rows,
        "unresolved_authority_control": {
            "status": unresolved["authority"]["status"],
            "reason": unresolved["authority"]["reason"],
            "valid_semantic_operator_construction_refused": refused_valid_construction,
            "refusal": refused_error,
        },
        "observed_scalar_decision_flip": {
            "score_0_69": "abstained",
            "score_0_70": "supported",
            "only_scalar_value_changed_between_boundary_cases": True,
        },
        "observed_channel_decision_flip": {
            "support_at_0_70": "supported",
            "refutation_at_0_70": "contradicted",
            "rc8j_warrant_unchanged": True,
            "channel_is_fixture_stipulation": True,
        },
        "shortcut_supported": False,
        "terminal_disposition": (
            "RC8J_WARRANT_IS_NOT_DECISION_STRENGTH_OR_POLARITY; "
            "EXISTING_SEMANTIC_OPERATOR_DECISION_PATH_REQUIRES_ADDITIONAL_UNOWNED_SCORE_AND_CHANNEL_SEMANTICS"
        ),
        "next_decision": (
            "Choose successor research architecture: categorical warranted-relation participation "
            "versus separately authorized/calibrated decision-strength measurement."
        ),
    }

    out = run_output / "RC8J-SEMANTIC-OPERATOR-SCORE-FALSIFIER.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
