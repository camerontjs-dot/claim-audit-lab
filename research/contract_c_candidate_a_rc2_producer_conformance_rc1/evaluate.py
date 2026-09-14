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
    CategoricalRelation,
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
    derive_basis_passage_ids,
    materialize_unsealed,
    public_terminal_state,
)

CAL = "a902621e8baea3063dddd7f92ba975aade305464"
APPARATUS_RC2 = "3e1c44d6e264e2baa37324b66f78165b15a927f1"
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


def strict_context(rows: list[tuple[str, str]], label: str) -> AuditContext:
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
        "Q1",
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
    passages = (
        AdmittedPassage.create("U1", "src-u1", "Alice may release dossier."),
        AdmittedPassage.create("U2", "src-u2", "Bob may retain dossier."),
    )
    world = EvidenceWorld.create(
        "1.2.0",
        "bundle-unsupported",
        _tagged("bundle-unsupported"),
        passages,
        _aperture("unsupported"),
    )
    proposition = TypedProposition.create(
        "QU0",
        SemanticFamily.PERMISSION_EXCEPTION,
        {"actor": "alice"},
        text_sha256=_hex("Alice may release dossier."),
    )
    return AuditContext("Alice may release dossier.", proposition, world)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def norm_groups(groups: Any) -> tuple[tuple[str, ...], ...]:
    return tuple(sorted(tuple(sorted(str(member) for member in group)) for group in groups))


def candidate_groups(sealed: dict[str, Any]) -> tuple[tuple[str, ...], ...]:
    return norm_groups(
        [
            [ref["passage_id"] for ref in group]
            for group in sealed["propositions"][0]["basis_groups"]
        ]
    )


def candidate_roles(sealed: dict[str, Any]) -> dict[str, tuple[str, str]]:
    return {
        row["evidence_ref"]["passage_id"]: (row["relation"], row["role"])
        for row in sealed["propositions"][0]["participants"]
    }


def weak_flat_groups(result) -> tuple[tuple[str, ...], ...]:
    deciding = tuple(
        sorted(
            trace.passage_id
            for trace in result.traces
            if trace.relation is not None
            and trace.relation.categorical_relation
            in {CategoricalRelation.SUPPORTS, CategoricalRelation.REFUTES}
        )
    )
    if result.failure_code is FailureCode.MIXED_RELATIONS and deciding:
        return (deciding,)
    return tuple((pid,) for pid in deciding)


def validate_candidate(candidate, resolver: dict[str, Any], context: AuditContext, result) -> dict[str, Any]:
    unsealed = materialize_unsealed(
        context,
        result,
        semantic_implementation_sha=CAL,
    )
    sealed = candidate.seal(unsealed)
    candidate.verify_candidate(
        sealed,
        exact_contract_b=unsealed["contract_b"],
        evidence_index={
            (passage.source_id, passage.passage_id)
            for passage in context.evidence_world.admitted_passages
        },
        independently_selected_resolver_commit_sha=RESOLVER_COMMIT,
        resolver_entries=resolver["entries"],
        expected_whole_object_sha256=candidate.whole_object_sha256(sealed),
    )
    return sealed


def evaluate(apparatus_root: Path) -> dict[str, Any]:
    candidate = load_module(
        "candidate_a_rc2",
        apparatus_root
        / "research"
        / "contract_c_successor_candidate_a_rc2_20260913"
        / "candidate_a_rc2.py",
    )
    phase2 = load_module(
        "phase2_oracle_for_cal_rc2",
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
    inherited_ok = True
    deterministic = True

    for case_id, context in cases.items():
        result = audit(context)
        sealed = validate_candidate(candidate, resolver, context, result)
        repeat = validate_candidate(candidate, resolver, context, result)
        deterministic = deterministic and candidate.canonical_bytes(sealed) == candidate.canonical_bytes(repeat)

        oracle_prop = oracles[case_id]["propositions"][0]
        expected_groups = norm_groups(oracle_prop["msc"])
        expected_roles = {
            row["symbol"]: (
                "supports"
                if row["polarity"] == "support"
                else "refutes"
                if row["polarity"] == "refute"
                else "non_polarized",
                row["role"],
            )
            for row in oracle_prop["participants"]
        }
        prop = sealed["propositions"][0]
        matches = (
            prop["terminal"] == oracle_prop["terminal"]
            and candidate_groups(sealed) == expected_groups
            and candidate_roles(sealed) == expected_roles
        )
        inherited_ok = inherited_ok and matches
        observations[case_id] = {
            "terminal": prop["terminal"],
            "basis_groups": [list(group) for group in candidate_groups(sealed)],
            "roles": candidate_roles(sealed),
            "oracle_match": matches,
        }

    checks["inherited_current_cal_phase2_controls"] = inherited_ok
    checks["deterministic_repeat"] = deterministic

    sp10 = audit(cases["SP-10-alt-joint-mixed"])
    sp11 = audit(cases["SP-11-symmetric-alt-joint-mixed"])
    target10 = norm_groups(oracles["SP-10-alt-joint-mixed"]["propositions"][0]["msc"])
    target11 = norm_groups(oracles["SP-11-symmetric-alt-joint-mixed"]["propositions"][0]["msc"])
    checks["exact_alt_joint_basis"] = derive_basis_passage_ids(cases["SP-10-alt-joint-mixed"], sp10) == target10
    checks["exact_symmetric_alt_joint_basis"] = derive_basis_passage_ids(cases["SP-11-symmetric-alt-joint-mixed"], sp11) == target11
    checks["weak_flat_control_killed"] = weak_flat_groups(sp10) != target10 and weak_flat_groups(sp11) != target11

    event_support = event_context("Alice reviewed dossier before Bob archived dossier.", "event-support")
    event_refute = event_context("Alice reviewed dossier after Bob archived dossier.", "event-refute")
    event_scope = event_context("Report says Alice reviewed dossier before Bob archived dossier.", "event-scope")
    es = validate_candidate(candidate, resolver, event_support, audit(event_support))
    er = validate_candidate(candidate, resolver, event_refute, audit(event_refute))
    en = validate_candidate(candidate, resolver, event_scope, audit(event_scope))
    checks["event_order_family_controls"] = (
        es["propositions"][0]["terminal"] == {"verdict": "supported", "reason": "categorical_support"}
        and candidate_groups(es) == (("E1",),)
        and er["propositions"][0]["terminal"] == {"verdict": "contradicted", "reason": "categorical_refutation"}
        and candidate_groups(er) == (("E1",),)
        and en["propositions"][0]["terminal"] == {"verdict": "not_checkable", "reason": "no_deciding_relation"}
        and candidate_groups(en) == ()
        and candidate_roles(en)["E1"] == ("non_polarized", "residual")
    )

    unsupported = unsupported_context()
    unsupported_result = audit(unsupported)
    unsupported_obj = validate_candidate(candidate, resolver, unsupported, unsupported_result)
    unsupported_prop = unsupported_obj["propositions"][0]
    checks["unsupported_exact_cal_result_preserved"] = (
        unsupported_result.conclusion is Conclusion.NOT_CHECKABLE
        and unsupported_result.failure_code is FailureCode.UNSUPPORTED_SEMANTIC_FAMILY
        and unsupported_prop["terminal"]
        == {"verdict": "not_checkable", "reason": "UNSUPPORTED_SEMANTIC_FAMILY"}
        and unsupported_prop["basis_groups"] == []
        and all(
            row["relation"] == "non_polarized" and row["role"] == "residual"
            for row in unsupported_prop["participants"]
        )
    )
    observations["unsupported_family"] = {
        "cal_terminal": list(public_terminal_state(unsupported_result)),
        "candidate_terminal": unsupported_prop["terminal"],
        "participants": unsupported_prop["participants"],
        "basis_groups": unsupported_prop["basis_groups"],
        "result_set_id": unsupported_obj["result_set_id"],
        "whole_object_sha256": candidate.whole_object_sha256(unsupported_obj),
    }

    alias_unsealed = materialize_unsealed(unsupported, unsupported_result, semantic_implementation_sha=CAL)
    alias_unsealed["propositions"][0]["terminal"]["reason"] = "no_deciding_relation"
    alias_obj = candidate.seal(alias_unsealed)
    candidate.validate_object(alias_obj)
    checks["weak_reason_alias_control_killed"] = (
        alias_obj["propositions"][0]["terminal"] != unsupported_prop["terminal"]
        and alias_obj["result_set_id"] != unsupported_obj["result_set_id"]
        and candidate.whole_object_sha256(alias_obj) != candidate.whole_object_sha256(unsupported_obj)
    )

    # Exact Candidate A RC1 remains the predecessor discriminator.
    rc1 = load_module(
        "candidate_a_rc1_predecessor",
        apparatus_root
        / "research"
        / "contract_c_successor_candidate_a_rc1_20260913"
        / "candidate_a_rc1.py",
    )
    predecessor = json.loads(json.dumps(unsupported_obj))
    predecessor.pop("result_set_id")
    predecessor["profile"] = rc1.PROFILE
    predecessor = rc1.seal(predecessor)
    rc1_rejected = False
    try:
        rc1.validate_object(predecessor)
    except Exception:
        rc1_rejected = True
    checks["rc1_predecessor_discriminator_preserved"] = rc1_rejected

    required = [
        "inherited_current_cal_phase2_controls",
        "deterministic_repeat",
        "exact_alt_joint_basis",
        "exact_symmetric_alt_joint_basis",
        "weak_flat_control_killed",
        "event_order_family_controls",
        "unsupported_exact_cal_result_preserved",
        "weak_reason_alias_control_killed",
        "rc1_predecessor_discriminator_preserved",
    ]
    failures = [name for name in required if not checks[name]]
    disposition = "SUPPORTED_RC2_PRODUCER_CONFORMANCE" if not failures else "FALSIFIED"
    return {
        "schema": "contract-c-candidate-a-rc2-producer-conformance-rc1-result-v1",
        "research_disposition": disposition,
        "cal_authority": CAL,
        "apparatus_candidate": APPARATUS_RC2,
        "checks": checks,
        "failures": failures,
        "observations": observations,
        "interpretation": {
            "basis_groups_derived_without_new_semantic_judgment": all(
                checks[name]
                for name in [
                    "inherited_current_cal_phase2_controls",
                    "exact_alt_joint_basis",
                    "exact_symmetric_alt_joint_basis",
                ]
            ),
            "unsupported_family_preserved_without_relabelling": checks["unsupported_exact_cal_result_preserved"],
            "producer_gate_satisfied": disposition == "SUPPORTED_RC2_PRODUCER_CONFORMANCE",
            "independent_consumer_gate_satisfied": False,
            "production_promotion_authorized": False,
            "official_contract_c_version_assigned": False,
        },
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: evaluate.py <apparatus-root> <output-json>")
    result = evaluate(Path(sys.argv[1]))
    output = Path(sys.argv[2])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
