"""Frozen Gate-1B cohort for event-occurrence authority RC0."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CleanCase:
    case_id: str
    text: str


CLEAN: tuple[CleanCase, ...] = (
    CleanCase("EW01", "QA approved the batch."),
    CleanCase("EW02", "QA did not approve the batch."),
    CleanCase("EW03", "Ops released the batch."),
    CleanCase("EW04", "QA signed the record."),
    CleanCase("EW05", "System recorded the event."),
    CleanCase("EW06", "QA approved the batch at T1."),
    CleanCase("EW07", "The batch was approved by QA."),
    CleanCase("EW08", "The batch was not approved by QA."),
    CleanCase("EW09", "QA quarantined the batch."),
    CleanCase("EW10", "QA's approval of the batch occurred."),
    CleanCase("EW11", "Event: QA approved batch."),
)
