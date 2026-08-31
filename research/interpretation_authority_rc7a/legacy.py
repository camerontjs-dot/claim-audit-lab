from __future__ import annotations

import copy
from typing import Any

from .contract import EXTRACTION_UNRESOLVED, INSUFFICIENT_AUTHORITY, project_case


def collapse(receipt: dict[str, Any]) -> dict[str, Any]:
    """Intentionally unsafe comparator for the category error under test."""
    family = receipt["family"]
    fields = copy.deepcopy(receipt["fields"])
    for name, item in fields.items():
        if item["status"] not in {EXTRACTION_UNRESOLVED, INSUFFICIENT_AUTHORITY}:
            continue
        if family == "only_permission" and name in {"membership", "explicit_permission"}:
            item.update({"status": "semantic_unknown", "value": "unknown", "span": "<fabricated-by-collapse>", "warrant": "legacy_collapse"})
        elif family == "role_binding":
            defaults = {"predicate": "review", "subject": "e0", "object": "e1", "polarity": "positive"}
            item.update({"status": "established", "value": defaults[name], "span": "<fabricated-by-collapse>", "warrant": "legacy_default"})
        elif family == "quantifier":
            defaults = {"population": "inspector", "predicate": "sign", "quantifier": "some", "polarity": "positive"}
            item.update({"status": "established", "value": defaults[name], "span": "<fabricated-by-collapse>", "warrant": "legacy_default"})
    return project_case(family, fields, receipt["query"])
