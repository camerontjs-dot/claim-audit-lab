#!/usr/bin/env python3
"""Project two-channel evidence states and compare the shadow decision table.

Read-only: loads existing trace JSON, derives legacy channel probabilities from
recorded logits when needed, and writes one JSON report to stdout.  It never runs
retrieval or model inference and never modifies the input traces.
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
    EvidenceStateProjection,
    project_evidence_state,
    with_derived_channel_probabilities,
)
from claim_audit_lab.v1.models import AuditConfig, AuditTrace, VerdictReason

ShadowVerdict = Literal[
    "supported",
    "partially_supported",
    "unsupported",
    "contradicted",
    "not_checkable",
    "needs_review",
    "deferred",
]


class ShadowDecision(BaseModel):
    """Experimental table output; never serialized into production traces."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    verdict: ShadowVerdict
    reason: str
    support_verdict_reason: VerdictReason | None = None


def shadow_decide(
    trace: AuditTrace, projection: EvidenceStateProjection, config: AuditConfig
) -> ShadowDecision:
    """Map state to an operator-blind shadow verdict for diff measurement only."""
    if trace.verdict.support_verdict_reason == "out_of_scope":
        return ShadowDecision(
            verdict="not_checkable",
            reason="production scope gate remains authoritative in Stages 1-2",
            support_verdict_reason="out_of_scope",
        )
    if projection.state == "unmeasured":
        return ShadowDecision(
            verdict="deferred",
            reason="trace lacks independent support/refutation measurements",
        )
    if projection.state == "no_evidence":
        return ShadowDecision(
            verdict="not_checkable",
            reason="no passage reached NLI",
            support_verdict_reason="no_evidence",
        )
    if projection.state == "read_silent":
        return ShadowDecision(
            verdict="unsupported",
            reason="evidence was read; neither channel reached the shadow floor",
        )
    if projection.state == "mixed":
        return ShadowDecision(
            verdict="needs_review",
            reason="support and refutation both reached the shadow floor",
        )
    if projection.state == "support_only":
        score = projection.support_candidates[0].score
        verdict: ShadowVerdict = (
            "supported" if score >= config.supported_threshold else "partially_supported"
        )
        return ShadowDecision(
            verdict=verdict,
            reason=(
                f"best support {score:.4f} compared with supported threshold "
                f"{config.supported_threshold:.4f}"
            ),
        )

    score = projection.refutation_candidates[0].score
    verdict = "contradicted" if score >= config.contradicted_threshold else "unsupported"
    return ShadowDecision(
        verdict=verdict,
        reason=(
            f"best refutation {score:.4f} compared with contradicted threshold "
            f"{config.contradicted_threshold:.4f}"
        ),
    )


def _load_traces(trace_dir: Path) -> list[AuditTrace]:
    return [
        AuditTrace.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted(trace_dir.glob("*.json"))
    ]


def build_report(trace_dir: Path, *, signal_floor: float) -> dict[str, Any]:
    traces = list(with_derived_channel_probabilities(_load_traces(trace_dir)))
    config = load_default_audit_config()
    rows: list[dict[str, Any]] = []
    for trace in traces:
        projection = project_evidence_state(trace, signal_floor=signal_floor)
        shadow = shadow_decide(trace, projection, config)
        current = trace.verdict.support_verdict
        changed = shadow.verdict not in {current, "deferred"}
        rows.append(
            {
                "claim_id": trace.claim_id,
                "state": projection.state,
                "current_verdict": current,
                "shadow_verdict": shadow.verdict,
                "changed": changed,
                "new_contradicted": shadow.verdict == "contradicted" and current != "contradicted",
                "support_to_adverse": current in {"supported", "partially_supported"}
                and shadow.verdict in {"unsupported", "contradicted"},
                "admitted_passage_ids": list(projection.admitted_passage_ids),
                "support_candidates": [
                    candidate.model_dump() for candidate in projection.support_candidates
                ],
                "refutation_candidates": [
                    candidate.model_dump() for candidate in projection.refutation_candidates
                ],
                "shadow_reason": shadow.reason,
            }
        )

    return {
        "schema_version": "cal-evidence-state-shadow-v1",
        "source": str(trace_dir),
        "signal_floor": signal_floor,
        "production_verdicts_changed": False,
        "n_claims": len(rows),
        "state_counts": dict(sorted(Counter(row["state"] for row in rows).items())),
        "current_verdict_counts": dict(
            sorted(Counter(row["current_verdict"] for row in rows).items())
        ),
        "shadow_verdict_counts": dict(
            sorted(Counter(row["shadow_verdict"] for row in rows).items())
        ),
        "n_changed": sum(row["changed"] for row in rows),
        "n_new_contradicted": sum(row["new_contradicted"] for row in rows),
        "n_support_to_adverse": sum(row["support_to_adverse"] for row in rows),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-dir", type=Path, required=True)
    parser.add_argument("--signal-floor", type=float, default=0.20)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = (
        json.dumps(build_report(args.trace_dir, signal_floor=args.signal_floor), indent=2) + "\n"
    )
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
