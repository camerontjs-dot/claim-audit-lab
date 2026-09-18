"""Frozen Gate-1B cohort for strict-comparison authority RC1."""

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
    Case("SCW01", "Women had a higher rate than Men.", Expected.WARRANT),
    Case("SCW02", "Sector A exceeded Sector B by 4 units.", Expected.WARRANT),
    Case("SCW03", "Sector A had a lower score than Sector B.", Expected.WARRANT),
    Case(
        "SCW04",
        "Sector A processed 20 units, 3 more than Sector B.",
        Expected.WARRANT,
    ),
    Case("SCR01", "Sector A was not higher than Sector B.", Expected.REFUSE),
    Case("SCR02", "Sector A was no higher than Sector B.", Expected.REFUSE),
    Case("SCR03", "Sector A was probably higher than Sector B.", Expected.REFUSE),
    Case("SCR04", "Sector A was allegedly higher than Sector B.", Expected.REFUSE),
    Case("SCR05", "Sector A may be higher than Sector B.", Expected.REFUSE),
    Case("SCR06", "Sector A could be higher than Sector B.", Expected.REFUSE),
    Case(
        "SCR07",
        "The report says Sector A is higher than Sector B.",
        Expected.REFUSE,
    ),
)
