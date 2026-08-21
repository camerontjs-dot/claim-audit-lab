"""Audit the by-construction corpus and score CAL against the derived gold.

Runs the pinned v1 pipeline over ``outputs/2026-08-19-construction-gold/`` and
compares each verdict to the one derived from the construction. Writes traces so
``claim-audit explain`` can be run over them afterwards.

The variant groups are the point. Each group holds everything constant except
one declared parameter and states what that parameter must do:

* ``separates`` — the gold verdicts differ across the group, so CAL must split
  it the same way. Failing means the parameter is invisible to the rules.
* ``invariant`` — the gold verdicts are identical, so CAL must not split it at
  all. Failing means something with no bearing on the claim moved the verdict.

Both are scored the same way: CAL's partition of the group must equal gold's.
That is a stronger and fairer test than per-case agreement, because it does not
care whether CAL picks the same verdict as gold — only whether it responds to
the parameter the way the construction says it must.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.models import AuditRequest, Passage
from claim_audit_lab.v1.runner import run_default_audit

DEFAULT_CORPUS = Path(__file__).resolve().parents[2] / "outputs" / "2026-08-19-construction-gold"


def _partition(labels: dict[str, str]) -> set[frozenset[str]]:
    """Group member ids by the label they carry."""
    buckets: dict[str, set[str]] = {}
    for member, label in labels.items():
        buckets.setdefault(label, set()).add(member)
    return {frozenset(v) for v in buckets.values()}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--corpus",
        type=Path,
        default=DEFAULT_CORPUS,
        help="directory holding corpus.json (default: the 2026-08-19 build)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help=(
            "directory to write audit_results.json and traces/ into. Defaults to --corpus. "
            "Point it at a fresh dated directory to re-run without overwriting a sealed one."
        ),
    )
    args = ap.parse_args(argv)
    corpus_root: Path = args.corpus
    out_root: Path = args.out if args.out is not None else corpus_root
    traces_dir = out_root / "traces"

    corpus = json.loads((corpus_root / "corpus.json").read_text(encoding="utf-8"))
    config = load_default_audit_config()
    traces_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for case in corpus["cases"]:
        request = AuditRequest(
            claim_id=case["claim_id"],
            claim_text=case["claim_text"],
            passages=[
                Passage(passage_id=p["passage_id"], text=p["text"]) for p in case["passages"]
            ],
            audit_config=config,
            source_boundary=case["source_boundary"],
            claimed_material_is_a_named_gap=bool(
                case.get("claimed_material_is_a_named_gap", False)
            ),
        )
        trace = run_default_audit(request)
        (traces_dir / f"{case['claim_id']}.json").write_text(
            trace.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        floor = config.retrieval_floor
        distractor_ids = {p["passage_id"] for p in case["passages"] if p["role"] == "distractor"}
        admitted = [r.passage_id for r in trace.retrieval if r.score >= floor]
        rows.append(
            {
                "case_id": case["case_id"],
                "claim_id": case["claim_id"],
                "boundary": case["source_boundary"],
                "relation": case["relation"],
                "multi_document": case["multi_document"],
                "n_distractors": case["n_distractor_passages"],
                "distractor_kind": case.get("distractor_kind"),
                "n_admitted": len(admitted),
                "n_distractors_admitted": sum(1 for a in admitted if a in distractor_ids),
                "n_entailed": len(trace.entailment),
                "gold": case["expected_verdict"],
                "cal": trace.verdict.support_verdict,
                "reason": trace.verdict.support_verdict_reason,
                "rules": [r.rule_id for r in trace.rules_fired],
                "variant_group": case.get("variant_group"),
            }
        )

    agree = sum(1 for r in rows if r["gold"] == r["cal"])
    print(f"\nExact agreement with derived gold: {agree}/{len(rows)}\n")
    print(f"{'case':<8} {'boundary':<24} {'relation':<20} {'gold':<14} {'CAL':<14} ok")
    print("-" * 94)
    for r in rows:
        ok = "OK" if r["gold"] == r["cal"] else "MISS"
        print(
            f"{r['case_id']:<8} {r['boundary']:<24} {r['relation']:<20} "
            f"{r['gold']:<14} {r['cal']:<14} {ok}"
        )

    # --- per-relation and per-boundary breakdown -------------------------
    def breakdown(key: str) -> list[tuple[str, int, int]]:
        totals: Counter[str] = Counter()
        hits: Counter[str] = Counter()
        for r in rows:
            totals[str(r[key])] += 1
            if r["gold"] == r["cal"]:
                hits[str(r[key])] += 1
        return [(k, hits[k], totals[k]) for k in sorted(totals)]

    for key, title in (("relation", "by relation"), ("boundary", "by boundary")):
        print(f"\n{title}:")
        for name, hit, total in breakdown(key):
            print(f"  {name:<24} {hit}/{total}")

    # --- variant groups: partition agreement -----------------------------
    by_id = {r["case_id"]: r for r in rows}
    group_rows: list[dict[str, Any]] = []
    print("\nVariant groups — everything constant except one declared parameter:\n")
    print(f"{'group':<22} {'axis':<17} {'expects':<11} {'CAL':<12} reading")
    print("-" * 94)
    for gid, group in sorted(corpus["variant_groups"].items()):
        members = group["members"]
        gold_part = _partition({m: by_id[m]["gold"] for m in members})
        cal_part = _partition({m: by_id[m]["cal"] for m in members})
        matched = gold_part == cal_part
        cal_split = len(cal_part) > 1
        if matched:
            reading = "CAL responds as constructed"
        elif group["expectation"] == "separates":
            reading = (
                "splits, but not as gold does" if cal_split else "parameter invisible to the rules"
            )
        else:
            reading = "verdict moved on evidence that cannot bear on the claim"
        print(
            f"{gid:<22} {group['axis']:<17} {group['expectation']:<11} "
            f"{('match' if matched else 'MISMATCH'):<12} {reading}"
        )
        group_rows.append(
            {
                "group": gid,
                "axis": group["axis"],
                "expectation": group["expectation"],
                "members": members,
                "gold": {m: by_id[m]["gold"] for m in members},
                "cal": {m: by_id[m]["cal"] for m in members},
                "partition_match": matched,
                "reading": reading,
            }
        )

    matched_groups = sum(1 for g in group_rows if g["partition_match"])
    print(f"\nVariant-group partition agreement: {matched_groups}/{len(group_rows)}")

    # --- vacuity: a correct answer that no reasoning produced ------------
    # An abstention reached because nothing cleared the retrieval floor is the
    # right answer for none of the right reasons. Counting it as a win would
    # flatter the engine, and a distractor that never reaches the entailer
    # tests the floor rather than the rule layer.
    hollow = [r for r in rows if r["gold"] == r["cal"] and r["n_entailed"] == 0]
    print("\nVacuity check:")
    print(f"  correct with zero passages entailed : {len(hollow)}/{agree} of the agreements")
    if hollow:
        print(f"    {', '.join(r['case_id'] for r in hollow)}")
    with_d = [r for r in rows if r["n_distractors"]]
    reached = [r for r in with_d if r["n_distractors_admitted"]]
    print(f"  distractor arms whose distractors cleared the floor : {len(reached)}/{len(with_d)}")
    for r in with_d:
        print(
            f"    {r['case_id']:<8} kind={str(r['distractor_kind']):<15} "
            f"supplied={r['n_distractors']} admitted={r['n_distractors_admitted']} "
            f"entailer_saw={r['n_entailed']}"
        )
    boundary_read = any(
        g["axis"] == "source_boundary" and len(set(g["cal"].values())) > 1 for g in group_rows
    )
    print(
        f"  CAL verdict ever varies with source_boundary : {boundary_read} "
        "(if False, every boundary-axis `invariant` group passes vacuously)"
    )

    (out_root / "audit_results.json").write_text(
        json.dumps(
            {
                "corpus_id": corpus["corpus_id"],
                "n": len(rows),
                "exact_agreement": agree,
                "by_relation": {k: [h, t] for k, h, t in breakdown("relation")},
                "by_boundary": {k: [h, t] for k, h, t in breakdown("boundary")},
                "hollow_agreements": [r["case_id"] for r in hollow],
                "boundary_ever_read": boundary_read,
                "variant_groups_matched": matched_groups,
                "variant_groups_total": len(group_rows),
                "variant_groups": group_rows,
                "rows": rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nwrote {out_root / 'audit_results.json'} and {len(rows)} traces")


if __name__ == "__main__":
    main()
