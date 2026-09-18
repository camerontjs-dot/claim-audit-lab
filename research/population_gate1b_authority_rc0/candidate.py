"""Independent source completion for population/membership Gate-1B RC0."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from research.population_measurement_machinery_rc0.cohort import (
    ALICE,
    BOB,
    GROUP_A,
    QUALIFIED_PERSONNEL,
    QUALIFIED_TECHNICIANS,
    REVIEWERS,
    STERILE_TECHNICIANS,
    TRAINED_PERSONNEL,
    Atom,
    MembershipAtom,
    MembershipStatus,
    SubsetAtom,
)


@dataclass(frozen=True, slots=True)
class PopulationAuthority:
    atom: Atom
    source_sha256: str
    status: str = "WARRANTED"


_ENTITY = {
    "alice": ALICE,
    "bob": BOB,
}

_POPULATION = {
    "qualified technician": QUALIFIED_TECHNICIANS,
    "qualified technicians": QUALIFIED_TECHNICIANS,
    "reviewer": REVIEWERS,
    "reviewers": REVIEWERS,
    "group a": GROUP_A,
    "sterile technician": STERILE_TECHNICIANS,
    "sterile technicians": STERILE_TECHNICIANS,
    "trained personnel": TRAINED_PERSONNEL,
    "qualified personnel": QUALIFIED_PERSONNEL,
}


def _clean(text: str) -> str:
    compact = " ".join(text.strip().split())
    return compact[:-1] if compact.endswith(".") else compact


def _membership(
    entity: str,
    population: str,
    status: MembershipStatus,
) -> MembershipAtom:
    return MembershipAtom(
        _ENTITY[entity.casefold()],
        _POPULATION[population.casefold()],
        status,
    )


def _subset(child: str, parent: str) -> SubsetAtom:
    return SubsetAtom(
        _POPULATION[child.casefold()],
        _POPULATION[parent.casefold()],
    )


def _source_atom(text: str) -> Atom:
    compact = _clean(text)

    member_of = re.fullmatch(
        r"(?P<entity>Alice|Bob)\s+is\s+(?P<neg>not\s+)?a\s+member\s+of\s+"
        r"(?P<population>Group A)",
        compact,
        re.IGNORECASE,
    )
    if member_of is not None:
        status = (
            MembershipStatus.NON_MEMBER
            if member_of.group("neg") is not None
            else MembershipStatus.MEMBER
        )
        return _membership(
            member_of.group("entity"),
            member_of.group("population"),
            status,
        )

    simple_member = re.fullmatch(
        r"(?P<entity>Alice|Bob)\s+is\s+(?P<neg>not\s+)?a\s+"
        r"(?P<population>qualified technician|reviewer)",
        compact,
        re.IGNORECASE,
    )
    if simple_member is not None:
        status = (
            MembershipStatus.NON_MEMBER
            if simple_member.group("neg") is not None
            else MembershipStatus.MEMBER
        )
        return _membership(
            simple_member.group("entity"),
            simple_member.group("population"),
            status,
        )

    subset_plain = re.fullmatch(
        r"(?P<child>Sterile technicians)\s+are\s+"
        r"(?P<parent>trained personnel)",
        compact,
        re.IGNORECASE,
    )
    if subset_plain is not None:
        return _subset(
            subset_plain.group("child"),
            subset_plain.group("parent"),
        )

    subset_all = re.fullmatch(
        r"All\s+(?P<child>sterile technicians)\s+are\s+"
        r"(?P<parent>trained personnel)",
        compact,
        re.IGNORECASE,
    )
    if subset_all is not None:
        return _subset(
            subset_all.group("child"),
            subset_all.group("parent"),
        )

    subset_every = re.fullmatch(
        r"Every\s+(?P<child>sterile technician)\s+is\s+"
        r"(?P<parent>trained personnel)",
        compact,
        re.IGNORECASE,
    )
    if subset_every is not None:
        return _subset(
            subset_every.group("child"),
            subset_every.group("parent"),
        )

    belongs = re.fullmatch(
        r"(?P<entity>Alice|Bob) belongs to (?P<population>Group A)",
        compact,
        re.IGNORECASE,
    )
    if belongs is not None:
        return _membership(
            belongs.group("entity"),
            belongs.group("population"),
            MembershipStatus.MEMBER,
        )

    includes = re.fullmatch(
        r"Qualified technicians include (?P<entity>Alice|Bob)",
        compact,
        re.IGNORECASE,
    )
    if includes is not None:
        return MembershipAtom(
            _ENTITY[includes.group("entity").casefold()],
            QUALIFIED_TECHNICIANS,
            MembershipStatus.MEMBER,
        )

    explicit_subset = re.fullmatch(
        r"Sterile technicians form a subset of trained personnel",
        compact,
        re.IGNORECASE,
    )
    if explicit_subset is not None:
        return SubsetAtom(STERILE_TECHNICIANS, TRAINED_PERSONNEL)

    serves = re.fullmatch(
        r"(?P<entity>Alice|Bob) serves as a reviewer",
        compact,
        re.IGNORECASE,
    )
    if serves is not None:
        return MembershipAtom(
            _ENTITY[serves.group("entity").casefold()],
            REVIEWERS,
            MembershipStatus.MEMBER,
        )

    raise ValueError("population source not independently reconstructable")


def complete_and_warrant_population(
    text: str,
    measured: Atom,
) -> PopulationAuthority:
    completed = _source_atom(text)
    if completed != measured:
        raise ValueError("measurement/source semantic mismatch")
    return PopulationAuthority(
        atom=completed,
        source_sha256=hashlib.sha256(text.encode()).hexdigest(),
    )
