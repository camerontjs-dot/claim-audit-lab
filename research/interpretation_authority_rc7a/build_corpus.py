from __future__ import annotations

import copy
import hashlib
import json
from itertools import product
from typing import Any

from .contract import established, extraction_unresolved, insufficient_authority, semantic_unknown


def _stable_sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _base_only(query_kind: str = "permission") -> dict[str, Any]:
    return {
        "family": "only_permission",
        "fields": {
            "entity": established("e0", "Mira", "entity_name"),
            "population": established("inspector", "licensed inspectors", "population_name"),
            "membership": established("member", "Mira is a licensed inspector", "explicit_membership"),
            "predicate": established("release", "release batch A", "predicate_phrase"),
            "only_population_may": established(True, "Only licensed inspectors may release batch A", "only_necessary_condition"),
            "explicit_permission": established("permitted", "Mira is authorized to release batch A", "explicit_permission_grant"),
        },
        "query": {"kind": query_kind, "entity": "e0", "population": "inspector", "predicate": "release"},
    }


def _base_role() -> dict[str, Any]:
    return {
        "family": "role_binding",
        "fields": {
            "predicate": established("review", "reviewed", "binary_event_predicate"),
            "subject": established("e0", "Dana", "semantic_subject"),
            "object": established("e1", "Lee", "semantic_object"),
            "polarity": established("positive", "reviewed", "positive_assertion"),
        },
        "query": {"kind": "event", "predicate": "review", "roles": {"subject": "e0", "object": "e1"}, "polarity": "positive"},
    }


def _base_quantifier() -> dict[str, Any]:
    return {
        "family": "quantifier",
        "fields": {
            "population": established("inspector", "inspectors", "population_name"),
            "predicate": established("sign", "sign the log", "predicate_phrase"),
            "quantifier": established("every", "Every", "universal_quantifier"),
            "polarity": established("positive", "sign", "positive_assertion"),
        },
        "query": {"kind": "quantified", "population": "inspector", "predicate": "sign", "quantifier": "some", "polarity": "positive"},
    }


def build_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    idx = 0

    member_states = [
        ("member", established("member", "Mira is a licensed inspector", "explicit_membership")),
        ("non_member", established("non_member", "Mira is not a licensed inspector", "explicit_nonmembership")),
        ("semantic_unknown", semantic_unknown("It is unknown whether Mira is a licensed inspector", "explicit_unknown_membership")),
        ("extraction_unresolved", extraction_unresolved()),
        ("insufficient_authority", insufficient_authority()),
    ]
    perm_states = [
        ("permitted", established("permitted", "Mira is authorized to release batch A", "explicit_permission_grant")),
        ("not_permitted", established("not_permitted", "Mira is not authorized to release batch A", "explicit_permission_denial")),
        ("semantic_unknown", semantic_unknown("It is unknown whether Mira is authorized to release batch A", "explicit_unknown_permission")),
        ("extraction_unresolved", extraction_unresolved()),
        ("insufficient_authority", insufficient_authority()),
    ]
    for query_kind, (mname, mobs), (pname, pobs) in product(("permission", "membership"), member_states, perm_states):
        idx += 1
        r = _base_only(query_kind)
        r["fields"]["membership"] = copy.deepcopy(mobs)
        r["fields"]["explicit_permission"] = copy.deepcopy(pobs)
        cases.append({"case_id": f"OP-{idx:03d}", "tags": [mname, pname, query_kind], "receipt": r})

    role_bases = []
    for polarity in ("positive", "negative"):
        r = _base_role()
        r["fields"]["polarity"] = established(polarity, "did not review" if polarity == "negative" else "reviewed", "polarity_assertion")
        role_bases.append(r)
    for bidx, base in enumerate(role_bases, 1):
        idx = 0
        cases.append({"case_id": f"RB-{bidx}-BASE", "tags": ["established"], "receipt": copy.deepcopy(base)})
        for field in ("predicate", "subject", "object", "polarity"):
            for reason, obs in (("extraction_unresolved", extraction_unresolved()), ("insufficient_authority", insufficient_authority())):
                idx += 1
                r = copy.deepcopy(base)
                r["fields"][field] = obs
                cases.append({"case_id": f"RB-{bidx}-{idx:02d}", "tags": [field, reason], "receipt": r})

    for qval in ("every", "none", "some", "not_every"):
        base = _base_quantifier()
        base["fields"]["quantifier"] = established(qval, qval.replace("_", " "), "quantifier_assertion")
        base["query"]["quantifier"] = "some"
        cases.append({"case_id": f"QU-{qval}-BASE", "tags": ["established", qval], "receipt": copy.deepcopy(base)})
        for field in ("population", "predicate", "quantifier", "polarity"):
            for reason, obs in (("extraction_unresolved", extraction_unresolved()), ("insufficient_authority", insufficient_authority())):
                r = copy.deepcopy(base)
                r["fields"][field] = obs
                cases.append({"case_id": f"QU-{qval}-{field}-{reason}", "tags": [field, reason, qval], "receipt": r})

    return cases


def build_invalid_cases() -> list[dict[str, Any]]:
    invalid = []
    r = _base_role()
    r["fields"]["subject"] = semantic_unknown("unknown subject", "explicit_unknown")
    invalid.append({"case_id": "INV-ROLE-SEMUNK", "receipt": r, "expected_error": "semantic_unknown"})

    r = _base_quantifier()
    r["fields"]["quantifier"] = semantic_unknown("unknown quantifier", "explicit_unknown")
    invalid.append({"case_id": "INV-QUANT-SEMUNK", "receipt": r, "expected_error": "semantic_unknown"})

    r = _base_only()
    r["fields"]["membership"] = {"status": "established", "value": "member", "span": None, "warrant": "explicit_membership"}
    invalid.append({"case_id": "INV-MISSING-SPAN", "receipt": r, "expected_error": "span"})

    r = _base_only()
    r["fields"]["explicit_permission"] = {"status": "extraction_unresolved", "value": "unknown", "span": None, "warrant": None}
    invalid.append({"case_id": "INV-BLOCKING-VALUE", "receipt": r, "expected_error": "value"})
    return invalid


def build_mutations() -> list[dict[str, Any]]:
    out = []
    for state_name, obs in (
        ("semantic_unknown", semantic_unknown("explicitly unknown", "explicit_unknown_membership")),
        ("extraction_unresolved", extraction_unresolved()),
        ("insufficient_authority", insufficient_authority()),
    ):
        before = _base_only("permission")
        after = copy.deepcopy(before)
        after["fields"]["membership"] = obs
        out.append({"name": f"only_membership_to_{state_name}", "before": before, "after": after, "field": "membership", "target_status": state_name})

    for family, base, fields in (
        ("role_binding", _base_role(), ("predicate", "subject", "object", "polarity")),
        ("quantifier", _base_quantifier(), ("population", "predicate", "quantifier", "polarity")),
    ):
        for field in fields:
            for state_name, obs in (("extraction_unresolved", extraction_unresolved()), ("insufficient_authority", insufficient_authority())):
                after = copy.deepcopy(base)
                after["fields"][field] = obs
                out.append({"name": f"{family}_{field}_to_{state_name}", "before": copy.deepcopy(base), "after": after, "field": field, "target_status": state_name})
    return out


def build() -> dict[str, Any]:
    payload = {"cases": build_cases(), "invalid_cases": build_invalid_cases(), "mutations": build_mutations()}
    payload["sha256"] = _stable_sha(payload)
    return payload


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
