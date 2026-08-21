"""Run frozen Simple Logic Gold direct facts through the current CAL v1 pipeline.

This is a DEV diagnostic runner. It reads frozen construction gold but never
changes it, never tunes CAL, and keeps named-missing-material cases out of a
false relation-equivalence score because direct CAL input has no retrieval-gap
control channel. Parent results are explicitly atom-derived diagnostics, not a
claim that CAL natively decomposed or audited a parent claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.models import AuditRequest, Passage
from claim_audit_lab.v1.runner import run_default_audit

_FREEZE_SCHEMA = "simple-logic-gold-frozen-dev-v0.1"
_FREEZE_STATUS = "frozen_approved_dev_not_validation_or_gate_evidence"
_ATOM_RELATIONS = {"supports", "refutes", "insufficient", "retrieval_gap"}
_OPERATORS = {"single", "all_of"}


def _sha256_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _required_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"frozen artifact {field} must be a non-empty string")
    return value


def _load_frozen(frozen_path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw_bytes = frozen_path.read_bytes()
        frozen = json.loads(raw_bytes)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load frozen Simple Logic Gold: {exc}") from exc
    if not isinstance(frozen, dict):
        raise ValueError("frozen Simple Logic Gold artifact must be a mapping")
    _validate_frozen(frozen)
    return frozen, _sha256_bytes(raw_bytes)


def _validate_frozen(frozen: dict[str, Any]) -> None:
    if frozen.get("schema_version") != _FREEZE_SCHEMA:
        raise ValueError("direct lane requires a frozen Simple Logic Gold artifact")
    if frozen.get("status") != _FREEZE_STATUS:
        raise ValueError("frozen artifact has an invalid DEV-only status")
    _required_string(frozen.get("freeze_version"), "freeze_version")
    _required_string(frozen.get("freeze_identifier"), "freeze_identifier")
    for field in ("manifest_version", "manifest_sha256", "derived_gold_sha256"):
        _required_string(frozen.get(field), field)
    cases = frozen.get("frozen_cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("frozen artifact frozen_cases must be a non-empty list")
    if frozen.get("world_count") != len(cases):
        raise ValueError("frozen artifact world_count does not match frozen_cases")

    atom_counts: Counter[str] = Counter()
    parent_counts: Counter[str] = Counter()
    case_ids: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("every frozen case must be a mapping")
        case_id = _required_string(case.get("base_case_id"), "base_case_id")
        if case_id in case_ids:
            raise ValueError("frozen artifact base_case_id values must be unique")
        case_ids.add(case_id)
        if case.get("operator") not in _OPERATORS:
            raise ValueError(f"{case_id}: frozen operator is invalid")
        facts = case.get("facts")
        if not isinstance(facts, list) or not facts:
            raise ValueError(f"{case_id}: frozen facts must be a non-empty list")
        fact_ids: set[str] = set()
        for fact in facts:
            if not isinstance(fact, dict):
                raise ValueError(f"{case_id}: frozen facts must be mappings")
            fact_id = _required_string(fact.get("fact_id"), "fact_id")
            if fact_id in fact_ids:
                raise ValueError(f"{case_id}: frozen fact_id values must be unique")
            fact_ids.add(fact_id)
            _required_string(fact.get("text"), "fact text")
        atoms = case.get("atoms")
        if not isinstance(atoms, list) or not atoms:
            raise ValueError(f"{case_id}: frozen atoms must be a non-empty list")
        atom_ids: set[str] = set()
        relations: list[str] = []
        for atom in atoms:
            if not isinstance(atom, dict):
                raise ValueError(f"{case_id}: frozen atoms must be mappings")
            atom_id = _required_string(atom.get("atom_id"), "atom_id")
            if atom_id in atom_ids:
                raise ValueError(f"{case_id}: frozen atom_id values must be unique")
            atom_ids.add(atom_id)
            _required_string(atom.get("claim"), "atom claim")
            relation = atom.get("relation")
            if relation not in _ATOM_RELATIONS:
                raise ValueError(f"{case_id}: frozen atom relation is invalid")
            relations.append(relation)
            atom_counts[relation] += 1
        expected_parent = _atom_parent_verdict(case["operator"], relations)
        if case.get("parent_verdict") != expected_parent:
            raise ValueError(f"{case_id}: frozen parent_verdict does not match atoms/operator")
        parent_counts[expected_parent] += 1
    if frozen.get("atom_relation_counts") != dict(sorted(atom_counts.items())):
        raise ValueError("frozen artifact atom_relation_counts do not match frozen atoms")
    if frozen.get("parent_verdict_counts") != dict(sorted(parent_counts.items())):
        raise ValueError("frozen artifact parent_verdict_counts do not match frozen cases")


def run_direct_lane(
    frozen_path: Path,
    *,
    config_loader: Callable[[], Any] = load_default_audit_config,
    audit_runner: Callable[[AuditRequest], Any] = run_default_audit,
) -> dict[str, Any]:
    """Run direct atom diagnostics, with injectable dependencies for portable tests."""
    frozen, frozen_file_sha256 = _load_frozen(frozen_path)
    config = config_loader()
    atoms: list[dict[str, Any]] = []
    parents: list[dict[str, Any]] = []
    for case in frozen["frozen_cases"]:
        passages = [
            Passage(
                passage_id=fact["fact_id"],
                text=fact["text"],
                source_meta={"direct_logic_gold": "true", "base_case_id": case["base_case_id"]},
            )
            for fact in case["facts"]
        ]
        case_atoms: list[dict[str, Any]] = []
        for atom in case["atoms"]:
            trace = audit_runner(
                AuditRequest(
                    claim_id=atom["atom_id"],
                    claim_text=atom["claim"],
                    passages=passages,
                    audit_config=config,
                )
            )
            observed = _map_cal_verdict(trace.verdict.support_verdict)
            comparable = atom["relation"] != "retrieval_gap"
            record = {
                "base_case_id": case["base_case_id"],
                "atom_id": atom["atom_id"],
                "expected_relation": atom["relation"],
                "cal_support_verdict": trace.verdict.support_verdict,
                "cal_support_verdict_reason": trace.verdict.support_verdict_reason,
                "cal_flags": trace.verdict.audit_flags,
                "cal_observed_relation": observed,
                "comparable": comparable,
                "match": observed == atom["relation"] if comparable else None,
                "defect_route": _defect_route(atom["relation"], observed, comparable),
                "trace": trace.model_dump(mode="json"),
            }
            atoms.append(record)
            case_atoms.append(record)
        parents.append(_parent_diagnostic(case, case_atoms))
    return {
        "schema_version": "simple-logic-gold-direct-cal-run-v0.2",
        "label": "DEV diagnostic only; not validation, representative accuracy, or gate evidence",
        "frozen_freeze_version": frozen["freeze_version"],
        "frozen_freeze_identifier": frozen["freeze_identifier"],
        "frozen_file_sha256": frozen_file_sha256,
        "frozen_manifest_version": frozen["manifest_version"],
        "frozen_manifest_sha256": frozen["manifest_sha256"],
        "frozen_derived_gold_sha256": frozen["derived_gold_sha256"],
        "cal_audit_config_hash": atoms[0]["trace"]["audit_config_hash"] if atoms else None,
        "atoms": atoms,
        "atom_derived_parent_diagnostics": parents,
        "summary": {
            "atoms": len(atoms),
            "comparable_atoms": sum(atom["comparable"] for atom in atoms),
            "matching_comparable_atoms": sum(atom["match"] is True for atom in atoms),
            "named_missing_material_noncomparable": sum(not atom["comparable"] for atom in atoms),
            "parents": len(parents),
            "comparable_atom_derived_parents": sum(parent["comparable"] for parent in parents),
            "matching_atom_derived_parents": sum(parent["match"] is True for parent in parents),
            "noncomparable_atom_derived_parents": sum(
                not parent["comparable"] for parent in parents
            ),
        },
    }


def _atom_parent_verdict(operator: str, relations: list[str]) -> str:
    if operator == "single":
        return {
            "supports": "supported",
            "refutes": "contradicted",
            "insufficient": "not_checkable",
            "retrieval_gap": "pending",
        }[relations[0]]
    if "refutes" in relations:
        return "contradicted"
    if "retrieval_gap" in relations:
        return "pending"
    if all(relation == "supports" for relation in relations):
        return "supported"
    if all(relation == "insufficient" for relation in relations):
        return "not_checkable"
    return "partially_supported"


def _parent_diagnostic(case: dict[str, Any], atoms: list[dict[str, Any]]) -> dict[str, Any]:
    observed_relations = [atom["cal_observed_relation"] for atom in atoms]
    has_retrieval_gap = any(atom["expected_relation"] == "retrieval_gap" for atom in atoms)
    has_unmapped = any(relation is None for relation in observed_relations)
    comparable = not has_retrieval_gap and not has_unmapped
    mapped_relations = [relation for relation in observed_relations if relation]
    observed_parent = (
        _atom_parent_verdict(case["operator"], mapped_relations) if comparable else None
    )
    return {
        "base_case_id": case["base_case_id"],
        "operator": case["operator"],
        "expected_parent_verdict": case["parent_verdict"],
        "cal_observed_atom_relations": observed_relations,
        "atom_derived_cal_parent_verdict": observed_parent,
        "comparable": comparable,
        "match": observed_parent == case["parent_verdict"] if comparable else None,
        "label": (
            "atom-derived parent diagnostic; CAL did not natively decompose or audit this parent"
        ),
        "noncomparable_reason": (
            "named missing material is not relation-comparable in direct CAL input"
            if has_retrieval_gap
            else "one or more CAL support degrees have no declared atom-relation mapping"
            if has_unmapped
            else None
        ),
    }


def _map_cal_verdict(verdict: str) -> str | None:
    return {
        "supported": "supports",
        "contradicted": "refutes",
        "not_checkable": "insufficient",
    }.get(verdict)


def _defect_route(expected: str, observed: str | None, comparable: bool) -> str:
    if not comparable:
        return "availability semantics are intentionally not comparable in direct CAL input"
    if observed == expected:
        return "no mismatch"
    return "inspect atom relation, NLI, rule, aggregation, and trace evidence without tuning gold"


def _write_absent_or_identical(path: Path, output: dict[str, Any]) -> None:
    text = json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise FileExistsError(f"refusing to overwrite non-identical direct-lane output: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        output = run_direct_lane(args.frozen)
        _write_absent_or_identical(args.out, output)
    except (FileExistsError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(output["summary"], sort_keys=True))


if __name__ == "__main__":
    _main()
