from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CleanCase:
    case_id: str
    text: str


CLEAN: tuple[CleanCase, ...] = (
    CleanCase("AW01", "Batch status is released."),
    CleanCase("AW02", "Batch status is held."),
    CleanCase("AW03", "Device mode is standby."),
    CleanCase("AW04", "Record tag is critical."),
    CleanCase("AW05", "System availability is unavailable."),
    CleanCase("AW06", "The batch's status is released."),
    CleanCase("AW07", "Batch status: released."),
    CleanCase("AW08", "The device is in standby mode."),
    CleanCase("AW09", "The batch remains held."),
    CleanCase("AW10", "Device mode is maintenance."),
    CleanCase("AW11", "Other batch status is released."),
    CleanCase("AW12", "Document status is released."),
)
