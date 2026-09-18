"""Frozen evaluator for warranted quantitative-change composition RC1."""

# ruff: noqa: I001

from __future__ import annotations

from collections.abc import Callable

from .apparatus import (
    CASES,
    Contribution,
    Query,
    Relation,
    oracle,
    weak_ignore_identity,
    weak_ignore_warrant,
    weak_input_order,
    weak_midpoint,
)


Candidate = Callable[[Contribution, Contribution, Query], Relation]


def failures(candidate: Candidate) -> tuple[str, ...]:
    result: list[str] = []
    for case in CASES:
        observed = candidate(case.left, case.right, case.query)
        expected = oracle(case)
        if observed is not expected:
            result.append(f"{case.case_id}:{observed.value}-expected-{expected.value}")
    return tuple(result)


WEAKS: tuple[tuple[str, Candidate], ...] = (
    ("input_order", weak_input_order),
    ("ignore_identity", weak_ignore_identity),
    ("midpoint", weak_midpoint),
    ("ignore_warrant", weak_ignore_warrant),
)


def weak_failures() -> dict[str, tuple[str, ...]]:
    return {name: failures(candidate) for name, candidate in WEAKS}
