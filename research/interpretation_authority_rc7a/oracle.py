from __future__ import annotations

from typing import Any

from .contract import BLOCKING, REQUIRED_FIELDS, project_case, validate_observation


def evaluate(receipt: dict[str, Any]) -> dict[str, Any]:
    family = receipt["family"]
    fields = receipt["fields"]
    for field in REQUIRED_FIELDS[family]:
        if field not in fields:
            raise ValueError(f"missing field {field}")
        validate_observation(family, field, fields[field])
    blockers = [
        {"field": field, "reason": fields[field]["status"]}
        for field in REQUIRED_FIELDS[family]
        if fields[field]["status"] in BLOCKING
    ]
    if blockers:
        return {"authorization": "NOT_AUTHORIZED", "blockers": blockers, "case": None}
    return {"authorization": "AUTHORIZED", "blockers": [], "case": project_case(family, fields, receipt["query"])}
