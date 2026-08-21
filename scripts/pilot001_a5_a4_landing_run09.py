"""PILOT-001 run-09: what cal-rules-v1.9.0 (D9 + D10) does to the human corpus.

A **rules-only** replay. The recorded run-08 evidence — retrieval scores,
entailment results, features, support signal, negation probe — is fed back
through the landed rules layer unchanged, so the models never run and the only
thing that can move a verdict is the rule change under test. Re-running
inference would introduce a second variable for no benefit; the models are
pinned and their outputs are already sealed.

Passages come from the packet because A3's negation backstop parses passage
*text*, which the trace does not carry. A missing packet is a hard failure
rather than a silent empty-passage run.

DEV evidence. Not validation, not gate evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from claim_audit_lab.v1.config import load_default_audit_config, load_rules_file
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.models import AuditTrace, SupportSignal

try:
    from scripts.pilot001_premise_granularity_run04 import build_request_index
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from pilot001_premise_granularity_run04 import build_request_index  # type: ignore[no-redef]

EXPECTED_VERSION = "cal-rules-v1.10.0"


def _assert_baseline_carries_current_signal_fields(
    sample_trace: Path, *, allow_stale: bool
) -> None:
    """Refuse to replay a baseline that predates fields the current rules read (D15).

    A rules-only replay is only evidence for gates whose inputs already existed when
    the baseline was recorded. ``A5_conflicting_evidence`` reads ``best_entail`` and
    ``best_contradict``, added in ``cal-rules-v1.9.0``; replayed against a ``v1.7.0``
    baseline its precondition is unsatisfiable, so the replay reported "0 of 98
    verdicts changed" for a gate that in fact moves two. That figure was published.

    Silence from a harness that cannot see the thing is indistinguishable from a
    genuine no-op, so this fails closed rather than warning.
    """
    recorded = json.loads(sample_trace.read_text(encoding="utf-8")).get("support_signal", {})
    current = set(SupportSignal.model_fields)
    missing = sorted(current - set(recorded))
    if not missing:
        return
    message = (
        f"baseline {sample_trace.parent.parent.name} predates these SupportSignal fields: "
        f"{', '.join(missing)}. Any rule reading them cannot fire on this replay, so a "
        "'no change' result would be an artifact. Run the pipeline end to end "
        "(`claim-audit calibrate`) instead, or pass --allow-stale-baseline and do not cite "
        "the result for those rules. See D15."
    )
    if not allow_stale:
        raise SystemExit(message)
    print(f"WARNING: {message}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--expect-rules-version",
        default=EXPECTED_VERSION,
        help=(
            "Rules version this replay asserts. Override to re-run the same replay "
            "against the previous surface as a control, which is the only way to tell "
            "a change caused by this landing from one already in the tree."
        ),
    )
    parser.add_argument(
        "--allow-stale-baseline",
        action="store_true",
        help=(
            "Proceed even though the baseline predates fields the current rules read. "
            "The result cannot be cited as evidence about the gates that read them."
        ),
    )
    args = parser.parse_args()

    config = load_default_audit_config()
    payload, _ = load_rules_file()
    if payload["rules_version"] != args.expect_rules_version:
        raise ValueError(f"expected {args.expect_rules_version}, got {payload['rules_version']!r}")

    requests = build_request_index(args.packet, config)
    rules = VerdictRules(rules_file_sha=config.rules_file_sha)

    trace_files = sorted((args.baseline_run / "traces").glob("*.json"))
    if not trace_files:
        raise ValueError(f"no baseline traces under {args.baseline_run}")

    _assert_baseline_carries_current_signal_fields(
        trace_files[0], allow_stale=args.allow_stale_baseline
    )

    rows: list[dict[str, object]] = []
    changed: list[dict[str, object]] = []
    new_rules: Counter[str] = Counter()

    for path in trace_files:
        baseline = AuditTrace.model_validate_json(path.read_text(encoding="utf-8"))
        request = requests.get(baseline.claim_id)
        if request is None:
            raise ValueError(f"claim {baseline.claim_id} is not in the packet")

        verdict, fired = rules.apply(
            claim=baseline.claim_text,
            features=baseline.features,
            passages=request.passages,
            retrieval=baseline.retrieval,
            entailment=baseline.entailment,
            support_signal=baseline.support_signal,
            audit_config=config,
            negation_probe=baseline.negation_probe,
        )
        rule_ids = [r.rule_id for r in fired]
        new_rules.update(rule_ids)
        before = baseline.verdict.support_verdict
        after = verdict.support_verdict
        row = {
            "claim_id": baseline.claim_id,
            "before": before,
            "after": after,
            "before_reason": baseline.verdict.support_verdict_reason,
            "after_reason": verdict.support_verdict_reason,
            "before_rules": [r.rule_id for r in baseline.rules_fired],
            "after_rules": rule_ids,
        }
        rows.append(row)
        if before != after:
            changed.append(row)

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "run09-rules-replay.json").write_text(
        json.dumps(
            {
                "rules_version": payload["rules_version"],
                "rules_file_sha": config.rules_file_sha,
                "baseline_run": str(args.baseline_run),
                "n": len(rows),
                "n_verdict_changed": len(changed),
                "changed": changed,
                "rows": rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"claims replayed        : {len(rows)}")
    print(f"verdicts changed       : {len(changed)}")
    for row in changed:
        print(f"  {row['claim_id']}: {row['before']} -> {row['after']} ({row['after_rules']})")
    print(f"\nA5_conflicting_evidence fired        : {new_rules['A5_conflicting_evidence']}")
    print(f"A4_negation_consistency fired        : {new_rules['A4_negation_consistency']}")
    print(f"A4_negation_probe_uninformative fired: {new_rules['A4_negation_probe_uninformative']}")
    print(f"A4_hard_contradiction fired          : {new_rules['A4_hard_contradiction']}")
    print(f"\nwrote {args.out / 'run09-rules-replay.json'}")


if __name__ == "__main__":
    main()
