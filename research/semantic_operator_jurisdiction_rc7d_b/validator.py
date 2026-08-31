"""Independent deterministic warrant validator for RC7D-B.

The validator consumes frozen specialist proposals. It does not call the proposal
operators and does not inspect gold labels. Rejected/unresolved proposals remain
preserved; only AUTHORIZED atoms may flow to composition.
"""
from __future__ import annotations

import hashlib
import re

VERSION = "rc7d-b-validator-v1"

_SCOPE_WORDS = re.compile(
    r"\b(?:except|excluding|other than|save for|apart from|bar|aside from|before|after|prior to|following|until|as of|during|probably|likely|unlikely|chance|probability)\b",
    re.I,
)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip(" .,:;\t\n").lower())


def _raw_ok(raw: str, proposal: dict) -> bool:
    if proposal.get("raw_source") != raw:
        return False
    if proposal.get("raw_source_sha256") != hashlib.sha256(raw.encode()).hexdigest():
        return False
    for span in proposal.get("spans", []):
        a, b = span.get("start"), span.get("end")
        if not isinstance(a, int) or not isinstance(b, int) or not (0 <= a < b <= len(raw)):
            return False
        if raw[a:b] != span.get("text"):
            return False
    return True


def _no_scope_leak(*values: str) -> bool:
    return not any(_SCOPE_WORDS.search(v or "") for v in values)


def _result(atom: dict, status: str, reason: str) -> dict:
    return {
        "validator_version": VERSION,
        "atom": atom,
        "status": status,
        "reason": reason,
    }


def _validate_permission(raw: str, atom: dict) -> tuple[str, str]:
    kind = atom.get("kind")
    if kind == "necessary_permission_condition":
        pop = atom.get("population", "")
        pred = atom.get("predicate", "")
        if not pop or not pred or not _no_scope_leak(pop, pred):
            return "REJECTED", "modifier_leak_or_missing_field"
        p1 = re.compile(
            rf"\bonly\s+{re.escape(pop)}\s+may\s+{re.escape(pred)}(?=\s*(?:[.;]|$|except\b|excluding\b|other than\b|save for\b|bar\b|aside from\b))",
            re.I,
        )
        p2 = re.compile(
            rf"\bpermission\s+to\s+{re.escape(pred)}\s+(?:is\s+)?(?:restricted|limited)\s+to\s+{re.escape(pop)}(?=\s*(?:[.;,]|$))",
            re.I,
        )
        if p1.search(raw) or p2.search(raw):
            return "AUTHORIZED", "exact_necessary_permission_warrant"
        return "REJECTED", "exact_necessary_permission_warrant_not_found"

    if kind == "explicit_permission":
        ent = atom.get("entity", "")
        pred = atom.get("predicate", "")
        val = atom.get("value")
        if not ent or not pred or not _no_scope_leak(pred):
            return "REJECTED", "modifier_leak_or_missing_field"
        if val == "unknown":
            pat = re.compile(
                rf"\b(?:whether\s+)?{re.escape(ent)}\s+(?:is\s+)?(?:permitted|authorized|allowed)\s+to\s+{re.escape(pred)}\s+is\s+unknown\b",
                re.I,
            )
            return ("AUTHORIZED", "explicit_unknown_warrant") if pat.search(raw) else ("REJECTED", "explicit_unknown_warrant_not_found")
        neg = r"not\s+" if val == "not_permitted" else r""
        if val not in {"permitted", "not_permitted"}:
            return "REJECTED", "unsupported_permission_value"
        pat = re.compile(
            rf"\b{re.escape(ent)}\s+(?:is|was)\s+{neg}(?:authorized|permitted|allowed)\s+to\s+{re.escape(pred)}(?=\s*(?:[.;]|$|before\b|after\b|prior to\b|following\b|until\b|as of\b))",
            re.I,
        )
        return ("AUTHORIZED", "exact_explicit_permission_warrant") if pat.search(raw) else ("REJECTED", "exact_explicit_permission_warrant_not_found")

    if kind == "membership":
        ent = atom.get("entity", "")
        pop = atom.get("population", "")
        val = atom.get("value")
        if not ent or not pop or not _no_scope_leak(pop):
            return "REJECTED", "modifier_leak_or_missing_field"
        if val == "unknown":
            pat = re.compile(
                rf"\b(?:it\s+is\s+unknown\s+whether|whether)\s+{re.escape(ent)}\s+(?:is\s+)?(?:a\s+)?(?:member\s+of|belongs\s+to)\s+{re.escape(pop)}",
                re.I,
            )
            return ("AUTHORIZED", "explicit_unknown_membership") if pat.search(raw) else ("REJECTED", "explicit_unknown_membership_not_found")
        if val not in {"member", "non_member"}:
            return "REJECTED", "unsupported_membership_value"
        neg = r"not\s+" if val == "non_member" else r""
        pat = re.compile(
            rf"\b{re.escape(ent)}\s+(?:is\s+)?{neg}(?:a\s+)?(?:member\s+of|belongs\s+to)\s+{re.escape(pop)}(?=\s*(?:[.;]|$|before\b|after\b|prior to\b|following\b|until\b|as of\b))",
            re.I,
        )
        return ("AUTHORIZED", "exact_membership_warrant") if pat.search(raw) else ("REJECTED", "exact_membership_warrant_not_found")

    return "UNRESOLVED", "unknown_permission_atom_kind"


def _validate_role(raw: str, atom: dict) -> tuple[str, str]:
    if atom.get("kind") != "event":
        return "UNRESOLVED", "unknown_role_atom"
    pred = atom.get("predicate")
    subj = atom.get("subject", "")
    obj = atom.get("object", "")
    pol = atom.get("polarity")
    verb = {"review": "reviewed", "inspect": "inspected", "approve": "approved", "sign": "signed", "release": "released"}.get(pred)
    if not verb or not subj or not obj or pol not in {"positive", "negative"} or not _no_scope_leak(subj, obj):
        return "REJECTED", "unsupported_or_leaky_role_atom"
    neg_active = r"did\s+not\s+" if pol == "negative" else r""
    neg_passive = r"not\s+" if pol == "negative" else r""
    active = re.compile(rf"\b{re.escape(subj)}\s+{neg_active}{verb}\s+{re.escape(obj)}(?=\s*[.;]|$)", re.I)
    passive = re.compile(rf"\b{re.escape(obj)}\s+(?:was|were)\s+{neg_passive}{verb}\s+by\s+{re.escape(subj)}(?=\s*[.;]|$)", re.I)
    if active.search(raw) or passive.search(raw):
        return "AUTHORIZED", "exact_role_binding_warrant"
    return "REJECTED", "exact_role_binding_warrant_not_found"


def _validate_quantifier(raw: str, atom: dict) -> tuple[str, str]:
    if atom.get("kind") != "quantifier":
        return "UNRESOLVED", "unknown_quantifier_atom"
    q = atom.get("quantifier")
    pop = atom.get("population", "")
    pred = atom.get("predicate", "")
    if not pop or not pred or not _no_scope_leak(pop, pred):
        return "REJECTED", "modifier_leak_or_missing_field"
    if " " not in pred:
        return "REJECTED", "predicate_shape"
    lemma, obj = pred.split(" ", 1)
    verb = {"review": "reviewed", "inspect": "inspected", "approve": "approved", "sign": "signed", "release": "released"}.get(lemma)
    qforms = {
        "every": ["every", "all", "each"],
        "none": ["no", "none", "not one"],
        "some": ["some", "at least one"],
        "not_every": ["not every", "not all"],
    }.get(q)
    if not verb or not qforms:
        return "REJECTED", "unsupported_quantifier_shape"
    for qf in qforms:
        pat = re.compile(
            rf"\b{re.escape(qf)}\s+{re.escape(pop)}\s+{verb}\s+{re.escape(obj)}(?=\s*(?:[.;]|$|except\b|excluding\b|other than\b|save for\b|bar\b|aside from\b|before\b|after\b))",
            re.I,
        )
        if pat.search(raw):
            return "AUTHORIZED", "exact_quantifier_warrant"
    return "REJECTED", "exact_quantifier_warrant_not_found"


def _validate_exception(raw: str, atom: dict) -> tuple[str, str]:
    if atom.get("kind") != "exception" or not atom.get("excluded"):
        return "UNRESOLVED", "unknown_exception_atom"
    x = atom["excluded"]
    forms = [
        rf"\bexcept\s+{re.escape(x)}\b",
        rf"\bexcluding\s+{re.escape(x)}\b",
        rf"\bother\s+than\s+{re.escape(x)}\b",
        rf"\bsave\s+for\s+{re.escape(x)}\b",
        rf"\bwith\s+the\s+exception\s+of\s+{re.escape(x)}\b",
        rf"\bapart\s+from\s+{re.escape(x)}\b",
    ]
    if any(re.search(p, raw, re.I) for p in forms):
        return "AUTHORIZED", "exact_exception_warrant"
    return "REJECTED", "exact_exception_warrant_not_found"


def _validate_temporal(raw: str, atom: dict) -> tuple[str, str]:
    if atom.get("kind") != "temporal_scope":
        return "UNRESOLVED", "unknown_temporal_atom"
    rel = atom.get("relation")
    ref = atom.get("reference", "")
    prefixes = {
        "before": ["before", "prior to"],
        "after": ["after", "following"],
        "until": ["until"],
        "as_of": ["as of"],
        "during": ["during"],
    }.get(rel, [])
    if ref and any(re.search(rf"\b{re.escape(p)}\s+{re.escape(ref)}\b", raw, re.I) for p in prefixes):
        return "AUTHORIZED", "exact_temporal_warrant"
    return "REJECTED", "exact_temporal_warrant_not_found"


def _validate_subclass(raw: str, atom: dict) -> tuple[str, str]:
    if atom.get("kind") != "subclass":
        return "UNRESOLVED", "unknown_subclass_atom"
    child, parent = atom.get("child", ""), atom.get("parent", "")
    if not child or not parent or not _no_scope_leak(child, parent):
        return "REJECTED", "subclass_shape"
    forms = [
        rf"\b{re.escape(child)}\s+(?:are|is)\s+(?:a\s+)?(?:subclass|subset|type|kind)\s+of\s+{re.escape(parent)}\b",
        rf"\b{re.escape(child)}\s+(?:sit|sits)\s+within\s+{re.escape(parent)}\b",
        rf"\b{re.escape(child)}\s+(?:fall|falls)\s+under\s+{re.escape(parent)}\b",
    ]
    if any(re.search(p, raw, re.I) for p in forms):
        return "AUTHORIZED", "exact_subclass_warrant"
    return "REJECTED", "exact_subclass_warrant_not_found"


def _validate_probability(raw: str, atom: dict) -> tuple[str, str]:
    if atom.get("kind") != "epistemic_probability":
        return "UNRESOLVED", "unknown_probability_atom"
    val = atom.get("value")
    forms = {
        "probable": [r"\bprobably\b"],
        "likely": [r"\blikely\b"],
        "unlikely": [r"\bunlikely\b"],
        "possible": [r"\bthere\s+is\s+(?:a\s+)?chance\b"],
        "probabilistic": [r"\bprobability\b"],
    }.get(val, [])
    if any(re.search(p, raw, re.I) for p in forms):
        return "AUTHORIZED", "exact_probability_warrant"
    return "REJECTED", "exact_probability_warrant_not_found"


def _validate_quantitative(raw: str, atom: dict) -> tuple[str, str]:
    if atom.get("kind") != "quantitative_scope":
        return "UNRESOLVED", "unknown_quantitative_atom"
    kind = atom.get("quantitative_kind")
    surface = atom.get("surface", "")
    if not surface or surface.lower() not in raw.lower():
        return "REJECTED", "quantitative_surface_not_found"
    checks = {
        "percentage": r"(?:\b\d{1,3}\s*%|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)\s+percent\b)",
        "exact_count": r"\bexactly\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b",
        "minimum_count": r"\bat\s+least\s+(?:\d+|two|three|four|five|six|seven|eight|nine|ten)\b",
        "majority": r"\b(?:a\s+)?majority\s+of\b",
        "most": r"\bmost\s+",
        "many": r"\bmany\s+",
        "few": r"\bfew\s+",
    }
    pat = checks.get(kind)
    if pat and re.search(pat, raw, re.I):
        return "AUTHORIZED", "exact_quantitative_warrant"
    return "REJECTED", "quantitative_kind_not_verified"


_VALIDATORS = {
    "permission": _validate_permission,
    "role_binding": _validate_role,
    "quantifier": _validate_quantifier,
    "exception": _validate_exception,
    "temporal": _validate_temporal,
    "subclass": _validate_subclass,
    "probability": _validate_probability,
    "quantitative": _validate_quantitative,
}


def validate_receipt(raw: str, proposal: dict) -> dict:
    dimension = proposal.get("dimension")
    record = {
        "operator_id": proposal.get("operator_id"),
        "dimension": dimension,
        "proposal_status": proposal.get("status"),
        "raw_source": raw,
        "raw_source_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "proposal": proposal,
        "atom_validations": [],
    }
    if not _raw_ok(raw, proposal):
        record["receipt_status"] = "REJECTED"
        record["reason"] = "raw_source_or_span_integrity_failure"
        return record
    if proposal.get("status") != "CLAIMED":
        record["receipt_status"] = proposal.get("status", "UNRESOLVED")
        record["reason"] = "no_claim_to_validate"
        return record
    fn = _VALIDATORS.get(dimension)
    if not fn:
        record["receipt_status"] = "UNRESOLVED"
        record["reason"] = "no_validator_for_dimension"
        return record
    for atom in proposal.get("atoms", []):
        status, reason = fn(raw, atom)
        record["atom_validations"].append(_result(atom, status, reason))
    statuses = {r["status"] for r in record["atom_validations"]}
    if statuses == {"AUTHORIZED"} and record["atom_validations"]:
        record["receipt_status"] = "AUTHORIZED"
    elif "REJECTED" in statuses:
        record["receipt_status"] = "REJECTED"
    else:
        record["receipt_status"] = "UNRESOLVED"
    return record


def validate_architecture_output(output: dict) -> dict:
    raw = output["raw_source"]
    validations = [validate_receipt(raw, p) for p in output.get("receipts", [])]
    authorized: dict[str, list[dict]] = {}
    rejected: list[dict] = []
    unresolved: list[dict] = []
    for rec in validations:
        for av in rec.get("atom_validations", []):
            if av["status"] == "AUTHORIZED":
                authorized.setdefault(rec["dimension"], []).append(av["atom"])
            elif av["status"] == "REJECTED":
                rejected.append({"dimension": rec["dimension"], **av})
            else:
                unresolved.append({"dimension": rec["dimension"], **av})
    return {
        "raw_source": raw,
        "raw_source_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "original_output": output,
        "proposal_receipts": output.get("receipts", []),
        "validation_receipts": validations,
        "authorized_atoms": authorized,
        "authorized_dimensions": sorted(authorized),
        "rejected_proposals": rejected,
        "unresolved_proposals": unresolved,
    }
