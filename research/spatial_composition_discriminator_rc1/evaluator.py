"""Frozen evaluator for spatial composition discriminator RC1."""

# ruff: noqa: I001

from __future__ import annotations

from collections.abc import Callable

from research.typed_binary_measurement_machinery_rc1.cohort import RelationAtom

from .apparatus import (
    CASES,
    Contribution,
    Relation,
    weak_all_transitive,
    weak_ignore_frame,
    weak_ignore_warrant,
    weak_no_inverse_normalization,
)


Candidate = Callable[[Contribution, Contribution, RelationAtom], Relation]


def failures(candidate: Candidate) -> tuple[str, ...]:
    result: list[str] = []
    for case in CASES:
        observed = candidate(case.left, case.right, case.query)
        if observed is not case.expected:
            result.append(
                f"{case.case_id}:{observed.value}-expected-{case.expected.value}"
            )
    return tuple(result)


WEAKS: tuple[tuple[str, Candidate], ...] = (
    ("all_transitive", weak_all_transitive),
    ("ignore_frame", weak_ignore_frame),
    ("ignore_warrant", weak_ignore_warrant),
    ("no_inverse", weak_no_inverse_normalization),
)


def weak_failures() -> dict[str, tuple[str, ...]]:
    return {name: failures(candidate) for name, candidate in WEAKS}
