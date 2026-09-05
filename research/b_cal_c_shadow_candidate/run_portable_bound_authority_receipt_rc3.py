"""Run preregistered RC8J portable bound authority receipt RC3."""
from __future__ import annotations

import argparse
from copy import deepcopy
import inspect
import json
from pathlib import Path
import secrets
from typing import Any

from pydantic import ValidationError

from categorical_warranted_relation_rc1 import (
    ComparisonProposition,
    compose_categorical_relations,
    derive_categorical_relation as _derive_frozen_rc1_relation,
)
from portable_bound_authority_receipt_rc3 import (
    PortableReceiptIssuanceRefusal,
    PortableReceiptRefusal,
    authority_subject_digest,
    issue_portable_warrant,
    parse_portable_warrant,
    serialize_portable_warrant,
    verify_and_derive_categorical_relation,
    verify_portable_warrant,
)
from run_authority_consumption_rc1 import (
    _load_rc8j,
    _typed_seam_control,
    _validated_b_coordinates,
)
from run_categorical_warranted_relation_rc1 import _authority, _variant


RC2_HEAD = "0c324a6a866f1bc0ce678c78d6502c6b314386c2"
RC8J_FREEZE_COMMIT = "8e75c6782bb95c3763d06230b9c5df2b6af44054"
RC8J_CANDIDATE_BLOB = "f55156e43e0c1b4a7868bc8339585b8892edda38"
PRODUCTION_MAIN = "32275a239b68af383a56bca843e28cbc1e343976"
KEY_ID = "rc3-run-ephemeral-key"


def _consume(
    *,
    case: dict[str, Any],
    proposition: ComparisonProposition,
    transport: str,
    key: bytes,
) -> dict[str, Any]:
    refused = False
    refusal_code: str | None = None
    refusal_detail: str | None = None
    relation_dump: dict[str, Any] | None = None
    conclusion_dump: dict[str, Any] | None = None
    deciding = False
    try:
        relation = verify_and_derive_categorical_relation(
            case=case,
            proposition=proposition,
            receipt_transport=transport,
            trusted_keys={KEY_ID: key},
        )
        conclusion = compose_categorical_relations(proposition, (relation,))
        relation_dump = relation.model_dump(mode="json")
        conclusion_dump = conclusion.model_dump(mode="json")
        deciding = conclusion.disposition == "decided"
    except PortableReceiptRefusal as exc:
        refused = True
        refusal_code = exc.code
        refusal_detail = exc.detail
    return {
        "refused": refused,
        "refusal_code": refusal_code,
        "refusal_detail": refusal_detail,
        "derived_relation": relation_dump,
        "scoreless_conclusion": conclusion_dump,
        "produced_deciding_conclusion": deciding,
    }


def _weak_digest_only_consumer(
    *,
    case: dict[str, Any],
    proposition: ComparisonProposition,
    attacker_supplied_status: str,
    attacker_supplied_reason: str,
    attacker_supplied_digest: str,
) -> dict[str, Any]:
    """Deliberately weak control: binding with no authenticated issuer."""
    if attacker_supplied_status != "WARRANTED":
        return {"accepted": False, "produced_deciding_conclusion": False}
    if attacker_supplied_digest != authority_subject_digest(case):
        return {"accepted": False, "produced_deciding_conclusion": False}
    relation = _derive_frozen_rc1_relation(
        case=case,
        authority_result={
            "authority": {
                "status": attacker_supplied_status,
                "reason": attacker_supplied_reason,
            }
        },
        proposition=proposition,
    )
    conclusion = compose_categorical_relations(proposition, (relation,))
    return {
        "accepted": True,
        "derived_relation": relation.model_dump(mode="json"),
        "scoreless_conclusion": conclusion.model_dump(mode="json"),
        "produced_deciding_conclusion": conclusion.disposition == "decided",
    }


def _tamper(transport: str, mutate) -> str:
    payload = json.loads(transport)
    mutate(payload)
    return json.dumps(payload, ensure_ascii=False)


def _expect_refusal(label: str, result: dict[str, Any]) -> None:
    if not result["refused"] or result["produced_deciding_conclusion"]:
        raise AssertionError(f"{label} was not refused closed: {result}")


def _relation(result: dict[str, Any]) -> str | None:
    value = result.get("derived_relation")
    return value.get("relation") if isinstance(value, dict) else None


def _verdict(result: dict[str, Any]) -> str | None:
    value = result.get("scoreless_conclusion")
    return value.get("verdict") if isinstance(value, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-output", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    args = parser.parse_args()

    outdir = args.run_output.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    evaluator = _load_rc8j(args.rc8j_root.resolve())
    coords = _validated_b_coordinates(outdir)
    base = _typed_seam_control(coords)
    claim_id = coords["claim_id"]
    key = secrets.token_bytes(32)

    target = ComparisonProposition(
        claim_id=claim_id,
        family="comparison",
        lhs_entity="fixture:left",
        rhs_entity="fixture:right",
        comparison_direction="greater_than",
    )
    swapped_target = ComparisonProposition(
        claim_id=claim_id,
        family="comparison",
        lhs_entity="fixture:right",
        rhs_entity="fixture:left",
        comparison_direction="less_than",
    )

    support_case = _variant(
        base,
        case_id="RC3-C1-SUPPORT",
        atom_id="atom:categorical:rc3:a-gt-b:v1",
        lhs="fixture:left",
        rhs="fixture:right",
        direction="greater_than",
    )
    refute_case = _variant(
        base,
        case_id="RC3-C2-REFUTE",
        atom_id="atom:categorical:rc3:a-lt-b:v1",
        lhs="fixture:left",
        rhs="fixture:right",
        direction="less_than",
    )
    irrelevant_case = _variant(
        base,
        case_id="RC3-C19-IRRELEVANT",
        atom_id="atom:categorical:rc3:x-gt-y:v1",
        lhs="fixture:other-left",
        rhs="fixture:other-right",
        direction="greater_than",
    )
    unresolved_semantic_case = _variant(
        base,
        case_id="RC3-C19-UNRESOLVED",
        atom_id="atom:categorical:rc3:a-at-least-b:v1",
        lhs="fixture:left",
        rhs="fixture:right",
        direction="at_least",
    )

    support_authority = _authority(support_case, evaluator)["authority"]
    if support_authority != {
        "status": "WARRANTED",
        "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
    }:
        raise AssertionError(f"base support setup is not warranted: {support_authority}")

    support_receipt = issue_portable_warrant(
        case=support_case,
        authority_evaluator=evaluator,
        key=key,
        key_id=KEY_ID,
    )
    support_transport = serialize_portable_warrant(support_receipt)
    support = _consume(case=support_case, proposition=target, transport=support_transport, key=key)

    # Exact RC1A replay killer: same atom identity, proposal changes, stale warrant retained.
    replay_case = deepcopy(support_case)
    replay_case["case_id"] = "RC3-C3-EXACT-RC1A-PAYLOAD-REPLAY"
    replay_case["proposal"]["fields"]["comparison_direction"] = "less_than"
    replay_independent = _authority(replay_case, evaluator)["authority"]
    replay = _consume(case=replay_case, proposition=target, transport=support_transport, key=key)
    _expect_refusal("exact RC1A payload replay", replay)

    # Weak digest-only control: attacker recomputes digest and launders the non-warranted payload.
    weak_forged_digest = authority_subject_digest(replay_case)
    weak = _weak_digest_only_consumer(
        case=replay_case,
        proposition=target,
        attacker_supplied_status="WARRANTED",
        attacker_supplied_reason="ALL_REQUIRED_WARRANT_ESTABLISHED",
        attacker_supplied_digest=weak_forged_digest,
    )

    # Strong recomputed-digest forgery: update digest but retain stale MAC.
    forged_digest_transport = _tamper(
        support_transport,
        lambda payload: payload["body"].__setitem__("subject_digest", weak_forged_digest),
    )
    forged_digest = _consume(
        case=replay_case,
        proposition=target,
        transport=forged_digest_transport,
        key=key,
    )
    _expect_refusal("recomputed digest without MAC", forged_digest)

    # Atom identity substitution.
    atom_case = deepcopy(support_case)
    atom_case["case_id"] = "RC3-C4-ATOM-ID-SUBSTITUTION"
    atom_case["target_atom_id"] = "atom:categorical:rc3:replacement:v1"
    atom_independent = _authority(atom_case, evaluator)["authority"]
    atom_sub = _consume(case=atom_case, proposition=target, transport=support_transport, key=key)
    _expect_refusal("atom substitution", atom_sub)

    # Claim substitution.
    claim_case = deepcopy(support_case)
    claim_case["case_id"] = "RC3-C5-CLAIM-SUBSTITUTION"
    claim_case["raw_claim_id"] = "claim:categorical:replacement"
    claim_independent = _authority(claim_case, evaluator)["authority"]
    claim_sub = _consume(case=claim_case, proposition=target, transport=support_transport, key=key)
    _expect_refusal("claim substitution", claim_sub)

    # Authority-subject substitution.
    subject_case = deepcopy(support_case)
    subject_case["case_id"] = "RC3-C6-AUTHORITY-SUBJECT-SUBSTITUTION"
    subject_case["authority_subject_id"] = "authority:replacement"
    subject_independent = _authority(subject_case, evaluator)["authority"]
    subject_sub = _consume(case=subject_case, proposition=target, transport=support_transport, key=key)
    _expect_refusal("authority-subject substitution", subject_sub)

    # Field warrant mutation.
    warrant_case = deepcopy(support_case)
    warrant_case["case_id"] = "RC3-C7-FIELD-WARRANT-MUTATION"
    warrant_case["field_warrants"]["comparison_direction"]["value"] = "less_than"
    warrant_independent = _authority(warrant_case, evaluator)["authority"]
    warrant_sub = _consume(case=warrant_case, proposition=target, transport=support_transport, key=key)
    _expect_refusal("field warrant mutation", warrant_sub)

    # Evidence coordinate mutation.
    evidence_case = deepcopy(support_case)
    evidence_case["case_id"] = "RC3-C8-EVIDENCE-COORDINATE-MUTATION"
    evidence_case["raw_passage_id"] = "passage:replacement"
    evidence_independent = _authority(evidence_case, evaluator)["authority"]
    evidence_sub = _consume(case=evidence_case, proposition=target, transport=support_transport, key=key)
    _expect_refusal("evidence coordinate mutation", evidence_sub)

    # Authenticated receipt field tampering.
    status_tampered = _tamper(
        support_transport,
        lambda payload: payload["body"].__setitem__("authority_status", "REJECTED"),
    )
    status_result = _consume(case=support_case, proposition=target, transport=status_tampered, key=key)
    _expect_refusal("status tamper", status_result)

    reason_tampered = _tamper(
        support_transport,
        lambda payload: payload["body"].__setitem__("authority_reason", "OTHER"),
    )
    reason_result = _consume(case=support_case, proposition=target, transport=reason_tampered, key=key)
    _expect_refusal("reason tamper", reason_result)

    issuer_commit_tampered = _tamper(
        support_transport,
        lambda payload: payload["body"].__setitem__("issuer_rc8j_commit", "0" * 40),
    )
    issuer_commit_result = _consume(
        case=support_case, proposition=target, transport=issuer_commit_tampered, key=key
    )
    _expect_refusal("issuer commit tamper", issuer_commit_result)

    issuer_blob_tampered = _tamper(
        support_transport,
        lambda payload: payload["body"].__setitem__("issuer_rc8j_blob", "0" * 40),
    )
    issuer_blob_result = _consume(
        case=support_case, proposition=target, transport=issuer_blob_tampered, key=key
    )
    _expect_refusal("issuer blob tamper", issuer_blob_result)

    key_id_tampered = _tamper(
        support_transport,
        lambda payload: payload["body"].__setitem__("key_id", "unknown-key"),
    )
    key_id_result = _consume(case=support_case, proposition=target, transport=key_id_tampered, key=key)
    _expect_refusal("key id tamper", key_id_result)

    wrong_key_refused = False
    wrong_key_code: str | None = None
    try:
        verify_portable_warrant(
            case=support_case,
            receipt_transport=support_transport,
            trusted_keys={KEY_ID: b"x" * 32},
        )
    except PortableReceiptRefusal as exc:
        wrong_key_refused = True
        wrong_key_code = exc.code

    mac_tampered = _tamper(
        support_transport,
        lambda payload: payload.__setitem__("mac", ("0" if payload["mac"][0] != "0" else "1") + payload["mac"][1:]),
    )
    mac_result = _consume(case=support_case, proposition=target, transport=mac_tampered, key=key)
    _expect_refusal("MAC mutation", mac_result)

    mac_truncated = _tamper(
        support_transport,
        lambda payload: payload.__setitem__("mac", payload["mac"][:-2]),
    )
    mac_truncated_result = _consume(
        case=support_case, proposition=target, transport=mac_truncated, key=key
    )
    _expect_refusal("MAC truncation", mac_truncated_result)

    partial_payload = json.loads(support_transport)
    del partial_payload["body"]["subject_digest"]
    partial_result = _consume(
        case=support_case,
        proposition=target,
        transport=json.dumps(partial_payload),
        key=key,
    )
    _expect_refusal("partial receipt", partial_result)

    unknown_payload = json.loads(support_transport)
    unknown_payload["unexpected"] = "forbidden"
    unknown_result = _consume(
        case=support_case,
        proposition=target,
        transport=json.dumps(unknown_payload),
        key=key,
    )
    _expect_refusal("unknown receipt field", unknown_result)

    duplicate_transport = '{"body":{},"body":{},"auth_algorithm":"hmac-sha256","mac":"' + ("0" * 64) + '"}'
    duplicate_refused = False
    duplicate_code: str | None = None
    try:
        parse_portable_warrant(duplicate_transport)
    except PortableReceiptRefusal as exc:
        duplicate_refused = True
        duplicate_code = exc.code

    # Transport serialization metamorphic.
    payload = json.loads(support_transport)
    reordered_payload = {
        "mac": payload["mac"],
        "auth_algorithm": payload["auth_algorithm"],
        "body": dict(reversed(list(payload["body"].items()))),
    }
    reordered_transport = json.dumps(reordered_payload, indent=4, ensure_ascii=False)
    transport_reordered_verified = verify_portable_warrant(
        case=support_case,
        receipt_transport=reordered_transport,
        trusted_keys={KEY_ID: key},
    ) == support_receipt

    # Case insertion order metamorphic.
    reordered_case = dict(reversed(list(support_case.items())))
    reordered_case["proposal"] = dict(reversed(list(support_case["proposal"].items())))
    reordered_case["proposal"]["fields"] = dict(
        reversed(list(support_case["proposal"]["fields"].items()))
    )
    case_order_digest_same = authority_subject_digest(reordered_case) == authority_subject_digest(support_case)
    case_order_result = _consume(
        case=reordered_case,
        proposition=target,
        transport=support_transport,
        key=key,
    )

    # Diagnostic metadata invariance.
    diagnostic_case = deepcopy(support_case)
    diagnostic_case["case_id"] = "RC3-C17-DIAGNOSTIC-INVARIANCE"
    diagnostic_case["instrument_ids"] = ["diag-one", "diag-two", "diag-three"]
    diagnostic_case["reader_agreement_count"] = 99
    diagnostic_digest_same = authority_subject_digest(diagnostic_case) == authority_subject_digest(support_case)
    diagnostic_result = _consume(
        case=diagnostic_case,
        proposition=target,
        transport=support_transport,
        key=key,
    )

    # Producer must not issue for the exact non-warranted replay case.
    producer_refused_nonwarranted = False
    producer_refusal: dict[str, str] | None = None
    try:
        issue_portable_warrant(
            case=replay_case,
            authority_evaluator=evaluator,
            key=key,
            key_id=KEY_ID,
        )
    except PortableReceiptIssuanceRefusal as exc:
        producer_refused_nonwarranted = True
        producer_refusal = {"status": exc.status, "reason": exc.reason}

    # Categorical regression cases all use separately issued portable receipts.
    def issue_and_consume(case: dict[str, Any], proposition: ComparisonProposition) -> tuple[Any, dict[str, Any]]:
        receipt = issue_portable_warrant(
            case=case,
            authority_evaluator=evaluator,
            key=key,
            key_id=KEY_ID,
        )
        result = _consume(
            case=case,
            proposition=proposition,
            transport=serialize_portable_warrant(receipt),
            key=key,
        )
        return receipt, result

    refute_receipt, refute = issue_and_consume(refute_case, target)
    irrelevant_receipt, irrelevant = issue_and_consume(irrelevant_case, target)
    unresolved_receipt, unresolved = issue_and_consume(unresolved_semantic_case, target)
    _, swapped = issue_and_consume(support_case, swapped_target)

    support_relation = verify_and_derive_categorical_relation(
        case=support_case,
        proposition=target,
        receipt_transport=support_transport,
        trusted_keys={KEY_ID: key},
    )
    refute_relation = verify_and_derive_categorical_relation(
        case=refute_case,
        proposition=target,
        receipt_transport=serialize_portable_warrant(refute_receipt),
        trusted_keys={KEY_ID: key},
    )
    irrelevant_relation = verify_and_derive_categorical_relation(
        case=irrelevant_case,
        proposition=target,
        receipt_transport=serialize_portable_warrant(irrelevant_receipt),
        trusted_keys={KEY_ID: key},
    )
    unresolved_relation = verify_and_derive_categorical_relation(
        case=unresolved_semantic_case,
        proposition=target,
        receipt_transport=serialize_portable_warrant(unresolved_receipt),
        trusted_keys={KEY_ID: key},
    )
    mixed_forward = compose_categorical_relations(target, (support_relation, refute_relation))
    mixed_reverse = compose_categorical_relations(target, (refute_relation, support_relation))
    support_irrelevant = compose_categorical_relations(target, (support_relation, irrelevant_relation))
    support_unresolved = compose_categorical_relations(target, (support_relation, unresolved_relation))

    forbidden_inputs: dict[str, bool] = {}
    target_payload = target.model_dump(mode="json")
    for field, value in (
        ("score", 0.99),
        ("confidence", 0.99),
        ("threshold", 0.7),
        ("channel", "support"),
        ("relation_hint", "SUPPORTS"),
    ):
        rejected = False
        try:
            ComparisonProposition.model_validate({**target_payload, field: value})
        except ValidationError:
            rejected = True
        forbidden_inputs[field] = rejected

    consumer_signature = inspect.signature(verify_and_derive_categorical_relation)
    consumer_no_evaluator_parameter = "authority_evaluator" not in consumer_signature.parameters
    consumer_no_authority_result_parameter = "authority_result" not in consumer_signature.parameters

    forbidden_output_keys = {"score", "confidence", "threshold", "channel", "relation_hint"}
    forbidden_surface_present = bool(
        forbidden_output_keys.intersection(support_receipt.model_dump(mode="json"))
        or forbidden_output_keys.intersection(support_relation.model_dump(mode="json"))
        or forbidden_output_keys.intersection(
            compose_categorical_relations(target, (support_relation,)).model_dump(mode="json")
        )
    )

    independent_negative_controls = {
        "replay": replay_independent,
        "atom_substitution": atom_independent,
        "claim_substitution": claim_independent,
        "authority_subject_substitution": subject_independent,
        "field_warrant_mutation": warrant_independent,
        "evidence_coordinate_mutation": evidence_independent,
    }
    all_independent_negatives_nonwarranted = all(
        item["status"] != "WARRANTED" for item in independent_negative_controls.values()
    )

    authenticated_negative_results = {
        "replay": replay,
        "recomputed_digest_forgery": forged_digest,
        "atom_substitution": atom_sub,
        "claim_substitution": claim_sub,
        "authority_subject_substitution": subject_sub,
        "field_warrant_mutation": warrant_sub,
        "evidence_coordinate_mutation": evidence_sub,
        "status_tamper": status_result,
        "reason_tamper": reason_result,
        "issuer_commit_tamper": issuer_commit_result,
        "issuer_blob_tamper": issuer_blob_result,
        "key_id_tamper": key_id_result,
        "mac_mutation": mac_result,
        "mac_truncation": mac_truncated_result,
        "partial_receipt": partial_result,
        "unknown_receipt_field": unknown_result,
    }
    authenticated_attacks_refused = all(
        result["refused"] and not result["produced_deciding_conclusion"]
        for result in authenticated_negative_results.values()
    )

    weak_control_valid = (
        replay_independent["status"] != "WARRANTED"
        and weak.get("accepted") is True
        and weak.get("produced_deciding_conclusion") is True
        and weak.get("derived_relation", {}).get("relation") == "REFUTES"
    )

    categorical_regressions_pass = all(
        [
            not support["refused"] and _relation(support) == "SUPPORTS" and _verdict(support) == "supported",
            not refute["refused"] and _relation(refute) == "REFUTES" and _verdict(refute) == "contradicted",
            not irrelevant["refused"] and _relation(irrelevant) == "IRRELEVANT",
            not unresolved["refused"] and _relation(unresolved) == "UNRESOLVED",
            not swapped["refused"] and _relation(swapped) == "SUPPORTS" and _verdict(swapped) == "supported",
            mixed_forward.disposition == "abstained" and mixed_forward.reason_code == "mixed_categorical_relations",
            mixed_forward == mixed_reverse,
            support_irrelevant.disposition == "decided" and support_irrelevant.verdict == "supported",
            support_unresolved.disposition == "abstained" and support_unresolved.reason_code == "unresolved_categorical_relation",
        ]
    )

    serialization_controls_pass = all(
        [
            duplicate_refused and duplicate_code == "DUPLICATE_JSON_KEY",
            transport_reordered_verified,
            case_order_digest_same,
            not case_order_result["refused"],
            diagnostic_digest_same,
            not diagnostic_result["refused"],
            diagnostic_result["derived_relation"] == support["derived_relation"],
            diagnostic_result["scoreless_conclusion"] == support["scoreless_conclusion"],
        ]
    )

    interface_controls_pass = all(forbidden_inputs.values()) and not forbidden_surface_present and consumer_no_evaluator_parameter and consumer_no_authority_result_parameter

    setup_valid = all(
        [
            support_authority["status"] == "WARRANTED",
            replay_independent["status"] != "WARRANTED",
            weak_control_valid,
            all_independent_negatives_nonwarranted,
            producer_refused_nonwarranted,
        ]
    )

    any_authenticated_nonwarranted_decided = any(
        authenticated_negative_results[name]["produced_deciding_conclusion"]
        for name in (
            "replay",
            "atom_substitution",
            "claim_substitution",
            "authority_subject_substitution",
            "field_warrant_mutation",
            "evidence_coordinate_mutation",
            "recomputed_digest_forgery",
        )
    )

    if any_authenticated_nonwarranted_decided or not authenticated_attacks_refused:
        disposition = "FALSIFIED_PORTABLE_AUTHORITY_BINDING"
    elif not setup_valid:
        disposition = "INCONCLUSIVE_SETUP_INVALID"
    elif not serialization_controls_pass or not interface_controls_pass or not categorical_regressions_pass or not wrong_key_refused:
        disposition = "FALSIFIED_PORTABLE_AUTHORITY_BINDING"
    else:
        disposition = "SUPPORTED_WITH_BOUNDS"

    result = {
        "experiment": "RC8J portable authenticated authority receipt RC3",
        "frozen_parent_rc2_head": RC2_HEAD,
        "production_main_reference": PRODUCTION_MAIN,
        "rc8j": {
            "freeze_commit": RC8J_FREEZE_COMMIT,
            "candidate_blob": RC8J_CANDIDATE_BLOB,
        },
        "trust_model": {
            "receipt_authentication": "HMAC-SHA-256",
            "key_id": KEY_ID,
            "key_material_recorded": False,
            "shared_secret_required": True,
            "production_key_management_established": False,
        },
        "base_support_authority": support_authority,
        "portable_support_receipt": support_receipt.model_dump(mode="json"),
        "support_result": support,
        "weak_digest_only_control": {
            "independent_mutated_authority": replay_independent,
            "forged_digest": weak_forged_digest,
            "result": weak,
            "control_valid": weak_control_valid,
        },
        "authenticated_binding_attacks": {
            "exact_rc1a_payload_replay": replay,
            "recomputed_digest_without_valid_mac": forged_digest,
            "atom_id_substitution": atom_sub,
            "claim_substitution": claim_sub,
            "authority_subject_substitution": subject_sub,
            "field_warrant_mutation": warrant_sub,
            "evidence_coordinate_mutation": evidence_sub,
        },
        "independent_negative_authorities": independent_negative_controls,
        "receipt_tamper_controls": {
            "status": status_result,
            "reason": reason_result,
            "issuer_commit": issuer_commit_result,
            "issuer_blob": issuer_blob_result,
            "key_id": key_id_result,
            "wrong_key_refused": wrong_key_refused,
            "wrong_key_code": wrong_key_code,
            "mac_mutation": mac_result,
            "mac_truncation": mac_truncated_result,
            "partial_receipt": partial_result,
            "unknown_receipt_field": unknown_result,
            "duplicate_json_refused": duplicate_refused,
            "duplicate_json_code": duplicate_code,
        },
        "canonicalization_and_transport": {
            "transport_reordered_verified": transport_reordered_verified,
            "case_insertion_order_digest_same": case_order_digest_same,
            "case_insertion_order_verified": not case_order_result["refused"],
            "diagnostic_digest_same": diagnostic_digest_same,
            "diagnostic_relation_unchanged": diagnostic_result["derived_relation"] == support["derived_relation"],
            "diagnostic_conclusion_unchanged": diagnostic_result["scoreless_conclusion"] == support["scoreless_conclusion"],
        },
        "producer_nonwarranted_control": {
            "refused": producer_refused_nonwarranted,
            "refusal": producer_refusal,
        },
        "categorical_regressions": {
            "support": support,
            "refute": refute,
            "irrelevant": irrelevant,
            "unresolved": unresolved,
            "swapped_inverse": swapped,
            "mixed_forward": mixed_forward.model_dump(mode="json"),
            "mixed_reverse": mixed_reverse.model_dump(mode="json"),
            "support_plus_irrelevant": support_irrelevant.model_dump(mode="json"),
            "support_plus_unresolved": support_unresolved.model_dump(mode="json"),
            "pass": categorical_regressions_pass,
        },
        "interface_controls": {
            "consumer_no_authority_evaluator_parameter": consumer_no_evaluator_parameter,
            "consumer_no_authority_result_parameter": consumer_no_authority_result_parameter,
            "forbidden_inputs_rejected": forbidden_inputs,
            "forbidden_scalar_or_polarity_surface_present": forbidden_surface_present,
            "pass": interface_controls_pass,
        },
        "setup_valid": setup_valid,
        "authenticated_attacks_refused": authenticated_attacks_refused,
        "serialization_controls_pass": serialization_controls_pass,
        "categorical_regressions_pass": categorical_regressions_pass,
        "nonwarranted_atom_produced_deciding_conclusion": any_authenticated_nonwarranted_decided,
        "research_disposition": disposition,
        "bounded_inference": (
            "Within the frozen RC8J and already-constructed typed-comparison fragment, an HMAC-authenticated portable warrant receipt can bind a transported authority result to the exact preregistered authority-relevant case projection and support scoreless categorical relation derivation without rerunning RC8J at the consumer."
            if disposition == "SUPPORTED_WITH_BOUNDS"
            else None
        ),
        "not_established": [
            "production cryptographic architecture",
            "production key management, rotation, revocation, or compromise recovery",
            "asymmetric signatures or public-verification trust",
            "generic semantic entailment",
            "semantic-text extraction",
            "proposition truth in the world",
            "broader semantic families",
            "Contract C projection or successor semantics",
            "Decision Engine policy",
            "independent clean-room reproduction",
        ],
        "production_promotion_authorized": False,
    }

    output_path = outdir / "RC8J-PORTABLE-BOUND-AUTHORITY-RECEIPT-RC3.json"
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
