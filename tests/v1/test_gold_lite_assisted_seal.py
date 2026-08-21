"""Contracts for sealing assisted Gold Lite Rung 4 review exports."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.gold_lite_assisted_seal import (
    build_assisted_sealed_review,
    validate_assisted_review,
    validate_packet_against_sources,
)
from scripts.gold_lite_review import (
    AtomDecision,
    DecompositionDecision,
    ReviewExport,
    ReviewPacket,
)

from .test_gold_lite_review import FIXTURE_ROOT, _manifest, _packet, _selected


def _review(packet: ReviewPacket) -> ReviewExport:
    return ReviewExport(
        schema_version="gold-lite-review-v0.1",
        rehearsal_id=packet.rehearsal_id,
        packet_sha256=packet.packet_sha256,
        reviewer="Cameron + Codex-assisted",
        exported_at_utc="2026-07-15T00:35:05Z",
        decompositions=[
            DecompositionDecision(parent_id="clm-001", status="approved"),
        ],
        decisions=[
            AtomDecision(
                atom_id="atom-1",
                label="supports",
                confidence="sure",
                selected_passages=[_selected(packet)],
            ),
            AtomDecision(
                atom_id="atom-2",
                label="insufficient",
                confidence="unsure",
            ),
        ],
    )


def test_assisted_contract_requires_a_documented_escalation(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    review = _review(packet)

    with pytest.raises(ValueError, match="requires documented needs_revision escalations"):
        validate_assisted_review(packet, review)


def _mixed_packet(packet: ReviewPacket) -> ReviewPacket:
    first_parent = packet.parents[0]
    escalated_parent = first_parent.model_copy(
        update={
            "parent_id": "clm-002",
            "atoms": [first_parent.atoms[0].model_copy(update={"atom_id": "atom-3"})],
        }
    )
    return packet.model_copy(update={"parents": [first_parent, escalated_parent]})


def test_assisted_contract_preserves_escalation_and_second_review_queue(tmp_path: Path) -> None:
    packet = _mixed_packet(_packet(tmp_path))
    review = _review(packet).model_copy(
        update={
            "decompositions": [
                DecompositionDecision(parent_id="clm-001", status="approved"),
                DecompositionDecision(
                    parent_id="clm-002",
                    status="needs_revision",
                    note="Needs a wider source boundary.",
                ),
            ],
        }
    )

    assisted = validate_assisted_review(packet, review)
    sealed = build_assisted_sealed_review(
        packet,
        review,
        assisted,
        review_sha256="0" * 64,
    )

    assert assisted["approved_parent_ids"] == ["clm-001"]
    assert sealed["adjudication_status"] == "completed_with_documented_escalations"
    assert sealed["legacy_complete_mode_green"] is False
    assert sealed["counts"]["approved_decompositions"] == 1
    assert sealed["counts"]["documented_needs_revision_escalations"] == 1
    assert sealed["counts"]["supports"] == 1
    assert sealed["counts"]["insufficient"] == 1
    assert sealed["second_review_atom_ids"] == ["atom-2"]
    assert "decompositions still need revision" in sealed["legacy_complete_mode_error"]


def test_assisted_contract_rejects_undocumented_escalation(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    review = _review(packet).model_copy(
        update={
            "decompositions": [DecompositionDecision(parent_id="clm-001", status="needs_revision")],
            "decisions": [],
        }
    )

    with pytest.raises(ValueError, match="needs_revision decompositions require notes"):
        validate_assisted_review(packet, review)


def test_assisted_contract_rejects_atoms_under_escalated_parents(tmp_path: Path) -> None:
    packet = _mixed_packet(_packet(tmp_path))
    selected = _selected(packet)
    review = _review(packet).model_copy(
        update={
            "decompositions": [
                DecompositionDecision(parent_id="clm-001", status="approved"),
                DecompositionDecision(
                    parent_id="clm-002",
                    status="needs_revision",
                    note="Needs a wider source boundary.",
                ),
            ],
            "decisions": [
                AtomDecision(
                    atom_id="atom-3",
                    label="supports",
                    confidence="sure",
                    selected_passages=[selected],
                )
            ],
        }
    )

    with pytest.raises(ValueError, match="requires approved decomposition"):
        validate_assisted_review(packet, review)


def test_assisted_contract_rebuilds_packet_from_canonical_sources(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    validate_packet_against_sources(
        packet,
        _manifest(),
        FIXTURE_ROOT,
        deviations_dir=tmp_path / "canonical-deviations",
    )

    altered = packet.model_copy(update={"label": "changed after review"})
    with pytest.raises(ValueError, match="fresh build from the manifest"):
        validate_packet_against_sources(
            altered,
            _manifest(),
            FIXTURE_ROOT,
            deviations_dir=tmp_path / "altered-deviations",
        )
