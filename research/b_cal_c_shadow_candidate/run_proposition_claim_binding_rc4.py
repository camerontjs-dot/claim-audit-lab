"""Run the preregistered proposition-content / claim-identity binding RC4 experiment."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import secrets
from typing import Any

from portable_bound_authority_receipt_rc3 import (
    PortableReceiptRefusal,
    issue_portable_warrant,
    serialize_portable_warrant,
    verify_and_derive_categorical_relation,
)
from proposition_claim_binding_rc4 import (
    ComparisonProposition,
    PropositionBindingRefusal,
    compose_categorical_relations,
    issue_proposition_binding,
    proposition_semantic_digest,
    serialize_proposition_binding,
    verify_bound_claim_warrant_and_derive_relation,
    verify_proposition_binding,
)
from run_authority_consumption_rc1 import (
    _load_rc8j,
    _typed_seam_control,
    _validated_b_coordinates,
)
from run_categorical_warranted_relation_rc1 import _authority, _variant


PRODUCTION_MAIN = "32275a239b68af383a56bca843e28cbc1e343976"
RC3_HEAD = "3f13b162d4b0d0cc837c99b9ad830c4c47707270"
RC2_HEAD = "0c324a6a866f1bc0ce678c78d6502c6b314386c2"
RC8J_FREEZE_COMMIT = "8e75c6782bb95c3763d06230b9c5df2b6af44054"
RC8J_CANDIDATE_BLOB = "f55156e43e0c1b4a7868bc8339585b8892edda38"


def _target(
    claim_id: str,
    *,
    lhs: str = "fixture:left",
    rhs: str = "fixture:right",
    direction: str = "greater_than",
) -> ComparisonProposition:
    return ComparisonProposition(
        claim_id=claim_id,
        family="comparison",
        lhs_entity=lhs,
        rhs_entity=rhs,
        comparison_direction=direction,
    )


def _issue_warrant(case: dict[str, Any], evaluator: Any, key: bytes) -> str:
    receipt = issue_portable_warrant(
        case=case,
        authority_evaluator=evaluator,
        key=key,
        key_id="rc4-warrant-key",
    )
    return serialize_portable_warrant(receipt)


def _issue_prop(prop: ComparisonProposition, key: bytes) -> str:
    receipt = issue_proposition_binding(
        proposition=prop,
        key=key,
        key_id="rc4-proposition-key",
    )
    return serialize_proposition_binding(receipt)


def _combined_attempt(
    *,
    case: dict[str, Any],
    proposition: ComparisonProposition,
    warrant: str,
    warrant_key: bytes,
    prop_receipt: str,
    prop_key: bytes,
) -> dict[str, Any]:
    try:
        relation = verify_bound_claim_warrant_and_derive_relation(
            case=case,
            proposition=proposition,
            warrant_receipt_transport=warrant,
            warrant_trusted_keys={"rc4-warrant-key": warrant_key},
            proposition_receipt_transport=prop_receipt,
            proposition_trusted_keys={"rc4-proposition-key": prop_key},
        )
        conclusion = compose_categorical_relations(proposition, (relation,))
        return {
            "refused": False,
            "refusal_layer": None,
            "refusal_code": None,
            "relation": relation.model_dump(mode="json"),
            "conclusion": conclusion.model_dump(mode="json"),
            "produced_deciding_conclusion": conclusion.disposition == "decided",
        }
    except PropositionBindingRefusal as exc:
        return {
            "refused": True,
            "refusal_layer": "proposition_binding",
            "refusal_code": exc.code,
            "refusal_detail": exc.detail,
            "relation": None,
            "conclusion": None,
            "produced_deciding_conclusion": False,
        }
    except PortableReceiptRefusal as exc:
        return {
            "refused": True,
            "refusal_layer": "portable_warrant",
            "refusal_code": exc.code,
            "refusal_detail": exc.detail,
            "relation": None,
            "conclusion": None,
            "produced_deciding_conclusion": False,
        }


def _weak_rc3_attempt(
    *,
    case: dict[str, Any],
    proposition: ComparisonProposition,
    warrant: str,
    warrant_key: bytes,
) -> dict[str, Any]:
    try:
        relation = verify_and_derive_categorical_relation(
            case=case,
            proposition=proposition,
            receipt_transport=warrant,
            trusted_keys={"rc4-warrant-key": warrant_key},
        )
        conclusion = compose_categorical_relations(proposition, (relation,))
        return {
            "refused": False,
            "relation": relation.model_dump(mode="json"),
            "conclusion": conclusion.model_dump(mode="json"),
        }
    except PortableReceiptRefusal as exc:
        return {
            "refused": True,
            "refusal_code": exc.code,
            "relation": None,
            "conclusion": None,
        }


def _relation(attempt: dict[str, Any]) -> str | None:
    relation = attempt.get("relation")
    return relation.get("relation") if isinstance(relation, dict) else None


def _verdict(attempt: dict[str, Any]) -> str | None:
    conclusion = attempt.get("conclusion")
    return conclusion.get("verdict") if isinstance(conclusion, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-output", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    args = parser.parse_args()

    run_output = args.run_output.resolve()
    run_output.mkdir(parents=True, exist_ok=True)
    evaluator = _load_rc8j(args.rc8j_root.resolve())
    coords = _validated_b_coordinates(run_output)
    base = _typed_seam_control(coords)
    claim_id = coords["claim_id"]

    warrant_key = secrets.token_bytes(32)
    prop_key = secrets.token_bytes(32)
    wrong_prop_key = secrets.token_bytes(32)

    target = _target(claim_id)
    substituted = _target(claim_id, direction="less_than")
    swapped = _target(
        claim_id,
        lhs="fixture:right",
        rhs="fixture:left",
        direction="less_than",
    )

    support_case = _variant(
        base,
        case_id="RC4-C1-SUPPORT",
        atom_id="atom:categorical:rc4:a-gt-b:v1",
        lhs="fixture:left",
        rhs="fixture:right",
        direction="greater_than",
    )
    support_authority = _authority(support_case, evaluator)["authority"]
    support_warrant = _issue_warrant(support_case, evaluator, warrant_key)
    target_binding = _issue_prop(target, prop_key)

    baseline = _combined_attempt(
        case=support_case,
        proposition=target,
        warrant=support_warrant,
        warrant_key=warrant_key,
        prop_receipt=target_binding,
        prop_key=prop_key,
    )

    weak_substitution = _weak_rc3_attempt(
        case=support_case,
        proposition=substituted,
        warrant=support_warrant,
        warrant_key=warrant_key,
    )

    stale_direction = _combined_attempt(
        case=support_case,
        proposition=substituted,
        warrant=support_warrant,
        warrant_key=warrant_key,
        prop_receipt=target_binding,
        prop_key=prop_key,
    )

    forged_payload = json.loads(target_binding)
    forged_payload["body"]["proposition_digest"] = proposition_semantic_digest(substituted)
    recomputed_digest_stale_mac = _combined_attempt(
        case=support_case,
        proposition=substituted,
        warrant=support_warrant,
        warrant_key=warrant_key,
        prop_receipt=json.dumps(forged_payload),
        prop_key=prop_key,
    )

    lhs_sub = _target(claim_id, lhs="fixture:other-left", rhs="fixture:right")
    rhs_sub = _target(claim_id, lhs="fixture:left", rhs="fixture:other-right")
    claim_sub = _target("claim:categorical:replacement")

    identity_attacks = {
        "lhs_substitution": _combined_attempt(
            case=support_case,
            proposition=lhs_sub,
            warrant=support_warrant,
            warrant_key=warrant_key,
            prop_receipt=target_binding,
            prop_key=prop_key,
        ),
        "rhs_substitution": _combined_attempt(
            case=support_case,
            proposition=rhs_sub,
            warrant=support_warrant,
            warrant_key=warrant_key,
            prop_receipt=target_binding,
            prop_key=prop_key,
        ),
        "claim_id_substitution": _combined_attempt(
            case=support_case,
            proposition=claim_sub,
            warrant=support_warrant,
            warrant_key=warrant_key,
            prop_receipt=target_binding,
            prop_key=prop_key,
        ),
        "swapped_inverse_stale_receipt": _combined_attempt(
            case=support_case,
            proposition=swapped,
            warrant=support_warrant,
            warrant_key=warrant_key,
            prop_receipt=target_binding,
            prop_key=prop_key,
        ),
    }

    swapped_bound = _combined_attempt(
        case=support_case,
        proposition=swapped,
        warrant=support_warrant,
        warrant_key=warrant_key,
        prop_receipt=_issue_prop(swapped, prop_key),
        prop_key=prop_key,
    )

    # Receipt-authentication and strict-transport controls.
    wrong_key_refused = False
    wrong_key_code = None
    try:
        verify_proposition_binding(
            proposition=target,
            receipt_transport=target_binding,
            trusted_keys={"rc4-proposition-key": wrong_prop_key},
        )
    except PropositionBindingRefusal as exc:
        wrong_key_refused = True
        wrong_key_code = exc.code

    tampered_key_payload = json.loads(target_binding)
    tampered_key_payload["body"]["key_id"] = "unknown-key"
    tampered_key_refused = False
    tampered_key_code = None
    try:
        verify_proposition_binding(
            proposition=target,
            receipt_transport=json.dumps(tampered_key_payload),
            trusted_keys={"rc4-proposition-key": prop_key},
        )
    except PropositionBindingRefusal as exc:
        tampered_key_refused = True
        tampered_key_code = exc.code

    mac_payload = json.loads(target_binding)
    original_mac = mac_payload["mac"]
    mac_payload["mac"] = ("0" if original_mac[0] != "0" else "1") + original_mac[1:]
    mac_refused = False
    mac_code = None
    try:
        verify_proposition_binding(
            proposition=target,
            receipt_transport=json.dumps(mac_payload),
            trusted_keys={"rc4-proposition-key": prop_key},
        )
    except PropositionBindingRefusal as exc:
        mac_refused = True
        mac_code = exc.code

    truncated_payload = json.loads(target_binding)
    truncated_payload["mac"] = truncated_payload["mac"][:-1]
    truncated_refused = False
    truncated_code = None
    try:
        verify_proposition_binding(
            proposition=target,
            receipt_transport=json.dumps(truncated_payload),
            trusted_keys={"rc4-proposition-key": prop_key},
        )
    except PropositionBindingRefusal as exc:
        truncated_refused = True
        truncated_code = exc.code

    partial_payload = json.loads(target_binding)
    del partial_payload["body"]["proposition_digest"]
    partial_refused = False
    partial_code = None
    try:
        verify_proposition_binding(
            proposition=target,
            receipt_transport=json.dumps(partial_payload),
            trusted_keys={"rc4-proposition-key": prop_key},
        )
    except PropositionBindingRefusal as exc:
        partial_refused = True
        partial_code = exc.code

    unknown_payload = json.loads(target_binding)
    unknown_payload["unexpected"] = True
    unknown_refused = False
    unknown_code = None
    try:
        verify_proposition_binding(
            proposition=target,
            receipt_transport=json.dumps(unknown_payload),
            trusted_keys={"rc4-proposition-key": prop_key},
        )
    except PropositionBindingRefusal as exc:
        unknown_refused = True
        unknown_code = exc.code

    duplicate_transport = (
        '{"body":{},"body":{},"auth_algorithm":"hmac-sha256","mac":"'
        + ("0" * 64)
        + '"}'
    )
    duplicate_refused = False
    duplicate_code = None
    try:
        verify_proposition_binding(
            proposition=target,
            receipt_transport=duplicate_transport,
            trusted_keys={"rc4-proposition-key": prop_key},
        )
    except PropositionBindingRefusal as exc:
        duplicate_refused = True
        duplicate_code = exc.code

    target_receipt_obj = issue_proposition_binding(
        proposition=target,
        key=prop_key,
        key_id="rc4-proposition-key",
    )
    pretty_transport = serialize_proposition_binding(target_receipt_obj, pretty=True)
    pretty_verified = False
    try:
        verify_proposition_binding(
            proposition=target,
            receipt_transport=pretty_transport,
            trusted_keys={"rc4-proposition-key": prop_key},
        )
        pretty_verified = True
    except PropositionBindingRefusal:
        pass

    reconstructed = ComparisonProposition.model_validate(
        {
            "comparison_direction": "greater_than",
            "rhs_entity": "fixture:right",
            "lhs_entity": "fixture:left",
            "family": "comparison",
            "claim_id": claim_id,
        }
    )
    reconstruction_same_digest = (
        proposition_semantic_digest(reconstructed) == proposition_semantic_digest(target)
    )
    reconstruction_verified = False
    try:
        verify_proposition_binding(
            proposition=reconstructed,
            receipt_transport=target_binding,
            trusted_keys={"rc4-proposition-key": prop_key},
        )
        reconstruction_verified = True
    except PropositionBindingRefusal:
        pass

    # Inherited RC3 atom-warrant binding must still close the old replay path.
    mutated_atom = deepcopy(support_case)
    mutated_atom["case_id"] = "RC4-C20-MUTATED-ATOM"
    mutated_atom["proposal"]["fields"]["comparison_direction"] = "less_than"
    mutated_atom_authority = _authority(mutated_atom, evaluator)["authority"]
    mutated_atom_attempt = _combined_attempt(
        case=mutated_atom,
        proposition=target,
        warrant=support_warrant,
        warrant_key=warrant_key,
        prop_receipt=target_binding,
        prop_key=prop_key,
    )

    # Scoreless categorical regression matrix through the combined boundary.
    refute_case = _variant(
        base,
        case_id="RC4-R-REFUTE",
        atom_id="atom:categorical:rc4:a-lt-b:v1",
        lhs="fixture:left",
        rhs="fixture:right",
        direction="less_than",
    )
    irrelevant_case = _variant(
        base,
        case_id="RC4-R-IRRELEVANT",
        atom_id="atom:categorical:rc4:x-gt-y:v1",
        lhs="fixture:other-left",
        rhs="fixture:other-right",
        direction="greater_than",
    )
    unresolved_case = _variant(
        base,
        case_id="RC4-R-UNRESOLVED",
        atom_id="atom:categorical:rc4:a-at-least-b:v1",
        lhs="fixture:left",
        rhs="fixture:right",
        direction="at_least",
    )

    def relation_for(case: dict[str, Any], proposition: ComparisonProposition) -> Any:
        return verify_bound_claim_warrant_and_derive_relation(
            case=case,
            proposition=proposition,
            warrant_receipt_transport=_issue_warrant(case, evaluator, warrant_key),
            warrant_trusted_keys={"rc4-warrant-key": warrant_key},
            proposition_receipt_transport=_issue_prop(proposition, prop_key),
            proposition_trusted_keys={"rc4-proposition-key": prop_key},
        )

    support_relation = relation_for(support_case, target)
    refute_relation = relation_for(refute_case, target)
    irrelevant_relation = relation_for(irrelevant_case, target)
    unresolved_relation = relation_for(unresolved_case, target)
    swapped_relation = relation_for(support_case, swapped)

    supported = compose_categorical_relations(target, (support_relation,))
    contradicted = compose_categorical_relations(target, (refute_relation,))
    irrelevant_only = compose_categorical_relations(target, (irrelevant_relation,))
    unresolved_only = compose_categorical_relations(target, (unresolved_relation,))
    swapped_supported = compose_categorical_relations(swapped, (swapped_relation,))
    mixed_forward = compose_categorical_relations(target, (support_relation, refute_relation))
    mixed_reverse = compose_categorical_relations(target, (refute_relation, support_relation))
    support_irrelevant = compose_categorical_relations(target, (support_relation, irrelevant_relation))
    support_unresolved = compose_categorical_relations(target, (support_relation, unresolved_relation))

    categorical_regressions_pass = all(
        [
            support_relation.relation == "SUPPORTS" and supported.verdict == "supported",
            refute_relation.relation == "REFUTES" and contradicted.verdict == "contradicted",
            irrelevant_relation.relation == "IRRELEVANT"
            and irrelevant_only.reason_code == "no_deciding_categorical_relation",
            unresolved_relation.relation == "UNRESOLVED"
            and unresolved_only.reason_code == "unresolved_categorical_relation",
            swapped_relation.relation == "SUPPORTS" and swapped_supported.verdict == "supported",
            mixed_forward == mixed_reverse
            and mixed_forward.reason_code == "mixed_categorical_relations",
            support_irrelevant.verdict == "supported",
            support_unresolved.reason_code == "unresolved_categorical_relation",
        ]
    )

    weak_control_valid = (
        support_authority == {
            "status": "WARRANTED",
            "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
        }
        and not baseline["refused"]
        and _relation(baseline) == "SUPPORTS"
        and _verdict(baseline) == "supported"
        and not weak_substitution["refused"]
        and _relation(weak_substitution) == "REFUTES"
        and _verdict(weak_substitution) == "contradicted"
    )

    proposition_attacks = {
        "same_claim_direction_substitution": stale_direction,
        "recomputed_digest_stale_mac": recomputed_digest_stale_mac,
        **identity_attacks,
    }
    proposition_attacks_refused = all(
        item["refused"] and not item["produced_deciding_conclusion"]
        for item in proposition_attacks.values()
    )

    swapped_exact_identity_control_pass = (
        identity_attacks["swapped_inverse_stale_receipt"]["refused"]
        and not swapped_bound["refused"]
        and _relation(swapped_bound) == "SUPPORTS"
        and _verdict(swapped_bound) == "supported"
    )

    parser_auth_controls_pass = all(
        [
            wrong_key_refused and wrong_key_code == "MAC_MISMATCH",
            tampered_key_refused and tampered_key_code == "UNTRUSTED_KEY_ID",
            mac_refused and mac_code == "MAC_MISMATCH",
            truncated_refused and truncated_code == "INVALID_RECEIPT_SCHEMA",
            partial_refused and partial_code == "INVALID_RECEIPT_SCHEMA",
            unknown_refused and unknown_code == "INVALID_RECEIPT_SCHEMA",
            duplicate_refused and duplicate_code == "DUPLICATE_JSON_KEY",
            pretty_verified,
            reconstruction_same_digest,
            reconstruction_verified,
        ]
    )

    inherited_warrant_survived = (
        mutated_atom_authority["status"] != "WARRANTED"
        and mutated_atom_attempt["refused"]
        and mutated_atom_attempt["refusal_layer"] == "portable_warrant"
        and not mutated_atom_attempt["produced_deciding_conclusion"]
    )

    if not weak_control_valid:
        disposition = "INCONCLUSIVE_CONTROL_PRECONDITION"
    elif not proposition_attacks_refused or not swapped_exact_identity_control_pass or not parser_auth_controls_pass:
        disposition = "FALSIFIED_PROPOSITION_CLAIM_BINDING"
    elif not inherited_warrant_survived:
        disposition = "FALSIFIED_INHERITED_WARRANT_BINDING"
    elif not categorical_regressions_pass:
        disposition = "FALSIFIED_CATEGORICAL_REGRESSION"
    else:
        disposition = "SUPPORTED_WITH_BOUNDS"

    result = {
        "experiment": "RC8J proposition-content / claim-identity binding RC4",
        "lineage": {
            "production_main": PRODUCTION_MAIN,
            "rc3_parent_head": RC3_HEAD,
            "rc2_head": RC2_HEAD,
            "rc8j_freeze_commit": RC8J_FREEZE_COMMIT,
            "rc8j_candidate_blob": RC8J_CANDIDATE_BLOB,
        },
        "trust_model": {
            "atom_warrant": "RC3 HMAC authenticated portable warrant",
            "proposition_binding": "separate HMAC authenticated claim/proposition binding",
            "separate_runtime_keys": True,
            "key_material_recorded": False,
            "production_key_management_established": False,
        },
        "baseline": {
            "authority": support_authority,
            "combined": baseline,
        },
        "weak_claim_id_only_control": {
            "same_claim_id": target.claim_id == substituted.claim_id,
            "baseline_proposition": target.model_dump(mode="json"),
            "substituted_proposition": substituted.model_dump(mode="json"),
            "rc3_only_substitution": weak_substitution,
            "control_valid": weak_control_valid,
        },
        "proposition_binding_attacks": proposition_attacks,
        "proposition_attacks_refused": proposition_attacks_refused,
        "swapped_inverse_exact_identity_control": {
            "stale_receipt_attempt": identity_attacks["swapped_inverse_stale_receipt"],
            "separately_bound_attempt": swapped_bound,
            "pass": swapped_exact_identity_control_pass,
        },
        "receipt_transport_controls": {
            "wrong_key": {"refused": wrong_key_refused, "code": wrong_key_code},
            "tampered_key_id": {"refused": tampered_key_refused, "code": tampered_key_code},
            "mac_mutation": {"refused": mac_refused, "code": mac_code},
            "truncated_mac": {"refused": truncated_refused, "code": truncated_code},
            "partial_receipt": {"refused": partial_refused, "code": partial_code},
            "unknown_field": {"refused": unknown_refused, "code": unknown_code},
            "duplicate_json_key": {"refused": duplicate_refused, "code": duplicate_code},
            "pretty_reordered_transport_verified": pretty_verified,
            "reconstructed_model_same_digest": reconstruction_same_digest,
            "reconstructed_model_verified": reconstruction_verified,
            "pass": parser_auth_controls_pass,
        },
        "inherited_atom_warrant_control": {
            "independent_mutated_atom_authority": mutated_atom_authority,
            "combined_attempt": mutated_atom_attempt,
            "survived": inherited_warrant_survived,
        },
        "categorical_regressions": {
            "support": f"{support_relation.relation} -> {supported.verdict}",
            "refute": f"{refute_relation.relation} -> {contradicted.verdict}",
            "irrelevant": f"{irrelevant_relation.relation} -> {irrelevant_only.reason_code}",
            "unresolved": f"{unresolved_relation.relation} -> {unresolved_only.reason_code}",
            "swapped": f"{swapped_relation.relation} -> {swapped_supported.verdict}",
            "mixed_order_invariant": mixed_forward == mixed_reverse,
            "support_plus_irrelevant": support_irrelevant.model_dump(mode="json"),
            "support_plus_unresolved": support_unresolved.model_dump(mode="json"),
            "pass": categorical_regressions_pass,
        },
        "research_disposition": disposition,
        "bounded_inference": (
            "Within the already-constructed typed strict-comparison fragment and the bounded "
            "HMAC research trust model, exact proposition content can be authenticated to a "
            "claim identity at the relation-consumer boundary while preserving RC3 atom-warrant "
            "transport and scoreless categorical composition."
        ),
        "not_established": [
            "production claim-id issuance trust",
            "semantic-equivalence normalization",
            "natural-language claim parsing or semantic extraction",
            "generic semantic entailment",
            "proposition truth in the world",
            "broader semantic families",
            "production cryptographic key management",
            "asymmetric signatures or public verification",
            "Contract C projection or successor semantics",
            "Decision Engine policy",
            "production CAL architecture",
            "independent clean-room recoverability",
        ],
        "production_promotion_authorized": False,
    }

    out = run_output / "RC8J-PROPOSITION-CLAIM-BINDING-RC4.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
