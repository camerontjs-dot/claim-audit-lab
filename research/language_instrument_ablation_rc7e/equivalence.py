"""Frozen RC7E scoring equivalence. Comparison-only; never rewrites source."""
from __future__ import annotations

import json
import re
import unicodedata
from typing import Any

VERB_LEMMA = {
    "reviewed": "review", "reviewing": "review", "reviews": "review", "review": "review",
    "inspected": "inspect", "inspecting": "inspect", "inspects": "inspect", "inspect": "inspect",
    "approved": "approve", "approving": "approve", "approves": "approve", "approve": "approve",
    "signed": "sign", "signing": "sign", "signs": "sign", "sign": "sign",
    "released": "release", "releasing": "release", "releases": "release", "release": "release",
}
QUANT = {"all": "every", "every": "every", "each": "every", "no": "none", "none": "none", "some": "some", "not all": "not_every", "not every": "not_every", "not_every": "not_every"}
TEXT_FIELDS = {"population", "predicate", "excluded", "entity", "subject", "object", "child", "parent", "reference", "surface", "speaker", "quote", "antecedent", "anaphor", "marker", "condition", "consequent", "left", "right", "unit"}


def norm_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"\s+", " ", value.strip().lower())
    return value.rstrip(" .,:;")


def canonical_atom(atom: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in atom.items():
        if isinstance(value, str):
            v = norm_text(value)
            if key == "predicate":
                parts = v.split(" ", 1)
                if parts:
                    parts[0] = VERB_LEMMA.get(parts[0], parts[0])
                    v = " ".join(parts)
            elif key == "quantifier":
                v = QUANT.get(v, v)
            out[key] = v
        elif isinstance(value, list):
            out[key] = sorted(canonical_value(x) for x in value)
        else:
            out[key] = canonical_value(value)
    return out


def canonical_value(value: Any) -> Any:
    if isinstance(value, dict):
        return canonical_atom(value)
    if isinstance(value, str):
        return norm_text(value)
    if isinstance(value, list):
        return [canonical_value(v) for v in value]
    return value


def atom_key(dimension: str, atom: dict[str, Any]) -> str:
    payload = {"dimension": dimension, "atom": canonical_atom(atom)}
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
