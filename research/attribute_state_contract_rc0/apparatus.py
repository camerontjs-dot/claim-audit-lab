"""Frozen apparatus for Attribute State Family Contract RC0."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum


class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class State:
    entity: str
    attribute: str
    domain: str
    value: str
    functional: bool


def oracle(source: State, query: State) -> Relation:
    if (source.entity, source.attribute, source.domain) != (query.entity, query.attribute, query.domain):
        return Relation.UNRESOLVED
    if source.value == query.value:
        return Relation.SUPPORTS
    if source.functional and query.functional:
        return Relation.REFUTES
    return Relation.UNRESOLVED


def weak_generic_spo(source: State, query: State) -> Relation:
    if source.entity == query.entity and source.attribute == query.attribute:
        return Relation.SUPPORTS if source.value == query.value else Relation.REFUTES
    return Relation.UNRESOLVED


def weak_ignore_domain(source: State, query: State) -> Relation:
    return oracle(replace(source, domain=query.domain), query)


def weak_ignore_entity(source: State, query: State) -> Relation:
    return oracle(replace(source, entity=query.entity), query)


def weak_nonfunctional_as_functional(source: State, query: State) -> Relation:
    return oracle(replace(source, functional=True), replace(query, functional=True))


CASES: tuple[tuple[str, State, State], ...] = (
    ("A01", State("batch", "status", "batch_status", "released", True), State("batch", "status", "batch_status", "released", True)),
    ("A02", State("batch", "status", "batch_status", "released", True), State("batch", "status", "batch_status", "held", True)),
    ("A03", State("batch", "status", "batch_status", "released", True), State("other", "status", "batch_status", "held", True)),
    ("A04", State("batch", "status", "batch_status", "released", True), State("batch", "status", "document_status", "held", True)),
    ("A05", State("device", "mode", "device_mode", "standby", True), State("device", "mode", "device_mode", "active", True)),
    ("A06", State("record", "tag", "labels", "critical", False), State("record", "tag", "labels", "reviewed", False)),
    ("A07", State("record", "tag", "labels", "critical", False), State("record", "tag", "labels", "critical", False)),
)


def disagreements(strategy) -> tuple[str, ...]:
    return tuple(case_id for case_id, source, query in CASES if strategy(source, query) != oracle(source, query))
