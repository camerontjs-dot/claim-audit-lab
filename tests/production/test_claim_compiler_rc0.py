from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from claim_audit_lab.production_v1.bundle_input import load_target, prepare_contract_b_input
from claim_audit_lab.production_v1.claim_compiler import (
    CompilerObservation,
    CompilerStatus,
    _resolve_observations,
    canonical_target_bytes,
    compile_claim,
)
from claim_audit_lab.production_v1.semantic.models import SemanticFamily

FIXTURE = Path(__file__).parent / "fixtures" / "claim_compiler_rc0.json"


def _cases() -> list[dict[str, object]]:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert value["schema"] == "cal-v1-claim-compiler-rc0-corpus-v1"
    assert value["frozen_before_implementation_run"] is True
    return value["cases"]


@pytest.mark.parametrize("case", _cases(), ids=lambda case: str(case["case_id"]))
def test_frozen_claim_compiler_corpus(case: dict[str, object], tmp_path: Path) -> None:
    claim_id = str(case["claim_id"])
    claim_text = str(case["claim_text"])
    receipt = compile_claim(claim_id, claim_text)

    assert receipt.status.value == case["expected_status"]
    assert receipt.claim_id == claim_id
    assert receipt.claim_text_sha256 == hashlib.sha256(claim_text.encode("utf-8")).hexdigest()
    receipt.verify()

    target = receipt.target()
    if receipt.status is not CompilerStatus.ESTABLISHED:
        assert case["expected_family"] is None
        assert case["expected_fields"] is None
        assert receipt.proposition is None
        assert target is None
        return

    assert target is not None
    assert receipt.proposition is not None
    assert receipt.proposition.semantic_family.value == case["expected_family"]
    assert receipt.proposition.field_map() == case["expected_fields"]
    assert target == {
        "claim_id": claim_id,
        "proposition": {
            "proposition_id": claim_id,
            "text_sha256": hashlib.sha256(claim_text.encode("utf-8")).hexdigest(),
            "semantic_family": case["expected_family"],
            "fields": case["expected_fields"],
        },
    }

    path = tmp_path / f"{case['case_id']}.json"
    raw = canonical_target_bytes(receipt)
    path.write_bytes(raw)
    loaded, loaded_raw = load_target(path)
    assert loaded == target
    assert loaded_raw == raw


def test_compiler_is_deterministic_and_content_bound() -> None:
    first = compile_claim("claim-1", "Alpha reported a higher rate than Beta.")
    replay = compile_claim("claim-1", "Alpha reported a higher rate than Beta.")
    changed_text = compile_claim("claim-1", "Alpha reported a lower rate than Beta.")
    changed_id = compile_claim("claim-2", "Alpha reported a higher rate than Beta.")

    assert first == replay
    assert first.receipt_id == replay.receipt_id
    assert first.receipt_id != changed_text.receipt_id
    assert first.receipt_id != changed_id.receipt_id
    assert first.proposition is not None
    assert changed_text.proposition is not None
    assert first.proposition.sha256 != changed_text.proposition.sha256
    assert first.proposition.sha256 != changed_id.proposition.sha256


def test_disagreeing_candidates_are_ambiguous_and_never_emit_target() -> None:
    more = {
        "lhs_entity": "alpha",
        "rhs_entity": "beta",
        "comparison_direction": "MORE_THAN",
    }
    less = {
        "lhs_entity": "alpha",
        "rhs_entity": "beta",
        "comparison_direction": "LESS_THAN",
    }
    observations = (
        CompilerObservation.candidate(
            "comparison-a", SemanticFamily.STRICT_COMPARISON, more
        ),
        CompilerObservation.candidate(
            "comparison-b", SemanticFamily.STRICT_COMPARISON, less
        ),
        CompilerObservation.not_applicable(
            "event-a", SemanticFamily.DIRECT_EVENT_ORDER
        ),
        CompilerObservation.not_applicable(
            "event-b", SemanticFamily.DIRECT_EVENT_ORDER
        ),
    )

    receipt = _resolve_observations("claim-1", "synthetic disagreement", observations)

    assert receipt.status is CompilerStatus.AMBIGUOUS
    assert receipt.proposition is None
    assert receipt.target() is None


def test_one_sided_candidate_cannot_establish_target() -> None:
    fields = {
        "lhs_entity": "alpha",
        "rhs_entity": "beta",
        "comparison_direction": "MORE_THAN",
    }
    observations = (
        CompilerObservation.candidate(
            "comparison-a", SemanticFamily.STRICT_COMPARISON, fields
        ),
        CompilerObservation.unresolved(
            "comparison-b", SemanticFamily.STRICT_COMPARISON, "could not bind rhs"
        ),
        CompilerObservation.not_applicable(
            "event-a", SemanticFamily.DIRECT_EVENT_ORDER
        ),
        CompilerObservation.not_applicable(
            "event-b", SemanticFamily.DIRECT_EVENT_ORDER
        ),
    )

    receipt = _resolve_observations("claim-1", "synthetic partial parse", observations)

    assert receipt.status is CompilerStatus.EXTRACTION_UNRESOLVED
    assert receipt.proposition is None
    assert receipt.target() is None


def test_cross_family_signal_blocks_otherwise_agreed_candidate() -> None:
    fields = {
        "lhs_entity": "alpha",
        "rhs_entity": "beta",
        "comparison_direction": "MORE_THAN",
    }
    observations = (
        CompilerObservation.candidate(
            "comparison-a", SemanticFamily.STRICT_COMPARISON, fields
        ),
        CompilerObservation.candidate(
            "comparison-b", SemanticFamily.STRICT_COMPARISON, fields
        ),
        CompilerObservation.unresolved(
            "event-a", SemanticFamily.DIRECT_EVENT_ORDER, "temporal cue present"
        ),
        CompilerObservation.unresolved(
            "event-b", SemanticFamily.DIRECT_EVENT_ORDER, "temporal cue present"
        ),
    )

    receipt = _resolve_observations("claim-1", "synthetic cross-family signal", observations)

    assert receipt.status is CompilerStatus.EXTRACTION_UNRESOLVED
    assert receipt.target() is None


def test_compiler_target_binds_existing_contract_b_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper_path = Path(__file__).with_name("test_contract_b_integration_candidate.py")
    spec = importlib.util.spec_from_file_location("_contract_b_fixture", helper_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    view = module._view()

    import claim_audit_lab.production_v1.bundle_input as bundle_input

    monkeypatch.setattr(bundle_input, "load_contract_b_intake", lambda _path: view)
    receipt = compile_claim("claim-1", "Women had a higher rate than Men.")
    assert receipt.status is CompilerStatus.ESTABLISHED

    target_path = tmp_path / "target.json"
    target_path.write_bytes(canonical_target_bytes(receipt))
    prepared = prepare_contract_b_input(tmp_path / "bundle", target_path)

    assert prepared.context.original_claim == "Women had a higher rate than Men."
    assert prepared.context.proposition == receipt.proposition
    assert prepared.context.proposition.text_sha256 == hashlib.sha256(
        prepared.context.original_claim.encode("utf-8")
    ).hexdigest()


def test_compiler_receipt_exposes_no_verdict_or_authority_surface() -> None:
    receipt = compile_claim("claim-1", "Alpha reported a higher rate than Beta.")
    assert receipt.status is CompilerStatus.ESTABLISHED

    forbidden = {
        "conclusion",
        "categorical_relation",
        "authority_id",
        "decision",
        "decision_result",
        "contract_c",
    }
    assert forbidden.isdisjoint(set(receipt.__dataclass_fields__))
    target = receipt.target()
    assert target is not None
    assert set(target) == {"claim_id", "proposition"}
    assert set(target["proposition"]) == {
        "proposition_id",
        "text_sha256",
        "semantic_family",
        "fields",
    }
