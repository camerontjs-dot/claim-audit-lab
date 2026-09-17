# ruff: noqa: I001, E501
"""Frozen oracle and weak controls for Population Family Discriminator RC0."""

from __future__ import annotations

from itertools import product

from .cohort import (
    A,
    B,
    CASES,
    Authority,
    MembershipStatus,
    Query,
    QueryPolarity,
    Relation,
    SubsetEdge,
)


def _worlds(authority: Authority) -> tuple[dict[str, bool], ...]:
    worlds: list[dict[str, bool]] = []
    for in_a, in_b in product((False, True), repeat=2):
        world = {A: in_a, B: in_b}
        if authority.subset_edge is SubsetEdge.A_SUB_B and in_a and not in_b:
            continue
        if authority.subset_edge is SubsetEdge.B_SUB_A and in_b and not in_a:
            continue
        status = world[authority.population]
        if authority.status is MembershipStatus.MEMBER and not status:
            continue
        if authority.status is MembershipStatus.NON_MEMBER and status:
            continue
        worlds.append(world)
    assert worlds
    return tuple(worlds)


def oracle_relation(authority: Authority, query: Query) -> Relation:
    if authority.entity != query.entity:
        return Relation.UNRESOLVED
    values = []
    for world in _worlds(authority):
        member = world[query.population]
        values.append(member if query.polarity is QueryPolarity.MEMBER_OF else not member)
    unique = set(values)
    if unique == {True}:
        return Relation.SUPPORTS
    if unique == {False}:
        return Relation.REFUTES
    return Relation.UNRESOLVED


def _direct(authority: Authority, query: Query) -> Relation:
    if authority.entity != query.entity:
        return Relation.UNRESOLVED
    if authority.population == query.population:
        if authority.status is MembershipStatus.UNKNOWN:
            return Relation.UNRESOLVED
        source_member = authority.status is MembershipStatus.MEMBER
        query_member = query.polarity is QueryPolarity.MEMBER_OF
        return Relation.SUPPORTS if source_member == query_member else Relation.REFUTES

    edge = authority.subset_edge
    if edge is SubsetEdge.A_SUB_B:
        if authority.population == A and query.population == B and authority.status is MembershipStatus.MEMBER:
            return Relation.SUPPORTS if query.polarity is QueryPolarity.MEMBER_OF else Relation.REFUTES
        if authority.population == B and query.population == A and authority.status is MembershipStatus.NON_MEMBER:
            return Relation.REFUTES if query.polarity is QueryPolarity.MEMBER_OF else Relation.SUPPORTS
    if edge is SubsetEdge.B_SUB_A:
        if authority.population == B and query.population == A and authority.status is MembershipStatus.MEMBER:
            return Relation.SUPPORTS if query.polarity is QueryPolarity.MEMBER_OF else Relation.REFUTES
        if authority.population == A and query.population == B and authority.status is MembershipStatus.NON_MEMBER:
            return Relation.REFUTES if query.polarity is QueryPolarity.MEMBER_OF else Relation.SUPPORTS
    return Relation.UNRESOLVED


def weak_positive_converse(authority: Authority, query: Query) -> Relation:
    if authority.entity == query.entity and authority.status is MembershipStatus.MEMBER:
        if authority.subset_edge is SubsetEdge.A_SUB_B and authority.population == B and query.population == A:
            return Relation.SUPPORTS if query.polarity is QueryPolarity.MEMBER_OF else Relation.REFUTES
        if authority.subset_edge is SubsetEdge.B_SUB_A and authority.population == A and query.population == B:
            return Relation.SUPPORTS if query.polarity is QueryPolarity.MEMBER_OF else Relation.REFUTES
    return _direct(authority, query)


def weak_negative_converse(authority: Authority, query: Query) -> Relation:
    if authority.entity == query.entity and authority.status is MembershipStatus.NON_MEMBER:
        if authority.subset_edge is SubsetEdge.A_SUB_B and authority.population == A and query.population == B:
            return Relation.REFUTES if query.polarity is QueryPolarity.MEMBER_OF else Relation.SUPPORTS
        if authority.subset_edge is SubsetEdge.B_SUB_A and authority.population == B and query.population == A:
            return Relation.REFUTES if query.polarity is QueryPolarity.MEMBER_OF else Relation.SUPPORTS
    return _direct(authority, query)


def weak_no_negative_inheritance(authority: Authority, query: Query) -> Relation:
    if authority.entity != query.entity:
        return Relation.UNRESOLVED
    if authority.population == query.population:
        return _direct(authority, query)
    if authority.status is MembershipStatus.NON_MEMBER:
        return Relation.UNRESOLVED
    return _direct(authority, query)


def weak_symmetric_subset(authority: Authority, query: Query) -> Relation:
    if authority.entity != query.entity:
        return Relation.UNRESOLVED
    if authority.status is MembershipStatus.MEMBER and authority.population != query.population:
        if authority.subset_edge is not SubsetEdge.NONE:
            return Relation.SUPPORTS if query.polarity is QueryPolarity.MEMBER_OF else Relation.REFUTES
    if authority.status is MembershipStatus.NON_MEMBER and authority.population != query.population:
        if authority.subset_edge is not SubsetEdge.NONE:
            return Relation.REFUTES if query.polarity is QueryPolarity.MEMBER_OF else Relation.SUPPORTS
    return _direct(authority, query)


def weak_unknown_as_negative(authority: Authority, query: Query) -> Relation:
    if authority.status is MembershipStatus.UNKNOWN and authority.entity == query.entity:
        if authority.population == query.population:
            return Relation.REFUTES if query.polarity is QueryPolarity.MEMBER_OF else Relation.SUPPORTS
    return _direct(authority, query)


def disagreements(strategy) -> tuple[str, ...]:
    return tuple(
        case.case_id
        for case in CASES
        if strategy(case.authority, case.query) != oracle_relation(case.authority, case.query)
    )


def oracle_vector() -> tuple[tuple[str, str], ...]:
    return tuple(
        (case.case_id, oracle_relation(case.authority, case.query).value)
        for case in CASES
    )
