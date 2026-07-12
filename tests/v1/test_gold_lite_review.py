"""Fast contract tests for the DEV-only Gold Lite rehearsal tooling."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.gold_lite_review import (
    AtomDecision,
    DecompositionDecision,
    GoldLiteManifest,
    ReviewExport,
    SelectedPassage,
    aggregate_parent_result,
    build_review_packet,
    load_review_packet,
    render_review_html,
    validate_review_export,
    write_rehearsal_artifacts,
)

FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "cb"
BUNDLE_NAME = "evidence-bundle-minimal"


def _manifest() -> GoldLiteManifest:
    return GoldLiteManifest.model_validate(
        {
            "schema_version": "gold-lite-manifest-v0.1",
            "rehearsal_id": "gold-lite-test",
            "label": "DEV test; not validation",
            "selection": {
                "method": "sha256-lowest",
                "seed": "gold-lite-test-seed",
                "source_claim_count": 1,
                "sample_size": 1,
            },
            "initial_candidate_limit": 1,
            "parents": [
                {
                    "parent_id": "clm-001",
                    "bundle_dir": BUNDLE_NAME,
                    "source_claim_id": "clm-001",
                    "operator": "all_of",
                    "atoms": [
                        {"atom_id": "atom-1", "text": "The package needs stability data."},
                        {"atom_id": "atom-2", "text": "The data must support shelf life."},
                    ],
                }
            ],
        }
    )


def _packet(tmp_path: Path):
    return build_review_packet(
        _manifest(),
        FIXTURE_ROOT,
        deviations_dir=tmp_path / "deviations",
    )


def _selected(packet) -> SelectedPassage:
    candidate = packet.parents[0].candidates[0]
    return SelectedPassage(
        candidate_id=candidate.candidate_id,
        source_id=candidate.source_id,
        passage_id=candidate.passage_id,
        passage_hash=candidate.passage_hash,
    )


def _review(packet, *decisions: AtomDecision) -> ReviewExport:
    return ReviewExport(
        schema_version="gold-lite-review-v0.1",
        rehearsal_id=packet.rehearsal_id,
        packet_sha256=packet.packet_sha256,
        reviewer="reviewer-1",
        exported_at_utc="2026-07-11T12:00:00Z",
        decompositions=[DecompositionDecision(parent_id="clm-001", status="approved")],
        decisions=list(decisions),
    )


def test_packet_selection_is_deterministic_blinded_and_hash_bound(tmp_path: Path) -> None:
    first = _packet(tmp_path)
    second = _packet(tmp_path)

    assert first == second
    assert first.packet_sha256.startswith("sha256:")
    assert [parent.parent_id for parent in first.parents] == ["clm-001"]
    assert [atom.atom_id for atom in first.parents[0].atoms] == ["atom-1", "atom-2"]
    assert len(first.parents[0].candidates) == 1

    serialized = json.dumps(first.model_dump(mode="json"), sort_keys=True)
    for forbidden in (
        '"workflow_condition"',
        '"scaffold_support_status"',
        '"source_trust_level"',
        '"evidence_role"',
        '"audit"',
    ):
        assert forbidden not in serialized

    packet_path = tmp_path / "packet.json"
    packet_path.write_text(
        json.dumps(first.model_dump(mode="json"), sort_keys=True), encoding="utf-8"
    )
    assert load_review_packet(packet_path) == first


def test_packet_hash_drift_fails_closed(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    raw = packet.model_dump(mode="json")
    raw["parents"][0]["parent_text"] = "Changed after packet seal."
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ValueError, match="packet hash drift"):
        load_review_packet(packet_path)


def test_html_is_self_contained_and_artifacts_are_byte_stable(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    html = render_review_html(packet)

    assert "__GOLD_LITE_PACKET_JSON__" not in html
    assert packet.packet_sha256 in html
    assert "localStorage" in html
    assert "DEV usability rehearsal only" in html

    out = tmp_path / "out"
    manifest_path = tmp_path / "manifest.yaml"
    manifest_path.write_text("fixture", encoding="utf-8")
    write_rehearsal_artifacts(packet, out, manifest_path=manifest_path)
    before = {path.name: path.read_bytes() for path in out.iterdir() if path.is_file()}
    write_rehearsal_artifacts(packet, out, manifest_path=manifest_path)
    after = {path.name: path.read_bytes() for path in out.iterdir() if path.is_file()}

    assert before == after
    assert set(before) == {"README.md", "review-packet.json", "review.html"}


def test_complete_review_derives_partial_parent_and_preserves_uncertainty(
    tmp_path: Path,
) -> None:
    packet = _packet(tmp_path)
    review = _review(
        packet,
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
    )

    results = validate_review_export(packet, review, require_complete=True)

    assert len(results) == 1
    assert results[0].support_verdict == "partially_supported"
    assert results[0].atom_labels == ["supports", "insufficient"]
    assert results[0].needs_second_review is True


@pytest.mark.parametrize(
    ("labels", "expected"),
    [
        (("supports", "supports"), "supported"),
        (("supports", "refutes"), "contradicted"),
        (("insufficient", "insufficient"), "not_checkable"),
        (("supports", "retrieval_gap"), "pending"),
    ],
)
def test_all_of_parent_aggregation(labels, expected, tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    parent = packet.parents[0]
    decisions = {}
    for atom, label in zip(parent.atoms, labels, strict=True):
        selected = [_selected(packet)] if label in {"supports", "refutes"} else []
        decisions[atom.atom_id] = AtomDecision(
            atom_id=atom.atom_id,
            label=label,
            confidence="sure",
            selected_passages=selected,
        )

    result = aggregate_parent_result(
        parent,
        DecompositionDecision(parent_id=parent.parent_id, status="approved"),
        decisions,
    )

    assert result.support_verdict == expected
    assert result.needs_second_review is (expected == "pending")


def test_relation_labels_require_valid_rationale_shape(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    selected = _selected(packet)

    with pytest.raises(ValidationError, match="requires at least one selected passage"):
        AtomDecision(atom_id="atom-1", label="supports", confidence="sure")
    with pytest.raises(ValidationError, match="retrieval_gap cannot select"):
        AtomDecision(
            atom_id="atom-1",
            label="retrieval_gap",
            confidence="sure",
            selected_passages=[selected],
        )


def test_export_validation_rejects_hash_drift_and_unapproved_atoms(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    selected = _selected(packet).model_copy(update={"passage_hash": "sha256:" + "0" * 64})
    drifted = _review(
        packet,
        AtomDecision(
            atom_id="atom-1",
            label="supports",
            confidence="sure",
            selected_passages=[selected],
        ),
    )
    with pytest.raises(ValueError, match="provenance/hash drift"):
        validate_review_export(packet, drifted, require_complete=False)

    unapproved = drifted.model_copy(
        update={
            "decompositions": [
                DecompositionDecision(
                    parent_id="clm-001",
                    status="needs_revision",
                    note="Second atom changes the parent meaning.",
                )
            ],
            "decisions": [
                AtomDecision(
                    atom_id="atom-1",
                    label="supports",
                    confidence="sure",
                    selected_passages=[_selected(packet)],
                )
            ],
        }
    )
    with pytest.raises(ValueError, match="requires approved decomposition"):
        validate_review_export(packet, unapproved, require_complete=False)


def test_incomplete_checkpoint_is_reportable_but_not_complete(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    checkpoint = ReviewExport(
        schema_version="gold-lite-review-v0.1",
        rehearsal_id=packet.rehearsal_id,
        packet_sha256=packet.packet_sha256,
        reviewer="reviewer-1",
        exported_at_utc="2026-07-11T12:00:00Z",
    )

    results = validate_review_export(packet, checkpoint, require_complete=False)
    assert results[0].support_verdict == "pending"
    with pytest.raises(ValueError, match="missing decomposition decisions"):
        validate_review_export(packet, checkpoint, require_complete=True)


def test_manifest_rejects_operator_atom_mismatch() -> None:
    raw = _manifest().model_dump(mode="json")
    raw["parents"][0]["operator"] = "single"

    with pytest.raises(ValidationError, match="single parents require exactly one atom"):
        GoldLiteManifest.model_validate(raw)
