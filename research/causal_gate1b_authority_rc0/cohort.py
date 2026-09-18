from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CleanCase:
    case_id: str
    text: str


CLEAN: tuple[CleanCase, ...] = (
    CleanCase("CW01", "A causes B."),
    CleanCase("CW02", "A contributes to B."),
    CleanCase("CW03", "A prevents B."),
    CleanCase("CW04", "A correlates with B."),
    CleanCase("CW05", "A precedes B."),
    CleanCase("CW06", "A co-occurs with B."),
    CleanCase("CW07", "X causes Y."),
    CleanCase("CW08", "B is caused by A."),
    CleanCase("CW09", "B is prevented by A."),
    CleanCase("CW10", "A is a contributing factor to B."),
    CleanCase("CW11", "A occurs before B."),
    CleanCase("CW12", "A occurs together with B."),
)
