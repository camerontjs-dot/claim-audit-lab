"""Contract tests for the DEV-only Gold Lite Anthropic tier panel."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.anthropic_api_bridge import canonical_sha256, run_prepared_request
from scripts.gold_lite_model_panel import (
    BRIDGE_SCHEMA,
    DEV_LABEL,
    MODEL_IDS,
    MODEL_OUTPUT_SCHEMA,
    ModelCoderOutput,
    aggregate_model_reviews,
    build_anthropic_request,
    build_blinded_prompt,
    build_majority_triage,
    finalize_parent_panel,
    normalize_model_output,
    prepare_panel,
    prepare_parent_panel,
    validate_api_response,
)
from scripts.gold_lite_review import GoldLiteManifest, build_review_packet

FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "cb"
BUNDLE_NAME = "evidence-bundle-minimal"


def _packet(tmp_path: Path):
    manifest = GoldLiteManifest.model_validate(
        {
            "schema_version": "gold-lite-manifest-v0.1",
            "rehearsal_id": "gold-lite-model-panel-test",
            "label": "DEV test; not validation",
            "selection": {
                "method": "sha256-lowest",
                "seed": "gold-lite-model-panel-test-seed",
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
    return build_review_packet(
        manifest,
        FIXTURE_ROOT,
        deviations_dir=tmp_path / "deviations",
    )


def _coder_output(packet, labels=("supports", "supports"), confidence="sure"):
    candidate_id = packet.parents[0].candidates[0].candidate_id
    decisions = []
    for atom, label in zip(packet.parents[0].atoms, labels, strict=True):
        decisions.append(
            {
                "atom_id": atom.atom_id,
                "label": label,
                "confidence": confidence,
                "selected_candidate_ids": (
                    [candidate_id] if label in {"supports", "refutes"} else []
                ),
                "note": "",
            }
        )
    return ModelCoderOutput.model_validate(
        {
            "schema_version": MODEL_OUTPUT_SCHEMA,
            "packet_sha256": packet.packet_sha256,
            "parent_reviews": [
                {
                    "parent_id": packet.parents[0].parent_id,
                    "decomposition_status": "approved",
                    "decomposition_note": "",
                    "atom_decisions": decisions,
                }
            ],
        }
    )


def _artifact(packet, model_id, labels=("supports", "supports"), confidence="sure"):
    output = _coder_output(packet, labels=labels, confidence=confidence)
    review, parent_results = normalize_model_output(
        packet,
        output,
        model_id=model_id,
        exported_at_utc="2026-07-11T20:00:00+00:00",
    )
    return {
        "schema_version": "gold-lite-model-review-v0.1",
        "label": DEV_LABEL,
        "panel_id": "test-panel",
        "packet_sha256": packet.packet_sha256,
        "model_id": model_id,
        "review": review.model_dump(mode="json"),
        "parent_results": parent_results,
    }


def test_blinded_prompt_has_exact_packet_content_without_hidden_fields(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    prompt = build_blinded_prompt(packet)

    assert packet.packet_sha256 in prompt
    for parent in packet.parents:
        assert parent.parent_id in prompt
        for atom in parent.atoms:
            assert atom.atom_id in prompt
        for candidate in parent.candidates:
            assert candidate.candidate_id in prompt
            assert candidate.text in prompt
    for forbidden in (
        '"workflow_condition"',
        '"scaffold_support_status"',
        '"source_trust_level"',
        '"evidence_role"',
        '"retrieval_rank"',
    ):
        assert forbidden not in prompt


def test_prepare_panel_is_byte_stable_and_uses_pinned_tiers(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    out = tmp_path / "panel"

    first = prepare_panel(packet, out, tiers=list(MODEL_IDS), max_tokens=12_000)
    before = {path.relative_to(out): path.read_bytes() for path in out.rglob("*") if path.is_file()}
    second = prepare_panel(packet, out, tiers=list(MODEL_IDS), max_tokens=12_000)
    after = {path.relative_to(out): path.read_bytes() for path in out.rglob("*") if path.is_file()}

    assert first == second
    assert before == after
    assert first["model_ids"] == list(MODEL_IDS.values())
    assert len(list(out.glob("*/request.json"))) == 4
    for request_path in out.glob("*/request.json"):
        request = json.loads(request_path.read_text(encoding="utf-8"))
        assert request["output_config"]["format"]["type"] == "json_schema"
        assert request["max_tokens"] == 12_000


def test_parent_panel_locks_real_ids_and_uses_low_effort_only_where_supported(
    tmp_path: Path,
) -> None:
    packet = _packet(tmp_path)
    out = tmp_path / "parent-panel"

    manifest = prepare_parent_panel(
        packet,
        out,
        tiers=["haiku", "sonnet"],
        max_tokens=4_000,
        effort="low",
    )

    assert manifest["request_mode"] == "one-parent-per-call"
    assert len(list(out.glob("*/p01/request.json"))) == 2
    haiku = json.loads(
        (out / MODEL_IDS["haiku"] / "p01" / "request.json").read_text(encoding="utf-8")
    )
    sonnet = json.loads(
        (out / MODEL_IDS["sonnet"] / "p01" / "request.json").read_text(encoding="utf-8")
    )
    assert "effort" not in haiku["output_config"]
    assert sonnet["output_config"]["effort"] == "low"
    schema = sonnet["output_config"]["format"]["schema"]
    assert "maxItems" not in json.dumps(schema)
    assert schema["properties"]["packet_sha256"]["enum"] == [packet.packet_sha256]
    parent_schema = schema["properties"]["parent_reviews"]["items"]
    assert parent_schema["properties"]["parent_id"]["enum"] == ["clm-001"]
    assert set(
        parent_schema["properties"]["atom_decisions"]["items"]["properties"]["atom_id"]["enum"]
    ) == {"atom-1", "atom-2"}


def test_parent_panel_combines_validated_calls_before_silver_aggregation(
    tmp_path: Path,
) -> None:
    packet = _packet(tmp_path)
    out = tmp_path / "parent-panel"
    prepare_parent_panel(
        packet,
        out,
        tiers=["haiku", "sonnet"],
        max_tokens=4_000,
        effort="low",
    )
    structured = _coder_output(packet).model_dump_json()
    for model_id in (MODEL_IDS["haiku"], MODEL_IDS["sonnet"]):
        request_path = out / model_id / "p01" / "request.json"
        request = json.loads(request_path.read_text(encoding="utf-8"))
        envelope = {
            "schema_version": BRIDGE_SCHEMA,
            "request_sha256": canonical_sha256(request),
            "called_at_utc": "2026-07-11T20:00:00+00:00",
            "counted_input_tokens": 100,
            "response": {
                "id": f"msg_{model_id}",
                "model": model_id,
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": structured}],
                "usage": {"input_tokens": 100, "output_tokens": 50},
            },
        }
        (request_path.parent / "api-response.json").write_text(
            json.dumps(envelope),
            encoding="utf-8",
        )

    consensus = finalize_parent_panel(packet, out)

    assert consensus["counts"]["models"] == 2
    assert consensus["counts"]["unanimous_silver_atoms"] == 2
    for model_id in (MODEL_IDS["haiku"], MODEL_IDS["sonnet"]):
        combined = json.loads((out / model_id / "model-review.json").read_text())
        assert combined["request_mode"] == "one-parent-per-call"
        assert len(combined["source_parent_reviews"]) == 1


def test_parent_refusal_is_preserved_as_unavailable_vote(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    out = tmp_path / "parent-panel"
    prepare_parent_panel(
        packet,
        out,
        tiers=["haiku", "fable"],
        max_tokens=4_000,
        effort="low",
    )
    structured = _coder_output(packet).model_dump_json()
    for model_id, stop_reason in (
        (MODEL_IDS["haiku"], "end_turn"),
        (MODEL_IDS["fable"], "refusal"),
    ):
        request_path = out / model_id / "p01" / "request.json"
        request = json.loads(request_path.read_text(encoding="utf-8"))
        content = [{"type": "text", "text": structured}] if stop_reason == "end_turn" else []
        envelope = {
            "schema_version": BRIDGE_SCHEMA,
            "request_sha256": canonical_sha256(request),
            "called_at_utc": "2026-07-11T20:00:00+00:00",
            "counted_input_tokens": 100,
            "response": {
                "id": f"msg_{model_id}",
                "model": model_id,
                "stop_reason": stop_reason,
                "content": content,
                "usage": {"input_tokens": 100, "output_tokens": 5},
            },
        }
        (request_path.parent / "api-response.json").write_text(
            json.dumps(envelope),
            encoding="utf-8",
        )

    consensus = finalize_parent_panel(packet, out)

    assert consensus["counts"]["model_parent_failures"] == 1
    assert consensus["counts"]["atom_dispositions"]["missing_vote_queue"] == 2
    assert consensus["counts"]["human_queue_parents"] == 1
    failure = out / MODEL_IDS["fable"] / "p01" / "model-review-failure.json"
    assert json.loads(failure.read_text())["stop_reason"] == "refusal"


def test_normalization_binds_selected_candidate_to_packet_provenance(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    output = _coder_output(packet, labels=("supports", "insufficient"))

    review, parent_results = normalize_model_output(
        packet,
        output,
        model_id=MODEL_IDS["haiku"],
        exported_at_utc="2026-07-11T20:00:00+00:00",
    )

    assert review.reviewer == f"anthropic-api:{MODEL_IDS['haiku']}"
    assert review.decisions[0].selected_passages[0].passage_hash.startswith("sha256:")
    assert review.decisions[1].selected_passages == []
    assert parent_results[0]["support_verdict"] == "partially_supported"


def test_normalization_rejects_unknown_candidate_and_missing_atom(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    raw = _coder_output(packet).model_dump(mode="json")
    raw["parent_reviews"][0]["atom_decisions"][0]["selected_candidate_ids"] = ["unknown"]
    unknown = ModelCoderOutput.model_validate(raw)
    with pytest.raises(ValueError, match="unknown selected candidates"):
        normalize_model_output(
            packet,
            unknown,
            model_id=MODEL_IDS["haiku"],
            exported_at_utc="2026-07-11T20:00:00+00:00",
        )

    raw = _coder_output(packet).model_dump(mode="json")
    raw["parent_reviews"][0]["atom_decisions"].pop()
    missing = ModelCoderOutput.model_validate(raw)
    with pytest.raises(ValueError, match="model atom coverage mismatch"):
        normalize_model_output(
            packet,
            missing,
            model_id=MODEL_IDS["haiku"],
            exported_at_utc="2026-07-11T20:00:00+00:00",
        )


def test_api_response_validation_checks_request_hash_model_and_output(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    model_id = MODEL_IDS["haiku"]
    request = build_anthropic_request(packet, model_id=model_id, max_tokens=12_000)
    request_path = tmp_path / "request.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    structured = _coder_output(packet).model_dump_json()
    envelope = {
        "schema_version": BRIDGE_SCHEMA,
        "request_sha256": canonical_sha256(request),
        "called_at_utc": "2026-07-11T20:00:00+00:00",
        "counted_input_tokens": 100,
        "response": {
            "id": "msg_test",
            "model": model_id,
            "stop_reason": "end_turn",
            "content": [{"type": "text", "text": structured}],
            "usage": {"input_tokens": 100, "output_tokens": 50},
        },
    }
    response_path = tmp_path / "response.json"
    response_path.write_text(json.dumps(envelope), encoding="utf-8")
    manifest = {
        "panel_id": "test-panel",
        "prompt_sha256": "0" * 64,
    }

    artifact = validate_api_response(
        packet,
        request_path,
        response_path,
        tmp_path / "model-review.json",
        panel_manifest=manifest,
    )

    assert artifact["model_id"] == model_id
    assert artifact["review"]["decisions"][0]["atom_id"] == "atom-1"
    envelope["request_sha256"] = "sha256:" + "0" * 64
    response_path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(ValueError, match="request hash"):
        validate_api_response(
            packet,
            request_path,
            response_path,
            tmp_path / "other-review.json",
            panel_manifest=manifest,
        )


def test_unanimous_tier_votes_create_only_audited_silver_candidates(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    artifacts = [_artifact(packet, model_id) for model_id in MODEL_IDS.values()]
    manifest = {"panel_id": "test-panel"}

    consensus = aggregate_model_reviews(packet, artifacts, panel_manifest=manifest)

    assert consensus["counts"]["unanimous_silver_atoms"] == 2
    assert consensus["counts"]["silver_parents_before_audit"] == 1
    assert consensus["counts"]["audit_sample_parents"] == 1
    assert consensus["counts"]["human_queue_parents"] == 1
    assert consensus["parents"][0]["silver_parent_result"]["support_verdict"] == "supported"
    assert "not independent human annotation" in consensus["panel_limit"]
    triage = build_majority_triage(consensus)
    assert triage["counts"]["strong_majority_suggestion"] == 2
    assert triage["human_decision_required_for_every_atom"] is True


def test_disagreement_uncertainty_and_retrieval_gap_stay_in_human_queue(
    tmp_path: Path,
) -> None:
    packet = _packet(tmp_path)
    manifest = {"panel_id": "test-panel"}
    disagreement = [
        _artifact(packet, MODEL_IDS["haiku"], labels=("supports", "supports")),
        _artifact(packet, MODEL_IDS["sonnet"], labels=("insufficient", "supports")),
    ]
    result = aggregate_model_reviews(packet, disagreement, panel_manifest=manifest)
    assert result["counts"]["silver_parents_before_audit"] == 0
    assert result["human_queue"][0]["parent_id"] == "clm-001"
    assert "label_disagreement_queue" in result["human_queue"][0]["reasons"][0]

    uncertain = [
        _artifact(packet, MODEL_IDS["haiku"], confidence="sure"),
        _artifact(packet, MODEL_IDS["sonnet"], confidence="unsure"),
    ]
    result = aggregate_model_reviews(packet, uncertain, panel_manifest=manifest)
    assert result["counts"]["atom_dispositions"]["uncertainty_queue"] == 2

    gaps = [
        _artifact(packet, MODEL_IDS["haiku"], labels=("retrieval_gap", "retrieval_gap")),
        _artifact(packet, MODEL_IDS["sonnet"], labels=("retrieval_gap", "retrieval_gap")),
    ]
    result = aggregate_model_reviews(packet, gaps, panel_manifest=manifest)
    assert result["counts"]["atom_dispositions"]["retrieval_gap_queue"] == 2
    triage = build_majority_triage(result)
    assert triage["counts"]["weak_available_unanimity"] == 2


class _FakeMessages:
    def __init__(self, response: dict) -> None:
        self.response = response
        self.count_body = None
        self.create_body = None

    def count_tokens(self, **kwargs):
        self.count_body = kwargs
        return SimpleNamespace(input_tokens=321)

    def create(self, **kwargs):
        self.create_body = kwargs
        return SimpleNamespace(model_dump=lambda **_kwargs: self.response)


def test_bridge_counts_once_executes_once_and_refuses_overwrite(tmp_path: Path) -> None:
    request = {"model": MODEL_IDS["haiku"], "max_tokens": 100, "messages": []}
    request_path = tmp_path / "request.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    response_path = tmp_path / "response.json"
    messages = _FakeMessages({"model": MODEL_IDS["haiku"], "stop_reason": "end_turn"})
    client = SimpleNamespace(messages=messages)

    envelope = run_prepared_request(
        request_path,
        response_path,
        env_file=tmp_path / "unused.env",
        max_input_tokens=1_000,
        client=client,
    )

    assert envelope["counted_input_tokens"] == 321
    assert "max_tokens" not in messages.count_body
    assert messages.create_body == request
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        run_prepared_request(
            request_path,
            response_path,
            env_file=tmp_path / "unused.env",
            max_input_tokens=1_000,
            client=client,
        )
