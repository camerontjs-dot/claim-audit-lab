"""Frozen evaluator for occurrence + order binding discriminator RC0."""

from __future__ import annotations

from collections.abc import Callable

from .apparatus import (
    CASES,
    OccurrenceContribution,
    OrderContribution,
    Query,
    Relation,
    weak_binding_only,
    weak_call_order,
    weak_field_only,
    weak_ignore_warrant,
)

Candidate = Callable[
    [OccurrenceContribution, OccurrenceContribution, OrderContribution, Query],
    Relation,
]


def failures(candidate: Candidate) -> tuple[str, ...]:
    result: list[str] = []
    for case in CASES:
        observed = candidate(
            case.first_occurrence,
            case.second_occurrence,
            case.order,
            case.query,
        )
        if observed is not case.expected:
            result.append(
                f"{case.case_id}:{observed.value}-expected-{case.expected.value}"
            )
    return tuple(result)


WEAKS: tuple[tuple[str, Candidate], ...] = (
    ("field_only", weak_field_only),
    ("binding_only", weak_binding_only),
    ("ignore_warrant", weak_ignore_warrant),
    ("call_order", weak_call_order),
)


def weak_failures() -> dict[str, tuple[str, ...]]:
    return {name: failures(candidate) for name, candidate in WEAKS}
