"""Frozen Gate-1B cohort for bounded deontic authority RC0."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CleanCase:
    case_id: str
    text: str


CLEAN: tuple[CleanCase, ...] = (
    CleanCase("DW01", "Qualified technicians may release the batch."),
    CleanCase("DW02", "Qualified technicians must not release the batch."),
    CleanCase("DW03", "Qualified technicians must release the batch."),
    CleanCase("DW04", "Only qualified technicians may release the batch."),
    CleanCase("DW05", "Qualified technicians are permitted to release the batch."),
    CleanCase("DW06", "Qualified technicians are prohibited from releasing the batch."),
    CleanCase("DW07", "Qualified technicians are required to release the batch."),
    CleanCase("DW08", "QA may approve the record."),
    CleanCase("DW09", "Qualified technicians may archive the record."),
    CleanCase(
        "DW10",
        "Qualified technicians may release the batch if QA approves.",
    ),
    CleanCase(
        "DW11",
        "Qualified technicians must release the batch after QA signs.",
    ),
    CleanCase(
        "DW12",
        "Qualified technicians may release the batch before QA signs.",
    ),
    CleanCase(
        "DW13",
        "Qualified technicians may release the batch except contractors.",
    ),
    CleanCase(
        "DW14",
        "Only qualified technicians may release the batch after QA signs.",
    ),
)
