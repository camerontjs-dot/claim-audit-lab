"""Rung 04: realistic Contract-B-shaped bundle sequence with a research sidecar."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pytest
import yaml

from claim_audit_lab.v1.decision_model import (
    CANONICAL_STAGE_ORDER,
    ChannelApertureAssessment,
    ChannelMeasurement,
    EligibilityAssessment,
    EvidenceContribution,
    EvidenceDecisionInput,
    EvidenceDecisionTrace,
    StageReceipt,
    ValidityAssessment,
    evaluate_evidence,
)

_FIXTURE = (
    Path(__file__).parents[1]
    / "fixtures"
    / "research"
    / "rung04_apparatus_bundle_series.yaml"
)
_SIGNAL_FLOOR = 0.20
_SUPPORT_THRESHOLD = 0.70
_REFUTATION_THRESHOLD = 0.70


def _receipt(seed: str) -> str:
    return "sha256:" + hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _load_fixture() -> dict[str, Any]:
    loaded = yaml.safe_load(_FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _snapshot(data: dict[str, Any], name: str) -> dict[str, Any]:
    for item in data["snapshots"]:
        if item["name"] == name:
            return item
    raise AssertionError(f"missing fixture snapshot {name}")


def _passage_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    claim = snapshot["claim"]
    passages = claim["evidence_passages"] + claim["counterevidence_passages"]
    result = {item["passage_id"]: item for item in passages}
    assert len(result) == len(passages)
    return result


def _stage_receipts(bundle_id: str) -> tuple[StageReceipt, ...]:
    return tuple(
        StageReceipt(
            stage=stage,
            evidence_path=f"bundle:{bundle_id}/stage:{stage}",
            receipt_sha256=_receipt(f"{bundle_id}:{stage}"),
        )
        for stage in CANONICAL_STAGE_ORDER
    )


def _build_input(data: dict[str, Any], snapshot: dict[str, Any]) -> EvidenceDecisionInput:
    sidecar = snapshot.get("research_decision_annotations")
    if not isinstance(sidecar, dict):
        raise ValueError("research decision sidecar is required for the rich shadow input")

    manifest = snapshot["bundle_manifest"]
    claim = snapshot["claim"]
    bundle_id = manifest["bundle_id"]
    passages = _passage_map(snapshot)
    assessments = sidecar["passage_assessments"]
    measurements_fixture = data["measurement_fixture"]

    assert set(assessments) == set(passages)

    measurements: list[ChannelMeasurement] = []
    contributions: list[EvidenceContribution] = []
    for passage_id in sorted(passages):
        scores = measurements_fixture[passage_id]
        assessment = assessments[passage_id]
        measurement_receipt = _receipt(f"measurement:{passage_id}")
        measurements.append(
            ChannelMeasurement(
                passage_id=passage_id,
                support_score=scores["support"],
                refutation_score=scores["refutation"],
                receipt_sha256=measurement_receipt,
                evidence_path=f"bundle:{bundle_id}/passage:{passage_id}",
            )
        )
        channel = assessment["channel"]
        contributions.append(
            EvidenceContribution(
                contribution_id=f"{channel}:{passage_id}",
                channel=channel,
                passage_ids=(passage_id,),
                score=scores[channel],
                score_method="direct_nli_probability",
                score_receipt_sha256=measurement_receipt,
                origin="direct_nli",
                eligibility=EligibilityAssessment(
                    status=assessment["eligibility"],
                    reason=assessment["reason"],
                    evidence_path=f"sidecar:{bundle_id}/eligibility:{passage_id}",
                    receipt_sha256=_receipt(f"eligibility:{bundle_id}:{passage_id}"),
                ),
                validity=ValidityAssessment(
                    status=assessment["validity"],
                    reason=assessment["reason"],
                    evidence_path=f"sidecar:{bundle_id}/validity:{passage_id}",
                    receipt_sha256=_receipt(f"validity:{bundle_id}:{passage_id}"),
                    operator=assessment["operator"],
                ),
            )
        )

    apertures = sidecar["apertures"]
    aperture_models = tuple(
        ChannelApertureAssessment(
            channel=channel,
            status=apertures[channel],
            reason=f"research sidecar declares {channel} aperture {apertures[channel]}",
            evidence_path=f"sidecar:{bundle_id}/aperture:{channel}",
            receipt_sha256=_receipt(f"aperture:{bundle_id}:{channel}"),
        )
        for channel in ("support", "refutation")
    )

    return EvidenceDecisionInput(
        claim_id=claim["claim_id"],
        scope_status=sidecar["scope_status"],
        stage_receipts=_stage_receipts(bundle_id),
        admitted_passage_ids=tuple(sorted(passages)),
        measurements=tuple(measurements),
        apertures=aperture_models,
        signal_floor=_SIGNAL_FLOOR,
        support_threshold=_SUPPORT_THRESHOLD,
        refutation_threshold=_REFUTATION_THRESHOLD,
        policy_id="rung04-realistic-apparatus-bundles",
        policy_receipt_sha256=_receipt("rung04-realistic-apparatus-bundles"),
        contributions=tuple(contributions),
    )


def _trace(data: dict[str, Any], name: str) -> EvidenceDecisionTrace:
    return evaluate_evidence(_build_input(data, _snapshot(data, name)))


def _measurement_map(trace: EvidenceDecisionTrace) -> dict[str, tuple[float | None, float | None]]:
    return {
        item.passage_id: (item.support_score, item.refutation_score)
        for item in trace.inputs.measurements
    }


def test_r04_01_bundles_are_immutable_monotonic_snapshots() -> None:
    data = _load_fixture()
    snapshots = [_snapshot(data, name) for name in ("B04-1", "B04-2", "B04-3")]
    bundle_ids = [item["bundle_manifest"]["bundle_id"] for item in snapshots]
    passage_maps = [_passage_map(item) for item in snapshots]

    assert len(set(bundle_ids)) == 3
    assert set(passage_maps[0]) < set(passage_maps[1]) < set(passage_maps[2])

    for earlier, later in zip(passage_maps, passage_maps[1:], strict=True):
        for passage_id, passage in earlier.items():
            assert later[passage_id] == passage


def test_r04_02_measurements_are_frozen_across_bundle_snapshots() -> None:
    data = _load_fixture()
    traces = [_trace(data, name) for name in ("B04-1", "B04-2", "B04-3")]
    measurement_maps = [_measurement_map(trace) for trace in traces]

    for earlier, later in zip(measurement_maps, measurement_maps[1:], strict=True):
        for passage_id, scores in earlier.items():
            assert later[passage_id] == scores


def test_r04_03_resolving_supplier_unknown_exposes_mixed_evidence() -> None:
    data = _load_fixture()
    first = _trace(data, "B04-1")
    second = _trace(data, "B04-2")

    assert first.decision.disposition == "abstained"
    assert first.decision.reason_code == "eligibility_unknown"
    assert second.decision.disposition == "abstained"
    assert second.valid.state == "mixed"
    assert second.decision.reason_code == "mixed_valid_evidence"


def test_r04_04_remediation_can_resolve_without_erasing_history() -> None:
    data = _load_fixture()
    third = _trace(data, "B04-3")

    raw_ids = set(third.raw.contribution_ids)
    valid_ids = set(third.valid.contribution_ids)

    assert "support:p-pre-validation" in raw_ids
    assert "refutation:p-incident" in raw_ids
    assert "support:p-pre-validation" not in valid_ids
    assert "refutation:p-incident" not in valid_ids
    assert "support:p-current-validation" in valid_ids
    assert "support:p-capa-closure" in valid_ids
    assert third.valid.state == "support_only"
    assert third.decision.disposition == "decided"
    assert third.decision.verdict == "supported"
    assert third.decision.reason_code == "support_above_threshold"


def test_r04_05_contract_shaped_claim_does_not_contain_rich_decision_fields() -> None:
    data = _load_fixture()
    claim = _snapshot(data, "B04-3")["claim"]
    passages = _passage_map(_snapshot(data, "B04-3"))
    forbidden_claim_fields = {
        "eligibility",
        "validity",
        "aperture",
        "temporal_applicability",
        "authority_status",
    }

    assert forbidden_claim_fields.isdisjoint(claim)
    for passage in passages.values():
        assert forbidden_claim_fields.isdisjoint(passage)


def test_r04_06_reconstruction_without_sidecar_fails_explicitly() -> None:
    data = _load_fixture()
    snapshot = dict(_snapshot(data, "B04-3"))
    snapshot.pop("research_decision_annotations")

    with pytest.raises(ValueError, match="research decision sidecar is required"):
        _build_input(data, snapshot)
