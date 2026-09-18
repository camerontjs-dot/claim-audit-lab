"""Fresh post-freeze cohort for strict-comparison structural gate RC1."""

from dataclasses import dataclass

from claim_audit_lab.cal_v1_candidate.models import Conclusion


@dataclass(frozen=True, slots=True)
class FreshCase:
    case_id: str
    text: str
    expected: Conclusion


FRESH_CASES: tuple[FreshCase, ...] = (
    FreshCase(
        "SCS-F01",
        "Sector A is significantly higher than Sector B.",
        Conclusion.SUPPORTED,
    ),
    FreshCase(
        "SCS-F02",
        "Sector A showed a lower score than Sector B.",
        Conclusion.CONTRADICTED,
    ),
    FreshCase(
        "SCS-F03",
        "Sector A trailed Sector B by 2 percent.",
        Conclusion.CONTRADICTED,
    ),
    FreshCase(
        "SCS-F04",
        "Sector A handled 40 units, 5 more than Sector B.",
        Conclusion.SUPPORTED,
    ),
    FreshCase(
        "SCS-F05",
        "Sector A had a larger share than Sector B.",
        Conclusion.SUPPORTED,
    ),
    FreshCase(
        "SCS-U01",
        "Analysts believe Sector A is higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCS-U02",
        "Sector A would be higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCS-U03",
        "Sector A might have a higher rate than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCS-U04",
        "Sector A was supposedly higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCS-U05",
        "Sector A was higher than Sector B according to QA.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCS-U06",
        "Sector A was higher than Sector B in the simulation.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCS-U07",
        "Sector A was generally higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCS-U08",
        "Sector A was higher than Sector B, but only in Q1.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCS-U09",
        "Was Sector A higher than Sector B?",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCS-U10",
        '"Sector A was higher than Sector B," the memo states.',
        Conclusion.NOT_CHECKABLE,
    ),
)
