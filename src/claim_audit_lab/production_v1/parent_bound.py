"""Production-shaped CAL V1 parent recomposition and frozen Contract C handoff.

This module deliberately does not own Contract C semantics.  It runs already-qualified
CAL child audits, uses the exact frozen DecompositionComposer, and requires external
Apparatus checkouts at the pinned Contract C candidate, RC2 authority, and resolver
commits before it can emit a parent-bound Contract C object.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from claim_audit_lab.production_v1 import DISTRIBUTION_VERSION, SEMANTIC_IMPLEMENTATION_SHA
from claim_audit_lab.production_v1.bundle_input import prepare_contract_b_input
from claim_audit_lab.production_v1.execution import run_contract_b_bundle
from claim_audit_lab.production_v1.semantic.decomposition import (
    BoundAuditOutcome,
    DecompositionDeclaration,
    DecompositionRefusal,
    DecompositionResult,
    DecompositionState,
    PropositionRef,
    recompose,
)
from claim_audit_lab.production_v1.semantic.models import Conclusion

CONTRACT_C_FREEZE_COMMIT = "c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec"
CONTRACT_C_CANDIDATE_PATH = (
    "research/contract_c_cal_v1_parent_recomposition_rc0_20260919/candidate_rc0.py"
)
CONTRACT_C_CANDIDATE_BLOB = "df6b6ed410f52cafaeadfe1578d770f480a34b09"
CONTRACT_C_PROFILE = "contract-c-cal-v1-parent-recomposition-rc0"

RC2_AUTHORITY_COMMIT = "b42c827acb0a9fe65353354d709add0e27bab307"
RC2_VALIDATOR_PATH = "validators/contract_c_rc2.py"
RC2_VALIDATOR_BLOB = "1d2ecd228cde807138013c33c8675c3003421d3c"

RESOLVER_AUTHORITY_COMMIT = "1d33e0612befcf8016816197c90c062373796df9"
RESOLVER_PATH = "research/contract_c2_current_cal_resolver_successor_rc0/RESOLVER.json"
RESOLVER_BLOB = "1a408246fd3bef0758a958ae716b44ea74bc0689"

CAL_FREEZE_COMMIT = "e24e405f5336ee024674f39dba97255bb58a2dd9"
CAL_SEMANTIC_SOURCE_COMMIT = "7cf0d2e50562ec4ce4082d1e1c058a11025b1a48"
POLICY_SHA256 = "44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c"
POLICY_RESOLVER_COMMIT = RESOLVER_AUTHORITY_COMMIT

_PARENT_RESULT_SCHEMA = "cal-v1-parent-result-v1"
_PARENT_MANIFEST_SCHEMA = "cal-v1-parent-bound-manifest-v1"


class ParentBoundPipelineError(ValueError):
    """Raised when the production-shaped parent path cannot preserve exact authority."""


@dataclass(frozen=True, slots=True)
class NativeChild:
    proposition_id: str
    result_bytes: bytes
    result_record: dict[str, Any]
    outcome: BoundAuditOutcome


@dataclass(frozen=True, slots=True)
class ParentBoundBuild:
    parent: DecompositionResult
    children: tuple[NativeChild, ...]
    contract_c_object: dict[str, Any]
    contract_c_bytes: bytes
    contract_c_sha256: str
    recomposition_authority: dict[str, Any]


def _tagged_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _git_text(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise ParentBoundPipelineError(f"git authority check failed: {detail}")
    return result.stdout.strip()


def _verify_checkout(
    root: Path,
    *,
    expected_head: str,
    required_blobs: Mapping[str, str],
    label: str,
) -> None:
    if _git_text(root, "rev-parse", "HEAD") != expected_head:
        raise ParentBoundPipelineError(f"{label} checkout is not exact pinned authority")
    if _git_text(root, "status", "--porcelain") != "":
        raise ParentBoundPipelineError(f"{label} checkout must be clean")
    for path, blob in required_blobs.items():
        if _git_text(root, "rev-parse", f"HEAD:{path}") != blob:
            raise ParentBoundPipelineError(f"{label} blob mismatch: {path}")


def verify_external_authorities(
    *,
    contract_c_root: Path,
    rc2_root: Path,
    resolver_root: Path,
) -> None:
    _verify_checkout(
        contract_c_root,
        expected_head=CONTRACT_C_FREEZE_COMMIT,
        required_blobs={CONTRACT_C_CANDIDATE_PATH: CONTRACT_C_CANDIDATE_BLOB},
        label="Contract C freeze",
    )
    _verify_checkout(
        rc2_root,
        expected_head=RC2_AUTHORITY_COMMIT,
        required_blobs={RC2_VALIDATOR_PATH: RC2_VALIDATOR_BLOB},
        label="Contract C RC2",
    )
    _verify_checkout(
        resolver_root,
        expected_head=RESOLVER_AUTHORITY_COMMIT,
        required_blobs={RESOLVER_PATH: RESOLVER_BLOB},
        label="Contract C resolver",
    )


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ParentBoundPipelineError(f"cannot load exact authority module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_rc2_package(rc2_root: Path) -> ModuleType:
    package_name = "_cal_contract_c_rc2_authority"
    module_name = f"{package_name}.contract_c_rc2"
    package = ModuleType(package_name)
    package.__path__ = [str(rc2_root / "validators")]  # type: ignore[attr-defined]
    package.__package__ = package_name
    sys.modules[package_name] = package
    return _load_module(rc2_root / RC2_VALIDATOR_PATH, module_name)


def _load_authority_modules(
    *,
    contract_c_root: Path,
    rc2_root: Path,
) -> tuple[ModuleType, ModuleType]:
    candidate = _load_module(
        contract_c_root / CONTRACT_C_CANDIDATE_PATH,
        "cal_v1_parent_bound_contract_c_candidate",
    )
    rc2 = _load_rc2_package(rc2_root)
    if getattr(candidate, "PROFILE", None) != CONTRACT_C_PROFILE:
        raise ParentBoundPipelineError("Contract C candidate profile mismatch")
    if getattr(candidate, "CAL_SEMANTIC_IMPLEMENTATION", None) != SEMANTIC_IMPLEMENTATION_SHA:
        raise ParentBoundPipelineError("Contract C candidate CAL semantic identity mismatch")
    if getattr(candidate, "CAL_FREEZE_COMMIT", None) != CAL_FREEZE_COMMIT:
        raise ParentBoundPipelineError("Contract C candidate CAL freeze identity mismatch")
    if getattr(candidate, "CAL_SEMANTIC_SOURCE_COMMIT", None) != CAL_SEMANTIC_SOURCE_COMMIT:
        raise ParentBoundPipelineError("Contract C candidate semantic source mismatch")
    if getattr(candidate, "POLICY_RESOLVER_COMMIT", None) != POLICY_RESOLVER_COMMIT:
        raise ParentBoundPipelineError("Contract C candidate resolver identity mismatch")
    return candidate, rc2


def _declaration(contract_a: Mapping[str, Any]) -> DecompositionDeclaration:
    try:
        root = contract_a["root_proposition"]
        decomposition = contract_a["decomposition"]
    except KeyError as exc:
        raise ParentBoundPipelineError(f"Contract A missing parent binding: {exc}") from exc
    if not isinstance(root, dict) or not isinstance(decomposition, dict):
        raise ParentBoundPipelineError("Contract A root/decomposition must be objects")
    if decomposition.get("state") != "declared":
        raise ParentBoundPipelineError(\n            "parent-bound Contract C path is qualified only for declared decomposition"\n        )
    children = decomposition.get("children")
    if not isinstance(children, list):
        raise ParentBoundPipelineError("Contract A decomposition children must be a list")
    try:
        declaration = DecompositionDeclaration(
            root=PropositionRef(
                str(root["proposition_id"]),
                str(root["text_sha256"]),
            ),
            state=DecompositionState.DECLARED,
            decomposition_id=str(decomposition["decomposition_id"]),
            operator=str(decomposition["operator"]),
            children=tuple(
                PropositionRef(
                    str(row["proposition_id"]),
                    str(row["text_sha256"]),
                    int(row["sequence"]),
                )
                for row in children
            ),
        )
        declaration.verify()
    except (KeyError, TypeError, ValueError, DecompositionRefusal) as exc:
        raise ParentBoundPipelineError(f"Contract A decomposition refused: {exc}") from exc
    return declaration


def _child_row(declaration: DecompositionDeclaration, proposition_id: str) -> PropositionRef:
    for row in declaration.children:
        if row.proposition_id == proposition_id:
            return row
    raise ParentBoundPipelineError(\n        f"native CAL child is not declared by Contract A: {proposition_id}"\n    )


def _native_child(
    declaration: DecompositionDeclaration,
    result_bytes: bytes,
) -> NativeChild:
    try:
        record = json.loads(result_bytes)
        proposition = record["proposition"]
        result = record["result"]
        proposition_id = str(proposition["proposition_id"])
        native_text_sha = str(proposition["text_sha256"])
        conclusion = Conclusion(str(result["conclusion"]))
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ParentBoundPipelineError(f"invalid native CAL child result: {exc}") from exc

    child = _child_row(declaration, proposition_id)
    if child.text_sha256 != "sha256:" + native_text_sha:
        raise ParentBoundPipelineError(
            f"native CAL child text binding disagrees with Contract A: {proposition_id}"
        )
    try:
        outcome = BoundAuditOutcome.create(
            proposition_id=proposition_id,
            text_sha256=child.text_sha256,
            audit_result_sha256=_tagged_bytes(result_bytes),
            conclusion=conclusion,
        )
    except (ValueError, DecompositionRefusal) as exc:
        raise ParentBoundPipelineError(f"unqualified native CAL child: {exc}") from exc
    return NativeChild(proposition_id, result_bytes, record, outcome)


def compose_native_children(
    contract_a: Mapping[str, Any],
    child_result_bytes: Sequence[bytes],
) -> tuple[DecompositionResult, tuple[NativeChild, ...]]:
    declaration = _declaration(contract_a)
    children = tuple(_native_child(declaration, raw) for raw in child_result_bytes)
    by_id: dict[str, NativeChild] = {}
    for child in children:
        if child.proposition_id in by_id:
            raise ParentBoundPipelineError(f"duplicate native child result: {child.proposition_id}")
        by_id[child.proposition_id] = child
    declared = [row.proposition_id for row in declaration.children]
    missing = [value for value in declared if value not in by_id]
    extra = [value for value in by_id if value not in set(declared)]
    if missing:
        raise ParentBoundPipelineError("missing native child result(s): " + ",".join(missing))
    if extra:
        raise ParentBoundPipelineError("extra native child result(s): " + ",".join(sorted(extra)))

    ordered = tuple(by_id[value] for value in declared)
    try:
        parent = recompose(
            declaration,
            child_outcomes=tuple(child.outcome for child in ordered),
        )
    except DecompositionRefusal as exc:
        raise ParentBoundPipelineError(f"parent recomposition refused: {exc}") from exc
    return parent, ordered


def _public_terminal(record: Mapping[str, Any]) -> tuple[str, str]:
    result = record["result"]
    conclusion = result["conclusion"]
    failure = result["failure_code"]
    if conclusion == "supported":
        return "supported", "categorical_support"
    if conclusion == "contradicted":
        return "contradicted", "categorical_refutation"
    if failure == "MIXED_RELATIONS":
        return "not_checkable", "MIXED_RELATIONS"
    if failure == "UNSUPPORTED_SEMANTIC_FAMILY":
        return "not_checkable", "UNSUPPORTED_SEMANTIC_FAMILY"
    if failure == "RELATION_UNRESOLVED":
        has_unresolved = any(
            trace.get("relation") is not None
            and trace["relation"].get("categorical_relation") == "UNRESOLVED"
            for trace in result["traces"]
        )
        return (
            ("not_checkable", "unresolved_categorical_relation")
            if has_unresolved
            else ("not_checkable", "no_deciding_relation")
        )
    if failure == "NO_DECIDING_RELATION":
        return "not_checkable", "no_deciding_relation"
    raise ParentBoundPipelineError(
        f"UNREPRESENTABLE_RC2_TERMINAL:{conclusion}:{failure}"
    )


def _participant_rows(
    record: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[list[dict[str, str]]]]:
    traces = record["result"]["traces"]
    deciding = set(record["result"]["deciding_passage_ids"])
    participants: list[dict[str, Any]] = []
    support_refs: list[dict[str, str]] = []
    refute_refs: list[dict[str, str]] = []
    unresolved_refs: list[dict[str, str]] = []

    for trace in traces:
        relation = trace.get("relation")
        authority = trace.get("authority")
        if relation is None or authority is None:
            continue
        atom = authority.get("atom") or {}
        ref = {
            "source_id": str(atom["source_id"]),
            "passage_id": str(trace["passage_id"]),
        }
        category = relation["categorical_relation"]
        if category == "SUPPORTS":
            label = "supports"
            support_refs.append(ref)
        elif category == "REFUTES":
            label = "refutes"
            refute_refs.append(ref)
        else:
            label = "non_polarized"
            unresolved_refs.append(ref)
        participants.append(
            {
                "evidence_ref": ref,
                "relation": label,
                "role": "causal" if trace["passage_id"] in deciding else "residual",
            }
        )

    verdict, reason = _public_terminal(record)
    if verdict == "supported":
        groups = [
            [ref]
            for ref in support_refs
            if any(
                p["evidence_ref"] == ref and p["role"] == "causal"
                for p in participants
            )
        ]
    elif verdict == "contradicted":
        groups = [
            [ref]
            for ref in refute_refs
            if any(
                p["evidence_ref"] == ref and p["role"] == "causal"
                for p in participants
            )
        ]
    elif reason == "MIXED_RELATIONS":
        groups = [[s, r] for s in support_refs for r in refute_refs]
        causal = {
            (x["source_id"], x["passage_id"]) for group in groups for x in group
        }
        for row in participants:
            key = (
                row["evidence_ref"]["source_id"],
                row["evidence_ref"]["passage_id"],
            )
            row["role"] = "causal" if key in causal else "residual"
    elif reason == "unresolved_categorical_relation":
        groups = [[ref] for ref in unresolved_refs]
        causal = {
            (x["source_id"], x["passage_id"]) for group in groups for x in group
        }
        for row in participants:
            key = (
                row["evidence_ref"]["source_id"],
                row["evidence_ref"]["passage_id"],
            )
            row["role"] = "causal" if key in causal else "residual"
    else:
        groups = []
        for row in participants:
            row["role"] = "residual"
            if reason in {"no_deciding_relation", "UNSUPPORTED_SEMANTIC_FAMILY"}:
                row["relation"] = "non_polarized"
    return participants, groups


def _rc2_proposition(record: Mapping[str, Any]) -> dict[str, Any]:
    verdict, reason = _public_terminal(record)
    participants, groups = _participant_rows(record)
    completion = "assessed" if verdict in {"supported", "contradicted"} else "not_checkable"
    return {
        "proposition": {
            "proposition_id": record["proposition"]["proposition_id"],
            "content_sha256": "sha256:" + record["proposition"]["proposition_sha256"],
        },
        "execution": {"state": "completed", "completion": completion},
        "terminal": {"verdict": verdict, "reason": reason},
        "participants": participants,
        "basis_groups": groups,
    }


def _contract_b_from_record(record: Mapping[str, Any]) -> dict[str, str]:
    row = record["input"]["contract_b"]
    return {
        "contract_version": str(row["version"]),
        "bundle_id": str(row["bundle_id"]),
        "bundle_hash": str(row["bundle_hash"]),
    }


def _recomposition_authority(
    contract_a: Mapping[str, Any],
    *,
    inner: Mapping[str, Any],
    parent: DecompositionResult,
    children: Sequence[NativeChild],
) -> dict[str, Any]:
    declaration = _declaration(contract_a)
    root = contract_a["root_proposition"]
    content_by_id = {
        str(row["proposition"]["proposition_id"]): str(row["proposition"]["content_sha256"])
        for row in inner["propositions"]
    }
    child_by_id = {child.proposition_id: child for child in children}
    return {
        "cal_freeze_commit": CAL_FREEZE_COMMIT,
        "cal_semantic_source_commit": CAL_SEMANTIC_SOURCE_COMMIT,
        "root": {
            "proposition_id": str(root["proposition_id"]),
            "text_sha256": str(root["text_sha256"]),
        },
        "decomposition_id": str(declaration.decomposition_id),
        "operator": str(declaration.operator),
        "ordered_children": [
            {
                "sequence": int(row.sequence or 0),
                "proposition_id": row.proposition_id,
                "text_sha256": row.text_sha256,
                "contract_c_content_sha256": content_by_id[row.proposition_id],
                "native_result_sha256": _tagged_bytes(
                    child_by_id[row.proposition_id].result_bytes
                ),
                "cal_result_id": child_by_id[row.proposition_id].outcome.result_id,
                "conclusion": child_by_id[row.proposition_id].outcome.conclusion.value,
            }
            for row in declaration.children
        ],
        "decomposition_receipt_id": parent.receipt.receipt_id,
        "parent_conclusion": parent.conclusion.value,
    }


def _load_resolver(resolver_root: Path) -> dict[str, Any]:
    try:
        value = json.loads((resolver_root / RESOLVER_PATH).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ParentBoundPipelineError(f"cannot load exact resolver authority: {exc}") from exc
    if not isinstance(value, dict) or not isinstance(value.get("entries"), list):
        raise ParentBoundPipelineError("resolver authority has invalid shape")
    return value


def build_parent_bound_contract_c(
    *,
    contract_a: Mapping[str, Any],
    child_result_bytes: Sequence[bytes],
    evidence_index: set[tuple[str, str]],
    contract_c_root: Path,
    rc2_root: Path,
    resolver_root: Path,
) -> ParentBoundBuild:
    verify_external_authorities(
        contract_c_root=contract_c_root,
        rc2_root=rc2_root,
        resolver_root=resolver_root,
    )
    candidate, rc2 = _load_authority_modules(
        contract_c_root=contract_c_root,
        rc2_root=rc2_root,
    )
    resolver = _load_resolver(resolver_root)

    parent, children = compose_native_children(contract_a, child_result_bytes)
    contract_b_values = [_contract_b_from_record(child.result_record) for child in children]
    exact_contract_b = contract_b_values[0]
    if any(value != exact_contract_b for value in contract_b_values[1:]):
        raise ParentBoundPipelineError("child results do not share exact Contract B evidence world")

    inner = rc2.seal(
        {
            "profile": rc2.PROFILE,
            "contract_b": exact_contract_b,
            "producer": {
                "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
                "policy_sha256": POLICY_SHA256,
                "policy_resolver_commit_sha": POLICY_RESOLVER_COMMIT,
            },
            "execution": {"state": "completed"},
            "propositions": [_rc2_proposition(child.result_record) for child in children],
        }
    )
    inner_expected = rc2.whole_object_sha256(inner)
    rc2.verify_candidate(
        inner,
        exact_contract_b=exact_contract_b,
        evidence_index=evidence_index,
        independently_selected_resolver_commit_sha=POLICY_RESOLVER_COMMIT,
        resolver_entries=resolver["entries"],
        expected_whole_object_sha256=inner_expected,
    )

    authority = _recomposition_authority(
        contract_a,
        inner=inner,
        parent=parent,
        children=children,
    )
    outer = candidate.seal(
        {
            "profile": candidate.PROFILE,
            "rc2_result": inner,
            "recomposition": authority,
        }
    )
    candidate.validate_object(outer, rc2_validator=rc2)
    candidate.verify_recomposition_authority(
        outer,
        exact_recomposition=authority,
        rc2_validator=rc2,
    )
    contract_c_bytes = candidate.canonical_bytes(outer, rc2_validator=rc2)
    contract_c_sha = candidate.whole_object_sha256(outer, rc2_validator=rc2)
    return ParentBoundBuild(
        parent=parent,
        children=children,
        contract_c_object=outer,
        contract_c_bytes=contract_c_bytes,
        contract_c_sha256=contract_c_sha,
        recomposition_authority=authority,
    )


def _evidence_index(bundle_dir: Path, one_target: Path) -> set[tuple[str, str]]:
    prepared = prepare_contract_b_input(bundle_dir, one_target)
    return {
        (str(source_id), str(passage.passage_id))
        for source_id, passages in prepared.intake.bundle.passages.items()
        for passage in passages
    }


def _parent_result_record(
    *,
    contract_a: Mapping[str, Any],
    build: ParentBoundBuild,
) -> dict[str, Any]:
    declaration = _declaration(contract_a)
    return {
        "schema": _PARENT_RESULT_SCHEMA,
        "distribution_version": DISTRIBUTION_VERSION,
        "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
        "cal_freeze_commit": CAL_FREEZE_COMMIT,
        "cal_semantic_source_commit": CAL_SEMANTIC_SOURCE_COMMIT,
        "contract_a": {
            "handoff_id": contract_a.get("handoff_id"),
            "handoff_sha256": contract_a.get("handoff_sha256"),
            "root_proposition_id": declaration.root.proposition_id,
            "root_text_sha256": declaration.root.text_sha256,
            "decomposition_id": declaration.decomposition_id,
            "operator": declaration.operator,
        },
        "children": [
            {
                "sequence": row.sequence,
                "proposition_id": row.proposition_id,
                "text_sha256": row.text_sha256,
                "native_result_sha256": _tagged_bytes(
                    next(
                        child.result_bytes
                        for child in build.children
                        if child.proposition_id == row.proposition_id
                    )
                ),
                "cal_result_id": next(
                    child.outcome.result_id
                    for child in build.children
                    if child.proposition_id == row.proposition_id
                ),
                "conclusion": next(
                    child.outcome.conclusion.value
                    for child in build.children
                    if child.proposition_id == row.proposition_id
                ),
            }
            for row in declaration.children
        ],
        "decomposition_receipt_id": build.parent.receipt.receipt_id,
        "parent_conclusion": build.parent.conclusion.value,
        "contract_c": {
            "profile": CONTRACT_C_PROFILE,
            "freeze_commit": CONTRACT_C_FREEZE_COMMIT,
            "candidate_blob": CONTRACT_C_CANDIDATE_BLOB,
            "whole_object_sha256": build.contract_c_sha256,
        },
        "authorization": {
            "state": "not_evaluated",
            "automatic_action_allowed": False,
        },
    }


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _ensure_destination_available(out_dir: Path) -> None:
    if out_dir.is_symlink():
        raise ParentBoundPipelineError(f"output directory must not be a symlink: {out_dir}")
    if not out_dir.exists():
        return
    if not out_dir.is_dir():
        raise ParentBoundPipelineError(f"output path is not a directory: {out_dir}")
    try:
        next(out_dir.iterdir())
    except StopIteration:
        return
    raise ParentBoundPipelineError(f"refusing to overwrite non-empty output directory: {out_dir}")


def run_parent_bound_pipeline(
    *,
    contract_a_path: Path,
    bundle_dir: Path,
    child_targets: Mapping[str, Path],
    out_dir: Path,
    contract_c_root: Path,
    rc2_root: Path,
    resolver_root: Path,
) -> dict[str, Any]:
    _ensure_destination_available(out_dir)
    try:
        contract_a = json.loads(contract_a_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ParentBoundPipelineError(f"cannot load Contract A input: {exc}") from exc
    if not isinstance(contract_a, dict):
        raise ParentBoundPipelineError("Contract A input must be an object")

    declaration = _declaration(contract_a)
    declared_ids = [row.proposition_id for row in declaration.children]
    if set(child_targets) != set(declared_ids):
        missing = sorted(set(declared_ids) - set(child_targets))
        extra = sorted(set(child_targets) - set(declared_ids))
        raise ParentBoundPipelineError(
            f"child target set mismatch; missing={missing}, extra={extra}"
        )

    out_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{out_dir.name}.tmp-", dir=out_dir.parent))
    try:
        result_bytes: list[bytes] = []
        for proposition_id in declared_ids:
            child_out = temp_dir / "children" / proposition_id
            run_contract_b_bundle(
                bundle_dir,
                child_targets[proposition_id],
                child_out,
            )
            result_bytes.append((child_out / "result.json").read_bytes())

        evidence_index = _evidence_index(bundle_dir, child_targets[declared_ids[0]])
        build = build_parent_bound_contract_c(
            contract_a=contract_a,
            child_result_bytes=result_bytes,
            evidence_index=evidence_index,
            contract_c_root=contract_c_root,
            rc2_root=rc2_root,
            resolver_root=resolver_root,
        )
        parent_record = _parent_result_record(contract_a=contract_a, build=build)
        parent_bytes = _canonical_json_bytes(parent_record)
        (temp_dir / "parent-result.json").write_bytes(parent_bytes)
        (temp_dir / "contract-c.json").write_bytes(build.contract_c_bytes)
        manifest = {
            "schema": _PARENT_MANIFEST_SCHEMA,
            "distribution_version": DISTRIBUTION_VERSION,
            "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
            "contract_c_freeze_commit": CONTRACT_C_FREEZE_COMMIT,
            "contract_c_candidate_blob": CONTRACT_C_CANDIDATE_BLOB,
            "rc2_authority_commit": RC2_AUTHORITY_COMMIT,
            "resolver_authority_commit": RESOLVER_AUTHORITY_COMMIT,
            "parent_result_sha256": _tagged_bytes(parent_bytes),
            "contract_c_sha256": build.contract_c_sha256,
            "child_result_sha256": {
                child.proposition_id: _tagged_bytes(child.result_bytes)
                for child in build.children
            },
            "authorization": {
                "state": "not_evaluated",
                "automatic_action_allowed": False,
            },
        }
        (temp_dir / "manifest.json").write_bytes(_canonical_json_bytes(manifest))

        if out_dir.exists():
            _ensure_destination_available(out_dir)
            out_dir.rmdir()
        os.replace(temp_dir, out_dir)
        return manifest
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def inspect_parent_bound_authority() -> dict[str, Any]:
    return {
        "distribution_version": DISTRIBUTION_VERSION,
        "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
        "cal_freeze_commit": CAL_FREEZE_COMMIT,
        "cal_semantic_source_commit": CAL_SEMANTIC_SOURCE_COMMIT,
        "decomposition": {
            "implementation_blob": "268d0dc4dd22ddde3848141d62b7d719e48d374d",
            "qualified_operator": "all_of",
        },
        "contract_c": {
            "state": "frozen_unreleased_external_authority",
            "profile": CONTRACT_C_PROFILE,
            "freeze_commit": CONTRACT_C_FREEZE_COMMIT,
            "candidate_blob": CONTRACT_C_CANDIDATE_BLOB,
            "rc2_authority_commit": RC2_AUTHORITY_COMMIT,
            "resolver_authority_commit": RESOLVER_AUTHORITY_COMMIT,
        },
        "target_authoring": {
            "state": "not_owned",
            "requirement": "trusted_or_prevalidated_child_targets",
        },
        "authorization": {
            "automatic_action_allowed": False,
        },
    }


__all__ = [
    "CAL_FREEZE_COMMIT",
    "CAL_SEMANTIC_SOURCE_COMMIT",
    "CONTRACT_C_CANDIDATE_BLOB",
    "CONTRACT_C_FREEZE_COMMIT",
    "CONTRACT_C_PROFILE",
    "ParentBoundBuild",
    "ParentBoundPipelineError",
    "build_parent_bound_contract_c",
    "compose_native_children",
    "inspect_parent_bound_authority",
    "run_parent_bound_pipeline",
    "verify_external_authorities",
]
