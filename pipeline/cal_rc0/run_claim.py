"""Run one real supplied-evidence claim through the supported CAL RC0 semantics.

This is an operator-facing research runner, not a pipeline release and not a
production CAL promotion. It deliberately bypasses Contract A/B/C packaging so
CAL can be exercised directly against an explicit operator-supplied evidence
world.

Supported semantic family: strict_comparison only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
from typing import Any, Callable

import run_pipeline as base

PACKET_SCHEMA = "cal-runnable-claim-rc0-v1"
RESULT_SCHEMA = "cal-runnable-claim-result-rc0-v1"
ALLOWED_ADMISSION = {"accepted", "rejected", "needs-review"}
ALLOWED_DIRECTIONS = {"greater_than", "less_than"}


def _canonical_bytes(value: Any) -> bytes:
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


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_packet(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("claim packet must be a JSON object")
    if set(value) != {"schema", "claim_id", "claim_text", "target", "evidence"}:
        raise ValueError("claim packet top-level shape mismatch")
    if value.get("schema") != PACKET_SCHEMA:
        raise ValueError(f"claim packet schema must be {PACKET_SCHEMA}")
    claim_id = value.get("claim_id")
    claim_text = value.get("claim_text")
    if not isinstance(claim_id, str) or not claim_id.strip():
        raise ValueError("claim_id must be a non-empty string")
    if not isinstance(claim_text, str) or not claim_text.strip():
        raise ValueError("claim_text must be a non-empty string")

    target = value.get("target")
    if not isinstance(target, dict) or set(target) != {
        "family",
        "lhs_entity",
        "rhs_entity",
        "comparison_direction",
    }:
        raise ValueError("target must declare family, lhs_entity, rhs_entity, comparison_direction")
    if target.get("family") != "strict_comparison":
        raise ValueError("RC0 runnable CAL currently supports strict_comparison only")
    lhs = target.get("lhs_entity")
    rhs = target.get("rhs_entity")
    direction = target.get("comparison_direction")
    if not isinstance(lhs, str) or not lhs.strip() or not isinstance(rhs, str) or not rhs.strip():
        raise ValueError("target entities must be non-empty strings")
    if lhs.casefold() == rhs.casefold():
        raise ValueError("target entities must be distinct")
    if direction not in ALLOWED_DIRECTIONS:
        raise ValueError("comparison_direction must be greater_than or less_than")

    evidence = value.get("evidence")
    if not isinstance(evidence, list):
        raise ValueError("evidence must be a list")
    passage_ids: set[str] = set()
    for index, row in enumerate(evidence, start=1):
        if not isinstance(row, dict) or set(row) != {
            "source_id",
            "passage_id",
            "text",
            "admission",
        }:
            raise ValueError(f"evidence row {index} shape mismatch")
        for field in ("source_id", "passage_id", "text"):
            if not isinstance(row.get(field), str) or not str(row[field]).strip():
                raise ValueError(f"evidence row {index} requires non-empty {field}")
        pid = str(row["passage_id"])
        if pid in passage_ids:
            raise ValueError(f"duplicate passage_id: {pid}")
        passage_ids.add(pid)
        if row.get("admission") not in ALLOWED_ADMISSION:
            raise ValueError(
                f"evidence row {index} admission must be accepted, rejected, or needs-review"
            )
    return value


def _git(*args: str, cwd: Path | None = None) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def _ensure_checkout(*, root: Path, commit: str) -> None:
    if not root.exists():
        root.parent.mkdir(parents=True, exist_ok=True)
        _git(
            "clone",
            "--no-checkout",
            "https://github.com/camerontjs-dot/claim-audit-lab.git",
            str(root),
        )
    if not (root / ".git").exists():
        raise RuntimeError(f"dependency path is not a git checkout: {root}")
    try:
        _git("cat-file", "-e", f"{commit}^{{commit}}", cwd=root)
    except subprocess.CalledProcessError:
        _git("fetch", "origin", commit, cwd=root)
    _git("checkout", "--detach", "--force", commit, cwd=root)
    if _git("rev-parse", "HEAD", cwd=root) != commit:
        raise RuntimeError(f"failed to pin dependency {root} to {commit}")


def _dependency_roots(args: argparse.Namespace) -> tuple[Path, Path]:
    if args.rc7fb1_root is not None or args.rc8j_root is not None:
        if args.rc7fb1_root is None or args.rc8j_root is None:
            raise ValueError("--rc7fb1-root and --rc8j-root must be supplied together")
        return args.rc7fb1_root.resolve(), args.rc8j_root.resolve()

    deps = args.deps_dir.resolve()
    rc7 = deps / "rc7fb1"
    rc8 = deps / "rc8j"
    _ensure_checkout(root=rc7, commit=base.RC7FB1_HEAD)
    _ensure_checkout(root=rc8, commit=base.RC8J_HEAD)
    return rc7, rc8


def _complete_entity_scoped(
    *,
    runtime: Any,
    resolver: Callable[[str, str], tuple[int, int] | None],
    claim_id: str,
    evidence: Any,
    measurement: dict[str, Any],
) -> tuple[Any, str]:
    """Apply RC0A only to lhs/rhs entity lookup, preserving frozen RC0 elsewhere."""
    frozen_complete = runtime.complete_strict_comparison_atom
    frozen_span = runtime._unique_casefold_span
    calls = 0

    def entity_then_frozen(text: str, surface: str) -> tuple[int, int] | None:
        nonlocal calls
        calls += 1
        if calls <= 2:
            return resolver(text, surface)
        return frozen_span(text, surface)

    runtime._unique_casefold_span = entity_then_frozen
    try:
        return frozen_complete(claim_id=claim_id, evidence=evidence, measurement=measurement)
    finally:
        runtime._unique_casefold_span = frozen_span


def _execute_claim(
    *,
    packet: dict[str, Any],
    runtime: Any,
    entity_resolver: Callable[[str, str], tuple[int, int] | None],
    measure_fn: Callable[[str], dict[str, Any]],
    authority_evaluator: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    target = packet["target"]
    proposition = runtime.BoundProposition(
        claim_id=str(packet["claim_id"]),
        claim_text=str(packet["claim_text"]),
        family=str(target["family"]),
        lhs_entity=str(target["lhs_entity"]).casefold(),
        rhs_entity=str(target["rhs_entity"]).casefold(),
        comparison_direction=str(target["comparison_direction"]),
    )

    packet_digest = hashlib.sha256(_canonical_bytes(packet)).hexdigest()
    bundle_id = f"operator-supplied-evidence-world:{packet_digest}"
    admitted_rows = [row for row in packet["evidence"] if row["admission"] == "accepted"]
    admitted = [
        runtime.EvidenceInput(
            source_id=str(row["source_id"]),
            bundle_id=bundle_id,
            passage_id=str(row["passage_id"]),
            passage_text=str(row["text"]),
            passage_sha256=_sha256_text(str(row["text"])),
            semantic_family="strict_comparison",
            metadata={
                "evidence_world": "operator_supplied",
                "admission": "accepted",
            },
        )
        for row in admitted_rows
    ]

    atom_key = secrets.token_bytes(32)
    proposition_key = secrets.token_bytes(32)
    atom_key_id = "cal-runnable-claim-ephemeral-atom-v1"
    proposition_key_id = "cal-runnable-claim-ephemeral-proposition-v1"

    relations: list[Any] = []
    stages: list[dict[str, Any]] = []
    if not admitted:
        relations.append(
            runtime.unresolved_relation(
                proposition=proposition,
                evidence=None,
                reason="NO_ADMITTED_EVIDENCE",
            )
        )
    else:
        proposition_binding = runtime.issue_proposition_binding(
            proposition=proposition,
            key=proposition_key,
            key_id=proposition_key_id,
        )
        proposition_binding_identity = runtime.stable_id(
            "proposition-binding", proposition_binding
        )
        for evidence in admitted:
            stage: dict[str, Any] = {
                "source_id": evidence.source_id,
                "passage_id": evidence.passage_id,
                "admission": "accepted",
                "measurement": None,
                "typed_atom": None,
                "warrant_status": None,
                "warrant_atom_receipt_identity": None,
                "proposition_binding_identity": proposition_binding_identity,
                "categorical_relation": None,
                "failure_category": None,
            }
            measurement = measure_fn(evidence.passage_text)
            stage["measurement"] = deepcopy(measurement)
            atom, atom_state = _complete_entity_scoped(
                runtime=runtime,
                resolver=entity_resolver,
                claim_id=proposition.claim_id,
                evidence=evidence,
                measurement=measurement,
            )
            if atom is None:
                relation = runtime.unresolved_relation(
                    proposition=proposition,
                    evidence=evidence,
                    reason=atom_state,
                )
                relations.append(relation)
                stage["categorical_relation"] = asdict(relation)
                stage["failure_category"] = (
                    "MEASUREMENT_MISS_SAFE"
                    if atom_state == "MEASUREMENT_MISS_SAFE"
                    else "ATOM_INCOMPLETE"
                )
                stages.append(stage)
                continue

            stage["typed_atom"] = asdict(atom)
            case = runtime.build_rc8j_case(atom=atom, evidence=evidence)
            authority_observation = authority_evaluator(deepcopy(case))
            stage["warrant_status"] = deepcopy(authority_observation)
            if authority_observation.get("authority_status") != "WARRANTED":
                relation = runtime.unresolved_relation(
                    proposition=proposition,
                    evidence=evidence,
                    reason=(
                        f"WARRANT_{authority_observation.get('authority_status')}:"
                        f"{authority_observation.get('reason')}"
                    ),
                )
                relations.append(relation)
                stage["categorical_relation"] = asdict(relation)
                stage["failure_category"] = "WARRANT_UNRESOLVED"
                stages.append(stage)
                continue

            atom_warrant = runtime.issue_atom_warrant(
                case=case,
                authority_evaluator=authority_evaluator,
                key=atom_key,
                key_id=atom_key_id,
            )
            stage["warrant_atom_receipt_identity"] = runtime.stable_id(
                "warrant-receipt", atom_warrant
            )
            evidence_ref = {
                "source_id": evidence.source_id,
                "passage_id": evidence.passage_id,
                "passage_sha256": evidence.passage_sha256,
            }
            relation = runtime.derive_categorical_relation(
                case=case,
                proposition=proposition,
                atom_warrant=atom_warrant,
                atom_trusted_keys={atom_key_id: atom_key},
                proposition_binding=proposition_binding,
                proposition_trusted_keys={proposition_key_id: proposition_key},
                evidence_ref=evidence_ref,
            )
            relations.append(relation)
            stage["categorical_relation"] = asdict(relation)
            stages.append(stage)

    conclusion = runtime.compose_categorical_relations(
        proposition=proposition,
        relations=relations,
        required_relation_count=max(1, len(admitted)),
    )
    verdict = conclusion.verdict if conclusion.disposition == "decided" else "not_checkable"
    admission_counts = Counter(str(row["admission"]) for row in packet["evidence"])

    return {
        "schema": RESULT_SCHEMA,
        "execution_status": "PASS",
        "claim": {
            "claim_id": proposition.claim_id,
            "claim_text": proposition.claim_text,
            "claim_text_sha256": runtime.claim_text_sha256(proposition.claim_text),
            "target": runtime.proposition_projection(proposition),
        },
        "evidence_world": {
            "kind": "operator_supplied",
            "bundle_id": bundle_id,
            "packet_sha256": packet_digest,
            "total_passages": len(packet["evidence"]),
            "admission_counts": dict(sorted(admission_counts.items())),
            "admitted_passage_ids": [item.passage_id for item in admitted],
            "nonadmitted": [
                {
                    "source_id": row["source_id"],
                    "passage_id": row["passage_id"],
                    "admission": row["admission"],
                    "passage_sha256": _sha256_text(str(row["text"])),
                }
                for row in packet["evidence"]
                if row["admission"] != "accepted"
            ],
        },
        "cal": {
            "profile": runtime.PROFILE_ID,
            "span_resolver": "rc0a_entity_only_unique_exact_lexical_boundary",
            "entity_span_scope": ["lhs_entity", "rhs_entity"],
            "non_entity_span_resolver": "frozen_rc0_unique_casefold_span",
            "rc7fb1_head": base.RC7FB1_HEAD,
            "rc7fb1_blob": base.RC7FB1_BLOB,
            "rc8j_head": base.RC8J_HEAD,
            "rc8j_blob": base.RC8J_BLOB,
            "rc0_runtime_blob": base.RC0_RUNTIME_BLOB,
            "rc0a_span_blob": base.RC0A_SPAN_BLOB,
        },
        "receipt_authentication": {
            "mode": "ephemeral_local_run",
            "portable_verification": False,
            "detail": (
                "HMAC bindings are verified inside this run; ephemeral keys are not persisted. "
                "This runner does not claim a production issuer/key-management envelope."
            ),
        },
        "stages": stages,
        "relations": [asdict(item) for item in relations],
        "conclusion": asdict(conclusion),
        "reported_verdict": verdict,
        "boundaries": {
            "supported_semantic_family": "strict_comparison",
            "raw_claim_to_typed_target_inference": "NOT_PERFORMED",
            "evidence_discovery_or_retrieval": "NOT_PERFORMED",
            "contract_b_transport": "NOT_USED_STANDALONE_CAL_RUN",
            "contract_c_projection": "NOT_USED_STANDALONE_CAL_RUN",
            "root_or_multi_claim_composition": "NOT_APPLICABLE_SINGLE_CLAIM",
            "operational_authorization": "NOT_EVALUATED",
            "production_release_authorized": False,
        },
    }


def _render_markdown(result: dict[str, Any]) -> str:
    claim = result["claim"]
    target = claim["target"]
    conclusion = result["conclusion"]
    lines = [
        "# CAL single-claim audit",
        "",
        f"**Claim ID:** `{claim['claim_id']}`",
        "",
        f"> {claim['claim_text']}",
        "",
        "## Result",
        "",
        f"**Reported verdict:** `{result['reported_verdict']}`",
        f"**Disposition:** `{conclusion['disposition']}`",
        f"**Reason:** `{conclusion['reason_code']}`",
        "",
        "## Typed target supplied by operator",
        "",
        f"- family: `{target['family']}`",
        f"- lhs entity: `{target['lhs_entity']}`",
        f"- rhs entity: `{target['rhs_entity']}`",
        f"- comparison direction: `{target['comparison_direction']}`",
        "",
        "## Evidence participation",
        "",
    ]
    if not result["stages"]:
        lines.append("No evidence passage was admitted into CAL.")
    else:
        lines.extend(
            [
                "| Passage | Measurement | Warrant | Relation | Failure |",
                "|---|---|---|---|---|",
            ]
        )
        for stage in result["stages"]:
            measurement = stage["measurement"] or {}
            warrant = stage["warrant_status"] or {}
            relation = stage["categorical_relation"] or {}
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{stage['passage_id']}`",
                        f"`{measurement.get('status', 'NOT_RUN')}`",
                        f"`{warrant.get('authority_status', 'NOT_RUN')}`",
                        f"`{relation.get('relation', 'UNRESOLVED')}`",
                        f"`{stage['failure_category'] or 'none'}`",
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "This is a standalone CAL run over an explicitly supplied evidence world. It does not "
            "perform web retrieval, infer the typed target from raw English, emit Contract B/C, or "
            "authorize an operational action.",
            "",
            "Evidence marked `accepted` means admitted to the audit, not semantically supporting. "
            "The CAL relation and conclusion are derived after admission.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_outputs(result: dict[str, Any], out_dir: Path) -> None:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    (out_dir / "CAL-AUDIT-RESULT.json").write_bytes(_canonical_bytes(result))
    (out_dir / "CAL-AUDIT-REPORT.md").write_text(_render_markdown(result), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one supplied-evidence strict-comparison claim through CAL RC0."
    )
    parser.add_argument("packet", type=Path, help="cal-runnable-claim-rc0-v1 JSON packet")
    parser.add_argument("--out-dir", type=Path, default=Path("build/cal-runnable-claim"))
    parser.add_argument("--deps-dir", type=Path, default=Path(".cal/rc0-deps"))
    parser.add_argument("--rc7fb1-root", type=Path)
    parser.add_argument("--rc8j-root", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cal_root = Path(__file__).resolve().parents[2]
    packet = _load_packet(args.packet.resolve())

    if base.git_blob(cal_root, "research/cal_research_profile_rc0/runtime.py") != base.RC0_RUNTIME_BLOB:
        raise RuntimeError("frozen RC0 runtime blob mismatch")
    if (
        base.git_blob(
            cal_root,
            "research/cal_research_profile_rc0a_span_anchoring/span_anchor.py",
        )
        != base.RC0A_SPAN_BLOB
    ):
        raise RuntimeError("RC0A span resolver blob mismatch")

    rc7_root, rc8_root = _dependency_roots(args)
    base.require_identity(
        rc7_root,
        head=base.RC7FB1_HEAD,
        blobs={"research/comparative_relation_measurement_rc7fb1/comparator.py": base.RC7FB1_BLOB},
    )
    base.require_identity(
        rc8_root,
        head=base.RC8J_HEAD,
        blobs={"research/semantic_authority_machinery_rc8/authority_contract_rc8j.py": base.RC8J_BLOB},
    )

    runtime = base.load_module(
        "cal_runnable_claim_runtime",
        cal_root / "research" / "cal_research_profile_rc0" / "runtime.py",
    )
    span = base.load_module(
        "cal_runnable_claim_span",
        cal_root / "research" / "cal_research_profile_rc0a_span_anchoring" / "span_anchor.py",
    )
    if span.unique_lexical_span("Women trailed Men by 11 percentage points.", "Men") != (14, 17):
        raise RuntimeError("RC0A lexical span integration control failed")

    measure_fn = base.load_measure(rc7_root)
    authority_evaluator = base.load_rc8j(rc8_root)
    result = _execute_claim(
        packet=packet,
        runtime=runtime,
        entity_resolver=span.unique_lexical_span,
        measure_fn=measure_fn,
        authority_evaluator=authority_evaluator,
    )
    _write_outputs(result, args.out_dir.resolve())
    print(json.dumps({
        "execution_status": result["execution_status"],
        "claim_id": result["claim"]["claim_id"],
        "reported_verdict": result["reported_verdict"],
        "reason_code": result["conclusion"]["reason_code"],
        "out_dir": str(args.out_dir.resolve()),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
