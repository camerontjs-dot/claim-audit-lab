from __future__ import annotations

from typing import Any

from .contract import (
    ESTABLISHED,
    EXTRACTION_UNRESOLVED,
    INSUFFICIENT_AUTHORITY,
    REQUIRED_FIELDS,
    SEMANTIC_UNKNOWN,
    project_case,
)


def evaluate(receipt: dict[str, Any]) -> dict[str, Any]:
    family = receipt.get("family")
    if family not in REQUIRED_FIELDS:
        raise ValueError(f"unsupported family {family!r}")
    fields = receipt.get("fields")
    if not isinstance(fields, dict):
        raise ValueError("fields must be a dict")

    blockers: list[dict[str, str]] = []
    for name in REQUIRED_FIELDS[family]:
        if name not in fields:
            raise ValueError(f"missing field {name}")
        item = fields[name]
        status = item.get("status")
        if status in (EXTRACTION_UNRESOLVED, INSUFFICIENT_AUTHORITY):
            if item.get("value") is not None:
                raise ValueError(f"{name}: blocking state carries value")
            blockers.append({"field": name, "reason": status})
            continue
        if status not in (ESTABLISHED, SEMANTIC_UNKNOWN):
            raise ValueError(f"{name}: invalid status")
        if item.get("value") is None or not item.get("span") or not item.get("warrant"):
            raise ValueError(f"{name}: incomplete semantic warrant")
        if status == SEMANTIC_UNKNOWN:
            if family != "only_permission" or name not in {"membership", "explicit_permission"} or item.get("value") != "unknown":
                raise ValueError(f"{name}: illegal semantic_unknown")

    if blockers:
        return {"authorization": "NOT_AUTHORIZED", "blockers": blockers, "case": None}
    return {"authorization": "AUTHORIZED", "blockers": [], "case": project_case(family, fields, receipt["query"])}
