from __future__ import annotations

import hashlib
import json

import pytest

from claim_audit_lab.cal_v1_candidate.prototype import (
    OUTPUT_SCHEMA,
    PROTOTYPE_PROFILE,
    SEMANTIC_IMPLEMENTATION_SHA,
    run_packet,
)


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return "sha256:" + _hex(value)


def _packet(*, evidence_text: str = "Women had a higher rate than Men.") -> dict[str, object]:
    return {
        "original_claim": "Women had a higher rate than Men.",
        "proposition": {
            "proposition_id": "claim-1",
            "text_sha256": _hex("Women had a higher rate than Men."),
            "semantic_family": "strict_comparison",
            "fields": {
                "lhs_entity": "Women",
                "rhs_entity": "Men",
                "comparison_direction": "MORE_THAN",
            },
        },
        "evidence_world": {
            "contract_b_version": "1.2.0",
            "bundle_id": "bundle-1",
            "bundle_hash": _tagged("bundle-1"),
            "aperture_observation": {
                "search_scope": {"corpus": "prototype-fixture"},
                "outcome": {"state": "unknown", "value": None},
                "limitations": [],
            },
            "admitted_passages": [
                {
                    "passage_id": "p1",
                    "source_id": "source-1",
                    "text": evidence_text,
                    "text_sha256": _tagged(evidence_text),
                    "source_sha256": _tagged("source-1"),
                }
            ],
        },
    }


def test_prototype_emits_pinned_identity_and_no_downstream_authority() -> None:
    packet = _packet()
    _, _, record = run_packet(packet, packet_sha256="sha256:" + "1" * 64)

    assert record["schema"] == OUTPUT_SCHEMA
    assert record["prototype_profile"] == PROTOTYPE_PROFILE
    assert record["semantic_implementation_sha"] == SEMANTIC_IMPLEMENTATION_SHA
    assert record["result"]["conclusion"] == "supported"
    assert record["contract_c_handoff"]["state"] == "not_emitted"
    assert record["authorization"] == {
        "state": "not_evaluated",
        "automatic_action_allowed": False,
    }


def test_prototype_is_deterministic_for_identical_packet() -> None:
    packet = _packet()
    first = run_packet(packet, packet_sha256="sha256:" + "2" * 64)[2]
    second = run_packet(packet, packet_sha256="sha256:" + "2" * 64)[2]
    assert first == second


def test_prototype_preserves_mixed_evidence_abstention() -> None:
    packet = _packet()
    second_text = "Women had a lower rate than Men."
    packet["evidence_world"]["admitted_passages"].append(
        {
            "passage_id": "p2",
            "source_id": "source-1",
            "text": second_text,
            "text_sha256": _tagged(second_text),
            "source_sha256": _tagged("source-1"),
        }
    )
    _, _, record = run_packet(packet, packet_sha256="sha256:" + "3" * 64)
    assert record["result"]["conclusion"] == "not_checkable"
    assert record["result"]["failure_code"] == "MIXED_RELATIONS"


def test_prototype_fails_closed_on_stale_passage_hash() -> None:
    packet = _packet()
    packet["evidence_world"]["admitted_passages"][0]["text"] = "tampered"
    with pytest.raises(ValueError, match="passage hash mismatch"):
        run_packet(packet, packet_sha256="sha256:" + "4" * 64)


def test_serialized_record_round_trip_is_stable() -> None:
    record = run_packet(_packet(), packet_sha256="sha256:" + "5" * 64)[2]
    encoded = json.dumps(record, sort_keys=True, separators=(",", ":"))
    assert json.loads(encoded) == record
