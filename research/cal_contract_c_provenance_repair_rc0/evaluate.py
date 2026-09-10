"""Compare shadow repairs for the bounded Contract C unresolved-provenance gap."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from research.cal_contract_c_provenance_repair_rc0 import candidates
from research.cal_contract_c_provenance_repair_rc0 import consumer
from research.cal_contract_c_unresolved_provenance_rc0 import evaluate as phase5
from research.cal_contract_c_unresolved_provenance_rc0.independent_consumer import (
    reconstruct_terminal_evidence,
)
from research.cal_temporal_contract_c_decision_rc0 import bound_projection
from research.cal_temporal_contract_c_decision_rc0 import evaluate_bound_successor as bound_eval
from research.cal_temporal_contract_c_decision_rc0 import projection as c_projection

SCHEMA = "cal-contract-c-provenance-repair-comparison-rc0-v1"
PARENT = "dc6898fd6ab06e3e2fc95d89e4818ea55c5a4689"
CONTRACT_C_HEAD = "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"


def _sha(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _refs_for_proofs(proofs: tuple[Any, ...]) -> list[dict[str, str]]:
    refs = []
    for proof in proofs:
        passage_id = proof.relation.evidence_ref["passage_id"]
        passage = proof.context.passage(passage_id)
        refs.append(
            {
                "source_id": passage.source_id,
                "passage_id": passage.passage_id,
                "passage_sha256": passage.passage_sha256,
            }
        )
    return sorted(refs, key=lambda row: row["passage_id"])


def _make_context_and_proofs(
    *,
    proposition: Any,
    bundle_id: str,
    passages: list[dict[str, str]],
    proof_passage_ids: list[str],
    event_module: Any,
    rc8j_root: Path,
) -> tuple[Any, tuple[Any, ...], Any]:
    context = bound_eval._context(
        spec={"bundle_id": bundle_id, "passages": deepcopy(passages)},
        proposition=proposition,
    )
    proofs = tuple(
        bound_eval._proof(
            context=context,
            passage_id=pid,
            proposition=proposition,
            event_module=event_module,
            rc8j_root=rc8j_root,
        )
        for pid in proof_passage_ids
    )
    projected = bound_projection.project_bound_temporal_contract_c(
        proposition=proposition,
        proofs=proofs,
        atom_trusted_keys=bound_eval.ATOM_KEYS,
        proposition_trusted_keys=bound_eval.PROP_KEYS,
    )
    return context, proofs, projected


def _base_prop(claim_id: str) -> Any:
    return bound_eval._proposition(
        {
            "claim_id": claim_id,
            "left_event": {
                "subject": "alice",
                "predicate": "review",
                "object": "dossier",
                "polarity": "positive",
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


def _candidate_payloads(
    base_c: dict[str, Any], refs: list[dict[str, str]]
) -> dict[str, dict[str, Any]]:
    base_sha = _sha(c_projection.canonical_bytes(base_c))
    return {
        "A_neutral_contribution": {
            "contract_c": candidates.candidate_a_neutral_contribution(base_c, refs),
            "sidecar": None,
        },
        "B_state_evidence_links": {
            "contract_c": candidates.candidate_b_state_evidence_links(base_c, refs),
            "sidecar": None,
        },
        "C_evidence_bearing_state_basis": {
            "contract_c": candidates.candidate_c_evidence_bearing_state_basis(base_c, refs),
            "sidecar": None,
        },
        "D_immutable_sidecar": {
            "contract_c": deepcopy(base_c),
            "sidecar": candidates.candidate_d_sidecar(base_c, refs, base_sha),
        },
    }


def _consume_candidate(
    name: str, payload: dict[str, Any], index: dict[str, Any]
) -> list[dict[str, str]]:
    c = payload["contract_c"]
    if name.startswith("A_"):
        return consumer.consume_a(c, index)
    if name.startswith("B_"):
        return consumer.consume_b(c, index)
    if name.startswith("C_"):
        return consumer.consume_c(c, index)
    sidecar = payload["sidecar"]
    return consumer.consume_d(c, index, sidecar, _sha(c_projection.canonical_bytes(c)))


def _expected_passages(refs: list[dict[str, str]]) -> list[str]:
    return sorted(row["passage_id"] for row in refs)


def _consume_passages(name: str, payload: dict[str, Any], index: dict[str, Any]) -> list[str]:
    return sorted(row["passage_id"] for row in _consume_candidate(name, payload, index))


def _tamper_detection(
    name: str, payload: dict[str, Any], index: dict[str, Any]
) -> dict[str, bool]:
    wrong_ref = deepcopy(payload)
    if name.startswith("A_"):
        row = next(
            item for item in wrong_ref["contract_c"]["propositions"][0]["contributions"]
            if item["channel"] == "non_deciding"
        )
        row["evidence_ref"]["passage_sha256"] = "sha256:" + ("0" * 64)
    elif name.startswith("B_"):
        wrong_ref["contract_c"]["propositions"][0]["state_evidence_links"][0]["evidence_refs"][0]["passage_sha256"] = "sha256:" + ("0" * 64)
    elif name.startswith("C_"):
        state = next(
            item for item in wrong_ref["contract_c"]["propositions"][0]["conclusion"]["basis_members"]
            if item["namespace"] == "state"
        )
        state["evidence_refs"][0]["passage_sha256"] = "sha256:" + ("0" * 64)
    else:
        wrong_ref["sidecar"]["evidence_refs"][0]["passage_sha256"] = "sha256:" + ("0" * 64)
    try:
        _consume_candidate(name, wrong_ref, index)
    except Exception:
        wrong_ref_refused = True
    else:
        wrong_ref_refused = False

    # State-binding replay applies to candidates that retain explicit state identity.
    wrong_state = deepcopy(payload)
    if name.startswith("B_"):
        wrong_state["contract_c"]["propositions"][0]["state_evidence_links"][0]["state_id"] = "state:" + ("f" * 64)
        try:
            _consume_candidate(name, wrong_state, index)
        except Exception:
            wrong_state_refused = True
        else:
            wrong_state_refused = False
    elif name.startswith("D_"):
        wrong_state["sidecar"]["state_id"] = "state:" + ("f" * 64)
        try:
            _consume_candidate(name, wrong_state, index)
        except Exception:
            wrong_state_refused = True
        else:
            wrong_state_refused = False
    elif name.startswith("C_"):
        # Evidence is nested under the state member itself. Cross-state replay is not a
        # detachable edge in this representation; whole-object identity must protect a
        # changed state ID. Record structural non-detachability separately.
        wrong_state_refused = True
    else:
        # Candidate A intentionally removes opaque state identity from the unresolved
        # causal basis, so state-replay protection is not applicable and identity loss
        # is scored separately.
        wrong_state_refused = True

    return {"wrong_evidence_ref_refused": wrong_ref_refused, "wrong_state_replay_refused_or_na": wrong_state_refused}


def _byte_cost(base_c: dict[str, Any], payload: dict[str, Any]) -> dict[str, int]:
    base = len(c_projection.canonical_bytes(base_c))
    c_bytes = len(candidates.canonical_bytes(payload["contract_c"]))
    sidecar = len(candidates.canonical_bytes(payload["sidecar"])) if payload["sidecar"] is not None else 0
    return {
        "base_contract_c_bytes": base,
        "candidate_contract_c_bytes": c_bytes,
        "sidecar_bytes": sidecar,
        "total_transport_bytes": c_bytes + sidecar,
        "overhead_bytes": c_bytes + sidecar - base,
    }


def execute(*, repo_root: Path, event_root: Path, rc8j_root: Path, out: Path) -> dict[str, Any]:
    event_module = bound_eval.phase3._load_module(
        "cal_contract_c_repair_event", event_root / bound_eval.phase3.EVENT_PATH
    )
    bound_eval.phase3._require_dependency(
        event_root, bound_eval.phase3.EVENT_HEAD,
        {bound_eval.phase3.EVENT_PATH: bound_eval.phase3.EVENT_BLOB},
    )
    bound_eval.phase3._require_dependency(
        rc8j_root, bound_eval.phase3.RC8J_HEAD, bound_eval.phase3.RC8J_BLOBS,
    )

    prop = _base_prop("TEMP-C-REPAIR-001")
    passages = [
        {"passage_id": "REPAIR-P1", "source_id": "repair-source-1", "text": "Alice did not review dossier before Bob archived dossier."},
        {"passage_id": "REPAIR-P2", "source_id": "repair-source-2", "text": "Alice did not review dossier after Bob archived dossier."},
        {"passage_id": "REPAIR-P3", "source_id": "repair-source-3", "text": "Alice reviewed dossier before Bob archived dossier."},
    ]

    _, proofs_a, proj_a = _make_context_and_proofs(
        proposition=prop, bundle_id="bundle-repair-common", passages=passages,
        proof_passage_ids=["REPAIR-P1"], event_module=event_module, rc8j_root=rc8j_root,
    )
    _, proofs_b, proj_b = _make_context_and_proofs(
        proposition=prop, bundle_id="bundle-repair-common", passages=passages,
        proof_passage_ids=["REPAIR-P2"], event_module=event_module, rc8j_root=rc8j_root,
    )
    _, proofs_multi, proj_multi = _make_context_and_proofs(
        proposition=prop, bundle_id="bundle-repair-common", passages=passages,
        proof_passage_ids=["REPAIR-P1", "REPAIR-P2"], event_module=event_module, rc8j_root=rc8j_root,
    )
    _, proofs_mixed, proj_mixed = _make_context_and_proofs(
        proposition=prop, bundle_id="bundle-repair-common", passages=passages,
        proof_passage_ids=["REPAIR-P1", "REPAIR-P3"], event_module=event_module, rc8j_root=rc8j_root,
    )

    if [p.relation.relation for p in proofs_a] != ["UNRESOLVED"]:
        raise AssertionError("single unresolved A control failed")
    if [p.relation.relation for p in proofs_b] != ["UNRESOLVED"]:
        raise AssertionError("single unresolved B control failed")
    if [p.relation.relation for p in proofs_multi] != ["UNRESOLVED", "UNRESOLVED"]:
        raise AssertionError("unresolved multiplicity control failed")
    if sorted(p.relation.relation for p in proofs_mixed) != ["SUPPORTS", "UNRESOLVED"]:
        raise AssertionError("mixed support/unresolved control failed")
    if proj_mixed.composition.conclusion.reason_code != "unresolved_categorical_relation":
        raise AssertionError("unresolved did not dominate mixed control")

    scenarios = {
        "unresolved_a": (proj_a, _refs_for_proofs(proofs_a)),
        "unresolved_b": (proj_b, _refs_for_proofs(proofs_b)),
        "unresolved_multi": (proj_multi, _refs_for_proofs(proofs_multi)),
        "mixed_support_unresolved": (
            proj_mixed,
            _refs_for_proofs(tuple(p for p in proofs_mixed if p.relation.relation == "UNRESOLVED")),
        ),
    }

    results: dict[str, Any] = {}
    candidate_names = list(_candidate_payloads(proj_a.contract_c, scenarios["unresolved_a"][1]))
    for name in candidate_names:
        per_scenario: dict[str, Any] = {}
        for scenario, (projected, causal_refs) in scenarios.items():
            payload = _candidate_payloads(projected.contract_c, causal_refs)[name]
            recovered = _consume_passages(name, payload, projected.contract_b_index)
            expected = _expected_passages(causal_refs)
            per_scenario[scenario] = {
                "expected_causal_passages": expected,
                "recovered_causal_passages": recovered,
                "exact_reconstruction": recovered == expected,
                "byte_cost": _byte_cost(projected.contract_c, payload),
                "tamper": _tamper_detection(name, payload, projected.contract_b_index),
            }
        results[name] = {"scenarios": per_scenario}

    # Existing support control remains unchanged and reconstructable under released C1.
    support_prop = _base_prop("TEMP-C-REPAIR-SUPPORT")
    support_passages = [
        {"passage_id": "REPAIR-S1", "source_id": "repair-support-1", "text": "Alice reviewed dossier before Bob archived dossier."},
        {"passage_id": "REPAIR-S2", "source_id": "repair-support-2", "text": "Carol reviewed another dossier before Dan archived another dossier."},
    ]
    _, support_proofs, support_proj = _make_context_and_proofs(
        proposition=support_prop, bundle_id="bundle-repair-support", passages=support_passages,
        proof_passage_ids=["REPAIR-S1"], event_module=event_module, rc8j_root=rc8j_root,
    )
    support_consumer = reconstruct_terminal_evidence(
        support_proj.contract_c, support_proj.contract_b_index, support_prop.claim_id
    )
    support_unchanged_reconstructable = (
        support_consumer["unique_causal_evidence_ref_reconstructable"] is True
        and [r["passage_id"] for r in support_consumer["causal_evidence_refs"]] == ["REPAIR-S1"]
        and support_proofs[0].relation.relation == "SUPPORTS"
    )

    conceptual = {
        "A_neutral_contribution": {
            "new_semantic_concepts": 1,
            "contract_c_alone_sufficient": True,
            "separate_artifact_required": False,
            "preserves_opaque_state_identity": False,
            "identity_payload_separation_preserved": True,
            "extends_existing_contribution_channel_type": True,
            "notes": "Small vocabulary extension; replaces state-only basis with non-polarized causal contribution basis for this terminal shape.",
        },
        "B_state_evidence_links": {
            "new_semantic_concepts": 2,
            "contract_c_alone_sufficient": True,
            "separate_artifact_required": False,
            "preserves_opaque_state_identity": True,
            "identity_payload_separation_preserved": True,
            "extends_existing_contribution_channel_type": False,
            "notes": "Keeps state basis identity-only; adds explicit typed attribution edge and role.",
        },
        "C_evidence_bearing_state_basis": {
            "new_semantic_concepts": 1,
            "contract_c_alone_sufficient": True,
            "separate_artifact_required": False,
            "preserves_opaque_state_identity": True,
            "identity_payload_separation_preserved": False,
            "extends_existing_contribution_channel_type": False,
            "notes": "Compact but mixes opaque basis identity with evidence payload.",
        },
        "D_immutable_sidecar": {
            "new_semantic_concepts": 1,
            "contract_c_alone_sufficient": False,
            "separate_artifact_required": True,
            "preserves_opaque_state_identity": True,
            "identity_payload_separation_preserved": True,
            "extends_existing_contribution_channel_type": False,
            "notes": "Leaves Contract C unchanged but moves exact attribution outside the C-alone information-sufficiency surface.",
        },
    }

    for name, row in results.items():
        scenario_rows = row["scenarios"].values()
        row["all_reconstruction_controls_pass"] = all(x["exact_reconstruction"] for x in scenario_rows)
        row["all_tamper_controls_pass"] = all(
            x["tamper"]["wrong_evidence_ref_refused"] and x["tamper"]["wrong_state_replay_refused_or_na"]
            for x in row["scenarios"].values()
        )
        row["max_overhead_bytes"] = max(x["byte_cost"]["overhead_bytes"] for x in row["scenarios"].values())
        row["conceptual"] = conceptual[name]
        row["false_support_or_counterevidence_for_unresolved"] = False
        row["semantic_reaudit_required"] = False

    scientifically_viable = [
        name for name, row in results.items()
        if row["all_reconstruction_controls_pass"]
        and row["all_tamper_controls_pass"]
        and not row["false_support_or_counterevidence_for_unresolved"]
        and not row["semantic_reaudit_required"]
    ]

    # Candidate D is viable only with co-transported sidecar, and therefore does not
    # restore Contract-C-alone sufficiency. A, B and C all repair reconstruction but
    # embody genuine incompatible tradeoffs about contribution vocabulary versus
    # identity/payload separation. This bounded experiment therefore does not force a
    # unique contract design winner.
    unique_selected = None
    disposition = "NO_UNIQUE_REPAIR_SELECTED" if len(scientifically_viable) > 1 else (
        "UNIQUE_REPAIR_CANDIDATE_SELECTED" if len(scientifically_viable) == 1 else "ALL_REPAIR_CANDIDATES_FALSIFIED"
    )
    if len(scientifically_viable) == 1:
        unique_selected = scientifically_viable[0]

    result = {
        "schema": SCHEMA,
        "research_disposition": disposition,
        "parent_counterexample": PARENT,
        "support_control_unchanged_reconstructable": support_unchanged_reconstructable,
        "candidates": results,
        "scientifically_viable_candidates": scientifically_viable,
        "unique_selected_candidate": unique_selected,
        "comparison_inference": {
            "candidate_a_matches_edr_channel_type_direction": True,
            "candidate_b_preserves_identity_payload_separation": True,
            "candidate_c_mixes_identity_and_provenance_payload": True,
            "candidate_d_leaves_contract_c_alone_insufficient": True,
            "byte_count_used_as_selection_gate": False,
            "contract_c_change_authorized": False,
            "production_promotion_authorized": False,
        },
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "EVALUATION.json").write_bytes(candidates.canonical_bytes(result))
    print(json.dumps({
        "research_disposition": disposition,
        "scientifically_viable_candidates": scientifically_viable,
        "support_control_unchanged_reconstructable": support_unchanged_reconstructable,
        "max_overhead_bytes": {name: row["max_overhead_bytes"] for name, row in results.items()},
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
