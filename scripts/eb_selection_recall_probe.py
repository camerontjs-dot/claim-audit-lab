#!/usr/bin/env python3
"""EB selection-recall probe — how much support did EB's per-claim selection drop?

The question
-----------
Every CAL number the project has reported is conditional on the Evidence Bundler's
per-claim selection: CAL only ever saw the passages EB nominated. The PILOT-001 human
gold cannot answer this, because the gold template instructs the annotator to judge
"against the evidence only" — the annotator read the same bundle. CAL and the human
therefore share EB's blind spot by construction, and their agreement can never reveal it.

The probe
---------
PILOT-001 is small enough to exhaust by machine. For every claim in every sealed run,
run the *same* pinned CAL v1 pipeline twice:

    arm A (as-ran)          claim x the passages EB SELECTED for that claim
    arm B (counterfactual)  claim x EVERY passage the run INDEXED

Arm A is always a subset of arm B, so arm B is strictly more evidence and every verdict
that changes is attributable to a passage EB selected out. Config, models, rules file and
thresholds are byte-identical across arms; the passage set is the only variable.

What it measures, and what it does not
--------------------------------------
Measures: *selection* recall — did EB's per-claim nomination drop a passage that CAL
would have found decisive, out of what that run indexed?

Does NOT measure: *index* recall (whether the run's chunker missed something in the
source documents), and it uses CAL as the judge of decisiveness, so it inherits CAL's
own errors. This is an upper bound on how much selection could be hurting, not a true
recall figure. Report it as that.

A clean result (zero flips) is informative: it says selection is not the ceiling and
moves the search upstream to indexing or to claim extraction.

Usage
-----
    python scripts/eb_selection_recall_probe.py --out outputs/<dir>
    python scripts/eb_selection_recall_probe.py --limit-runs 1   # smoke
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
PILOT_ROOT = (
    REPO_ROOT
    / "scaffold-claims-study"
    / "workbench"
    / "reproduce"
    / "build"
    / "pilot-001-audit"
)


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def discover_runs(pilot_root: Path) -> list[Path]:
    """Return each sealed run's audited bundle directory."""
    runs: list[Path] = []
    for run_dir in sorted(pilot_root.glob("rsh-*")):
        if not run_dir.is_dir():
            continue
        for audited in sorted(run_dir.glob("*-audited")):
            if (audited / "claims").is_dir():
                runs.append(audited)
    return runs


def load_indexed_passages(bundle: Path) -> dict[str, str]:
    """Every passage this run INDEXED, as {passage_id: text}. Arm B's universe."""
    indexed: dict[str, str] = {}
    evidence_dir = bundle / "evidence"
    if not evidence_dir.is_dir():
        return indexed
    for passage_yaml in sorted(evidence_dir.glob("*/passages/*.yaml")):
        record = _load_yaml(passage_yaml)
        if not isinstance(record, dict):
            continue
        pid = record.get("passage_id")
        text = record.get("passage_text")
        if pid and text:
            indexed[str(pid)] = str(text)
    return indexed


def load_claims(bundle: Path) -> list[dict[str, Any]]:
    """Each claim with the passages EB SELECTED for it. Arm A."""
    claims: list[dict[str, Any]] = []
    for claim_yaml in sorted((bundle / "claims").glob("*.yaml")):
        record = _load_yaml(claim_yaml)
        if not isinstance(record, dict):
            continue
        selected: dict[str, str] = {}
        for passage in record.get("evidence_passages") or []:
            if isinstance(passage, dict):
                pid = passage.get("passage_id")
                text = passage.get("passage_text")
                if pid and text:
                    selected[str(pid)] = str(text)
        claims.append(
            {
                "claim_id": str(record.get("claim_id", claim_yaml.stem)),
                "claim_text": str(record.get("claim_text", "")),
                "scaffold_support_status": record.get("scaffold_support_status"),
                "selected": selected,
            }
        )
    return claims


def _p_entail(result: Any) -> float:
    """Support probability for a premise, whatever the argmax label.

    ``score`` is the probability of the argmax class, so on a neutral result it
    reports confidence that the passage is irrelevant. ``p_entail`` carries the
    support probability unconditionally; it is None on traces predating the
    2026-08-05 instrumentation, in which case ``score`` is only usable when the
    label actually is ``entail``.
    """
    if result.p_entail is not None:
        return float(result.p_entail)
    return float(result.score) if result.label == "entail" else 0.0


def _summarize(trace: Any) -> dict[str, Any]:
    """Pull the verdict-bearing fields off an AuditTrace."""
    verdict = trace.verdict
    return {
        "support_verdict": verdict.support_verdict,
        "support_verdict_reason": verdict.support_verdict_reason,
        "audit_flags": list(verdict.audit_flags),
        "citation_status": verdict.citation_status,
        "audit_confidence": verdict.audit_confidence,
        "top_entail": round(max((_p_entail(r) for r in trace.entailment), default=0.0), 4)
        if trace.entailment
        else None,
        "n_entailed": len(trace.entailment),
        "n_retrieved": len(trace.retrieval),
    }


def _winning_passage(trace: Any) -> str | None:
    """The passage id carrying the highest support probability, if any."""
    best_id, best_p = None, -1.0
    for result in trace.entailment:
        p = _p_entail(result)
        if p > best_p:
            best_id, best_p = result.passage_id, p
    return best_id


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--out", type=Path, default=None, help="Directory for results")
    parser.add_argument("--limit-runs", type=int, default=None, help="Smoke-test cap")
    parser.add_argument("--limit-claims", type=int, default=None)
    args = parser.parse_args(argv)

    from claim_audit_lab.v1.config import load_default_audit_config
    from claim_audit_lab.v1.models import AuditRequest, Passage
    from claim_audit_lab.v1.runner import run_default_audit

    config = load_default_audit_config()

    runs = discover_runs(args.pilot_root)
    if args.limit_runs:
        runs = runs[: args.limit_runs]
    if not runs:
        print(f"FAIL: no sealed runs found under {args.pilot_root}", file=sys.stderr)
        return 1

    print(f"runs: {len(runs)}  |  config rules_file_sha: {config.rules_file_sha[:16]}")

    records: list[dict[str, Any]] = []
    flips = 0
    total = 0

    for bundle in runs:
        indexed = load_indexed_passages(bundle)
        claims = load_claims(bundle)
        if args.limit_claims:
            claims = claims[: args.limit_claims]
        print(f"\n{bundle.parent.name}: {len(claims)} claims, {len(indexed)} indexed passages")

        for claim in claims:
            selected = claim["selected"]
            # Arm B is the union, so arm A is guaranteed to be a subset even if a
            # selected passage is somehow absent from the evidence/ index.
            universe = {**indexed, **selected}
            extra_ids = sorted(set(universe) - set(selected))

            arm_a = AuditRequest(
                claim_id=claim["claim_id"],
                claim_text=claim["claim_text"],
                passages=[Passage(passage_id=p, text=t) for p, t in sorted(selected.items())],
                audit_config=config,
            )
            arm_b = AuditRequest(
                claim_id=claim["claim_id"],
                claim_text=claim["claim_text"],
                passages=[Passage(passage_id=p, text=t) for p, t in sorted(universe.items())],
                audit_config=config,
            )

            trace_a = run_default_audit(arm_a)
            trace_b = run_default_audit(arm_b)
            sum_a, sum_b = _summarize(trace_a), _summarize(trace_b)
            flipped = sum_a["support_verdict"] != sum_b["support_verdict"]

            winner_b = _winning_passage(trace_b)
            record = {
                "run": bundle.parent.name,
                "claim_id": claim["claim_id"],
                "claim_text": claim["claim_text"],
                "scaffold_support_status": claim["scaffold_support_status"],
                "n_selected": len(selected),
                "n_universe": len(universe),
                "n_extra": len(extra_ids),
                "arm_a": sum_a,
                "arm_b": sum_b,
                "flipped": flipped,
                # Set only on a flip: did the deciding passage come from outside
                # EB's selection? That is the receipt for a selection miss.
                "decisive_passage_b": winner_b,
                "decisive_was_unselected": bool(winner_b and winner_b not in selected),
            }
            records.append(record)
            total += 1
            if flipped:
                flips += 1
                marker = "  <-- decisive passage was UNSELECTED" if record["decisive_was_unselected"] else ""
                print(
                    f"  FLIP {claim['claim_id']}: "
                    f"{sum_a['support_verdict']} -> {sum_b['support_verdict']}"
                    f" (+{len(extra_ids)} passages){marker}"
                )

    transitions = Counter(
        f"{r['arm_a']['support_verdict']} -> {r['arm_b']['support_verdict']}"
        for r in records
        if r["flipped"]
    )
    summary = {
        "claims_probed": total,
        "verdict_flips": flips,
        "flip_rate": round(flips / total, 4) if total else 0.0,
        # Counted over ALL claims, not just flips: how often did arm B's best
        # supporting passage come from outside EB's selection at all? A flip is
        # the loud case; this is the broader signal.
        "claims_where_top_support_came_from_unselected_passage": sum(
            1 for r in records if r["decisive_was_unselected"]
        ),
        "flips_where_top_support_came_from_unselected_passage": sum(
            1 for r in records if r["flipped"] and r["decisive_was_unselected"]
        ),
        "transitions": dict(transitions),
        "arm_a_verdicts": dict(Counter(r["arm_a"]["support_verdict"] for r in records)),
        "arm_b_verdicts": dict(Counter(r["arm_b"]["support_verdict"] for r in records)),
        "rules_file_sha": config.rules_file_sha,
        "retrieval_floor": config.retrieval_floor,
        "measures": "selection recall only — not index recall; CAL is the judge of decisiveness",
    }

    print("\n" + "=" * 68)
    print(json.dumps(summary, indent=2))

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "records.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
        (args.out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"\nwrote {args.out}/records.json and summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
