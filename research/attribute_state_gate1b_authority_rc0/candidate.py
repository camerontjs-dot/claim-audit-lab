"""Independent source completion for bounded attribute-state Gate-1B RC0."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from research.attribute_state_measurement_machinery_rc1.cohort import StateAtom


@dataclass(frozen=True, slots=True)
class AttributeStateAuthority:
    atom: StateAtom
    source_sha256: str
    status: str = "WARRANTED"


_DECLARED = {
    ("batch", "status"): ("batch_status", True),
    ("device", "mode"): ("device_mode", True),
    ("record", "tag"): ("labels", False),
    ("system", "availability"): ("availability", True),
    ("other_batch", "status"): ("batch_status", True),
    ("document", "status"): ("document_status", True),
}


def _clean(text: str) -> str:
    compact = " ".join(text.strip().split())
    return compact[:-1] if compact.endswith(".") else compact


def _atom(entity: str, attribute: str, value: str) -> StateAtom:
    domain, functional = _DECLARED[(entity, attribute)]
    return StateAtom(entity, attribute, domain, value, functional)


def _source_atom(text: str) -> StateAtom:
    compact = _clean(text)

    direct = re.fullmatch(
        r"(?P<entity>Batch|Device|Record|System) "
        r"(?P<attribute>status|mode|tag|availability) is "
        r"(?P<value>[A-Za-z_-]+)",
        compact,
        re.IGNORECASE,
    )
    if direct is not None:
        key = (
            direct.group("entity").casefold(),
            direct.group("attribute").casefold(),
        )
        if key not in _DECLARED:
            raise ValueError("undeclared attribute")
        return _atom(key[0], key[1], direct.group("value").casefold())

    patterns: tuple[tuple[str, tuple[str, str, str]], ...] = (
        (r"The batch's status is released", ("batch", "status", "released")),
        (r"Batch status:\s*released", ("batch", "status", "released")),
        (r"The device is in standby mode", ("device", "mode", "standby")),
        (r"The batch remains held", ("batch", "status", "held")),
        (r"Device mode is maintenance", ("device", "mode", "maintenance")),
        (
            r"Other batch status is released",
            ("other_batch", "status", "released"),
        ),
        (
            r"Document status is released",
            ("document", "status", "released"),
        ),
    )
    for pattern, (entity, attribute, value) in patterns:
        if re.fullmatch(pattern, compact, re.IGNORECASE):
            return _atom(entity, attribute, value)

    raise ValueError("attribute-state source not independently reconstructable")


def complete_and_warrant_attribute_state(
    text: str,
    measured: StateAtom,
) -> AttributeStateAuthority:
    completed = _source_atom(text)
    if completed != measured:
        raise ValueError("measurement/source semantic mismatch")
    return AttributeStateAuthority(
        atom=completed,
        source_sha256=hashlib.sha256(text.encode()).hexdigest(),
    )
