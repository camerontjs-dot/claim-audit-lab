"""Run the preregistered RC8J atomic warranted-relation RC2 experiment."""
from __future__ import annotations

import argparse
from copy import deepcopy
import inspect
import json
from pathlib import Path
from typing import Any, Callable

from pydantic import ValidationError

from atomic_warranted_relation_rc2 import (
    AtomicAuthorityRefusal,
    ComparisonProposition,
    assess_and_derive_categorical_relation,
    compose_categorical_relations,
)
from run_authority_consumption_rc1 import (
    _load_rc8j,
    _typed_seam_control,
    _validated_b_coordinates,
)
from run_categorical_warranted_relation_rc1 import _authority, _variant


RC1A_HEAD = "6a01e5be07c0b2ddc11aeeb3974f3221eccc9c0e"
RC1_HEAD = "598968205a5371323989f972442fb9820ba19b35"
RC8J_FREEZE_COMMIT = "8e75c6782bb95c3763d06230b9c5df2b6af44054"
RC8J_CANDIDATE_BLOB = "f55156e43e0c1b4a7868bc8339585b8892edda38"
PRODUCTION_MAIN = "32275a239b68af383a56bca843e28cbc1e343976"


def _attempt(
    case: dict[str, Any],
    proposition: ComparisonProposition,
    evaluator: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    independent = _authority(case, evaluator)["authority"]
    refused = False
    refusal: dict[str, str] | None = None
    relation_dump: dict[str, Any] | None = None
    conclusion_dump: dict[str, Any] | None = None
    deciding = False

    try:
        relation = assess_and_derive_categorical_relation(
            case=case,
            proposition=proposition,
            authority_evaluator=evaluator,
        )
        conclusion = compose_categorical_relations(proposition, (relation,))
        relation_dump = relation.model_dump(mode="json")
        conclusion_dump = conclusion.model_dump(mode="json")
        deciding = conclusion.disposition == "decided"
    except AtomicAuthorityRefusal as exc:
        refused = True
        refusal = {"status": exc.status, "reason": exc.reason}

    return {
        "independent_rc8j_authority": independent,
        "atomic_refused": refused,
        "atomic_refusal": refusal,
        "derived_relation": relation_dump,
        "scoreless_conclusion": conclusion_dump,
        "produced_deciding_conclusion": deciding,
    }


def _expected_warranted(attempt: dict[str, Any]) -> bool:
    return attempt["independent_rc8j_authority"] == {
        "status": "WARRANTED",
        "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
    } and not attempt["atomic_refused"]


def _relation(attempt: dict[str, Any]) -> str | None:
    relation = attempt.get("derived_relation")
    return relation.get("relation") if isinstance(relation, dict) else None


def _verdict(attempt: dict[str, Any]) -> str | None:
    conclusion = attempt.get("scoreless_conclusion")
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
        case_id="RC2-C1-SUPPORT",
        atom_id="atom:categorical:rc2:a-gt-b:v1",
        lhs="fixture:left",
        rhs="fixture:right",
        direction="greater_than",
    )
    refute_case = _variant(
        base,
        case_id="RC2-C2-REFUTE",
        atom_id="atom:categorical:rc2:a-lt-b:v1",
        lhs="fixture:left",
        rhs="fixture:right",
        direction="less_than",
    )
    irrelevant_case = _variant(
        base,
        case_id="RC2-C10-IRRELEVANT",
        atom_id="atom:categorical:rc2:x-gt-y:v1",
        lhs="fixture:other-left",
        rhs="fixture:other-right",
        direction="greater_than",
    )
    unresolved_semantic_case = _variant(
        base,
        case_id="RC2-C10-UNRESOLVED",
        atom_id="atom:categorical:rc2:a-at-least-b:v1",
        lhs="fixture:left",
        rhs="fixture:right",
        direction="at_least",
    )

    support = _attempt(support_case, target, evaluator)
    refute = _attempt(refute_case, target, evaluator)
    irrelevant = _attempt(irrelevant_case, target, evaluator)
    unresolved_semantic = _attempt(unresolved_semantic_case, target, evaluator)
    swapped = _attempt(support_case, swapped_target, evaluator)

    # Exact RC1A replay killer: same identity, mutated payload, stale field warrant.
    replay_case = deepcopy(support_case)
    replay_case["case_id"] = "RC2-C3-EXACT-RC1A-REPLAY-KILLER"
    replay_case["proposal"]["fields"]["comparison_direction"] = "less_than"
    replay_preserved_warrant = replay_case["field_warrants"]["comparison_direction"]["value"]
    replay = _attempt(replay_case, target, evaluator)

    # Atom identity substitution: target changes, authority subject remains frozen.
    identity_case = deepcopy(support_case)
    identity_case["case_id"] = "RC2-C4-ATOM-IDENTITY-SUBSTITUTION"
    identity_case["target_atom_id"] = "atom:categorical:rc2:replacement:v1"
    identity = _attempt(identity_case, target, evaluator)

    # Claim binding substitution: raw claim changes, authority subject remains frozen.
    claim_case = deepcopy(support_case)
    claim_case["case_id"] = "RC2-C5-CLAIM-BINDING-SUBSTITUTION"
    claim_case["raw_claim_id"] = "claim:categorical:replacement"
    claim = _attempt(claim_case, target, evaluator)

    # Evidence segment unresolved authority must fail closed.
    unresolved_authority_case = deepcopy(support_case)
    unresolved_authority_case["case_id"] = "RC2-C6-UNRESOLVED-AUTHORITY"
    unresolved_authority_case["authority_subject_bundle_id"] = None
    unresolved_authority = _attempt(unresolved_authority_case, target, evaluator)

    # Caller mutation after return cannot alter the immutable returned receipt.
    mutation_case = deepcopy(support_case)
    mutation_case["case_id"] = "RC2-C7-CALLER-MUTATION-ISOLATION"
    mutation_receipt = assess_and_derive_categorical_relation(
        case=mutation_case,
        proposition=target,
        authority_evaluator=evaluator,
    )
    mutation_before = mutation_receipt.model_dump(mode="json")
    mutation_case["proposal"]["fields"]["comparison_direction"] = "less_than"
    mutation_case["target_atom_id"] = "atom:categorical:rc2:post-call-replacement:v1"
    mutation_after = mutation_receipt.model_dump(mode="json")
    caller_mutation_isolated = mutation_before == mutation_after

    # Supplemental stronger TOCTOU control: evaluator-side mutation of its input
    # must not change the untouched relation snapshot retained by RC2.
    evaluator_mutation_seen: dict[str, Any] = {}

    def mutating_wrapper(case_seen: dict[str, Any]) -> dict[str, Any]:
        observed = evaluator(case_seen)
        evaluator_mutation_seen["before"] = deepcopy(case_seen["proposal"]["fields"])
        case_seen["proposal"]["fields"]["comparison_direction"] = "less_than"
        evaluator_mutation_seen["after"] = deepcopy(case_seen["proposal"]["fields"])
        return observed

    evaluator_mutation_receipt = assess_and_derive_categorical_relation(
        case=support_case,
        proposition=target,
        authority_evaluator=mutating_wrapper,
    )
    evaluator_mutation_isolated = (
        evaluator_mutation_receipt.relation == "SUPPORTS"
        and evaluator_mutation_receipt.atom_comparison_direction == "greater_than"
        and evaluator_mutation_seen.get("after", {}).get("comparison_direction") == "less_than"
    )

    # Diagnostic-only metadata invariance.
    diagnostic_case = deepcopy(support_case)
    diagnostic_case["case_id"] = "RC2-C8-DIAGNOSTIC-METADATA-INVARIANCE"
    diagnostic_case["instrument_ids"] = ["diagnostic-one", "diagnostic-two", "diagnostic-three"]
    diagnostic_case["reader_agreement_count"] = 99
    diagnostic = _attempt(diagnostic_case, target, evaluator)
    diagnostic_unchanged = (
        _relation(diagnostic) == _relation(support)
        and _verdict(diagnostic) == _verdict(support)
        and diagnostic["independent_rc8j_authority"] == support["independent_rc8j_authority"]
    )

    # Interface and score/polarity exclusions.
    params = inspect.signature(assess_and_derive_categorical_relation).parameters
    no_authority_result_parameter = "authority_result" not in params
    exact_public_parameters = set(params) == {"case", "proposition", "authority_evaluator"}

    forbidden_inputs: dict[str, bool] = {}
    target_payload = target.model_dump(mode="json")
    for key, value in (
        ("score", 0.99),
        ("confidence", 0.99),
        ("threshold", 0.70),
        ("channel", "support"),
        ("relation_hint", "SUPPORTS"),
    ):
        rejected = False
        try:
            ComparisonProposition.model_validate({**target_payload, key: value})
        except ValidationError:
            rejected = True
        forbidden_inputs[key] = rejected

    forbidden_surface_keys = {"score", "confidence", "threshold", "channel", "relation_hint"}
    support_relation_dump = support["derived_relation"] or {}
    support_conclusion_dump = support["scoreless_conclusion"] or {}
    no_forbidden_output_surface = not forbidden_surface_keys.intersection(
        {*support_relation_dump.keys(), *support_conclusion_dump.keys()}
    )

    # Multi-relation categorical regression controls reuse only receipts created by RC2.
    support_receipt = assess_and_derive_categorical_relation(
        case=support_case, proposition=target, authority_evaluator=evaluator
    )
    refute_receipt = assess_and_derive_categorical_relation(
        case=refute_case, proposition=target, authority_evaluator=evaluator
    )
    irrelevant_receipt = assess_and_derive_categorical_relation(
        case=irrelevant_case, proposition=target, authority_evaluator=evaluator
    )
    unresolved_receipt = assess_and_derive_categorical_relation(
        case=unresolved_semantic_case, proposition=target, authority_evaluator=evaluator
    )
    mixed_forward = compose_categorical_relations(target, (support_receipt, refute_receipt))
    mixed_reverse = compose_categorical_relations(target, (refute_receipt, support_receipt))
    support_irrelevant = compose_categorical_relations(target, (support_receipt, irrelevant_receipt))
    support_unresolved = compose_categorical_relations(target, (support_receipt, unresolved_receipt))

    categorical_regressions_pass = all(
        [
            _expected_warranted(support) and _relation(support) == "SUPPORTS" and _verdict(support) == "supported",
            _expected_warranted(refute) and _relation(refute) == "REFUTES" and _verdict(refute) == "contradicted",
            _expected_warranted(irrelevant) and _relation(irrelevant) == "IRRELEVANT" and not irrelevant["produced_deciding_conclusion"],
            _expected_warranted(unresolved_semantic) and _relation(unresolved_semantic) == "UNRESOLVED" and not unresolved_semantic["produced_deciding_conclusion"],
            _expected_warranted(swapped) and _relation(swapped) == "SUPPORTS" and _verdict(swapped) == "supported",
            mixed_forward == mixed_reverse,
            mixed_forward.disposition == "abstained" and mixed_forward.reason_code == "mixed_categorical_relations",
            support_irrelevant.disposition == "decided" and support_irrelevant.verdict == "supported",
            support_unresolved.disposition == "abstained" and support_unresolved.reason_code == "unresolved_categorical_relation",
        ]
    )

    replay_control_valid = (
        replay_preserved_warrant == "greater_than"
        and replay["independent_rc8j_authority"] == {
            "status": "REJECTED",
            "reason": "FIELD_VALUE_MISMATCH:comparison_direction",
        }
    )
    replay_survived = replay_control_valid and replay["atomic_refused"] and not replay["produced_deciding_conclusion"]

    identity_control_valid = identity["independent_rc8j_authority"] == {
        "status": "REJECTED",
        "reason": "AUTHORITY_ATOM_IDENTITY_MISMATCH",
    }
    identity_survived = identity_control_valid and identity["atomic_refused"] and not identity["produced_deciding_conclusion"]

    claim_control_valid = claim["independent_rc8j_authority"] == {
        "status": "REJECTED",
        "reason": "AUTHORITY_CLAIM_MISMATCH",
    }
    claim_survived = claim_control_valid and claim["atomic_refused"] and not claim["produced_deciding_conclusion"]

    unresolved_control_valid = unresolved_authority["independent_rc8j_authority"] == {
        "status": "UNRESOLVED",
        "reason": "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED",
    }
    unresolved_survived = (
        unresolved_control_valid
        and unresolved_authority["atomic_refused"]
        and not unresolved_authority["produced_deciding_conclusion"]
    )

    setup_valid = all(
        [
            _expected_warranted(support),
            _expected_warranted(refute),
            _expected_warranted(irrelevant),
            _expected_warranted(unresolved_semantic),
            _expected_warranted(swapped),
        ]
    )
    negative_controls_valid = all(
        [replay_control_valid, identity_control_valid, claim_control_valid, unresolved_control_valid]
    )
    authority_binding_survived = all(
        [replay_survived, identity_survived, claim_survived, unresolved_survived]
    )
    interface_controls_pass = all(
        [
            no_authority_result_parameter,
            exact_public_parameters,
            all(forbidden_inputs.values()),
            no_forbidden_output_surface,
            caller_mutation_isolated,
            evaluator_mutation_isolated,
            diagnostic_unchanged,
        ]
    )

    nonwarranted_deciding = any(
        item["independent_rc8j_authority"]["status"] != "WARRANTED"
        and item["produced_deciding_conclusion"]
        for item in (replay, identity, claim, unresolved_authority)
    )

    if nonwarranted_deciding:
        disposition = "FALSIFIED_NONWARRANTED_PARTICIPATION"
    elif not setup_valid or not negative_controls_valid:
        disposition = "INCONCLUSIVE_CONTROL_PRECONDITION"
    elif not authority_binding_survived or not interface_controls_pass:
        disposition = "FALSIFIED_ATOMIC_BINDING"
    elif not categorical_regressions_pass:
        disposition = "FALSIFIED_CATEGORICAL_REGRESSION"
    else:
        disposition = "SUPPORTED_WITH_BOUNDS"

    result = {
        "experiment": "RC8J atomic warranted-relation RC2",
        "frozen_parent": {
            "rc1a_head": RC1A_HEAD,
            "rc1_head": RC1_HEAD,
        },
        "production_main_reference": PRODUCTION_MAIN,
        "rc8j": {
            "freeze_commit": RC8J_FREEZE_COMMIT,
            "candidate_blob": RC8J_CANDIDATE_BLOB,
            "verified_by_loader": True,
        },
        "candidate_interface": {
            "parameters": list(params),
            "caller_supplied_authority_result_available": not no_authority_result_parameter,
            "exact_expected_parameters": exact_public_parameters,
        },
        "controls": {
            "C1_support": support,
            "C2_refute": refute,
            "C3_exact_rc1a_payload_replay": {
                **replay,
                "preserved_field_warrant_direction": replay_preserved_warrant,
                "control_valid": replay_control_valid,
                "survived": replay_survived,
            },
            "C4_atom_identity_substitution": {
                **identity,
                "control_valid": identity_control_valid,
                "survived": identity_survived,
            },
            "C5_claim_binding_substitution": {
                **claim,
                "control_valid": claim_control_valid,
                "survived": claim_survived,
            },
            "C6_unresolved_authority": {
                **unresolved_authority,
                "control_valid": unresolved_control_valid,
                "survived": unresolved_survived,
            },
            "C7_caller_mutation_isolation": {
                "receipt_before": mutation_before,
                "receipt_after": mutation_after,
                "isolated": caller_mutation_isolated,
                "evaluator_side_mutation_isolated": evaluator_mutation_isolated,
                "evaluator_side_mutation_observed": evaluator_mutation_seen,
            },
            "C8_diagnostic_metadata_invariance": {
                "attempt": diagnostic,
                "unchanged": diagnostic_unchanged,
            },
            "C9_forbidden_inputs": forbidden_inputs,
            "C9_no_forbidden_output_surface": no_forbidden_output_surface,
            "C10_irrelevant": irrelevant,
            "C10_unresolved_semantic": unresolved_semantic,
            "C10_swapped_inverse": swapped,
            "C10_mixed_forward": mixed_forward.model_dump(mode="json"),
            "C10_mixed_reverse": mixed_reverse.model_dump(mode="json"),
            "C10_support_plus_irrelevant": support_irrelevant.model_dump(mode="json"),
            "C10_support_plus_unresolved": support_unresolved.model_dump(mode="json"),
        },
        "summary": {
            "setup_valid": setup_valid,
            "negative_controls_valid": negative_controls_valid,
            "authority_binding_survived": authority_binding_survived,
            "interface_controls_pass": interface_controls_pass,
            "categorical_regressions_pass": categorical_regressions_pass,
            "nonwarranted_atom_produced_deciding_conclusion": nonwarranted_deciding,
        },
        "research_disposition": disposition,
        "bounded_inference_if_supported": (
            "Within the already-constructed typed comparison fragment, authority evaluation and "
            "categorical relation derivation can share one captured case value so that a caller "
            "cannot replay a stale authority result against a different semantic payload, while "
            "retaining scoreless proposition composition."
        ),
        "not_established": [
            "portable or cryptographically bound authority receipts",
            "generic semantic entailment",
            "semantic-text extraction",
            "proposition truth in the world",
            "Contract C projection",
            "Decision Engine policy",
            "production CAL architecture",
            "release or promotion",
        ],
        "production_promotion_authorized": False,
    }

    out = run_output / "RC8J-ATOMIC-WARRANTED-RELATION-RC2.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
