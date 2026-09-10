"""Decisive information-sufficiency evaluator for unresolved temporal provenance."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
from typing import Any

from research.cal_temporal_contract_c_decision_rc0 import bound_projection
from research.cal_temporal_contract_c_decision_rc0 import evaluate_bound_successor as bound_eval
from research.cal_temporal_contract_c_decision_rc0 import projection as c_projection
from research.cal_contract_c_unresolved_provenance_rc0.independent_consumer import (
    reconstruct_terminal_evidence,
)

SCHEMA = "cal-contract-c-unresolved-provenance-rc0-v1"
BOUND_FREEZE = "10ce0894a56f265434b24963bf0543765c453996"
CONTRACT_C_HEAD = "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(c_projection.canonical_bytes(value))


def _validate_contract_c(
    *, contract_c_root: Path, contract_c: dict[str, Any], index: dict[str, Any], out: Path, name: str
) -> dict[str, Any]:
    case_dir = out / name
    c_path = case_dir / "contract-c.json"
    b_path = case_dir / "contract-b-index.json"
    _write(c_path, contract_c)
    _write(b_path, index)
    proc = subprocess.run(
        [
            "python3",
            str(contract_c_root / "validators" / "contract_c.py"),
            str(c_path),
            "--contract-b-index",
            str(b_path),
        ],
        capture_output=True,
        text=True,
    )
    return {
        "pass": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _prop(*, claim_id: str, left_polarity: str) -> Any:
    return bound_eval._proposition(
        {
            "claim_id": claim_id,
            "left_event": {
                "subject": "alice",
                "predicate": "review",
                "object": "dossier",
                "polarity": left_polarity,
            },
            "relation": "BEFORE",
            "right_event": {
                "subject": "bob",
                "predicate": "archive",
                "object": "dossier",
                "polarity": "positive",
            },
        }
    )


def _spec(*, bundle_id: str, passages: list[dict[str, str]]) -> dict[str, Any]:
    return {"bundle_id": bundle_id, "passages": deepcopy(passages)}


def _project_one(
    *,
    context: Any,
    passage_id: str,
    proposition: Any,
    event_module: Any,
    rc8j_root: Path,
) -> tuple[Any, Any]:
    proof = bound_eval._proof(
        context=context,
        passage_id=passage_id,
        proposition=proposition,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )
    projected = bound_projection.project_bound_temporal_contract_c(
        proposition=proposition,
        proofs=(proof,),
        atom_trusted_keys=bound_eval.ATOM_KEYS,
        proposition_trusted_keys=bound_eval.PROP_KEYS,
    )
    return proof, projected


def execute(
    *, repo_root: Path, event_root: Path, rc8j_root: Path, contract_c_root: Path, out: Path
) -> dict[str, Any]:
    if _git(contract_c_root, "rev-parse", "HEAD") != CONTRACT_C_HEAD:
        raise RuntimeError("Contract C authority head mismatch")
    if _git(repo_root, "hash-object", "research/cal_temporal_contract_c_decision_rc0/bound_relation.py") != "94b44f3b0b2b3f077c17ca55eb944117ffa22b77":
        raise RuntimeError("bound relation blob drift")
    if _git(repo_root, "hash-object", "research/cal_temporal_contract_c_decision_rc0/bound_projection.py") != "77fed3e7a7273b13e6dfb89e0ffee7fce1503c6c":
        raise RuntimeError("bound projection blob drift")

    bound_eval.phase3._require_dependency(
        event_root, bound_eval.phase3.EVENT_HEAD,
        {bound_eval.phase3.EVENT_PATH: bound_eval.phase3.EVENT_BLOB},
    )
    bound_eval.phase3._require_dependency(
        rc8j_root, bound_eval.phase3.RC8J_HEAD, bound_eval.phase3.RC8J_BLOBS,
    )
    event_module = bound_eval.phase3._load_module(
        "cal_contract_c_info_sufficiency_event", event_root / bound_eval.phase3.EVENT_PATH
    )

    unresolved_prop = _prop(claim_id="TEMP-C-INFO-U-001", left_polarity="negative")
    unresolved_passages = [
        {
            "passage_id": "INFO-U-P1",
            "source_id": "source-info-u-1",
            "text": "Alice did not review dossier before Bob archived dossier.",
        },
        {
            "passage_id": "INFO-U-P2",
            "source_id": "source-info-u-2",
            "text": "Alice did not review dossier after Bob archived dossier.",
        },
    ]
    unresolved_context = bound_eval._context(
        spec=_spec(bundle_id="bundle-info-unresolved", passages=unresolved_passages),
        proposition=unresolved_prop,
    )
    proof_a, projected_a = _project_one(
        context=unresolved_context,
        passage_id="INFO-U-P1",
        proposition=unresolved_prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )
    proof_b, projected_b = _project_one(
        context=unresolved_context,
        passage_id="INFO-U-P2",
        proposition=unresolved_prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )

    for label, proof, projected in (
        ("unresolved-a", proof_a, projected_a),
        ("unresolved-b", proof_b, projected_b),
    ):
        if proof.relation.relation != "UNRESOLVED":
            raise AssertionError(f"{label}: expected UNRESOLVED")
        if projected.projection_status != "VALID_WITH_PROVENANCE_COMPRESSION":
            raise AssertionError(f"{label}: expected provenance compression")
        c_prop = projected.contract_c["propositions"][0]
        if c_prop["execution"] != {"state": "completed", "completion": "not_checkable"}:
            raise AssertionError(f"{label}: expected not_checkable")
        if c_prop["conclusion"]["terminal_branch"] != "unresolved_categorical_relation":
            raise AssertionError(f"{label}: wrong terminal branch")
        if c_prop["contributions"]:
            raise AssertionError(f"{label}: unresolved relation was falsely polarized")

    validation_a = _validate_contract_c(
        contract_c_root=contract_c_root,
        contract_c=projected_a.contract_c,
        index=projected_a.contract_b_index,
        out=out,
        name="unresolved-a",
    )
    validation_b = _validate_contract_c(
        contract_c_root=contract_c_root,
        contract_c=projected_b.contract_c,
        index=projected_b.contract_b_index,
        out=out,
        name="unresolved-b",
    )

    consumer_a = reconstruct_terminal_evidence(
        projected_a.contract_c, projected_a.contract_b_index, unresolved_prop.claim_id
    )
    consumer_b = reconstruct_terminal_evidence(
        projected_b.contract_c, projected_b.contract_b_index, unresolved_prop.claim_id
    )

    # Positive control: Contract C contribution basis must recover exact support evidence
    # even when another admitted passage exists in the same bound evidence world.
    support_prop = _prop(claim_id="TEMP-C-INFO-S-001", left_polarity="positive")
    support_passages = [
        {
            "passage_id": "INFO-S-P1",
            "source_id": "source-info-s-1",
            "text": "Alice reviewed dossier before Bob archived dossier.",
        },
        {
            "passage_id": "INFO-S-P2",
            "source_id": "source-info-s-2",
            "text": "Carol reviewed another dossier before Dan archived another dossier.",
        },
    ]
    support_context = bound_eval._context(
        spec=_spec(bundle_id="bundle-info-support", passages=support_passages),
        proposition=support_prop,
    )
    support_proof, support_projected = _project_one(
        context=support_context,
        passage_id="INFO-S-P1",
        proposition=support_prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )
    if support_proof.relation.relation != "SUPPORTS":
        raise AssertionError("support control did not derive SUPPORTS")
    support_validation = _validate_contract_c(
        contract_c_root=contract_c_root,
        contract_c=support_projected.contract_c,
        index=support_projected.contract_b_index,
        out=out,
        name="support-control",
    )
    support_consumer = reconstruct_terminal_evidence(
        support_projected.contract_c,
        support_projected.contract_b_index,
        support_prop.claim_id,
    )

    support_recovered = (
        support_consumer["unique_causal_evidence_ref_reconstructable"] is True
        and [row["passage_id"] for row in support_consumer["causal_evidence_refs"]] == ["INFO-S-P1"]
    )
    unresolved_a_recovered = (
        consumer_a["unique_causal_evidence_ref_reconstructable"] is True
        and [row["passage_id"] for row in consumer_a["causal_evidence_refs"]] == ["INFO-U-P1"]
    )
    unresolved_b_recovered = (
        consumer_b["unique_causal_evidence_ref_reconstructable"] is True
        and [row["passage_id"] for row in consumer_b["causal_evidence_refs"]] == ["INFO-U-P2"]
    )

    exact_same_bound_world = projected_a.contract_b_index == projected_b.contract_b_index
    same_terminal_public_semantics = (
        projected_a.contract_c["propositions"][0]["execution"]
        == projected_b.contract_c["propositions"][0]["execution"]
        and projected_a.contract_c["propositions"][0]["conclusion"]["reported_verdict"]
        == projected_b.contract_c["propositions"][0]["conclusion"]["reported_verdict"]
        and projected_a.contract_c["propositions"][0]["conclusion"]["terminal_branch"]
        == projected_b.contract_c["propositions"][0]["conclusion"]["terminal_branch"]
    )
    opaque_state_signals_differ = (
        projected_a.contract_c["propositions"][0]["conclusion"]["basis_members"]
        != projected_b.contract_c["propositions"][0]["conclusion"]["basis_members"]
    )
    # Different opaque IDs prove producer-visible state differs, but released Contract C
    # supplies no state->evidence reference relation for an independent consumer to follow.
    unresolved_underdetermined = (
        not unresolved_a_recovered
        and not unresolved_b_recovered
        and bool(consumer_a["opaque_causal_basis_members"])
        and bool(consumer_b["opaque_causal_basis_members"])
        and len(consumer_a["all_bound_evidence_refs"]) == 2
        and len(consumer_b["all_bound_evidence_refs"]) == 2
    )

    apparatus_valid = validation_a["pass"] and validation_b["pass"] and support_validation["pass"] and support_recovered
    gap_supported = apparatus_valid and exact_same_bound_world and same_terminal_public_semantics and unresolved_underdetermined
    disposition = (
        "SUPPORTED_BOUNDED_CONTRACT_C_UNRESOLVED_PROVENANCE_GAP"
        if gap_supported
        else "FALSIFIED_OR_INCONCLUSIVE_CONTRACT_C_UNRESOLVED_PROVENANCE_GAP"
    )

    result = {
        "schema": SCHEMA,
        "research_disposition": disposition,
        "pins": {
            "bound_freeze": BOUND_FREEZE,
            "contract_c_authority": CONTRACT_C_HEAD,
        },
        "validations": {
            "unresolved_a": validation_a,
            "unresolved_b": validation_b,
            "support_control": support_validation,
        },
        "ground_truth": {
            "unresolved_a_causal_passage_id": "INFO-U-P1",
            "unresolved_b_causal_passage_id": "INFO-U-P2",
            "support_control_causal_passage_id": "INFO-S-P1",
        },
        "independent_consumer": {
            "unresolved_a": consumer_a,
            "unresolved_b": consumer_b,
            "support_control": support_consumer,
        },
        "observations": {
            "support_control_recovered": support_recovered,
            "unresolved_a_recovered": unresolved_a_recovered,
            "unresolved_b_recovered": unresolved_b_recovered,
            "unresolved_causal_evidence_underdetermined": unresolved_underdetermined,
            "same_exact_contract_b_index_between_unresolved_executions": exact_same_bound_world,
            "same_terminal_public_semantics_between_unresolved_executions": same_terminal_public_semantics,
            "opaque_state_basis_ids_differ": opaque_state_signals_differ,
            "contract_c_bytes_differ_between_unresolved_executions": (
                c_projection.canonical_bytes(projected_a.contract_c)
                != c_projection.canonical_bytes(projected_b.contract_c)
            ),
            "unresolved_a_omitted_relation_ids": list(projected_a.omitted_relation_ids),
            "unresolved_b_omitted_relation_ids": list(projected_b.omitted_relation_ids),
        },
        "interpretation": {
            "contract_c_schema_change_selected": False,
            "contract_c_validator_defect_established": False,
            "fresh_semantic_reaudit_required_for_reconstruction": False,
            "producer_private_state_required_to_map_opaque_basis_to_evidence": gap_supported,
            "production_promotion_authorized": False,
            "contract_e_authorization_evaluated": False,
        },
    }
    out.mkdir(parents=True, exist_ok=True)
    _write(out / "EVALUATION.json", result)
    print(json.dumps({"research_disposition": disposition, **result["observations"]}, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--event-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--contract-c-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    execute(
        repo_root=args.repo_root.resolve(),
        event_root=args.event_root.resolve(),
        rc8j_root=args.rc8j_root.resolve(),
        contract_c_root=args.contract_c_root.resolve(),
        out=args.out.resolve(),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
