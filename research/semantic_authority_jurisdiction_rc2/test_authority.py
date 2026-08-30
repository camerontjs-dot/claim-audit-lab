from pathlib import Path

from research.semantic_authority_jurisdiction_rc2.authority import (
    AuthorityReceipt,
    Quantity,
    assess_absence_boundary,
    assess_numeric_relation,
)
from research.semantic_authority_jurisdiction_rc2.native_descriptor import (
    from_contract_b_fixture,
)


def test_domain_firewall_rejects_cross_use():
    receipt = AuthorityReceipt(
        "r1",
        "numeric_relation",
        "semantic.validate_numeric",
        "claim-1",
        True,
        True,
        "valid",
        "fixture",
    )
    assert receipt.may_decide(
        required_domain="numeric_relation",
        operation="semantic.validate_numeric",
        target_id="claim-1",
    )
    assert not receipt.may_decide(
        required_domain="source_boundary",
        operation="semantic.validate_absence",
        target_id="claim-1",
    )


def test_expired_or_inapplicable_receipt_cannot_decide():
    expired = AuthorityReceipt(
        "r",
        "numeric_relation",
        "semantic.validate_numeric",
        "c",
        False,
        True,
        "valid",
        "expired",
    )
    inapplicable = AuthorityReceipt(
        "r2",
        "numeric_relation",
        "semantic.validate_numeric",
        "c",
        True,
        False,
        "inapplicable",
        "scope",
    )
    for receipt in (expired, inapplicable):
        assert not receipt.may_decide(
            required_domain="numeric_relation",
            operation="semantic.validate_numeric",
            target_id="c",
        )


def test_cg12_numeric_bound_is_refuted_without_a4():
    claim = Quantity(
        "deviation_recording_deadline",
        "deviation_general",
        5,
        "business_day",
        "max",
    )
    evidence = Quantity(
        "deviation_recording_deadline",
        "deviation_general",
        1,
        "business_day",
        "max",
    )
    receipt = assess_numeric_relation(
        claim=claim,
        evidence=evidence,
        target_id="CG-12a",
        receipt_id="num-cg12",
    )
    assert receipt.status == "invalid"
    assert receipt.may_decide(
        required_domain="numeric_relation",
        operation="semantic.validate_numeric",
        target_id="CG-12a",
    )


def test_cg24_wrong_scope_matching_number_is_inapplicable():
    claim = Quantity(
        "deviation_recording_deadline",
        "building_4",
        5,
        "business_day",
        "max",
    )
    wrong_scope = Quantity(
        "deviation_recording_deadline",
        "contract_lab",
        5,
        "business_day",
        "max",
    )
    receipt = assess_numeric_relation(
        claim=claim,
        evidence=wrong_scope,
        target_id="CG-24",
        receipt_id="num-cg24-wrong",
    )
    assert receipt.status == "inapplicable"
    assert receipt.reason == "scope_mismatch"
    assert not receipt.may_decide(
        required_domain="numeric_relation",
        operation="semantic.validate_numeric",
        target_id="CG-24",
    )


def test_cg24_in_scope_one_day_refutes_five_day_claim():
    claim = Quantity(
        "deviation_recording_deadline",
        "building_4",
        5,
        "business_day",
        "max",
    )
    evidence = Quantity(
        "deviation_recording_deadline",
        "building_4",
        1,
        "business_day",
        "max",
    )
    receipt = assess_numeric_relation(
        claim=claim,
        evidence=evidence,
        target_id="CG-24",
        receipt_id="num-cg24-right",
    )
    assert receipt.status == "invalid"


def test_property_and_unit_substitutions_fail_closed():
    claim = Quantity("temperature", "batch-1", 10, "celsius", "eq")
    wrong_property = Quantity("duration", "batch-1", 10, "celsius", "eq")
    wrong_unit = Quantity("temperature", "batch-1", 10, "fahrenheit", "eq")
    assert assess_numeric_relation(
        claim=claim,
        evidence=wrong_property,
        target_id="x",
        receipt_id="r1",
    ).status == "inapplicable"
    assert assess_numeric_relation(
        claim=claim,
        evidence=wrong_unit,
        target_id="x",
        receipt_id="r2",
    ).status == "inapplicable"


def test_cg05_numeric_authority_only_establishes_conditions_not_quality_hold():
    temp = assess_numeric_relation(
        claim=Quantity("temperature", "cold_chain_batch", 10, "celsius", "eq"),
        evidence=Quantity("temperature", "cold_chain_batch", 8, "celsius", "gt"),
        target_id="CG-05:temperature",
        receipt_id="num-cg05-temp",
    )
    duration = assess_numeric_relation(
        claim=Quantity("duration", "cold_chain_batch", 7, "hour", "eq"),
        evidence=Quantity("duration", "cold_chain_batch", 6, "hour", "gt"),
        target_id="CG-05:duration",
        receipt_id="num-cg05-duration",
    )
    assert temp.status == duration.status == "valid"
    for receipt in (temp, duration):
        assert not receipt.may_decide(
            required_domain="composition",
            operation="semantic.compose",
            target_id="CG-05",
        )


def test_source_boundary_triple_retention_samples():
    topic = "storage conditions for retention samples"
    exhaustive = assess_absence_boundary(
        boundary="exhaustive",
        topic=topic,
        named_gaps=(),
        claimed_material_is_named_gap=False,
        target_id="CG-08a",
        receipt_id="b1",
    )
    bounded = assess_absence_boundary(
        boundary="bounded",
        topic=topic,
        named_gaps=(),
        claimed_material_is_named_gap=False,
        target_id="CG-08b",
        receipt_id="b2",
    )
    named = assess_absence_boundary(
        boundary="named_missing_material",
        topic=topic,
        named_gaps=(topic, "photostability chamber calibration"),
        claimed_material_is_named_gap=True,
        target_id="CG-21",
        receipt_id="b3",
    )
    assert exhaustive.status == "valid"
    assert bounded.status == "unknown"
    assert named.status == "invalid"


def test_source_boundary_triple_postrelease_deviation():
    topic = "deviations detected after batch release"
    exhaustive = assess_absence_boundary(
        boundary="exhaustive",
        topic=topic,
        named_gaps=(),
        claimed_material_is_named_gap=False,
        target_id="CG-09a",
        receipt_id="b1",
    )
    bounded = assess_absence_boundary(
        boundary="bounded",
        topic=topic,
        named_gaps=(),
        claimed_material_is_named_gap=False,
        target_id="CG-09b",
        receipt_id="b2",
    )
    named = assess_absence_boundary(
        boundary="named_missing_material",
        topic=topic,
        named_gaps=("escalation of repeat deviations",),
        claimed_material_is_named_gap=False,
        target_id="CG-22",
        receipt_id="b3",
    )
    assert exhaustive.status == "valid"
    assert bounded.status == "unknown"
    assert named.status == "unknown"


def test_boundary_receipt_cannot_be_used_as_numeric_authority():
    receipt = assess_absence_boundary(
        boundary="exhaustive",
        topic="x",
        named_gaps=(),
        claimed_material_is_named_gap=False,
        target_id="c",
        receipt_id="b",
    )
    assert not receipt.may_decide(
        required_domain="numeric_relation",
        operation="semantic.validate_numeric",
        target_id="c",
    )


def test_cal_native_assessment_descriptor_binds_identity_not_semantics():
    root = Path(__file__).resolve().parents[2]
    descriptor = from_contract_b_fixture(root)
    assert descriptor.actor == "claim-audit-lab"
    assert descriptor.operation == "assessment.issue"
    assert descriptor.authority_domain == "assessment_mandate"
    assert descriptor.target_id.endswith("::clm-001")
    assert descriptor.current_hash.startswith("sha256:")


def test_assessment_mandate_is_not_semantic_support_authority():
    root = Path(__file__).resolve().parents[2]
    descriptor = from_contract_b_fixture(root)
    assert descriptor.authority_domain != "numeric_relation"
    assert "support" not in descriptor.authority_domain
