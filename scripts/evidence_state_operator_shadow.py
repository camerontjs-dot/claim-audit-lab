#!/usr/bin/env python3
"""Apply explicit semantic-operator validity to an eligibility shadow report.

This adapter is shadow-only. It distinguishes raw NLI channel measurements from
rule-derived channel contributions and removes only contributions explicitly
marked ``invalid`` or ``unknown``. Unknown operator results never decide. No
semantic judgment is inferred from a score.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.evidence_state import (
    ChannelCandidate,
    EvidenceState,
    EvidenceStateProjection,
)
from claim_audit_lab.v1.features import has_conjunct_scoped_negation
from claim_audit_lab.v1.models import AuditTrace
from scripts.evidence_state_shadow import ShadowVerdict, _load_traces, shadow_decide

OperatorStatus = Literal["valid", "invalid", "unknown"]
Channel = Literal["support", "refutation"]


class OperatorJudgment(BaseModel):
    """One evidence-backed judgment; never inferred from an NLI score."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    claim_id: str
    channel: Channel
    passage_ids: tuple[str, ...]
    status: OperatorStatus
    operator: str
    reason: str
    evidence_path: str
    derived: bool = False
    score: float | None = None


def recorded_operator_judgments(
    trace: AuditTrace, eligible_refutation: list[dict[str, Any]]
) -> list[OperatorJudgment]:
    """Translate only recorded production operator outcomes into judgments."""
    judgments: list[OperatorJudgment] = []
    probe = trace.negation_probe
    if probe is not None and eligible_refutation:
        if probe.abstained or probe.result is None:
            for candidate in eligible_refutation:
                judgments.append(
                    OperatorJudgment(
                        claim_id=trace.claim_id,
                        channel="refutation",
                        passage_ids=(str(candidate["passage_id"]),),
                        status="unknown",
                        operator="A4_negation_consistency",
                        reason="the recorded structural negator abstained; unknown may not decide",
                        evidence_path="AuditTrace.negation_probe",
                    )
                )
        else:
            probed = probe.result.passage_id
            for candidate in eligible_refutation:
                passage_id = str(candidate["passage_id"])
                if passage_id == probed:
                    status: OperatorStatus = (
                        "valid" if probe.result.label == "entail" else "invalid"
                    )
                    reason = (
                        "the same passage entails the structurally negated claim"
                        if status == "valid"
                        else "the same passage does not entail the structurally negated claim"
                    )
                else:
                    status = "unknown"
                    reason = "A4 recorded no semantic probe for this passage"
                judgments.append(
                    OperatorJudgment(
                        claim_id=trace.claim_id,
                        channel="refutation",
                        passage_ids=(passage_id,),
                        status=status,
                        operator="A4_negation_consistency",
                        reason=reason,
                        evidence_path="AuditTrace.negation_probe",
                    )
                )

    rule_ids = {item.rule_id for item in trace.rules_fired}
    if "A3_negation_backstop" in rule_ids:
        contributing_passage_id = trace.support_signal.contributing_passage_id
        if contributing_passage_id is None:
            raise ValueError("recorded A3 fire lacks a contributing passage")
        invalid_scope = trace.features.compound_claim and has_conjunct_scoped_negation(
            trace.claim_text
        )
        judgments.append(
            OperatorJudgment(
                claim_id=trace.claim_id,
                channel="refutation",
                passage_ids=(contributing_passage_id,),
                status="invalid" if invalid_scope else "valid",
                operator="A3_whole_claim_negation_mirror",
                reason=(
                    "negation is confined to a non-root conjunct; the unary mirror is invalid"
                    if invalid_scope
                    else "production A3's recorded whole-claim negation preconditions hold"
                ),
                evidence_path="AuditTrace.rules_fired + D8/X11 scope detector",
                derived=True,
                score=trace.support_signal.max_entailment_score,
            )
        )
    return judgments


def _state(
    support: tuple[ChannelCandidate, ...], refutation: tuple[ChannelCandidate, ...]
) -> EvidenceState:
    if support and refutation:
        return "mixed"
    if support:
        return "support_only"
    if refutation:
        return "refutation_only"
    return "read_silent"


def _candidate_key(channel: Channel, candidate: dict[str, Any]) -> tuple[str, str]:
    return channel, str(candidate["passage_id"])


def build_operator_report(
    eligibility_report: dict[str, Any],
    judgments: list[OperatorJudgment],
) -> dict[str, Any]:
    """Recompute states using only valid or ordinary direct-NLI contributions.

    A judgment overrides the ordinary direct-NLI contribution for its named
    passages. A valid derived judgment adds a channel contribution; invalid and
    unknown derived judgments remain in the audit ledger but never enter state.
    """
    by_claim: dict[str, list[OperatorJudgment]] = {}
    for judgment in judgments:
        by_claim.setdefault(judgment.claim_id, []).append(judgment)

    traces = {trace.claim_id: trace for trace in _load_traces(Path(eligibility_report["source"]))}
    config = load_default_audit_config()
    rows: list[dict[str, Any]] = []
    for source_row in eligibility_report["rows"]:
        claim_id = str(source_row["claim_id"])
        trace = traces[claim_id]
        manifest_judgments = by_claim.get(claim_id, [])
        recorded_judgments = recorded_operator_judgments(
            trace, source_row["after_refutation_candidates"]
        )
        # A later, explicit semantic operator may supersede a production
        # operator judgment for the same channel contribution.  Preserve the
        # superseded receipt below for auditability; do not let the malformed
        # earlier operator veto the replacement operator's result.
        manifest_keys = {
            (item.channel, passage_id)
            for item in manifest_judgments
            for passage_id in item.passage_ids
        }
        superseded = [
            item
            for item in recorded_judgments
            if any((item.channel, passage_id) in manifest_keys for passage_id in item.passage_ids)
        ]
        claim_judgments = manifest_judgments + [
            item for item in recorded_judgments if item not in superseded
        ]
        overrides: dict[tuple[str, str], list[OperatorJudgment]] = {}
        derived = []
        for judgment in claim_judgments:
            if judgment.derived:
                derived.append(judgment)
            else:
                for passage_id in judgment.passage_ids:
                    overrides.setdefault((judgment.channel, passage_id), []).append(judgment)

        retained: dict[Channel, list[ChannelCandidate]] = {"support": [], "refutation": []}
        excluded: list[dict[str, Any]] = []
        candidate_fields: tuple[tuple[Channel, str], ...] = (
            ("support", "after_support_candidates"),
            ("refutation", "after_refutation_candidates"),
        )
        for channel, field in candidate_fields:
            for raw in source_row[field]:
                candidate = ChannelCandidate.model_validate(raw)
                matched = overrides.get(_candidate_key(channel, raw), [])
                blocking = [item for item in matched if item.status != "valid"]
                if blocking:
                    excluded.append(
                        {
                            "passage_id": candidate.passage_id,
                            "channel": channel,
                            "score": candidate.score,
                            "judgments": [item.model_dump() for item in blocking],
                        }
                    )
                else:
                    retained[channel].append(candidate)

        for judgment in derived:
            if judgment.status != "valid":
                excluded.append(
                    {
                        "passage_ids": list(judgment.passage_ids),
                        "channel": judgment.channel,
                        "score": judgment.score,
                        "derived": True,
                        "judgments": [judgment.model_dump()],
                    }
                )
                continue
            if judgment.score is None:
                raise ValueError("valid derived judgments require a score")
            retained[judgment.channel].append(
                ChannelCandidate(
                    passage_id="operator-set:" + "+".join(judgment.passage_ids),
                    score=judgment.score,
                )
            )

        support = tuple(
            sorted(retained["support"], key=lambda item: (-item.score, item.passage_id))
        )
        refutation = tuple(
            sorted(retained["refutation"], key=lambda item: (-item.score, item.passage_id))
        )
        if source_row["after_state"] in {"no_evidence", "unmeasured"}:
            state: EvidenceState = source_row["after_state"]
        else:
            state = _state(support, refutation)
        projection = EvidenceStateProjection(
            state=state,
            signal_floor=float(eligibility_report["signal_floor"]),
            admitted_passage_ids=tuple(
                dict.fromkeys(
                    [item["passage_id"] for item in source_row["after_support_candidates"]]
                    + [item["passage_id"] for item in source_row["after_refutation_candidates"]]
                )
            ),
            support_candidates=support,
            refutation_candidates=refutation,
        )
        decision = shadow_decide(trace, projection, config)
        eligible_verdict: ShadowVerdict = source_row["eligible_shadow_verdict"]
        rows.append(
            {
                "claim_id": claim_id,
                "current_verdict": source_row["current_verdict"],
                "raw_state": source_row["before_state"],
                "eligible_state": source_row["after_state"],
                "operator_state": state,
                "raw_shadow_verdict": source_row["raw_shadow_verdict"],
                "eligible_shadow_verdict": eligible_verdict,
                "operator_shadow_verdict": decision.verdict,
                "operator_state_changed": source_row["after_state"] != state,
                "operator_verdict_changed": eligible_verdict != decision.verdict,
                "operator_judgments": [item.model_dump() for item in claim_judgments],
                "superseded_operator_judgments": [item.model_dump() for item in superseded],
                "excluded_operator_contributions": excluded,
                "operator_support_candidates": [item.model_dump() for item in support],
                "operator_refutation_candidates": [item.model_dump() for item in refutation],
            }
        )

    applied_judgments = [judgment for row in rows for judgment in row["operator_judgments"]]
    return {
        "schema_version": "cal-evidence-state-operator-shadow-v1",
        "source_eligibility_report": eligibility_report.get("source"),
        "signal_floor": eligibility_report["signal_floor"],
        "production_verdicts_changed": False,
        "n_claims": len(rows),
        "n_manifest_judgments": len(judgments),
        "n_applied_judgments": len(applied_judgments),
        "n_unknown_judgments": sum(item["status"] == "unknown" for item in applied_judgments),
        "operator_state_counts": dict(
            sorted(Counter(row["operator_state"] for row in rows).items())
        ),
        "n_operator_state_changed": sum(row["operator_state_changed"] for row in rows),
        "n_operator_verdict_changed": sum(row["operator_verdict_changed"] for row in rows),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eligibility-report", type=Path, required=True)
    parser.add_argument("--judgments", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    eligibility = json.loads(args.eligibility_report.read_text(encoding="utf-8"))
    judgments = [
        OperatorJudgment.model_validate(item, strict=False)
        for item in json.loads(args.judgments.read_text(encoding="utf-8"))["judgments"]
    ]
    rendered = json.dumps(build_operator_report(eligibility, judgments), indent=2) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
