"""Tests for the deterministic Simple Logic Gold draft constructor."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

import pytest
import yaml

from scripts.simple_logic_gold import (
    derive_gold,
    freeze_approved_draft,
    load_manifest,
    render_review_cards,
    render_review_html,
    validate_manifest,
    write_draft_artifacts,
    write_frozen_artifact,
)


def _manifest() -> dict[str, object]:
    worlds: list[dict[str, object]] = []
    for number, relation in enumerate(
        [
            "supports",
            "supports",
            "refutes",
            "refutes",
            "insufficient",
            "insufficient",
            "retrieval_gap",
            "retrieval_gap",
        ],
        start=1,
    ):
        facts = [{"fact_id": "support", "text": "The stated supporting fact is present."}]
        atom: dict[str, object] = {
            "atom_id": f"a-{number}",
            "claim": "A plain claim.",
            "support_fact_ids": ["support"] if relation == "supports" else [],
            "contradicting_fact_ids": ["support"] if relation == "refutes" else [],
        }
        if relation == "retrieval_gap":
            atom["missing_material_id"] = "named-record"
            atom["missing_material_description"] = "The named record needed for this claim."
        worlds.append(
            {
                "base_case_id": f"case-{number}",
                "logic_family": "fixture",
                "source_boundary": "named_missing_material"
                if relation == "retrieval_gap"
                else "bounded",
                "source_boundary_note": "Explicit fixture boundary.",
                "plain_claim": "A plain claim.",
                "operator": "single",
                "facts": facts,
                "atoms": [atom],
            }
        )
    for number, verdict_relations in enumerate(
        [
            ["supports", "insufficient"],
            ["supports", "insufficient"],
            ["supports", "retrieval_gap"],
            ["supports", "retrieval_gap"],
        ],
        start=9,
    ):
        atoms: list[dict[str, object]] = []
        for atom_number, relation in enumerate(verdict_relations, start=1):
            atom = {
                "atom_id": f"a-{number}-{atom_number}",
                "claim": "A plain atom.",
                "support_fact_ids": ["support"] if relation == "supports" else [],
                "contradicting_fact_ids": [],
            }
            if relation == "retrieval_gap":
                atom["missing_material_id"] = "named-record"
                atom["missing_material_description"] = "The named record needed for this claim."
            atoms.append(atom)
        worlds.append(
            {
                "base_case_id": f"case-{number}",
                "logic_family": "fixture",
                "source_boundary": "named_missing_material"
                if "retrieval_gap" in verdict_relations
                else "bounded",
                "source_boundary_note": "Explicit fixture boundary.",
                "plain_claim": "A plain all-of claim.",
                "operator": "all_of",
                "facts": [{"fact_id": "support", "text": "The stated supporting fact is present."}],
                "atoms": atoms,
            }
        )
    return {
        "schema_version": "simple-logic-gold-worlds-v0.1",
        "approval_status": "draft_pending_cameron_approval",
        "version": "v0.1-draft-fixture",
        "worlds": worlds,
    }


def test_derivation_is_repeatable_and_covers_all_contract_outcomes() -> None:
    manifest = _manifest()
    validate_manifest(manifest)

    first = derive_gold(manifest, manifest_sha256="sha256:" + "a" * 64)
    second = derive_gold(manifest, manifest_sha256="sha256:" + "a" * 64)

    assert first == second
    assert first["world_count"] == 12
    assert all(count >= 2 for count in first["atom_relation_counts"].values())
    assert all(count >= 2 for count in first["parent_verdict_counts"].values())
    assert "CAL" not in str(first)


def test_manifest_rejects_named_missing_material_outside_declared_boundary() -> None:
    manifest = _manifest()
    manifest["worlds"][6]["source_boundary"] = "bounded"  # type: ignore[index]

    with pytest.raises(ValueError, match="missing material requires named_missing_material"):
        validate_manifest(manifest)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda manifest: manifest["worlds"][0].pop("plain_claim"),
        lambda manifest: manifest["worlds"][0].update({"facts": ["not-a-mapping"]}),
        lambda manifest: manifest["worlds"][0]["atoms"][0].update({"atom_id": ""}),
        lambda manifest: manifest["worlds"][0]["atoms"][0].update({"support_fact_ids": [""]}),
    ],
)
def test_manifest_rejects_missing_or_malformed_construction_fields(mutate: object) -> None:
    manifest = _manifest()
    mutate(manifest)  # type: ignore[operator]

    with pytest.raises(ValueError):
        validate_manifest(manifest)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda manifest: manifest["worlds"][0]["atoms"][0].update(
            {"contradicting_fact_ids": ["support"]}
        ),
        lambda manifest: manifest["worlds"][6]["atoms"][0].update(
            {"support_fact_ids": ["support"]}
        ),
        lambda manifest: manifest["worlds"][6]["atoms"][0].pop("missing_material_description"),
    ],
)
def test_manifest_rejects_ambiguous_or_opaque_atom_routes(mutate: object) -> None:
    manifest = _manifest()
    mutate(manifest)  # type: ignore[operator]

    with pytest.raises(ValueError):
        validate_manifest(manifest)


def test_manifest_rejects_insufficient_coverage() -> None:
    manifest = copy.deepcopy(_manifest())
    for world_index, atom_index in [(6, 0), (7, 0), (10, 1)]:
        manifest["worlds"][world_index]["atoms"][atom_index].pop("missing_material_id")  # type: ignore[index]
        manifest["worlds"][world_index]["atoms"][atom_index].pop(  # type: ignore[index]
            "missing_material_description"
        )

    with pytest.raises(ValueError, match="every atom relation must appear at least twice"):
        derive_gold(manifest, manifest_sha256="sha256:" + "a" * 64)


def test_scoped_counterexample_derives_refutes_not_insufficient() -> None:
    manifest = _manifest()
    manifest["worlds"][2]["atoms"][0]["scope_fact_ids"] = ["support"]  # type: ignore[index]

    derived = derive_gold(manifest, manifest_sha256="sha256:" + "a" * 64)
    assert derived["cases"][2]["atoms"][0]["relation"] == "refutes"


def test_overlay_composition_preserves_scoped_routes_and_canonical_hash(tmp_path: Path) -> None:
    base = _manifest()
    base["worlds"][0]["atoms"][0]["scope_fact_ids"] = ["support"]  # type: ignore[index]
    base["worlds"][2]["atoms"][0]["scope_fact_ids"] = ["support"]  # type: ignore[index]
    base_path = tmp_path / "base.yaml"
    base_path.write_text(yaml.safe_dump(base, sort_keys=False), encoding="utf-8")
    revision_path = tmp_path / "revision.yaml"
    revision_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": "simple-logic-gold-worlds-v0.1",
                "approval_status": "draft_pending_cameron_approval",
                "version": "v0.1-draft-overlay",
                "base_manifest": "base.yaml",
                "world_overrides": {"case-1": {"plain_claim": "Overlay claim."}},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    child_path = tmp_path / "child.yaml"
    child_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": "simple-logic-gold-worlds-v0.1",
                "approval_status": "draft_pending_cameron_approval",
                "version": "v0.1-draft-child",
                "base_manifest": "revision.yaml",
                "world_overrides": {"case-2": {"plain_claim": "Child overlay claim."}},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    manifest = load_manifest(child_path)
    canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    manifest_hash = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    derived = derive_gold(manifest, manifest_sha256=manifest_hash)
    by_id = {case["base_case_id"]: case for case in derived["cases"]}

    assert manifest["version"] == "v0.1-draft-child"
    assert manifest["worlds"][0]["plain_claim"] == "Overlay claim."
    assert manifest["worlds"][1]["plain_claim"] == "Child overlay claim."
    assert by_id["case-1"]["atoms"][0]["relation"] == "supports"
    assert by_id["case-3"]["atoms"][0]["relation"] == "refutes"
    assert derived["manifest_sha256"] == manifest_hash
    assert (
        "# Simple Logic Gold v0.1-draft-child — Cameron construction review"
        in render_review_cards(derived)
    )
    assert "Simple Logic Gold v0.1-draft-child" in render_review_html(derived)


def test_overlay_controls_fail_closed_without_safe_relative_base(tmp_path: Path) -> None:
    no_base = tmp_path / "no-base.yaml"
    no_base.write_text(
        yaml.safe_dump({**_manifest(), "world_overrides": {"case-1": {}}}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="world_overrides requires base_manifest"):
        load_manifest(no_base)

    absolute = tmp_path / "absolute.yaml"
    absolute.write_text(
        yaml.safe_dump({"base_manifest": "/tmp/worlds.yaml", "world_overrides": {}}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="base_manifest must be relative"):
        load_manifest(absolute)


def test_review_cards_make_the_construction_decision_visible() -> None:
    derived = derive_gold(_manifest(), manifest_sha256="sha256:" + "a" * 64)
    cards = render_review_cards(derived)
    reviewer_html = render_review_html(derived)

    assert "Approve or revise each explicit world" in cards
    assert "not a CAL run" in cards
    assert "# Simple Logic Gold v0.1-draft-fixture — Cameron construction review" in cards
    assert "Download checkpoint" in reviewer_html
    radio_names = re.findall(r'<input type="radio" name="([^"]+)"', reviewer_html)
    assert len(radio_names) == 24
    assert len(set(radio_names)) == 12
    assert "getElementsByName" in reviewer_html
    assert "x.checked=x.value===s[id]" in reviewer_html
    assert "Object.fromEntries" not in reviewer_html
    assert "!reviewer" in reviewer_html
    assert "draft_checkpoint_not_freeze" in reviewer_html
    assert "DEV construction checkpoint; not validation or gate evidence" in reviewer_html
    assert reviewer_html.index("The stated supporting fact is present.") < reviewer_html.index(
        "<details>"
    )
    assert "value.trim()||null" in reviewer_html
    assert "base.manifest_version+'-construction-review-checkpoint.json'" in reviewer_html
    assert "http://" not in reviewer_html
    assert "https://" not in reviewer_html
    assert "<script src=" not in reviewer_html


def test_reviewer_html_escapes_hostile_manifest_text() -> None:
    manifest = _manifest()
    manifest["worlds"][0]["plain_claim"] = "<script>alert('unsafe')</script>"  # type: ignore[index]
    manifest["worlds"][0]["facts"][0]["text"] = "A & B < C"  # type: ignore[index]
    html = render_review_html(derive_gold(manifest, manifest_sha256="sha256:" + "a" * 64))

    assert "&lt;script&gt;alert(&#x27;unsafe&#x27;)&lt;/script&gt;" in html
    assert "A &amp; B &lt; C" in html
    assert "<script>alert" not in html


def test_draft_artifact_writes_are_repeatable_and_refuse_drift(tmp_path: Path) -> None:
    manifest_path = tmp_path / "worlds.yaml"
    manifest_path.write_text(yaml.safe_dump(_manifest(), sort_keys=False), encoding="utf-8")
    out_dir = tmp_path / "out"

    first = write_draft_artifacts(manifest_path, out_dir)
    before = {path.name: path.read_bytes() for path in out_dir.iterdir()}
    second = write_draft_artifacts(manifest_path, out_dir)
    after = {path.name: path.read_bytes() for path in out_dir.iterdir()}

    assert first == second
    assert before == after
    changed = _manifest()
    changed["worlds"][0]["plain_claim"] = "Changed after review surface creation."
    manifest_path.write_text(yaml.safe_dump(changed, sort_keys=False), encoding="utf-8")
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        write_draft_artifacts(manifest_path, out_dir)


def test_freeze_requires_exact_cameron_approval_and_fresh_rebuild(tmp_path: Path) -> None:
    manifest_path = tmp_path / "worlds.yaml"
    manifest_path.write_text(yaml.safe_dump(_manifest(), sort_keys=False), encoding="utf-8")
    draft_dir = tmp_path / "draft"
    derived = write_draft_artifacts(manifest_path, draft_dir)
    checkpoint = {
        "schema_version": "simple-logic-gold-construction-review-v0.1",
        "status": "draft_checkpoint_not_freeze",
        "reviewer": "Cameron",
        "exported_at_utc": "2026-07-15T12:00:00Z",
        "manifest_version": derived["manifest_version"],
        "manifest_sha256": derived["manifest_sha256"],
        "derived_gold_sha256": derived["derived_gold_sha256"],
        "decisions": [
            {"base_case_id": case["base_case_id"], "decision": "approve", "note": None}
            for case in derived["cases"]
        ],
    }
    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
    frozen = freeze_approved_draft(
        manifest_path,
        draft_dir / "derived-gold.json",
        checkpoint_path,
        freeze_version="v0.1-frozen-fixture",
        freeze_identifier="simple-logic-gold-v0.1-frozen-fixture",
    )

    assert frozen["status"] == "frozen_approved_dev_not_validation_or_gate_evidence"
    assert frozen["freeze_version"] == "v0.1-frozen-fixture"
    assert frozen["freeze_identifier"] == "simple-logic-gold-v0.1-frozen-fixture"
    assert frozen["approval"] == {"expected_case_count": 12, "approved": 12}
    assert frozen["world_count"] == 12
    assert frozen["atom_relation_counts"] == derived["atom_relation_counts"]
    assert frozen["parent_verdict_counts"] == derived["parent_verdict_counts"]
    out = tmp_path / "frozen.json"
    write_frozen_artifact(
        manifest_path,
        draft_dir / "derived-gold.json",
        checkpoint_path,
        out,
        freeze_version="v0.1-frozen-fixture",
        freeze_identifier="simple-logic-gold-v0.1-frozen-fixture",
    )
    write_frozen_artifact(
        manifest_path,
        draft_dir / "derived-gold.json",
        checkpoint_path,
        out,
        freeze_version="v0.1-frozen-fixture",
        freeze_identifier="simple-logic-gold-v0.1-frozen-fixture",
    )


@pytest.mark.parametrize(
    "mutate",
    [
        lambda checkpoint: checkpoint.update({"reviewer": "not-Cameron"}),
        lambda checkpoint: checkpoint.update({"status": "frozen"}),
        lambda checkpoint: checkpoint["decisions"].pop(),
        lambda checkpoint: checkpoint["decisions"][0].update({"decision": "revise"}),
        lambda checkpoint: checkpoint.update({"exported_at_utc": "   "}),
    ],
)
def test_freeze_rejects_invalid_checkpoint(tmp_path: Path, mutate: object) -> None:
    manifest_path = tmp_path / "worlds.yaml"
    manifest_path.write_text(yaml.safe_dump(_manifest(), sort_keys=False), encoding="utf-8")
    draft_dir = tmp_path / "draft"
    derived = write_draft_artifacts(manifest_path, draft_dir)
    checkpoint = {
        "schema_version": "simple-logic-gold-construction-review-v0.1",
        "status": "draft_checkpoint_not_freeze",
        "reviewer": "Cameron",
        "exported_at_utc": "2026-07-15T12:00:00Z",
        "manifest_version": derived["manifest_version"],
        "manifest_sha256": derived["manifest_sha256"],
        "derived_gold_sha256": derived["derived_gold_sha256"],
        "decisions": [
            {"base_case_id": case["base_case_id"], "decision": "approve", "note": None}
            for case in derived["cases"]
        ],
    }
    mutate(checkpoint)  # type: ignore[operator]
    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")

    with pytest.raises(ValueError):
        freeze_approved_draft(
            manifest_path,
            draft_dir / "derived-gold.json",
            checkpoint_path,
            freeze_version="v0.1-frozen-fixture",
            freeze_identifier="simple-logic-gold-v0.1-frozen-fixture",
        )


def test_freeze_hashes_raw_checkpoint_bytes_without_newline_translation(tmp_path: Path) -> None:
    manifest_path = tmp_path / "worlds.yaml"
    manifest_path.write_text(yaml.safe_dump(_manifest(), sort_keys=False), encoding="utf-8")
    draft_dir = tmp_path / "draft"
    derived = write_draft_artifacts(manifest_path, draft_dir)
    checkpoint = {
        "schema_version": "simple-logic-gold-construction-review-v0.1",
        "status": "draft_checkpoint_not_freeze",
        "reviewer": "Cameron",
        "exported_at_utc": "2026-07-15T12:00:00Z",
        "manifest_version": derived["manifest_version"],
        "manifest_sha256": derived["manifest_sha256"],
        "derived_gold_sha256": derived["derived_gold_sha256"],
        "decisions": [
            {"base_case_id": case["base_case_id"], "decision": "approve", "note": None}
            for case in derived["cases"]
        ],
    }
    raw_checkpoint = json.dumps(checkpoint, indent=2).replace("\n", "\r\n").encode() + b"\r\n\t "
    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint_path.write_bytes(raw_checkpoint)

    frozen = freeze_approved_draft(
        manifest_path,
        draft_dir / "derived-gold.json",
        checkpoint_path,
        freeze_version="v0.1-frozen-fixture",
        freeze_identifier="simple-logic-gold-v0.1-frozen-fixture",
    )

    expected_hash = f"sha256:{hashlib.sha256(raw_checkpoint).hexdigest()}"
    assert frozen["source_checkpoint_sha256"] == expected_hash
