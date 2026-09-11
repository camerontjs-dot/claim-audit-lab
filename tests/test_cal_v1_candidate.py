from __future__ import annotations

import hashlib
import json
from dataclasses import replace

import pytest

from claim_audit_lab.cal_v1_candidate import (
    AdmittedPassage,
    AuditContext,
    CategoricalRelation,
    Conclusion,
    EvidenceWorld,
    FailureCode,
    SemanticFamily,
    TypedProposition,
    audit,
    project_contract_c_successor,
)
from claim_audit_lab.cal_v1_candidate.authority import (
    AuthorityRefusal,
    complete_and_warrant,
)
from claim_audit_lab.cal_v1_candidate.cli import context_from_packet
from claim_audit_lab.cal_v1_candidate.engine import PassageTrace, compose
from claim_audit_lab.cal_v1_candidate.measurements import measure_strict_comparison
from claim_audit_lab.cal_v1_candidate.relations import derive_relation


_SEMANTIC_SHA = "a" * 40


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return f"sha256:{_hex(value)}"


def _aperture(label: str = "fixture") -> dict[str, object]:
    return {
        "search_scope": {"corpus": label},
        "outcome": {"state": "unknown", "value": None},
        "limitations": [],
    }


def _context(
    family: SemanticFamily,
    fields: dict[str, str],
    texts: list[str],
    *,
    bundle_id: str = "bundle-1",
    aperture: dict[str, object] | None = None,
) -> AuditContext:
    passages = tuple(
        AdmittedPassage.create(f"p{index}", "source-1", text)
        for index, text in enumerate(texts, start=1)
    )
    world = EvidenceWorld.create(
        "1.2.0",
        bundle_id,
        _tagged(bundle_id),
        passages,
        aperture or _aperture(),
    )
    proposition = TypedProposition.create(
        "claim-1",
        family,
        fields,
        text_sha256=_hex("typed claim"),
    )
    return AuditContext("typed claim", proposition, world)


def test_strict_support_and_refute_inverse() -> None:
    support = _context(
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Women",
            "rhs_entity": "Men",
            "comparison_direction": "MORE_THAN",
        },
        ["Women had a higher rate than Men."],
    )
    assert audit(support).conclusion is Conclusion.SUPPORTED
    inverse = _context(
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Men",
            "rhs_entity": "Women",
            "comparison_direction": "MORE_THAN",
        },
        ["Women had a higher rate than Men."],
    )
    assert audit(inverse).conclusion is Conclusion.CONTRADICTED


def test_mixed_support_refute_abstains_and_order_is_invariant() -> None:
    fields = {
        "lhs_entity": "Women",
        "rhs_entity": "Men",
        "comparison_direction": "MORE_THAN",
    }
    a = _context(
        SemanticFamily.STRICT_COMPARISON,
        fields,
        ["Women had a higher rate than Men.", "Women had a lower rate than Men."],
    )
    b = _context(
        SemanticFamily.STRICT_COMPARISON,
        fields,
        ["Women had a lower rate than Men.", "Women had a higher rate than Men."],
    )
    assert audit(a).conclusion is Conclusion.NOT_CHECKABLE
    assert audit(a).failure_code is FailureCode.MIXED_RELATIONS
    assert audit(b).conclusion is Conclusion.NOT_CHECKABLE
    assert audit(b).failure_code is FailureCode.MIXED_RELATIONS


def test_measurement_tamper_cannot_acquire_authority() -> None:
    ctx = _context(
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Women",
            "rhs_entity": "Men",
            "comparison_direction": "MORE_THAN",
        },
        ["Women had a higher rate than Men."],
    )
    receipt = measure_strict_comparison(ctx, "p1")
    tampered = replace(
        receipt,
        raw_measurement_json=receipt.raw_measurement_json.replace(
            "MORE_THAN", "LESS_THAN"
        ),
    )
    with pytest.raises(AuthorityRefusal):
        complete_and_warrant(ctx, tampered, "p1")


def test_proposition_substitution_changes_binding() -> None:
    ctx = _context(
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Women",
            "rhs_entity": "Men",
            "comparison_direction": "MORE_THAN",
        },
        ["Women had a higher rate than Men."],
    )
    receipt = measure_strict_comparison(ctx, "p1")
    authority = complete_and_warrant(ctx, receipt, "p1")
    relation = derive_relation(ctx, authority)
    substituted = AuditContext(
        ctx.original_claim,
        TypedProposition.create(
            "claim-1",
            SemanticFamily.STRICT_COMPARISON,
            {
                "lhs_entity": "Women",
                "rhs_entity": "Men",
                "comparison_direction": "LESS_THAN",
            },
            text_sha256=ctx.proposition.text_sha256,
        ),
        ctx.evidence_world,
    )
    with pytest.raises(ValueError):
        derive_relation(substituted, authority)
    assert relation.categorical_relation is CategoricalRelation.SUPPORTS


def test_cross_world_relation_composition_fails_closed() -> None:
    fields = {
        "lhs_entity": "Women",
        "rhs_entity": "Men",
        "comparison_direction": "MORE_THAN",
    }
    one = _context(
        SemanticFamily.STRICT_COMPARISON,
        fields,
        ["Women had a higher rate than Men."],
        bundle_id="one",
    )
    two = _context(
        SemanticFamily.STRICT_COMPARISON,
        fields,
        ["Women had a higher rate than Men."],
        bundle_id="two",
    )
    r1 = audit(one).traces[0].relation
    r2 = audit(two).traces[0].relation
    assert r1 is not None and r2 is not None
    traces = (
        PassageTrace("p1", None, None, r1, None, None),
        PassageTrace("p1", None, None, r2, None, None),
    )
    with pytest.raises(ValueError):
        compose(one, traces)


def test_aperture_observation_is_preserved_but_non_deciding() -> None:
    fields = {
        "lhs_entity": "Women",
        "rhs_entity": "Men",
        "comparison_direction": "MORE_THAN",
    }
    unknown = _context(
        SemanticFamily.STRICT_COMPARISON,
        fields,
        ["Women had a higher rate than Men."],
        aperture=_aperture("small-search"),
    )
    limited = _context(
        SemanticFamily.STRICT_COMPARISON,
        fields,
        ["Women had a higher rate than Men."],
        aperture={
            "search_scope": {"corpus": "different-search"},
            "outcome": {"state": "known", "value": "limited"},
            "limitations": ["one source family omitted"],
        },
    )
    assert (
        unknown.evidence_world.aperture_observation()
        != limited.evidence_world.aperture_observation()
    )
    assert (
        unknown.evidence_world.evidence_world_sha256
        != limited.evidence_world.evidence_world_sha256
    )
    assert audit(unknown).conclusion is Conclusion.SUPPORTED
    assert audit(limited).conclusion is Conclusion.SUPPORTED


def test_direct_event_order_support_refute_and_scope_refusal() -> None:
    fields = {
        "left_subject": "alice",
        "left_predicate": "review",
        "left_object": "dossier",
        "left_polarity": "positive",
        "temporal_relation": "BEFORE",
        "right_subject": "bob",
        "right_predicate": "archive",
        "right_object": "dossier",
        "right_polarity": "positive",
    }
    support = _context(
        SemanticFamily.DIRECT_EVENT_ORDER,
        fields,
        ["Alice reviewed dossier before Bob archived dossier."],
    )
    refute = _context(
        SemanticFamily.DIRECT_EVENT_ORDER,
        fields,
        ["Alice reviewed dossier after Bob archived dossier."],
    )
    scoped = _context(
        SemanticFamily.DIRECT_EVENT_ORDER,
        fields,
        ["Report says Alice reviewed dossier before Bob archived dossier."],
    )
    assert audit(support).conclusion is Conclusion.SUPPORTED
    assert audit(refute).conclusion is Conclusion.CONTRADICTED
    assert audit(scoped).conclusion is Conclusion.NOT_CHECKABLE


def test_unsupported_family_does_not_fall_back_and_preserves_evidence() -> None:
    ctx = _context(
        SemanticFamily.PERMISSION_EXCEPTION,
        {"actor": "alice"},
        ["Alice may release dossier."],
    )
    result = audit(ctx)
    assert result.conclusion is Conclusion.NOT_CHECKABLE
    assert result.failure_code is FailureCode.UNSUPPORTED_SEMANTIC_FAMILY
    assert result.non_deciding_passage_ids == ("p1",)


def test_projection_matches_qualified_contract_c_shadow_shape() -> None:
    fields = {
        "lhs_entity": "Women",
        "rhs_entity": "Men",
        "comparison_direction": "MORE_THAN",
    }
    ctx = _context(
        SemanticFamily.STRICT_COMPARISON,
        fields,
        ["Women appeared in the report.", "Women had a higher rate than Men."],
    )
    result = audit(ctx)
    payload = project_contract_c_successor(
        ctx, result, semantic_implementation_sha=_SEMANTIC_SHA
    )
    assert payload["contract_c_version"] == "research-non-deciding-rc0"
    assert set(payload) == {
        "contract_c_version",
        "input",
        "producer",
        "execution",
        "propositions",
        "result_set_id",
    }
    proposition = payload["propositions"][0]
    channels = {
        item["evidence_ref"]["passage_id"]: item["channel"]
        for item in proposition["contributions"]
    }
    assert channels["p1"] == "non_deciding"
    assert channels["p2"] == "support"
    assert proposition["conclusion"]["reported_verdict"] == "supported"
    assert proposition["conclusion"]["causal_form"] == "single_necessary"
    assert proposition["conclusion"]["residual_contribution_ids"]
    assert payload["result_set_id"].startswith("result-set:")
    canonical = json.dumps(
        {key: value for key, value in payload.items() if key != "result_set_id"},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ) + "\n"
    assert payload["result_set_id"] == "result-set:" + hashlib.sha256(
        canonical.encode()
    ).hexdigest()


def test_exact_intake_rejects_changed_passage_under_stale_hash() -> None:
    text = "Women had a higher rate than Men."
    packet = {
        "original_claim": "typed claim",
        "proposition": {
            "proposition_id": "claim-1",
            "text_sha256": _hex("typed claim"),
            "semantic_family": "strict_comparison",
            "fields": {
                "lhs_entity": "Women",
                "rhs_entity": "Men",
                "comparison_direction": "MORE_THAN",
            },
        },
        "evidence_world": {
            "contract_b_version": "1.2.0",
            "bundle_id": "bundle-1",
            "bundle_hash": _tagged("bundle-1"),
            "aperture_observation": _aperture(),
            "admitted_passages": [
                {
                    "passage_id": "p1",
                    "source_id": "source-1",
                    "text": text,
                    "text_sha256": _tagged(text),
                    "source_sha256": _tagged("source-1"),
                }
            ],
        },
    }
    assert context_from_packet(packet).evidence_world.passage("p1").text == text
    changed = json.loads(json.dumps(packet))
    changed["evidence_world"]["admitted_passages"][0]["text"] = "changed"
    with pytest.raises(ValueError, match="passage hash mismatch"):
        context_from_packet(changed)
