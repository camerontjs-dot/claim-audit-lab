#!/usr/bin/env python3
"""Build a receipt-bound DEV packet for the preserved D6 A4 alternatives.

The default path is inference-free: it enumerates the preserved unknown A4
passages, binds each row to its eligibility/operator/trace/source artifacts, and
records the exact missing semantic receipt.  An optional probe-receipt file can
be applied later, but it must bind an exact claim, passage, hypothesis, model
identity, and raw result.  This adapter never derives validity from ordinary NLI
scores, retrieval rank, labels, or claim relationships.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "cal-d6-aperture-shadow-v1"
PROBE_SCHEMA_VERSION = "cal-d6-probe-receipts-v1"
EXPECTED_TARGET_COUNT = 53
UNKNOWN_REASON_NO_PROBE = "A4 recorded no semantic probe for this passage"
UNKNOWN_REASON_ABSTAINED = "the recorded structural negator abstained; unknown may not decide"


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _path_record(path: Path) -> dict[str, str]:
    resolved = path.resolve()
    return {"path": str(resolved), "sha256": sha256(resolved)}


def _index_rows(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = report.get("rows")
    if not isinstance(rows, list):
        raise ValueError("report does not contain a rows list")
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        claim_id = str(row["claim_id"])
        if claim_id in indexed:
            raise ValueError(f"duplicate report row for {claim_id}")
        indexed[claim_id] = row
    return indexed


def _index_traces(trace_dir: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Path]]:
    traces: dict[str, dict[str, Any]] = {}
    paths: dict[str, Path] = {}
    for path in sorted(trace_dir.glob("*.json")):
        trace = _read_json(path)
        claim_id = str(trace["claim_id"])
        if claim_id in traces:
            raise ValueError(f"duplicate trace for {claim_id}")
        traces[claim_id] = trace
        paths[claim_id] = path.resolve()
    if not traces:
        raise ValueError(f"trace directory is empty: {trace_dir}")
    return traces, paths


def _index_claims(claims_path: Path | None) -> dict[str, dict[str, Any]]:
    if claims_path is None or not claims_path.exists():
        return {}
    claims = _read_json(claims_path)
    if not isinstance(claims, list):
        raise ValueError("claims packet is not a list")
    indexed: dict[str, dict[str, Any]] = {}
    for claim in claims:
        claim_id = str(claim["claim_id"])
        if claim_id in indexed:
            raise ValueError(f"duplicate claim record for {claim_id}")
        indexed[claim_id] = claim
    return indexed


def _source_stem(source_path: str) -> str:
    stem = Path(source_path).stem
    for suffix in ("_SUPERSEDED", "_DRAFT", "_CURRENT", "_APPROVED"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def _source_files(*, raw_dir: Path | None, claim_record: dict[str, Any] | None) -> dict[str, Any]:
    if raw_dir is None or claim_record is None:
        return {"prompt": None, "response": None}
    stem = _source_stem(str(claim_record.get("source_path", "")))
    prompt = (raw_dir / f"{stem}.prompt.txt").resolve()
    response = (raw_dir / f"{stem}.response.txt").resolve()
    return {
        "prompt": _path_record(prompt) if prompt.exists() else None,
        "response": _path_record(response) if response.exists() else None,
    }


def _candidate_map(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    candidates = row.get("after_refutation_candidates", [])
    return {str(item["passage_id"]): item for item in candidates}


def _trace_items(trace: dict[str, Any], field: str) -> dict[str, dict[str, Any]]:
    return {str(item["passage_id"]): item for item in trace.get(field, [])}


def _probe_state(trace: dict[str, Any], passage_id: str) -> dict[str, Any]:
    probe = trace.get("negation_probe")
    if probe is None:
        return {"state": "absent", "negated_claim": None, "result": None}
    if bool(probe.get("abstained")) or probe.get("result") is None:
        return {
            "state": "abstained",
            "negated_claim": probe.get("negated_claim"),
            "result": None,
        }
    result = probe["result"]
    result_passage = str(result["passage_id"])
    return {
        "state": "target" if result_passage == passage_id else "different_passage",
        "negated_claim": probe.get("negated_claim"),
        "result": result,
    }


def _unknown_targets(
    operator_rows: dict[str, dict[str, Any]],
) -> list[tuple[str, dict[str, Any], str, str]]:
    targets: list[tuple[str, dict[str, Any], str, str]] = []
    seen: set[tuple[str, str]] = set()
    for claim_id, row in sorted(operator_rows.items()):
        for judgment in row.get("operator_judgments", []):
            if (
                judgment.get("channel") != "refutation"
                or judgment.get("operator") != "A4_negation_consistency"
                or bool(judgment.get("derived", False))
                or judgment.get("status") != "unknown"
            ):
                continue
            passage_ids = tuple(str(value) for value in judgment.get("passage_ids", []))
            if len(passage_ids) != 1:
                raise ValueError(f"D6 target must name one passage: {claim_id}")
            passage_id = passage_ids[0]
            key = (claim_id, passage_id)
            if key in seen:
                raise ValueError(f"duplicate D6 target: {claim_id} / {passage_id}")
            seen.add(key)
            targets.append((claim_id, judgment, passage_id, str(judgment["reason"])))
    return targets


def _target_record(
    *,
    claim_id: str,
    judgment: dict[str, Any],
    passage_id: str,
    reason: str,
    eligibility_row: dict[str, Any],
    trace: dict[str, Any],
    trace_path: Path,
    claim_record: dict[str, Any] | None,
    raw_dir: Path | None,
) -> dict[str, Any]:
    candidates = _candidate_map(eligibility_row)
    retrieval = _trace_items(trace, "retrieval")
    entailment = _trace_items(trace, "entailment")
    blockers: list[str] = []
    if passage_id not in candidates:
        blockers.append("passage_absent_from_post_eligibility_candidates")
    if passage_id not in retrieval:
        blockers.append("passage_absent_from_trace_retrieval")
    if passage_id not in entailment:
        blockers.append("ordinary_entailment_receipt_absent")

    probe = _probe_state(trace, passage_id)
    if probe["state"] == "target":
        blockers.append("report_unknown_conflicts_with_target_probe")
    else:
        blockers.append("missing_alternative_a4_probe_receipt")
    if probe["negated_claim"] is None:
        blockers.append("negated_hypothesis_not_recorded")

    source_files = _source_files(raw_dir=raw_dir, claim_record=claim_record)
    if source_files["prompt"] is None:
        blockers.append("source_prompt_not_present_in_preserved_packet")
    source_hashes = {}
    if claim_record is not None:
        for kind, field in (("prompt", "prompt_sha256"), ("response", "response_sha256")):
            recorded = claim_record.get(field)
            observed = source_files[kind]["sha256"] if source_files[kind] is not None else None
            matches = (
                recorded == observed if recorded is not None and observed is not None else False
            )
            source_hashes[kind] = {"recorded": recorded, "observed": observed, "matches": matches}
            if not matches:
                blockers.append(f"{kind}_hash_mismatch_or_absent")

    return {
        "claim_id": claim_id,
        "passage_id": passage_id,
        "existing_judgment": judgment,
        "assessment": {
            "status": "unknown",
            "reason": reason,
            "operator": "A4_negation_consistency",
            "receipt_sha256": None,
        },
        "eligibility": {
            "status": "eligible_by_preserved_shadow" if passage_id in candidates else "unknown",
            "reason": (
                "present in the preserved post-eligibility refutation candidate list; "
                "source trust remains the historical P1 parity assumption"
            ),
            "candidate": candidates.get(passage_id),
        },
        "trace": {
            "path": str(trace_path.resolve()),
            "sha256": sha256(trace_path),
            "claim_id_matches": str(trace.get("claim_id")) == claim_id,
            "admitted_retrieval": retrieval.get(passage_id),
            "ordinary_entailment_receipt": entailment.get(passage_id),
            "negation_probe_state": probe,
        },
        "source": {
            "claim_record": claim_record,
            "prompt": source_files["prompt"],
            "response": source_files["response"],
            "hash_checks": source_hashes,
        },
        "blockers": sorted(set(blockers)),
        "probe_receipt": None,
    }


def _validate_probe_receipt(receipt: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    required = (
        "claim_id",
        "passage_id",
        "hypothesis",
        "label",
        "score",
        "raw_logits",
        "model_id",
        "model_revision",
        "config_hash",
        "evidence_path",
    )
    missing = [field for field in required if field not in receipt]
    if missing:
        raise ValueError(f"D6 probe receipt missing fields: {', '.join(missing)}")
    if str(receipt["claim_id"]) != target["claim_id"]:
        raise ValueError("D6 probe receipt claim ID does not match target")
    if str(receipt["passage_id"]) != target["passage_id"]:
        raise ValueError("D6 probe receipt passage ID does not match target")
    recorded_hypothesis = target["trace"]["negation_probe_state"].get("negated_claim")
    if recorded_hypothesis is not None and receipt["hypothesis"] != recorded_hypothesis:
        raise ValueError("D6 probe receipt hypothesis does not match the preserved hypothesis")
    if receipt["label"] not in {"entail", "contradict", "neutral"}:
        raise ValueError("D6 probe receipt has an unknown categorical label")
    if not isinstance(receipt["raw_logits"], list) or len(receipt["raw_logits"]) != 3:
        raise ValueError("D6 probe receipt must contain three raw logits")
    score = float(receipt["score"])
    if not 0.0 <= score <= 1.0:
        raise ValueError("D6 probe score must be between 0 and 1")
    return {
        **receipt,
        "receipt_sha256": canonical_sha256(receipt),
        "assessment_status": "valid" if receipt["label"] == "entail" else "invalid",
    }


def _apply_probe_receipts(packet: dict[str, Any], probe_path: Path | None) -> None:
    if probe_path is None:
        return
    payload = _read_json(probe_path)
    if payload.get("schema_version") != PROBE_SCHEMA_VERSION:
        raise ValueError(f"unsupported D6 probe schema: {payload.get('schema_version')}")
    receipts = payload.get("receipts")
    if not isinstance(receipts, list):
        raise ValueError("D6 probe packet does not contain receipts")
    targets = {(item["claim_id"], item["passage_id"]): item for item in packet["targets"]}
    seen: set[tuple[str, str]] = set()
    for receipt in receipts:
        key = (str(receipt.get("claim_id")), str(receipt.get("passage_id")))
        if key in seen:
            raise ValueError(f"duplicate D6 probe receipt: {key}")
        seen.add(key)
        if key not in targets:
            raise ValueError(f"D6 probe receipt is outside the frozen target universe: {key}")
        target = targets[key]
        validated = _validate_probe_receipt(receipt, target)
        target["probe_receipt"] = validated
        target["assessment"] = {
            "status": validated["assessment_status"],
            "reason": (
                "exact alternative-passage A4 probe entails the structural negation"
                if validated["assessment_status"] == "valid"
                else "exact alternative-passage A4 probe does not entail the structural negation"
            ),
            "operator": "A4_negation_consistency",
            "receipt_sha256": validated["receipt_sha256"],
        }
        target["blockers"] = [
            item
            for item in target["blockers"]
            if item
            not in {"missing_alternative_a4_probe_receipt", "negated_hypothesis_not_recorded"}
        ]
    packet["probe_input"] = _path_record(probe_path)


def _aperture_summary(packet: dict[str, Any]) -> dict[str, Any]:
    by_claim: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for target in packet["targets"]:
        by_claim[target["claim_id"]].append(target)
    summaries: dict[str, Any] = {}
    for claim_id, targets in sorted(by_claim.items()):
        statuses = Counter(item["assessment"]["status"] for item in targets)
        unknown = [
            item["passage_id"] for item in targets if item["assessment"]["status"] == "unknown"
        ]
        summaries[claim_id] = {
            "target_count": len(targets),
            "assessment_counts": dict(sorted(statuses.items())),
            "status": "complete" if not unknown else "unknown",
            "unknown_passage_ids": sorted(unknown),
        }
    return summaries


def build_packet(
    eligibility_path: Path,
    operator_path: Path,
    *,
    claims_path: Path | None = None,
    raw_dir: Path | None = None,
    trace_dir: Path | None = None,
    probe_path: Path | None = None,
    expected_target_count: int | None = EXPECTED_TARGET_COUNT,
) -> dict[str, Any]:
    """Enumerate and assess the frozen D6 target universe without inference."""
    eligibility = _read_json(eligibility_path)
    operator = _read_json(operator_path)
    eligibility_rows = _index_rows(eligibility)
    operator_rows = _index_rows(operator)
    if trace_dir is None:
        trace_dir = Path(str(eligibility["source"]))
    traces, trace_paths = _index_traces(trace_dir)
    claims = _index_claims(claims_path)
    targets = _unknown_targets(operator_rows)
    if expected_target_count is not None and len(targets) != expected_target_count:
        raise ValueError(
            f"D6 target count changed: expected {expected_target_count}, found {len(targets)}"
        )

    rendered_targets: list[dict[str, Any]] = []
    for claim_id, judgment, passage_id, reason in targets:
        if claim_id not in eligibility_rows:
            raise ValueError(f"D6 target claim is absent from eligibility report: {claim_id}")
        if claim_id not in traces:
            raise ValueError(f"D6 target claim is absent from trace packet: {claim_id}")
        rendered_targets.append(
            _target_record(
                claim_id=claim_id,
                judgment=judgment,
                passage_id=passage_id,
                reason=reason,
                eligibility_row=eligibility_rows[claim_id],
                trace=traces[claim_id],
                trace_path=trace_paths[claim_id],
                claim_record=claims.get(claim_id),
                raw_dir=raw_dir,
            )
        )

    rendered_targets.sort(key=lambda item: (item["claim_id"], item["passage_id"]))
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "label": "DEV-only D6 aperture packet; no inference and no production authority",
        "model_inference": False,
        "production_behavior_changed": False,
        "preregistration": "outputs/2026-08-08-d6-aperture-shadow/PREREGISTRATION.md",
        "inputs": {
            "eligibility_report": _path_record(eligibility_path),
            "operator_report": _path_record(operator_path),
            "claims_packet": _path_record(claims_path) if claims_path else None,
            "trace_dir": str(trace_dir.resolve()),
            "raw_dir": str(raw_dir.resolve()) if raw_dir else None,
            "operator_report_target_count": operator.get("n_unknown_judgments"),
        },
        "target_count": len(rendered_targets),
        "target_reason_counts": dict(
            sorted(
                Counter(item["existing_judgment"]["reason"] for item in rendered_targets).items()
            )
        ),
        "hypothesis_state_counts": dict(
            sorted(
                Counter(
                    item["trace"]["negation_probe_state"]["state"] for item in rendered_targets
                ).items()
            )
        ),
        "targets": rendered_targets,
        "probe_input": None,
    }
    _apply_probe_receipts(packet, probe_path)
    packet["aperture_by_claim"] = _aperture_summary(packet)
    packet["assessment_counts"] = dict(
        sorted(Counter(item["assessment"]["status"] for item in rendered_targets).items())
    )
    packet["blocking_target_count"] = sum(
        item["assessment"]["status"] == "unknown" for item in rendered_targets
    )
    packet["target_universe_sha256"] = canonical_sha256(
        [(item["claim_id"], item["passage_id"]) for item in rendered_targets]
    )
    return packet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eligibility-report", type=Path, required=True)
    parser.add_argument("--operator-report", type=Path, required=True)
    parser.add_argument("--claims", type=Path)
    parser.add_argument("--raw-dir", type=Path)
    parser.add_argument("--trace-dir", type=Path)
    parser.add_argument("--probe-receipts", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    packet = build_packet(
        args.eligibility_report,
        args.operator_report,
        claims_path=args.claims,
        raw_dir=args.raw_dir,
        trace_dir=args.trace_dir,
        probe_path=args.probe_receipts,
    )
    rendered = json.dumps(packet, indent=2) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
