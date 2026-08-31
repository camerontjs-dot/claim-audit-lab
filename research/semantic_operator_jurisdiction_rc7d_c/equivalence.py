"""Frozen semantic-equivalence rules for RC7D-C scoring only."""
from __future__ import annotations

import re
import unicodedata

VERSION = "rc7d-c-equivalence-v1"


def norm_text(value: str) -> str:
    s = unicodedata.normalize("NFKC", str(value)).lower().strip()
    s = re.sub(r"[.?!,:;]+$", "", s).strip()
    s = re.sub(r"\s+", " ", s)
    return s


def norm_np(value: str) -> str:
    s = norm_text(value)
    return re.sub(r"^(?:a|an|the)\s+", "", s, count=1)


def norm_predicate(value: str) -> str:
    s = norm_text(value)
    parts = s.split(" ", 1)
    if len(parts) == 1:
        return s
    lemma, complement = parts
    return lemma + " " + norm_np(complement)


def canonical_atom(atom: dict) -> dict:
    kind = atom.get("kind")
    out = {"kind": kind}
    if kind == "quantifier":
        out.update({
            "quantifier": atom.get("quantifier"),
            "population": norm_np(atom.get("population", "")),
            "predicate": norm_predicate(atom.get("predicate", "")),
        })
    elif kind == "exception":
        out["excluded"] = norm_np(atom.get("excluded", ""))
    elif kind == "temporal_scope":
        out.update({"relation": atom.get("relation"), "reference": norm_np(atom.get("reference", ""))})
    elif kind == "subclass":
        out.update({"child": norm_np(atom.get("child", "")), "parent": norm_np(atom.get("parent", ""))})
    elif kind == "necessary_permission_condition":
        out.update({"population": norm_np(atom.get("population", "")), "predicate": norm_predicate(atom.get("predicate", ""))})
    elif kind == "explicit_permission":
        out.update({"entity": norm_np(atom.get("entity", "")), "predicate": norm_predicate(atom.get("predicate", "")), "value": atom.get("value")})
    elif kind == "membership":
        out.update({"entity": norm_np(atom.get("entity", "")), "population": norm_np(atom.get("population", "")), "value": atom.get("value")})
    elif kind == "event":
        out.update({
            "predicate": norm_text(atom.get("predicate", "")),
            "subject": norm_np(atom.get("subject", "")),
            "object": norm_np(atom.get("object", "")),
            "polarity": atom.get("polarity"),
        })
    elif kind == "epistemic_probability":
        out["value"] = atom.get("value")
    elif kind == "quantitative_scope":
        out["quantitative_kind"] = atom.get("quantitative_kind")
        if "value" in atom:
            out["value"] = norm_text(atom.get("value", ""))
        # surface is provenance and is intentionally not semantic identity.
    else:
        # Unknown atom kinds receive no relaxed equivalence.
        for k, v in sorted(atom.items()):
            if k != "kind":
                out[k] = v
    return out
