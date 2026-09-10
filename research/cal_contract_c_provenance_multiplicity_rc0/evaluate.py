"""Pressure-test frozen repair candidates for evidence-level causal multiplicity."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from research.cal_contract_c_provenance_multiplicity_rc0.multiplicity_consumer import (
    inspect_candidate,
)
from research.cal_contract_c_provenance_repair_rc0 import candidates
from research.cal_contract_c_provenance_repair_rc0 import evaluate as repair_eval
from research.cal_temporal_contract_c_decision_rc0 import evaluate_bound_successor as bound_eval
from research.cal_temporal_contract_c_decision_rc0 import projection as c_projection

SCHEMA = "cal-contract-c-provenance-multiplicity-rc0-v1"
FROZEN_REPAIR_HEAD = "bd1e0a0b171eed8a74445052202f938e3b734f74"
FROZEN_CANDIDATES_BLOB = "a7934b3c242dcf1c33a28121b3b141c9c6adc203"


def _git(root: Path, *args: str) -> str:
    import subprocess
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _sha(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def execute(*, repo_root: Path, event_root: Path, rc8j_root: Path, out: Path) -> dict:
    if _git(repo_root, "hash-object", "research/cal_contract_c_provenance_repair_rc0/candidates.py") != FROZEN_CANDIDATES_BLOB:
        raise RuntimeError("frozen repair candidates drifted")
    bound_eval.phase3._require_dependency(
        event_root, bound_eval.phase3.EVENT_HEAD,
        {bound_eval.phase3.EVENT_PATH: bound_eval.phase3.EVENT_BLOB},
    )
    bound_eval.phase3._require_dependency(
        rc8j_root, bound_eval.phase3.RC8J_HEAD, bound_eval.phase3.RC8J_BLOBS,
    )
    event_module = bound_eval.phase3._load_module(
        "cal_contract_c_multiplicity_event", event_root / bound_eval.phase3.EVENT_PATH
    )

    prop = repair_eval._base_prop("TEMP-C-MULTIPLICITY-001")
    passages = [
        {"passage_id": "MULT-U1", "source_id": "multi-u1", "text": "Alice did not review dossier before Bob archived dossier."},
        {"passage_id": "MULT-U2", "source_id": "multi-u2", "text": "Alice did not review dossier after Bob archived dossier."},
    ]
    _, p1, proj1 = repair_eval._make_context_and_proofs(
        proposition=prop, bundle_id="bundle-multiplicity", passages=passages,
        proof_passage_ids=["MULT-U1"], event_module=event_module, rc8j_root=rc8j_root,
    )
    _, p2, proj2 = repair_eval._make_context_and_proofs(
        proposition=prop, bundle_id="bundle-multiplicity", passages=passages,
        proof_passage_ids=["MULT-U2"], event_module=event_module, rc8j_root=rc8j_root,
    )
    _, both, projected = repair_eval._make_context_and_proofs(
        proposition=prop, bundle_id="bundle-multiplicity", passages=passages,
        proof_passage_ids=["MULT-U1", "MULT-U2"], event_module=event_module, rc8j_root=rc8j_root,
    )

    single_1 = proj1.composition.conclusion
    single_2 = proj2.composition.conclusion
    combined = projected.composition.conclusion
    if single_1.reason_code != "unresolved_categorical_relation" or single_2.reason_code != "unresolved_categorical_relation":
        raise AssertionError("single unresolved sufficiency controls failed")
    if combined.reason_code != "unresolved_categorical_relation":
        raise AssertionError("combined unresolved control failed")
    if len(combined.basis_relation_ids) != 2:
        raise AssertionError("combined upstream basis did not preserve both unresolved relations")
    if len(single_1.basis_relation_ids) != 1 or len(single_2.basis_relation_ids) != 1:
        raise AssertionError("single upstream basis malformed")
    independent_sufficiency_observed = (
        single_1.disposition == combined.disposition
        and single_2.disposition == combined.disposition
        and single_1.verdict == combined.verdict
        and single_2.verdict == combined.verdict
        and single_1.reason_code == combined.reason_code
        and single_2.reason_code == combined.reason_code
    )
    if not independent_sufficiency_observed:
        raise AssertionError("upstream evidence does not establish independent unresolved sufficiency")

    causal_refs = repair_eval._refs_for_proofs(both)
    payloads = repair_eval._candidate_payloads(projected.contract_c, causal_refs)
    expected_ids = ["MULT-U1", "MULT-U2"]
    results = {}
    survivors = []
    for name, payload in payloads.items():
        observed = inspect_candidate(
            name,
            payload,
            projected.contract_b_index,
            _sha(c_projection.canonical_bytes(payload["contract_c"])),
        )
        provenance_pass = observed["causal_passage_ids"] == expected_ids
        multiplicity_pass = observed["evidence_level_causal_form"] == "independent_sufficient_alternatives"
        stronger_pass = provenance_pass and multiplicity_pass
        if stronger_pass:
            survivors.append(name)
        results[name] = {
            "consumer_observation": observed,
            "exact_provenance_preserved": provenance_pass,
            "independent_sufficiency_preserved": multiplicity_pass,
            "stronger_causal_attribution_obligation_pass": stronger_pass,
        }

    disposition = (
        "UNIQUE_MULTIPLICITY_PRESERVING_REPAIR_CANDIDATE"
        if len(survivors) == 1
        else "NO_UNIQUE_MULTIPLICITY_PRESERVING_REPAIR_CANDIDATE"
        if len(survivors) > 1
        else "ALL_FROZEN_REPAIR_CANDIDATES_FAIL_MULTIPLICITY"
    )
    result = {
        "schema": SCHEMA,
        "research_disposition": disposition,
        "frozen_repair_head": FROZEN_REPAIR_HEAD,
        "frozen_candidates_blob": FROZEN_CANDIDATES_BLOB,
        "upstream_observation": {
            "u1_alone_terminal_reason": single_1.reason_code,
            "u2_alone_terminal_reason": single_2.reason_code,
            "u1_plus_u2_terminal_reason": combined.reason_code,
            "u1_plus_u2_basis_relation_count": len(combined.basis_relation_ids),
            "independent_sufficiency_observed_by_ablation": independent_sufficiency_observed,
        },
        "candidates": results,
        "surviving_candidates": survivors,
        "interpretation": {
            "unique_candidate_is_contract_change_authorization": False,
            "candidate_a_production_schema_validated": False,
            "cross_repository_consumer_conformance_established": False,
            "production_promotion_authorized": False,
        },
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "EVALUATION.json").write_bytes(candidates.canonical_bytes(result))
    print(json.dumps({
        "research_disposition": disposition,
        "surviving_candidates": survivors,
        "independent_sufficiency_observed_by_ablation": independent_sufficiency_observed,
    }, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--event-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    execute(
        repo_root=args.repo_root.resolve(), event_root=args.event_root.resolve(),
        rc8j_root=args.rc8j_root.resolve(), out=args.out.resolve()
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
