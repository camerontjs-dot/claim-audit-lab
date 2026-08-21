"""Focused E2 contracts for caller-declared explicit claim structure."""

from __future__ import annotations

from collections.abc import Callable
from itertools import product
from typing import Literal, cast

import pytest
from pydantic import ValidationError

from claim_audit_lab import __version__
from claim_audit_lab.v1 import (
    canonical_explicit_claim_request_json,
    hash_explicit_claim_request,
    runner,
    serialize_explicit_claim_trace,
)
from claim_audit_lab.v1.config import hash_audit_config, load_default_audit_config
from claim_audit_lab.v1.explicit_claims import (
    AtomProvenance,
    ExplicitClaimAtom,
    ExplicitClaimRequest,
    ExplicitClaimTrace,
    ParentAggregationTrace,
    SupportVerdict,
    aggregate_explicit_claim_verdicts,
    run_explicit_claim_audit,
)
from claim_audit_lab.v1.models import (
    AuditConfig,
    AuditRequest,
    AuditTrace,
    ExtractedFeatures,
    Passage,
    SupportSignal,
    Verdict,
)

_DEGREES: tuple[SupportVerdict, ...] = (
    "supported",
    "partially_supported",
    "unsupported",
    "contradicted",
    "not_checkable",
)


def _provenance(reference_id: str = "construction-card") -> AtomProvenance:
    return AtomProvenance(
        origin="source_contract",
        reference_id=reference_id,
        reference_sha256=f"sha256:{'a' * 64}",
    )


def _atom(atom_id: str, text: str) -> ExplicitClaimAtom:
    return ExplicitClaimAtom(atom_id=atom_id, claim_text=text, provenance=_provenance(atom_id))


def _request(
    *,
    operator: Literal["single", "all_of"] = "all_of",
    atoms: list[ExplicitClaimAtom] | None = None,
    parent_id: str = "parent-1",
    parent_text: str = "Every declared valve was inspected.",
) -> ExplicitClaimRequest:
    return ExplicitClaimRequest(
        parent_claim_id=parent_id,
        parent_claim_text=parent_text,
        operator=operator,
        atoms=atoms
        or [
            _atom("atom-1", "Valve V1 was inspected."),
            _atom("atom-2", "Valve V2 was inspected."),
        ],
        passages=[
            Passage(passage_id="passage-1", text="The inspection record covers V1 and V2."),
            Passage(passage_id="passage-2", text="A second bounded source."),
        ],
        audit_config=load_default_audit_config(),
    )


def _atomic_trace(
    atom_id: str,
    text: str,
    config: AuditConfig,
    verdict: Verdict,
    *,
    library_version: str = __version__,
) -> AuditTrace:
    return AuditTrace(
        claim_id=atom_id,
        claim_text=text,
        retrieval=[],
        entailment=[],
        features=ExtractedFeatures(),
        support_signal=SupportSignal(label="neutral", max_entailment_score=0.0),
        rules_fired=[],
        verdict=verdict,
        audit_config_hash=hash_audit_config(config),
        library_version=library_version,
    )


def _auditor(verdicts: dict[str, Verdict]) -> Callable[[AuditRequest], AuditTrace]:
    def audit(request: AuditRequest) -> AuditTrace:
        return _atomic_trace(
            request.claim_id,
            request.claim_text,
            request.audit_config,
            verdicts[request.claim_id],
        )

    return audit


def _expected_all_of_degree(first: SupportVerdict, second: SupportVerdict) -> SupportVerdict:
    if "contradicted" in {first, second}:
        return "contradicted"
    if first == second == "supported":
        return "supported"
    if "supported" in {first, second} or "partially_supported" in {first, second}:
        return "partially_supported"
    if "unsupported" in {first, second}:
        return "unsupported"
    return "not_checkable"


def _trace_from_request(request: ExplicitClaimRequest) -> ExplicitClaimTrace:
    verdicts = {atom.atom_id: Verdict(support_verdict="supported") for atom in request.atoms}
    return run_explicit_claim_audit(
        request,
        auditor=_auditor(verdicts),
    )


def test_strict_round_trips_extra_field_rejection_and_public_helpers() -> None:
    request = _request()

    assert ExplicitClaimRequest.model_validate_json(request.model_dump_json()) == request
    assert canonical_explicit_claim_request_json(request).startswith("{")
    assert hash_explicit_claim_request(request).startswith("sha256:")
    with pytest.raises(ValidationError, match="extra_forbidden"):
        ExplicitClaimRequest.model_validate({**request.model_dump(), "unexpected": "drift"})
    with pytest.raises(ValidationError, match="lowercase sha256"):
        AtomProvenance(
            origin="operator_declared",
            reference_id="operator-note",
            reference_sha256=f"sha256:{'A' * 64}",
        )

    trace = _trace_from_request(request)
    assert type(trace).model_validate_json(trace.model_dump_json()) == trace
    assert serialize_explicit_claim_trace(trace).startswith("{")
    with pytest.raises(ValidationError, match="extra_forbidden"):
        type(trace).model_validate({**trace.model_dump(), "unexpected": "drift"})


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"operator": "single"}, "single requires exactly one atom"),
        (
            {"operator": "all_of", "atoms": [_atom("atom-1", "Only one.")]},
            "all_of requires at least two atoms",
        ),
        (
            {
                "operator": "single",
                "atoms": [_atom("atom-1", "Different text.")],
                "parent_text": "Parent text.",
            },
            "parent/atom text identity",
        ),
        (
            {"atoms": [_atom("parent-1", "One."), _atom("atom-2", "Two.")]},
            "cannot equal parent_claim_id",
        ),
        (
            {"atoms": [_atom("atom-1", "One."), _atom("atom-1", "Two.")]},
            "atom_ids must be unique",
        ),
        (
            {"atoms": [_atom("atom-1", "Same."), _atom("atom-2", "Same.")]},
            "atom claim_text values must be unique",
        ),
    ],
)
def test_fail_closed_request_shape_invariants(kwargs: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        _request(**kwargs)


def test_blank_and_boundary_whitespace_normalization_is_consistent() -> None:
    atom = _atom(" atom-1 ", " Valve V1 was inspected. ")
    request = _request(
        operator="single",
        parent_id=" parent-1 ",
        parent_text=" Valve V1 was inspected. ",
        atoms=[atom],
    )

    assert request.parent_claim_id == "parent-1"
    assert request.parent_claim_text == "Valve V1 was inspected."
    assert request.atoms[0].atom_id == "atom-1"
    assert request.atoms[0].claim_text == "Valve V1 was inspected."
    assert request.atoms[0].provenance.reference_id == "atom-1"
    for model, kwargs in [
        (
            AtomProvenance,
            {
                "origin": "source_contract",
                "reference_id": " ",
                "reference_sha256": f"sha256:{'a' * 64}",
            },
        ),
        (ExplicitClaimAtom, {"atom_id": " ", "claim_text": "Text.", "provenance": _provenance()}),
        (ExplicitClaimAtom, {"atom_id": "atom", "claim_text": " ", "provenance": _provenance()}),
        (ExplicitClaimRequest, {**request.model_dump(), "parent_claim_id": " "}),
    ]:
        with pytest.raises(ValidationError, match="must be non-empty"):
            model.model_validate(kwargs)


def test_fail_closed_duplicate_and_blank_passage_ids() -> None:
    payload = _request().model_dump()
    payload["passages"] = [
        {"passage_id": "p", "text": "One."},
        {"passage_id": "p", "text": "Two."},
    ]
    with pytest.raises(ValidationError, match="passage_ids must be unique"):
        ExplicitClaimRequest.model_validate(payload)
    payload["passages"] = [{"passage_id": " ", "text": "One."}]
    with pytest.raises(ValidationError, match="passage_id values must be non-empty"):
        ExplicitClaimRequest.model_validate(payload)


def test_atoms_are_audited_independently_in_input_order_with_shared_inputs() -> None:
    request = _request()
    seen: list[AuditRequest] = []

    def audit(atomic_request: AuditRequest) -> AuditTrace:
        seen.append(atomic_request)
        return _atomic_trace(
            atomic_request.claim_id,
            atomic_request.claim_text,
            atomic_request.audit_config,
            Verdict(support_verdict="supported", audit_confidence="high"),
        )

    trace = run_explicit_claim_audit(request, auditor=audit)

    assert [item.claim_id for item in seen] == ["atom-1", "atom-2"]
    assert all(item.passages == request.passages for item in seen)
    assert all(item.audit_config is request.audit_config for item in seen)
    assert trace.parent_aggregation.atom_support_verdicts == ["supported", "supported"]


@pytest.mark.parametrize("first,second", list(product(_DEGREES, repeat=2)))
def test_all_25_ordered_two_atom_parent_table(
    first: SupportVerdict, second: SupportVerdict
) -> None:
    aggregation = aggregate_explicit_claim_verdicts(
        "all_of",
        [Verdict(support_verdict=first), Verdict(support_verdict=second)],
    )

    assert aggregation.verdict.support_verdict == _expected_all_of_degree(first, second)
    assert aggregation.atom_support_verdicts == [first, second]


def test_invalid_runtime_aggregation_operator_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported explicit-claim operator"):
        aggregate_explicit_claim_verdicts(
            cast(Literal["single", "all_of"], "any_of"),
            [Verdict(support_verdict="supported")],
        )


@pytest.mark.parametrize(
    ("operator", "degrees", "message"),
    [
        ("single", ["supported", "supported"], "single aggregation requires exactly one"),
        ("all_of", ["supported"], "all_of aggregation requires at least two"),
    ],
)
def test_standalone_aggregation_cardinality_is_fail_closed(
    operator: Literal["single", "all_of"], degrees: list[SupportVerdict], message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        ParentAggregationTrace(
            operator=operator,
            atom_support_verdicts=degrees,
            rule_id="ECA-TEST",
            reason="Test receipt.",
            verdict=Verdict(support_verdict="supported"),
        )


def test_single_copies_every_axis_exactly() -> None:
    atomic = Verdict(
        support_verdict="partially_supported",
        audit_flags=["inferred", "overstated"],
        citation_status="partial",
        audit_confidence="low",
    )

    aggregation = aggregate_explicit_claim_verdicts("single", [atomic])

    assert aggregation.verdict is atomic
    assert aggregation.rule_id == "ECA-SINGLE-COPY"


def test_all_of_aggregates_fixed_flag_citation_confidence_and_reason_rules() -> None:
    aggregation = aggregate_explicit_claim_verdicts(
        "all_of",
        [
            Verdict(
                support_verdict="not_checkable",
                support_verdict_reason="no_evidence",
                audit_flags=["coverage_loss", "inferred"],
                citation_status="not_applicable",
                audit_confidence="high",
            ),
            Verdict(
                support_verdict="not_checkable",
                support_verdict_reason="no_evidence",
                audit_flags=["overstated", "inferred"],
                citation_status="partial",
                audit_confidence="low",
            ),
        ],
    )

    assert aggregation.verdict.audit_flags == ["overstated", "inferred", "coverage_loss"]
    assert aggregation.verdict.citation_status == "partial"
    assert aggregation.verdict.audit_confidence == "low"
    assert aggregation.verdict.support_verdict_reason == "no_evidence"

    assert (
        aggregate_explicit_claim_verdicts(
            "all_of",
            [
                Verdict(support_verdict="unsupported", citation_status="partial"),
                Verdict(support_verdict="unsupported", citation_status="wrong_source"),
            ],
        ).verdict.citation_status
        == "wrong_source"
    )
    assert (
        aggregate_explicit_claim_verdicts(
            "all_of",
            [
                Verdict(support_verdict="unsupported", citation_status="correct"),
                Verdict(support_verdict="unsupported", citation_status="missing_needed"),
            ],
        ).verdict.citation_status
        == "missing_needed"
    )

    different_reasons = aggregate_explicit_claim_verdicts(
        "all_of",
        [
            Verdict(support_verdict="not_checkable", support_verdict_reason="no_evidence"),
            Verdict(support_verdict="not_checkable", support_verdict_reason="no_entail_signal"),
        ],
    )
    assert different_reasons.verdict.support_verdict_reason is None


@pytest.mark.parametrize(
    "drift", ["claim_id", "claim_text", "audit_config_hash", "library_version"]
)
def test_auditor_binding_drift_rejects_the_whole_request(drift: str) -> None:
    request = _request()

    def audit(atomic_request: AuditRequest) -> AuditTrace:
        trace = _atomic_trace(
            atomic_request.claim_id,
            atomic_request.claim_text,
            atomic_request.audit_config,
            Verdict(support_verdict="supported"),
        )
        if drift == "claim_id":
            return trace.model_copy(update={"claim_id": "different-atom"})
        if drift == "claim_text":
            return trace.model_copy(update={"claim_text": "Different text."})
        if drift == "audit_config_hash":
            return trace.model_copy(update={"audit_config_hash": f"sha256:{'b' * 64}"})
        return trace.model_copy(update={"library_version": "other-version"})

    with pytest.raises(ValueError, match="drift"):
        run_explicit_claim_audit(request, auditor=audit)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda payload: payload.update({"library_version": "other-version"}), "library_version"),
        (
            lambda payload: payload["parent_aggregation"].update({"rule_id": "ECA-TAMPERED"}),
            "parent aggregation does not match",
        ),
        (
            lambda payload: (
                payload["parent_aggregation"]["verdict"].update({"citation_status": "correct"}),
                payload["verdict"].update({"citation_status": "correct"}),
            ),
            "parent aggregation does not match",
        ),
    ],
)
def test_parsed_trace_rejects_library_and_complete_aggregation_drift(
    mutation: Callable[[dict[str, object]], None], message: str
) -> None:
    payload = _trace_from_request(_request()).model_dump()
    mutation(payload)

    with pytest.raises(ValidationError, match=message):
        ExplicitClaimTrace.model_validate(payload)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda payload: (
                payload["atom_audits"][1].update({"atom_id": "atom-1"}),
                payload["atom_audits"][1]["audit_trace"].update({"claim_id": "atom-1"}),
            ),
            "atom_ids must be unique",
        ),
        (
            lambda payload: (
                payload["atom_audits"][1].update({"claim_text": "Valve V1 was inspected."}),
                payload["atom_audits"][1]["audit_trace"].update(
                    {"claim_text": "Valve V1 was inspected."}
                ),
            ),
            "atom claim_text values must be unique",
        ),
        (
            lambda payload: payload.update({"parent_claim_id": "atom-1"}),
            "cannot equal parent_claim_id",
        ),
        (
            lambda payload: payload.update({"parent_claim_id": " "}),
            "must be non-empty",
        ),
    ],
)
def test_parsed_trace_enforces_locally_verifiable_request_shape(
    mutate: Callable[[dict[str, object]], None], message: str
) -> None:
    payload = _trace_from_request(_request()).model_dump()
    mutate(payload)

    with pytest.raises(ValidationError, match=message):
        ExplicitClaimTrace.model_validate(payload)


def test_repeat_serialized_trace_is_byte_identical() -> None:
    request = _request()
    verdicts = {
        "atom-1": Verdict(support_verdict="supported", audit_confidence="high"),
        "atom-2": Verdict(support_verdict="unsupported", audit_confidence="low"),
    }

    first = run_explicit_claim_audit(request, auditor=_auditor(verdicts))
    second = run_explicit_claim_audit(request, auditor=_auditor(verdicts))

    assert serialize_explicit_claim_trace(first) == serialize_explicit_claim_trace(second)
    assert first.request_sha256 == second.request_sha256


def test_default_wrapper_delegates_without_loading_a_real_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = _request()
    calls: list[AuditRequest] = []

    def fake_default_audit(atomic_request: AuditRequest) -> AuditTrace:
        calls.append(atomic_request)
        return _atomic_trace(
            atomic_request.claim_id,
            atomic_request.claim_text,
            atomic_request.audit_config,
            Verdict(support_verdict="supported"),
        )

    monkeypatch.setattr(runner, "run_default_audit", fake_default_audit)
    trace = runner.run_default_explicit_claim_audit(request)

    assert [call.claim_id for call in calls] == ["atom-1", "atom-2"]
    assert trace.verdict.support_verdict == "supported"


def test_slg04_finite_scope_is_caller_declared_without_case_logic() -> None:
    request = _request(
        parent_id="finite-valve-roster",
        parent_text="Every listed valve passed inspection.",
        atoms=[
            _atom("valve-v1", "Valve V1 passed inspection."),
            _atom("valve-v2", "Valve V2 passed inspection."),
            _atom("valve-v3", "Valve V3 passed inspection."),
        ],
    )
    trace = _trace_from_request(request)

    assert trace.verdict.support_verdict == "supported"
    assert trace.parent_aggregation.atom_support_verdicts == ["supported"] * 3
