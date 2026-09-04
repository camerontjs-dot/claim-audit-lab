"""Run the preregistered categorical warranted-relation participation experiment."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Callable

from pydantic import ValidationError

from categorical_warranted_relation_rc1 import (
    ComparisonProposition,
    compose_categorical_relations,
    derive_categorical_relation,
)
from run_authority_consumption_rc1 import (
    _load_rc8j,
    _typed_seam_control,
    _validated_b_coordinates,
)


PARENT_SCORE_HEAD = "884405755eee6e71434c43ccae0d95d5fa1fd517"
DECISION_MODEL_BLOB = "f0d9d3bc061d966ed9c8c16b3424b3dd5c3bb339"
RC8J_FREEZE_COMMIT = "8e75c6782bb95c3763d06230b9c5df2b6af44054"
RC8J_CANDIDATE_BLOB = "f55156e43e0c1b4a7868bc8339585b8892edda38"


def _authority(case: dict[str, Any], evaluator: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
    observed = evaluator(deepcopy(case))
    if not isinstance(observed, dict):
        raise AssertionError("RC8J evaluator returned a non-object")
    status = observed.get("authority_status")
    reason = observed.get("reason")
    if status not in {"WARRANTED", "REJECTED", "UNRESOLVED", "NO_ASSESSMENT"}:
        raise AssertionError(f"unexpected RC8J status: {status!r}")
    if not isinstance(reason, str) or not reason:
        raise AssertionError("RC8J evaluator returned an invalid reason")
    return {
        "authority": {"status": status, "reason": reason},
        "research_dependency": {
            "freeze_commit": RC8J_FREEZE_COMMIT,
            "candidate_blob": RC8J_CANDIDATE_BLOB,
        },
    }


def _variant(
    base: dict[str, Any],
    *,
    case_id: str,
    atom_id: str,
    lhs: str,
    rhs: str,
    direction: str,
) -> dict[str, Any]:
    case = deepcopy(base)
    case["case_id"] = case_id
    case["target_atom_id"] = atom_id
    case["authority_subject_atom_id"] = atom_id
    fields = {
        "lhs_entity": lhs,
        "rhs_entity": rhs,
        "comparison_direction": direction,
    }
    case["proposal"]["fields"] = fields
    for field, value in fields.items():
        case["field_warrants"][field]["value"] = value
    return case


def _require_warranted(label: str, result: dict[str, Any]) -> None:
    authority = result["authority"]
    if authority != {"status": "WARRANTED", "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED"}:
        raise AssertionError(f"{label} did not remain fully warranted: {authority}")


def _case_row(case_id: str, authority_result: dict[str, Any], relation: Any, conclusion: Any) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "authority": authority_result["authority"],
        "derived_relation": relation.model_dump(mode="json"),
        "scoreless_conclusion": conclusion.model_dump(mode="json"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-output", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    args = parser.parse_args()

    run_output = args.run_output.resolve()
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
        case_id="C1-SUPPORT",
        atom_id="atom:categorical:a-gt-b:v1",
        lhs="fixture:left",
        rhs="fixture:right",
        direction="greater_than",
    )
    refute_case = _variant(
        base,
        case_id="C2-REFUTE",
        atom_id="atom:categorical:a-lt-b:v1",
        lhs="fixture:left",
        rhs="fixture:right",
        direction="less_than",
    )
    irrelevant_case = _variant(
        base,
        case_id="C4-IRRELEVANT",
        atom_id="atom:categorical:x-gt-y:v1",
        lhs="fixture:other-left",
        rhs="fixture:other-right",
        direction="greater_than",
    )
    unresolved_semantic_case = _variant(
        base,
        case_id="C5-UNRESOLVED-SEMANTIC-RELATION",
        atom_id="atom:categorical:a-at-least-b:v1",
        lhs="fixture:left",
        rhs="fixture:right",
        direction="at_least",
    )

    support_auth = _authority(support_case, evaluator)
    refute_auth = _authority(refute_case, evaluator)
    irrelevant_auth = _authority(irrelevant_case, evaluator)
    unresolved_semantic_auth = _authority(unresolved_semantic_case, evaluator)
    for label, result in (
        ("support", support_auth),
        ("refute", refute_auth),
        ("irrelevant", irrelevant_auth),
        ("unresolved-semantic", unresolved_semantic_auth),
    ):
        _require_warranted(label, result)

    support = derive_categorical_relation(
        case=support_case, authority_result=support_auth, proposition=target
    )
    refute = derive_categorical_relation(
        case=refute_case, authority_result=refute_auth, proposition=target
    )
    irrelevant = derive_categorical_relation(
        case=irrelevant_case, authority_result=irrelevant_auth, proposition=target
    )
    unresolved_semantic = derive_categorical_relation(
        case=unresolved_semantic_case,
        authority_result=unresolved_semantic_auth,
        proposition=target,
    )
    swapped_equivalent = derive_categorical_relation(
        case=support_case, authority_result=support_auth, proposition=swapped_target
    )

    if support.relation != "SUPPORTS":
        raise AssertionError(f"same strict comparison did not SUPPORT: {support.relation}")
    if refute.relation != "REFUTES":
        raise AssertionError(f"opposite strict comparison did not REFUTE: {refute.relation}")
    if irrelevant.relation != "IRRELEVANT":
        raise AssertionError(f"different entity pair was not IRRELEVANT: {irrelevant.relation}")
    if unresolved_semantic.relation != "UNRESOLVED":
        raise AssertionError(
            f"unsupported same-pair relation was not UNRESOLVED: {unresolved_semantic.relation}"
        )
    if swapped_equivalent.relation != "SUPPORTS":
        raise AssertionError("swapped inverse strict comparison lost semantic equivalence")

    supported = compose_categorical_relations(target, (support,))
    contradicted = compose_categorical_relations(target, (refute,))
    mixed_forward = compose_categorical_relations(target, (support, refute))
    mixed_reverse = compose_categorical_relations(target, (refute, support))
    irrelevant_only = compose_categorical_relations(target, (irrelevant,))
    support_irrelevant = compose_categorical_relations(target, (support, irrelevant))
    unresolved_only = compose_categorical_relations(target, (unresolved_semantic,))
    support_unresolved = compose_categorical_relations(target, (support, unresolved_semantic))
    swapped_supported = compose_categorical_relations(swapped_target, (swapped_equivalent,))

    if supported.verdict != "supported" or supported.disposition != "decided":
        raise AssertionError(f"support case did not decide supported: {supported}")
    if contradicted.verdict != "contradicted" or contradicted.disposition != "decided":
        raise AssertionError(f"refute case did not decide contradicted: {contradicted}")
    if mixed_forward.reason_code != "mixed_categorical_relations" or mixed_forward.disposition != "abstained":
        raise AssertionError(f"mixed case did not abstain: {mixed_forward}")
    if mixed_forward != mixed_reverse:
        raise AssertionError("categorical composition changed under relation input reordering")
    if irrelevant_only.reason_code != "no_deciding_categorical_relation":
        raise AssertionError(f"irrelevant-only case became deciding: {irrelevant_only}")
    if support_irrelevant.verdict != "supported":
        raise AssertionError("irrelevant categorical evidence changed supported conclusion")
    if unresolved_only.reason_code != "unresolved_categorical_relation":
        raise AssertionError("unresolved relation was laundered into another abstention state")
    if support_unresolved.reason_code != "unresolved_categorical_relation":
        raise AssertionError("support + unresolved failed to abstain closed")
    if swapped_supported.verdict != "supported":
        raise AssertionError("swapped-equivalent support did not compose to supported")

    diagnostic_case = deepcopy(support_case)
    diagnostic_case["case_id"] = "C10-DIAGNOSTIC-METADATA-INVARIANCE"
    diagnostic_case["instrument_ids"] = ["diagnostic-one", "diagnostic-two", "diagnostic-three"]
    diagnostic_case["reader_agreement_count"] = 99
    diagnostic_auth = _authority(diagnostic_case, evaluator)
    _require_warranted("diagnostic-metadata mutation", diagnostic_auth)
    diagnostic_relation = derive_categorical_relation(
        case=diagnostic_case, authority_result=diagnostic_auth, proposition=target
    )
    diagnostic_conclusion = compose_categorical_relations(target, (diagnostic_relation,))
    if diagnostic_relation != support or diagnostic_conclusion != supported:
        raise AssertionError("diagnostic reader/instrument metadata changed relation or conclusion")

    unresolved_authority_case = deepcopy(support_case)
    unresolved_authority_case["case_id"] = "C11-UNRESOLVED-AUTHORITY-REFUSED"
    unresolved_authority_case["authority_subject_bundle_id"] = None
    unresolved_authority = _authority(unresolved_authority_case, evaluator)
    if unresolved_authority["authority"] != {
        "status": "UNRESOLVED",
        "reason": "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED",
    }:
        raise AssertionError(f"authority negative control changed: {unresolved_authority}")
    unresolved_authority_refused = False
    unresolved_authority_error = None
    try:
        derive_categorical_relation(
            case=unresolved_authority_case,
            authority_result=unresolved_authority,
            proposition=target,
        )
    except ValueError as exc:
        unresolved_authority_refused = True
        unresolved_authority_error = str(exc)
    if not unresolved_authority_refused:
        raise AssertionError("non-warranted atom entered categorical relation operator")

    proposition_payload = target.model_dump(mode="json")
    forbidden_inputs: dict[str, bool] = {}
    for key, value in (
        ("score", 0.99),
        ("channel", "support"),
        ("relation_hint", "SUPPORTS"),
    ):
        rejected = False
        try:
            ComparisonProposition.model_validate({**proposition_payload, key: value})
        except ValidationError:
            rejected = True
        if not rejected:
            raise AssertionError(f"caller-supplied forbidden field was accepted: {key}")
        forbidden_inputs[key] = rejected

    relation_dump = support.model_dump(mode="json")
    conclusion_dump = supported.model_dump(mode="json")
    forbidden_surface_keys = {"score", "confidence", "channel", "threshold", "relation_hint"}
    if forbidden_surface_keys.intersection(relation_dump):
        raise AssertionError("derived relation receipt exposed an unowned scalar/polarity surface")
    if forbidden_surface_keys.intersection(conclusion_dump):
        raise AssertionError("scoreless conclusion exposed an unowned scalar/polarity surface")

    cases = [
        _case_row("C1-SUPPORT", support_auth, support, supported),
        _case_row("C2-REFUTE", refute_auth, refute, contradicted),
        {
            "case_id": "C3-MIXED",
            "authority": [support_auth["authority"], refute_auth["authority"]],
            "derived_relations": [
                support.model_dump(mode="json"),
                refute.model_dump(mode="json"),
            ],
            "scoreless_conclusion": mixed_forward.model_dump(mode="json"),
            "order_invariant": mixed_forward == mixed_reverse,
        },
        _case_row("C4-IRRELEVANT", irrelevant_auth, irrelevant, irrelevant_only),
        _case_row(
            "C5-UNRESOLVED-SEMANTIC-RELATION",
            unresolved_semantic_auth,
            unresolved_semantic,
            unresolved_only,
        ),
        {
            "case_id": "C6-SUPPORT-PLUS-IRRELEVANT",
            "scoreless_conclusion": support_irrelevant.model_dump(mode="json"),
        },
        {
            "case_id": "C7-SUPPORT-PLUS-UNRESOLVED",
            "scoreless_conclusion": support_unresolved.model_dump(mode="json"),
        },
        {
            "case_id": "C8-SWAPPED-SEMANTIC-EQUIVALENCE",
            "derived_relation": swapped_equivalent.model_dump(mode="json"),
            "scoreless_conclusion": swapped_supported.model_dump(mode="json"),
        },
        {
            "case_id": "C10-DIAGNOSTIC-METADATA-INVARIANCE",
            "authority": diagnostic_auth["authority"],
            "relation_unchanged": diagnostic_relation == support,
            "conclusion_unchanged": diagnostic_conclusion == supported,
        },
    ]

    result = {
        "experiment": "RC8J categorical warranted-relation participation RC1",
        "parent_score_falsifier_head": PARENT_SCORE_HEAD,
        "frozen_decision_model_blob": DECISION_MODEL_BLOB,
        "rc8j": {
            "freeze_commit": RC8J_FREEZE_COMMIT,
            "candidate_blob": RC8J_CANDIDATE_BLOB,
            "verified_by_loader": True,
        },
        "semantic_fragment": "already-constructed typed strict comparison atoms only",
        "semantic_values_inferred_from_text": False,
        "caller_supplied_polarity_used": False,
        "scalar_decision_strength_used": False,
        "threshold_used": False,
        "cases": cases,
        "authority_negative_control": {
            "authority": unresolved_authority["authority"],
            "categorical_relation_construction_refused": unresolved_authority_refused,
            "refusal": unresolved_authority_error,
        },
        "forbidden_input_controls": forbidden_inputs,
        "forbidden_scalar_or_polarity_surface_present": False,
        "observed_categorical_path": {
            "support": "SUPPORTS -> supported",
            "refute": "REFUTES -> contradicted",
            "mixed": "SUPPORTS + REFUTES -> mixed-abstain",
            "irrelevant": "IRRELEVANT -> unresolved-abstain",
            "unresolved": "UNRESOLVED -> unresolved-abstain",
        },
        "research_disposition": "SUPPORTED_WITH_BOUNDS",
        "bounded_inference": (
            "Within the preregistered already-constructed strict-comparison fragment, a fully "
            "warranted RC8J atom can participate in a proposition conclusion through a derived "
            "categorical relation and scoreless composition without caller polarity or scalar strength."
        ),
        "not_established": [
            "semantic-text extraction",
            "generic semantic entailment",
            "truth of the fixture proposition in the world",
            "calibration or probabilistic decision strength",
            "production CAL architecture",
            "Contract C projection or successor semantics",
            "Decision Engine policy or operational authorization",
            "independent reproduction or clean-room recoverability",
        ],
        "production_promotion_authorized": False,
    }

    out = run_output / "RC8J-CATEGORICAL-WARRANTED-RELATION-RC1.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
