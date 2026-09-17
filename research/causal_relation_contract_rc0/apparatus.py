"""Frozen apparatus for Causal Relation Family Contract RC0."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum


class Kind(StrEnum):
    CAUSES = "CAUSES"
    CONTRIBUTES_TO = "CONTRIBUTES_TO"
    PREVENTS = "PREVENTS"
    CORRELATES_WITH = "CORRELATES_WITH"
    PRECEDES = "PRECEDES"
    CO_OCCURS = "CO_OCCURS"


class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class Claim:
    cause: str
    effect: str
    kind: Kind


def oracle(source: Claim, query: Claim) -> Relation:
    if (source.cause, source.effect) != (query.cause, query.effect):
        return Relation.UNRESOLVED
    if source.kind is query.kind:
        return Relation.SUPPORTS
    if {source.kind, query.kind} == {Kind.CAUSES, Kind.PREVENTS}:
        return Relation.REFUTES
    return Relation.UNRESOLVED


def weak_precedence_causes(source: Claim, query: Claim) -> Relation:
    if source.kind is Kind.PRECEDES and query.kind is Kind.CAUSES and (source.cause, source.effect) == (query.cause, query.effect):
        return Relation.SUPPORTS
    return oracle(source, query)


def weak_correlation_causes(source: Claim, query: Claim) -> Relation:
    if source.kind is Kind.CORRELATES_WITH and query.kind is Kind.CAUSES and (source.cause, source.effect) == (query.cause, query.effect):
        return Relation.SUPPORTS
    return oracle(source, query)


def weak_contribution_causes(source: Claim, query: Claim) -> Relation:
    if source.kind is Kind.CONTRIBUTES_TO and query.kind is Kind.CAUSES and (source.cause, source.effect) == (query.cause, query.effect):
        return Relation.SUPPORTS
    return oracle(source, query)


def weak_cause_contributes(source: Claim, query: Claim) -> Relation:
    if source.kind is Kind.CAUSES and query.kind is Kind.CONTRIBUTES_TO and (source.cause, source.effect) == (query.cause, query.effect):
        return Relation.SUPPORTS
    return oracle(source, query)


BASE = Claim("A", "B", Kind.CAUSES)
CASES: tuple[tuple[str, Claim, Claim], ...] = (
    ("C01", BASE, BASE),
    ("C02", BASE, replace(BASE, kind=Kind.PREVENTS)),
    ("C03", replace(BASE, kind=Kind.PREVENTS), BASE),
    ("C04", replace(BASE, kind=Kind.CONTRIBUTES_TO), BASE),
    ("C05", BASE, replace(BASE, kind=Kind.CONTRIBUTES_TO)),
    ("C06", replace(BASE, kind=Kind.CORRELATES_WITH), BASE),
    ("C07", replace(BASE, kind=Kind.PRECEDES), BASE),
    ("C08", replace(BASE, kind=Kind.CO_OCCURS), BASE),
    ("C09", BASE, replace(BASE, cause="X")),
    ("C10", BASE, replace(BASE, effect="Y")),
)


def disagreements(strategy) -> tuple[str, ...]:
    return tuple(case_id for case_id, source, query in CASES if strategy(source, query) != oracle(source, query))
