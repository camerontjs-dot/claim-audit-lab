"""Frozen apparatus for spatial composition discriminator RC1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from research.typed_binary_measurement_machinery_rc1.cohort import RelationAtom


class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class Contribution:
    atom: RelationAtom
    authority_id: str
    warranted: bool = True
    frame_id: str | None = None
    frame_established: bool = True


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    left: Contribution
    right: Contribution
    query: RelationAtom
    expected: Relation


def a(subject: str, predicate: str, obj: str, positive: bool = True) -> RelationAtom:
    return RelationAtom(subject, predicate, obj, positive)


def c(
    atom: RelationAtom,
    authority_id: str,
    *,
    warranted: bool = True,
    frame_id: str | None = None,
    frame_established: bool = True,
) -> Contribution:
    return Contribution(atom, authority_id, warranted, frame_id, frame_established)


CASES: tuple[Case, ...] = (
    Case(
        "SC01",
        c(a("room","IN","zone"),"a1"),
        c(a("zone","IN","facility"),"a2"),
        a("room","IN","facility"),
        Relation.SUPPORTS,
    ),
    Case(
        "SC02",
        c(a("facility","CONTAINS","zone"),"a1"),
        c(a("zone","CONTAINS","room"),"a2"),
        a("facility","CONTAINS","room"),
        Relation.SUPPORTS,
    ),
    Case(
        "SC03",
        c(a("a","NORTH_OF","b"),"a1",frame_id="map-1"),
        c(a("b","NORTH_OF","c"),"a2",frame_id="map-1"),
        a("a","NORTH_OF","c"),
        Relation.SUPPORTS,
    ),
    Case(
        "SC04",
        c(a("c","SOUTH_OF","b"),"a1",frame_id="map-1"),
        c(a("b","SOUTH_OF","a"),"a2",frame_id="map-1"),
        a("c","SOUTH_OF","a"),
        Relation.SUPPORTS,
    ),
    Case(
        "SC05",
        c(a("room","IN","zone"),"a1"),
        c(a("zone","IN","facility"),"a2"),
        a("room","IN","facility",False),
        Relation.REFUTES,
    ),
    Case(
        "SC06",
        c(a("zone","IN","facility"),"a2"),
        c(a("room","IN","zone"),"a1"),
        a("facility","CONTAINS","room"),
        Relation.SUPPORTS,
    ),
    Case(
        "SU01",
        c(a("a","ADJACENT_TO","b"),"a1"),
        c(a("b","ADJACENT_TO","c"),"a2"),
        a("a","ADJACENT_TO","c"),
        Relation.UNRESOLVED,
    ),
    Case(
        "SU02",
        c(a("a","OWNS","b"),"a1"),
        c(a("b","OWNS","c"),"a2"),
        a("a","OWNS","c"),
        Relation.UNRESOLVED,
    ),
    Case(
        "SU03",
        c(a("a","NORTH_OF","b"),"a1",frame_id="map-1"),
        c(a("b","NORTH_OF","c"),"a2",frame_id="map-2"),
        a("a","NORTH_OF","c"),
        Relation.UNRESOLVED,
    ),
    Case(
        "SU04",
        c(a("a","NORTH_OF","b"),"a1"),
        c(a("b","NORTH_OF","c"),"a2"),
        a("a","NORTH_OF","c"),
        Relation.UNRESOLVED,
    ),
    Case(
        "SU05",
        c(a("a","NORTH_OF","b"),"a1",frame_id="map-1",frame_established=False),
        c(a("b","NORTH_OF","c"),"a2",frame_id="map-1"),
        a("a","NORTH_OF","c"),
        Relation.UNRESOLVED,
    ),
    Case(
        "SU06",
        c(a("room","IN","zone"),"a1"),
        c(a("zone","NORTH_OF","facility"),"a2",frame_id="map-1"),
        a("room","NORTH_OF","facility"),
        Relation.UNRESOLVED,
    ),
    Case(
        "SU07",
        c(a("a","NORTH_OF","b",False),"a1",frame_id="map-1"),
        c(a("b","NORTH_OF","c"),"a2",frame_id="map-1"),
        a("a","NORTH_OF","c"),
        Relation.UNRESOLVED,
    ),
    Case(
        "SU08",
        c(a("room","IN","zone"),"a1"),
        c(a("other_zone","IN","facility"),"a2"),
        a("room","IN","facility"),
        Relation.UNRESOLVED,
    ),
    Case(
        "SU09",
        c(a("room","IN","zone"),"same"),
        c(a("zone","IN","facility"),"same"),
        a("room","IN","facility"),
        Relation.UNRESOLVED,
    ),
    Case(
        "SU10",
        c(a("room","IN","zone"),"a1",warranted=False),
        c(a("zone","IN","facility"),"a2"),
        a("room","IN","facility"),
        Relation.UNRESOLVED,
    ),
    Case(
        "SU11",
        c(a("a","NORTH_OF","b"),"a1",frame_id="map-1"),
        c(a("b","NORTH_OF","a"),"a2",frame_id="map-1"),
        a("a","NORTH_OF","a"),
        Relation.UNRESOLVED,
    ),
    Case(
        "SU12",
        c(a("zone","CONTAINS","room",False),"a1"),
        c(a("facility","CONTAINS","zone"),"a2"),
        a("facility","CONTAINS","room"),
        Relation.UNRESOLVED,
    ),
)


def weak_all_transitive(left: Contribution, right: Contribution, query: RelationAtom) -> Relation:
    if left.atom.object != right.atom.subject:
        return Relation.UNRESOLVED
    if left.atom.predicate != right.atom.predicate:
        return Relation.UNRESOLVED
    derived = a(left.atom.subject, left.atom.predicate, right.atom.object)
    if (derived.subject,derived.predicate,derived.object)==(
        query.subject,query.predicate,query.object
    ):
        return Relation.SUPPORTS if query.positive else Relation.REFUTES
    return Relation.UNRESOLVED


def weak_ignore_frame(left: Contribution, right: Contribution, query: RelationAtom) -> Relation:
    return weak_all_transitive(left, right, query)


def weak_ignore_warrant(left: Contribution, right: Contribution, query: RelationAtom) -> Relation:
    return weak_all_transitive(left, right, query)


def weak_no_inverse_normalization(
    left: Contribution,
    right: Contribution,
    query: RelationAtom,
) -> Relation:
    return weak_all_transitive(left, right, query)
