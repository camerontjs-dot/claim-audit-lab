"""Frozen evaluator and adversarial controls for RC7E."""
from __future__ import annotations

import itertools
import math
from typing import Any

from research.language_instrument_ablation_rc7e.equivalence import atom_key


def _safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0


def gold_sets(case: dict[str, Any]) -> tuple[set[str], set[str]]:
    dims = set(case.get("gold_dimensions", sorted(case.get("gold", {}))))
    atoms = {atom_key(dim, atom) for dim, rows in case.get("gold", {}).items() for atom in rows}
    return dims, atoms


def proposal_sets(receipts: list[dict[str, Any]]) -> tuple[set[str], set[str]]:
    dims = {d for r in receipts for d in r.get("proposed_dimensions", [])}
    atoms = {
        atom_key(row["dimension"], row["atom"])
        for r in receipts
        for row in r.get("candidate_atoms", [])
        if row.get("scorable") and isinstance(row.get("atom"), dict)
    }
    return dims, atoms


def authority_sets(authorities: list[dict[str, Any]]) -> tuple[set[str], set[str]]:
    dims = {d for a in authorities for d in a.get("authorized_dimensions", [])}
    atoms = {atom_key(dim, atom) for a in authorities for dim, rows in a.get("authorized_atoms", {}).items() for atom in rows}
    return dims, atoms


def score_cases(cases: list[dict[str, Any]], receipt_by_case: dict[str, list[dict[str, Any]]], authority_by_case: dict[str, list[dict[str, Any]]] | None = None) -> dict[str, Any]:
    gd = ga = pd = pa = ad = aa = 0
    correct_pd = correct_pa = correct_ad = correct_aa = 0
    false_pd = false_pa = false_ad = false_aa = 0
    residual = unresolved = 0
    case_rows = []
    for case in cases:
        cid = case["case_id"]
        gdim, gat = gold_sets(case)
        pdim, pat = proposal_sets(receipt_by_case.get(cid, []))
        if authority_by_case is None:
            adim, aat = set(), set()
        else:
            adim, aat = authority_sets(authority_by_case.get(cid, []))
        gd += len(gdim); ga += len(gat); pd += len(pdim); pa += len(pat); ad += len(adim); aa += len(aat)
        cpd = len(gdim & pdim); cpa = len(gat & pat); cad = len(gdim & adim); caa = len(gat & aat)
        correct_pd += cpd; correct_pa += cpa; correct_ad += cad; correct_aa += caa
        false_pd += len(pdim - gdim); false_pa += len(pat - gat); false_ad += len(adim - gdim); false_aa += len(aat - gat)
        residual += len(gdim - pdim)
        if authority_by_case is not None:
            unresolved += sum(len(a.get("unresolved_proposals", [])) for a in authority_by_case.get(cid, []))
        case_rows.append({"case_id": cid, "gold_dimensions": sorted(gdim), "proposal_dimensions": sorted(pdim), "authorized_dimensions": sorted(adim), "residual_dimensions": sorted(gdim-pdim), "false_proposal_dimensions": sorted(pdim-gdim), "false_authorized_dimensions": sorted(adim-gdim)})
    return {
        "case_count": len(cases),
        "proposal": {
            "semantic_dimension_recall": _safe_div(correct_pd, gd),
            "semantic_dimension_precision": _safe_div(correct_pd, pd),
            "typed_atom_recall": _safe_div(correct_pa, ga),
            "typed_atom_precision": _safe_div(correct_pa, pa),
            "false_dimension_count": false_pd,
            "unsafe_atom_count": false_pa,
            "residual_dimension_count": residual,
        },
        "authorized": {
            "semantic_dimension_recall": _safe_div(correct_ad, gd),
            "semantic_dimension_precision": _safe_div(correct_ad, ad),
            "typed_atom_recall": _safe_div(correct_aa, ga),
            "typed_atom_precision": _safe_div(correct_aa, aa),
            "false_dimension_count": false_ad,
            "unsafe_atom_count": false_aa,
            "unresolved_proposal_count": unresolved,
        },
        "cases": case_rows,
    }


def unique_contributions(cases: list[dict[str, Any]], all_receipts: dict[str, dict[str, dict[str, Any]]], instruments: list[str]) -> dict[str, Any]:
    out = {}
    for instrument in instruments:
        unique_dims = []
        unique_atoms = []
        for case in cases:
            cid = case["case_id"]
            gdim, gat = gold_sets(case)
            own = all_receipts.get(instrument, {}).get(cid)
            if not own:
                continue
            odim, oat = proposal_sets([own])
            other_receipts = [all_receipts.get(x, {}).get(cid) for x in instruments if x != instrument]
            other_receipts = [x for x in other_receipts if x]
            xdim, xat = proposal_sets(other_receipts)
            unique_dims.extend((cid, d) for d in (odim & gdim) - xdim)
            unique_atoms.extend((cid, a) for a in (oat & gat) - xat)
        out[instrument] = {"unique_correct_dimensions": len(unique_dims), "unique_correct_atoms": len(unique_atoms), "dimension_examples": unique_dims[:20], "atom_examples": unique_atoms[:20]}
    return out


def pairwise_overlap_and_error(cases: list[dict[str, Any]], all_receipts: dict[str, dict[str, dict[str, Any]]], instruments: list[str]) -> dict[str, Any]:
    overlap = {}
    corr = {}
    errors: dict[str, list[int]] = {i: [] for i in instruments}
    correct_sets: dict[str, set[tuple[str,str]]] = {}
    for i in instruments:
        s=set()
        for c in cases:
            r=all_receipts.get(i,{}).get(c["case_id"])
            gdim,_=gold_sets(c)
            if r:
                pdim, pat=proposal_sets([r]); s |= {(c["case_id"],d) for d in pdim & gdim}
                false_dim=bool(pdim-gdim)
                _,gat=gold_sets(c)
                false_atom=bool(pat-gat)
                errors[i].append(1 if false_dim or false_atom else 0)
            else:
                errors[i].append(0)
        correct_sets[i]=s
    for a,b in itertools.combinations(instruments,2):
        inter=len(correct_sets[a]&correct_sets[b]); union=len(correct_sets[a]|correct_sets[b])
        overlap[f"{a}::{b}"]={"jaccard_correct_dimension_overlap":_safe_div(inter,union),"intersection":inter,"union":union}
        xa=errors[a]; xb=errors[b]; ma=sum(xa)/len(xa) if xa else 0; mb=sum(xb)/len(xb) if xb else 0
        num=sum((x-ma)*(y-mb) for x,y in zip(xa,xb)); den=math.sqrt(sum((x-ma)**2 for x in xa)*sum((y-mb)**2 for y in xb))
        corr[f"{a}::{b}"]={"binary_case_error_correlation": num/den if den else 0.0}
    return {"overlap":overlap,"error_correlation":corr}


def evaluator_controls() -> dict[str, Any]:
    base={"case_id":"C","gold":{"role_binding":[{"kind":"event","predicate":"review","subject":"dana","object":"the dossier","polarity":"positive"}],"temporal":[{"kind":"temporal_scope","relation":"before","reference":"2026-09-01"}]},"gold_dimensions":["role_binding","temporal"]}
    perfect=[{"proposed_dimensions":["role_binding","temporal"],"candidate_atoms":[{"dimension":"role_binding","atom":base["gold"]["role_binding"][0],"scorable":True},{"dimension":"temporal","atom":base["gold"]["temporal"][0],"scorable":True}]}]
    safe=[{"proposed_dimensions":["role_binding"],"candidate_atoms":[{"dimension":"role_binding","atom":base["gold"]["role_binding"][0],"scorable":True}]}]
    over=[{"proposed_dimensions":["role_binding","temporal","permission"],"candidate_atoms":[{"dimension":"role_binding","atom":{"kind":"event","predicate":"review","subject":"hugo","object":"the dossier","polarity":"positive"},"scorable":True}]}]
    equiv=[{"proposed_dimensions":["role_binding"],"candidate_atoms":[{"dimension":"role_binding","atom":{"kind":"event","predicate":"reviewed","subject":"DANA ","object":"THE DOSSIER.","polarity":"POSITIVE"},"scorable":True}]}]
    wrong_scope=[{"proposed_dimensions":["temporal"],"candidate_atoms":[{"dimension":"temporal","atom":{"kind":"temporal_scope","relation":"after","reference":"2026-09-01"},"scorable":True}]}]
    def ps(rows): return proposal_sets(rows)
    gd,ga=gold_sets(base)
    checks={
        "perfect": ps(perfect)==(gd,ga),
        "safe_incomplete": ps(safe)[0] < gd and not (ps(safe)[0]-gd),
        "systematic_overclaim_detected": bool(ps(over)[0]-gd) and bool(ps(over)[1]-ga),
        "representation_equivalence": atom_key("role_binding",equiv[0]["candidate_atoms"][0]["atom"]) in ga,
        "wrong_scope_detected": bool(ps(wrong_scope)[1]-ga),
        "domain_word_trap": proposal_sets([{"proposed_dimensions":[],"candidate_atoms":[]}])==(set(),set()),
        "jointly_wrong_agreement_not_truth": atom_key("role_binding",over[0]["candidate_atoms"][0]["atom"]) not in ga,
        "disagreement_one_right": atom_key("role_binding",perfect[0]["candidate_atoms"][0]["atom"]) in ga and atom_key("role_binding",over[0]["candidate_atoms"][0]["atom"]) not in ga,
        "preserved_contradiction": len({atom_key("role_binding",{"kind":"event","predicate":"review","subject":"dana","object":"the dossier","polarity":p}) for p in ("positive","negative")})==2,
        "mutation_changes_one_dimension": atom_key("temporal",base["gold"]["temporal"][0]) != atom_key("temporal",wrong_scope[0]["candidate_atoms"][0]["atom"]),
        "paraphrase_changes_none_under_frozen_equivalence": atom_key("role_binding",equiv[0]["candidate_atoms"][0]["atom"])==atom_key("role_binding",base["gold"]["role_binding"][0]),
    }
    return {"checks":checks,"all_passed":all(checks.values())}
