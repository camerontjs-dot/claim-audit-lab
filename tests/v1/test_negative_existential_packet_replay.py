"""Replay contract for the separately frozen D5 admitted-evidence packet."""

from pathlib import Path

from scripts.negative_existential_packet_replay import replay

_PROJECT = Path(__file__).resolve().parents[2]
_EVIDENCE = _PROJECT.parent / "outputs" / "2026-08-07-negative-existential-packet"


def test_frozen_d5_packet_replays_expected_state_movements(tmp_path: Path) -> None:
    report = replay(_EVIDENCE / "packet.json", _EVIDENCE / "receipts.json", tmp_path)
    rows = {row["claim_id"]: row for row in report["rows"]}

    assert report["model_inference"] is False
    assert rows["d5-supported"]["operator_state"] == "support_only"
    assert rows["d5-refuted"]["operator_state"] == "refutation_only"
    assert rows["d5-refuted"]["operator_shadow_verdict"] == "contradicted"
    assert rows["d5-insufficient"]["operator_state"] == "read_silent"
    assert rows["ordinary-refuted"]["operator_state"] == "refutation_only"
    assert rows["d5-ambiguous"]["operator_state"] == "read_silent"


def test_frozen_d5_packet_hashes_match_manifest(tmp_path: Path) -> None:
    import json

    manifest = json.loads((_EVIDENCE / "manifest.json").read_text(encoding="utf-8"))
    report = replay(_EVIDENCE / "packet.json", _EVIDENCE / "receipts.json", tmp_path)
    assert "sha256:" + report["packet_sha256"] == manifest["files"]["packet.json"]
    assert "sha256:" + report["receipts_sha256"] == manifest["files"]["receipts.json"]
