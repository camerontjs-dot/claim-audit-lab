# ruff: noqa: I001
"""Revealed prior failures used only as RC1 development controls."""

from .candidate import eligibility

UNSAFE = (
    "Sector A was not higher than Sector B.",
    "Sector A was no higher than Sector B.",
    "Sector A was probably higher than Sector B.",
    "Sector A was allegedly higher than Sector B.",
    "Sector A may be higher than Sector B.",
    "Sector A could be higher than Sector B.",
    "Sector A is believed to be higher than Sector B.",
    "Sector A is thought to be higher than Sector B.",
    "Sector A should be higher than Sector B.",
    "Sector A must be higher than Sector B.",
    "Sector A can be higher than Sector B.",
    "Sector A is conceivably higher than Sector B.",
    "Sector A is expected to be higher than Sector B.",
)

POSITIVE = (
    "Sector A was higher than Sector B.",
    "Sector A remained higher than Sector B.",
    "Sector A was substantially higher than Sector B.",
    "Sector A stayed lower than Sector B.",
    "Sector A recorded a higher rate than Sector B.",
    "Sector A exceeded Sector B by 4 units.",
    "Sector A processed 20 units, 3 more than Sector B.",
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
