#!/usr/bin/env python3
"""Replay the strict contribution-ledger candidate over preserved shadow reports.

This adapter is deterministic and inference-free.  It consumes immutable trace JSON
plus the already-produced eligibility/operator reports, binds every constructed
assessment to an input-file hash, and emits a new DEV comparison report.  It never
modifies the preserved inputs or the production verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Literal

from claim_audit_lab.v1.decision_model import (
    CANONICAL_STAGE_ORDER,
    ChannelApertureAssessment,
    ChannelMeasurement,
    EligibilityAssessment,
    EligibilityStatus,
    EvidenceChannel,
    EvidenceContribution,
    EvidenceDecisionInput,
    Sha256Receipt,
    StageName,
    StageReceipt,
    ValidityAssessment,
    ValidityStatus,
    evaluate_evidence,
)
from claim_audit_lab.v1.evidence_state import with_derived_channel_probabilities
from claim_audit_lab.v1.models import AuditTrace


def _sha256(path: Path) -> Sha256Receipt:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(payload: dict[str, Any]) -> Sha256Receipt:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _candidate_key(channel: EvidenceChannel, passage_id: str) -> tuple[str, str]:
    return channel, passage_id


def _candidate_keys(row: dict[str, Any], prefix: str) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    fields: tuple[tuple[EvidenceChannel, str], ...] = (
        ("support", f"{prefix}_support_candidates"),
        ("refutation", f"{prefix}_refutation_candidates"),
    )
    for channel, field in fields:
        keys.update(_candidate_key(channel, str(item["passage_id"])) for item in row[field])
    return keys


def _source_id(passage_id: str) -> str:
    return passage_id.split("/", 1)[0]


def _as_channel(value: object) -> EvidenceChannel:
    if value == "support":
        return "support"
    if value == "refutation":
        return "refutation"
    raise ValueError(f"unknown evidence channel: {value!r}")


def _as_validity_status(value: object) -> ValidityStatus:
    if value == "valid":
        return "valid"
    if value == "invalid":
        return "invalid"
    if value == "unknown":
        return "unknown"
    raise ValueError(f"unknown semantic-validity status: {value!r}")


def _direct_eligibility(
    *,
    channel: EvidenceChannel,
    passage_id: str,
    eligibility_row: dict[str, Any],
    evidence_path: Path,
    receipt: Sha256Receipt,
) -> EligibilityAssessment:
    key = _candidate_key(channel, passage_id)
    before = _candidate_keys(eligibility_row, "before")
    after = _candidate_keys(eligibility_row, "after")
    if key not in before:
        raise ValueError(f"eligibility report omitted raw candidate {key!r}")
    if key in after:
        status: EligibilityStatus = "eligible"
        reason = "the preserved eligibility adapter retained this channel contribution"
    else:
        status = "ineligible"
        exclusions = [
            item
            for item in eligibility_row["excluded_contributions"]
            if _candidate_key(_as_channel(item["channel"]), str(item["passage_id"])) == key
        ]
        reason = (
            str(exclusions[0]["reason"])
            if exclusions
            else "the preserved eligibility adapter excluded this contribution"
        )
    return EligibilityAssessment(
        status=status,
        reason=reason,
        evidence_path=str(evidence_path),
        receipt_sha256=receipt,
    )


def _matching_direct_judgments(
    row: dict[str, Any], *, channel: EvidenceChannel, passage_id: str
) -> list[dict[str, Any]]:
    return [
        item
        for item in row.get("operator_judgments", [])
        if not bool(item.get("derived", False))
        and item["channel"] == channel
        and passage_id in item["passage_ids"]
    ]


def _direct_validity(
    *,
    channel: EvidenceChannel,
    passage_id: str,
    operator_row: dict[str, Any],
    evidence_path: Path,
    receipt: Sha256Receipt,
) -> ValidityAssessment:
    matched = _matching_direct_judgments(operator_row, channel=channel, passage_id=passage_id)
    if matched:
        statuses = {str(item["status"]) for item in matched}
        if len(statuses) == 1:
            status: ValidityStatus = statuses.pop()  # type: ignore[assignment]
        else:
            status = "unknown"
        operators = "+".join(sorted({str(item["operator"]) for item in matched}))
        reasons = "; ".join(str(item["reason"]) for item in matched)
        return ValidityAssessment(
            status=status,
            reason=reasons,
            operator=operators,
            evidence_path=str(evidence_path),
            receipt_sha256=receipt,
        )
    if channel == "refutation":
        return ValidityAssessment(
            status="unknown",
            reason="no explicit semantic-validity judgment covers this refutation",
            operator="refutation_operator_unmeasured",
            evidence_path=str(evidence_path),
            receipt_sha256=receipt,
        )
    return ValidityAssessment(
        status="valid",
        reason="the preserved operator path retained direct claim-identity support",
        operator="direct_claim_identity",
        evidence_path=str(evidence_path),
        receipt_sha256=receipt,
    )


def _derived_eligibility(
    *,
    judgment: dict[str, Any],
    trust_by_source: dict[str, str],
    evidence_path: Path,
    receipt: Sha256Receipt,
) -> EligibilityAssessment:
    channel = str(judgment["channel"])
    passage_ids = tuple(str(value) for value in judgment["passage_ids"])
    excluded = channel == "refutation" and any(
        (trust := trust_by_source.get(_source_id(passage_id))) is not None and trust != "primary"
        for passage_id in passage_ids
    )
    return EligibilityAssessment(
        status="ineligible" if excluded else "eligible",
        reason=(
            "at least one set member is explicitly non-primary under the preserved P1 policy"
            if excluded
            else "the preserved P1 policy found no explicit source exclusion for this set"
        ),
        evidence_path=str(evidence_path),
        receipt_sha256=receipt,
    )


def _derived_contributions(
    *,
    operator_row: dict[str, Any],
    trust_by_source: dict[str, str],
    eligibility_path: Path,
    eligibility_receipt: Sha256Receipt,
    operator_path: Path,
    operator_receipt: Sha256Receipt,
) -> tuple[EvidenceContribution, ...]:
    contributions: list[EvidenceContribution] = []
    derived = [
        item
        for item in operator_row.get("operator_judgments", [])
        if bool(item.get("derived", False))
    ]
    for index, judgment in enumerate(derived):
        passage_ids = tuple(str(value) for value in judgment["passage_ids"])
        reported_score = judgment.get("score")
        # Preserved multi-passage judgments carry a scalar but no aggregation
        # method.  Keep the contribution and deliberately withhold that score.
        score = (
            float(reported_score) if reported_score is not None and len(passage_ids) == 1 else None
        )
        contributions.append(
            EvidenceContribution(
                contribution_id=(
                    f"operator:{judgment['operator']}:{index}:" + "+".join(sorted(passage_ids))
                ),
                channel=_as_channel(judgment["channel"]),
                passage_ids=passage_ids,
                score=score,
                score_method="preserved_operator_judgment_score" if score is not None else None,
                score_receipt_sha256=operator_receipt if score is not None else None,
                origin="semantic_operator",
                eligibility=_derived_eligibility(
                    judgment=judgment,
                    trust_by_source=trust_by_source,
                    evidence_path=eligibility_path,
                    receipt=eligibility_receipt,
                ),
                validity=ValidityAssessment(
                    status=_as_validity_status(judgment["status"]),
                    reason=str(judgment["reason"]),
                    operator=str(judgment["operator"]),
                    evidence_path=str(operator_path),
                    receipt_sha256=operator_receipt,
                ),
            )
        )
    return tuple(contributions)


def _unmeasured_rule_contributions(
    *,
    trace: AuditTrace,
    operator_row: dict[str, Any],
    trust_by_source: dict[str, str],
    eligibility_path: Path,
    eligibility_receipt: Sha256Receipt,
    trace_path: Path,
    trace_receipt: Sha256Receipt,
) -> tuple[EvidenceContribution, ...]:
    """Keep unassessed legacy degree-changing operators explicit and non-deciding."""
    rule_ids = {item.rule_id for item in trace.rules_fired}
    numeric_judgments = [
        item
        for item in operator_row.get("operator_judgments", [])
        if bool(item.get("derived", False))
        and str(item["operator"]) in {"C6a_numeric_equality", "numeric_region_violation"}
    ]
    if "C6a_numeric" not in rule_ids or numeric_judgments:
        return ()
    passage_id = trace.support_signal.contributing_passage_id
    if passage_id is None:
        return ()
    placeholder = {
        "channel": "refutation",
        "passage_ids": [passage_id],
    }
    return (
        EvidenceContribution(
            contribution_id=f"operator:C6a_numeric_unmeasured:{passage_id}",
            channel="refutation",
            passage_ids=(passage_id,),
            score=None,
            score_method=None,
            score_receipt_sha256=None,
            origin="semantic_operator",
            eligibility=_derived_eligibility(
                judgment=placeholder,
                trust_by_source=trust_by_source,
                evidence_path=eligibility_path,
                receipt=eligibility_receipt,
            ),
            validity=ValidityAssessment(
                status="unknown",
                reason="legacy C6a changed the support degree without a typed operator judgment",
                operator="C6a_numeric_unmeasured",
                evidence_path=str(trace_path),
                receipt_sha256=trace_receipt,
            ),
        ),
    )


def _aperture(
    *,
    channel: EvidenceChannel,
    trace: AuditTrace,
    operator_row: dict[str, Any],
    evidence_path: Path,
    receipt: Sha256Receipt,
) -> ChannelApertureAssessment:
    judgments = [
        item for item in operator_row.get("operator_judgments", []) if item["channel"] == channel
    ]
    if any(item["status"] == "unknown" for item in judgments):
        status: Literal["complete", "incomplete", "unknown"] = "unknown"
        reason = "the preserved report contains an explicit unknown operator judgment"
    elif channel == "support" and trace.features.compound_claim:
        valid_set = any(
            item["operator"] == "compound_supporting_set" and item["status"] == "valid"
            for item in judgments
        )
        invalid_unary = any(
            item["operator"] == "compound_whole_claim_coverage" and item["status"] == "invalid"
            for item in judgments
        )
        if valid_set:
            status = "complete"
            reason = "a preserved valid compound passage-set judgment covers support"
        elif invalid_unary:
            status = "incomplete"
            reason = "preserved compound coverage is explicitly incomplete"
        else:
            status = "unknown"
            reason = "compound support passage-set completeness was not assessed"
    else:
        status = "complete"
        reason = "all at-floor contributions in this channel have terminal report status"
    return ChannelApertureAssessment(
        channel=channel,
        status=status,
        reason=reason,
        evidence_path=str(evidence_path),
        receipt_sha256=receipt,
    )


def _stage_receipts(
    *,
    trace_path: Path,
    trace_receipt: Sha256Receipt,
    eligibility_path: Path,
    eligibility_receipt: Sha256Receipt,
    operator_path: Path,
    operator_receipt: Sha256Receipt,
    policy_id: str,
    policy_receipt: Sha256Receipt,
) -> tuple[StageReceipt, ...]:
    """Bind the candidate replay to the canonical stage handoff order."""
    paths: dict[StageName, tuple[str, Sha256Receipt]] = {
        "scope_identity": (str(trace_path), trace_receipt),
        "decomposition": (str(trace_path), trace_receipt),
        "retrieve_admit": (str(trace_path), trace_receipt),
        "measure": (str(trace_path), trace_receipt),
        "eligibility": (str(eligibility_path), eligibility_receipt),
        "semantic_validity": (str(operator_path), operator_receipt),
        "aperture": (str(operator_path), operator_receipt),
        "aggregate": (f"policy:{policy_id}", policy_receipt),
        "resolve": (f"policy:{policy_id}", policy_receipt),
    }
    return tuple(
        StageReceipt(
            stage=stage,
            evidence_path=str(paths[stage][0]),
            receipt_sha256=paths[stage][1],
        )
        for stage in CANONICAL_STAGE_ORDER
    )


def _legacy_stratum(current: str, raw_state: str) -> str | None:
    if current != "not_checkable":
        return None
    return {
        "no_evidence": "B1_no_evidence",
        "read_silent": "B2a_read_silent",
        "refutation_only": "B2b_refutation_signal_on_legacy_abstention",
        "support_only": "B3_support_signal_discarded_by_legacy",
        "mixed": "B4_mixed_signal_on_legacy_abstention",
        "unmeasured": "unmeasured_legacy_abstention",
    }[raw_state]


def build_report(
    eligibility_path: Path,
    operator_path: Path,
    *,
    support_threshold: float,
    refutation_threshold: float,
) -> dict[str, Any]:
    """Build one receipt-bound candidate replay with no model calls."""
    eligibility_report = json.loads(eligibility_path.read_text(encoding="utf-8"))
    operator_report = json.loads(operator_path.read_text(encoding="utf-8"))
    signal_floor = float(eligibility_report["signal_floor"])
    if float(operator_report["signal_floor"]) != signal_floor:
        raise ValueError("eligibility and operator reports use different signal floors")

    trace_dir = Path(str(eligibility_report["source"]))
    trace_paths = sorted(trace_dir.glob("*.json"))
    raw_traces = [
        AuditTrace.model_validate_json(path.read_text(encoding="utf-8")) for path in trace_paths
    ]
    traces = list(with_derived_channel_probabilities(raw_traces))
    trace_path_by_claim = {
        trace.claim_id: path for trace, path in zip(traces, trace_paths, strict=True)
    }
    eligibility_rows = {str(row["claim_id"]): row for row in eligibility_report["rows"]}
    operator_rows = {str(row["claim_id"]): row for row in operator_report["rows"]}
    claim_ids = {trace.claim_id for trace in traces}
    if claim_ids != set(eligibility_rows) or claim_ids != set(operator_rows):
        raise ValueError("trace, eligibility, and operator claim sets differ")

    eligibility_receipt = _sha256(eligibility_path)
    operator_receipt = _sha256(operator_path)
    policy = {
        "label": "DEV candidate replay policy; no operating-point promotion",
        "signal_floor": signal_floor,
        "support_threshold": support_threshold,
        "refutation_threshold": refutation_threshold,
        "eligibility_report_sha256": eligibility_receipt,
        "operator_report_sha256": operator_receipt,
    }
    policy_receipt = _canonical_sha256(policy)
    trust_by_source = {
        str(key): str(value) for key, value in eligibility_report["trust_by_source"].items()
    }

    rows: list[dict[str, Any]] = []
    for trace in traces:
        eligibility_row = eligibility_rows[trace.claim_id]
        operator_row = operator_rows[trace.claim_id]
        trace_path = trace_path_by_claim[trace.claim_id]
        trace_receipt = _sha256(trace_path)
        measurements: list[ChannelMeasurement] = []
        contributions: list[EvidenceContribution] = []
        for result in trace.entailment:
            if result.p_entail is None or result.p_contradict is None:
                raise ValueError(f"trace {trace.claim_id} lacks derived channel probabilities")
            measurements.append(
                ChannelMeasurement(
                    passage_id=result.passage_id,
                    support_score=result.p_entail,
                    refutation_score=result.p_contradict,
                    evidence_path=str(trace_path),
                    receipt_sha256=trace_receipt,
                )
            )
            channel_scores: tuple[tuple[EvidenceChannel, float], ...] = (
                ("support", result.p_entail),
                ("refutation", result.p_contradict),
            )
            for channel, score in channel_scores:
                if score < signal_floor:
                    continue
                contributions.append(
                    EvidenceContribution(
                        contribution_id=f"direct:{channel}:{result.passage_id}",
                        channel=channel,
                        passage_ids=(result.passage_id,),
                        score=score,
                        score_method="direct_nli_probability",
                        score_receipt_sha256=trace_receipt,
                        origin="direct_nli",
                        eligibility=_direct_eligibility(
                            channel=channel,
                            passage_id=result.passage_id,
                            eligibility_row=eligibility_row,
                            evidence_path=eligibility_path,
                            receipt=eligibility_receipt,
                        ),
                        validity=_direct_validity(
                            channel=channel,
                            passage_id=result.passage_id,
                            operator_row=operator_row,
                            evidence_path=operator_path,
                            receipt=operator_receipt,
                        ),
                    )
                )
        derived_contributions = _derived_contributions(
            operator_row=operator_row,
            trust_by_source=trust_by_source,
            eligibility_path=eligibility_path,
            eligibility_receipt=eligibility_receipt,
            operator_path=operator_path,
            operator_receipt=operator_receipt,
        )
        derived_contributions += _unmeasured_rule_contributions(
            trace=trace,
            operator_row=operator_row,
            trust_by_source=trust_by_source,
            eligibility_path=eligibility_path,
            eligibility_receipt=eligibility_receipt,
            trace_path=trace_path,
            trace_receipt=trace_receipt,
        )
        admitted_ids = {result.passage_id for result in trace.entailment}
        adapter_exclusions = [
            {
                "contribution_id": item.contribution_id,
                "passage_ids": list(item.passage_ids),
                "reason": "operator judgment names a passage absent from the admitted trace",
            }
            for item in derived_contributions
            if not set(item.passage_ids).issubset(admitted_ids)
        ]
        contributions.extend(
            item for item in derived_contributions if set(item.passage_ids).issubset(admitted_ids)
        )
        aperture_channels: tuple[EvidenceChannel, ...] = ("support", "refutation")
        inputs = EvidenceDecisionInput(
            claim_id=trace.claim_id,
            scope_status=(
                "out_of_scope"
                if trace.verdict.support_verdict_reason == "out_of_scope"
                else "in_scope"
            ),
            stage_receipts=_stage_receipts(
                trace_path=trace_path,
                trace_receipt=trace_receipt,
                eligibility_path=eligibility_path,
                eligibility_receipt=eligibility_receipt,
                operator_path=operator_path,
                operator_receipt=operator_receipt,
                policy_id="cal-decision-model-replay-v0.1",
                policy_receipt=policy_receipt,
            ),
            admitted_passage_ids=tuple(result.passage_id for result in trace.entailment),
            measurements=tuple(measurements),
            apertures=tuple(
                _aperture(
                    channel=channel,
                    trace=trace,
                    operator_row=operator_row,
                    evidence_path=operator_path,
                    receipt=operator_receipt,
                )
                for channel in aperture_channels
            ),
            signal_floor=signal_floor,
            support_threshold=support_threshold,
            refutation_threshold=refutation_threshold,
            policy_id="cal-decision-model-replay-v0.1",
            policy_receipt_sha256=policy_receipt,
            contributions=tuple(contributions),
        )
        candidate = evaluate_evidence(inputs)
        decision = candidate.decision
        current = trace.verdict.support_verdict
        candidate_outcome = decision.verdict or "abstain"
        changed = candidate_outcome != current and not (
            candidate_outcome == "abstain" and current == "not_checkable"
        )
        rows.append(
            {
                "claim_id": trace.claim_id,
                "current_verdict": current,
                "candidate_outcome": candidate_outcome,
                "changed": changed,
                "new_contradicted": candidate_outcome == "contradicted"
                and current != "contradicted",
                "support_to_adverse": current in {"supported", "partially_supported"}
                and candidate_outcome == "contradicted",
                "legacy_stratum": _legacy_stratum(current, candidate.raw.state),
                "adapter_exclusions": adapter_exclusions,
                "candidate": candidate.model_dump(mode="json"),
            }
        )

    return {
        "schema_version": "cal-contribution-ledger-replay-v0.1",
        "label": "DEV deterministic replay; not validation or production evidence",
        "production_behavior_changed": False,
        "model_inference": False,
        "source_trace_dir": str(trace_dir),
        "eligibility_report": str(eligibility_path),
        "eligibility_report_sha256": eligibility_receipt,
        "operator_report": str(operator_path),
        "operator_report_sha256": operator_receipt,
        "policy": policy,
        "policy_receipt_sha256": policy_receipt,
        "limitations": [
            "missing source trust retains the preserved P1 parity behavior",
            "unjudged support is treated as direct claim-identity support",
            "unjudged refutation is explicit unknown and non-deciding",
            "aperture completeness is assessed only at the preserved signal floor",
            "multi-passage judgment scores are withheld because no aggregation method is recorded",
        ],
        "n_claims": len(rows),
        "candidate_outcome_counts": dict(
            sorted(Counter(row["candidate_outcome"] for row in rows).items())
        ),
        "reason_counts": dict(
            sorted(Counter(row["candidate"]["decision"]["reason_code"] for row in rows).items())
        ),
        "legacy_stratum_counts": dict(
            sorted(Counter(row["legacy_stratum"] for row in rows if row["legacy_stratum"]).items())
        ),
        "n_changed": sum(row["changed"] for row in rows),
        "n_new_contradicted": sum(row["new_contradicted"] for row in rows),
        "n_support_to_adverse": sum(row["support_to_adverse"] for row in rows),
        "n_adapter_exclusions": sum(len(row["adapter_exclusions"]) for row in rows),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eligibility-report", type=Path, required=True)
    parser.add_argument("--operator-report", type=Path, required=True)
    parser.add_argument("--support-threshold", type=float, required=True)
    parser.add_argument("--refutation-threshold", type=float, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report(
        args.eligibility_report,
        args.operator_report,
        support_threshold=args.support_threshold,
        refutation_threshold=args.refutation_threshold,
    )
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
