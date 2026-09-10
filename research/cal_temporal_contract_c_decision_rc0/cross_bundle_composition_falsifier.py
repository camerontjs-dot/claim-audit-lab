"""Post-evidence falsifier for Phase-3 temporal multi-relation composition.

Tests whether two individually genuine warranted temporal relations derived under
different Contract-B bundle identities can be composed merely because they share
an exact proposition identity.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.cal_event_order_relation_rc0 import candidate
from research.cal_event_order_relation_rc0 import evaluate as phase3
from research.cal_temporal_contract_c_decision_rc0.projection import canonical_bytes

PHASE3_FREEZE = "94ea0c7531aeb852520f34bd56393b63a4b5ac75"
PHASE3_RELATION_BLOB = "70f9eff65330c4182b5ac3bd1a11d13059326ed6"
PHASE3_CANDIDATE_BLOB = "7e964d85eb80298b9b0d5b84eff32e14bed4b013"


def execute(*, repo_root: Path, event_root: Path, rc8j_root: Path, out: Path) -> dict:
    assert phase3._git(repo_root, "hash-object", "research/cal_event_order_relation_rc0/relation.py") == PHASE3_RELATION_BLOB
    assert phase3._git(repo_root, "hash-object", "research/cal_event_order_relation_rc0/candidate.py") == PHASE3_CANDIDATE_BLOB
    phase3._require_dependency(event_root, phase3.EVENT_HEAD, {phase3.EVENT_PATH: phase3.EVENT_BLOB})
    phase3._require_dependency(rc8j_root, phase3.RC8J_HEAD, phase3.RC8J_BLOBS)
    event_module = phase3._load_module("cal_cross_bundle_composition_event", event_root / phase3.EVENT_PATH)

    prop_row = {
        "left_event": {"subject": "alice", "predicate": "review", "object": "dossier", "polarity": "positive"},
        "relation": "BEFORE",
        "right_event": {"subject": "bob", "predicate": "archive", "object": "dossier", "polarity": "positive"},
    }
    proposition = phase3._proposition(claim_id="TEMP-CROSS-WORLD-COMPOSE-001", row=prop_row)

    context_a, case_a, warrant_a = phase3._prepare_case(
        event_module=event_module,
        rc8j_root=rc8j_root,
        case_id="WORLD-A-SUPPORT",
        source="Alice reviewed dossier before Bob archived dossier.",
        proposition=proposition,
    )
    support = phase3._derive(case=case_a, warrant=warrant_a, proposition=proposition)
    assert support.relation == "SUPPORTS"

    context_b, case_b, warrant_b = phase3._prepare_case(
        event_module=event_module,
        rc8j_root=rc8j_root,
        case_id="WORLD-B-REFUTE",
        source="Alice reviewed dossier after Bob archived dossier.",
        proposition=proposition,
    )
    refute = phase3._derive(case=case_b, warrant=warrant_b, proposition=proposition)
    assert refute.relation == "REFUTES"
    assert context_a.bundle_id != context_b.bundle_id
    assert context_a.bundle_hash != context_b.bundle_hash

    conclusion = candidate.compose_temporal_relations(
        proposition=proposition,
        relations=(support, refute),
    )
    accepted_cross_world = (
        conclusion.disposition == "abstained"
        and conclusion.verdict is None
        and conclusion.reason_code == "mixed_categorical_relations"
    )
    result = {
        "schema": "cal-event-order-cross-bundle-composition-falsifier-v1",
        "phase3_candidate_freeze": PHASE3_FREEZE,
        "bundle_a": {"id": context_a.bundle_id, "hash": context_a.bundle_hash},
        "bundle_b": {"id": context_b.bundle_id, "hash": context_b.bundle_hash},
        "support_relation_id": support.relation_id,
        "refute_relation_id": refute.relation_id,
        "observed_conclusion": {
            "disposition": conclusion.disposition,
            "verdict": conclusion.verdict,
            "reason_code": conclusion.reason_code,
            "basis_relation_ids": list(conclusion.basis_relation_ids),
        },
        "cross_bundle_composition_accepted": accepted_cross_world,
        "research_disposition": (
            "FALSIFIED_COMMON_EVIDENCE_WORLD_BINDING"
            if accepted_cross_world
            else "CROSS_BUNDLE_COMPOSITION_REFUSED"
        ),
        "interpretation": {
            "single_relation_semantics_falsified": False,
            "phase3_multi_relation_common_world_binding_falsified": accepted_cross_world,
            "production_promotion_authorized": False,
        },
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "CROSS-BUNDLE-COMPOSITION.json").write_bytes(canonical_bytes(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--event-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = execute(
        repo_root=args.repo_root.resolve(),
        event_root=args.event_root.resolve(),
        rc8j_root=args.rc8j_root.resolve(),
        out=args.out.resolve(),
    )
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
