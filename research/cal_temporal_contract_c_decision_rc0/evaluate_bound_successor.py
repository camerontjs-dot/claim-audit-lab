"""Decisive evaluator for the evidence-world-bound temporal successor."""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable

from research.cal_measurement_envelope_rc0.envelope import AdmittedPassage, AuditContext, measure_passage
from research.cal_event_order_authority_rc0 import candidate as event_authority
from research.cal_event_order_relation_rc0 import candidate as temporal
from research.cal_event_order_relation_rc0 import evaluate as phase3
from research.cal_temporal_contract_c_decision_rc0 import bound_projection
from research.cal_temporal_contract_c_decision_rc0 import bound_relation
from research.cal_temporal_contract_c_decision_rc0 import projection as failed_projection

SCHEMA = "cal-bound-temporal-world-rc0-evaluation-v1"
CANDIDATE_FREEZE = "10ce0894a56f265434b24963bf0543765c453996"
CANDIDATE_BLOBS = {
    "research/cal_temporal_contract_c_decision_rc0/bound_relation.py": "94b44f3b0b2b3f077c17ca55eb944117ffa22b77",
    "research/cal_temporal_contract_c_decision_rc0/bound_projection.py": "77fed3e7a7273b13e6dfb89e0ffee7fce1503c6c",
    "research/cal_temporal_contract_c_decision_rc0/projection.py": "57d389f8b39d458388a6aed7c99c620ea165354a",
    "research/cal_event_order_relation_rc0/relation.py": "70f9eff65330c4182b5ac3bd1a11d13059326ed6",
    "research/cal_event_order_relation_rc0/candidate.py": "7e964d85eb80298b9b0d5b84eff32e14bed4b013",
    "research/cal_event_order_authority_rc0/event_authority.py": "88df954235069e98582e731f48e46e5b257da93f",
    "research/cal_event_order_authority_rc0/candidate.py": "36a8d1fbd9e52ec743757f750f744ad4553b5698",
    "research/cal_measurement_envelope_rc0/envelope.py": "f8ce6362f6ccc165cdad29f314721bb26a21f871",
}
CONTRACT_C_HEAD = "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"
CONTRACT_C_VALIDATOR_BLOB = "9c75ccfbf2223578a8d1a7bf0c39673b394fbea4"
ATOM_KEYS = {phase3.ATOM_KEY_ID: phase3.ATOM_KEY}
PROP_KEYS = {phase3.PROP_KEY_ID: phase3.PROP_KEY}


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _require_candidate(root: Path) -> None:
    if subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", CANDIDATE_FREEZE, "HEAD"]
    ).returncode != 0:
        raise RuntimeError("candidate freeze is not an ancestor")
    for path, expected in CANDIDATE_BLOBS.items():
        actual = _git(root, "hash-object", path)
        if actual != expected:
            raise RuntimeError(f"frozen candidate blob drift {path}: {actual} != {expected}")


def _sha(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _event(row: dict[str, Any]) -> temporal.EventSemantics:
    return temporal.EventSemantics(
        subject=str(row["subject"]),
        predicate=str(row["predicate"]),
        object=str(row["object"]),
        polarity=str(row["polarity"]),
    )


def _claim_text(row: dict[str, Any]) -> str:
    return "event-order-proposition:" + json.dumps(row, sort_keys=True, separators=(",", ":"))


def _proposition(row: dict[str, Any]) -> temporal.TemporalProposition:
    return temporal.TemporalProposition(
        claim_id=str(row["claim_id"]),
        claim_text=_claim_text(row),
        left_event=_event(row["left_event"]),
        relation=str(row["relation"]),
        right_event=_event(row["right_event"]),
    )


def _context(*, spec: dict[str, Any], proposition: temporal.TemporalProposition) -> AuditContext:
    passages = tuple(
        AdmittedPassage(
            source_id=str(item["source_id"]),
            passage_id=str(item["passage_id"]),
            passage_sha256=_sha(str(item["text"])),
            passage_text=str(item["text"]),
        )
        for item in spec["passages"]
    )
    bundle_material = json.dumps(
        {
            "bundle_id": spec["bundle_id"],
            "claim_id": proposition.claim_id,
            "passages": [p.payload() for p in passages],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return AuditContext.create(
        audit_id="BOUND-" + str(spec["bundle_id"]),
        original_claim_id=proposition.claim_id,
        original_claim_text=proposition.claim_text,
        proposition_id=proposition.claim_id,
        proposition_payload={
            "family": "event_ordering",
            "claim_text": proposition.claim_text,
            "research_scope": "bound_temporal_world_rc0",
        },
        decomposition_path=(proposition.claim_id,),
        contract_b_version="1.2.0",
        bundle_id=str(spec["bundle_id"]),
        bundle_hash=_sha(bundle_material),
        admitted_passages=passages,
    )


def _proof(
    *,
    context: AuditContext,
    passage_id: str,
    proposition: temporal.TemporalProposition,
    event_module: Any,
    rc8j_root: Path,
) -> bound_relation.BoundTemporalProof:
    receipt = measure_passage(
        context=context,
        passage_id=passage_id,
        instrument_id=event_authority.EVENT_INSTRUMENT_ID,
        instrument_version=str(event_module.VERSION),
        semantic_family=event_authority.EVENT_FAMILY,
        measure_fn=event_module.measure,
    )
    if receipt.measurement_status != "CLAIMED":
        raise RuntimeError(f"{passage_id}: RC7F-C did not return CLAIMED")
    atom = event_authority.complete_event_order_atom(
        context=context,
        receipt=receipt,
        passage_id=passage_id,
    )
    case = event_authority.build_rc8j_case(atom=atom)
    warrant = temporal.issue_event_atom_warrant(
        case=case,
        authority_evaluator=lambda value: phase3._rc8j(rc8j_root, value),
        key=phase3.ATOM_KEY,
        key_id=phase3.ATOM_KEY_ID,
    )
    prop_binding = temporal.issue_proposition_binding(
        proposition=proposition,
        key=phase3.PROP_KEY,
        key_id=phase3.PROP_KEY_ID,
    )
    relation = temporal.derive_temporal_relation(
        case=case,
        proposition=proposition,
        atom_warrant=warrant,
        atom_trusted_keys=ATOM_KEYS,
        proposition_binding=prop_binding,
        proposition_trusted_keys=PROP_KEYS,
    )
    return bound_relation.BoundTemporalProof(
        context=context,
        measurement_receipt=receipt,
        passage_id=passage_id,
        proposition=proposition,
        atom_warrant=warrant,
        proposition_binding=prop_binding,
        relation=relation,
    )


def _validate_contract_c(
    *, result: bound_projection.BoundProjectionResult, authority_root: Path, out_dir: Path, name: str
) -> dict[str, Any]:
    case_dir = out_dir / name
    case_dir.mkdir(parents=True, exist_ok=True)
    contract_c_path = case_dir / "contract-c.json"
    index_path = case_dir / "contract-b-index.json"
    contract_c_path.write_bytes(failed_projection.canonical_bytes(result.contract_c))
    index_path.write_bytes(failed_projection.canonical_bytes(result.contract_b_index))
    proc = subprocess.run(
        [
            sys.executable,
            str(authority_root / "validators" / "contract_c.py"),
            str(contract_c_path),
            "--contract-b-index",
            str(index_path),
        ],
        capture_output=True,
        text=True,
    )
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "contract_c_path": str(contract_c_path),
        "index_path": str(index_path),
    }


def _expect_bound_refusal(code: str, fn: Callable[[], Any]) -> dict[str, Any]:
    try:
        fn()
    except bound_relation.BoundRelationRefusal as exc:
        if exc.code != code:
            raise AssertionError(f"expected {code}, got {exc.code}: {exc.detail}") from exc
        return {"pass": True, "code": exc.code, "detail": exc.detail}
    raise AssertionError(f"expected refusal {code}")


def _mutated_context(
    context: AuditContext,
    *,
    bundle_id: str | None = None,
    bundle_hash: str | None = None,
    claim_text: str | None = None,
    passage_text_overrides: dict[str, str] | None = None,
) -> AuditContext:
    overrides = passage_text_overrides or {}
    passages = []
    for item in context.admitted_passages:
        text = overrides.get(item.passage_id, item.passage_text)
        passages.append(
            AdmittedPassage(
                source_id=item.source_id,
                passage_id=item.passage_id,
                passage_sha256=_sha(text),
                passage_text=text,
            )
        )
    return AuditContext.create(
        audit_id=context.audit_id,
        original_claim_id=context.original_claim_id,
        original_claim_text=claim_text if claim_text is not None else context.original_claim_text,
        proposition_id=context.proposition_id,
        proposition_payload={
            **context.proposition_payload,
            "claim_text": claim_text if claim_text is not None else context.original_claim_text,
        },
        decomposition_path=context.decomposition_path,
        contract_b_version=context.contract_b_version,
        bundle_id=bundle_id if bundle_id is not None else context.bundle_id,
        bundle_hash=bundle_hash if bundle_hash is not None else context.bundle_hash,
        admitted_passages=passages,
    )


def execute(
    *, repo_root: Path, event_root: Path, rc8j_root: Path, contract_c_root: Path,
    cohort_path: Path, out_dir: Path
) -> dict[str, Any]:
    _require_candidate(repo_root)
    phase3._require_dependency(event_root, phase3.EVENT_HEAD, {phase3.EVENT_PATH: phase3.EVENT_BLOB})
    phase3._require_dependency(rc8j_root, phase3.RC8J_HEAD, phase3.RC8J_BLOBS)
    if _git(contract_c_root, "rev-parse", "HEAD") != CONTRACT_C_HEAD:
        raise RuntimeError("Contract C authority head mismatch")
    if _git(contract_c_root, "hash-object", "validators/contract_c.py") != CONTRACT_C_VALIDATOR_BLOB:
        raise RuntimeError("Contract C validator blob mismatch")
    event_module = phase3._load_module("cal_bound_successor_event", event_root / phase3.EVENT_PATH)
    cohort = json.loads(cohort_path.read_text(encoding="utf-8"))
    if cohort.get("candidate_freeze_before_cohort") != CANDIDATE_FREEZE:
        raise RuntimeError("cohort does not bind exact successor freeze")

    prop = _proposition(cohort["proposition"])
    support_context = _context(spec=cohort["single_support"], proposition=prop)
    support_proof = _proof(
        context=support_context,
        passage_id=cohort["single_support"]["passages"][0]["passage_id"],
        proposition=prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )
    refute_context = _context(spec=cohort["single_refute"], proposition=prop)
    refute_proof = _proof(
        context=refute_context,
        passage_id=cohort["single_refute"]["passages"][0]["passage_id"],
        proposition=prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )

    mixed_context = _context(spec=cohort["same_world_mixed"], proposition=prop)
    mixed_support = _proof(
        context=mixed_context,
        passage_id=cohort["same_world_mixed"]["passages"][0]["passage_id"],
        proposition=prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )
    mixed_refute = _proof(
        context=mixed_context,
        passage_id=cohort["same_world_mixed"]["passages"][1]["passage_id"],
        proposition=prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )

    unresolved_prop = _proposition(cohort["single_unresolved"]["proposition"])
    unresolved_context = _context(spec=cohort["single_unresolved"], proposition=unresolved_prop)
    unresolved_proof = _proof(
        context=unresolved_context,
        passage_id=cohort["single_unresolved"]["passages"][0]["passage_id"],
        proposition=unresolved_prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )

    positive: dict[str, Any] = {}
    support_projection = bound_projection.project_bound_temporal_contract_c(
        proposition=prop,
        proofs=(support_proof,),
        atom_trusted_keys=ATOM_KEYS,
        proposition_trusted_keys=PROP_KEYS,
    )
    support_validation = _validate_contract_c(
        result=support_projection, authority_root=contract_c_root, out_dir=out_dir, name="support"
    )
    positive["support"] = {
        "pass": (
            support_projection.composition.conclusion.verdict == "supported"
            and support_projection.projection_status == "LOSSLESS_TERMINAL_AND_DECIDING_PROVENANCE"
            and [c["channel"] for c in support_projection.contract_c["propositions"][0]["contributions"]] == ["support"]
            and support_validation["returncode"] == 0
        ),
        "context_sha256": support_context.context_sha256,
        "bundle_id": support_context.bundle_id,
        "projection_status": support_projection.projection_status,
        "validation": support_validation,
    }

    refute_projection = bound_projection.project_bound_temporal_contract_c(
        proposition=prop,
        proofs=(refute_proof,),
        atom_trusted_keys=ATOM_KEYS,
        proposition_trusted_keys=PROP_KEYS,
    )
    refute_validation = _validate_contract_c(
        result=refute_projection, authority_root=contract_c_root, out_dir=out_dir, name="refute"
    )
    positive["refute"] = {
        "pass": (
            refute_projection.composition.conclusion.verdict == "contradicted"
            and refute_projection.projection_status == "LOSSLESS_TERMINAL_AND_DECIDING_PROVENANCE"
            and [c["channel"] for c in refute_projection.contract_c["propositions"][0]["contributions"]] == ["counterevidence"]
            and refute_validation["returncode"] == 0
        ),
        "context_sha256": refute_context.context_sha256,
        "bundle_id": refute_context.bundle_id,
        "projection_status": refute_projection.projection_status,
        "validation": refute_validation,
    }

    mixed_projection = bound_projection.project_bound_temporal_contract_c(
        proposition=prop,
        proofs=(mixed_support, mixed_refute),
        atom_trusted_keys=ATOM_KEYS,
        proposition_trusted_keys=PROP_KEYS,
    )
    mixed_reverse = bound_projection.project_bound_temporal_contract_c(
        proposition=prop,
        proofs=(mixed_refute, mixed_support),
        atom_trusted_keys=ATOM_KEYS,
        proposition_trusted_keys=PROP_KEYS,
    )
    mixed_validation = _validate_contract_c(
        result=mixed_projection, authority_root=contract_c_root, out_dir=out_dir, name="mixed"
    )
    positive["same_world_mixed"] = {
        "pass": (
            mixed_projection.composition.conclusion.reason_code == "mixed_categorical_relations"
            and mixed_projection.composition.conclusion == mixed_reverse.composition.conclusion
            and mixed_projection.contract_c == mixed_reverse.contract_c
            and set(c["channel"] for c in mixed_projection.contract_c["propositions"][0]["contributions"])
            == {"support", "counterevidence"}
            and mixed_projection.projection_status == "LOSSLESS_TERMINAL_AND_DECIDING_PROVENANCE"
            and mixed_validation["returncode"] == 0
        ),
        "context_sha256": mixed_context.context_sha256,
        "bundle_id": mixed_context.bundle_id,
        "projection_status": mixed_projection.projection_status,
        "validation": mixed_validation,
    }

    unresolved_projection = bound_projection.project_bound_temporal_contract_c(
        proposition=unresolved_prop,
        proofs=(unresolved_proof,),
        atom_trusted_keys=ATOM_KEYS,
        proposition_trusted_keys=PROP_KEYS,
    )
    unresolved_validation = _validate_contract_c(
        result=unresolved_projection, authority_root=contract_c_root, out_dir=out_dir, name="unresolved"
    )
    positive["unresolved"] = {
        "pass": (
            unresolved_projection.composition.conclusion.reason_code == "unresolved_categorical_relation"
            and unresolved_projection.projection_status == "VALID_WITH_PROVENANCE_COMPRESSION"
            and unresolved_projection.omitted_relation_ids == (unresolved_proof.relation.relation_id,)
            and unresolved_projection.contract_c["propositions"][0]["contributions"] == []
            and unresolved_validation["returncode"] == 0
        ),
        "context_sha256": unresolved_context.context_sha256,
        "bundle_id": unresolved_context.bundle_id,
        "projection_status": unresolved_projection.projection_status,
        "omitted_relation_ids": list(unresolved_projection.omitted_relation_ids),
        "validation": unresolved_validation,
    }

    falsifiers: dict[str, Any] = {}
    falsifiers["cross_bundle_composition"] = _expect_bound_refusal(
        "COMMON_EVIDENCE_WORLD_MISMATCH",
        lambda: bound_relation.compose_bound_temporal_proofs(
            proposition=prop,
            proofs=(support_proof, refute_proof),
            atom_trusted_keys=ATOM_KEYS,
            proposition_trusted_keys=PROP_KEYS,
        ),
    )
    falsifiers["cross_bundle_projection"] = _expect_bound_refusal(
        "COMMON_EVIDENCE_WORLD_MISMATCH",
        lambda: bound_projection.project_bound_temporal_contract_c(
            proposition=prop,
            proofs=(support_proof, refute_proof),
            atom_trusted_keys=ATOM_KEYS,
            proposition_trusted_keys=PROP_KEYS,
        ),
    )

    changed_hash_context = _mutated_context(
        support_context,
        bundle_hash=_sha("changed-bundle-hash-with-same-bundle-id"),
    )
    stale_context_proof = replace(support_proof, context=changed_hash_context)
    falsifiers["stale_measurement_changed_bundle_hash"] = _expect_bound_refusal(
        "SOURCE_RECONSTRUCTION_FAILED",
        lambda: bound_relation.verify_bound_temporal_proof(
            proof=stale_context_proof,
            atom_trusted_keys=ATOM_KEYS,
            proposition_trusted_keys=PROP_KEYS,
        ),
    )

    changed_text = support_context.admitted_passages[0].passage_text.replace("before", "after")
    changed_text_context = _mutated_context(
        support_context,
        passage_text_overrides={support_proof.passage_id: changed_text},
    )
    stale_text_proof = replace(support_proof, context=changed_text_context)
    falsifiers["stale_measurement_changed_passage"] = _expect_bound_refusal(
        "SOURCE_RECONSTRUCTION_FAILED",
        lambda: bound_relation.verify_bound_temporal_proof(
            proof=stale_text_proof,
            atom_trusted_keys=ATOM_KEYS,
            proposition_trusted_keys=PROP_KEYS,
        ),
    )

    stale_warrant_proof = replace(refute_proof, atom_warrant=support_proof.atom_warrant)
    falsifiers["stale_atom_warrant"] = _expect_bound_refusal(
        "ATOM_WARRANT_REVERIFY_FAILED",
        lambda: bound_relation.verify_bound_temporal_proof(
            proof=stale_warrant_proof,
            atom_trusted_keys=ATOM_KEYS,
            proposition_trusted_keys=PROP_KEYS,
        ),
    )

    after_row = {**cohort["proposition"], "relation": "AFTER"}
    after_prop = _proposition(after_row)
    changed_prop_spec = {
        "bundle_id": "bundle-bound-changed-proposition",
        "passages": cohort["single_support"]["passages"],
    }
    changed_prop_context = _context(spec=changed_prop_spec, proposition=after_prop)
    changed_prop_proof = _proof(
        context=changed_prop_context,
        passage_id=changed_prop_spec["passages"][0]["passage_id"],
        proposition=after_prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )
    stale_prop_binding = replace(
        changed_prop_proof,
        proposition_binding=support_proof.proposition_binding,
    )
    falsifiers["stale_proposition_binding"] = _expect_bound_refusal(
        "PROPOSITION_BINDING_REVERIFY_FAILED",
        lambda: bound_relation.verify_bound_temporal_proof(
            proof=stale_prop_binding,
            atom_trusted_keys=ATOM_KEYS,
            proposition_trusted_keys=PROP_KEYS,
        ),
    )

    mutated_relation = replace(support_proof.relation, relation="REFUTES")
    forged_relation_proof = replace(support_proof, relation=mutated_relation)
    falsifiers["caller_modified_relation"] = _expect_bound_refusal(
        "RELATION_REDERIVATION_MISMATCH",
        lambda: bound_relation.verify_bound_temporal_proof(
            proof=forged_relation_proof,
            atom_trusted_keys=ATOM_KEYS,
            proposition_trusted_keys=PROP_KEYS,
        ),
    )

    wrong_passage_proof = replace(mixed_support, passage_id=mixed_refute.passage_id)
    falsifiers["measurement_passage_substitution"] = _expect_bound_refusal(
        "SOURCE_RECONSTRUCTION_FAILED",
        lambda: bound_relation.verify_bound_temporal_proof(
            proof=wrong_passage_proof,
            atom_trusted_keys=ATOM_KEYS,
            proposition_trusted_keys=PROP_KEYS,
        ),
    )

    projector_params = set(inspect.signature(bound_projection.project_bound_temporal_contract_c).parameters)
    no_caller_binding_surface = not ({"contract_b_binding", "evidence_index", "bundle_id", "bundle_hash"} & projector_params)
    falsifiers["no_caller_contract_b_binding_surface"] = {
        "pass": no_caller_binding_surface,
        "parameters": sorted(projector_params),
    }

    positive_failures = [name for name, row in positive.items() if not row["pass"]]
    falsifier_failures = [name for name, row in falsifiers.items() if not row["pass"]]
    unresolved_gap_preserved = (
        unresolved_projection.projection_status == "VALID_WITH_PROVENANCE_COMPRESSION"
        and len(unresolved_projection.omitted_relation_ids) == 1
    )
    disposition = (
        "SUPPORTED_WITH_BOUNDS_AND_CONTRACT_C_PROVENANCE_GAP"
        if not positive_failures and not falsifier_failures and unresolved_gap_preserved
        else "FALSIFIED_BOUND_TEMPORAL_WORLD_SUCCESSOR"
    )
    result = {
        "schema": SCHEMA,
        "candidate_freeze": CANDIDATE_FREEZE,
        "candidate_blobs": CANDIDATE_BLOBS,
        "contract_c_authority": CONTRACT_C_HEAD,
        "positive_controls": positive,
        "falsifiers": falsifiers,
        "summary": {
            "positive_failures": positive_failures,
            "falsifier_failures": falsifier_failures,
            "same_world_mixed_order_invariant": positive["same_world_mixed"]["pass"],
            "cross_bundle_composition_refused": falsifiers["cross_bundle_composition"]["pass"],
            "cross_bundle_projection_refused": falsifiers["cross_bundle_projection"]["pass"],
            "unresolved_contract_c_provenance_gap_preserved": unresolved_gap_preserved,
        },
        "research_disposition": disposition,
        "interpretation": {
            "single_relation_temporal_semantics_reproduced": not positive_failures,
            "common_evidence_world_binding_supported_in_candidate": not falsifier_failures,
            "contract_c_unresolved_evidence_provenance_lossless": False,
            "decision_engine_conformance_established": False,
            "contract_e_authorization_evaluated": False,
            "production_promotion_authorized": False,
        },
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "BOUND-EVALUATION.json").write_bytes(failed_projection.canonical_bytes(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--event-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--contract-c-root", type=Path, required=True)
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = execute(
        repo_root=args.repo_root.resolve(),
        event_root=args.event_root.resolve(),
        rc8j_root=args.rc8j_root.resolve(),
        contract_c_root=args.contract_c_root.resolve(),
        cohort_path=args.cohort.resolve(),
        out_dir=args.out.resolve(),
    )
    print(json.dumps({"research_disposition": result["research_disposition"], **result["summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
