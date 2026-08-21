"""Operator-facing reason glosses for the abstention vocabulary.

The property under test is that every ``VerdictReason`` CAL can emit has its own
operator gloss. The fallback in ``derive_reason`` is a safety net, not a
destination: an abstention that lands there tells a reviewer only that CAL
abstained, which is the one thing they already knew.
"""

from __future__ import annotations

from typing import get_args

import pytest

from claim_audit_lab.ui.reasons import derive_reason
from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.models import AuditTrace, RuleFired, VerdictReason

_CONFIG = load_default_audit_config()


def _abstention_trace(reason: VerdictReason) -> AuditTrace:
    return AuditTrace.model_validate(
        {
            "claim_id": f"ui-{reason}",
            "claim_text": "The platform validates submitted input records.",
            "retrieval": [{"passage_id": "p-1", "score": 0.91}],
            "entailment": [],
            "features": {
                "sentence_type": "declarative",
                "claim_token_count": 8,
                "has_explicit_negation": False,
                "has_universal_quantifier": False,
                "compound_claim": False,
                "modal_strength": "asserts",
                "numerical_values": [],
            },
            "support_signal": {
                "label": "neutral",
                "max_entailment_score": 0.0,
                "contributing_passage_id": None,
            },
            "rules_fired": [],
            "verdict": {
                "support_verdict": "not_checkable",
                "support_verdict_reason": reason,
                "audit_confidence": "low",
            },
            "audit_config_hash": "sha256:" + "0" * 64,
            "library_version": "0.3.0",
        }
    )


@pytest.mark.parametrize("reason", get_args(VerdictReason))
def test_every_verdict_reason_has_its_own_gloss(reason: VerdictReason) -> None:
    """Parametrized over the Literal itself, so a new reason fails until it is glossed."""
    result = derive_reason(_abstention_trace(reason), _CONFIG)
    assert result["verdict"] == "not_checkable"
    assert result["reason_code"] != "NOT_ESTABLISHED", (
        f"{reason!r} fell through to the generic fallback — add it to _ABSTENTION_GLOSS"
    )
    assert reason not in result["detail"], "the gloss should read as prose, not echo the key"


def test_conflicting_evidence_tells_the_reviewer_to_read_both() -> None:
    """A5's abstention is actionable only if the operator text says what to do."""
    result = derive_reason(_abstention_trace("conflicting_evidence"), _CONFIG)
    assert result["reason_code"] == "EVIDENCE_DISAGREES"
    assert "both" in result["detail"].lower()
    assert result["triage_color"] == "amber"


def _verdict_trace(verdict: str, **verdict_fields: object) -> AuditTrace:
    trace = _abstention_trace("no_entail_signal")
    return trace.model_copy(
        update={
            "verdict": trace.verdict.model_copy(
                update={
                    "support_verdict": verdict,
                    "support_verdict_reason": None,
                    **verdict_fields,
                }
            )
        }
    )


@pytest.mark.parametrize(
    ("verdict", "code"),
    [
        ("supported", "SUPPORTED"),
        ("partially_supported", "PARTIALLY_SUPPORTED"),
        ("unsupported", "UNSUPPORTED"),
        ("contradicted", "CONTRADICTED"),
    ],
)
def test_every_non_abstention_verdict_has_a_reason_code(verdict: str, code: str) -> None:
    result = derive_reason(_verdict_trace(verdict), _CONFIG)
    assert result["reason_code"] == code
    assert result["verdict"] == verdict
    assert result["detail"]
    assert result["triage_action"] == result["routing"]


def test_reason_carries_the_rules_that_produced_the_verdict() -> None:
    """Operator text without provenance is an opinion; CAL's has to cite the rule."""
    trace = _abstention_trace("conflicting_evidence").model_copy(
        update={
            "rules_fired": [
                RuleFired(
                    rule_id="A5_conflicting_evidence",
                    reason="p-1 entails at 0.95 and p-2 contradicts at 0.96",
                )
            ]
        }
    )
    result = derive_reason(trace, _CONFIG)
    assert any("A5_conflicting_evidence" in line for line in result["provenance"])


def test_reason_works_without_a_config() -> None:
    """A caller holding only a trace still gets a correct reason, minus the numbers."""
    result = derive_reason(_abstention_trace("conflicting_evidence"))
    assert result["reason_code"] == "EVIDENCE_DISAGREES"
