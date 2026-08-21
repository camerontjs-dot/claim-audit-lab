#!/usr/bin/env python3
"""Recompute shadow evidence states after production P1 eligibility filtering.

This is an analysis-only adapter over the committed evidence-state projection.
It removes a passage only from the refutation channel when its existing
``trust_level`` is present and not ``primary``: the exact P1 adverse-decision
precondition in ``v1.impl.rules``. Support contributions are not removed.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.evidence_state import (
    ChannelCandidate,
    EvidenceState,
    EvidenceStateProjection,
    project_evidence_state,
    with_derived_channel_probabilities,
)
from scripts.evidence_state_shadow import _load_traces, shadow_decide


def _source_id(passage_id: str) -> str:
    return passage_id.split("/", 1)[0]


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


def build_eligibility_report(
    trace_dir: Path, *, signal_floor: float, trust_by_source: dict[str, str]
) -> dict[str, Any]:
    traces = list(with_derived_channel_probabilities(_load_traces(trace_dir)))
    config = load_default_audit_config()
    rows: list[dict[str, Any]] = []
    for trace in traces:
        before = project_evidence_state(trace, signal_floor=signal_floor)
        excluded = []
        eligible_refutation = []
        for candidate in before.refutation_candidates:
            source = _source_id(candidate.passage_id)
            trust = trust_by_source.get(source)
            if trust is not None and trust != "primary":
                excluded.append(
                    {
                        "passage_id": candidate.passage_id,
                        "channel": "refutation",
                        "score": candidate.score,
                        "source_id": source,
                        "trust_level": trust,
                        "reason": (
                            "production P1: present non-primary trust may not "
                            "solo-decide an adverse degree"
                        ),
                    }
                )
            else:
                eligible_refutation.append(candidate)

        if before.state in {"no_evidence", "unmeasured"}:
            after_state = before.state
        else:
            after_state = _state(before.support_candidates, tuple(eligible_refutation))
        after = EvidenceStateProjection(
            state=after_state,
            signal_floor=before.signal_floor,
            admitted_passage_ids=before.admitted_passage_ids,
            support_candidates=before.support_candidates,
            refutation_candidates=tuple(eligible_refutation),
        )
        raw_shadow = shadow_decide(trace, before, config)
        eligible_shadow = shadow_decide(trace, after, config)
        rows.append(
            {
                "claim_id": trace.claim_id,
                "current_verdict": trace.verdict.support_verdict,
                "before_state": before.state,
                "after_state": after.state,
                "raw_shadow_verdict": raw_shadow.verdict,
                "eligible_shadow_verdict": eligible_shadow.verdict,
                "state_changed": before.state != after.state,
                "shadow_verdict_changed": raw_shadow.verdict != eligible_shadow.verdict,
                "excluded_contributions": excluded,
                "before_support_candidates": [
                    candidate.model_dump() for candidate in before.support_candidates
                ],
                "before_refutation_candidates": [
                    candidate.model_dump() for candidate in before.refutation_candidates
                ],
                "after_support_candidates": [
                    candidate.model_dump() for candidate in after.support_candidates
                ],
                "after_refutation_candidates": [
                    candidate.model_dump() for candidate in after.refutation_candidates
                ],
            }
        )

    return {
        "schema_version": "cal-evidence-state-eligibility-shadow-v1",
        "source": str(trace_dir),
        "signal_floor": signal_floor,
        "trust_by_source": trust_by_source,
        "production_verdicts_changed": False,
        "n_claims": len(rows),
        "before_state_counts": dict(sorted(Counter(row["before_state"] for row in rows).items())),
        "after_state_counts": dict(sorted(Counter(row["after_state"] for row in rows).items())),
        "n_state_changed": sum(row["state_changed"] for row in rows),
        "n_shadow_verdict_changed": sum(row["shadow_verdict_changed"] for row in rows),
        "n_excluded_contributions": sum(len(row["excluded_contributions"]) for row in rows),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-dir", type=Path, required=True)
    parser.add_argument("--signal-floor", type=float, default=0.20)
    parser.add_argument(
        "--source-trust",
        action="append",
        default=[],
        metavar="SOURCE_ID=TRUST_LEVEL",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    trust_by_source = dict(item.split("=", 1) for item in args.source_trust)
    rendered = (
        json.dumps(
            build_eligibility_report(
                args.trace_dir,
                signal_floor=args.signal_floor,
                trust_by_source=trust_by_source,
            ),
            indent=2,
        )
        + "\n"
    )
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
