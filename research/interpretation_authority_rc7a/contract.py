from __future__ import annotations

from typing import Any

ESTABLISHED = "established"
SEMANTIC_UNKNOWN = "semantic_unknown"
EXTRACTION_UNRESOLVED = "extraction_unresolved"
INSUFFICIENT_AUTHORITY = "insufficient_authority"
STATUSES = {ESTABLISHED, SEMANTIC_UNKNOWN, EXTRACTION_UNRESOLVED, INSUFFICIENT_AUTHORITY}
BLOCKING = {EXTRACTION_UNRESOLVED, INSUFFICIENT_AUTHORITY}

UNKNOWN_CAPABLE = {
    ("only_permission", "membership"),
    ("only_permission", "explicit_permission"),
}

REQUIRED_FIELDS = {
    "only_permission": ("entity", "population", "membership", "predicate", "only_population_may", "explicit_permission"),
    "role_binding": ("predicate", "subject", "object", "polarity"),
    "quantifier": ("population", "predicate", "quantifier", "polarity"),
}


def obs(status: str, value: Any = None, span: str | None = None, warrant: str | None = None) -> dict[str, Any]:
    return {"status": status, "value": value, "span": span, "warrant": warrant}


def established(value: Any, span: str = "source-span", warrant: str = "explicit_assertion") -> dict[str, Any]:
    return obs(ESTABLISHED, value, span, warrant)


def semantic_unknown(span: str = "source-span", warrant: str = "explicit_unknown") -> dict[str, Any]:
    return obs(SEMANTIC_UNKNOWN, "unknown", span, warrant)


def extraction_unresolved() -> dict[str, Any]:
    return obs(EXTRACTION_UNRESOLVED)


def insufficient_authority() -> dict[str, Any]:
    return obs(INSUFFICIENT_AUTHORITY)


def validate_observation(family: str, field: str, observation: dict[str, Any]) -> None:
    status = observation.get("status")
    if status not in STATUSES:
        raise ValueError(f"invalid status {status!r}")
    if status in {ESTABLISHED, SEMANTIC_UNKNOWN}:
        if observation.get("value") is None:
            raise ValueError(f"{field}: semantic observation requires value")
        if not observation.get("span") or not observation.get("warrant"):
            raise ValueError(f"{field}: semantic observation requires span and warrant")
    else:
        if observation.get("value") is not None:
            raise ValueError(f"{field}: blocking state must not carry semantic value")
    if status == SEMANTIC_UNKNOWN and (family, field) not in UNKNOWN_CAPABLE:
        raise ValueError(f"{field}: semantic_unknown unsupported for {family}")


def project_case(family: str, fields: dict[str, dict[str, Any]], query: dict[str, Any]) -> dict[str, Any]:
    values = {k: fields[k]["value"] for k in REQUIRED_FIELDS[family]}
    if family == "only_permission":
        authority = {
            "entity": values["entity"],
            "population": values["population"],
            "membership": values["membership"],
            "predicate": values["predicate"],
            "only_population_may": values["only_population_may"],
            "explicit_permission": values["explicit_permission"],
        }
    elif family == "role_binding":
        authority = {
            "event": {
                "predicate": values["predicate"],
                "roles": {"subject": values["subject"], "object": values["object"]},
                "polarity": values["polarity"],
            }
        }
    elif family == "quantifier":
        authority = {
            "population": values["population"],
            "members": ["e0", "e1"],
            "predicate": values["predicate"],
            "quantifier": values["quantifier"],
            "polarity": values["polarity"],
        }
    else:
        raise ValueError(family)
    return {"dimension": family, "authority": authority, "query": query}
