from __future__ import annotations

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
from claim_audit_lab.cal_v1_candidate.engine import PassageTrace, compose
from claim_audit_lab.cal_v1_candidate.measurements import measure_strict_comparison
from claim_audit_lab.cal_v1_candidate.relations import derive_relation


def _context(
    family: SemanticFamily,
    fields: dict[str, str],
    texts: list[str],
    *,
    bundle_id: str = "bundle-1",
) -> AuditContext:
    passages = tuple(
        AdmittedPassage.create(f"p{index}", "source-1", text)
        for index, text in enumerate(texts, start=1)
    )
    world = EvidenceWorld(
        "1.2.0", bundle_id, f"hash-{bundle_id}", passages, "declared"
    )
    proposition = TypedProposition.create("claim-1", family, fields)
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


def test_unsupported_family_does_not_fall_back_to_legacy_rules() -> None:
    ctx = _context(
        SemanticFamily.PERMISSION_EXCEPTION,
        {"actor": "alice"},
        ["Alice may release dossier."],
    )
    result = audit(ctx)
    assert result.conclusion is Conclusion.NOT_CHECKABLE
    assert result.failure_code is FailureCode.UNSUPPORTED_SEMANTIC_FAMILY


def test_projection_preserves_non_deciding_without_laundering() -> None:
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
    payload = project_contract_c_successor(ctx, result)
    channels = {
        item["evidence_ref"]["passage_id"]: item["channel"]
        for item in payload["contributions"]
    }
    assert channels["p1"] == "non_deciding"
    assert channels["p2"] == "support"
