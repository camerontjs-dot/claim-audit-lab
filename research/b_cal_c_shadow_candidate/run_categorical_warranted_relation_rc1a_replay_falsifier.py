"""Adversarial authority-receipt replay test for frozen categorical RC1."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any

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
from run_categorical_warranted_relation_rc1 import _authority, _variant


RC1_HEAD = "598968205a5371323989f972442fb9820ba19b35"
RC8J_FREEZE_COMMIT = "8e75c6782bb95c3763d06230b9c5df2b6af44054"
RC8J_CANDIDATE_BLOB = "f55156e43e0c1b4a7868bc8339585b8892edda38"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-output", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    args = parser.parse_args()

    run_output = args.run_output.resolve()
    evaluator = _load_rc8j(args.rc8j_root.resolve())
    coords = _validated_b_coordinates(run_output)
    base = _typed_seam_control(coords)

    target = ComparisonProposition(
        claim_id=coords["claim_id"],
        family="comparison",
        lhs_entity="fixture:left",
        rhs_entity="fixture:right",
        comparison_direction="greater_than",
    )

    warranted_case = _variant(
        base,
        case_id="R1A-BASE-WARRANTED",
        atom_id="atom:categorical:replay-subject:v1",
        lhs="fixture:left",
        rhs="fixture:right",
        direction="greater_than",
    )
    warranted_authority = _authority(warranted_case, evaluator)
    if warranted_authority["authority"] != {
        "status": "WARRANTED",
        "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
    }:
        raise AssertionError(f"base replay subject is not warranted: {warranted_authority}")

    mutated_case = deepcopy(warranted_case)
    mutated_case["case_id"] = "R1A-MUTATED-NONWARRANTED"
    mutated_case["proposal"]["fields"]["comparison_direction"] = "less_than"
    # Deliberately preserve the original field-warrant receipt value. If RC8J is
    # actually run on this mutated atom, the semantic field is no longer warranted.

    actual_mutated_authority = _authority(mutated_case, evaluator)
    mutated_is_nonwarranted = actual_mutated_authority["authority"]["status"] != "WARRANTED"

    replay_refused = False
    replay_error: str | None = None
    replay_relation: dict[str, Any] | None = None
    replay_conclusion: dict[str, Any] | None = None
    replay_decided = False

    try:
        relation = derive_categorical_relation(
            case=mutated_case,
            authority_result=warranted_authority,
            proposition=target,
        )
        conclusion = compose_categorical_relations(target, (relation,))
        replay_relation = relation.model_dump(mode="json")
        replay_conclusion = conclusion.model_dump(mode="json")
        replay_decided = conclusion.disposition == "decided"
    except (ValueError, TypeError) as exc:
        replay_refused = True
        replay_error = str(exc)

    if not mutated_is_nonwarranted:
        disposition = "INCONCLUSIVE_MUTATION_REMAINED_WARRANTED"
    elif replay_decided:
        disposition = "FALSIFIED_AUTHORITY_RECEIPT_REPLAY"
    elif replay_refused:
        disposition = "SURVIVED_AUTHORITY_RECEIPT_REPLAY_CONTROL"
    else:
        disposition = "INCONCLUSIVE_REPLAY_ACCEPTED_BUT_NONDECIDING"

    result = {
        "experiment": "RC8J categorical warranted-relation RC1A authority-replay falsifier",
        "frozen_parent_rc1_head": RC1_HEAD,
        "rc8j": {
            "freeze_commit": RC8J_FREEZE_COMMIT,
            "candidate_blob": RC8J_CANDIDATE_BLOB,
        },
        "base_case": {
            "case_id": warranted_case["case_id"],
            "proposal": warranted_case["proposal"],
            "authority": warranted_authority["authority"],
        },
        "mutated_case": {
            "case_id": mutated_case["case_id"],
            "proposal": mutated_case["proposal"],
            "preserved_field_warrant_direction": mutated_case["field_warrants"]["comparison_direction"]["value"],
            "actual_rc8j_authority": actual_mutated_authority["authority"],
            "is_nonwarranted": mutated_is_nonwarranted,
        },
        "replayed_authority": warranted_authority["authority"],
        "replay_refused": replay_refused,
        "replay_error": replay_error,
        "replay_relation": replay_relation,
        "replay_conclusion": replay_conclusion,
        "replay_produced_deciding_conclusion": replay_decided,
        "research_disposition": disposition,
        "production_promotion_authorized": False,
        "not_established": [
            "a corrected authority-binding design",
            "production CAL architecture",
            "generic semantic entailment",
            "semantic-text extraction",
            "Contract C projection",
        ],
    }

    out = run_output / "RC8J-CATEGORICAL-WARRANTED-RELATION-RC1A-REPLAY.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
