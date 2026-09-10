"""Post-freeze falsifier for the first temporal Contract C projector.

The test asks whether a genuine Phase-3 warranted relation produced under bundle A
can be projected under a different Contract-B bundle B when B repeats the same
claim/evidence references. A successful projection is a falsification of the
first projector's cross-boundary provenance binding, not of Contract C itself.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from research.cal_event_order_relation_rc0 import candidate as temporal
from research.cal_event_order_relation_rc0 import evaluate as phase3
from research.cal_temporal_contract_c_decision_rc0 import projection

PROJECTOR_FREEZE = "75242634cc6c638f961035d2f2dc3f8570308090"
PROJECTOR_BLOB = "57d389f8b39d458388a6aed7c99c620ea165354a"


def _validate(contract_c: dict, index: dict, authority_root: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    c_path = out / "contract-c.json"
    i_path = out / "contract-b-index.json"
    c_path.write_bytes(projection.canonical_bytes(contract_c))
    i_path.write_bytes(projection.canonical_bytes(index))
    proc = subprocess.run(
        [sys.executable, str(authority_root / "validators" / "contract_c.py"), str(c_path), "--contract-b-index", str(i_path)],
        capture_output=True,
        text=True,
    )
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def execute(*, repo_root: Path, event_root: Path, rc8j_root: Path, contract_c_root: Path, out: Path) -> dict:
    if phase3._git(repo_root, "hash-object", "research/cal_temporal_contract_c_decision_rc0/projection.py") != PROJECTOR_BLOB:
        raise RuntimeError("first projector blob drifted")
    phase3._require_dependency(event_root, phase3.EVENT_HEAD, {phase3.EVENT_PATH: phase3.EVENT_BLOB})
    phase3._require_dependency(rc8j_root, phase3.RC8J_HEAD, phase3.RC8J_BLOBS)
    event_module = phase3._load_module("cal_phase4_cross_bundle_event", event_root / phase3.EVENT_PATH)

    prop_row = {
        "left_event": {"subject": "alice", "predicate": "review", "object": "dossier", "polarity": "positive"},
        "relation": "BEFORE",
        "right_event": {"subject": "bob", "predicate": "archive", "object": "dossier", "polarity": "positive"},
    }
    proposition = phase3._proposition(claim_id="TEMP-CROSS-BUNDLE-001", row=prop_row)
    context, case, warrant = phase3._prepare_case(
        event_module=event_module,
        rc8j_root=rc8j_root,
        case_id="CROSS-BUNDLE-A",
        source="Alice reviewed dossier before Bob archived dossier.",
        proposition=proposition,
    )
    relation = phase3._derive(case=case, warrant=warrant, proposition=proposition)
    conclusion = temporal.compose_temporal_relations(proposition=proposition, relations=(relation,))
    assert relation.relation == "SUPPORTS" and conclusion.verdict == "supported"

    evidence_index = {
        passage.passage_id: {
            "source_id": passage.source_id,
            "passage_sha256": passage.passage_sha256,
        }
        for passage in context.admitted_passages
    }
    correct_binding = {
        "contract_version": context.contract_b_version,
        "bundle_id": context.bundle_id,
        "bundle_hash": context.bundle_hash,
    }
    correct = projection.project_temporal_contract_c(
        proposition=proposition,
        relations=(relation,),
        conclusion=conclusion,
        contract_b_binding=correct_binding,
        evidence_index=evidence_index,
    )

    forged_binding = {
        "contract_version": context.contract_b_version,
        "bundle_id": "bundle-forged-cross-bundle-b",
        "bundle_hash": projection._stable_id("sha256", {"forged": "bundle-b"}),
    }
    # _stable_id gives sha256:<hex>, which is syntactically a Contract-B bundle hash.
    forged = projection.project_temporal_contract_c(
        proposition=proposition,
        relations=(relation,),
        conclusion=conclusion,
        contract_b_binding=forged_binding,
        evidence_index=evidence_index,
    )
    validation = _validate(forged.contract_c, forged.contract_b_index, contract_c_root, out)

    attack_succeeded = (
        forged.contract_c["input"]["contract_b"]["bundle_id"] == forged_binding["bundle_id"]
        and case["raw_bundle_id"] == correct_binding["bundle_id"]
        and forged_binding["bundle_id"] != case["raw_bundle_id"]
        and validation["returncode"] == 0
    )
    result = {
        "schema": "cal-temporal-contract-c-cross-bundle-falsifier-v1",
        "projector_freeze": PROJECTOR_FREEZE,
        "projector_blob": PROJECTOR_BLOB,
        "source_authority_bundle_id": case["raw_bundle_id"],
        "forged_contract_c_bundle_id": forged_binding["bundle_id"],
        "relation_id": relation.relation_id,
        "correct_projection_status": correct.projection_status,
        "forged_contract_c_validation": validation,
        "attack_succeeded": attack_succeeded,
        "research_disposition": (
            "FALSIFIED_CROSS_BUNDLE_PROVENANCE_BINDING"
            if attack_succeeded
            else "CROSS_BUNDLE_ATTACK_REFUSED"
        ),
        "interpretation": {
            "contract_c_defect_established": False,
            "phase3_relation_semantics_falsified": False,
            "first_projector_cross_bundle_binding_falsified": attack_succeeded,
            "production_promotion_authorized": False,
        },
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "CROSS-BUNDLE-FALSIFIER.json").write_bytes(projection.canonical_bytes(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--event-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--contract-c-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = execute(
        repo_root=args.repo_root.resolve(),
        event_root=args.event_root.resolve(),
        rc8j_root=args.rc8j_root.resolve(),
        contract_c_root=args.contract_c_root.resolve(),
        out=args.out.resolve(),
    )
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
