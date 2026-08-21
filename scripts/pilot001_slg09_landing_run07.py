"""PILOT-001 run-07: confirm the cal-rules-v1.7.0 landing leaves the DEV baseline unchanged.

Replays the recorded run-06 evidence through the *landed package* rules with
live A4 negation-consistency probes. Per the preregistered trial
(``plans/adr-v1-slg09-negation-consistency.md``) the only A4-decided
contradiction is a semicolon compound whose negator abstains, so every one of
the 98 verdicts must be unchanged. DEV evidence, never validation or a gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from claim_audit_lab.v1.config import load_default_audit_config, load_rules_file
from claim_audit_lab.v1.features import negate_claim
from claim_audit_lab.v1.impl.entailer import DeBERTaEntailer
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.models import NegationProbe

try:
    from scripts.pilot001_floor_sweep import load_traces
    from scripts.pilot001_premise_granularity_run04 import build_request_index
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from pilot001_floor_sweep import load_traces  # type: ignore[no-redef]
    from pilot001_premise_granularity_run04 import (  # type: ignore[no-redef]
        build_request_index,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    config = load_default_audit_config()
    rules_payload, _ = load_rules_file()
    if rules_payload["rules_version"] != "cal-rules-v1.7.0":
        raise ValueError(f"expected cal-rules-v1.7.0, got {rules_payload['rules_version']!r}")
    baseline = load_traces(args.baseline_run / "traces")
    requests = build_request_index(args.packet, config)
    rules = VerdictRules(rules_file_sha=config.rules_file_sha)
    entailer = DeBERTaEntailer(revision=config.entailer)

    changed: list[str] = []
    probed: list[dict[str, object]] = []
    for claim_id, trace in sorted(baseline.items()):
        request = requests[claim_id]
        probe: NegationProbe | None = None
        signal = trace.support_signal
        if (
            signal.label == "contradict"
            and signal.max_entailment_score >= config.contradicted_threshold
        ):
            negated = negate_claim(trace.claim_text)
            passages = {p.passage_id: p for p in request.passages}
            contributing = (
                passages.get(signal.contributing_passage_id)
                if signal.contributing_passage_id
                else None
            )
            if negated is None or contributing is None:
                probe = NegationProbe(negated_claim=negated, abstained=True, result=None)
            else:
                probe = NegationProbe(
                    negated_claim=negated,
                    abstained=False,
                    result=entailer.entail(negated, contributing.text, contributing.passage_id),
                )
            probed.append({"claim_id": claim_id, "abstained": probe.abstained, "negated": negated})
        verdict, _fired = rules.apply(
            claim=trace.claim_text,
            features=trace.features,
            passages=request.passages,
            retrieval=trace.retrieval,
            entailment=trace.entailment,
            support_signal=trace.support_signal,
            audit_config=config,
            negation_probe=probe,
        )
        if (
            verdict.support_verdict != trace.verdict.support_verdict
            or verdict.support_verdict_reason != trace.verdict.support_verdict_reason
        ):
            changed.append(claim_id)

    if changed:
        raise ValueError(f"landing changed PILOT verdicts, expected none: {changed}")
    args.out.mkdir(parents=True, exist_ok=True)
    receipt = {
        "label": "DEV landing receipt (adaptation set), not validated and not a gate",
        "baseline_run": str(args.baseline_run.resolve()),
        "n_claims": len(baseline),
        "verdict_changes": changed,
        "probed_claims": probed,
        "rules_version": "cal-rules-v1.7.0",
        "rules_file_sha": config.rules_file_sha,
    }
    (args.out / "run-metadata.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"verdict_changes": 0, "probed": probed}, sort_keys=True))


if __name__ == "__main__":
    main()
