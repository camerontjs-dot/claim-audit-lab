# ruff: noqa: I001
"""Revealed event-order failures used only as RC1 development controls."""

from .candidate import eligibility

UNSAFE = (
    "Perhaps Talia reviewed packet u before Ravi signed ledger c.",
    "If Talia reviewed packet u before Ravi signed ledger c.",
    "Talia reviewed packet u not before Ravi signed ledger c.",
    "Talia reviewed packet u immediately before Ravi signed ledger c.",
    "Talia reviewed packet u shortly before Ravi signed ledger c.",
    "Talia reviewed packet u before Ravi signed ledger c because QA requested it.",
    "Talia reviewed packet u before Ravi signed ledger c and Ivo released form j.",
)

POSITIVE = (
    "Talia reviewed packet u before Ravi signed ledger c.",
    "Talia reviewed packet u after Ravi signed ledger c.",
    "Talia did not review packet u before Ravi signed ledger c.",
    "Talia reviewed packet u after Ravi did not sign ledger c.",
)


def failures() -> tuple[str, ...]:
    problems: list[str] = []
    for text in UNSAFE:
        if eligibility(text).eligible:
            problems.append(f"unsafe-admit:{text}")
    for text in POSITIVE:
        if not eligibility(text).eligible:
            problems.append(f"positive-block:{text}")
    return tuple(problems)
