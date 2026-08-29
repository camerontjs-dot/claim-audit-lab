"""Promotion tests for the minimal Contract-C 1.0.0 CAL exporter."""

from __future__ import annotations

import copy
import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from claim_audit_lab.auditor import audit_claims
from claim_audit_lab.contracts.adapter import (
    adapt_bundle_to_pipeline,
    build_claim_evidence_scopes,
)
from claim_audit_lab.contracts.bundle_loader import BundleContents, load_bundle
from claim_audit_lab.contracts.contract_c import (
    CONTRACT_C_SEMANTIC_IMPLEMENTATION_SHA,
    ContractCExportError,
    canonical_bytes,
    export_contract_c,
    export_contract_c_bytes,
)
from claim_audit_lab.models import (
    Claim,
    EvidenceCandidate,
    EvidenceExcerpt,
)
from claim_audit_lab.policy import CAL_RULES_V1_2_0
from claim_audit_lab.rules import assess_claim_support

FIXTURE_BUNDLE = (
    Path(__file__).parent / "fixtures" / "cb" / "evidence-bundle-minimal"
)
POLICY_SHA256 = (
    "88f007c96f3acf63a191556fe7fa46b80b37e9fcb5224ec1e90fb626a061104d"
)


def _production_run(
    tmp_path: Path,
) -> tuple[BundleContents, list, object, object]:
    contents = load_bundle(
        FIXTURE_BUNDLE,
        deviations_dir=tmp_path / "deviations",
    )
    claims, evidence_bundle, audit_config = adapt_bundle_to_pipeline(contents)
    assessments = audit_claims(
        claims,
        evidence_bundle,
        audit_config,
        evidence_scopes=build_claim_evidence_scopes(contents),
    )
    return contents, assessments, evidence_bundle, audit_config


def test_exporter_is_deterministic_and_exactly_binds_cal_policy_and_contract_b(
    tmp_path: Path,
) -> None:
    contents, assessments, evidence_bundle, audit_config = _production_run(
        tmp_path
    )

    first = export_contract_c_bytes(
        contents=contents,
        assessments=assessments,
        evidence_bundle=evidence_bundle,
        audit_config=audit_config,
    )
    second = export_contract_c_bytes(
        contents=contents,
        assessments=assessments,
        evidence_bundle=evidence_bundle,
        audit_config=audit_config,
    )

    assert first == second
    result = export_contract_c(
        contents=contents,
        assessments=assessments,
        evidence_bundle=evidence_bundle,
        audit_config=audit_config,
    )
    assert first == canonical_bytes(result)
    assert result["contract_c_version"] == "1.0.0"
    assert result["input"]["contract_b"] == {
        "contract_version": contents.manifest.schema_version,
        "bundle_id": contents.manifest.bundle_id,
        "bundle_hash": contents.manifest.bundle.bundle_hash,
    }
    assert (
        result["producer"]["semantic_implementation_sha"]
        == CONTRACT_C_SEMANTIC_IMPLEMENTATION_SHA
    )
    assert result["producer"]["policy"]["sha256"] == POLICY_SHA256
    assert result["producer"]["policy"]["canonical"] == {
        "config_id": "cal-rules-v1.2.0",
        "candidate_admission": 0.4,
        "partial_support": 0.55,
        "sourced_support": 0.8,
        "counterevidence_weight": 0.3,
        "false_caution_detection": True,
        "false_caution_threshold": 0.85,
        "overstated_detection": True,
        "needs_source_detection": True,
        "require_passage_level_match": True,
    }
    body = copy.deepcopy(result)
    observed_id = body.pop("result_set_id")
    expected_id = "result-set:" + hashlib.sha256(
        canonical_bytes(body)
    ).hexdigest()
    assert observed_id == expected_id


def test_exporter_preserves_reference_measurement_and_not_performed_state(
    tmp_path: Path,
) -> None:
    contents, assessments, evidence_bundle, audit_config = _production_run(
        tmp_path
    )
    result = export_contract_c(
        contents=contents,
        assessments=assessments,
        evidence_bundle=evidence_bundle,
        audit_config=audit_config,
    )

    proposition = result["propositions"][0]
    assert proposition["execution"] == {
        "state": "completed",
        "completion": "assessed",
    }
    assert set(proposition["assessments"]) == {
        "eligibility",
        "semantic_validity",
        "aperture_completeness",
        "temporal_applicability",
    }
    assert all(
        value == {"state": "not_performed"}
        for value in proposition["assessments"].values()
    )
    assert (
        proposition["measurement"]["kind"]
        == "cal_v0_2_aggregate_support_signal"
    )
    assert proposition["measurement"]["basis_contribution_ids"]
    contribution = proposition["contributions"][0]
    assert contribution["evidence_ref"]["source_id"] == "src-001"
    assert contribution["evidence_ref"]["passage_id"] == "pass-001"
    assert contribution["evidence_ref"]["passage_sha256"].startswith(
        "sha256:"
    )
    assert "citation" not in proposition["assessments"]
    assert "reassessment" not in proposition


def test_exporter_fails_closed_on_unresolved_contract_b_reference(
    tmp_path: Path,
) -> None:
    contents, assessments, evidence_bundle, audit_config = _production_run(
        tmp_path
    )
    assessment = assessments[0].model_copy(
        update={
            "candidate_evidence": [
                assessments[0].candidate_evidence[0].model_copy(
                    update={"excerpt_id": "src-001/missing"}
                )
            ]
        }
    )

    with pytest.raises(
        ContractCExportError,
        match="cannot be resolved to Contract B",
    ):
        export_contract_c(
            contents=contents,
            assessments=[assessment],
            evidence_bundle=evidence_bundle,
            audit_config=audit_config,
        )


def test_tied_co_maxima_export_as_independent_sufficient_alternatives(
    tmp_path: Path,
) -> None:
    contents, _assessments, evidence_bundle, audit_config = _production_run(
        tmp_path
    )
    claim = Claim(
        id="clm-tied",
        text=(
            "Accelerated approval applications require a submission package."
        ),
        claim_type="capability",
    )
    source = evidence_bundle.sources[0]
    first_excerpt = source.excerpts[0].model_copy(
        update={
            "id": "src-001/pass-a",
            "text": claim.text,
        }
    )
    second_excerpt = EvidenceExcerpt(
        id="src-001/pass-b",
        text=claim.text,
    )
    tied_bundle = evidence_bundle.model_copy(
        update={
            "sources": [
                source.model_copy(
                    update={"excerpts": [first_excerpt, second_excerpt]}
                )
            ]
        }
    )
    candidate_a = EvidenceCandidate(
        source_id="src-001",
        excerpt_id="src-001/pass-a",
        score=0.8,
        source_reliability="high",
    )
    candidate_b = EvidenceCandidate(
        source_id="src-001",
        excerpt_id="src-001/pass-b",
        score=0.8,
        source_reliability="high",
    )
    assessment = assess_claim_support(
        claim,
        tied_bundle,
        [candidate_a, candidate_b],
        audit_config,
        policy=CAL_RULES_V1_2_0,
    )
    base_passage = contents.passages["src-001"][0]
    tied_contents = replace(
        contents,
        claims=[
            contents.claims[0].model_copy(
                update={"claim_id": "clm-tied", "claim_text": claim.text}
            )
        ],
        passages={
            "src-001": [
                base_passage.model_copy(
                    update={
                        "passage_id": "pass-a",
                        "passage_text": first_excerpt.text,
                        "passage_hash": "sha256:" + "a" * 64,
                    }
                ),
                base_passage.model_copy(
                    update={
                        "passage_id": "pass-b",
                        "passage_text": second_excerpt.text,
                        "passage_hash": "sha256:" + "b" * 64,
                    }
                ),
            ]
        },
    )

    result = export_contract_c(
        contents=tied_contents,
        assessments=[assessment],
        evidence_bundle=tied_bundle,
        audit_config=audit_config,
    )
    proposition = result["propositions"][0]
    assert (
        proposition["conclusion"]["causal_form"]
        == "independent_sufficient_alternatives"
    )
    assert len(proposition["conclusion"]["basis_members"]) == 2
    assert len(proposition["measurement"]["basis_contribution_ids"]) == 2
    assert proposition["conclusion"]["residual_contribution_ids"] == []


def test_unclassified_early_return_is_completed_not_checkable_not_failure(
    tmp_path: Path,
) -> None:
    contents, _assessments, evidence_bundle, audit_config = _production_run(
        tmp_path
    )
    claim = Claim(
        id="clm-early",
        text="Maybe useful someday",
        claim_type="unclassified",
    )
    assessment = assess_claim_support(
        claim,
        evidence_bundle,
        [],
        audit_config,
    )
    early_contents = replace(
        contents,
        claims=[
            contents.claims[0].model_copy(
                update={"claim_id": claim.id, "claim_text": claim.text}
            )
        ],
    )

    result = export_contract_c(
        contents=early_contents,
        assessments=[assessment],
        evidence_bundle=evidence_bundle,
        audit_config=audit_config,
    )
    proposition = result["propositions"][0]
    assert proposition["execution"] == {
        "state": "completed",
        "completion": "not_checkable",
    }
    assert proposition["conclusion"]["reported_verdict"] == "not_checkable"
    assert proposition["conclusion"]["basis_members"] == [
        {"namespace": "state", "id": "state:claim_type:unclassified"}
    ]
    assert proposition["measurement"] is None


def test_credential_missing_source_uses_producer_owned_state_basis(
    tmp_path: Path,
) -> None:
    contents, _assessments, evidence_bundle, audit_config = _production_run(
        tmp_path
    )
    claim = Claim(
        id="clm-credential",
        text="The author is board certified.",
        claim_type="credential",
    )
    assessment = assess_claim_support(
        claim,
        evidence_bundle,
        [],
        audit_config,
    )
    credential_contents = replace(
        contents,
        claims=[
            contents.claims[0].model_copy(
                update={"claim_id": claim.id, "claim_text": claim.text}
            )
        ],
    )

    result = export_contract_c(
        contents=credential_contents,
        assessments=[assessment],
        evidence_bundle=evidence_bundle,
        audit_config=audit_config,
    )
    proposition = result["propositions"][0]
    assert proposition["conclusion"]["reported_verdict"] == "needs_source"
    assert proposition["conclusion"]["basis_members"] == [
        {
            "namespace": "state",
            "id": "state:direct_support_contexts_empty",
        }
    ]
    assert proposition["conclusion"]["rule_roles"] == [
        {
            "rule_id": (
                "rule-role:clm-credential:credential_missing_source"
            ),
            "code": "credential_missing_source",
            "terminal_role": "causal",
        }
    ]


def test_absolute_wording_with_counterevidence_preserves_joint_state_basis(
    tmp_path: Path,
) -> None:
    contents, _assessments, evidence_bundle, audit_config = _production_run(
        tmp_path
    )
    claim = Claim(
        id="clm-joint",
        text="The system guarantees approval.",
        claim_type="prediction",
    )
    source = evidence_bundle.sources[0]
    support_excerpt = EvidenceExcerpt(
        id="src-001/pass-support",
        text=claim.text,
    )
    counter_excerpt = EvidenceExcerpt(
        id="src-001/pass-counter",
        text="The system has a known limitation.",
    )
    joint_bundle = evidence_bundle.model_copy(
        update={
            "sources": [
                source.model_copy(
                    update={
                        "excerpts": [support_excerpt, counter_excerpt]
                    }
                )
            ]
        }
    )
    support = EvidenceCandidate(
        source_id="src-001",
        excerpt_id=support_excerpt.id,
        score=1.0,
        source_reliability="high",
    )
    counter = EvidenceCandidate(
        source_id="src-001",
        excerpt_id=counter_excerpt.id,
        score=0.5,
        source_reliability="high",
    )
    assessment = assess_claim_support(
        claim,
        joint_bundle,
        [support],
        audit_config,
        counterevidence=[counter],
    )
    assert assessment.support_label == "overstated"
    assert {flag.code for flag in assessment.rule_flags} >= {
        "future_certainty",
        "overconfident_wording",
        "counterevidence_present",
    }
    base_passage = contents.passages["src-001"][0]
    joint_contents = replace(
        contents,
        claims=[
            contents.claims[0].model_copy(
                update={"claim_id": claim.id, "claim_text": claim.text}
            )
        ],
        passages={
            "src-001": [
                base_passage.model_copy(
                    update={
                        "passage_id": "pass-support",
                        "passage_text": support_excerpt.text,
                        "passage_hash": "sha256:" + "c" * 64,
                    }
                ),
                base_passage.model_copy(
                    update={
                        "passage_id": "pass-counter",
                        "passage_text": counter_excerpt.text,
                        "passage_hash": "sha256:" + "d" * 64,
                    }
                ),
            ]
        },
    )

    result = export_contract_c(
        contents=joint_contents,
        assessments=[assessment],
        evidence_bundle=joint_bundle,
        audit_config=audit_config,
    )
    conclusion = result["propositions"][0]["conclusion"]
    assert conclusion["causal_form"] == "jointly_sufficient"
    assert conclusion["basis_members"] == [
        {
            "namespace": "state",
            "id": "state:absolute_lexical_trigger",
        },
        {
            "namespace": "state",
            "id": "state:counterevidence_contexts_nonempty",
        },
    ]
    roles = {
        row["code"]: row["terminal_role"]
        for row in conclusion["rule_roles"]
    }
    assert roles["future_certainty"] == "causal"
    assert roles["overconfident_wording"] == "causal"
    assert roles["counterevidence_present"] == "residual"


def test_exporter_rejects_policy_drift_instead_of_reinterpreting_v1(
    tmp_path: Path,
) -> None:
    contents, assessments, evidence_bundle, audit_config = _production_run(
        tmp_path
    )
    drifted = replace(CAL_RULES_V1_2_0, sourced_support=0.81)
    with pytest.raises(
        ContractCExportError,
        match="supports only CAL_RULES_V1_2_0",
    ):
        export_contract_c(
            contents=contents,
            assessments=assessments,
            evidence_bundle=evidence_bundle,
            audit_config=audit_config,
            policy=drifted,
        )
