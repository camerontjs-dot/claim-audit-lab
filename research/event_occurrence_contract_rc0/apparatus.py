"""Frozen typed apparatus for Event Occurrence Family Contract RC0."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum


class Polarity(StrEnum):
    OCCURRED = "OCCURRED"
    DID_NOT_OCCUR = "DID_NOT_OCCUR"


class SourceKind(StrEnum):
    DIRECT = "DIRECT"
    ORDER_MENTION_ONLY = "ORDER_MENTION_ONLY"


class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class Event:
    actor: str
    action: str
    object: str
    polarity: Polarity
    scope: str = "NARRATOR"
    time: str | None = None
    source_kind: SourceKind = SourceKind.DIRECT


def oracle(source: Event, query: Event) -> Relation:
    if source.source_kind is not SourceKind.DIRECT:
        return Relation.UNRESOLVED
    if (
        source.actor,
        source.action,
        source.object,
        source.scope,
        source.time,
    ) != (
        query.actor,
        query.action,
        query.object,
        query.scope,
        query.time,
    ):
        return Relation.UNRESOLVED
    return Relation.SUPPORTS if source.polarity is query.polarity else Relation.REFUTES


def weak_ignore_polarity(source: Event, query: Event) -> Relation:
    if (source.actor, source.action, source.object) == (query.actor, query.action, query.object):
        return Relation.SUPPORTS
    return Relation.UNRESOLVED


def weak_ignore_roles(source: Event, query: Event) -> Relation:
    left = sorted((source.actor, source.object))
    right = sorted((query.actor, query.object))
    if source.action == query.action and left == right:
        return Relation.SUPPORTS if source.polarity is query.polarity else Relation.REFUTES
    return Relation.UNRESOLVED


def weak_erase_scope(source: Event, query: Event) -> Relation:
    return oracle(replace(source, scope=query.scope), query)


def weak_mention_is_occurrence(source: Event, query: Event) -> Relation:
    return oracle(replace(source, source_kind=SourceKind.DIRECT), query)


BASE = Event("QA", "approved", "batch", Polarity.OCCURRED)
CASES: tuple[tuple[str, Event, Event], ...] = (
    ("E01", BASE, BASE),
    ("E02", BASE, replace(BASE, polarity=Polarity.DID_NOT_OCCUR)),
    ("E03", replace(BASE, polarity=Polarity.DID_NOT_OCCUR), BASE),
    ("E04", BASE, replace(BASE, actor="Ops")),
    ("E05", BASE, replace(BASE, object="record")),
    ("E06", Event("QA", "assigned", "Ops", Polarity.OCCURRED), Event("Ops", "assigned", "QA", Polarity.OCCURRED)),
    ("E07", replace(BASE, scope="REPORTED"), BASE),
    ("E08", replace(BASE, time="T1"), replace(BASE, time="T2")),
    ("E09", replace(BASE, source_kind=SourceKind.ORDER_MENTION_ONLY), BASE),
    ("E10", replace(BASE, time="T1"), replace(BASE, time="T1")),
)


def disagreements(strategy) -> tuple[str, ...]:
    return tuple(case_id for case_id, source, query in CASES if strategy(source, query) != oracle(source, query))
