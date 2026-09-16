from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

from claim_audit_lab.production_v1 import SEMANTIC_IMPLEMENTATION_SHA
from claim_audit_lab.production_v1.semantic.engine import audit
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    Conclusion,
    EvidenceWorld,
    FailureCode,
    SemanticFamily,
    TypedProposition,
)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from materialize import (  # noqa: E402
    POLICY,
    POLICY_SHA256,
    derive_basis_passage_ids,
    materialize_unsealed,
    public_terminal_state,
)

CURRENT_CAL = "847cc970642bb648dc994b929c2053b5c9d4648c"
OLD_CAL = "a902621e8baea3063dddd7f92ba975aade305464"
OLD_RESOLVER_COMMIT = "43b571464734325277374ee81098553fb7c1b944"
C2_HEAD = "b42c827acb0a9fe65353354d709add0e27bab307"
POLICY_PROJECTION_BLOB = "9bc152275759304be03b84014c56bd434549a64a"

SUPPORT_A = "Women had a higher rate than Men."
SUPPORT_B = "Women had a greater rate than Men."
REFUTE_A = "Women had a lower rate than Men."
REFUTE_B = "Women had a smaller rate than Men."
IRRELEVANT = "Cats had a higher rate than Dogs."


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return "sha256:" + _hex(value)


def _policy_digest(value: dict[str, Any]) -> str:
    raw = (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode()
    return hashlib.sha256(raw).hexdigest()


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


def event_context(
    rows: list[tuple[str, str]],
    label: str,
    *,
    left_polarity: str = "positive",
) -> AuditContext:
    passages = tuple(
        AdmittedPassage.create(pid, f"src-{pid.lower()}", text) for pid, text in rows
    )
    world = EvidenceWorld.create(
        "1.2.0",
        f"bundle-{label}",
        _tagged(f"bundle-{label}"),
        passages,
        _aperture(label),
    )
    claim = (
        "Alice did not review dossier before Bob archived dossier."
        if left_polarity == "negative"
        else "Alice reviewed dossier before Bob archived dossier."
    )
    proposition = TypedProposition.create(
        "QE1",
        SemanticFamily.DIRECT_EVENT_ORDER,
        {
            "left_subject": "alice",
            "left_predicate": "review",
            "left_object": "dossier",
            "left_polarity": left_polarity,
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
        "QU1",
        SemanticFamily.PERMISSION_EXCEPTION,
        {"actor": "alice"},
        text_sha256=_hex(text),
    )
    return AuditContext(text, proposition, world)


def _load_c2(apparatus_root: Path):
    if apparatus_root.name == "":
        raise RuntimeError("invalid apparatus root")
    sys.path.insert(0, str(apparatus_root))
    try:
        return importlib.import_module("validators.contract_c_v2")
    finally:
        sys.path.pop(0)


def _resolver(resolver_root: Path) -> dict[str, Any]:
    path = resolver_root / "research/contract_c_successor_ground_up_20260913/PHASE_1_5_POLICY_RESOLVER.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _groups(value: dict[str, Any]) -> tuple[tuple[str, ...], ...]:
    return tuple(
        sorted(
            tuple(sorted(ref["passage_id"] for ref in group))
            for group in value["propositions"][0]["basis_groups"]
        )
    )


def _roles(value: dict[str, Any]) -> dict[str, tuple[str, str]]:
    return {
        row["evidence_ref"]["passage_id"]: (row["relation"], row["role"])
        for row in value["propositions"][0]["participants"]
    }


def _assert_raises(fn, label: str) -> str:
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 - deliberate cross-boundary negative control
        return f"{type(exc).__name__}: {exc}"
    raise AssertionError(f"negative control unexpectedly succeeded: {label}")


def evaluate(apparatus_root: Path, resolver_root: Path, materializer_blob: str) -> dict[str, Any]:
    if SEMANTIC_IMPLEMENTATION_SHA != CURRENT_CAL:
        raise AssertionError(
            f"current CAL runtime identity drift: {SEMANTIC_IMPLEMENTATION_SHA} != {CURRENT_CAL}"
        )
    c2 = _load_c2(apparatus_root)
    resolver = _resolver(resolver_root)
    entries = resolver["entries"]
    if len(entries) != 1:
        raise AssertionError("old immutable resolver fixture cardinality drift")
    old = entries[0]
    if old["semantic_implementation_sha"] != OLD_CAL:
        raise AssertionError("old resolver semantic implementation drift")
    if old["policy_sha256"] != POLICY_SHA256 or old["policy"] != POLICY:
        raise AssertionError("current policy payload differs from frozen resolver policy")
    if old["projection_blob"] != POLICY_PROJECTION_BLOB:
        raise AssertionError("old policy projection provenance drift")
    if _policy_digest(POLICY) != POLICY_SHA256:
        raise AssertionError("canonical current policy digest mismatch")

    cases: dict[str, AuditContext] = {
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
            left_polarity="negative",
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

    expected_groups = {
        "strict_support": (("S1",),),
        "strict_refutation": (("R1",),),
        "two_supports": (("S1",), ("S2",)),
        "support_irrelevant": (("S1",),),
        "minimal_mixed": (("R1", "S1"),),
        "alternative_joint": (("R1", "S1"), ("R1", "S2")),
        "symmetric_alternative_joint": (("R1", "S1"), ("R2", "S1")),
        "four_way_mixed": (("R1", "S1"), ("R1", "S2"), ("R2", "S1"), ("R2", "S2")),
        "irrelevant_only": (),
        "measurement_not_applicable": (),
        "event_support": (("E1",),),
        "event_refutation": (("E1",),),
        "negative_event_unresolved": (("E1",),),
        "support_plus_unresolved": (("E2",),),
        "unsupported_family": (),
    }

    observations: dict[str, Any] = {}
    failures: list[str] = []
    sealed_by_case: dict[str, dict[str, Any]] = {}

    for case_id, context in cases.items():
        try:
            result = audit(context)
            unsealed = materialize_unsealed(
                context,
                result,
                semantic_implementation_sha=CURRENT_CAL,
                policy_resolver_commit_sha=OLD_RESOLVER_COMMIT,
            )
            sealed = c2.seal(unsealed)
            c2.validate_object(sealed)
            c2.verify_contract_b_references(
                sealed,
                exact_contract_b=unsealed["contract_b"],
                evidence_index={
                    (passage.source_id, passage.passage_id)
                    for passage in context.evidence_world.admitted_passages
                },
            )
            repeat = c2.seal(
                materialize_unsealed(
                    context,
                    result,
                    semantic_implementation_sha=CURRENT_CAL,
                    policy_resolver_commit_sha=OLD_RESOLVER_COMMIT,
                )
            )
            if c2.canonical_bytes(repeat) != c2.canonical_bytes(sealed):
                raise AssertionError("deterministic repeat differs")
            if sealed["producer"]["semantic_implementation_sha"] != CURRENT_CAL:
                raise AssertionError("producer identity drift")
            if sealed["producer"]["policy_sha256"] != POLICY_SHA256:
                raise AssertionError("policy digest drift")
            terminal = sealed["propositions"][0]["terminal"]
            expected_terminal = {
                "verdict": public_terminal_state(result)[0],
                "reason": public_terminal_state(result)[1],
            }
            if terminal != expected_terminal:
                raise AssertionError(f"terminal mismatch {terminal} != {expected_terminal}")
            derived_groups = derive_basis_passage_ids(context, result)
            if _groups(sealed) != derived_groups:
                raise AssertionError("sealed basis differs from compose-only derivation")
            if case_id in expected_groups and _groups(sealed) != expected_groups[case_id]:
                raise AssertionError(
                    f"known basis mismatch {_groups(sealed)} != {expected_groups[case_id]}"
                )
            participant_ids = [
                row["evidence_ref"]["passage_id"]
                for row in sealed["propositions"][0]["participants"]
            ]
            trace_ids = [trace.passage_id for trace in result.traces]
            if sorted(participant_ids) != sorted(trace_ids) or len(participant_ids) != len(set(participant_ids)):
                raise AssertionError("retained participation mismatch")
            roles = _roles(sealed)
            causal = {pid for group in _groups(sealed) for pid in group}
            if {pid for pid, (_, role) in roles.items() if role == "causal"} != causal:
                raise AssertionError("causal partition mismatch")
            permuted = copy.deepcopy(sealed)
            permuted["propositions"][0]["participants"].reverse()
            permuted["propositions"][0]["basis_groups"].reverse()
            for group in permuted["propositions"][0]["basis_groups"]:
                group.reverse()
            if c2.canonical_bytes(permuted) != c2.canonical_bytes(sealed):
                raise AssertionError("unordered permutation changed canonical bytes")
            sealed_by_case[case_id] = sealed
            observations[case_id] = {
                "cal_conclusion": result.conclusion.value,
                "cal_failure_code": None if result.failure_code is None else result.failure_code.value,
                "public_terminal": terminal,
                "basis_groups": [list(group) for group in _groups(sealed)],
                "roles": roles,
                "result_set_id": sealed["result_set_id"],
                "whole_object_sha256": c2.whole_object_sha256(sealed),
                "deterministic_repeat": True,
                "canonical_permutation_invariant": True,
            }
        except Exception as exc:  # noqa: BLE001 - terminal experiment record
            failures.append(f"{case_id}: {type(exc).__name__}: {exc}")

    negative_controls: dict[str, str] = {}
    if sealed_by_case:
        sample_id = "strict_support"
        sample = sealed_by_case[sample_id]
        sample_context = cases[sample_id]
        sample_result = audit(sample_context)

        negative_controls["old_resolver_rejects_current_cal"] = _assert_raises(
            lambda: c2.verify_policy_resolution(
                sample,
                independently_selected_resolver_commit_sha=OLD_RESOLVER_COMMIT,
                resolver_entries=entries,
            ),
            "old resolver accepted current CAL",
        )

        duplicate = copy.deepcopy(sample)
        duplicate["propositions"][0]["participants"].append(
            copy.deepcopy(duplicate["propositions"][0]["participants"][0])
        )
        duplicate = c2.seal(duplicate)
        negative_controls["duplicate_participant_rejected"] = _assert_raises(
            lambda: c2.validate_object(duplicate), "duplicate participant"
        )

        if sample["propositions"][0]["basis_groups"]:
            duplicate_basis = copy.deepcopy(sample)
            duplicate_basis["propositions"][0]["basis_groups"].append(
                copy.deepcopy(duplicate_basis["propositions"][0]["basis_groups"][0])
            )
            duplicate_basis = c2.seal(duplicate_basis)
            negative_controls["duplicate_basis_group_rejected"] = _assert_raises(
                lambda: c2.validate_object(duplicate_basis), "duplicate basis group"
            )

        stale_ref = copy.deepcopy(sample)
        stale_ref["propositions"][0]["participants"][0]["evidence_ref"]["passage_id"] = "missing"
        for group in stale_ref["propositions"][0]["basis_groups"]:
            for ref in group:
                if ref["passage_id"] == "S1":
                    ref["passage_id"] = "missing"
        stale_ref = c2.seal(stale_ref)
        negative_controls["stale_contract_b_reference_rejected"] = _assert_raises(
            lambda: c2.verify_contract_b_references(
                stale_ref,
                exact_contract_b=sample["contract_b"],
                evidence_index={
                    (passage.source_id, passage.passage_id)
                    for passage in sample_context.evidence_world.admitted_passages
                },
            ),
            "stale Contract B reference",
        )

        other_context = cases["strict_refutation"]
        negative_controls["context_result_mismatch_rejected"] = _assert_raises(
            lambda: materialize_unsealed(
                other_context,
                sample_result,
                semantic_implementation_sha=CURRENT_CAL,
                policy_resolver_commit_sha=OLD_RESOLVER_COMMIT,
            ),
            "context/result mismatch",
        )

    required_case_count = 16
    classification = (
        "SUPPORTED_FOR_APPARATUS_RESOLVER_SUCCESSOR_QUALIFICATION"
        if not failures
        and len(observations) == required_case_count
        and "old_resolver_rejects_current_cal" in negative_controls
        else "FALSIFIED_CURRENT_CAL_TO_C2_PROJECTION"
    )

    proposal = None
    if classification == "SUPPORTED_FOR_APPARATUS_RESOLVER_SUCCESSOR_QUALIFICATION":
        proposal = {
            "schema": "contract-c-policy-resolver-successor-row-proposal-v1",
            "not_authority": True,
            "semantic_implementation_sha": CURRENT_CAL,
            "policy_sha256": POLICY_SHA256,
            "policy": POLICY,
            "prior_policy_projection_blob": POLICY_PROJECTION_BLOB,
            "current_c2_materializer_blob": materializer_blob,
            "required_independent_owner": "camerontjs-dot/apparatus-contracts",
        }

    return {
        "schema": "current-cal-contract-c2-producer-conformance-rc0-result-v1",
        "classification": classification,
        "authorities": {
            "current_cal": CURRENT_CAL,
            "contract_c2_head": C2_HEAD,
            "old_resolver_commit": OLD_RESOLVER_COMMIT,
            "old_resolver_cal": OLD_CAL,
            "policy_sha256": POLICY_SHA256,
            "materializer_blob": materializer_blob,
        },
        "observations": observations,
        "negative_controls": negative_controls,
        "failures": failures,
        "resolver_successor_row_proposal": proposal,
        "nonclaims": [
            "No independent resolver authority is established by this CAL-side experiment.",
            "No Contract C2 release or promotion is authorized.",
            "No Decision, Contract E, Authorization, or execution claim is established.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apparatus", type=Path, required=True)
    parser.add_argument("--resolver", type=Path, required=True)
    parser.add_argument("--materializer-blob", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    result = evaluate(args.apparatus.resolve(), args.resolver.resolve(), args.materializer_blob)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"classification": result["classification"], "failures": result["failures"]}, sort_keys=True))
    return 0 if result["classification"] == "SUPPORTED_FOR_APPARATUS_RESOLVER_SUCCESSOR_QUALIFICATION" else 1


if __name__ == "__main__":
    raise SystemExit(main())
