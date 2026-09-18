"""Frozen evaluator for population + deontic applicability discriminator RC0."""

from __future__ import annotations

from collections.abc import Callable

from .apparatus import (
    CASES,
    AppliedNorm,
    MembershipContribution,
    NormContribution,
    Relation,
    weak_drop_modifiers,
    weak_ignore_status,
    weak_ignore_subject_kind,
    weak_ignore_warrant,
    weak_string_only,
)


Candidate = Callable[
    [NormContribution, MembershipContribution, AppliedNorm],
    Relation,
]


def failures(candidate: Candidate) -> tuple[str, ...]:
    result: list[str] = []
    for case in CASES:
        observed = candidate(case.norm, case.membership, case.query)
        if observed is not case.expected:
            result.append(
                f"{case.case_id}:{observed.value}-expected-{case.expected.value}"
            )
    return tuple(result)


WEAKS: tuple[tuple[str, Candidate], ...] = (
    ("string_only", weak_string_only),
    ("ignore_status", weak_ignore_status),
    ("ignore_subject_kind", weak_ignore_subject_kind),
    ("drop_modifiers", weak_drop_modifiers),
    ("ignore_warrant", weak_ignore_warrant),
)


def weak_failures() -> dict[str, tuple[str, ...]]:
    return {name: failures(candidate) for name, candidate in WEAKS}
