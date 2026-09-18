"""Frozen Gate-1B cohort for population/membership authority RC0."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CleanCase:
    case_id: str
    text: str


CLEAN: tuple[CleanCase, ...] = (
    CleanCase("PW01", "Alice is a qualified technician."),
    CleanCase("PW02", "Alice is not a qualified technician."),
    CleanCase("PW03", "Alice is a member of Group A."),
    CleanCase("PW04", "Sterile technicians are trained personnel."),
    CleanCase("PW05", "All sterile technicians are trained personnel."),
    CleanCase("PW06", "Every sterile technician is trained personnel."),
    CleanCase("PW07", "Bob is a reviewer."),
    CleanCase("PW08", "Alice belongs to Group A."),
    CleanCase("PW09", "Qualified technicians include Alice."),
    CleanCase(
        "PW10",
        "Sterile technicians form a subset of trained personnel.",
    ),
    CleanCase("PW11", "Alice serves as a reviewer."),
)
