"""Contract tests for provider-neutral Gold Lite model comparison tooling."""

from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from scripts.codex_cli_model_bridge import (
    _tool_event_violations,
)
from scripts.codex_cli_model_bridge import (
    run_prepared_request as run_codex_request,
)
from scripts.gold_lite_model_panel import (
    MODEL_OUTPUT_SCHEMA,
    ModelCoderOutput,
    normalize_model_output,
)
from scripts.gold_lite_portable_panel import (
    PORTABLE_RECEIPT_SCHEMA,
    build_cross_model_comparison,
    comparison_markdown,
    extract_model_output,
    finalize_portable_panel,
    prepare_external_kit,
    prepare_portable_panel,
    validate_portable_receipt,
)
from scripts.gold_lite_review import GoldLiteManifest, ReviewExport, build_review_packet
from scripts.mlx_model_bridge import run_model_directory

FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "cb"
BUNDLE_NAME = "evidence-bundle-minimal"


def _packet(tmp_path: Path):
    manifest = GoldLiteManifest.model_validate(
        {
            "schema_version": "gold-lite-manifest-v0.1",
            "rehearsal_id": "gold-lite-portable-panel-test",
            "label": "DEV test; not validation",
            "selection": {
                "method": "sha256-lowest",
                "seed": "gold-lite-portable-panel-test-seed",
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


def _coder_output(packet, labels=("supports", "supports")) -> ModelCoderOutput:
    candidate_id = packet.parents[0].candidates[0].candidate_id
    return ModelCoderOutput.model_validate(
        {
            "schema_version": MODEL_OUTPUT_SCHEMA,
            "packet_sha256": packet.packet_sha256,
            "parent_reviews": [
                {
                    "parent_id": packet.parents[0].parent_id,
                    "decomposition_status": "approved",
                    "decomposition_note": "",
                    "atom_decisions": [
                        {
                            "atom_id": atom.atom_id,
                            "label": label,
                            "confidence": "sure",
                            "selected_candidate_ids": (
                                [candidate_id] if label in {"supports", "refutes"} else []
                            ),
                            "note": "",
                        }
                        for atom, label in zip(packet.parents[0].atoms, labels, strict=True)
                    ],
                }
            ],
        }
    )


def _canonical_sha256(value) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return f"sha256:{hashlib.sha256(encoded.encode()).hexdigest()}"


def _receipt(request: dict, response_text: str, *, finish_reason="stop") -> dict:
    return {
        "schema_version": PORTABLE_RECEIPT_SCHEMA,
        "request_sha256": _canonical_sha256(request),
        "called_at_utc": "2026-07-12T12:00:00+00:00",
        "provider": request["provider"],
        "model_id": request["model_id"],
        "finish_reason": finish_reason,
        "response_text": response_text,
        "response_sha256": (f"sha256:{hashlib.sha256(response_text.encode()).hexdigest()}"),
        "usage": {"input_tokens": 100, "output_tokens": 50},
        "runtime": {"test": True},
    }


def _write_receipt(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def _artifact(packet, model_id: str, labels) -> dict:
    output = _coder_output(packet, labels=labels)
    review, parent_results = normalize_model_output(
        packet,
        output,
        model_id=model_id,
        reviewer=f"test-provider:{model_id}",
        exported_at_utc="2026-07-12T12:00:00+00:00",
    )
    return {
        "schema_version": "gold-lite-model-review-v0.1",
        "packet_sha256": packet.packet_sha256,
        "provider": "test-provider",
        "model_id": model_id,
        "source_reviews": [{"protocol_exact_json": True}],
        "failed_parent_reviews": [],
        "review": review.model_dump(mode="json"),
        "parent_results": parent_results,
    }


def test_prepare_portable_panel_is_stable_and_exactly_bound(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    out = tmp_path / "panel"
    kwargs = {
        "provider": "test-provider",
        "runtime": "test-runtime",
        "model_ids": ["model-a", "model-b"],
        "request_mode": "one-parent-per-call",
        "max_tokens": 800,
        "independence_boundary": "test models are correlated; not human coders",
    }
    first = prepare_portable_panel(packet, out, **kwargs)
    before = {path.relative_to(out): path.read_bytes() for path in out.rglob("*") if path.is_file()}
    second = prepare_portable_panel(packet, out, **kwargs)
    after = {path.relative_to(out): path.read_bytes() for path in out.rglob("*") if path.is_file()}

    assert first == second
    assert before == after
    assert len(list(out.glob("*/p01/request.json"))) == 2
    request = json.loads(next(out.glob("*/p01/request.json")).read_text())
    assert request["packet_sha256"] == packet.packet_sha256
    assert request["parent_ids"] == ["clm-001"]
    schema = request["output_schema"]
    assert schema["properties"]["packet_sha256"]["enum"] == [packet.packet_sha256]


def test_external_kit_contains_full_and_parent_fallbacks(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    out = tmp_path / "external"
    prepare_external_kit(packet, out)

    paste_ready = (out / "full-packet/paste-ready-prompt.txt").read_text()
    assert packet.packet_sha256 in paste_ready
    assert "required_output_json_schema" in paste_ready
    assert MODEL_OUTPUT_SCHEMA in paste_ready
    assert (out / "one-parent-per-call/p01/output-schema.json").is_file()
    assert "not human gold" in (out / "README.md").read_text()


def test_extract_model_output_accepts_wrapping_but_never_repairs_json(tmp_path: Path) -> None:
    output = _coder_output(_packet(tmp_path)).model_dump_json()

    assert extract_model_output(output)[1] == "exact-json"
    assert extract_model_output(f"```json\n{output}\n```")[1] == "fenced-json"
    assert extract_model_output(f"<think>bounded review</think>\n{output}")[1] == "embedded-json"
    with pytest.raises(ValueError, match="found 2"):
        extract_model_output(f"{output}\n{output}")
    with pytest.raises(ValueError, match="exactly one recoverable"):
        extract_model_output('{"schema_version": "wrong"}')


def test_portable_receipt_normalizes_generic_reviewer_and_provenance(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    out = tmp_path / "panel"
    manifest = prepare_portable_panel(
        packet,
        out,
        provider="test-provider",
        runtime="test-runtime",
        model_ids=["model-a"],
        request_mode="full-packet",
        max_tokens=800,
        independence_boundary="one test model; no gold claim",
    )
    request_path = out / "test-provider--model-a/request.json"
    request = json.loads(request_path.read_text())
    response_text = _coder_output(packet).model_dump_json()
    receipt_path = request_path.parent / "model-response.json"
    _write_receipt(receipt_path, _receipt(request, response_text))

    artifact = validate_portable_receipt(
        packet,
        request_path,
        receipt_path,
        request_path.parent / "model-review.json",
        panel_manifest=manifest,
    )

    assert artifact["review"]["reviewer"] == "test-provider:model-a"
    assert artifact["protocol_exact_json"] is True
    assert artifact["review"]["decisions"][0]["selected_passages"][0]["passage_hash"].startswith(
        "sha256:"
    )


def test_portable_receipt_rejects_a_hash_bound_but_noncanonical_request(
    tmp_path: Path,
) -> None:
    packet = _packet(tmp_path)
    out = tmp_path / "panel"
    manifest = prepare_portable_panel(
        packet,
        out,
        provider="test-provider",
        runtime="test-runtime",
        model_ids=["model-a"],
        request_mode="full-packet",
        max_tokens=800,
        independence_boundary="one test model; no gold claim",
    )
    request_path = out / "test-provider--model-a/request.json"
    request = json.loads(request_path.read_text())
    request["user_prompt"] += "\nOld labels: supports."
    rendered = request["system_prompt"] + "\n\n" + request["user_prompt"]
    request["prompt_sha256"] = f"sha256:{hashlib.sha256(rendered.encode()).hexdigest()}"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    receipt_path = request_path.parent / "model-response.json"
    _write_receipt(receipt_path, _receipt(request, _coder_output(packet).model_dump_json()))

    with pytest.raises(ValueError, match="not canonical"):
        validate_portable_receipt(
            packet,
            request_path,
            receipt_path,
            request_path.parent / "model-review.json",
            panel_manifest=manifest,
        )


def test_finalize_preserves_failed_model_and_generic_panel_limit(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    out = tmp_path / "panel"
    boundary = "two test models are correlated and are not independent human coders"
    prepare_portable_panel(
        packet,
        out,
        provider="test-provider",
        runtime="test-runtime",
        model_ids=["model-a", "model-b"],
        request_mode="one-parent-per-call",
        max_tokens=800,
        independence_boundary=boundary,
    )
    response_text = _coder_output(packet).model_dump_json()
    for model_id, finish_reason in (("model-a", "stop"), ("model-b", "length")):
        request_path = out / f"test-provider--{model_id}/p01/request.json"
        request = json.loads(request_path.read_text())
        _write_receipt(
            request_path.parent / "model-response.json",
            _receipt(request, response_text, finish_reason=finish_reason),
        )

    artifacts = finalize_portable_panel(packet, out)
    consensus = json.loads((out / "strict-model-consensus.json").read_text())

    assert len(artifacts) == 2
    assert artifacts[1]["failed_parent_reviews"][0]["parent_id"] == "clm-001"
    assert consensus["panel_limit"] == boundary
    assert consensus["counts"]["model_parent_failures"] == 1


def test_comparison_is_diagnostic_and_supplied_reference_stays_neutral(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    artifact_a = _artifact(packet, "model-a", ("supports", "supports"))
    artifact_b = _artifact(packet, "model-b", ("supports", "insufficient"))

    pending = build_cross_model_comparison(packet, [artifact_a, artifact_b])
    assert pending["reference_status"] == "pending-human-reference"
    assert pending["models"][0].get("human_reference") is None
    assert pending["pairwise_exact_label_agreement"][0]["exact_label_rate"] == 0.5
    assert pending["counts"]["runtime_provenance_complete_models"] == 0

    reference_raw = dict(artifact_a["review"])
    reference_raw["reviewer"] = "human:test"
    reference = ReviewExport.model_validate(reference_raw)
    scored = build_cross_model_comparison(
        packet,
        [artifact_a, artifact_b],
        reference=reference,
    )
    model_a = next(item for item in scored["models"] if item["model_id"] == "model-a")
    model_b = next(item for item in scored["models"] if item["model_id"] == "model-b")
    assert scored["reference_status"] == "complete-reference"
    assert model_a["reference"]["exact_label_rate"] == 1.0
    assert model_b["reference"]["exact_label_rate"] == 0.5
    assert "not described as human gold" in scored["comparison_limit"]


def test_comparison_validates_nested_reviews_and_dynamic_denominators(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    artifact_a = _artifact(packet, "model-a", ("supports", "supports"))
    artifact_b = _artifact(packet, "model-b", ("supports", "insufficient"))
    comparison = build_cross_model_comparison(packet, [artifact_a, artifact_b])
    markdown = comparison_markdown(comparison)
    assert "1/1" in markdown
    assert "2/2" in markdown
    assert "/10" not in markdown
    assert "/17" not in markdown

    artifact_b["review"]["decisions"][0]["selected_passages"][0]["passage_hash"] = (
        "sha256:" + "0" * 64
    )
    with pytest.raises(ValueError, match="provenance/hash drift"):
        build_cross_model_comparison(packet, [artifact_a, artifact_b])


def test_comparison_rejects_relabelled_identity_and_duplicate_source_receipts(
    tmp_path: Path,
) -> None:
    packet = _packet(tmp_path)
    artifact_a = _artifact(packet, "model-a", ("supports", "supports"))
    relabelled = deepcopy(artifact_a)
    relabelled["model_id"] = "model-b"
    with pytest.raises(ValueError, match="identity drift"):
        build_cross_model_comparison(packet, [artifact_a, relabelled])

    artifact_b = _artifact(packet, "model-b", ("supports", "supports"))
    response_hash = "sha256:" + "1" * 64
    artifact_a["source_reviews"] = [{"response_receipt_sha256": response_hash}]
    artifact_b["source_reviews"] = [{"response_receipt_sha256": response_hash}]
    with pytest.raises(ValueError, match="duplicate model source receipts"):
        build_cross_model_comparison(packet, [artifact_a, artifact_b])


def test_finalize_rejects_manifest_path_traversal_before_writing(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    out = tmp_path / "panel"
    prepare_portable_panel(
        packet,
        out,
        provider="test-provider",
        runtime="test-runtime",
        model_ids=["model-a", "model-b"],
        request_mode="full-packet",
        max_tokens=800,
        independence_boundary="test models are correlated",
    )
    manifest_path = out / "panel-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["models"][0]["model_dir"] = "../escape"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="model_dir"):
        finalize_portable_panel(packet, out)
    assert not (tmp_path / "escape/model-review.json").exists()


def test_codex_bridge_uses_ephemeral_read_only_structured_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet = _packet(tmp_path)
    out = tmp_path / "panel"
    prepare_portable_panel(
        packet,
        out,
        provider="codex-cli",
        runtime="codex-cli-test",
        model_ids=["gpt-test"],
        request_mode="full-packet",
        max_tokens=800,
        independence_boundary="cold test session",
    )
    request_path = out / "codex-cli--gpt-test/request.json"
    captured: dict[str, object] = {}

    def fake_run(command, *, input, text, capture_output, check):
        captured["command"] = command
        captured["prompt"] = input
        message_path = Path(command[command.index("--output-last-message") + 1])
        message_path.write_text(_coder_output(packet).model_dump_json(), encoding="utf-8")
        events = "\n".join(
            [
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"type": "agent_message", "text": "done"},
                    }
                ),
                json.dumps({"type": "turn.completed", "usage": {"input_tokens": 7}}),
            ]
        )
        return SimpleNamespace(returncode=0, stdout=events + "\n", stderr="")

    monkeypatch.setattr("scripts.codex_cli_model_bridge.subprocess.run", fake_run)
    receipt = run_codex_request(
        request_path,
        request_path.parent / "model-response.json",
        request_path.parent / "codex-events.jsonl",
        codex_bin="codex-test",
        reasoning_effort="low",
    )

    command = captured["command"]
    assert "--ephemeral" in command
    assert ["--sandbox", "read-only"] == command[
        command.index("--sandbox") : command.index("--sandbox") + 2
    ]
    assert receipt["finish_reason"] == "completed"
    assert receipt["usage"] == {"input_tokens": 7}
    assert receipt["runtime"]["bridge_script_sha256"].startswith("sha256:")
    assert receipt["runtime"]["max_output_tokens_enforced"] is False
    assert receipt["runtime"]["rendered_input_sha256"].startswith("sha256:")
    assert receipt["runtime"]["tool_event_audit"] == {
        "status": "passed",
        "violations": [],
    }


def test_codex_event_audit_rejects_incomplete_lifecycles() -> None:
    assert "item lifecycle event is missing its item" in " ".join(
        _tool_event_violations(json.dumps({"type": "item.completed"}))
    )
    thread_only = _tool_event_violations(json.dumps({"type": "thread.started"}))
    assert "no completed agent_message" in " ".join(thread_only)
    assert "no turn.completed" in " ".join(thread_only)


def test_codex_bridge_preserves_and_rejects_tool_bearing_events(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet = _packet(tmp_path)
    out = tmp_path / "panel"
    prepare_portable_panel(
        packet,
        out,
        provider="codex-cli",
        runtime="codex-cli-test",
        model_ids=["gpt-test"],
        request_mode="full-packet",
        max_tokens=800,
        independence_boundary="cold test session",
    )
    request_path = out / "codex-cli--gpt-test/request.json"
    receipt_path = request_path.parent / "model-response.json"
    events_path = request_path.parent / "codex-events.jsonl"

    def fake_run(command, *, input, text, capture_output, check):
        del input, text, capture_output, check
        message_path = Path(command[command.index("--output-last-message") + 1])
        message_path.write_text(_coder_output(packet).model_dump_json(), encoding="utf-8")
        events = json.dumps(
            {
                "type": "item.completed",
                "item": {"type": "command_execution", "command": "pwd"},
            }
        )
        return SimpleNamespace(returncode=0, stdout=events + "\n", stderr="")

    monkeypatch.setattr("scripts.codex_cli_model_bridge.subprocess.run", fake_run)
    with pytest.raises(RuntimeError, match="prohibited or unauditable"):
        run_codex_request(
            request_path,
            receipt_path,
            events_path,
            codex_bin="codex-test",
            reasoning_effort="low",
        )

    receipt = json.loads(receipt_path.read_text())
    assert receipt["finish_reason"] == "protocol_violation"
    assert receipt["runtime"]["tool_event_audit"]["status"] == "failed"
    assert events_path.is_file()


def test_codex_bridge_preflights_existing_outputs_before_subprocess(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet = _packet(tmp_path)
    out = tmp_path / "panel"
    prepare_portable_panel(
        packet,
        out,
        provider="codex-cli",
        runtime="codex-cli-test",
        model_ids=["gpt-test"],
        request_mode="full-packet",
        max_tokens=800,
        independence_boundary="cold test session",
    )
    request_path = out / "codex-cli--gpt-test/request.json"
    receipt_path = request_path.parent / "model-response.json"
    events_path = request_path.parent / "codex-events.jsonl"
    receipt_path.write_text("already present", encoding="utf-8")

    def should_not_run(*args, **kwargs):
        raise AssertionError("subprocess must not run after a failed preflight")

    monkeypatch.setattr("scripts.codex_cli_model_bridge.subprocess.run", should_not_run)
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        run_codex_request(
            request_path,
            receipt_path,
            events_path,
            codex_bin="codex-test",
            reasoning_effort="low",
        )


def test_mlx_bridge_rejects_models_outside_scaffold_study_set(tmp_path: Path) -> None:
    model_dir = tmp_path / "mlx-local--unknown"
    request_dir = model_dir / "p01"
    request_dir.mkdir(parents=True)
    (request_dir / "request.json").write_text(
        json.dumps(
            {
                "schema_version": "gold-lite-portable-model-request-v0.1",
                "provider": "mlx-local",
                "model_id": "unknown/model",
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="not in the scaffold-study MLX set"):
        run_model_directory(model_dir)


def test_mlx_bridge_loads_pinned_snapshot_and_preserves_stream_finish_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_id = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
    model_dir = tmp_path / "model"
    request_dir = model_dir / "p01"
    request_dir.mkdir(parents=True)
    request = {
        "schema_version": "gold-lite-portable-model-request-v0.1",
        "provider": "mlx-local",
        "model_id": model_id,
        "system_prompt": "Bounded evidence only.",
        "user_prompt": "Return the annotation.",
        "output_schema": {"type": "object"},
        "max_output_tokens": 20,
    }
    (request_dir / "request.json").write_text(json.dumps(request), encoding="utf-8")
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    loaded: dict[str, object] = {}

    class FakeTokenizer:
        chat_template = "test-template"

        def apply_chat_template(self, messages, **kwargs):
            loaded["messages"] = messages
            loaded["template_kwargs"] = kwargs
            return "rendered prompt"

    mlx_package = ModuleType("mlx")
    mlx_core = ModuleType("mlx.core")
    mlx_core.clear_cache = lambda: None  # type: ignore[attr-defined]
    mlx_package.core = mlx_core  # type: ignore[attr-defined]
    mlx_lm = ModuleType("mlx_lm")

    def fake_load(path):
        loaded["path"] = path
        return object(), FakeTokenizer()

    def fake_stream_generate(model, tokenizer, *, prompt, max_tokens, sampler):
        del model, tokenizer, sampler
        loaded["prompt"] = prompt
        loaded["max_tokens"] = max_tokens
        yield SimpleNamespace(
            text='{"ok": true}',
            generation_tokens=4,
            prompt_tokens=12,
            finish_reason=None,
        )
        yield SimpleNamespace(
            text="",
            generation_tokens=4,
            prompt_tokens=12,
            finish_reason="stop",
        )

    mlx_lm.load = fake_load  # type: ignore[attr-defined]
    mlx_lm.stream_generate = fake_stream_generate  # type: ignore[attr-defined]
    sample_utils = ModuleType("mlx_lm.sample_utils")
    sample_utils.make_sampler = lambda **kwargs: kwargs  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "mlx", mlx_package)
    monkeypatch.setitem(sys.modules, "mlx.core", mlx_core)
    monkeypatch.setitem(sys.modules, "mlx_lm", mlx_lm)
    monkeypatch.setitem(sys.modules, "mlx_lm.sample_utils", sample_utils)
    monkeypatch.setattr(
        "scripts.mlx_model_bridge._cached_snapshot",
        lambda requested: (snapshot.resolve(), "a" * 40),
    )
    monkeypatch.setattr("scripts.mlx_model_bridge.importlib.metadata.version", lambda name: "test")

    receipts = run_model_directory(model_dir)

    assert loaded["path"] == str(snapshot.resolve())
    assert receipts[0]["finish_reason"] == "stop"
    assert receipts[0]["usage"] == {"input_tokens": 12, "output_tokens": 4}
    runtime = receipts[0]["runtime"]
    assert runtime["model_revision"] == "a" * 40
    assert runtime["finish_reason_source"] == "mlx_lm.stream_generate"
    assert runtime["rendered_input_sha256"].startswith("sha256:")
    assert runtime["chat_template_sha256"].startswith("sha256:")
