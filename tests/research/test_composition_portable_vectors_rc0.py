from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from research.composition_provenance_carrier_rc0.apparatus import (
    CompositionRequest,
    Relation,
)
from research.composition_provenance_carrier_rc0.candidate import bind_composition

ROOT = Path(__file__).resolve().parents[2]
VECTORS = ROOT / "research" / "composition_portable_vectors_rc0" / "vectors.json"
EXPECTED_BYTES_SHA256 = "11818e585780ff70b5bf00fe519463fb487dba9d191abb7810946ad43afebf39"


def test_vector_bytes_are_frozen() -> None:
    assert hashlib.sha256(VECTORS.read_bytes()).hexdigest() == EXPECTED_BYTES_SHA256


def test_frozen_vectors_match_exact_qualified_carrier() -> None:
    fixture = json.loads(VECTORS.read_text())
    assert fixture["canonicalization"]["profile"] == "CAL-CANONICAL-JSON-BOUNDED-1"

    for vector in fixture["vectors"]:
        raw = vector["request"]
        request = CompositionRequest(
            module_id=raw["module_id"],
            relation=Relation(raw["relation"]),
            input_authority_ids=tuple(raw["input_authority_ids"]),
            semantic_input=raw["semantic_input"],
            modifier_state=raw["modifier_state"],
            query=raw["query"],
        )
        observed = asdict(bind_composition(request))
        observed["relation"] = observed["relation"].value
        observed["input_authority_ids"] = list(observed["input_authority_ids"])
        assert observed == vector["expected_receipt"], vector["vector_id"]
