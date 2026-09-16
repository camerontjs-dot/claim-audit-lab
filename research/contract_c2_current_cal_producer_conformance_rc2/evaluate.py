from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from claim_audit_lab.production_v1 import SEMANTIC_IMPLEMENTATION_SHA
from claim_audit_lab.production_v1.semantic.engine import audit
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)

CURRENT_CAL = "847cc970642bb648dc994b929c2053b5c9d4648c"
NEW_RESOLVER = "1d33e0612befcf8016816197c90c062373796df9"
OLD_RESOLVER = "43b571464734325277374ee81098553fb7c1b944"
POLICY_SHA256 = "44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c"
CURRENT_PROJECTION = "ef32fa4fca52a2bb7fe2896b378f9b6fdef0dfde"

SUPPORT_A = "Women had a higher rate than Men."
SUPPORT_B = "Women had a greater rate than Men."
REFUTE_A = "Women had a lower rate than Men."
REFUTE_B = "Women had a smaller rate than Men."
IRRELEVANT = "Cats had a higher rate than Dogs."

HERE = Path(__file__).resolve().parent
RC1_MATERIALIZER = HERE.parent / "contract_c2_current_cal_producer_conformance_rc1/materialize.py"


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
        AdmittedPassage.create(pid, f"src-{pid.lower()}", text) for pid, text in rows
    )
    world = EvidenceWorld.create(
        "1.2.0", f"bundle-{label}", _tagged(f"bundle-{label}"), passages, _aperture(label)
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


def event_context(rows: list[tuple[str, str]], label: str) -> AuditContext:
    passages = tuple(
        AdmittedPassage.create(pid, f"src-{pid.lower()}", text) for pid, text in rows
    )
    world = EvidenceWorld.create(
        "1.2.0", f"bundle-{label}", _tagged(f"bundle-{label}"), passages, _aperture(label)
    )
    claim = "Alice reviewed dossier before Bob archived dossier."
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
        text_sha256=_hex(claim),
    )
    return AuditContext(claim, proposition, world)


def unsupported_context() -> AuditContext:
    text = "Alice may release dossier."
    passage = AdmittedPassage.create("U1", "src-u1", text)
    world = EvidenceWorld.create(
        "1.2.0", "bundle-unsupported", _tagged("bundle-unsupported"), (passage,), _aperture("unsupported")
    )
    proposition = TypedProposition.create(
        "QU1", SemanticFamily.PERMISSION_EXCEPTION, {"actor": "alice"}, text_sha256=_hex(text)
    )
    return AuditContext(text, proposition, world)


def _cases() -> dict[str, AuditContext]:
    return {
        "strict_support": strict_context([("S1", SUPPORT_A)], "strict-support"),
        "strict_refutation": strict_context([("R1", REFUTE_A)], "strict-refutation"),
        "two_supports": strict_context([("S1", SUPPORT_A), ("S2", SUPPORT_B)], "two-supports"),
        "support_irrelevant": strict_context([("S1", SUPPORT_A), ("N1", IRRELEVANT)], "support-irrelevant"),
        "minimal_mixed": strict_context([("S1", SUPPORT_A), ("R1", REFUTE_A)], "minimal-mixed"),
        "alternative_joint": strict_context(
            [("S1", SUPPORT_A), ("S2", SUPPORT_B), ("R1", REFUTE_A)], "alternative-joint"
        ),
        "symmetric_alternative_joint": strict_context(
            [("S1", SUPPORT_A), ("R1", REFUTE_A), ("R2", REFUTE_B)], "symmetric-alternative-joint"
        ),
        "four_way_mixed": strict_context(
            [("S1", SUPPORT_A), ("S2", SUPPORT_B), ("R1", REFUTE_A), ("R2", REFUTE_B)],
            "four-way-mixed",
        ),
        "irrelevant_only": strict_context([("N1", IRRELEVANT)], "irrelevant-only"),
        "measurement_not_applicable": strict_context(
            [("N1", "The report describes annual enrollment totals.")], "measurement-not-applicable"
        ),
        "event_support": event_context(
            [("E1", "Alice reviewed dossier before Bob archived dossier.")], "event-support"
        ),
        "event_refutation": event_context(
            [("E1", "Alice reviewed dossier after Bob archived dossier.")], "event-refutation"
        ),
        "negative_event_unresolved": event_context(
            [("E1", "Alice did not review dossier before Bob archived dossier.")],
            "negative-event-unresolved",
        ),
        "support_plus_unresolved": event_context(
            [
                ("E1", "Alice reviewed dossier before Bob archived dossier."),
                ("E2", "Alice did not review dossier before Bob archived dossier."),
            ],
            "support-plus-unresolved",
        ),
        "event_scope_stress": event_context(
            [("E1", "Report says Alice reviewed dossier before Bob archived dossier.")],
            "event-scope-stress",
        ),
        "unsupported_family": unsupported_context(),
    }


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_c2(root: Path) -> ModuleType:
    sys.path.insert(0, str(root))
    try:
        return importlib.import_module("validators.contract_c_v2")
    finally:
        sys.path.pop(0)


def _reject(fn, label: str) -> str:
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 - deliberate negative boundary
        return f"{type(exc).__name__}: {exc}"
    raise AssertionError(f"negative control unexpectedly succeeded: {label}")


def _without_resolver_identity(value: dict[str, Any]) -> dict[str, Any]:
    x = copy.deepcopy(value)
    x.pop("result_set_id", None)
    x["producer"].pop("policy_resolver_commit_sha", None)
    return x


def evaluate(c2_root: Path, resolver_root: Path) -> dict[str, Any]:
    if SEMANTIC_IMPLEMENTATION_SHA != CURRENT_CAL:
        raise AssertionError("CAL semantic implementation identity drift")
    c2 = _load_c2(c2_root)
    materialize = _load_module("current_cal_c2_rc1_materializer", RC1_MATERIALIZER)
    if materialize.SEMANTIC_IMPLEMENTATION_SHA != CURRENT_CAL:
        raise AssertionError("materializer semantic authority drift")

    resolver = json.loads(
        (
            resolver_root
            / "research/contract_c2_current_cal_resolver_successor_rc0/RESOLVER.json"
        ).read_text(encoding="utf-8")
    )
    entries = resolver["entries"]
    current = [row for row in entries if row["semantic_implementation_sha"] == CURRENT_CAL]
    if len(current) != 1:
        raise AssertionError("independent resolver missing exact current CAL row")
    current_row = current[0]
    if current_row["policy_sha256"] != POLICY_SHA256:
        raise AssertionError("resolver current policy digest mismatch")
    if current_row["projection_blob"] != CURRENT_PROJECTION:
        raise AssertionError("resolver current projection blob mismatch")

    observations: dict[str, Any] = {}
    sealed_current: dict[str, dict[str, Any]] = {}
    failures: list[str] = []
    for case_id, context in _cases().items():
        try:
            result = audit(context)
            predecessor_unsealed = materialize.materialize_unsealed(
                context, result, policy_resolver_commit_sha=OLD_RESOLVER
            )
            current_unsealed = materialize.materialize_unsealed(
                context, result, policy_resolver_commit_sha=NEW_RESOLVER
            )
            predecessor = c2.seal(predecessor_unsealed)
            sealed = c2.seal(current_unsealed)
            c2.validate_object(sealed)
            c2.verify_contract_b_references(
                sealed,
                exact_contract_b=current_unsealed["contract_b"],
                evidence_index={
                    (passage.source_id, passage.passage_id)
                    for passage in context.evidence_world.admitted_passages
                },
            )
            resolved = c2.verify_policy_resolution(
                sealed,
                independently_selected_resolver_commit_sha=NEW_RESOLVER,
                resolver_entries=entries,
            )
            if resolved != current_row:
                raise AssertionError("resolver returned a non-current row")
            if _without_resolver_identity(predecessor) != _without_resolver_identity(sealed):
                raise AssertionError("semantic/public C2 content changed beyond resolver identity")
            repeat = c2.seal(
                materialize.materialize_unsealed(
                    context, result, policy_resolver_commit_sha=NEW_RESOLVER
                )
            )
            if c2.canonical_bytes(repeat) != c2.canonical_bytes(sealed):
                raise AssertionError("deterministic repeat mismatch")
            if sealed["producer"] != {
                "semantic_implementation_sha": CURRENT_CAL,
                "policy_sha256": POLICY_SHA256,
                "policy_resolver_commit_sha": NEW_RESOLVER,
            }:
                raise AssertionError("producer authority tuple mismatch")
            sealed_current[case_id] = sealed
            observations[case_id] = {
                "terminal": sealed["propositions"][0]["terminal"],
                "basis_groups": sealed["propositions"][0]["basis_groups"],
                "result_set_id": sealed["result_set_id"],
                "whole_object_sha256": c2.whole_object_sha256(sealed),
                "semantic_content_unchanged_from_predecessor_resolver": True,
                "deterministic_repeat": True,
            }
        except Exception as exc:  # noqa: BLE001 - terminal experiment record
            failures.append(f"{case_id}: {type(exc).__name__}: {exc}")

    negative: dict[str, str] = {}
    if "strict_support" in sealed_current:
        sample = sealed_current["strict_support"]
        sample_context = _cases()["strict_support"]
        sample_result = audit(sample_context)

        old_commit_object = c2.seal(
            materialize.materialize_unsealed(
                sample_context, sample_result, policy_resolver_commit_sha=OLD_RESOLVER
            )
        )
        negative["predecessor_resolver_commit_substitution_rejected"] = _reject(
            lambda: c2.verify_policy_resolution(
                old_commit_object,
                independently_selected_resolver_commit_sha=NEW_RESOLVER,
                resolver_entries=entries,
            ),
            "predecessor resolver commit substituted",
        )

        without_current = [row for row in entries if row["semantic_implementation_sha"] != CURRENT_CAL]
        negative["missing_current_row_rejected"] = _reject(
            lambda: c2.verify_policy_resolution(
                sample,
                independently_selected_resolver_commit_sha=NEW_RESOLVER,
                resolver_entries=without_current,
            ),
            "missing current resolver row",
        )

        wrong_policy = copy.deepcopy(sample)
        wrong_policy["producer"]["policy_sha256"] = "0" * 64
        wrong_policy = c2.seal(wrong_policy)
        negative["wrong_policy_digest_rejected"] = _reject(
            lambda: c2.verify_policy_resolution(
                wrong_policy,
                independently_selected_resolver_commit_sha=NEW_RESOLVER,
                resolver_entries=entries,
            ),
            "wrong policy digest",
        )

        negative["caller_semantic_identity_selection_rejected"] = _reject(
            lambda: materialize.materialize_unsealed(
                sample_context,
                sample_result,
                policy_resolver_commit_sha=NEW_RESOLVER,
                semantic_implementation_sha="a902621e8baea3063dddd7f92ba975aade305464",
            ),
            "caller semantic identity selection",
        )

    classification = (
        "SUPPORTED_CURRENT_CAL_TO_C2_WITH_RESOLVER_AUTHORITY"
        if not failures and len(observations) == 16 and len(negative) == 4
        else "FALSIFIED_CURRENT_CAL_TO_C2_AUTHORITY_BINDING"
    )
    return {
        "schema": "current-cal-contract-c2-producer-conformance-rc2-result-v1",
        "classification": classification,
        "semantic_implementation_sha": CURRENT_CAL,
        "resolver_authority": NEW_RESOLVER,
        "predecessor_resolver": OLD_RESOLVER,
        "policy_sha256": POLICY_SHA256,
        "materializer_blob": CURRENT_PROJECTION,
        "observations": observations,
        "negative_controls": negative,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--c2", type=Path, required=True)
    parser.add_argument("--resolver", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(args.c2.resolve(), args.resolver.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"classification": result["classification"], "failures": result["failures"]}, sort_keys=True))
    return 0 if result["classification"] == "SUPPORTED_CURRENT_CAL_TO_C2_WITH_RESOLVER_AUTHORITY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
