"""Gold-blind semantic measurement comparison taxonomy.

Research-only. This module compares preserved measurement proposals. It does
not inspect evaluator gold and it does not select a winning interpretation.
"""
from __future__ import annotations

import json
import re
from typing import Iterable

from research.semantic_operator_jurisdiction_rc7d_c.equivalence import canonical_atom

VERSION = "semantic-measurement-comparison-rc1-v1"

_SCOPE_RE = re.compile(
    r"\b(?:except|excluding|excluded|exception|apart from|aside from|save for|bar|but not|left out|kept out|"
    r"before|after|prior to|following|until|during|as of|"
    r"probably|probable|likely|unlikely|possibly|possible|perhaps|conceivably|apparently|reportedly|allegedly|"
    r"may well|might|seems? doubtful|"
    r"if|unless|otherwise|provided that|only if|not)\b",
    re.I,
)


def _raw_key(atom: dict) -> str:
    return json.dumps(atom, sort_keys=True, separators=(",", ":"))


def _canon_key(atom: dict) -> str:
    return json.dumps(canonical_atom(atom), sort_keys=True, separators=(",", ":"))


def _claimed(receipt: dict) -> bool:
    return receipt.get("status") == "CLAIMED" and bool(receipt.get("atoms"))


def _values(atom: dict, fields: Iterable[str]) -> list[str]:
    out = []
    for field in fields:
        value = atom.get(field)
        if isinstance(value, str):
            out.append(value)
    return out


def _has_scope(value: str) -> bool:
    return bool(_SCOPE_RE.search(value or ""))


def _scope_difference(left: dict, right: dict) -> bool:
    fields = ("population", "predicate", "subject", "object", "entity", "child", "parent", "reference")
    lv = _values(left, fields)
    rv = _values(right, fields)
    if any(_has_scope(x) for x in lv + rv):
        # Scope-bearing material is present and the atoms are already known to differ.
        return True
    return False


def _kind(atom: dict) -> str | None:
    return atom.get("kind")


def _pair_relation(left: dict, right: dict) -> tuple[str, list[str]]:
    """Classify two non-equivalent atoms without gold."""
    lk, rk = _kind(left), _kind(right)
    facets: list[str] = []
    if lk != rk:
        return "INCOMMENSURABLE", ["different_atom_kind"]

    if _scope_difference(left, right):
        facets.append("scope_bearing_slot_difference")
        return "SCOPE_ATTACHMENT_DISAGREEMENT", facets

    if lk == "event":
        if left.get("polarity") != right.get("polarity"):
            return "POLARITY_DISAGREEMENT", ["event_polarity"]
        if left.get("predicate") != right.get("predicate"):
            return "ROLE_BINDING_DISAGREEMENT", ["predicate_identity"]
        if left.get("subject") != right.get("subject") or left.get("object") != right.get("object"):
            return "ROLE_BINDING_DISAGREEMENT", ["participant_binding"]

    if lk == "quantifier":
        if left.get("quantifier") != right.get("quantifier"):
            return "OPERATOR_VALUE_DISAGREEMENT", ["quantifier_value"]
        if left.get("population") != right.get("population") or left.get("predicate") != right.get("predicate"):
            return "SLOT_BOUNDARY_DISAGREEMENT", ["quantifier_argument_boundary"]

    if lk in {"explicit_permission", "membership"}:
        if left.get("value") != right.get("value"):
            return "OPERATOR_VALUE_DISAGREEMENT", [f"{lk}_value"]
        comparable = ("entity", "predicate") if lk == "explicit_permission" else ("entity", "population")
        if any(left.get(f) != right.get(f) for f in comparable):
            return "SLOT_BOUNDARY_DISAGREEMENT", [f"{lk}_argument_boundary"]

    if lk == "necessary_permission_condition":
        if left.get("population") != right.get("population") or left.get("predicate") != right.get("predicate"):
            return "SLOT_BOUNDARY_DISAGREEMENT", ["permission_condition_boundary"]

    if lk == "epistemic_probability":
        if left.get("value") != right.get("value"):
            return "OPERATOR_VALUE_DISAGREEMENT", ["epistemic_value"]

    if lk == "temporal_scope":
        if left.get("relation") != right.get("relation"):
            return "OPERATOR_VALUE_DISAGREEMENT", ["temporal_relation"]
        if left.get("reference") != right.get("reference"):
            return "SLOT_BOUNDARY_DISAGREEMENT", ["temporal_reference"]

    if lk == "quantitative_scope":
        if left.get("quantitative_kind") != right.get("quantitative_kind") or left.get("value") != right.get("value"):
            return "OPERATOR_VALUE_DISAGREEMENT", ["quantitative_value_or_kind"]

    if lk == "exception" and left.get("excluded") != right.get("excluded"):
        return "SLOT_BOUNDARY_DISAGREEMENT", ["exception_target"]

    if lk == "subclass" and (left.get("child") != right.get("child") or left.get("parent") != right.get("parent")):
        return "SLOT_BOUNDARY_DISAGREEMENT", ["subclass_binding"]

    return "SLOT_BOUNDARY_DISAGREEMENT", ["unclassified_same_kind_difference"]


def compare_receipts(left: dict, right: dict) -> dict | None:
    """Compare two receipts for the same intended semantic dimension.

    Returns None when neither receipt makes an active claim. Classification is
    gold-blind and never chooses a winner.
    """
    l_claim, r_claim = _claimed(left), _claimed(right)
    if not l_claim and not r_claim:
        return None
    if l_claim != r_claim:
        return {
            "taxonomy_version": VERSION,
            "relation": "JURISDICTION_DISAGREEMENT",
            "facets": ["claimed_vs_inactive"],
            "left_status": left.get("status"),
            "right_status": right.get("status"),
            "left_atoms": left.get("atoms", []),
            "right_atoms": right.get("atoms", []),
            "winner": None,
        }

    l_atoms = left.get("atoms", [])
    r_atoms = right.get("atoms", [])
    l_raw = {_raw_key(a) for a in l_atoms}
    r_raw = {_raw_key(a) for a in r_atoms}
    l_can = {_canon_key(a) for a in l_atoms}
    r_can = {_canon_key(a) for a in r_atoms}

    if l_raw == r_raw:
        relation, facets = "EXACT_AGREEMENT", ["same_native_atom_set"]
    elif l_can == r_can:
        relation, facets = "SEMANTIC_EQUIVALENCE", ["same_canonical_atom_set"]
    elif l_can & r_can:
        relation, facets = "GRANULARITY_MISMATCH", ["partial_canonical_overlap"]
    elif len(l_atoms) == 1 and len(r_atoms) == 1:
        relation, facets = _pair_relation(l_atoms[0], r_atoms[0])
    else:
        # Multi-atom sets with no exact overlap. Inspect all pairings. A single
        # high-risk scope/polarity/value disagreement dominates the comparison
        # state; otherwise retain granularity as the safest description.
        pair_relations = [_pair_relation(a, b)[0] for a in l_atoms for b in r_atoms]
        priority = (
            "POLARITY_DISAGREEMENT",
            "OPERATOR_VALUE_DISAGREEMENT",
            "SCOPE_ATTACHMENT_DISAGREEMENT",
            "ROLE_BINDING_DISAGREEMENT",
            "SLOT_BOUNDARY_DISAGREEMENT",
            "INCOMMENSURABLE",
        )
        relation = next((p for p in priority if p in pair_relations), "GRANULARITY_MISMATCH")
        facets = ["multi_atom_set_difference"]

    return {
        "taxonomy_version": VERSION,
        "relation": relation,
        "facets": facets,
        "left_status": left.get("status"),
        "right_status": right.get("status"),
        "left_atoms": l_atoms,
        "right_atoms": r_atoms,
        "winner": None,
    }
