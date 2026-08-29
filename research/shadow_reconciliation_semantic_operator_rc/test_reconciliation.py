"""Invariant-led falsifiers for the semantic-operator reconciliation RC."""

from __future__ import annotations

from claim_audit_lab.v1.decision_model import evaluate_evidence
from claim_audit_lab.v1.semantic_operators import SemanticProbeReceipt, project_negation
from research.production_trace_decision_shadow.metamorphic_controls import (
    _direct,
    _input,
    _measurement,
    _sha,
)
from research.shadow_reconciliation_semantic_operator_rc.operator_contract import (
    a4_application,
    operator_contract_matrix,
    unresolved_refutation_validity,
)
from research.shadow_reconciliation_semantic_operator_rc.parallel_artifact import (
    build_failure_artifact,
)


def _completed_probe(claim: str, *, label: str = "entail") -> SemanticProbeReceipt:
    projection = project_negation(claim)
    assert projection.complement is not None
    return SemanticProbeReceipt(
        passage_ids=("p-refute",),
        hypothesis=projection.complement,
        label=label,  # type: ignore[arg-type]
        abstained=False,
        evidence_path="research synthetic exact probe",
        receipt_sha256=_sha(f"probe:{claim}:{projection.complement}:{label}"),
    )


def _refutation_trace(*, label: str, validity: str, eligibility: str = "eligible"):
    measurement = _measurement("p-refute", 0.01, 0.95, label)
    contribution = _direct(
        passage_id="p-refute",
        channel="refutation",
        score=0.95,
        measurement=measurement,
        label=label,
        eligibility=eligibility,
        validity=validity,
    )
    return evaluate_evidence(
        _input(
            label=label,
            admitted=("p-refute",),
            measurements=(measurement,),
            contributions=(contribution,),
        )
    )


def test_e2e08_numeric_contradiction_has_no_a4_canonical_target() -> None:
    claim = "The service meets 95 percent uptime and 40 percent capacity."
    receipt = SemanticProbeReceipt(
        passage_ids=("p-1",),
        hypothesis=None,
        label=None,
        abstained=True,
        evidence_path="run 33275342888 e2e-08 AuditTrace.negation_probe",
        receipt_sha256="sha256:3f4e19e6e628d48a788efbde9bc9270acc0a34c9163fdc91922ebb199eb688fc",
    )
    application = a4_application(
        claim=claim,
        contribution_passage_ids=("p-1",),
        receipt=receipt,
    )
    assert application.applicability == "inapplicable"
    assert application.canonical_hypothesis is None
    assert application.validity is None
    assert application.may_supply_decision_authority is False


def test_unknown_semantic_validity_cannot_decide() -> None:
    trace = _refutation_trace(label="unknown-cannot-decide", validity="unknown")
    assert trace.raw.state == "refutation_only"
    assert trace.eligible.state == "refutation_only"
    assert trace.valid.state == "read_silent"
    assert trace.decision.disposition == "abstained"
    assert trace.decision.reason_code == "semantic_validity_unknown"


def test_removing_semantic_validity_cannot_strengthen_conclusion() -> None:
    validated = _refutation_trace(label="receipt-present", validity="valid")
    missing = _refutation_trace(label="receipt-removed", validity="unknown")
    assert validated.decision.verdict == "contradicted"
    assert missing.decision.disposition == "abstained"
    assert missing.decision.verdict is None


def test_replacing_applicable_operator_with_inapplicable_loses_authority() -> None:
    lexical_claim = "The batch was released on schedule."
    lexical = a4_application(
        claim=lexical_claim,
        contribution_passage_ids=("p-refute",),
        receipt=_completed_probe(lexical_claim),
    )
    assert lexical.applicability == "applicable"
    assert lexical.validity is not None and lexical.validity.status == "valid"
    assert lexical.may_supply_decision_authority is True

    numeric_claim = "The service meets 95 percent uptime and 40 percent capacity."
    numeric = a4_application(
        claim=numeric_claim,
        contribution_passage_ids=("p-refute",),
        receipt=SemanticProbeReceipt(
            passage_ids=("p-refute",),
            hypothesis=None,
            label=None,
            abstained=True,
            evidence_path="synthetic inapplicable operator",
            receipt_sha256=_sha("numeric-inapplicable"),
        ),
    )
    assert numeric.applicability == "inapplicable"
    assert numeric.may_supply_decision_authority is False

    unresolved = unresolved_refutation_validity(
        evidence_path="synthetic inapplicable operator",
        receipt_sha256=_sha("numeric-unresolved"),
        reason="no applicable operator validates the numeric relation",
    )
    assert unresolved.status == "unknown"


def test_adding_irrelevant_evidence_cannot_strengthen_basis() -> None:
    support = _measurement("p-support", 0.90, 0.01, "irrelevant-base-rc")
    contribution = _direct(
        passage_id="p-support",
        channel="support",
        score=0.90,
        measurement=support,
        label="irrelevant-base-rc",
    )
    base = evaluate_evidence(
        _input(
            label="irrelevant-base-rc",
            admitted=("p-support",),
            measurements=(support,),
            contributions=(contribution,),
        )
    )
    irrelevant = _measurement("p-irrelevant", 0.05, 0.05, "irrelevant-added-rc")
    mutated = evaluate_evidence(
        _input(
            label="irrelevant-added-rc",
            admitted=("p-support", "p-irrelevant"),
            measurements=(support, irrelevant),
            contributions=(contribution,),
        )
    )
    assert base.decision.verdict == mutated.decision.verdict == "supported"
    assert base.decision.basis_contribution_ids == mutated.decision.basis_contribution_ids
    assert "p-irrelevant" not in " ".join(mutated.decision.basis_contribution_ids)


def test_ineligible_evidence_remains_observable_but_cannot_decide() -> None:
    trace = _refutation_trace(
        label="ineligible-refutation-rc",
        validity="valid",
        eligibility="ineligible",
    )
    assert trace.raw.state == "refutation_only"
    assert trace.eligible.state == "read_silent"
    assert trace.valid.state == "read_silent"
    assert trace.decision.disposition == "abstained"
    assert trace.decision.reason_code == "no_eligible_contribution"


def test_mixed_valid_evidence_remains_mixed() -> None:
    support = _measurement("p-support", 0.91, 0.01, "mixed-rc")
    refute = _measurement("p-refute", 0.01, 0.93, "mixed-rc")
    cs = _direct(
        passage_id="p-support",
        channel="support",
        score=0.91,
        measurement=support,
        label="mixed-rc",
    )
    cr = _direct(
        passage_id="p-refute",
        channel="refutation",
        score=0.93,
        measurement=refute,
        label="mixed-rc",
    )
    trace = evaluate_evidence(
        _input(
            label="mixed-rc",
            admitted=("p-support", "p-refute"),
            measurements=(support, refute),
            contributions=(cs, cr),
        )
    )
    assert trace.valid.state == "mixed"
    assert trace.decision.disposition == "abstained"
    assert trace.decision.reason_code == "mixed_valid_evidence"
    assert set(trace.decision.basis_contribution_ids) == {
        cs.contribution_id,
        cr.contribution_id,
    }


def test_execution_failure_is_not_epistemic_abstention() -> None:
    artifact = build_failure_artifact(
        claim_id="execution-failure-control",
        failure_class="FixtureLoadError",
        failure_detail="synthetic bootstrap failure before model measurement",
        execution_head_sha="f" * 40,
    )
    assert artifact.execution.status == "failed"
    assert artifact.decision_or_abstention is None
    assert artifact.raw_evidence_state is None
    assert artifact.unknowns == ()


def test_operator_matrix_covers_preregistered_phenomena() -> None:
    observed = {str(row["phenomenon"]) for row in operator_contract_matrix()}
    required = {
        "direct_entailment",
        "direct_contradiction",
        "explicit_negation",
        "numeric_mismatch",
        "threshold_mismatch",
        "quantity_mismatch",
        "categorical_incompatibility",
        "scope_mismatch",
        "quantifier_mismatch",
        "degree_mismatch",
        "multi_passage_composition",
        "mixed_support_refutation",
        "out_of_scope",
        "no_applicable_operator",
    }
    assert required <= observed
