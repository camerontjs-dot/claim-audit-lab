from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from claim_audit_lab.cal_v1_candidate import (
    AdmittedPassage,
    AuditContext,
    Conclusion,
    EvidenceWorld,
    FailureCode,
    SemanticFamily,
    TypedProposition,
    audit,
    project_contract_c_successor,
)

SEMANTIC_SHA = "a" * 40


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return f"sha256:{_hex(value)}"


def _aperture(label: str) -> dict[str, object]:
    return {
        "search_scope": {"corpus": label},
        "outcome": {"state": "unknown", "value": None},
        "limitations": [],
    }


def _context(texts: list[str], *, label: str) -> AuditContext:
    passages = tuple(
        AdmittedPassage.create(f"p{index}", "source-1", text)
        for index, text in enumerate(texts, start=1)
    )
    world = EvidenceWorld.create(
        "1.2.0",
        f"bundle-{label}",
        _tagged(f"bundle-{label}"),
        passages,
        _aperture(label),
    )
    proposition = TypedProposition.create(
        "claim-1",
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Women",
            "rhs_entity": "Men",
            "comparison_direction": "MORE_THAN",
        },
        text_sha256=_hex("Women had a higher rate than Men."),
    )
    return AuditContext("Women had a higher rate than Men.", proposition, world)


def _index(context: AuditContext) -> dict[str, Any]:
    return {
        "contract_version": context.evidence_world.contract_b_version,
        "bundle_id": context.evidence_world.bundle_id,
        "bundle_hash": context.evidence_world.bundle_hash,
        "propositions": {
            context.proposition.proposition_id: context.proposition.text_sha256,
        },
        "passages": {
            passage.passage_id: {
                "source_id": passage.source_id,
                "passage_sha256": passage.text_sha256,
            }
            for passage in context.evidence_world.admitted_passages
        },
    }


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _load_candidate_validator(apparatus_root: Path):
    sys.path.insert(0, str(apparatus_root.resolve()))
    path = apparatus_root / "research" / "contract_c_successor_candidate_rc0" / "validator.py"
    spec = importlib.util.spec_from_file_location("apparatus_contract_c_candidate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load exact Apparatus candidate validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _project_and_validate(context: AuditContext, candidate_validator) -> dict[str, Any]:
    result = audit(context)
    payload = project_contract_c_successor(
        context,
        result,
        semantic_implementation_sha=SEMANTIC_SHA,
    )
    errors = candidate_validator.validate_candidate_object(payload, contract_b_index=_index(context))
    return {
        "context": context,
        "result": result,
        "payload": payload,
        "errors": errors,
        "bytes": _canonical_bytes(payload),
    }


def _contribution_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    proposition = payload["propositions"][0]
    return {
        row["evidence_ref"]["passage_id"]: row
        for row in proposition["contributions"]
    }


def _basis_passages(payload: dict[str, Any]) -> set[str]:
    proposition = payload["propositions"][0]
    by_id = {
        row["contribution_id"]: row["evidence_ref"]["passage_id"]
        for row in proposition["contributions"]
    }
    return {
        by_id[member["id"]]
        for member in proposition["conclusion"]["basis_members"]
        if member["namespace"] == "contribution"
    }


def evaluate(apparatus_root: Path) -> dict[str, Any]:
    candidate = _load_candidate_validator(apparatus_root)
    checks: dict[str, bool] = {}
    observations: dict[str, Any] = {}

    support_a = "Women had a higher rate than Men."
    support_b = "Women had a greater rate than Men."
    refute = "Women had a lower rate than Men."
    irrelevant = "Cats had a higher rate than Dogs."

    # C3: single deciding support plus a neutral residual.
    single = _project_and_validate(
        _context([support_a, irrelevant], label="single-plus-residual"), candidate
    )
    single_prop = single["payload"]["propositions"][0]
    single_channels = {
        passage: row["channel"] for passage, row in _contribution_map(single["payload"]).items()
    }
    checks["single_plus_residual_candidate_valid"] = single["errors"] == []
    checks["single_plus_residual_semantics"] = (
        single["result"].conclusion is Conclusion.SUPPORTED
        and single_prop["conclusion"]["reported_verdict"] == "supported"
        and single_prop["conclusion"]["causal_form"] == "single_necessary"
        and single_channels == {"p1": "support", "p2": "non_deciding"}
        and _basis_passages(single["payload"]) == {"p1"}
        and len(single_prop["conclusion"]["residual_contribution_ids"]) == 1
    )

    # C2: deterministic repeat of exact legitimate producer state.
    repeated_payload = project_contract_c_successor(
        single["context"],
        single["result"],
        semantic_implementation_sha=SEMANTIC_SHA,
    )
    checks["projection_deterministic"] = (
        _canonical_bytes(repeated_payload) == single["bytes"]
        and repeated_payload["result_set_id"] == single["payload"]["result_set_id"]
    )

    # C4: two independently sufficient supports.
    two_support = _project_and_validate(
        _context([support_a, support_b], label="two-support"), candidate
    )
    support_a_only = audit(_context([support_a], label="support-a-only"))
    support_b_only = audit(_context([support_b], label="support-b-only"))
    two_support_prop = two_support["payload"]["propositions"][0]
    checks["two_support_candidate_valid"] = two_support["errors"] == []
    checks["two_support_independent_ablation"] = (
        two_support["result"].conclusion is Conclusion.SUPPORTED
        and support_a_only.conclusion is Conclusion.SUPPORTED
        and support_b_only.conclusion is Conclusion.SUPPORTED
        and two_support_prop["conclusion"]["causal_form"]
        == "independent_sufficient_alternatives"
        and _basis_passages(two_support["payload"]) == {"p1", "p2"}
    )

    # C5: exactly one support + one refute, where both are necessary for MIXED.
    minimal_mixed = _project_and_validate(
        _context([support_a, refute], label="minimal-mixed"), candidate
    )
    minimal_mixed_prop = minimal_mixed["payload"]["propositions"][0]
    refute_only = audit(_context([refute], label="refute-only"))
    checks["minimal_mixed_candidate_valid"] = minimal_mixed["errors"] == []
    checks["minimal_mixed_joint_ablation"] = (
        minimal_mixed["result"].conclusion is Conclusion.NOT_CHECKABLE
        and minimal_mixed["result"].failure_code is FailureCode.MIXED_RELATIONS
        and support_a_only.conclusion is Conclusion.SUPPORTED
        and refute_only.conclusion is Conclusion.CONTRADICTED
        and minimal_mixed_prop["conclusion"]["causal_form"] == "jointly_sufficient"
        and _basis_passages(minimal_mixed["payload"]) == {"p1", "p2"}
    )

    # F1: legitimate mixed state with a redundant duplicate support.
    mixed_redundant = _project_and_validate(
        _context([support_a, support_b, refute], label="mixed-redundant"), candidate
    )
    full_result = mixed_redundant["result"]
    full_prop = mixed_redundant["payload"]["propositions"][0]

    # Ablate each support while keeping the refute. Both ablations remain MIXED.
    remove_first_support = audit(
        _context([support_b, refute], label="mixed-without-support-a")
    )
    remove_second_support = audit(
        _context([support_a, refute], label="mixed-without-support-b")
    )
    both_supports_redundant_to_terminal_mixed = (
        remove_first_support.conclusion is Conclusion.NOT_CHECKABLE
        and remove_first_support.failure_code is FailureCode.MIXED_RELATIONS
        and remove_second_support.conclusion is Conclusion.NOT_CHECKABLE
        and remove_second_support.failure_code is FailureCode.MIXED_RELATIONS
    )
    exporter_marks_all_three_joint = (
        full_prop["conclusion"]["causal_form"] == "jointly_sufficient"
        and _basis_passages(mixed_redundant["payload"]) == {"p1", "p2", "p3"}
    )

    checks["mixed_redundant_candidate_structurally_valid"] = mixed_redundant["errors"] == []
    checks["mixed_redundant_ablation_proves_duplicate_support_not_necessary"] = (
        full_result.conclusion is Conclusion.NOT_CHECKABLE
        and full_result.failure_code is FailureCode.MIXED_RELATIONS
        and both_supports_redundant_to_terminal_mixed
    )
    checks["exporter_avoids_unsupported_joint_causal_claim"] = not (
        both_supports_redundant_to_terminal_mixed and exporter_marks_all_three_joint
    )

    observations["single_plus_residual"] = {
        "channels": single_channels,
        "causal_form": single_prop["conclusion"]["causal_form"],
        "basis_passages": sorted(_basis_passages(single["payload"])),
        "candidate_errors": single["errors"],
    }
    observations["two_support"] = {
        "causal_form": two_support_prop["conclusion"]["causal_form"],
        "basis_passages": sorted(_basis_passages(two_support["payload"])),
        "full_conclusion": two_support["result"].conclusion.value,
        "ablation_a": support_a_only.conclusion.value,
        "ablation_b": support_b_only.conclusion.value,
    }
    observations["minimal_mixed"] = {
        "causal_form": minimal_mixed_prop["conclusion"]["causal_form"],
        "basis_passages": sorted(_basis_passages(minimal_mixed["payload"])),
        "full_failure": minimal_mixed["result"].failure_code.value,
        "support_only": support_a_only.conclusion.value,
        "refute_only": refute_only.conclusion.value,
    }
    observations["mixed_redundant_falsifier"] = {
        "full_failure": full_result.failure_code.value if full_result.failure_code else None,
        "candidate_structurally_valid": mixed_redundant["errors"] == [],
        "projected_causal_form": full_prop["conclusion"]["causal_form"],
        "projected_basis_passages": sorted(_basis_passages(mixed_redundant["payload"])),
        "remove_support_a_failure": (
            remove_first_support.failure_code.value
            if remove_first_support.failure_code
            else None
        ),
        "remove_support_b_failure": (
            remove_second_support.failure_code.value
            if remove_second_support.failure_code
            else None
        ),
        "both_supports_individually_redundant_to_terminal_mixed": both_supports_redundant_to_terminal_mixed,
        "exporter_marks_all_three_jointly_sufficient": exporter_marks_all_three_joint,
    }

    prerequisite_checks = [
        "single_plus_residual_candidate_valid",
        "single_plus_residual_semantics",
        "projection_deterministic",
        "two_support_candidate_valid",
        "two_support_independent_ablation",
        "minimal_mixed_candidate_valid",
        "minimal_mixed_joint_ablation",
        "mixed_redundant_candidate_structurally_valid",
        "mixed_redundant_ablation_proves_duplicate_support_not_necessary",
    ]
    prereq_failures = [name for name in prerequisite_checks if not checks[name]]

    if prereq_failures:
        disposition = "INCONCLUSIVE"
        failures = prereq_failures
    elif not checks["exporter_avoids_unsupported_joint_causal_claim"]:
        disposition = "FALSIFIED"
        failures = ["exporter_avoids_unsupported_joint_causal_claim"]
    else:
        disposition = "SUPPORTED FOR PROMOTION"
        failures = []

    return {
        "schema": "contract-c-successor-producer-conformance-rc0-result-v1",
        "research_disposition": disposition,
        "cal_base": "a902621e8baea3063dddd7f92ba975aade305464",
        "apparatus_candidate": "242351af7214c23dce76edd06299f55c038cd3f0",
        "checks": checks,
        "failures": failures,
        "observations": observations,
        "interpretation": {
            "structural_candidate_validity_is_sufficient_for_producer_conformance": False,
            "exporter_may_invent_causal_multiplicity": disposition == "FALSIFIED",
            "production_promotion_authorized": False,
            "official_contract_c_version_assigned": False,
        },
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: evaluate.py <apparatus-candidate-root> <output-json>")
    apparatus_root = Path(sys.argv[1])
    output = Path(sys.argv[2])
    result = evaluate(apparatus_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["research_disposition"] == "INCONCLUSIVE":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
