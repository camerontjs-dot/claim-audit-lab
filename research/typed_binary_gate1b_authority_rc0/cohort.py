from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CleanCase:
    case_id: str
    text: str


CLEAN: tuple[CleanCase, ...] = (
    CleanCase("TW01", "A owns B."),
    CleanCase("TW02", "B is owned by A."),
    CleanCase("TW03", "A is adjacent to B."),
    CleanCase("TW04", "A is north of B."),
    CleanCase("TW05", "B is south of A."),
    CleanCase("TW06", "Room is in Zone."),
    CleanCase("TW07", "Zone contains Room."),
    CleanCase("TW08", "A does not own B."),
    CleanCase("TW09", "B owns A."),
    CleanCase("TW10", "B belongs to A."),
    CleanCase("TW11", "A lies north of B."),
    CleanCase("TW12", "Room lies within Zone."),
    CleanCase("TW13", "A and B are adjacent."),
)
