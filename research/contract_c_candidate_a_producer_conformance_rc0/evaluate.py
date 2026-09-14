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
)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from materialize import (  # noqa: E402
    UnrepresentablePublicReason,
    derive_basis_passage_ids,
    materialize_unsealed,
    public_terminal_state,
)

CAL = "a902621e8baea3063dddd7f92ba975aade305464"
APPARATUS = "ba5f55b0fb6ca54e0461a688813b66fd81bf8c4c"
RESOLVER_COMMIT = "43b571464734325277374ee81098553fb7c1b944"

SUPPORT_A = "Women had a higher rate than Men."
SUPPORT_B = "Women had a greater rate than Men."
REFUTE = "Women had a lower rate than Men."
IRRELEVANT = "Cats had a higher rate than Dogs."


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return "sha256:" + _hex(value)


def _aperture(label: str) -> dict[str, object]:
    return {
        "search_scope": {"corpus": label},
        "outcome": {"state": "unknown", "value": None},
        "limitations": [],
    }


def strict_context(rows: list[tuple[str, str]], label: str, *, proposition_id: str = "Q1") -> AuditContext:
    passages = tuple(
        AdmittedPassage.create(pid, f"src-{pid.lower()}", text)
        for pid, text in rows
    )
    world = EvidenceWorld.create(
        "1.2.0",
        f"bundle-{label}",
        _tagged(f"bundle-{label}"),
        passages,
        _aperture(label),
    )
    proposition = TypedProposition.create(
        proposition_id,
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Women",
            "rhs_entity": "Men",
            "comparison_direction": "MORE_THAN",
        },
        text_sha256=_hex("Women had a higher rate than Men."),
    )
    return AuditContext("Women had a higher rate than Men.", proposition, world)


def event_context(text: str, label: str) -> AuditContext:
    passage = AdmittedPassage.create("E1", "src-e1", text)
    world = EvidenceWorld.create(
        "1.2.0",
        f"bundle-{label}",
        _tagged(f"bundle-{label}"),
        (passage,),
        _aperture(label),
    )
    proposition = TypedProposition.create(
        "QE1",
        SemanticFamily.DIRECT_EVENT_ORDER,
        {
            "left_subject": "alice",
            "left_predicate": "review",
            "left_object": "dossier",
            "left_polarity": "positive",
            "temporal_relation": "BEFORE",
            "right_subject": "bob",
            "right_predicate": "archive",
            "right_object": "dossier",
            "right_polarity": "positive",
        },
        text_sha256=_hex("Alice reviewed dossier before Bob archived dossier."),
    )
    return AuditContext("Alice reviewed dossier before Bob archived dossier.", proposition, world)


def unsupported_context() -> AuditContext:
    passage = AdmittedPassage.create("U0", "src-u0", "Alice may release dossier.")
    world = EvidenceWorld.create(
        "1.2.0",
        "bundle-unsupported",
        _tagged("bundle-unsupported"),
        (passage,),
        _aperture("unsupported"),
    )
    proposition = TypedProposition.create(
        "QU0",
        SemanticFamily.PERMISSION_EXCEPTION,
        {"actor": "alice"},
        text_sha256=_hex("Alice may release dossier."),
    )
    return AuditContext("Alice may release dossier.", proposition, world)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _normalize_groups(groups: Any) -> tuple[tuple[str, ...], ...]:
    return tuple(sorted(tuple(sorted(str(member) for member in group)) for group in groups))


def _candidate_groups(sealed: dict[str, Any]) -> tuple[tuple[str, ...], ...]:
    prop = sealed["propositions"][0]
    return _normalize_groups(
        [[ref["passage_id"] for ref in group] for group in prop["basis_groups"]]
    )


def _candidate_roles(sealed: dict[str, Any]) -> dict[str, tuple[str, str]]:
    prop = sealed["propositions"][0]
    return {
        row["evidence_ref"]["passage_id"]: (row["relation"], row["role"])
        for row in prop["participants"]
    }


def _weak_flat_groups(result) -> tuple[tuple[str, ...], ...]:
    deciding = tuple(
        sorted(
            trace.passage_id
            for trace in result.traces
            if trace.relation is not None
            and trace.relation.categorical_relation.value in {"SUPPORTS", "REFUTES"}
        )
    )
    if result.failure_code is FailureCode.MIXED_RELATIONS and deciding:
        return (deciding,)
    return tuple((pid,) for pid in deciding)


def _validate_candidate(candidate, resolver: dict[str, Any], context: AuditContext, result) -> dict[str, Any]:
    unsealed = materialize_unsealed(
        context,
        result,
        semantic_implementation_sha=CAL,
    )
    sealed = candidate.seal(unsealed)
    candidate.validate_object(sealed)
    exact_b = unsealed["contract_b"]
    evidence_index = [
        (passage.source_id, passage.passage_id)
        for passage in context.evidence_world.admitted_passages
    ]
    candidate.verify_contract_b_references(
        sealed,
        exact_contract_b=exact_b,
        evidence_index=evidence_index,
    )
    candidate.verify_policy_resolution(
        sealed,
        independently_selected_resolver_commit_sha=RESOLVER_COMMIT,
        resolver_entries=resolver["entries"],
    )
    return sealed


def evaluate(apparatus_root: Path) -> dict[str, Any]:
    candidate = _load_module(
        "candidate_a_rc1",
        apparatus_root
        / "research"
        / "contract_c_successor_candidate_a_rc1_20260913"
        / "candidate_a_rc1.py",
    )
    phase2 = _load_module(
        "phase2_oracle",
        apparatus_root
        / "research"
        / "contract_c_successor_ground_up_20260913"
        / "phase2_bakeoff.py",
    )
    resolver = json.loads(
        (
            apparatus_root
            / "research"
            / "contract_c_successor_ground_up_20260913"
            / "PHASE_1_5_POLICY_RESOLVER.json"
        ).read_text()
    )
    oracles = phase2.oracles()

    cases: dict[str, AuditContext] = {
        "SP-01-single-support": strict_context([("S1", SUPPORT_A)], "sp01"),
        "SP-02-single-refutation": strict_context([("R1", REFUTE)], "sp02"),
        "SP-03-two-independent-supports": strict_context(
            [("S1", SUPPORT_A), ("S2", SUPPORT_B)], "sp03"
        ),
        "SP-04-two-independent-refutations": strict_context(
            [("R1", REFUTE), ("R2", REFUTE)], "sp04"
        ),
        "SP-06-support-plus-neutral-residual": strict_context(
            [("S1", SUPPORT_A), ("N1", IRRELEVANT)], "sp06"
        ),
        "SP-09-minimal-mixed": strict_context(
            [("S1", SUPPORT_A), ("R1", REFUTE)], "sp09"
        ),
        "SP-10-alt-joint-mixed": strict_context(
            [("S1", SUPPORT_A), ("S2", SUPPORT_B), ("R1", REFUTE)], "sp10"
        ),
        "SP-11-symmetric-alt-joint-mixed": strict_context(
            [("S1", SUPPORT_A), ("R1", REFUTE), ("R2", REFUTE)], "sp11"
        ),
        "SP-12-alt-by-alt-mixed": strict_context(
            [
                ("S1", SUPPORT_A),
                ("S2", SUPPORT_B),
                ("R1", REFUTE),
                ("R2", REFUTE),
            ],
            "sp12",
        ),
        "SP-13-completed-no-deciding": strict_context([("N1", IRRELEVANT)], "sp13"),
    }

    checks: dict[str, bool] = {}
    observations: dict[str, Any] = {}

    all_oracle_cases_match = True
    all_candidate_valid = True
    deterministic = True
    for case_id, context in cases.items():
        result = audit(context)
        sealed = _validate_candidate(candidate, resolver, context, result)
        repeat = _validate_candidate(candidate, resolver, context, result)
        deterministic = deterministic and candidate.canonical_bytes(sealed) == candidate.canonical_bytes(repeat)

        oracle_prop = oracles[case_id]["propositions"][0]
        expected_groups = _normalize_groups(oracle_prop["msc"])
        observed_groups = _candidate_groups(sealed)
        prop = sealed["propositions"][0]
        expected_terminal = oracle_prop["terminal"]
        terminal_match = prop["terminal"] == expected_terminal
        groups_match = observed_groups == expected_groups

        expected_roles = {
            row["symbol"]: (
                "supports" if row["polarity"] == "support" else "refutes" if row["polarity"] == "refute" else "non_polarized",
                row["role"],
            )
            for row in oracle_prop["participants"]
        }
        observed_roles = _candidate_roles(sealed)
        roles_match = observed_roles == expected_roles
        case_match = terminal_match and groups_match and roles_match
        all_oracle_cases_match = all_oracle_cases_match and case_match

        observations[case_id] = {
            "cal_conclusion": result.conclusion.value,
            "cal_failure": result.failure_code.value if result.failure_code else None,
            "public_terminal": list(public_terminal_state(result)),
            "basis_groups": [list(group) for group in observed_groups],
            "expected_basis_groups": [list(group) for group in expected_groups],
            "roles": observed_roles,
            "terminal_match": terminal_match,
            "groups_match": groups_match,
            "roles_match": roles_match,
            "candidate_whole_object_sha256": candidate.whole_object_sha256(sealed),
        }

    checks["phase2_current_cal_oracles_match"] = all_oracle_cases_match
    checks["candidate_a_structural_and_binding_validation"] = all_candidate_valid
    checks["deterministic_repeat"] = deterministic

    sp10_result = audit(cases["SP-10-alt-joint-mixed"])
    sp11_result = audit(cases["SP-11-symmetric-alt-joint-mixed"])
    sp10_target = _normalize_groups(oracles["SP-10-alt-joint-mixed"]["propositions"][0]["msc"])
    sp11_target = _normalize_groups(oracles["SP-11-symmetric-alt-joint-mixed"]["propositions"][0]["msc"])
    checks["sp10_exact_alt_joint_basis"] = derive_basis_passage_ids(cases["SP-10-alt-joint-mixed"], sp10_result) == sp10_target
    checks["sp11_exact_symmetric_alt_joint_basis"] = derive_basis_passage_ids(cases["SP-11-symmetric-alt-joint-mixed"], sp11_result) == sp11_target
    checks["weak_flat_control_killed"] = (
        _weak_flat_groups(sp10_result) != sp10_target
        and _weak_flat_groups(sp11_result) != sp11_target
    )
    observations["weak_flat_control"] = {
        "sp10": [list(group) for group in _weak_flat_groups(sp10_result)],
        "sp10_target": [list(group) for group in sp10_target],
        "sp11": [list(group) for group in _weak_flat_groups(sp11_result)],
        "sp11_target": [list(group) for group in sp11_target],
    }

    event_support = event_context(
        "Alice reviewed dossier before Bob archived dossier.", "event-support"
    )
    event_refute = event_context(
        "Alice reviewed dossier after Bob archived dossier.", "event-refute"
    )
    event_scope = event_context(
        "Report says Alice reviewed dossier before Bob archived dossier.", "event-scope"
    )
    event_support_result = audit(event_support)
    event_refute_result = audit(event_refute)
    event_scope_result = audit(event_scope)
    event_support_obj = _validate_candidate(candidate, resolver, event_support, event_support_result)
    event_refute_obj = _validate_candidate(candidate, resolver, event_refute, event_refute_result)
    event_scope_obj = _validate_candidate(candidate, resolver, event_scope, event_scope_result)
    checks["event_order_family_independent_basis"] = (
        _candidate_groups(event_support_obj) == (("E1",),)
        and event_support_obj["propositions"][0]["terminal"]
        == {"verdict": "supported", "reason": "categorical_support"}
        and _candidate_groups(event_refute_obj) == (("E1",),)
        and event_refute_obj["propositions"][0]["terminal"]
        == {"verdict": "contradicted", "reason": "categorical_refutation"}
        and _candidate_groups(event_scope_obj) == ()
        and event_scope_obj["propositions"][0]["terminal"]
        == {"verdict": "not_checkable", "reason": "no_deciding_relation"}
        and _candidate_roles(event_scope_obj)["E1"] == ("non_polarized", "residual")
    )
    observations["event_order"] = {
        "support": event_support_obj["propositions"][0],
        "refute": event_refute_obj["propositions"][0],
        "scope_refusal": event_scope_obj["propositions"][0],
    }

    unsupported = unsupported_context()
    unsupported_result = audit(unsupported)
    exact_reason_unrepresentable = False
    materializer_reason: str | None = None
    try:
        materialize_unsealed(unsupported, unsupported_result, semantic_implementation_sha=CAL)
    except UnrepresentablePublicReason as exc:
        exact_reason_unrepresentable = True
        materializer_reason = exc.reason

    candidate_rejects_exact_reason = False
    baseline = _validate_candidate(
        candidate,
        resolver,
        cases["SP-13-completed-no-deciding"],
        audit(cases["SP-13-completed-no-deciding"]),
    )
    mutated = json.loads(json.dumps(baseline))
    mutated.pop("result_set_id")
    mutated["propositions"][0]["terminal"]["reason"] = "UNSUPPORTED_SEMANTIC_FAMILY"
    resealed = candidate.seal(mutated)
    try:
        candidate.validate_object(resealed)
    except Exception:
        candidate_rejects_exact_reason = True

    checks["unsupported_family_is_legitimate_current_cal_result"] = (
        unsupported_result.conclusion is Conclusion.NOT_CHECKABLE
        and unsupported_result.failure_code is FailureCode.UNSUPPORTED_SEMANTIC_FAMILY
    )
    checks["candidate_a_can_preserve_unsupported_family_reason"] = not (
        exact_reason_unrepresentable and candidate_rejects_exact_reason
    )
    observations["unsupported_family_boundary"] = {
        "cal_conclusion": unsupported_result.conclusion.value,
        "cal_failure": unsupported_result.failure_code.value if unsupported_result.failure_code else None,
        "materializer_unrepresentable_reason": materializer_reason,
        "candidate_rejects_exact_public_reason": candidate_rejects_exact_reason,
    }

    prerequisite = [
        "phase2_current_cal_oracles_match",
        "candidate_a_structural_and_binding_validation",
        "deterministic_repeat",
        "sp10_exact_alt_joint_basis",
        "sp11_exact_symmetric_alt_joint_basis",
        "weak_flat_control_killed",
        "event_order_family_independent_basis",
        "unsupported_family_is_legitimate_current_cal_result",
    ]
    apparatus_failures = [name for name in prerequisite if not checks[name]]

    if apparatus_failures:
        disposition = "INCONCLUSIVE"
        failures = apparatus_failures
    elif not checks["candidate_a_can_preserve_unsupported_family_reason"]:
        disposition = "FALSIFIED"
        failures = ["candidate_a_can_preserve_unsupported_family_reason"]
    else:
        disposition = "SUPPORTED FOR PROMOTION"
        failures = []

    return {
        "schema": "contract-c-candidate-a-producer-conformance-rc0-result-v1",
        "research_disposition": disposition,
        "cal_authority": CAL,
        "apparatus_candidate": APPARATUS,
        "checks": checks,
        "failures": failures,
        "apparatus_failures": apparatus_failures,
        "observations": observations,
        "interpretation": {
            "basis_groups_derived_from_existing_relations_plus_compose_only": all_oracle_cases_match
            and checks["sp10_exact_alt_joint_basis"]
            and checks["sp11_exact_symmetric_alt_joint_basis"],
            "old_flat_causal_strategy_discriminated": checks["weak_flat_control_killed"],
            "candidate_a_rc1_complete_current_v1_producer_surface": disposition == "SUPPORTED FOR PROMOTION",
            "basis_group_architecture_falsified_by_unsupported_reason_gap": False,
            "production_promotion_authorized": False,
            "official_contract_c_version_assigned": False,
        },
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: evaluate.py <apparatus-root> <output-json>")
    apparatus_root = Path(sys.argv[1])
    output = Path(sys.argv[2])
    result = evaluate(apparatus_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
