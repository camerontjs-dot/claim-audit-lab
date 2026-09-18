"""Frozen Gate-1B cohort for direct-event-order authority RC1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Expected(StrEnum):
    WARRANT = "WARRANT"
    REFUSE = "REFUSE"


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    text: str
    expected: Expected


CASES: tuple[Case, ...] = (
    Case(
        "EOW01",
        "Talia reviewed packet u before Ravi signed ledger c.",
        Expected.WARRANT,
    ),
    Case(
        "EOW02",
        "Talia reviewed packet u after Ravi signed ledger c.",
        Expected.WARRANT,
    ),
    Case(
        "EOW03",
        "Talia did not review packet u before Ravi signed ledger c.",
        Expected.WARRANT,
    ),
    Case(
        "EOW04",
        "Talia reviewed packet u after Ravi did not sign ledger c.",
        Expected.WARRANT,
    ),
    Case(
        "EOR01",
        "Perhaps Talia reviewed packet u before Ravi signed ledger c.",
        Expected.REFUSE,
    ),
    Case(
        "EOR02",
        "If Talia reviewed packet u before Ravi signed ledger c.",
        Expected.REFUSE,
    ),
    Case(
        "EOR03",
        "Talia reviewed packet u not before Ravi signed ledger c.",
        Expected.REFUSE,
    ),
    Case(
        "EOR04",
        "Talia reviewed packet u immediately before Ravi signed ledger c.",
        Expected.REFUSE,
    ),
    Case(
        "EOR05",
        "Talia reviewed packet u shortly before Ravi signed ledger c.",
        Expected.REFUSE,
    ),
    Case(
        "EOR06",
        "Talia reviewed packet u before Ravi signed ledger c because QA requested it.",
        Expected.REFUSE,
    ),
)
