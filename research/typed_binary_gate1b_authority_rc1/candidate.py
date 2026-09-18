"""Independent source completion for typed-binary Gate-1B authority RC1."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from research.typed_binary_measurement_machinery_rc1.cohort import RelationAtom


@dataclass(frozen=True, slots=True)
class TypedBinaryAuthority:
    atom: RelationAtom
    source_sha256: str
    status: str = "WARRANTED"


def _clean(text: str) -> str:
    compact = " ".join(text.strip().split())
    return compact[:-1] if compact.endswith(".") else compact


def _atom(
    subject: str,
    predicate: str,
    obj: str,
    positive: bool = True,
) -> RelationAtom:
    return RelationAtom(
        subject.casefold(),
        predicate,
        obj.casefold(),
        positive,
    )


def _source_atom(text: str) -> RelationAtom:
    compact = _clean(text)

    patterns: tuple[tuple[str, str, bool], ...] = (
        (r"(?P<s>A|B) owns (?P<o>A|B)", "OWNS", True),
        (r"(?P<s>A|B) does not own (?P<o>A|B)", "OWNS", False),
        (r"(?P<s>A|B) is owned by (?P<o>A|B)", "OWNED_BY", True),
        (r"(?P<s>A|B) is adjacent to (?P<o>A|B)", "ADJACENT_TO", True),
        (r"(?P<s>A|B) is north of (?P<o>A|B)", "NORTH_OF", True),
        (r"(?P<s>A|B) is south of (?P<o>A|B)", "SOUTH_OF", True),
        (r"(?P<s>Room) is in (?P<o>Zone)", "IN", True),
        (r"(?P<s>Zone) contains (?P<o>Room)", "CONTAINS", True),
        (r"(?P<s>B) belongs to (?P<o>A)", "OWNED_BY", True),
        (r"(?P<s>A) lies north of (?P<o>B)", "NORTH_OF", True),
        (r"(?P<s>Room) lies within (?P<o>Zone)", "IN", True),
    )
    for pattern, predicate, positive in patterns:
        match = re.fullmatch(pattern, compact, re.IGNORECASE)
        if match is not None:
            return _atom(
                match.group("s"),
                predicate,
                match.group("o"),
                positive,
            )

    raise ValueError("typed-binary source not independently reconstructable")


def complete_and_warrant_typed_binary(
    text: str,
    measured: RelationAtom,
) -> TypedBinaryAuthority:
    completed = _source_atom(text)
    if completed != measured:
        raise ValueError("measurement/source semantic mismatch")
    return TypedBinaryAuthority(
        atom=completed,
        source_sha256=hashlib.sha256(text.encode()).hexdigest(),
    )
