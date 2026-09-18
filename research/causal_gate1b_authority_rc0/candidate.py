"""Independent source completion for explicit causal-assertion Gate-1B RC0."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from research.causal_measurement_machinery_rc0.cohort import CausalAtom, Kind


@dataclass(frozen=True, slots=True)
class CausalAssertionAuthority:
    atom: CausalAtom
    source_sha256: str
    status: str = "WARRANTED"


def _clean(text: str) -> str:
    compact = " ".join(text.strip().split())
    return compact[:-1] if compact.endswith(".") else compact


def _atom(cause: str, effect: str, kind: Kind) -> CausalAtom:
    return CausalAtom(cause.casefold(), effect.casefold(), kind)


def _source_atom(text: str) -> CausalAtom:
    compact = _clean(text)

    patterns: tuple[tuple[str, Kind], ...] = (
        (r"(?P<cause>A|X) causes (?P<effect>B|Y)", Kind.CAUSES),
        (
            r"(?P<cause>A|X) contributes to (?P<effect>B|Y)",
            Kind.CONTRIBUTES_TO,
        ),
        (r"(?P<cause>A|X) prevents (?P<effect>B|Y)", Kind.PREVENTS),
        (
            r"(?P<cause>A|X) correlates with (?P<effect>B|Y)",
            Kind.CORRELATES_WITH,
        ),
        (r"(?P<cause>A|X) precedes (?P<effect>B|Y)", Kind.PRECEDES),
        (r"(?P<cause>A|X) co-occurs with (?P<effect>B|Y)", Kind.CO_OCCURS),
    )
    for pattern, kind in patterns:
        match = re.fullmatch(pattern, compact, re.IGNORECASE)
        if match is not None:
            return _atom(match.group("cause"), match.group("effect"), kind)

    passive_cause = re.fullmatch(
        r"(?P<effect>B) is caused by (?P<cause>A)",
        compact,
        re.IGNORECASE,
    )
    if passive_cause is not None:
        return _atom(
            passive_cause.group("cause"),
            passive_cause.group("effect"),
            Kind.CAUSES,
        )

    passive_prevent = re.fullmatch(
        r"(?P<effect>B) is prevented by (?P<cause>A)",
        compact,
        re.IGNORECASE,
    )
    if passive_prevent is not None:
        return _atom(
            passive_prevent.group("cause"),
            passive_prevent.group("effect"),
            Kind.PREVENTS,
        )

    contributing = re.fullmatch(
        r"(?P<cause>A) is a contributing factor to (?P<effect>B)",
        compact,
        re.IGNORECASE,
    )
    if contributing is not None:
        return _atom(
            contributing.group("cause"),
            contributing.group("effect"),
            Kind.CONTRIBUTES_TO,
        )

    before = re.fullmatch(
        r"(?P<cause>A) occurs before (?P<effect>B)",
        compact,
        re.IGNORECASE,
    )
    if before is not None:
        return _atom(
            before.group("cause"),
            before.group("effect"),
            Kind.PRECEDES,
        )

    together = re.fullmatch(
        r"(?P<cause>A) occurs together with (?P<effect>B)",
        compact,
        re.IGNORECASE,
    )
    if together is not None:
        return _atom(
            together.group("cause"),
            together.group("effect"),
            Kind.CO_OCCURS,
        )

    raise ValueError("explicit causal assertion not independently reconstructable")


def complete_and_warrant_causal_assertion(
    text: str,
    measured: CausalAtom,
) -> CausalAssertionAuthority:
    completed = _source_atom(text)
    if completed != measured:
        raise ValueError("measurement/source semantic mismatch")
    return CausalAssertionAuthority(
        atom=completed,
        source_sha256=hashlib.sha256(text.encode()).hexdigest(),
    )
