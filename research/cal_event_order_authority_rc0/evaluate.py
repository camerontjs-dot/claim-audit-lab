"""Decisive evaluator for CAL Event-Ordering Authority RC0."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable

from research.cal_measurement_envelope_rc0.envelope import (
    AdmittedPassage,
    AuditContext,
    MeasurementReceipt,
    measure_passage,
    proposal_spans,
)
from research.cal_event_order_authority_rc0 import candidate

EVENT_HEAD = "e8d33913db66ad21027dffdf731d50f7a0977c8f"
EVENT_BLOB = "3e29b0e2ec5d9ba2d873d1584e76635147e421aa"
EVENT_PATH = "research/event_ordering_measurement_rc7fc/event_order.py"
RC8J_HEAD = "8e75c6782bb95c3763d06230b9c5df2b6af44054"
RC8J_BLOBS = {
    "research/semantic_authority_machinery_rc8/authority_contract_rc8j.py": "f55156e43e0c1b4a7868bc8339585b8892edda38",
    "research/semantic_authority_machinery_rc8/authority_contract_rc8h.py": "4b872e455d52d7a682bb719889860d2cac7909a7",
    "research/semantic_authority_machinery_rc8/authority_contract_rc8f.py": "efc50481be3179332cecb449c3c9c91da7c3dfaa",
    "research/semantic_authority_machinery_rc8/authority_contract_rc8d.py": "f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1",
    "research/semantic_authority_machinery_rc8/authority_contract_rc8b.py": "edf84bb5aae0dd217e3f780e7a49767440b7c1e5",
}
CANDIDATE_FREEZE = "634837fe368accbd9add2c9483dfff6722f5dfc7"
CANDIDATE_BLOBS = {
    "research/cal_event_order_authority_rc0/event_authority.py": "88df954235069e98582e731f48e46e5b257da93f",
    "research/cal_event_order_authority_rc0/candidate.py": "36a8d1fbd9e52ec743757f750f744ad4553b5698",
    "research/cal_measurement_envelope_rc0/envelope.py": "f8ce6362f6ccc165cdad29f314721bb26a21f871",
}
SCHEMA = "cal-event-order-authority-rc0-evaluation-v1"


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def _require_dependency(root: Path, head: str, blobs: dict[str, str]) -> None:
    observed = _git(root, "rev-parse", "HEAD")
    if observed != head:
        raise RuntimeError(f"dependency head mismatch: {observed} != {head}")
    for path, expected in blobs.items():
        actual = _git(root, "hash-object", path)
        if actual != expected:
            raise RuntimeError(f"dependency blob mismatch {path}: {actual} != {expected}")


def _require_candidate_blobs(root: Path) -> None:
    for path, expected in CANDIDATE_BLOBS.items():
        actual = _git(root, "hash-object", path)
        if actual != expected:
            raise RuntimeError(f"frozen candidate blob drift {path}: {actual} != {expected}")


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _sha(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _context(case_id: str, text: str) -> AuditContext:
    return AuditContext.create(
        audit_id=f"CAL-EVENT-AUTHORITY-{case_id}",
        original_claim_id=f"ROOT-{case_id}",
        original_claim_text=text,
        proposition_id=f"PROP-{case_id}",
        proposition_payload={
            "family": "event_ordering",
            "claim_text": text,
            "research_scope": "direct_event_order_atom_authority",
        },
        decomposition_path=(f"ROOT-{case_id}", f"PROP-{case_id}"),
        contract_b_version="1.2.0",
        bundle_id=f"bundle-{case_id.casefold()}",
        bundle_hash=_sha(f"bundle:{case_id}:{text}"),
        admitted_passages=(
            AdmittedPassage(
                source_id=f"source-{case_id.casefold()}",
                passage_id=f"passage-{case_id.casefold()}",
                passage_sha256=_sha(text),
                passage_text=text,
            ),
        ),
    )


def _measure(event_module: Any, context: AuditContext) -> MeasurementReceipt:
    passage_id = context.admitted_passage_ids[0]
    return measure_passage(
        context=context,
        passage_id=passage_id,
        instrument_id=candidate.EVENT_INSTRUMENT_ID,
        instrument_version=str(event_module.VERSION),
        semantic_family=candidate.EVENT_FAMILY,
        measure_fn=event_module.measure,
    )


def _mutated_receipt(
    *, context: AuditContext, original: MeasurementReceipt, mutate: Callable[[dict[str, Any]], None]
) -> MeasurementReceipt:
    raw = deepcopy(original.raw_measurement)
    mutate(raw)
    passage_id = context.admitted_passage_ids[0]
    return MeasurementReceipt.create(
        context=context,
        instrument_id=original.instrument_id,
        instrument_version=original.instrument_version,
        semantic_family=original.semantic_family,
        measurement_status=str(raw.get("status")),
        consumed_passage_ids=(passage_id,),
        raw_measurement=raw,
        consumed_spans=proposal_spans(passage_id=passage_id, raw_measurement=raw),
    )


def _rc8j(root: Path, case: dict[str, Any]) -> dict[str, Any]:
    code = (
        "import json,sys; "
        "from research.semantic_authority_machinery_rc8.authority_contract_rc8j import assess_authority; "
        "case=json.load(sys.stdin); json.dump(assess_authority(case),sys.stdout,sort_keys=True)"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root)
    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=root,
        env=env,
        input=json.dumps(case, sort_keys=True),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"RC8J execution failed: {proc.stderr or proc.stdout}")
    value = json.loads(proc.stdout)
    if not isinstance(value, dict):
        raise RuntimeError("RC8J returned non-object")
    return value


def _is_warranted(observation: dict[str, Any]) -> bool:
    return observation == {
        "authority_status": "WARRANTED",
        "reason": candidate.WARRANTED_REASON,
    }


def _completion_observation(
    *, context: AuditContext, receipt: MeasurementReceipt, rc8j_root: Path
) -> dict[str, Any]:
    passage_id = context.admitted_passage_ids[0]
    try:
        atom = candidate.complete_event_order_atom(
            context=context,
            receipt=receipt,
            passage_id=passage_id,
        )
    except candidate.EventAuthorityRefusal as exc:
        return {
            "completion": "REFUSED",
            "refusal_code": exc.code,
            "detail": exc.detail,
            "authority_observation": None,
            "warranted": False,
        }
    case = candidate.build_rc8j_case(atom=atom)
    observation = _rc8j(rc8j_root, case)
    return {
        "completion": "COMPLETED",
        "atom_id": atom.atom_id,
        "fields": atom.fields,
        "field_spans": {key: list(value) for key, value in atom.field_spans.items()},
        "authority_observation": observation,
        "warranted": _is_warranted(observation),
    }


def _semantic_mutations(
    *, context: AuditContext, receipt: MeasurementReceipt, rc8j_root: Path
) -> dict[str, dict[str, Any]]:
    mutations: dict[str, Callable[[dict[str, Any]], None]] = {
        "relation_before_to_after": lambda raw: raw["proposals"][0].__setitem__("relation", "AFTER"),
        "left_subject": lambda raw: raw["proposals"][0]["left_event"].__setitem__("subject", "mallory"),
        "right_object": lambda raw: raw["proposals"][0]["right_event"].__setitem__("object", "other dossier"),
        "left_polarity": lambda raw: raw["proposals"][0]["left_event"].__setitem__("polarity", "negative"),
        "right_polarity": lambda raw: raw["proposals"][0]["right_event"].__setitem__("polarity", "negative"),
        "stale_cue_span": lambda raw: raw["proposals"][0].__setitem__("span", [0, 5]),
        "swap_events": lambda raw: raw["proposals"][0].update(
            {
                "left_event": deepcopy(raw["proposals"][0]["right_event"]),
                "right_event": deepcopy(raw["proposals"][0]["left_event"]),
            }
        ),
    }
    rows: dict[str, dict[str, Any]] = {}
    for name, mutate in mutations.items():
        mutated = _mutated_receipt(context=context, original=receipt, mutate=mutate)
        rows[name] = _completion_observation(
            context=context,
            receipt=mutated,
            rc8j_root=rc8j_root,
        )
    return rows


def _binding_mutations(valid_case: dict[str, Any], rc8j_root: Path) -> dict[str, Any]:
    mutations: dict[str, Callable[[dict[str, Any]], None]] = {
        "foreign_source_identity": lambda case: case.__setitem__("raw_source_id", "FOREIGN-SOURCE"),
        "foreign_bundle_identity": lambda case: case.__setitem__("raw_bundle_id", "FOREIGN-BUNDLE"),
        "foreign_passage_identity": lambda case: case.__setitem__("raw_passage_id", "FOREIGN-PASSAGE"),
        "foreign_claim_identity": lambda case: case.__setitem__("raw_claim_id", "FOREIGN-CLAIM"),
        "atom_id_substitution": lambda case: case.__setitem__("target_atom_id", "event-atom:foreign"),
        "field_span_outside_admission": lambda case: case["field_warrants"]["left_subject"].__setitem__("span", [-1, 0]),
        "field_value_mismatch": lambda case: case["field_warrants"]["left_subject"].__setitem__("value", "mallory"),
        "operator_domain_mismatch": lambda case: case["operator"].__setitem__("domain", "comparison"),
        "evidence_not_admitted": lambda case: case.__setitem__("evidence_admitted", False),
    }
    rows: dict[str, Any] = {}
    for name, mutate in mutations.items():
        case = deepcopy(valid_case)
        mutate(case)
        observed = _rc8j(rc8j_root, case)
        rows[name] = {
            "authority_observation": observed,
            "warranted": _is_warranted(observed),
        }
    return rows


def execute(*, repo_root: Path, event_root: Path, rc8j_root: Path, cohort_path: Path) -> dict[str, Any]:
    _require_candidate_blobs(repo_root)
    _require_dependency(event_root, EVENT_HEAD, {EVENT_PATH: EVENT_BLOB})
    _require_dependency(rc8j_root, RC8J_HEAD, RC8J_BLOBS)
    event = _load_module("cal_event_authority_frozen_rc7fc", event_root / EVENT_PATH)

    cohort = json.loads(cohort_path.read_text(encoding="utf-8"))
    if cohort.get("candidate_freeze_before_cohort") != CANDIDATE_FREEZE:
        raise RuntimeError("cohort does not bind the frozen candidate")

    positive_rows: dict[str, Any] = {}
    positive_cases: list[tuple[AuditContext, MeasurementReceipt, dict[str, Any]]] = []
    setup_valid = True
    positive_failures = 0
    for row in cohort["positive_controls"]:
        context = _context(str(row["case_id"]), str(row["source"]))
        receipt = _measure(event, context)
        if receipt.measurement_status != "CLAIMED":
            setup_valid = False
        observed = _completion_observation(
            context=context,
            receipt=receipt,
            rc8j_root=rc8j_root,
        )
        if not observed["warranted"]:
            positive_failures += 1
        positive_rows[str(row["case_id"])] = {
            "measurement_status": receipt.measurement_status,
            "measurement_receipt_id": receipt.receipt_id,
            **observed,
        }
        if observed["completion"] == "COMPLETED":
            atom = candidate.complete_event_order_atom(
                context=context,
                receipt=receipt,
                passage_id=context.admitted_passage_ids[0],
            )
            positive_cases.append((context, receipt, candidate.build_rc8j_case(atom=atom)))

    if not positive_cases:
        raise RuntimeError("no valid positive case available for mutation controls")
    base_context, base_receipt, base_case = positive_cases[0]

    # Weak control: recompute a content-valid measurement receipt whose semantic relation
    # is caller-mutated, then let the weak constructor copy those values into warrants.
    weak_mutated_receipt = _mutated_receipt(
        context=base_context,
        original=base_receipt,
        mutate=lambda raw: raw["proposals"][0].__setitem__("relation", "AFTER"),
    )
    weak_case = candidate.weak_caller_stipulated_case(
        context=base_context,
        receipt=weak_mutated_receipt,
        passage_id=base_context.admitted_passage_ids[0],
    )
    weak_observation = _rc8j(rc8j_root, weak_case)
    weak_control_valid = _is_warranted(weak_observation)

    semantic_mutations = _semantic_mutations(
        context=base_context,
        receipt=base_receipt,
        rc8j_root=rc8j_root,
    )
    semantic_completion_leaks = sum(
        result["completion"] != "REFUSED" for result in semantic_mutations.values()
    )
    semantic_unsafe_warrants = sum(
        bool(result["warranted"]) for result in semantic_mutations.values()
    )

    direct_rows: dict[str, Any] = {}
    direct_failures = 0
    for row in cohort["direct_assertion_falsifiers"]:
        context = _context(str(row["case_id"]), str(row["source"]))
        receipt = _measure(event, context)
        expected_measurement = str(row["measurement_expected"])
        if receipt.measurement_status != expected_measurement:
            setup_valid = False
        observed = _completion_observation(
            context=context,
            receipt=receipt,
            rc8j_root=rc8j_root,
        )
        expected_refusal = str(row["candidate_expected"])
        candidate_pass = (
            observed["completion"] == "REFUSED"
            and observed.get("refusal_code") == expected_refusal
        )
        if not candidate_pass:
            direct_failures += 1
        direct_rows[str(row["case_id"])] = {
            "measurement_status": receipt.measurement_status,
            "expected_measurement_status": expected_measurement,
            "candidate_expected": expected_refusal,
            "candidate_pass": candidate_pass,
            **observed,
        }

    binding_mutations = _binding_mutations(base_case, rc8j_root)
    binding_unsafe_warrants = sum(
        bool(row["warranted"]) for row in binding_mutations.values()
    )

    unsafe_warranted_mutations = (
        semantic_unsafe_warrants + binding_unsafe_warrants
        + sum(bool(row["warranted"]) for row in direct_rows.values())
    )

    if not setup_valid:
        disposition = "INCONCLUSIVE_SETUP_INVALID"
    elif not weak_control_valid:
        disposition = "INCONCLUSIVE_WEAK_CONTROL_NOT_DISCRIMINATING"
    elif (
        positive_failures
        or semantic_completion_leaks
        or direct_failures
        or binding_unsafe_warrants
        or unsafe_warranted_mutations
    ):
        disposition = "FALSIFIED_EVENT_ORDER_AUTHORITY_CANDIDATE"
    else:
        disposition = "SUPPORTED_WITH_BOUNDS"

    return {
        "schema": SCHEMA,
        "research_disposition": disposition,
        "candidate_freeze": CANDIDATE_FREEZE,
        "setup_valid": setup_valid,
        "dependencies": {
            "event_order_measurement": {"head": EVENT_HEAD, "blob": EVENT_BLOB},
            "rc8j": {"head": RC8J_HEAD, "blobs": RC8J_BLOBS},
        },
        "weak_control": {
            "description": "caller-mutated BEFORE->AFTER proposal copied directly into matching broad-span field warrants",
            "authority_observation": weak_observation,
            "control_valid": weak_control_valid,
        },
        "positive_controls": positive_rows,
        "semantic_measurement_mutations": semantic_mutations,
        "direct_assertion_falsifiers": direct_rows,
        "rc8j_binding_mutations": binding_mutations,
        "summary": {
            "positive_failures": positive_failures,
            "semantic_completion_leaks": semantic_completion_leaks,
            "semantic_unsafe_warrants": semantic_unsafe_warrants,
            "direct_assertion_failures": direct_failures,
            "binding_unsafe_warrants": binding_unsafe_warrants,
            "unsafe_warranted_mutations": unsafe_warranted_mutations,
        },
        "interpretation": {
            "event_order_measurement_is_authority": False,
            "rc8j_parses_source_language": False,
            "proposition_relative_temporal_relation_established": False,
            "released_cal_v1_causal_role": False,
            "production_promotion_authorized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--event-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = execute(
        repo_root=args.repo_root.resolve(),
        event_root=args.event_root.resolve(),
        rc8j_root=args.rc8j_root.resolve(),
        cohort_path=args.cohort.resolve(),
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({
        "research_disposition": result["research_disposition"],
        "weak_control_valid": result["weak_control"]["control_valid"],
        **result["summary"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
