"""Fresh post-freeze pressure cohort for strict comparison modifier gate RC0."""

from dataclasses import dataclass

from claim_audit_lab.cal_v1_candidate.models import Conclusion


@dataclass(frozen=True, slots=True)
class FreshCase:
    case_id: str
    text: str
    expected: Conclusion


FRESH_CASES: tuple[FreshCase, ...] = (
    FreshCase(
        "SCG-F01",
        "Sector A remained higher than Sector B.",
        Conclusion.SUPPORTED,
    ),
    FreshCase(
        "SCG-F02",
        "Sector A was substantially higher than Sector B.",
        Conclusion.SUPPORTED,
    ),
    FreshCase(
        "SCG-F03",
        "Sector A stayed lower than Sector B.",
        Conclusion.CONTRADICTED,
    ),
    FreshCase(
        "SCG-F04",
        "Sector A was notably higher than Sector B.",
        Conclusion.SUPPORTED,
    ),
    FreshCase(
        "SCG-U01",
        "Sector A is believed to be higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCG-U02",
        "Sector A is thought to be higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCG-U03",
        "Sector A should be higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCG-U04",
        "Sector A must be higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCG-U05",
        "Sector A can be higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCG-U06",
        "Sector A is conceivably higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCG-U07",
        "Sector A is expected to be higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCG-U08",
        "Sector A is said to be higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCG-U09",
        "Sector A isn't higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    FreshCase(
        "SCG-U10",
        "Sector A is higher than Sector B only if QA approves.",
        Conclusion.NOT_CHECKABLE,
    ),
)
