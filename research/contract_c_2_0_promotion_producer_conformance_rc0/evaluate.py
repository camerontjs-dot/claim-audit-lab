from __future__ import annotations

import copy
import hashlib
import importlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path
from types import ModuleType
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
    POLICY_RESOLVER_COMMIT,
    POLICY_SHA256,
    derive_basis_passage_ids,
    materialize_unsealed,
    public_terminal_state,
)

CAL = "a902621e8baea3063dddd7f92ba975aade305464"
APPARATUS_PROMOTION = "b42c827acb0a9fe65353354d709add0e27bab307"
REFERENCE_RC1_BLOB = "03dbb5b774af523d8e6235bca86b18af5ddad5b0"
REFERENCE_RC2_BLOB = "ad5ed3ac71a8f8680188beb363c9d952c9922b15"
WIRE_PROFILE = "contract-c-successor-candidate-a-rc2-research"
PUBLIC_VERSION = "2.0.0"

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
        text_sha256=_hex(SUPPORT_A),
    )
    return AuditContext(SUPPORT_A, proposition, world)


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
    return AuditContext(
        "Alice reviewed dossier before Bob archived dossier.", proposition, world
    )


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


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_frozen_reference(apparatus_root: Path) -> ModuleType:
    reference = apparatus_root / "schema" / "contract-c" / "2.0.0" / "reference"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        rc1_dir = root / "research" / "contract_c_successor_candidate_a_rc1_20260913"
        rc2_dir = root / "research" / "contract_c_successor_candidate_a_rc2_20260913"
        rc1_dir.mkdir(parents=True)
        rc2_dir.mkdir(parents=True)
        shutil.copyfile(reference / "candidate_a_rc1.py", rc1_dir / "candidate_a_rc1.py")
        shutil.copyfile(reference / "candidate_a_rc2.py", rc2_dir / "candidate_a_rc2.py")
        return _load_module("c2_promotion_frozen_rc2", rc2_dir / "candidate_a_rc2.py")


def _load_production(apparatus_root: Path) -> ModuleType:
    sys.path.insert(0, str(apparatus_root))
    try:
        return importlib.import_module("validators.contract_c_v2")
    finally:
        sys.path.pop(0)


def _groups(sealed: dict[str, Any]) -> tuple[tuple[str, ...], ...]:
    groups = sealed["propositions"][0]["basis_groups"]
    return tuple(
        sorted(
            tuple(sorted(ref["passage_id"] for ref in group))
            for group in groups
        )
    )


def _roles(sealed: dict[str, Any]) -> dict[str, tuple[str, str]]:
    return {
        row["evidence_ref"]["passage_id"]: (row["relation"], row["role"])
        for row in sealed["propositions"][0]["participants"]
    }


def _weak_flat_groups(result: Any) -> tuple[tuple[str, ...], ...]:
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


def _resolver_entries() -> list[dict[str, str]]:
    return [
        {
            "semantic_implementation_sha": CAL,
            "policy_sha256": POLICY_SHA256,
        }
    ]


def _validate_production(
    prod: ModuleType,
    context: AuditContext,
    result: Any,
) -> dict[str, Any]:
    unsealed = materialize_unsealed(
        context,
        result,
        semantic_implementation_sha=CAL,
    )
    sealed = prod.seal(unsealed)
    prod.validate_object(sealed)
    prod.verify_contract_b_references(
        sealed,
        exact_contract_b=unsealed["contract_b"],
        evidence_index={
            (passage.source_id, passage.passage_id)
            for passage in context.evidence_world.admitted_passages
        },
    )
    prod.verify_policy_resolution(
        sealed,
        independently_selected_resolver_commit_sha=POLICY_RESOLVER_COMMIT,
        resolver_entries=_resolver_entries(),
    )
    prod.verify_external_authority(
        sealed,
        expected_whole_object_sha256=prod.whole_object_sha256(sealed),
    )
    return sealed


def evaluate(apparatus_root: Path) -> dict[str, Any]:
    prod = _load_production(apparatus_root)
    frozen = _load_frozen_reference(apparatus_root)

    global_versions = json.loads(
        (apparatus_root / "schema" / "contract-c" / "versions.json").read_text()
    )
    candidate_version = json.loads(
        (
            apparatus_root
            / "schema"
            / "contract-c"
            / "2.0.0"
            / "promotion-version.json"
        ).read_text()
    )

    cases: dict[str, AuditContext] = {
        "single_support": strict_context([("S1", SUPPORT_A)], "single-support"),
        "single_refutation": strict_context([("R1", REFUTE)], "single-refutation"),
        "two_independent_supports": strict_context(
            [("S1", SUPPORT_A), ("S2", SUPPORT_B)], "two-supports"
        ),
        "support_neutral": strict_context(
            [("S1", SUPPORT_A), ("N1", IRRELEVANT)], "support-neutral"
        ),
        "minimal_mixed": strict_context(
            [("S1", SUPPORT_A), ("R1", REFUTE)], "minimal-mixed"
        ),
        "alternative_joint": strict_context(
            [("S1", SUPPORT_A), ("S2", SUPPORT_B), ("R1", REFUTE)],
            "alternative-joint",
        ),
        "symmetric_alternative_joint": strict_context(
            [("S1", SUPPORT_A), ("R1", REFUTE), ("R2", REFUTE)],
            "symmetric-alternative-joint",
        ),
        "four_way_mixed": strict_context(
            [
                ("S1", SUPPORT_A),
                ("S2", SUPPORT_B),
                ("R1", REFUTE),
                ("R2", REFUTE),
            ],
            "four-way-mixed",
        ),
        "no_deciding": strict_context([("N1", IRRELEVANT)], "no-deciding"),
        "event_support": event_context(
            "Alice reviewed dossier before Bob archived dossier.", "event-support"
        ),
        "event_refute": event_context(
            "Alice reviewed dossier after Bob archived dossier.", "event-refute"
        ),
        "event_scope": event_context(
            "Report says Alice reviewed dossier before Bob archived dossier.",
            "event-scope",
        ),
        "unsupported_family": unsupported_context(),
    }

    checks: dict[str, bool] = {}
    observations: dict[str, Any] = {}
    all_equivalent = True
    all_terminal = True
    all_basis = True
    all_deterministic = True

    for case_id, context in cases.items():
        result = audit(context)
        unsealed = materialize_unsealed(context, result, semantic_implementation_sha=CAL)
        prod_obj = _validate_production(prod, context, result)
        frozen_obj = frozen.seal(unsealed)
        frozen.validate_object(frozen_obj)

        expected_groups = derive_basis_passage_ids(context, result)
        equivalent = (
            prod_obj == frozen_obj
            and prod.canonical_bytes(prod_obj) == frozen.canonical_bytes(frozen_obj)
            and prod.whole_object_sha256(prod_obj)
            == frozen.whole_object_sha256(frozen_obj)
            and prod_obj["result_set_id"] == frozen_obj["result_set_id"]
        )
        terminal_ok = prod_obj["propositions"][0]["terminal"] == {
            "verdict": public_terminal_state(result)[0],
            "reason": public_terminal_state(result)[1],
        }
        basis_ok = _groups(prod_obj) == expected_groups
        repeat = _validate_production(prod, context, result)
        deterministic = prod.canonical_bytes(repeat) == prod.canonical_bytes(prod_obj)

        all_equivalent = all_equivalent and equivalent
        all_terminal = all_terminal and terminal_ok
        all_basis = all_basis and basis_ok
        all_deterministic = all_deterministic and deterministic
        observations[case_id] = {
            "terminal": prod_obj["propositions"][0]["terminal"],
            "basis_groups": [list(group) for group in _groups(prod_obj)],
            "roles": _roles(prod_obj),
            "production_reference_equivalent": equivalent,
            "terminal_matches_cal": terminal_ok,
            "basis_matches_compose_only_derivation": basis_ok,
            "deterministic_repeat": deterministic,
            "result_set_id": prod_obj["result_set_id"],
            "whole_object_sha256": prod.whole_object_sha256(prod_obj),
        }

    checks["all_cases_production_reference_equivalent"] = all_equivalent
    checks["all_terminals_match_cal"] = all_terminal
    checks["all_basis_groups_match_compose_only_derivation"] = all_basis
    checks["all_cases_deterministic"] = all_deterministic

    alt_result = audit(cases["alternative_joint"])
    alt_groups = derive_basis_passage_ids(cases["alternative_joint"], alt_result)
    sym_result = audit(cases["symmetric_alternative_joint"])
    sym_groups = derive_basis_passage_ids(cases["symmetric_alternative_joint"], sym_result)
    checks["weak_flat_control_killed"] = (
        _weak_flat_groups(alt_result) != alt_groups
        and _weak_flat_groups(sym_result) != sym_groups
    )

    unsupported = cases["unsupported_family"]
    unsupported_result = audit(unsupported)
    unsupported_obj = _validate_production(prod, unsupported, unsupported_result)
    alias_unsealed = materialize_unsealed(
        unsupported,
        unsupported_result,
        semantic_implementation_sha=CAL,
    )
    alias_unsealed["propositions"][0]["terminal"]["reason"] = "no_deciding_relation"
    alias_obj = prod.seal(alias_unsealed)
    prod.validate_object(alias_obj)
    checks["unsupported_reason_not_aliased"] = (
        unsupported_obj["propositions"][0]["terminal"]["reason"]
        == "UNSUPPORTED_SEMANTIC_FAMILY"
        and unsupported_obj["propositions"][0]["basis_groups"] == []
        and all(
            row["relation"] == "non_polarized" and row["role"] == "residual"
            for row in unsupported_obj["propositions"][0]["participants"]
        )
        and unsupported_obj["result_set_id"] != alias_obj["result_set_id"]
        and prod.whole_object_sha256(unsupported_obj)
        != prod.whole_object_sha256(alias_obj)
    )

    checks["production_identity_constants_exact"] = (
        prod.CONTRACT_C_VERSION == PUBLIC_VERSION
        and prod.WIRE_PROFILE == WIRE_PROFILE
        and prod.PROFILE == WIRE_PROFILE
        and prod.POLICY_RESOLVER_FIXTURE_COMMIT == POLICY_RESOLVER_COMMIT
        and prod.CAL_RC1_IMPLEMENTATION == CAL
        and prod.CAL_RC1_POLICY_SHA256 == POLICY_SHA256
    )
    checks["premerge_global_discovery_remains_c1"] = global_versions == {
        "canonical_version": "1.0.0",
        "supported_versions": ["1.0.0"],
    }
    checks["candidate_version_is_noncanonical_c2"] = (
        candidate_version.get("candidate_compatibility_version") == PUBLIC_VERSION
        and candidate_version.get("wire_profile") == WIRE_PROFILE
        and candidate_version.get("base_canonical_version") == "1.0.0"
        and candidate_version.get("canonical_registry_switch_authorized") is False
    )

    required = [
        "all_cases_production_reference_equivalent",
        "all_terminals_match_cal",
        "all_basis_groups_match_compose_only_derivation",
        "all_cases_deterministic",
        "weak_flat_control_killed",
        "unsupported_reason_not_aliased",
        "production_identity_constants_exact",
        "premerge_global_discovery_remains_c1",
        "candidate_version_is_noncanonical_c2",
    ]
    failures = [name for name in required if not checks[name]]
    disposition = (
        "SUPPORTED_C2_PROMOTION_PRODUCER_CONFORMANCE" if not failures else "FALSIFIED"
    )
    return {
        "schema": "contract-c-2.0-promotion-producer-conformance-rc0-result-v1",
        "research_disposition": disposition,
        "cal_authority": CAL,
        "apparatus_promotion_head": APPARATUS_PROMOTION,
        "checks": checks,
        "failures": failures,
        "observations": observations,
        "interpretation": {
            "unchanged_materializer_preserved": True,
            "new_cal_semantic_judgment_required": False if not failures else None,
            "production_adapter_matches_frozen_rc2": all_equivalent,
            "producer_gate_satisfied": not failures,
            "independent_consumer_gate_satisfied_against_production_head": False,
            "contract_c_2_released": False,
            "production_promotion_merge_authorized": False,
        },
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: evaluate.py <apparatus-root> <output-json>")
    result = evaluate(Path(sys.argv[1]).resolve())
    output = Path(sys.argv[2])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["research_disposition"] != "SUPPORTED_C2_PROMOTION_PRODUCER_CONFORMANCE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
