from __future__ import annotations

import hashlib

from claim_audit_lab.production_v1.semantic.engine import audit
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    Conclusion,
    EvidenceWorld,
    FailureCode,
    SemanticFamily,
    TypedProposition,
)


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return f"sha256:{_hex(value)}"


def _context(
    family: SemanticFamily,
    fields: dict[str, str],
    texts: tuple[str, ...],
) -> AuditContext:
    passages = tuple(
        AdmittedPassage.create(f"p{index}", "source-1", text)
        for index, text in enumerate(texts, start=1)
    )
    world = EvidenceWorld.create(
        contract_b_version="1.2.0",
        bundle_id="convergence-bundle",
        bundle_hash=_tagged("convergence-bundle"),
        admitted_passages=passages,
        aperture_observation={
            "search_scope": {"corpus": "convergence-fixture"},
            "outcome": {"state": "unknown", "value": None},
            "limitations": [],
        },
    )
    proposition = TypedProposition.create(
        proposition_id="claim-1",
        semantic_family=family,
        fields=fields,
        text_sha256=_hex("typed claim"),
    )
    return AuditContext("typed claim", proposition, world)


def _event_fields(*, left_polarity: str = "positive") -> dict[str, str]:
    return {
        "left_subject": "alice",
        "left_predicate": "review",
        "left_object": "dossier",
        "left_polarity": left_polarity,
        "temporal_relation": "BEFORE",
        "right_subject": "bob",
        "right_predicate": "archive",
        "right_object": "dossier",
        "right_polarity": "positive",
    }


def test_negative_event_polarity_is_unresolved_not_deciding() -> None:
    context = _context(
        SemanticFamily.DIRECT_EVENT_ORDER,
        _event_fields(left_polarity="negative"),
        ("Alice did not review dossier before Bob archived dossier.",),
    )

    result = audit(context)

    assert result.conclusion is Conclusion.NOT_CHECKABLE
    assert result.failure_code is FailureCode.RELATION_UNRESOLVED
    assert result.traces[0].relation is not None
    assert result.traces[0].relation.categorical_relation.value == "UNRESOLVED"


def test_unresolved_relation_prevents_support_winner() -> None:
    context = _context(
        SemanticFamily.DIRECT_EVENT_ORDER,
        _event_fields(),
        (
            "Alice reviewed dossier before Bob archived dossier.",
            "Alice did not review dossier before Bob archived dossier.",
        ),
    )

    result = audit(context)

    assert result.conclusion is Conclusion.NOT_CHECKABLE
    assert result.failure_code is FailureCode.RELATION_UNRESOLVED
    categories = {
        trace.relation.categorical_relation.value for trace in result.traces if trace.relation
    }
    assert categories == {
        "SUPPORTS",
        "UNRESOLVED",
    }


def test_irrelevant_only_relation_is_no_deciding_relation() -> None:
    context = _context(
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Women",
            "rhs_entity": "Men",
            "comparison_direction": "MORE_THAN",
        },
        ("Cats had a higher rate than Dogs.",),
    )

    result = audit(context)

    assert result.conclusion is Conclusion.NOT_CHECKABLE
    assert result.failure_code is FailureCode.NO_DECIDING_RELATION
    assert result.traces[0].relation is not None
    assert result.traces[0].relation.categorical_relation.value == "IRRELEVANT"


def test_measurement_not_applicable_remains_localized() -> None:
    context = _context(
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Women",
            "rhs_entity": "Men",
            "comparison_direction": "MORE_THAN",
        },
        ("The report describes annual enrollment totals.",),
    )

    result = audit(context)

    assert result.conclusion is Conclusion.NOT_CHECKABLE
    assert result.failure_code is FailureCode.MEASUREMENT_NOT_APPLICABLE
    assert result.traces[0].failure_code is FailureCode.MEASUREMENT_NOT_APPLICABLE
