from __future__ import annotations

import hashlib
import json
import re
import socket
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from claim_audit_lab.cli import app

runner = CliRunner()
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _tagged(value: str) -> str:
    return f"sha256:{_hex(value)}"


def _packet(
    *,
    family: str = "strict_comparison",
    texts: tuple[str, ...] = ("Women had a higher rate than Men.",),
    contract_b_version: str = "1.2.0",
) -> dict[str, Any]:
    claim = "Women had a higher rate than Men."
    fields: dict[str, str]
    if family == "strict_comparison":
        fields = {
            "lhs_entity": "Women",
            "rhs_entity": "Men",
            "comparison_direction": "MORE_THAN",
        }
    elif family == "direct_event_order":
        fields = {
            "first_event": "launch",
            "second_event": "closure",
            "subject": "the programme",
        }
    else:
        fields = {"family_note": family}
    return {
        "original_claim": claim,
        "proposition": {
            "proposition_id": "cli-fixture-claim",
            "text_sha256": _hex(claim),
            "semantic_family": family,
            "fields": fields,
        },
        "evidence_world": {
            "contract_b_version": contract_b_version,
            "bundle_id": "cli-fixture-bundle",
            "bundle_hash": _tagged("cli-fixture-bundle"),
            "aperture_observation": {
                "search_scope": {"corpus": "cli-fixture"},
                "outcome": {"state": "unknown", "value": None},
                "limitations": [],
            },
            "admitted_passages": [
                {
                    "passage_id": f"cli-passage-{index}",
                    "source_id": "cli-source-1",
                    "text": text,
                    "text_sha256": _tagged(text),
                    "source_sha256": _tagged("cli-source-1"),
                }
                for index, text in enumerate(texts, start=1)
            ],
        },
    }


def _write_packet(path: Path, packet: dict[str, Any]) -> bytes:
    raw = (json.dumps(packet, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return raw


def _run(packet_path: Path, out_dir: Path):
    return runner.invoke(
        app,
        ["run", str(packet_path), "--out-dir", str(out_dir)],
    )


def _result(out_dir: Path) -> dict[str, Any]:
    return json.loads((out_dir / "result.json").read_text(encoding="utf-8"))


def test_production_help_surface_is_explicit_and_single_packet() -> None:
    root = runner.invoke(app, ["--help"])
    run = runner.invoke(app, ["run", "--help"])
    validate = runner.invoke(app, ["validate", "--help"])
    inspect = runner.invoke(app, ["inspect", "--help"])

    assert root.exit_code == 0
    assert all(command in root.output for command in ("run", "validate", "inspect"))
    assert "batch" not in root.output
    assert run.exit_code == 0
    assert "PACKET" in run.output
    assert "--out-dir" in run.output
    assert "--force" not in run.output
    assert validate.exit_code == 0
    assert "PACKET" in validate.output
    assert inspect.exit_code == 0
    assert "--json" in inspect.output


def test_inspect_json_is_deterministic_and_reports_runtime_authority() -> None:
    first = runner.invoke(app, ["inspect", "--json"])
    second = runner.invoke(app, ["inspect", "--json"])

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert first.output == second.output
    record = json.loads(first.output)
    assert record["distribution_version"] == "0.6.0"
    assert record["profile"] == "cal-v1-production-v1"
    assert record["semantic_implementation_sha"] == ("a902621e8baea3063dddd7f92ba975aade305464")
    assert record["supported_semantic_families"] == [
        "strict_comparison",
        "direct_event_order",
    ]
    assert HEX64.fullmatch(record["packet_schema_sha256"].removeprefix("sha256:"))
    assert HEX64.fullmatch(record["result_schema_sha256"].removeprefix("sha256:"))
    assert record["contract_c_handoff"] == {
        "owner": "apparatus-contracts",
        "state": "separate_versioned_handoff",
    }
    assert record["authorization"] == {"automatic_action_allowed": False}


def test_validate_does_not_execute_semantics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    packet_path = tmp_path / "packet.json"
    _write_packet(packet_path, _packet())

    def fail_if_called(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("CAL semantics must not run during validate")

    import claim_audit_lab.production_v1.semantic.engine as engine

    monkeypatch.setattr(engine, "audit", fail_if_called)
    result = runner.invoke(app, ["validate", str(packet_path)])

    assert result.exit_code == 0
    assert result.stdout.strip() == "VALID"


@pytest.mark.parametrize(
    ("mutation", "expected_text"),
    [
        ("extra", "unknown field"),
        ("unknown_family", "not supported"),
        ("malformed_hash", "64 lowercase hexadecimal"),
        ("stale_passage_hash", "passage hash mismatch"),
        ("wrong_contract_b", "released CAL input authority"),
    ],
)
def test_validate_rejects_invalid_intake(tmp_path: Path, mutation: str, expected_text: str) -> None:
    packet = _packet()
    if mutation == "extra":
        packet["extra"] = True
    elif mutation == "unknown_family":
        packet["proposition"]["semantic_family"] = "future_family"
    elif mutation == "malformed_hash":
        packet["proposition"]["text_sha256"] = "not-a-sha256"
    elif mutation == "stale_passage_hash":
        packet["evidence_world"]["admitted_passages"][0]["text"] = (
            "Women had a much higher rate than Men."
        )
    elif mutation == "wrong_contract_b":
        packet["evidence_world"]["contract_b_version"] = "2.0.0"

    packet_path = tmp_path / f"{mutation}.json"
    _write_packet(packet_path, packet)
    result = runner.invoke(app, ["validate", str(packet_path)])

    assert result.exit_code == 2
    assert "validate rejected" in result.stderr
    assert expected_text in result.stderr


@pytest.mark.parametrize(
    ("family", "texts", "conclusion", "failure"),
    [
        ("strict_comparison", ("Women had a higher rate than Men.",), "supported", None),
        ("strict_comparison", ("Women had a lower rate than Men.",), "contradicted", None),
        (
            "strict_comparison",
            (
                "Women had a higher rate than Men.",
                "Women had a lower rate than Men.",
            ),
            "not_checkable",
            "MIXED_RELATIONS",
        ),
        (
            "assertion_scope",
            ("Women had a higher rate than Men.",),
            "not_checkable",
            "UNSUPPORTED_SEMANTIC_FAMILY",
        ),
    ],
)
def test_terminal_scientific_results_exit_zero(
    tmp_path: Path,
    family: str,
    texts: tuple[str, ...],
    conclusion: str,
    failure: str | None,
) -> None:
    packet_path = tmp_path / "packet.json"
    _write_packet(packet_path, _packet(family=family, texts=texts))
    out_dir = tmp_path / "run"

    result = _run(packet_path, out_dir)

    assert result.exit_code == 0
    record = _result(out_dir)
    assert record["result"]["conclusion"] == conclusion
    assert record["result"]["failure_code"] == failure


def test_run_preserves_input_and_is_byte_deterministic(tmp_path: Path) -> None:
    packet_path = tmp_path / "packet.json"
    raw_packet = _write_packet(packet_path, _packet())
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    assert _run(packet_path, first_dir).exit_code == 0
    assert _run(packet_path, second_dir).exit_code == 0

    names = ("input.packet.json", "result.json", "report.md", "manifest.json")
    first_bytes = {name: (first_dir / name).read_bytes() for name in names}
    second_bytes = {name: (second_dir / name).read_bytes() for name in names}
    assert first_bytes == second_bytes
    assert first_bytes["input.packet.json"] == raw_packet

    manifest = json.loads(first_bytes["manifest.json"])
    assert manifest["files"]["input.packet.json"] == (
        "sha256:" + hashlib.sha256(raw_packet).hexdigest()
    )
    assert manifest["files"]["result.json"] == manifest["result_sha256"]
    assert manifest["files"]["report.md"] == manifest["report_sha256"]
    record = json.loads(first_bytes["result.json"])
    assert record["contract_c_handoff"] == {
        "state": "not_emitted",
        "owner": "apparatus-contracts",
        "reason": "separate_versioned_handoff_layer",
    }
    assert record["authorization"] == {
        "state": "not_evaluated",
        "automatic_action_allowed": False,
    }
    for _name, content in first_bytes.items():
        text = content.decode("utf-8")
        assert str(tmp_path) not in text
        assert socket.gethostname() not in text
        assert "timestamp" not in text.lower()
        assert re.search(r"\b\d{4}-\d{2}-\d{2}T\d{2}:", text) is None


def test_run_refuses_non_empty_output_directory(tmp_path: Path) -> None:
    packet_path = tmp_path / "packet.json"
    _write_packet(packet_path, _packet())
    out_dir = tmp_path / "existing"
    out_dir.mkdir()
    sentinel = out_dir / "sentinel"
    sentinel.write_text("preserve", encoding="utf-8")

    result = _run(packet_path, out_dir)

    assert result.exit_code == 2
    assert "non-empty" in result.stderr
    assert sentinel.read_text(encoding="utf-8") == "preserve"


def test_run_failure_leaves_no_partial_finalized_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    packet_path = tmp_path / "packet.json"
    _write_packet(packet_path, _packet())
    out_dir = tmp_path / "failed-run"

    import claim_audit_lab.production_v1.execution as execution

    def fail_replace(source: str | bytes, destination: str | bytes) -> None:
        raise OSError("forced finalization failure")

    monkeypatch.setattr(execution.os, "replace", fail_replace)
    result = _run(packet_path, out_dir)

    assert result.exit_code == 2
    assert not out_dir.exists()
    assert list(tmp_path.glob(f".{out_dir.name}.tmp-*")) == []


def test_run_does_not_route_through_legacy_audit_engine(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    packet_path = tmp_path / "packet.json"
    _write_packet(packet_path, _packet())
    out_dir = tmp_path / "run"

    import claim_audit_lab.cli as cli

    def fail_if_called(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("legacy audit engine was invoked")

    monkeypatch.setattr(cli, "audit_claims", fail_if_called)
    result = _run(packet_path, out_dir)

    assert result.exit_code == 0
    assert _result(out_dir)["result"]["conclusion"] == "supported"
