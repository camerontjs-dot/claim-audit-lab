"""Score CAL against the fresh-blind constructed twin (derived gold)."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.models import AuditRequest, Passage
from claim_audit_lab.v1.runner import run_default_audit

ROOT = Path(__file__).resolve().parents[2] / "outputs" / "2026-08-20-fresh-blind-constructed"
TRACES = ROOT / "traces"


def main() -> None:
    corpus = json.loads((ROOT / "corpus.json").read_text(encoding="utf-8"))
    config = load_default_audit_config()
    TRACES.mkdir(parents=True, exist_ok=True)

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
        (TRACES / f"{case['claim_id']}.json").write_text(
            trace.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        rows.append(
            {
                "case_id": case["case_id"],
                "claim_id": case["claim_id"],
                "register": case["register"],
                "boundary": case["source_boundary"],
                "relation": case["relation"],
                "n_support": case["n_support_passages"],
                "n_entailed": len(trace.entailment),
                "gold": case["expected_verdict"],
                "cal": trace.verdict.support_verdict,
                "reason": trace.verdict.support_verdict_reason,
                "rules": [r.rule_id for r in trace.rules_fired],
            }
        )

    agree = sum(1 for r in rows if r["gold"] == r["cal"])
    print(f"\nExact agreement with derived gold: {agree}/{len(rows)}\n")
    print(f"{'case':<10} {'register':<20} {'relation':<20} {'gold':<16} {'CAL':<16} ok")
    print("-" * 102)
    for r in rows:
        ok = "OK" if r["gold"] == r["cal"] else "MISS"
        print(
            f"{r['case_id']:<10} {r['register']:<20} {r['relation']:<20} "
            f"{r['gold']:<16} {r['cal']:<16} {ok}"
        )

    def breakdown(key: str) -> list[tuple[str, int, int]]:
        totals: Counter[str] = Counter()
        hits: Counter[str] = Counter()
        for r in rows:
            totals[str(r[key])] += 1
            if r["gold"] == r["cal"]:
                hits[str(r[key])] += 1
        return [(k, hits[k], totals[k]) for k in sorted(totals)]

    for key, title in (
        ("register", "by register"),
        ("relation", "by relation"),
        ("boundary", "by boundary"),
    ):
        print(f"\n{title}:")
        for name, hit, total in breakdown(key):
            print(f"  {name:<24} {hit}/{total}")

    misses = [r for r in rows if r["gold"] != r["cal"]]
    print(f"\nmisses ({len(misses)}):")
    for r in misses:
        print(f"  {r['case_id']:<10} gold={r['gold']:<16} cal={r['cal']:<16} {r['rules']}")

    (ROOT / "audit_results.json").write_text(
        json.dumps(
            {
                "corpus_id": corpus["corpus_id"],
                "n": len(rows),
                "exact_agreement": agree,
                "by_register": {k: [h, t] for k, h, t in breakdown("register")},
                "by_relation": {k: [h, t] for k, h, t in breakdown("relation")},
                "by_boundary": {k: [h, t] for k, h, t in breakdown("boundary")},
                "misses": [r["case_id"] for r in misses],
                "rows": rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nwrote {ROOT / 'audit_results.json'} and {len(rows)} traces")


if __name__ == "__main__":
    main()
