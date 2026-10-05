"""Early cue router for arm R. It chooses relation lanes. Required guards always run."""

from __future__ import annotations

import re

_EVENT = re.compile(r"\b(before|after|prior to|followed by)\b", re.IGNORECASE)
_QUANTITY = re.compile(
    r"\b(higher|lower|greater|fewer|increased|increasing|increase|decreased|decreasing|decrease|"
    r"grew|growing|declined|declining|fell|falling|reduced|reduction|dropped|dropping|drop|"
    r"rose|rising|percent|million|billion|trillion|edged down|edged up)\b|%|"
    r"\b(?:up|down)\s+\d",
    re.IGNORECASE,
)


def route(claim: str) -> dict[str, object]:
    event = _EVENT.search(claim) is not None
    quantity = _QUANTITY.search(claim) is not None
    relations: list[str] = []
    if quantity or not event:
        relations.append("quantity_relation")
    if event or not quantity:
        relations.append("event_order")
    if not event and not quantity:
        profile = "no_cue_all_relations"
    elif event and quantity:
        profile = "both_cues"
    elif event:
        profile = "event_only"
    else:
        profile = "quantity_only"
    processes = relations + ["scope_guard", "attribution_guard"]
    return {"profile": profile, "processes": processes}
