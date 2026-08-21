"""Dual-corpus smoke benchmark: whole-claim vs caller-declared atomic decomposition.

WHAT THIS IS: a self-authored smoke test. Both corpora under ``benchmarks/`` were
written by an agent (agy, 2026-08-18) together with their own expected verdicts, so
this measures whether CAL behaves as that author expected — not whether CAL is
correct. It is not gate evidence and not an accuracy claim. See
``outputs/2026-08-18-agy-decomposition-probe/FINDINGS.md`` D4.

WHAT IT IS NOT: evidence that decomposition improves CAL. The two corpora disagree
with each other, and on the messy corpus decomposition produces a false
``contradicted`` on a claim whose expected verdict is ``supported`` (MESSY-04).

Reason codes come from ``claim_audit_lab.ui.reasons.derive_reason``, which reads
CAL's recorded verdict and rule receipts rather than re-deciding from raw
probabilities.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

workbench_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(workbench_dir / "src"))

from claim_audit_lab.ui.reasons import derive_reason
from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.explicit_claims import (
    AtomProvenance,
    ExplicitClaimAtom,
    ExplicitClaimRequest,
)
from claim_audit_lab.v1.models import AuditConfig, AuditRequest, Passage
from claim_audit_lab.v1.runner import run_default_audit, run_default_explicit_claim_audit

# The corpora are fixtures, not sourced artifacts. Their atoms are authored in the
# JSON, so the explicit-claim provenance below is honestly a fixture reference —
# it is not a claim that a human declared these atoms against a real document.
_FIXTURE_SHA = "sha256:" + "0" * 64


def _fixture_provenance(corpus_id: str) -> AtomProvenance:
    return AtomProvenance(
        origin="operator_declared",
        reference_id=f"fixture:{corpus_id}",
        reference_sha256=_FIXTURE_SHA,
    )


def evaluate_benchmark(benchmark_path: Path, config: AuditConfig) -> list[dict]:
    data = json.loads(benchmark_path.read_text())
    corpus_id = data["corpus_id"]
    cases = data["cases"]

    print("\n" + "=" * 85)
    print(f"BENCHMARK: {corpus_id.upper()}  (self-authored fixture — not gate evidence)")
    print(f"Total Cases: {len(cases)}")
    print("=" * 85)

    results = []
    inconsistencies = []

    for c in cases:
        case_id = c["case_id"]
        passages = [Passage(passage_id=p["passage_id"], text=p["text"]) for p in c["passages"]]
        expected = c["expected_parent_verdict"]

        whole_trace = run_default_audit(
            AuditRequest(
                claim_id=case_id + "-whole",
                claim_text=c["parent_claim"],
                passages=passages,
                audit_config=config,
            )
        )
        whole_verdict = whole_trace.verdict.support_verdict
        whole_reason = derive_reason(whole_trace, config)

        explicit_trace = run_default_explicit_claim_audit(
            ExplicitClaimRequest(
                parent_claim_id=case_id,
                parent_claim_text=c["parent_claim"],
                operator=c["operator"],
                atoms=[
                    ExplicitClaimAtom(
                        atom_id=f"{case_id}-{a['atom_id']}",
                        claim_text=a["claim_text"],
                        provenance=_fixture_provenance(corpus_id),
                    )
                    for a in c["atoms"]
                ],
                passages=passages,
                audit_config=config,
            )
        )
        atomic_verdict = explicit_trace.verdict.support_verdict
        atomic_reason = derive_reason(explicit_trace, config)

        # Guard the property this script exists to protect: a reason must never
        # describe a verdict other than the one CAL returned.
        for label, verdict, reason in (
            ("whole", whole_verdict, whole_reason),
            ("atomic", atomic_verdict, atomic_reason),
        ):
            if reason["verdict"] != verdict:
                inconsistencies.append(f"{case_id} [{label}]: {reason['verdict']} != {verdict}")

        results.append(
            {
                "case_id": case_id,
                "expected": expected,
                "whole_verdict": whole_verdict,
                "atomic_verdict": atomic_verdict,
                "whole_match": whole_verdict == expected,
                "atomic_match": atomic_verdict == expected,
                "new_false_adverse": atomic_verdict == "contradicted" != expected,
            }
        )

        print(f"\n[{case_id}] expected: {expected.upper()}")
        print(f"  whole  -> {whole_verdict:20s} [{'PASS' if whole_verdict == expected else 'FAIL'}] {whole_reason['reason_code']}")
        print(f"           {whole_reason['detail']}")
        print(f"  atomic -> {atomic_verdict:20s} [{'PASS' if atomic_verdict == expected else 'FAIL'}] {atomic_reason['reason_code']}")
        print(f"           {atomic_reason['detail']}")

    n = len(results)
    whole_ok = sum(r["whole_match"] for r in results)
    atomic_ok = sum(r["atomic_match"] for r in results)
    false_adverse = [r["case_id"] for r in results if r["new_false_adverse"]]

    print("\n" + "-" * 85)
    print(f"SUMMARY — {corpus_id}")
    print(f"  whole-claim matches author expectation: {whole_ok}/{n}")
    print(f"  atomic     matches author expectation: {atomic_ok}/{n}")
    print(f"  NEW FALSE ADVERSE under atomic:        {len(false_adverse)} {false_adverse or ''}")
    if inconsistencies:
        print("  !! REASON/VERDICT INCONSISTENCY:")
        for line in inconsistencies:
            print(f"     {line}")
    else:
        print("  reason/verdict consistency:            OK (all reasons describe their own verdict)")
    print("-" * 85)
    return results


def main() -> None:
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    config = load_default_audit_config()
    benchmarks_dir = workbench_dir.parent / "benchmarks"

    for name in ("clean_canonical_reference.json", "realistic_prose_messy.json"):
        path = benchmarks_dir / name
        if not path.exists():
            raise FileNotFoundError(f"benchmark fixture missing: {path}")
        evaluate_benchmark(path, config)


if __name__ == "__main__":
    main()
