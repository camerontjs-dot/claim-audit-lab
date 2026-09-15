from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from claim_audit_lab.production_v1.bundle_input import PreparedContractBInput
from claim_audit_lab.production_v1.execution import run_contract_b_bundle
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _tagged(value: str) -> str:
    return f"sha256:{_hex(value)}"


def _prepared(target_bytes: bytes) -> PreparedContractBInput:
    claim = "Women had a higher rate than Men."
    passage = AdmittedPassage.create(
        "p1",
        "source-1",
        claim,
        source_sha256=_tagged("source-1"),
    )
    world = EvidenceWorld.create(
        contract_b_version="1.2.0",
        bundle_id="bundle-1",
        bundle_hash=_tagged("bundle-1"),
        admitted_passages=(passage,),
        aperture_observation={
            "contract_b_factual_context_state": "present",
            "observation": {
                "claim_id": "claim-1",
                "search_scope": {"profile": "fixture"},
                "outcome": {"state": "unknown", "value": None},
                "limitations": [],
            },
        },
    )
    proposition = TypedProposition.create(
        "claim-1",
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Women",
            "rhs_entity": "Men",
            "comparison_direction": "MORE_THAN",
        },
        text_sha256=_hex(claim),
    )
    context = AuditContext(claim, proposition, world)

    class _Intake:
        extension_state = "present"

    target = json.loads(target_bytes)
    return PreparedContractBInput(
        context=context,
        intake=_Intake(),  # type: ignore[arg-type]
        target=target,
        target_bytes=target_bytes,
        target_sha256="sha256:" + hashlib.sha256(target_bytes).hexdigest(),
        intake_snapshot={
            "schema": "cal-v1-contract-b-intake-snapshot-v1",
            "contract_b_version": "1.2.0",
            "extension_state": "present",
            "history": {"preserved_rejected_candidate": True},
        },
    )


def test_contract_b_run_writes_complete_native_artifact_and_is_deterministic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = {
        "claim_id": "claim-1",
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
    }
    target_bytes = (json.dumps(target, sort_keys=True) + "\n").encode("utf-8")
    prepared = _prepared(target_bytes)

    import claim_audit_lab.production_v1.execution as execution

    monkeypatch.setattr(
        execution,
        "prepare_contract_b_input",
        lambda _bundle, _target: prepared,
    )

    first = tmp_path / "first"
    second = tmp_path / "second"
    run_contract_b_bundle(tmp_path / "bundle", tmp_path / "target.json", first)
    run_contract_b_bundle(tmp_path / "bundle", tmp_path / "target.json", second)

    names = {
        "input.target.json",
        "contract_b_intake.snapshot.json",
        "audit_context.json",
        "result.json",
        "report.md",
        "manifest.json",
    }
    assert {path.name for path in first.iterdir()} == names
    assert {name: (first / name).read_bytes() for name in names} == {
        name: (second / name).read_bytes() for name in names
    }
    result = json.loads((first / "result.json").read_text(encoding="utf-8"))
    assert result["input"]["mode"] == "contract_b_bundle"
    assert result["input"]["contract_b"]["extension_state"] == "present"
    assert result["result"]["conclusion"] == "supported"
    assert result["measurements"][0]["available_passage_ids"] == ["p1"]
    assert result["measurements"][0]["consumed_passage_ids"] == ["p1"]
    assert result["composition"]["relation_categories"] == ["SUPPORTS"]
    intake = json.loads(
        (first / "contract_b_intake.snapshot.json").read_text(encoding="utf-8")
    )
    assert intake["history"]["preserved_rejected_candidate"] is True
