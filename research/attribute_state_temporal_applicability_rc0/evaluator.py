"""Frozen evaluator for attribute-state temporal applicability RC0."""

# ruff: noqa: I001

from __future__ import annotations

from collections.abc import Callable

from .apparatus import (
    StateContribution,
    Strategy,
    TemporalScope,
    TimedStateQuery,
    TemporalStateReceipt,
    failures,
    weak_all_functional,
    weak_ignore_scope,
    weak_ignore_scope_binding,
    weak_ignore_warrant,
    weak_latest_persists,
    weak_relation_only,
)

Candidate = Callable[
    [StateContribution, TemporalScope | None, TimedStateQuery],
    TemporalStateReceipt,
]

WEAKS: tuple[tuple[str, Strategy], ...] = (
    ("ignore_scope", weak_ignore_scope),
    ("latest_persists", weak_latest_persists),
    ("ignore_scope_binding", weak_ignore_scope_binding),
    ("all_functional", weak_all_functional),
    ("ignore_warrant", weak_ignore_warrant),
    ("relation_only", weak_relation_only),
)


def weak_failures() -> dict[str, tuple[str, ...]]:
    return {name: failures(strategy) for name, strategy in WEAKS}
