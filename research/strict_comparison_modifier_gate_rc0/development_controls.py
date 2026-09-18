"""Revealed parent failures used only as successor development controls."""

from .candidate import eligibility


KNOWN_PARENT_FAILURES = (
    "Sector A was not higher than Sector B.",
    "Sector A was no higher than Sector B.",
    "Sector A was probably higher than Sector B.",
    "Sector A was allegedly higher than Sector B.",
    "Sector A may be higher than Sector B.",
    "Sector A could be higher than Sector B.",
)

KNOWN_DIRECT_POSITIVES = (
    "Sector A was higher than Sector B.",
    "Sector A was slightly higher than Sector B.",
    "Sector A was substantially higher than Sector B.",
)


def development_failures() -> tuple[str, ...]:
    failures: list[str] = []
    for text in KNOWN_PARENT_FAILURES:
        if eligibility(text).eligible:
            failures.append(f"unsafe-admit:{text}")
    for text in KNOWN_DIRECT_POSITIVES:
        if not eligibility(text).eligible:
            failures.append(f"positive-block:{text}")
    return tuple(failures)
