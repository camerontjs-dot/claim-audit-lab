from __future__ import annotations

import copy
import sys
from hashlib import sha256
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shadow_candidate import (  # noqa: E402
    ASSERTION_SCOPE_FALSIFIER,
    AuthorityBoundaryError,
    MeasurementInstrument,
    canonical_bytes,
    candidate_internal_record,
    classify_legacy_shadow_divergence,
    measure_text,
    project_shadow_contract_c,
    require_external_warrant,
    result_set_identity,
)

CANDIDATE_SHA = "1" * 40


def _legacy(verdict: str = "supported") -> dict:
    contribution_id = "contribution:" + "2" * 64
    prop = {
        "proposition": {
            "proposition_id": "claim-1",
            "text_sha256": sha256(b"claim text").hexdigest(),
        },
        "execution": {"state": "completed", "completion": "assessed"},
        "assessments": {
            "eligibility": {"state": "not_performed"},
            "semantic_validity": {"state": "not_performed"},
            "aperture_completeness": {"state": "not_performed"},
            "temporal_applicability": {"state": "not_performed"},
        },
        "contributions": [
            {
                "contribution_id": contribution_id,
                "channel": "support",
                "evidence_ref": {
                    "source_id": "s1",
                    "passage_id": "p1",
                    "passage_sha256": "sha256:" + "3" * 64,
                },
            }
        ],
        "measurement": {
            "kind": "legacy_measurement",
            "value": 0.9,
            "basis_contribution_ids": [contribution_id],
        },
        "conclusion": {
            "reported_verdict": verdict,
            "terminal_branch": "legacy",
            "causal_form": "single_necessary",
            "basis_members": [{"namespace": "contribution", "id": contribution_id}],
            "residual_contribution_ids": [],
            "rule_roles": [],
        },
    }
    if verdict == "not_checkable":
        prop["execution"] = {"state": "completed", "completion": "not_checkable"}
        prop["conclusion"] = {
            "reported_verdict": "not_checkable",
            "terminal_branch": "legacy",
            "causal_form": "redundant_non_deciding",
            "basis_members": [],
            "residual_contribution_ids": [contribution_id],
            "rule_roles": [],
        }
    result = {
        "contract_c_version": "1.0.0",
        "input": {
            "contract_b": {
                "contract_version": "1.2.0",
                "bundle_id": "bundle-1",
                "bundle_hash": "sha256:" + "4" * 64,
            }
        },
        "producer": {
            "semantic_implementation_sha": "5" * 40,
            "policy": {"sha256": "6" * 64, "canonical": {"legacy": True}},
        },
        "execution": {"state": "completed"},
        "propositions": [prop],
    }
    result["result_set_id"] = result_set_identity(result)
    return result


def _internal(observations: list[dict] | None = None) -> dict[str, dict]:
    return {
        "claim-1": candidate_internal_record(
            claim_id="claim-1",
            selection_basis="test",
            observations=observations or [],
            excluded_passage_ids=[],
            aperture_observation=None,
        )
    }


def test_assertion_scope_falsifier_is_exact_terminal_identity() -> None:
    assert ASSERTION_SCOPE_FALSIFIER == "ead5a6b068c17aefea0c2fc6b0b54b78ced26729"


def test_claimed_measurement_never_grants_authority_even_when_instruments_agree() -> None:
    instruments = [
        MeasurementInstrument("a", lambda _: {"status": "CLAIMED", "value": "x"}, "a" * 40),
        MeasurementInstrument("b", lambda _: {"status": "CLAIMED", "value": "x"}, "b" * 40),
    ]
    observations = measure_text("x", instruments, passage_id="p1")
    assert [row["authority"]["state"] for row in observations] == [
        "insufficient_authority",
        "insufficient_authority",
    ]
    assert all(not row["authority"]["may_strengthen_conclusion"] for row in observations)


def test_operator_inapplicable_and_semantic_relation_unknown_remain_distinct() -> None:
    instruments = [
        MeasurementInstrument("none", lambda _: {"status": "NOT_APPLICABLE"}, "a" * 40),
        MeasurementInstrument("unknown", lambda _: {"status": "UNRESOLVED"}, "b" * 40),
    ]
    observations = measure_text("x", instruments, passage_id="p1")
    assert [row["authority"]["state"] for row in observations] == [
        "operator_inapplicable",
        "semantic_relation_unknown",
    ]


def test_execution_failure_is_preserved_as_execution_failure() -> None:
    def fail(_: str) -> dict:
        raise RuntimeError("boom")

    observations = measure_text(
        "x", [MeasurementInstrument("fail", fail, "a" * 40)], passage_id="p1"
    )
    assert observations[0]["authority"]["state"] == "execution_failure"
    assert observations[0]["measurement"] is None


@pytest.mark.parametrize(
    "receipt",
    [
        None,
        {"state": "semantic_unknown"},
        {"state": "extraction_unresolved"},
        {"state": "insufficient_authority"},
        {"state": "established"},
    ],
)
def test_integration_track_refuses_to_invent_or_verify_warrant(receipt: dict | None) -> None:
    with pytest.raises(AuthorityBoundaryError):
        require_external_warrant(receipt)


def test_projection_removes_causal_strength_and_preserves_contributions_as_residual() -> None:
    legacy = _legacy("supported")
    shadow = project_shadow_contract_c(
        legacy,
        semantic_implementation_sha=CANDIDATE_SHA,
        internal_records=_internal(),
    )
    prop = shadow["propositions"][0]
    assert prop["execution"] == {"state": "completed", "completion": "not_checkable"}
    assert prop["assessments"]["semantic_validity"] == {
        "state": "performed",
        "value": "unknown",
    }
    assert prop["conclusion"]["reported_verdict"] == "not_checkable"
    assert prop["conclusion"]["basis_members"] == []
    assert prop["conclusion"]["residual_contribution_ids"] == [
        prop["contributions"][0]["contribution_id"]
    ]
    assert prop["measurement"] == legacy["propositions"][0]["measurement"]


def test_projection_is_deterministic_and_result_id_is_content_bound() -> None:
    legacy = _legacy()
    a = project_shadow_contract_c(
        legacy, semantic_implementation_sha=CANDIDATE_SHA, internal_records=_internal()
    )
    b = project_shadow_contract_c(
        copy.deepcopy(legacy), semantic_implementation_sha=CANDIDATE_SHA, internal_records=_internal()
    )
    assert canonical_bytes(a) == canonical_bytes(b)
    assert a["result_set_id"] == result_set_identity(a)


def test_missing_internal_authority_record_fails_closed() -> None:
    with pytest.raises(ValueError, match="missing internal candidate record"):
        project_shadow_contract_c(
            _legacy(), semantic_implementation_sha=CANDIDATE_SHA, internal_records={}
        )


def test_supported_legacy_to_not_checkable_is_classified_authority_unresolved() -> None:
    legacy = _legacy("supported")
    shadow = project_shadow_contract_c(
        legacy, semantic_implementation_sha=CANDIDATE_SHA, internal_records=_internal()
    )
    assert classify_legacy_shadow_divergence(legacy, shadow)[0]["primary_class"] == (
        "authority_unresolved"
    )


def test_legacy_not_checkable_has_no_terminal_divergence() -> None:
    legacy = _legacy("not_checkable")
    shadow = project_shadow_contract_c(
        legacy, semantic_implementation_sha=CANDIDATE_SHA, internal_records=_internal()
    )
    assert classify_legacy_shadow_divergence(legacy, shadow)[0]["primary_class"] == (
        "no_terminal_divergence"
    )
