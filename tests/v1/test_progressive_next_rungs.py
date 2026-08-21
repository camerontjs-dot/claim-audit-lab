"""Contract tests for progressive human-gold Rung 2 and Rung 3 reviewers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.gold_lite_review import SelectedPassage
from scripts.progressive_next_rungs import (
    ProgressiveDecision,
    ProgressiveManifest,
    ProgressiveReview,
    _packet_hash,
    build_review_packet,
    build_sealed_review,
    load_review_packet,
    render_review_html,
    validate_packet_against_sources,
    validate_review_export,
    write_reviewer_artifacts,
)

FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "cb"


def _manifest(
    *,
    rung_id: str = "rung-02-atomic-polarity",
    availability: str = "not_applicable",
    missing_material_note: str | None = None,
    candidate_count: int = 1,
) -> ProgressiveManifest:
    return ProgressiveManifest.model_validate(
        {
            "schema_version": "progressive-next-rungs-manifest-v0.1",
            "ladder_id": "progressive-next-test",
            "rung_id": rung_id,
            "label": "Controlled DEV teaching fixture; not validation",
            "selection_method": "fixed-controlled-teaching-v0.1",
            "source_claim_count": 1,
            "candidate_count": candidate_count,
            "items": [
                {
                    "item_id": "item-001",
                    "source_claim_id": "clm-001",
                    "claim_text": "The submission package contains stability data.",
                    "availability": availability,
                    "missing_material_note": missing_material_note,
                }
            ],
        }
    )


def _packet(
    tmp_path: Path,
    *,
    rung_id: str = "rung-02-atomic-polarity",
    availability: str = "not_applicable",
    missing_material_note: str | None = None,
):
    manifest = _manifest(
        rung_id=rung_id,
        availability=availability,
        missing_material_note=missing_material_note,
    )
    return build_review_packet(
        manifest,
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
        schema_version="progressive-next-rungs-review-v0.1",
        ladder_id=packet.ladder_id,
        rung_id=packet.rung_id,
        packet_sha256=packet.packet_sha256,
        reviewer="reviewer-1",
        exported_at_utc="2026-07-14T12:00:00Z",
        decisions=list(decisions),
    )


def test_packet_is_deterministic_blinded_and_hash_bound(tmp_path: Path) -> None:
    first = _packet(tmp_path)
    second = _packet(tmp_path)

    assert first == second
    assert first.candidate_count == 1
    assert first.packet_sha256.startswith("sha256:")
    assert first.items[0].candidate_ids == ["src-001/pass-001"]
    assert "source_claim_id" not in first.items[0].model_fields_set

    serialized = json.dumps(first.model_dump(mode="json"), sort_keys=True)
    for forbidden in (
        '"workflow_condition"',
        '"scaffold_support_status"',
        '"source_trust_level"',
        '"evidence_role"',
        '"audit"',
        '"model"',
        '"expected"',
        '"target"',
    ):
        assert forbidden not in serialized


def test_manifest_enforces_rung_specific_availability() -> None:
    with pytest.raises(ValidationError, match="Rung 2 items must use"):
        _manifest(availability="none_identified")
    with pytest.raises(ValidationError, match="Rung 3 items require"):
        _manifest(rung_id="rung-03-bounded-sufficiency")
    with pytest.raises(ValidationError, match="requires a note"):
        _manifest(
            rung_id="rung-03-bounded-sufficiency",
            availability="specific_missing_material",
        )


def test_manifest_candidate_count_drift_fails_closed(tmp_path: Path) -> None:
    manifest = _manifest(candidate_count=2)

    with pytest.raises(ValueError, match="expected 2 canonical candidates"):
        build_review_packet(
            manifest,
            FIXTURE_ROOT,
            deviations_dir=tmp_path / "deviations",
        )


def test_packet_hash_drift_fails_closed(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    raw = packet.model_dump(mode="json")
    raw["items"][0]["claim_text"] = "Changed after packet seal."
    path = tmp_path / "packet.json"
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ValueError, match="packet hash drift"):
        load_review_packet(path)


def test_rehashed_packet_still_fails_canonical_source_validation(tmp_path: Path) -> None:
    manifest = _manifest()
    packet = build_review_packet(
        manifest,
        FIXTURE_ROOT,
        deviations_dir=tmp_path / "deviations",
    )
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
            manifest,
            FIXTURE_ROOT,
            deviations_dir=tmp_path / "canonical-deviations",
        )


@pytest.mark.parametrize("relation", ["supports", "refutes", "insufficient"])
def test_passage_relations_require_exactly_one_rationale(relation: str) -> None:
    with pytest.raises(ValidationError, match="requires one selected rationale passage"):
        ProgressiveDecision(item_id="item-001", relation=relation)


def test_retrieval_gap_binds_named_missing_source_not_visible_passage(
    tmp_path: Path,
) -> None:
    packet = _packet(
        tmp_path,
        rung_id="rung-03-bounded-sufficiency",
        availability="specific_missing_material",
        missing_material_note="The complete source PDF is absent from this packet.",
    )
    decision = ProgressiveDecision(
        item_id="item-001",
        relation="retrieval_gap",
        reviewed_candidate_ids=packet.items[0].candidate_ids,
    )

    results = validate_review_export(
        packet,
        _review(packet, decision),
        require_complete=True,
    )

    assert results[0].outcome == "retrieval_gap"
    assert "named missing material" in results[0].reason
    with pytest.raises(ValidationError, match="cannot select"):
        ProgressiveDecision(
            item_id="item-001",
            relation="retrieval_gap",
            selected_passages=[_selected(packet)],
        )


def test_direct_relation_requires_reviewed_exact_provenance(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    selected = _selected(packet)
    decision = ProgressiveDecision(
        item_id="item-001",
        relation="supports",
        reviewed_candidate_ids=[selected.candidate_id],
        selected_passages=[selected],
    )

    results = validate_review_export(
        packet,
        _review(packet, decision),
        require_complete=True,
    )
    assert results[0].derived_relation == "supports"

    unreviewed = decision.model_copy(update={"reviewed_candidate_ids": []})
    with pytest.raises(ValueError, match="was not recorded as reviewed"):
        validate_review_export(
            packet,
            _review(packet, unreviewed),
            require_complete=True,
        )

    drifted = selected.model_copy(update={"passage_hash": "sha256:" + "0" * 64})
    bad_hash = decision.model_copy(update={"selected_passages": [drifted]})
    with pytest.raises(ValueError, match="provenance/hash drift"):
        validate_review_export(
            packet,
            _review(packet, bad_hash),
            require_complete=True,
        )


def test_rung_2_neither_requires_every_candidate_and_escalates(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    decision = ProgressiveDecision(item_id="item-001", relation="neither")

    with pytest.raises(ValueError, match="requires reviewing every candidate"):
        validate_review_export(
            packet,
            _review(packet, decision),
            require_complete=True,
        )

    complete = decision.model_copy(update={"reviewed_candidate_ids": packet.items[0].candidate_ids})
    results = validate_review_export(
        packet,
        _review(packet, complete),
        require_complete=True,
    )
    assert results[0].outcome == "escalate_relation"
    assert results[0].derived_relation is None


@pytest.mark.parametrize("relation", ["insufficient", "retrieval_gap"])
def test_rung_2_rejects_sufficiency_relations(
    relation: str,
    tmp_path: Path,
) -> None:
    packet = _packet(tmp_path)
    selected = _selected(packet)
    selected_passages = [selected] if relation == "insufficient" else []
    decision = ProgressiveDecision(
        item_id="item-001",
        relation=relation,
        reviewed_candidate_ids=packet.items[0].candidate_ids,
        selected_passages=selected_passages,
    )

    with pytest.raises(ValueError, match="is not allowed"):
        validate_review_export(
            packet,
            _review(packet, decision),
            require_complete=True,
        )


def test_rung_3_insufficient_requires_all_candidates_and_no_named_gap(
    tmp_path: Path,
) -> None:
    packet = _packet(
        tmp_path,
        rung_id="rung-03-bounded-sufficiency",
        availability="none_identified",
    )
    selected = _selected(packet)
    decision = ProgressiveDecision(
        item_id="item-001",
        relation="insufficient",
        reviewed_candidate_ids=[],
        selected_passages=[selected],
    )
    with pytest.raises(ValueError, match="was not recorded as reviewed"):
        validate_review_export(
            packet,
            _review(packet, decision),
            require_complete=True,
        )

    complete = decision.model_copy(update={"reviewed_candidate_ids": packet.items[0].candidate_ids})
    results = validate_review_export(
        packet,
        _review(packet, complete),
        require_complete=True,
    )
    assert results[0].outcome == "insufficient"


def test_rung_3_retrieval_gap_requires_named_gap_and_all_candidates(
    tmp_path: Path,
) -> None:
    no_gap = _packet(
        tmp_path,
        rung_id="rung-03-bounded-sufficiency",
        availability="none_identified",
    )
    decision = ProgressiveDecision(
        item_id="item-001",
        relation="retrieval_gap",
        reviewed_candidate_ids=no_gap.items[0].candidate_ids,
    )
    with pytest.raises(ValueError, match="specifically identified missing material"):
        validate_review_export(
            no_gap,
            _review(no_gap, decision),
            require_complete=True,
        )

    named_gap = _packet(
        tmp_path,
        rung_id="rung-03-bounded-sufficiency",
        availability="specific_missing_material",
        missing_material_note="The complete source PDF is absent from this packet.",
    )
    with pytest.raises(ValueError, match="requires reviewing every candidate"):
        validate_review_export(
            named_gap,
            _review(
                named_gap,
                decision.model_copy(update={"reviewed_candidate_ids": []}),
            ),
            require_complete=True,
        )


def test_incomplete_checkpoint_cannot_be_sealed_as_complete(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    review = _review(packet)

    assert validate_review_export(packet, review, require_complete=False) == []
    with pytest.raises(ValueError, match="missing progressive-rung decisions"):
        validate_review_export(packet, review, require_complete=True)


def test_sealed_review_counts_relations_and_escalations(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    selected = _selected(packet)
    review = _review(
        packet,
        ProgressiveDecision(
            item_id="item-001",
            relation="refutes",
            reviewed_candidate_ids=[selected.candidate_id],
            selected_passages=[selected],
        ),
    )
    results = validate_review_export(packet, review, require_complete=True)

    sealed = build_sealed_review(
        packet,
        review,
        results,
        review_sha256="0" * 64,
        complete=True,
    )

    assert sealed["counts"] == {
        "items": 1,
        "decisions_recorded": 1,
        "supports": 0,
        "refutes": 1,
        "insufficient": 0,
        "retrieval_gap": 0,
        "escalations": 0,
    }


def test_html_and_artifacts_are_self_contained_and_byte_stable(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    html = render_review_html(packet)

    assert "__PROGRESSIVE_NEXT_PACKET_JSON__" not in html
    assert packet.packet_sha256 in html
    assert "Missing support is not refutation" in html
    assert "Neither unlocks after all five passages" in html
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
