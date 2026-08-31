"""RC7D-C deterministic authority validator v2.

Builds on the frozen RC7D-B validator while adding generic guards for the
failure classes observed there. The RC7D-C cohort does not yet exist at this
freeze.
"""
from __future__ import annotations

import re
from research.semantic_operator_jurisdiction_rc7d_b import validator as v1

VERSION = "rc7d-c-validator-v2"

_ADVERB_OR_SCOPE = re.compile(
    r"\b(?:conceivably|possibly|perhaps|apparently|reportedly|allegedly|presumably|probably|likely|unlikely|except|excluding|other than|save for|apart from|bar|aside from|before|after|prior to|following|until|during)\b|\b[a-z]+ly\b",
    re.I,
)


def _slot_leak(atom: dict) -> bool:
    for key in ("population", "predicate", "child", "parent", "subject", "object"):
        value = atom.get(key)
        if isinstance(value, str) and _ADVERB_OR_SCOPE.search(value):
            return True
    return False


def _probability_context_ok(raw: str, atom: dict) -> bool:
    value = atom.get("value")
    if value == "probable":
        return bool(re.search(r"\bprobably\b", raw, re.I))
    if value == "likely":
        return bool(re.search(r"\blikely\b", raw, re.I)) and not bool(re.search(r"\blikely\s+(?:label|field|column|name|token|folder|file|notebook)\b", raw, re.I))
    if value == "unlikely":
        return bool(re.search(r"\bunlikely\b", raw, re.I))
    if value == "possible":
        return bool(re.search(r"\b(?:there\s+is\s+(?:a\s+|a\s+reasonable\s+)?chance\b|possibly\b|conceivably\b|perhaps\b)", raw, re.I))
    if value == "probabilistic":
        return bool(re.search(r"\bprobability\s+(?:that|of)\b", raw, re.I))
    return False


def validate_receipt(raw: str, proposal: dict) -> dict:
    rec = v1.validate_receipt(raw, proposal)
    if proposal.get("status") != "CLAIMED":
        rec["validator_v2"] = VERSION
        return rec

    revised = []
    for av in rec.get("atom_validations", []):
        status, reason = av["status"], av["reason"]
        atom = av["atom"]
        if status == "AUTHORIZED":
            if _slot_leak(atom):
                status, reason = "REJECTED", "v2_modifier_or_scope_leak"
            elif atom.get("kind") == "epistemic_probability" and not _probability_context_ok(raw, atom):
                status, reason = "REJECTED", "v2_non_epistemic_probability_context"
        revised.append({**av, "status": status, "reason": reason})
    rec["atom_validations"] = revised
    statuses = {x["status"] for x in revised}
    if statuses == {"AUTHORIZED"} and revised:
        rec["receipt_status"] = "AUTHORIZED"
    elif "REJECTED" in statuses:
        rec["receipt_status"] = "REJECTED"
    else:
        rec["receipt_status"] = "UNRESOLVED"
    rec["validator_v2"] = VERSION
    return rec


def validate_architecture_output(output: dict) -> dict:
    raw = output["raw_source"]
    validations = [validate_receipt(raw, p) for p in output.get("receipts", [])]
    authorized: dict[str, list[dict]] = {}
    rejected, unresolved = [], []
    for rec in validations:
        for av in rec.get("atom_validations", []):
            row = {"dimension": rec["dimension"], **av}
            if av["status"] == "AUTHORIZED":
                authorized.setdefault(rec["dimension"], []).append(av["atom"])
            elif av["status"] == "REJECTED":
                rejected.append(row)
            else:
                unresolved.append(row)
    return {
        "raw_source": raw,
        "raw_source_sha256": output["raw_source_sha256"],
        "original_output": output,
        "proposal_receipts": output.get("receipts", []),
        "validation_receipts": validations,
        "authorized_atoms": authorized,
        "authorized_dimensions": sorted(authorized),
        "rejected_proposals": rejected,
        "unresolved_proposals": unresolved,
    }
