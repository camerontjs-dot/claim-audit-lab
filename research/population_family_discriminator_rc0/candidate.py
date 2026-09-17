"""Direct core consumer for Population Family Discriminator RC0."""

from __future__ import annotations

from .cohort import (
    A,
    Authority,
    B,
    MembershipStatus,
    Query,
    QueryPolarity,
    Relation,
    SubsetEdge,
)


def relate(authority: Authority, query: Query) -> Relation:
    """Relate one membership authority to one query without converse leakage."""
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
        if (
            authority.population == A
            and query.population == B
            and authority.status is MembershipStatus.MEMBER
        ):
            return (
                Relation.SUPPORTS
                if query.polarity is QueryPolarity.MEMBER_OF
                else Relation.REFUTES
            )
        if (
            authority.population == B
            and query.population == A
            and authority.status is MembershipStatus.NON_MEMBER
        ):
            return (
                Relation.REFUTES
                if query.polarity is QueryPolarity.MEMBER_OF
                else Relation.SUPPORTS
            )

    if edge is SubsetEdge.B_SUB_A:
        if (
            authority.population == B
            and query.population == A
            and authority.status is MembershipStatus.MEMBER
        ):
            return (
                Relation.SUPPORTS
                if query.polarity is QueryPolarity.MEMBER_OF
                else Relation.REFUTES
            )
        if (
            authority.population == A
            and query.population == B
            and authority.status is MembershipStatus.NON_MEMBER
        ):
            return (
                Relation.REFUTES
                if query.polarity is QueryPolarity.MEMBER_OF
                else Relation.SUPPORTS
            )

    return Relation.UNRESOLVED
