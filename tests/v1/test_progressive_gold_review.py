"""Contract tests for the progressive human-gold Rung 1 reviewer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.gold_lite_review import SelectedPassage
from scripts.progressive_gold_review import (
    ProgressiveDecision,
    ProgressiveManifest,
    ProgressiveReview,
    _packet_hash,
    build_review_packet,
    load_review_packet,
    render_review_html,
    validate_packet_against_sources,
    validate_review_export,
    write_reviewer_artifacts,
)

FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "cb"


def _manifest() -> ProgressiveManifest:
    return ProgressiveManifest.model_validate(
        {
            "schema_version": "progressive-gold-manifest-v0.1",
            "ladder_id": "progressive-gold-test",
            "rung_id": "rung-01-direct-support",
            "label": "DEV positive control; not validation",
            "selection": {
                "method": "fixed-positive-control-v0.1",
                "source_claim_count": 1,
                "claim_ids": ["clm-001"],
            },
        }
    )


def _packet(tmp_path: Path):
    return build_review_packet(
        _manifest(),
        FIXTURE_ROOT,
        deviations_dir=tmp_path / "deviations",
    )


def _selected(packet) -> SelectedPassage:
    candidate = packet.items[0].candidates[0]
    return SelectedPassage(
        candidate_id=candidate.candidate_id,
        source_id=candidate.source_id,
        passage_id=candidate.passage_id,
        passage_hash=candidate.passage_hash,
    )


def _review(packet, *decisions: ProgressiveDecision) -> ProgressiveReview:
    return ProgressiveReview(
        schema_version="progressive-gold-review-v0.1",
        ladder_id=packet.ladder_id,
        rung_id=packet.rung_id,
        packet_sha256=packet.packet_sha256,
        reviewer="reviewer-1",
        exported_at_utc="2026-07-12T12:00:00Z",
        decisions=list(decisions),
    )


def test_packet_is_fixed_blinded_and_hash_bound(tmp_path: Path) -> None:
    first = _packet(tmp_path)
    second = _packet(tmp_path)

    assert first == second
    assert [item.claim_id for item in first.items] == ["clm-001"]
    assert first.packet_sha256.startswith("sha256:")
    serialized = json.dumps(first.model_dump(mode="json"), sort_keys=True)
    for forbidden in (
        '"workflow_condition"',
        '"scaffold_support_status"',
        '"source_trust_level"',
        '"evidence_role"',
        '"audit"',
        '"model"',
    ):
        assert forbidden not in serialized


def test_packet_hash_drift_fails_closed(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    raw = packet.model_dump(mode="json")
    raw["items"][0]["claim_text"] = "Changed after packet seal."
    path = tmp_path / "packet.json"
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ValueError, match="packet hash drift"):
        load_review_packet(path)


def test_rehashed_packet_still_fails_canonical_source_validation(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    raw = packet.model_dump(mode="json")
    raw["items"][0]["claim_text"] = "Changed and deliberately re-hashed."
    payload = dict(raw)
    payload.pop("packet_sha256")
    raw["packet_sha256"] = _packet_hash(payload)
    path = tmp_path / "rehashed-packet.json"
    path.write_text(json.dumps(raw), encoding="utf-8")

    rehashed = load_review_packet(path)
    with pytest.raises(ValueError, match="fresh build from the manifest"):
        validate_packet_against_sources(
            rehashed,
            _manifest(),
            FIXTURE_ROOT,
            deviations_dir=tmp_path / "canonical-deviations",
        )


def test_decision_path_prevents_forced_relation() -> None:
    needs_split = ProgressiveDecision(claim_id="clm-001", atomicity="needs_split")
    assert needs_split.direct_support is None

    with pytest.raises(ValidationError, match="atomic items require"):
        ProgressiveDecision(claim_id="clm-001", atomicity="yes")
    with pytest.raises(ValidationError, match="direct support requires"):
        ProgressiveDecision(
            claim_id="clm-001",
            atomicity="yes",
            direct_support="yes",
        )
    with pytest.raises(ValidationError, match="cannot record direct support"):
        ProgressiveDecision(
            claim_id="clm-001",
            atomicity="unsure",
            direct_support="no",
        )


def test_complete_direct_support_derives_only_supports(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    review = _review(
        packet,
        ProgressiveDecision(
            claim_id="clm-001",
            atomicity="yes",
            direct_support="yes",
            reviewed_candidate_ids=[_selected(packet).candidate_id],
            selected_passages=[_selected(packet)],
        ),
    )

    results = validate_review_export(packet, review, require_complete=True)

    assert len(results) == 1
    assert results[0].outcome == "supports"
    assert results[0].derived_relation == "supports"


@pytest.mark.parametrize(
    ("decision", "outcome"),
    [
        (ProgressiveDecision(claim_id="clm-001", atomicity="needs_split"), "escalate_atomicity"),
        (
            ProgressiveDecision(claim_id="clm-001", atomicity="yes", direct_support="no"),
            "escalate_relation",
        ),
        (ProgressiveDecision(claim_id="clm-001", atomicity="unsure"), "second_review"),
        (
            ProgressiveDecision(claim_id="clm-001", atomicity="yes", direct_support="unsure"),
            "second_review",
        ),
    ],
)
def test_non_support_answers_escalate_without_derived_relation(
    decision: ProgressiveDecision,
    outcome: str,
    tmp_path: Path,
) -> None:
    packet = _packet(tmp_path)
    if decision.direct_support == "no":
        decision = ProgressiveDecision(
            claim_id=decision.claim_id,
            atomicity=decision.atomicity,
            direct_support=decision.direct_support,
            reviewed_candidate_ids=packet.items[0].candidate_ids,
        )
    results = validate_review_export(
        packet,
        _review(packet, decision),
        require_complete=True,
    )

    assert results[0].outcome == outcome
    assert results[0].derived_relation is None


def test_direct_support_no_requires_every_candidate_reviewed(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    decision = ProgressiveDecision(
        claim_id="clm-001",
        atomicity="yes",
        direct_support="no",
        reviewed_candidate_ids=packet.items[0].candidate_ids[:-1],
    )

    with pytest.raises(ValueError, match="requires reviewing every candidate"):
        validate_review_export(
            packet,
            _review(packet, decision),
            require_complete=True,
        )


def test_selected_passage_must_have_been_reviewed(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    decision = ProgressiveDecision(
        claim_id="clm-001",
        atomicity="yes",
        direct_support="yes",
        selected_passages=[_selected(packet)],
    )

    with pytest.raises(ValueError, match="was not recorded as reviewed"):
        validate_review_export(
            packet,
            _review(packet, decision),
            require_complete=True,
        )


def test_selected_passage_provenance_drift_fails(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    selected = _selected(packet).model_copy(update={"passage_hash": "sha256:" + "0" * 64})
    review = _review(
        packet,
        ProgressiveDecision(
            claim_id="clm-001",
            atomicity="yes",
            direct_support="yes",
            reviewed_candidate_ids=[selected.candidate_id],
            selected_passages=[selected],
        ),
    )

    with pytest.raises(ValueError, match="provenance/hash drift"):
        validate_review_export(packet, review, require_complete=True)


def test_incomplete_checkpoint_is_not_complete_reference(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    review = _review(packet)

    results = validate_review_export(packet, review, require_complete=False)
    assert results[0].outcome == "second_review"
    with pytest.raises(ValueError, match="missing progressive-gold decisions"):
        validate_review_export(packet, review, require_complete=True)


def test_html_and_artifacts_are_self_contained_and_byte_stable(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    html = render_review_html(packet)

    assert "__PROGRESSIVE_GOLD_PACKET_JSON__" not in html
    assert packet.packet_sha256 in html
    assert "one checkable idea" in html
    assert "No — none match" in html
    assert "reviewed_candidate_ids" in html
    assert "localStorage" in html

    out = tmp_path / "out"
    manifest_path = tmp_path / "manifest.yaml"
    manifest_path.write_text("fixture", encoding="utf-8")
    write_reviewer_artifacts(packet, out, manifest_path=manifest_path)
    before = {path.name: path.read_bytes() for path in out.iterdir() if path.is_file()}
    write_reviewer_artifacts(packet, out, manifest_path=manifest_path)
    after = {path.name: path.read_bytes() for path in out.iterdir() if path.is_file()}

    assert before == after
    assert set(before) == {"README.md", "review-packet.json", "review.html"}
