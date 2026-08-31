"""Scientific RC7E runner v2.

This module is frozen before the held-out corpus is authored. It preserves raw
source, proposal/authority separation, per-receipt authority provenance, NLI
proposal lineage, and subset-local symbolic reasoning.
"""
from __future__ import annotations

import itertools
import json
import resource
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.language_instrument_ablation_rc7e.authority import validate_common_receipt
from research.language_instrument_ablation_rc7e.authority_v2 import validate_portfolio
from research.language_instrument_ablation_rc7e.contract import make_receipt, source_sha
from research.language_instrument_ablation_rc7e.equivalence import atom_key
from research.language_instrument_ablation_rc7e.evaluator import (
    agreement_disagreement_risk,
    authority_sets,
    evaluator_controls,
    gold_sets,
    order_independent_coverage_contribution,
    pairwise_overlap_and_error,
    proposal_sets,
    score_cases,
    unique_contributions,
)
from research.language_instrument_ablation_rc7e.instruments import (
    CoreNLPFamily,
    OWLRLReasoner,
    QuantulumInstrument,
    RC7DBaseline,
    StanzaFamily,
)
from research.language_instrument_ablation_rc7e.qualified_instruments import (
    ProvenancedDebertaNLI,
    QualifiedSuParSDP,
    instrument_identities_v2,
)
from research.language_instrument_ablation_rc7e.cohort import CASES, COHORT_FREEZE_EXPECTED

OUT = Path("research/language_instrument_ablation_rc7e/results")
ORDER = [
    "rc7d_deterministic",
    "quantulum3",
    "stanza_ud",
    "corenlp_openie",
    "corenlp_natlog",
    "corenlp_sutime",
    "stanza_constituency",
    "corenlp_coref_quote",
    "supar_sdp",
    "deberta_nli",
    "owlrl_reasoner",
]
PROPOSAL_INSTRUMENTS = [x for x in ORDER if x not in {"deberta_nli", "owlrl_reasoner"}]
FAMILY = {
    "rc7d_deterministic": "deterministic",
    "quantulum3": "quantitative",
    "stanza_ud": "stanza",
    "stanza_constituency": "stanza",
    "corenlp_openie": "corenlp",
    "corenlp_natlog": "corenlp",
    "corenlp_sutime": "corenlp",
    "corenlp_coref_quote": "corenlp",
    "supar_sdp": "supar",
    "deberta_nli": "nli",
    "owlrl_reasoner": "symbolic_reasoner",
}
PAIRINGS = [
    ("stanza_ud", "corenlp_openie"),
    ("stanza_ud", "supar_sdp"),
    ("corenlp_openie", "supar_sdp"),
    ("corenlp_sutime", "stanza_ud"),
    ("quantulum3", "stanza_ud"),
    ("corenlp_natlog", "rc7d_deterministic"),
    ("corenlp_coref_quote", "corenlp_openie"),
    ("deberta_nli", "stanza_ud"),
]


def tagged_typed(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for receipt in receipts:
        for row in receipt.get("candidate_atoms", []):
            if row.get("scorable") and isinstance(row.get("atom"), dict):
                tagged = dict(row)
                tagged["proposal_instrument_id"] = receipt["instrument_id"]
                rows.append(tagged)
    return rows


def agreement_receipt(raw: str, receipts: list[dict[str, Any]]) -> dict[str, Any]:
    by_key = defaultdict(set)
    row_by_key = {}
    for receipt in receipts:
        if receipt["instrument_id"] in {"deberta_nli", "owlrl_reasoner"}:
            continue
        for row in receipt.get("candidate_atoms", []):
            if not row.get("scorable") or not isinstance(row.get("atom"), dict):
                continue
            key = atom_key(row["dimension"], row["atom"])
            by_key[key].add(FAMILY.get(receipt["instrument_id"], receipt["instrument_id"]))
            row_by_key[key] = row
    agreed = [row_by_key[key] for key, families in by_key.items() if len(families) >= 2]
    dims = sorted({row["dimension"] for row in agreed})
    return make_receipt(
        raw,
        instrument_id="agreement_only",
        instrument_identity={
            "version": "rc7e-v2",
            "rule": "same canonical typed atom from >=2 distinct runtime families",
        },
        measurement_principle="cross-family proposal agreement control",
        status="CLAIMED" if agreed else "NOT_APPLICABLE",
        proposed_dimensions=dims,
        candidate_atoms=agreed,
        jurisdiction=[],
        limitations=["agreement is evidence, not truth or authority"],
        residue=[],
    )


def run_case(case, stanza, core, supar, nli, owl):
    raw = case["text"]
    receipts = [RC7DBaseline().run(raw), QuantulumInstrument().run(raw)]
    receipts.extend(
        [
            stanza.ud_receipt(raw),
            core.openie_receipt(raw),
            core.natlog_receipt(raw),
            core.sutime_receipt(raw),
            stanza.constituency_receipt(raw),
            core.coref_quote_receipt(raw),
            supar.run(raw),
        ]
    )
    receipts.append(nli.measure(raw, tagged_typed(receipts)))

    base_authority = validate_portfolio(
        raw, [r for r in receipts if r["instrument_id"] != "deberta_nli"]
    )
    owl_receipt = owl.infer(raw, base_authority.get("authorized_atoms", {}))
    receipts.append(owl_receipt)

    agreement = agreement_receipt(raw, receipts)
    agreement_authority = validate_common_receipt(agreement)
    return receipts, agreement, agreement_authority


def evaluate_subset(cases, by_inst, names):
    receipt_by_case = {}
    authority_by_case = {}
    reasoner = OWLRLReasoner()
    for case in cases:
        cid = case["case_id"]
        raw = case["text"]
        selected = [
            by_inst[name][cid]
            for name in names
            if name != "owlrl_reasoner" and cid in by_inst.get(name, {})
        ]
        authority_inputs = [r for r in selected if r["instrument_id"] != "deberta_nli"]
        auths = []
        base_authority = None
        if authority_inputs:
            base_authority = validate_portfolio(raw, authority_inputs)
            auths.append(base_authority)
        proposal_receipts = list(selected)
        if "owlrl_reasoner" in names:
            warranted = base_authority.get("authorized_atoms", {}) if base_authority else {}
            reasoner_receipt = reasoner.infer(raw, warranted)
            proposal_receipts.append(reasoner_receipt)
            auths.append(validate_common_receipt(reasoner_receipt))
        receipt_by_case[cid] = proposal_receipts
        authority_by_case[cid] = auths
    return score_cases(cases, receipt_by_case, authority_by_case), receipt_by_case, authority_by_case


def nli_diagnostic(cases, by_inst):
    correct = []
    wrong = []
    by_origin = defaultdict(lambda: {"correct": [], "wrong": []})
    for case in cases:
        _, gold_atoms = gold_sets(case)
        receipt = by_inst.get("deberta_nli", {}).get(case["case_id"])
        if not receipt:
            continue
        for item in receipt.get("native_output", []):
            atom = item.get("proposal_atom")
            dim = item.get("proposal_dimension")
            if not isinstance(atom, dict) or not dim:
                continue
            key = atom_key(dim, atom)
            entailment = float(item.get("scores", {}).get("entailment", 0.0))
            target = correct if key in gold_atoms else wrong
            target.append(entailment)
            for origin in item.get("proposal_instrument_ids", []):
                by_origin[origin]["correct" if key in gold_atoms else "wrong"].append(entailment)
    return {
        "correct_count": len(correct),
        "wrong_count": len(wrong),
        "mean_entailment_correct": statistics.mean(correct) if correct else None,
        "mean_entailment_wrong": statistics.mean(wrong) if wrong else None,
        "by_proposal_origin": {
            origin: {
                "correct_count": len(rows["correct"]),
                "wrong_count": len(rows["wrong"]),
                "mean_entailment_correct": statistics.mean(rows["correct"]) if rows["correct"] else None,
                "mean_entailment_wrong": statistics.mean(rows["wrong"]) if rows["wrong"] else None,
            }
            for origin, rows in by_origin.items()
        },
        "note": "diagnostic relation measurement only; no threshold grants authority",
    }


def composition_accuracy(cases, receipt_by_case, authority_by_case):
    proposal_exact = 0
    authorized_exact = 0
    for case in cases:
        cid = case["case_id"]
        gd, ga = gold_sets(case)
        pd, pa = proposal_sets(receipt_by_case.get(cid, []))
        ad, aa = authority_sets(authority_by_case.get(cid, []))
        proposal_exact += int(pd == gd and pa == ga)
        authorized_exact += int(ad == gd and aa == ga)
    return {
        "proposal_exact_case_count": proposal_exact,
        "proposal_exact_case_rate": proposal_exact / len(cases) if cases else 0.0,
        "authorized_exact_case_count": authorized_exact,
        "authorized_exact_case_rate": authorized_exact / len(cases) if cases else 0.0,
    }


def metamorphic_performance(cases, receipt_by_case, authority_by_case):
    groups = defaultdict(list)
    for case in cases:
        if case.get("pair_id"):
            groups[case["pair_id"]].append(case)
    rows = []
    for pair_id, pair in sorted(groups.items()):
        if len(pair) != 2:
            rows.append({"pair_id": pair_id, "status": "UNRESOLVED_NON_BINARY_PAIR", "size": len(pair)})
            continue
        a, b = pair
        gda, gaa = gold_sets(a)
        gdb, gab = gold_sets(b)
        pda, paa = proposal_sets(receipt_by_case.get(a["case_id"], []))
        pdb, pab = proposal_sets(receipt_by_case.get(b["case_id"], []))
        ada, aaa = authority_sets(authority_by_case.get(a["case_id"], []))
        adb, aab = authority_sets(authority_by_case.get(b["case_id"], []))
        gold_dim_delta = gda ^ gdb
        gold_atom_delta = gaa ^ gab
        proposal_dim_delta = pda ^ pdb
        proposal_atom_delta = paa ^ pab
        auth_dim_delta = ada ^ adb
        auth_atom_delta = aaa ^ aab
        rows.append(
            {
                "pair_id": pair_id,
                "relation": a.get("pair_relation") or b.get("pair_relation"),
                "gold_dimension_delta": sorted(gold_dim_delta),
                "gold_atom_delta_count": len(gold_atom_delta),
                "proposal_dimension_delta": sorted(proposal_dim_delta),
                "proposal_atom_delta_count": len(proposal_atom_delta),
                "authorized_dimension_delta": sorted(auth_dim_delta),
                "authorized_atom_delta_count": len(auth_atom_delta),
                "proposal_dimension_delta_exact": proposal_dim_delta == gold_dim_delta,
                "proposal_atom_delta_exact": proposal_atom_delta == gold_atom_delta,
                "authorized_dimension_delta_exact": auth_dim_delta == gold_dim_delta,
                "authorized_atom_delta_exact": auth_atom_delta == gold_atom_delta,
            }
        )
    resolved = [r for r in rows if "proposal_atom_delta_exact" in r]
    return {
        "pair_count": len(resolved),
        "proposal_dimension_delta_exact_rate": statistics.mean([r["proposal_dimension_delta_exact"] for r in resolved]) if resolved else None,
        "proposal_atom_delta_exact_rate": statistics.mean([r["proposal_atom_delta_exact"] for r in resolved]) if resolved else None,
        "authorized_dimension_delta_exact_rate": statistics.mean([r["authorized_dimension_delta_exact"] for r in resolved]) if resolved else None,
        "authorized_atom_delta_exact_rate": statistics.mean([r["authorized_atom_delta_exact"] for r in resolved]) if resolved else None,
        "pairs": rows,
    }


def score_tag(cases, tag, by_inst, names):
    selected = [c for c in cases if tag in c.get("tags", [])]
    if not selected:
        return None
    metrics, _, _ = evaluate_subset(selected, by_inst, names)
    return metrics


def runtime_summary(by_inst, names):
    out = {}
    for name in names:
        receipts = list(by_inst.get(name, {}).values())
        out[name] = {
            "load_status": "FAILED_PRESENT"
            if any(r.get("runtime", {}).get("load_status") == "FAILED" for r in receipts)
            else "OK",
            "claimed_cases": sum(r.get("status") == "CLAIMED" for r in receipts),
            "failed_cases": sum(r.get("runtime", {}).get("load_status") == "FAILED" for r in receipts),
            "latency_s_total": sum(float(r.get("runtime", {}).get("latency_s", 0) or 0) for r in receipts),
        }
    return out


def all_subset_portfolios(cases, by_inst, runtime, baseline_metrics):
    fixed = ["rc7d_deterministic"]
    optional = [x for x in PROPOSAL_INSTRUMENTS if x != "rc7d_deterministic"]
    rows = []
    for k in range(len(optional) + 1):
        for combo in itertools.combinations(optional, k):
            for include_reasoner in (False, True):
                names = fixed + list(combo) + (["owlrl_reasoner"] if include_reasoner else [])
                metrics, _, _ = evaluate_subset(cases, by_inst, names)
                rows.append(
                    {
                        "instruments": names,
                        "instrument_count": len(names),
                        "proposal_recall": metrics["proposal"]["semantic_dimension_recall"],
                        "authorized_recall": metrics["authorized"]["semantic_dimension_recall"],
                        "authorized_typed_atom_precision": metrics["authorized"]["typed_atom_precision"],
                        "unsafe_authorized_atoms": metrics["authorized"]["unsafe_atom_count"],
                        "false_authorized_dimensions": metrics["authorized"]["false_dimension_count"],
                        "latency_s_observed_full_run": sum(runtime.get(n, {}).get("latency_s_total", 0.0) for n in names),
                    }
                )

    def dominates(a, b):
        better_or_equal = (
            a["proposal_recall"] >= b["proposal_recall"]
            and a["authorized_recall"] >= b["authorized_recall"]
            and a["authorized_typed_atom_precision"] >= b["authorized_typed_atom_precision"]
            and a["unsafe_authorized_atoms"] <= b["unsafe_authorized_atoms"]
            and a["false_authorized_dimensions"] <= b["false_authorized_dimensions"]
            and a["instrument_count"] <= b["instrument_count"]
            and a["latency_s_observed_full_run"] <= b["latency_s_observed_full_run"]
        )
        strict = any(
            [
                a["proposal_recall"] > b["proposal_recall"],
                a["authorized_recall"] > b["authorized_recall"],
                a["authorized_typed_atom_precision"] > b["authorized_typed_atom_precision"],
                a["unsafe_authorized_atoms"] < b["unsafe_authorized_atoms"],
                a["false_authorized_dimensions"] < b["false_authorized_dimensions"],
                a["instrument_count"] < b["instrument_count"],
                a["latency_s_observed_full_run"] < b["latency_s_observed_full_run"],
            ]
        )
        return better_or_equal and strict

    frontier = [row for row in rows if not any(dominates(other, row) for other in rows if other is not row)]
    baseline_recall = baseline_metrics["proposal"]["semantic_dimension_recall"]
    candidates = [
        row
        for row in rows
        if row["unsafe_authorized_atoms"] == 0
        and row["false_authorized_dimensions"] == 0
        and row["proposal_recall"] - baseline_recall >= 0.10
    ]
    candidates.sort(
        key=lambda r: (
            r["instrument_count"],
            -r["authorized_recall"],
            -r["proposal_recall"],
            r["latency_s_observed_full_run"],
        )
    )
    by_count = {}
    for count, bucket in itertools.groupby(sorted(rows, key=lambda r: r["instrument_count"]), key=lambda r: r["instrument_count"]):
        vals = list(bucket)
        by_count[str(count)] = {
            "subset_count": len(vals),
            "proposal_recall_min": min(r["proposal_recall"] for r in vals),
            "proposal_recall_median": statistics.median(r["proposal_recall"] for r in vals),
            "proposal_recall_max": max(r["proposal_recall"] for r in vals),
            "unsafe_authorized_atoms_min": min(r["unsafe_authorized_atoms"] for r in vals),
            "unsafe_authorized_atoms_median": statistics.median(r["unsafe_authorized_atoms"] for r in vals),
            "unsafe_authorized_atoms_max": max(r["unsafe_authorized_atoms"] for r in vals),
        }
    return {
        "evaluated_subset_count": len(rows),
        "pareto_frontier": frontier,
        "smallest_safe_gain_candidate": candidates[0] if candidates else None,
        "instrument_count_stress": by_count,
    }


def report_markdown(results):
    lines = [
        "# RC7E Semantic-Instrument Portfolio Map",
        "",
        "Research-only. No production authorization.",
        "",
        f"**Scientific state:** `{results['scientific_state']}`",
        "",
        "## Headline",
        f"- Cases: {results['case_count']}",
        f"- Raw-source preservation: {results['raw_source_preservation']:.3f}",
        f"- Baseline proposal dimension recall: {results['baseline']['proposal']['semantic_dimension_recall']:.3f}",
        f"- Complete union proposal dimension recall: {results['complete_union']['proposal']['semantic_dimension_recall']:.3f}",
        f"- Complete union authorized dimension recall: {results['complete_union']['authorized']['semantic_dimension_recall']:.3f}",
        f"- Complete union authorized typed-atom precision: {results['complete_union']['authorized']['typed_atom_precision']:.3f}",
        f"- Unsafe authorized atoms: {results['complete_union']['authorized']['unsafe_atom_count']}",
        f"- False authorized dimensions: {results['complete_union']['authorized']['false_dimension_count']}",
        "",
        "## Smallest safe gain candidate",
        f"`{results['subset_analysis']['smallest_safe_gain_candidate']}`",
        "",
        "## Instrument status",
    ]
    for iid, row in results["instrument_runtime"].items():
        lines.append(
            f"- `{iid}`: {row['load_status']} / proposals on {row['claimed_cases']} cases / failures {row['failed_cases']} / latency {row['latency_s_total']:.3f}s"
        )
    lines += ["", "## Unique correct direct contributions"]
    for iid, row in results["unique_contribution"].items():
        lines.append(
            f"- `{iid}`: {row.get('unique_correct_dimensions', 0)} dimensions; {row.get('unique_correct_atoms', 0)} scorable atoms"
        )
    lines += [
        "",
        "## Agreement/disagreement risk",
        f"`{results['agreement_disagreement_risk']}`",
        "",
        "## Residue",
        f"Residual semantic dimensions after complete proposal union: **{results['complete_union']['proposal']['residual_dimension_count']}**.",
    ]
    for dim, count in sorted(results["residual_by_dimension"].items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- `{dim}`: {count}")
    lines += ["", "## Strongest shared failures"]
    for row in results["strongest_shared_failures"][:12]:
        lines.append(f"- `{row['case_id']}` `{row['dimension']}` missed by {row['missed_by']} direct proposal instruments")
    lines += ["", "## Evaluator and apparatus notes"]
    for note in results.get("apparatus_notes", []):
        lines.append(f"- {note}")
    lines += [
        "",
        "## Bounded conclusion",
        results["bounded_conclusion"],
        "",
        f"Terminal research decision token: `{results['scientific_state']}`",
    ]
    return "\n".join(lines) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    controls = evaluator_controls()
    if not controls["all_passed"]:
        raise SystemExit("evaluator controls failed before scientific execution")

    stanza = StanzaFamily()
    core = CoreNLPFamily()
    supar = QualifiedSuParSDP()
    nli = ProvenancedDebertaNLI()
    owl = OWLRLReasoner()
    by_inst = defaultdict(dict)
    agreement_receipts = {}
    agreement_authorities = {}
    raw_ok = True
    try:
        for case in CASES:
            receipts, agreement, agreement_authority = run_case(case, stanza, core, supar, nli, owl)
            cid = case["case_id"]
            for receipt in receipts:
                by_inst[receipt["instrument_id"]][cid] = receipt
                raw_ok &= receipt["raw_source"] == case["text"] and receipt["raw_source_sha256"] == source_sha(case["text"])
            agreement_receipts[cid] = agreement
            agreement_authorities[cid] = agreement_authority
    finally:
        core.close()

    all_names = [name for name in ORDER if name in by_inst]
    complete, receipt_union, authority_union = evaluate_subset(CASES, by_inst, all_names)
    baseline, _, _ = evaluate_subset(CASES, by_inst, ["rc7d_deterministic"])
    individual = {name: evaluate_subset(CASES, by_inst, [name])[0] for name in all_names}

    cumulative = {}
    prefix = []
    for name in all_names:
        prefix.append(name)
        cumulative[str(len(prefix))] = {
            "instruments": list(prefix),
            "metrics": evaluate_subset(CASES, by_inst, prefix)[0],
        }
    leave_out = {
        name: evaluate_subset(CASES, by_inst, [x for x in all_names if x != name])[0]
        for name in all_names
    }
    pairings = {
        f"{a}+{b}": evaluate_subset(CASES, by_inst, [a, b])[0]
        for a, b in PAIRINGS
        if a in by_inst and b in by_inst
    }
    agreement = score_cases(
        CASES,
        {cid: [agreement_receipts[cid]] for cid in agreement_receipts},
        {cid: [agreement_authorities[cid]] for cid in agreement_authorities},
    )
    zero = score_cases(CASES, receipt_union, {c["case_id"]: [] for c in CASES})

    direct_names = [name for name in PROPOSAL_INSTRUMENTS if name in by_inst]
    unique = unique_contributions(CASES, by_inst, direct_names)
    unique["deberta_nli"] = {
        "unique_correct_dimensions": 0,
        "unique_correct_atoms": 0,
        "note": "relation measurement only; no direct proposal jurisdiction",
    }
    unique["owlrl_reasoner"] = {
        "unique_correct_dimensions": 0,
        "unique_correct_atoms": 0,
        "note": "conditional reasoning contribution is measured by subset deltas, not direct raw-source uniqueness",
    }
    shapley = order_independent_coverage_contribution(CASES, by_inst, direct_names)
    pairwise = pairwise_overlap_and_error(CASES, by_inst, direct_names)
    agree_risk = agreement_disagreement_risk(CASES, by_inst, direct_names, FAMILY)

    residual = Counter()
    shared = []
    for case in CASES:
        cid = case["case_id"]
        proposed_dims, _ = proposal_sets(receipt_union[cid])
        gold_dims, _ = gold_sets(case)
        for dim in gold_dims - proposed_dims:
            residual[dim] += 1
            missed = sum(
                1
                for name in direct_names
                if dim not in by_inst[name][cid].get("proposed_dimensions", [])
            )
            shared.append({"case_id": cid, "dimension": dim, "missed_by": missed})
    shared.sort(key=lambda x: (-x["missed_by"], x["case_id"], x["dimension"]))

    runtime = runtime_summary(by_inst, all_names)
    subset_analysis = all_subset_portfolios(CASES, by_inst, runtime, baseline)
    unseen_baseline = score_tag(CASES, "unseen_paraphrase", by_inst, ["rc7d_deterministic"])
    unseen_complete = score_tag(CASES, "unseen_paraphrase", by_inst, all_names)
    mixed_baseline = score_tag(CASES, "mixed_semantic", by_inst, ["rc7d_deterministic"])
    mixed_complete = score_tag(CASES, "mixed_semantic", by_inst, all_names)
    metamorphic = metamorphic_performance(CASES, receipt_union, authority_union)
    composition = composition_accuracy(CASES, receipt_union, authority_union)

    marginal = {}
    for name in all_names:
        loo = leave_out[name]
        marginal[name] = {
            "unique_correct_dimensions_direct": unique.get(name, {}).get("unique_correct_dimensions", 0),
            "unique_correct_atoms_direct": unique.get(name, {}).get("unique_correct_atoms", 0),
            "proposal_recall_delta_if_present": complete["proposal"]["semantic_dimension_recall"] - loo["proposal"]["semantic_dimension_recall"],
            "authorized_recall_delta_if_present": complete["authorized"]["semantic_dimension_recall"] - loo["authorized"]["semantic_dimension_recall"],
            "unsafe_authority_delta_if_present": complete["authorized"]["unsafe_atom_count"] - loo["authorized"]["unsafe_atom_count"],
            "false_authorized_dimension_delta_if_present": complete["authorized"]["false_dimension_count"] - loo["authorized"]["false_dimension_count"],
            "latency_s_observed_full_run": runtime[name]["latency_s_total"],
        }

    gain = complete["proposal"]["semantic_dimension_recall"] - baseline["proposal"]["semantic_dimension_recall"]
    strict_safe = complete["authorized"]["unsafe_atom_count"] == 0 and complete["authorized"]["false_dimension_count"] == 0
    major_fail = any(row["failed_cases"] > 0 for row in runtime.values())
    unseen_gain = None
    if unseen_baseline and unseen_complete:
        unseen_gain = unseen_complete["proposal"]["semantic_dimension_recall"] - unseen_baseline["proposal"]["semantic_dimension_recall"]

    candidate = subset_analysis["smallest_safe_gain_candidate"]
    if not controls["all_passed"] or not raw_ok:
        state = "ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE"
        conclusion = "Evaluator or raw-source preservation controls failed; scientific interpretation is blocked."
    elif major_fail:
        state = "ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE"
        conclusion = "At least one frozen instrument failed during held-out execution. Surviving lanes remain bounded evidence, but the complete frozen portfolio claim is technically inconclusive."
    elif candidate is not None and strict_safe and gain >= 0.10 and (unseen_gain is None or unseen_gain > 0):
        state = "PORTFOLIO_CANDIDATE_READY_FOR_HARDENING"
        conclusion = "At least one preregistered subset materially reduced semantic residue beyond frozen RC7D while retaining zero unsafe authorized atoms and zero false authorized dimensions, with gain not disappearing on the unseen-paraphrase slice. This supports hardening the smallest Pareto candidate, not production promotion."
    elif gain > 0:
        state = "MORE_NON_LLM_INSTRUMENT_RESEARCH_JUSTIFIED"
        conclusion = "Heterogeneous non-LLM measurements added semantic information, but the preregistered safety/coverage conditions for a hardening candidate were not met. A smaller discriminating non-LLM follow-up is justified before any LLM proposal experiment."
    else:
        state = "ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE"
        conclusion = "The tested heterogeneous portfolio did not materially reduce semantic-dimension residue beyond the frozen deterministic baseline under the frozen apparatus."

    results = {
        "experiment": "RC7E",
        "runner_version": "rc7e-run-ablation-v2-preheldout-frozen",
        "case_count": len(CASES),
        "cohort_freeze_expected": COHORT_FREEZE_EXPECTED,
        "evaluator_controls": controls,
        "raw_source_preservation": 1.0 if raw_ok else 0.0,
        "identities": instrument_identities_v2(),
        "order": all_names,
        "baseline": baseline,
        "individual": individual,
        "cumulative": cumulative,
        "leave_one_out": leave_out,
        "pairings": pairings,
        "complete_union": complete,
        "agreement_only": agreement,
        "preserve_all_authorize_none": zero,
        "oracle_dimension_ceiling": 1.0,
        "oracle_composition_accuracy": 1.0 if all(c.get("composition_oracle", True) for c in CASES) else None,
        "composition_accuracy": composition,
        "unique_contribution": unique,
        "order_independent_direct_coverage_contribution": shapley,
        "pairwise": pairwise,
        "agreement_disagreement_risk": agree_risk,
        "nli_diagnostic": nli_diagnostic(CASES, by_inst),
        "instrument_runtime": runtime,
        "marginal_value_components": marginal,
        "subset_analysis": subset_analysis,
        "unseen_paraphrase_baseline": unseen_baseline,
        "unseen_paraphrase_complete": unseen_complete,
        "mixed_semantic_baseline": mixed_baseline,
        "mixed_semantic_complete": mixed_complete,
        "metamorphic": metamorphic,
        "residual_by_dimension": dict(residual),
        "strongest_shared_failures": shared,
        "process_max_rss_kb": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "scientific_state": state,
        "bounded_conclusion": conclusion,
        "apparatus_notes": [
            "No production src/ path is imported or modified by RC7E.",
            "Every raw-language instrument receives untouched source independently.",
            "CoreNLP logical lanes share one runtime family and are not counted as independent by annotator name alone.",
            "SuPar SDP uses independent Stanza preprocessing from raw because the frozen pretrained model requires token/lemma/POS input; this dependency is explicit.",
            "NLI measures source-to-typed-proposal relation only and cannot originate or authorize semantic atoms.",
            "OWL-RL operates only on subset-local already-authorized subclass premises and is recomputed for every ablation subset.",
            "Portfolio authority validates each instrument receipt separately before merging authority, preventing cross-instrument anchor pooling.",
            "Per-instrument peak memory is not isolated; process max RSS and environment/model-cache receipts are recorded instead.",
        ],
    }
    (OUT / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    (OUT / "REPORT.md").write_text(report_markdown(results), encoding="utf-8")
    (OUT / "RECEIPTS.json").write_text(
        json.dumps({name: by_inst[name] for name in all_names}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "scientific_state": state,
                "baseline_proposal_recall": baseline["proposal"]["semantic_dimension_recall"],
                "union_proposal_recall": complete["proposal"]["semantic_dimension_recall"],
                "authorized_recall": complete["authorized"]["semantic_dimension_recall"],
                "unsafe_authorized_atoms": complete["authorized"]["unsafe_atom_count"],
                "false_authorized_dimensions": complete["authorized"]["false_dimension_count"],
                "smallest_safe_gain_candidate": candidate,
                "residual_by_dimension": dict(residual),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
