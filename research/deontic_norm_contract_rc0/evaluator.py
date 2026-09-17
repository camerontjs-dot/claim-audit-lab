"""Frozen oracle and weak controls for Deontic Norm Family Contract RC0."""
from __future__ import annotations

from itertools import product

from .cohort import CASES, Mode, Norm, Relation


_VARIABLE = {
    Mode.PERMITTED: "P",
    Mode.PROHIBITED: "F",
    Mode.OBLIGATORY: "O",
    Mode.PERMISSION_RESTRICTED_TO: "R",
}


def _scope(norm: Norm) -> tuple[object, ...]:
    return (
        norm.subject,
        norm.action,
        norm.exceptions,
        norm.condition,
        norm.temporal_relation,
        norm.temporal_reference,
    )


def _source_compatible(source: Norm, assignment: dict[str, bool]) -> bool:
    if source.mode is Mode.PERMITTED:
        return assignment["P"] and not assignment["F"]
    if source.mode is Mode.PROHIBITED:
        return assignment["F"] and not assignment["P"] and not assignment["O"]
    if source.mode is Mode.OBLIGATORY:
        return assignment["O"] and not assignment["F"]
    if source.mode is Mode.PERMISSION_RESTRICTED_TO:
        return assignment["R"]
    raise AssertionError(source.mode)


def oracle_relation(source: Norm, query: Norm) -> Relation:
    """Possible-assignment oracle for the frozen conservative deontic contract."""
    if _scope(source) != _scope(query):
        return Relation.UNRESOLVED

    worlds: list[dict[str, bool]] = []
    for p, f, o, r in product((False, True), repeat=4):
        assignment = {"P": p, "F": f, "O": o, "R": r}
        if _source_compatible(source, assignment):
            worlds.append(assignment)
    assert worlds

    query_var = _VARIABLE[query.mode]
    values = {world[query_var] for world in worlds}
    if values == {True}:
        return Relation.SUPPORTS
    if values == {False}:
        return Relation.REFUTES
    return Relation.UNRESOLVED


def weak_ought_implies_may(source: Norm, query: Norm) -> Relation:
    """Plausible weak strategy: incorrectly treats obligation as permission."""
    if _scope(source) == _scope(query):
        if source.mode is Mode.OBLIGATORY and query.mode is Mode.PERMITTED:
            return Relation.SUPPORTS
    return _direct_conservative(source, query)


def weak_restriction_grants_permission(source: Norm, query: Norm) -> Relation:
    """Plausible weak strategy: incorrectly turns a necessary condition into a grant."""
    if _scope(source) == _scope(query):
        if source.mode is Mode.PERMISSION_RESTRICTED_TO and query.mode is Mode.PERMITTED:
            return Relation.SUPPORTS
    return _direct_conservative(source, query)


def weak_ignore_modifiers(source: Norm, query: Norm) -> Relation:
    """Plausible weak strategy: erases exception/condition/temporal binding."""
    source_core = Norm(source.mode, source.subject, source.action)
    query_core = Norm(query.mode, query.subject, query.action)
    return _direct_conservative(source_core, query_core)


def weak_exact_mode_only(source: Norm, query: Norm) -> Relation:
    """Plausible weak strategy: supports equality but never emits contradiction."""
    if _scope(source) != _scope(query):
        return Relation.UNRESOLVED
    if source.mode is query.mode:
        return Relation.SUPPORTS
    return Relation.UNRESOLVED


def _direct_conservative(source: Norm, query: Norm) -> Relation:
    """Compact rule table matching the intended contract, used only by weak controls."""
    if _scope(source) != _scope(query):
        return Relation.UNRESOLVED
    if source.mode is query.mode:
        return Relation.SUPPORTS
    if {source.mode, query.mode} == {Mode.PERMITTED, Mode.PROHIBITED}:
        return Relation.REFUTES
    if {source.mode, query.mode} == {Mode.OBLIGATORY, Mode.PROHIBITED}:
        return Relation.REFUTES
    return Relation.UNRESOLVED


def disagreements(strategy) -> tuple[str, ...]:
    return tuple(
        case.case_id
        for case in CASES
        if strategy(case.source, case.query) != oracle_relation(case.source, case.query)
    )


def oracle_vector() -> tuple[tuple[str, str], ...]:
    return tuple((case.case_id, oracle_relation(case.source, case.query).value) for case in CASES)
