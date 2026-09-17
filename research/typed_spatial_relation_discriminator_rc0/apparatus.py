"""Frozen apparatus for typed-binary versus spatial relation RC0."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum


class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class Spec:
    predicate: str
    symmetric: bool = False
    inverse: str | None = None


@dataclass(frozen=True, slots=True)
class Atom:
    subject: str
    predicate: str
    object: str
    positive: bool = True


SPECS = {
    "OWNS": Spec("OWNS", inverse="OWNED_BY"),
    "OWNED_BY": Spec("OWNED_BY", inverse="OWNS"),
    "ADJACENT_TO": Spec("ADJACENT_TO", symmetric=True),
    "NORTH_OF": Spec("NORTH_OF", inverse="SOUTH_OF"),
    "SOUTH_OF": Spec("SOUTH_OF", inverse="NORTH_OF"),
    "IN": Spec("IN", inverse="CONTAINS"),
    "CONTAINS": Spec("CONTAINS", inverse="IN"),
}


def equivalent(source: Atom, query: Atom) -> bool:
    spec = SPECS.get(source.predicate)
    if spec is None or query.predicate not in SPECS:
        return False
    if (source.subject, source.predicate, source.object) == (query.subject, query.predicate, query.object):
        return True
    if spec.symmetric and source.predicate == query.predicate:
        return (source.subject, source.object) == (query.object, query.subject)
    if spec.inverse == query.predicate:
        return (source.subject, source.object) == (query.object, query.subject)
    return False


def oracle(source: Atom, query: Atom) -> Relation:
    if not equivalent(source, query):
        return Relation.UNRESOLVED
    return Relation.SUPPORTS if source.positive == query.positive else Relation.REFUTES


def weak_open_predicate(source: Atom, query: Atom) -> Relation:
    if (source.subject, source.predicate, source.object) == (query.subject, query.predicate, query.object):
        return Relation.SUPPORTS if source.positive == query.positive else Relation.REFUTES
    return oracle(source, query)


def weak_all_symmetric(source: Atom, query: Atom) -> Relation:
    if source.predicate == query.predicate and (source.subject, source.object) == (query.object, query.subject):
        return Relation.SUPPORTS if source.positive == query.positive else Relation.REFUTES
    return oracle(source, query)


def weak_ignore_inverse(source: Atom, query: Atom) -> Relation:
    if (source.subject, source.object) == (query.object, query.subject):
        return Relation.UNRESOLVED
    return oracle(source, query)


CASES: tuple[tuple[str, Atom, Atom], ...] = (
    ("R01", Atom("A", "OWNS", "B"), Atom("A", "OWNS", "B")),
    ("R02", Atom("A", "OWNS", "B"), Atom("B", "OWNED_BY", "A")),
    ("R03", Atom("A", "OWNS", "B"), Atom("B", "OWNS", "A")),
    ("R04", Atom("A", "OWNS", "B"), Atom("A", "OWNS", "B", False)),
    ("R05", Atom("A", "ADJACENT_TO", "B"), Atom("B", "ADJACENT_TO", "A")),
    ("R06", Atom("A", "NORTH_OF", "B"), Atom("B", "SOUTH_OF", "A")),
    ("R07", Atom("A", "NORTH_OF", "B"), Atom("B", "NORTH_OF", "A")),
    ("R08", Atom("Room", "IN", "Zone"), Atom("Zone", "CONTAINS", "Room")),
    ("R09", Atom("A", "CUSTOM", "B"), Atom("A", "CUSTOM", "B")),
)


def disagreements(strategy) -> tuple[str, ...]:
    return tuple(case_id for case_id, source, query in CASES if strategy(source, query) != oracle(source, query))
