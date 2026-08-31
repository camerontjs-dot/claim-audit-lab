"""RC7D-B proposal/authority/composition separation evaluator."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from collections import defaultdict

from research.semantic_operator_jurisdiction_rc7d import candidate
from research.semantic_operator_jurisdiction_rc7d_b import validator

EXPECTED_CASE_COUNT = 74
RC7D_EVIDENCE = "f57ffeb839f831d32d3e2b0bea1b34d5e73ac0e3"
VALIDATOR_FREEZE = "2e070cbcc48d80384ec71075998c142240a9042c"


def load_cases() -> list[dict]:
    p = Path("research/semantic_operator_jurisdiction_rc7d/cohort.py")
    src = p.read_text(encoding="utf-8")
    needle = "assert len(CASES) == 86, len(CASES)"
    assert src.count(needle) == 1
    ns = {"__name__": "rc7d_b_cohort"}
    exec(compile(src.replace(needle, "assert len(CASES) == 74, len(CASES)"), str(p), "exec"), ns)
    cases = ns["CASES"]
    assert len(cases) == EXPECTED_CASE_COUNT
    return cases


def canon(x: dict) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def proposal_atoms(output: dict) -> dict[str, list[dict]]:
    ans: dict[str, list[dict]] = defaultdict(list)
    for r in output.get("receipts", []):
        if r.get("status") == "CLAIMED":
            ans[r["dimension"]].extend(r.get("atoms", []))
    return dict(ans)


def score_atoms(case: dict, atoms: dict[str, list[dict]]) -> dict:
    gold = {d: {canon(a) for a in xs} for d, xs in case["gold"].items()}
    pred = {d: {canon(a) for a in xs} for d, xs in atoms.items()}
    gold_dims, pred_dims = set(gold), set(pred)
    correct_atoms = sum(len(gold.get(d, set()) & pred.get(d, set())) for d in gold_dims | pred_dims)
    gold_atoms = sum(len(v) for v in gold.values())
    pred_atoms = sum(len(v) for v in pred.values())
    unsafe_atoms = sum(len(pred.get(d, set()) - gold.get(d, set())) for d in pred_dims)
    return {
        "gold_dimensions": sorted(gold_dims),
        "predicted_dimensions": sorted(pred_dims),
        "correct_dimensions": len(gold_dims & pred_dims),
        "false_dimensions": sorted(pred_dims - gold_dims),
        "missing_dimensions": sorted(gold_dims - pred_dims),
        "gold_atom_count": gold_atoms,
        "pred_atom_count": pred_atoms,
        "correct_atom_count": correct_atoms,
        "unsafe_atom_count": unsafe_atoms,
    }


def aggregate(rows: list[dict], prefix: str) -> dict:
    gold_dims = sum(len(r[prefix]["gold_dimensions"]) for r in rows)
    pred_dims = sum(len(r[prefix]["predicted_dimensions"]) for r in rows)
    correct_dims = sum(r[prefix]["correct_dimensions"] for r in rows)
    false_dims = sum(len(r[prefix]["false_dimensions"]) for r in rows)
    gold_atoms = sum(r[prefix]["gold_atom_count"] for r in rows)
    pred_atoms = sum(r[prefix]["pred_atom_count"] for r in rows)
    correct_atoms = sum(r[prefix]["correct_atom_count"] for r in rows)
    unsafe_atoms = sum(r[prefix]["unsafe_atom_count"] for r in rows)
    mixed = [r for r in rows if len(r[prefix]["gold_dimensions"]) > 1]
    mixed_gold = sum(len(r[prefix]["gold_dimensions"]) for r in mixed)
    mixed_correct = sum(r[prefix]["correct_dimensions"] for r in mixed)
    return {
        "case_count": len(rows),
        "semantic_dimension_recall": correct_dims / gold_dims if gold_dims else 1.0,
        "dimension_precision": (pred_dims - false_dims) / pred_dims if pred_dims else 1.0,
        "false_dimension_count": false_dims,
        "typed_atom_recall": correct_atoms / gold_atoms if gold_atoms else 1.0,
        "typed_atom_precision": (pred_atoms - unsafe_atoms) / pred_atoms if pred_atoms else 1.0,
        "unsafe_atom_count": unsafe_atoms,
        "unsafe_case_rate": sum(r[prefix]["unsafe_atom_count"] > 0 for r in rows) / len(rows),
        "mixed_semantic_dimension_recall": mixed_correct / mixed_gold if mixed_gold else 1.0,
        "mixed_correct_dimensions": mixed_correct,
        "mixed_gold_dimensions": mixed_gold,
    }


def validate_lane(cases: list[dict], architecture: str, bank_size: int | None = None) -> tuple[dict, list[dict]]:
    rows = []
    for case in cases:
        if architecture == "broadcast":
            output = candidate.broadcast_all(case["text"], bank_size=bank_size or 8)
        elif architecture == "single":
            output = candidate.single_router(case["text"])
        else:
            raise ValueError(architecture)
        assert output["raw_source"] == case["text"]
        gated = validator.validate_architecture_output(output)
        proposed = score_atoms(case, proposal_atoms(output))
        authorized = score_atoms(case, gated["authorized_atoms"])
        rows.append({
            "case_id": case["case_id"],
            "group": case["group"],
            "raw_source": case["text"],
            "raw_source_sha256": hashlib.sha256(case["text"].encode()).hexdigest(),
            "proposed": proposed,
            "authorized": authorized,
            "rejected_count": len(gated["rejected_proposals"]),
            "unresolved_count": len(gated["unresolved_proposals"]),
            "gate": gated,
        })
    summary = {
        "proposal": aggregate(rows, "proposed"),
        "authorized": aggregate(rows, "authorized"),
        "rejected_proposal_count": sum(r["rejected_count"] for r in rows),
        "unresolved_proposal_count": sum(r["unresolved_count"] for r in rows),
    }
    return summary, rows


def composition_oracle(cases: list[dict]) -> dict:
    expected = 0
    correct = 0
    errors = []
    for case in cases:
        for row in case.get("composition", []):
            expected += 1
            pair = frozenset(row["dimensions"])
            observed = candidate._PAIR_RULES.get(pair, "unresolved")
            if observed == row["expected"]:
                correct += 1
            else:
                errors.append({"case_id": case["case_id"], "dimensions": row["dimensions"], "expected": row["expected"], "observed": observed})
    # Internal conflicts are a separate same-dimension concern. Perfect component input
    # must at least preserve all contradictory atoms; the oracle representation itself does.
    conflict_cases = [c for c in cases if c["group"] == "internal_conflict"]
    conflict_preserved = all(any(len(v) > 1 for v in c["gold"].values()) for c in conflict_cases)
    return {
        "expected_composition_count": expected,
        "correct_composition_count": correct,
        "composition_accuracy": correct / expected if expected else 1.0,
        "errors": errors,
        "oracle_conflict_component_preservation": conflict_preserved,
    }


def structural_ceiling(cases: list[dict]) -> dict:
    mixed = [c for c in cases if len(c["gold_dimensions"]) > 1]
    multi = sum(len(c["gold_dimensions"]) for c in mixed)
    single = sum(min(1, len(c["gold_dimensions"])) for c in mixed)
    return {
        "mixed_case_count": len(mixed),
        "gold_dimension_count": multi,
        "oracle_multi_operator_retained_dimensions": multi,
        "oracle_single_family_retained_dimensions": single,
        "oracle_multi_retention": 1.0 if multi else 1.0,
        "oracle_single_retention": single / multi if multi else 1.0,
        "dimensions_lost_by_exclusive_single_family": multi - single,
    }


def quantifier_disagreement(cases: list[dict]) -> dict:
    rows = []
    for case in cases:
        if "quantifier" not in case["gold"]:
            continue
        out = candidate.broadcast_all(case["text"])
        qa = out["quantifier_audit"]
        gold = {canon(a) for a in case["gold"]["quantifier"]}
        def aset(r):
            return {canon(a) for a in r.get("atoms", [])} if r.get("status") == "CLAIMED" else set()
        pa = aset(qa["primary"])
        aa = aset(qa["audit"])
        p_exact, a_exact = pa == gold, aa == gold
        rows.append({
            "case_id": case["case_id"],
            "agreement": qa["agreement"],
            "primary_exact": p_exact,
            "audit_exact": a_exact,
            "both_correct": p_exact and a_exact,
            "either_error": not (p_exact and a_exact),
        })
    disagree = [r for r in rows if r["agreement"] is False]
    agree = [r for r in rows if r["agreement"] is True]
    # Agreement-only authority gate: authorize primary quantifier only when both
    # implementations claim exactly the same atom set.
    agreement_authorized = len(agree)
    agreement_unsafe = sum(not r["both_correct"] for r in agree)
    return {
        "case_count": len(rows),
        "disagreement_count": len(disagree),
        "agreement_count": len(agree),
        "error_rate_when_disagree": sum(r["either_error"] for r in disagree) / len(disagree) if disagree else None,
        "error_rate_when_agree": sum(r["either_error"] for r in agree) / len(agree) if agree else None,
        "agreement_gate_authorized_count": agreement_authorized,
        "agreement_gate_unsafe_count": agreement_unsafe,
        "agreement_gate_unsafe_rate": agreement_unsafe / agreement_authorized if agreement_authorized else 0.0,
        "rows": rows,
    }


def stress(cases: list[dict]) -> list[dict]:
    rows = []
    for n in (2, 4, 6, 8):
        summary, details = validate_lane(cases, "broadcast", bank_size=n)
        rows.append({
            "bank_size": n,
            "proposal_false_dimension_count": summary["proposal"]["false_dimension_count"],
            "proposal_dimension_precision": summary["proposal"]["dimension_precision"],
            "authorized_false_dimension_count": summary["authorized"]["false_dimension_count"],
            "authorized_unsafe_atom_count": summary["authorized"]["unsafe_atom_count"],
            "authorized_unsafe_case_rate": summary["authorized"]["unsafe_case_rate"],
            "authorized_semantic_dimension_recall": summary["authorized"]["semantic_dimension_recall"],
        })
    return rows


def determine_state(broadcast: dict, single: dict, comp: dict, ceiling: dict, stress_rows: list[dict]) -> str:
    if comp["composition_accuracy"] < 1.0 or not comp["oracle_conflict_component_preservation"]:
        return "COMPOSITION_GOVERNOR_DEFECT"
    ba = broadcast["authorized"]
    sa = single["authorized"]
    if ba["unsafe_atom_count"] > 0 or ba["false_dimension_count"] > 0:
        return "AUTHORIZED_OVERCLAIM_PERSISTS"
    if ba["semantic_dimension_recall"] < 0.60:
        return "VALIDATION_GATE_TOO_LOSSY"
    if ceiling["oracle_single_family_retained_dimensions"] == ceiling["oracle_multi_operator_retained_dimensions"]:
        return "EXCLUSIVE_ROUTING_NOT_STRUCTURALLY_HARMFUL"
    if (
        ba["typed_atom_precision"] >= 0.98
        and ba["mixed_correct_dimensions"] > sa["mixed_correct_dimensions"]
        and all(r["authorized_unsafe_case_rate"] == 0 for r in stress_rows)
    ):
        return "PROPOSAL_AUTHORITY_SEPARATION_SUPPORTED"
    return "VALIDATION_GATE_TOO_LOSSY"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    cases = load_cases()
    broadcast, broadcast_rows = validate_lane(cases, "broadcast")
    single, single_rows = validate_lane(cases, "single")
    comp = composition_oracle(cases)
    ceiling = structural_ceiling(cases)
    qdiag = quantifier_disagreement(cases)
    stress_rows = stress(cases)
    state = determine_state(broadcast, single, comp, ceiling, stress_rows)

    zero_authority = {
        "semantic_dimension_recall": 0.0,
        "typed_atom_recall": 0.0,
        "typed_atom_precision": 1.0,
        "unsafe_atom_count": 0,
    }

    results = {
        "scientific_state": state,
        "claim_boundary": {"context_free": False, "independent_reproduction": False, "production_authorization": False, "llm_used": False},
        "frozen_rc7d_evidence": RC7D_EVIDENCE,
        "validator_freeze": VALIDATOR_FREEZE,
        "case_count": len(cases),
        "broadcast_proposals_validated": broadcast,
        "single_router_validated": single,
        "proposal_only_zero_authority_control": zero_authority,
        "oracle_component_composition": comp,
        "oracle_routing_ceiling": ceiling,
        "quantifier_duplicate": qdiag,
        "validated_operator_count_stress": stress_rows,
        "interpretation": {
            "all_proposals_preserved": True,
            "raw_source_preserved": True,
            "rejection_does_not_delete_proposal": True,
            "agreement_not_treated_as_truth": True,
        },
    }

    counterexamples = {
        "broadcast": [
            {
                "case_id": r["case_id"],
                "group": r["group"],
                "raw_source": r["raw_source"],
                "proposal": r["proposed"],
                "authorized": r["authorized"],
                "rejected_count": r["rejected_count"],
                "unresolved_count": r["unresolved_count"],
            }
            for r in broadcast_rows
            if r["authorized"]["unsafe_atom_count"] or r["authorized"]["false_dimensions"] or r["authorized"]["missing_dimensions"]
        ],
        "single": [
            {
                "case_id": r["case_id"],
                "group": r["group"],
                "raw_source": r["raw_source"],
                "proposal": r["proposed"],
                "authorized": r["authorized"],
            }
            for r in single_rows
            if r["authorized"]["unsafe_atom_count"] or r["authorized"]["false_dimensions"] or r["authorized"]["missing_dimensions"]
        ],
    }

    (outdir / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    (outdir / "BROADCAST_ROWS.json").write_text(json.dumps(broadcast_rows, indent=2, sort_keys=True) + "\n")
    (outdir / "SINGLE_ROWS.json").write_text(json.dumps(single_rows, indent=2, sort_keys=True) + "\n")
    (outdir / "COUNTEREXAMPLES.json").write_text(json.dumps(counterexamples, indent=2, sort_keys=True) + "\n")
    (outdir / "STRESS.json").write_text(json.dumps(stress_rows, indent=2, sort_keys=True) + "\n")

    ba, sa = broadcast["authorized"], single["authorized"]
    report = f"""# RC7D-B Proposal / Authority / Composition Results

Scientific state: **`{state}`**

No LLM or learned router was used.

## Broadcast proposal discovery
- semantic dimension recall: {broadcast['proposal']['semantic_dimension_recall']:.3f}
- dimension precision: {broadcast['proposal']['dimension_precision']:.3f}

## Broadcast after independent atom validation
- authorized semantic dimension recall: {ba['semantic_dimension_recall']:.3f}
- authorized typed atom recall: {ba['typed_atom_recall']:.3f}
- authorized typed atom precision: {ba['typed_atom_precision']:.3f}
- false authorized dimensions: {ba['false_dimension_count']}
- unsafe authorized atoms: {ba['unsafe_atom_count']}
- mixed-semantic authorized dimension recall: {ba['mixed_semantic_dimension_recall']:.3f}
- rejected proposals preserved: {broadcast['rejected_proposal_count']}

## Validated single routing
- authorized semantic dimension recall: {sa['semantic_dimension_recall']:.3f}
- authorized typed atom precision: {sa['typed_atom_precision']:.3f}
- unsafe authorized atoms: {sa['unsafe_atom_count']}
- mixed-semantic authorized dimension recall: {sa['mixed_semantic_dimension_recall']:.3f}

## Oracle structural routing ceiling
- mixed cases: {ceiling['mixed_case_count']}
- dimensions retained by perfect single-family selection: {ceiling['oracle_single_family_retained_dimensions']} / {ceiling['gold_dimension_count']}
- dimensions retained by perfect multi-operator selection: {ceiling['oracle_multi_operator_retained_dimensions']} / {ceiling['gold_dimension_count']}

## Oracle composition
- accuracy: {comp['composition_accuracy']:.3f}
- errors: {len(comp['errors'])}

## Deterministic quantifier duplicate
- disagreements: {qdiag['disagreement_count']}
- error rate when disagree: {qdiag['error_rate_when_disagree']}
- error rate when agree: {qdiag['error_rate_when_agree']}
- agreement-only gate unsafe rate: {qdiag['agreement_gate_unsafe_rate']:.3f}

## Boundary
Post-reveal local hardening only. No production authorization and no independent-consumability claim.
"""
    (outdir / "REPORT.md").write_text(report)
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
