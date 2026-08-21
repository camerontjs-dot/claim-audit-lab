"""Measure a non-landing bidirectional NLI contradiction consistency prototype.

This DEV-only measurement does not edit CAL source, rules, configuration, or
gold. It asks whether a high-confidence A4 contradiction remains high-confidence
contradiction when the premise/hypothesis direction is reversed. The candidate
would safely demote a directionally inconsistent contradiction to not_checkable;
it is rejected immediately if it loses any correct PILOT-001 contradiction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.calibrate import compute_calibration, crosswalk_gold, load_gold
from claim_audit_lab.v1.config import hash_audit_config, load_default_audit_config
from claim_audit_lab.v1.impl.entailer import DeBERTaEntailer
from claim_audit_lab.v1.models import AuditTrace, Verdict
from scripts.pilot001_floor_sweep import load_traces
from scripts.pilot001_premise_granularity_run04 import build_request_index


def _sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _tree_sha256(path: Path) -> str:
    """Hash a tree as sorted relative POSIX paths plus raw file bytes."""
    if not path.is_dir():
        raise ValueError(f"tree hash requires a directory: {path}")
    digest = hashlib.sha256()
    files = sorted(candidate for candidate in path.rglob("*") if candidate.is_file())
    if not files:
        raise ValueError(f"tree hash requires at least one file: {path}")
    for file_path in files:
        digest.update(file_path.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _write_absent_or_identical(path: Path, payload: dict[str, Any]) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise FileExistsError(f"refusing to overwrite non-identical prototype output: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _a4_contradiction(trace: AuditTrace) -> bool:
    return (
        trace.verdict.support_verdict == "contradicted"
        and trace.support_signal.label == "contradict"
        and any(rule.rule_id == "A4_hard_contradiction" for rule in trace.rules_fired)
    )


def _candidate_verdict(
    trace: AuditTrace,
    reverse_label: str,
    reverse_score: float,
    contradicted_threshold: float,
) -> Verdict:
    """Return the non-landing guard's simulated verdict without changing CAL."""
    if not _a4_contradiction(trace):
        return trace.verdict
    if reverse_label == "contradict" and reverse_score >= contradicted_threshold:
        return trace.verdict
    return Verdict(
        support_verdict="not_checkable",
        support_verdict_reason="no_entail_signal",
        audit_flags=[],
        citation_status=trace.verdict.citation_status,
        audit_confidence="low",
    )


def _contributing_text(trace: AuditTrace, passage_texts: dict[str, str]) -> str:
    passage_id = trace.support_signal.contributing_passage_id
    if passage_id is None or passage_id not in passage_texts:
        raise ValueError(f"{trace.claim_id}: missing contributing passage text")
    return passage_texts[passage_id]


def _trace_from_json_payload(payload: dict[str, Any]) -> AuditTrace:
    """Restore strict tuple fields after a JSON-mode ``AuditTrace`` serialization."""
    restored = json.loads(json.dumps(payload))
    for entailment in restored.get("entailment", []):
        if isinstance(entailment.get("raw_logits"), list):
            entailment["raw_logits"] = tuple(entailment["raw_logits"])
    return AuditTrace.model_validate(restored)


def _reverse_record(
    trace: AuditTrace,
    passage_texts: dict[str, str],
    entailer: Any,
    contradicted_threshold: float,
) -> tuple[dict[str, Any], AuditTrace]:
    if not _a4_contradiction(trace):
        return (
            {
                "claim_id": trace.claim_id,
                "eligible": False,
                "baseline_verdict": trace.verdict.support_verdict,
                "candidate_verdict": trace.verdict.support_verdict,
            },
            trace,
        )
    contributing_text = _contributing_text(trace, passage_texts)
    reverse = entailer.entail(
        contributing_text,
        trace.claim_text,
        f"{trace.support_signal.contributing_passage_id}#reverse",
    )
    candidate_verdict = _candidate_verdict(
        trace,
        reverse.label,
        reverse.score,
        contradicted_threshold,
    )
    changed = candidate_verdict != trace.verdict
    return (
        {
            "claim_id": trace.claim_id,
            "eligible": True,
            "baseline_verdict": trace.verdict.support_verdict,
            "forward_label": trace.support_signal.label,
            "forward_score": trace.support_signal.max_entailment_score,
            "contributing_passage_id": trace.support_signal.contributing_passage_id,
            "reverse_label": reverse.label,
            "reverse_score": reverse.score,
            "candidate_verdict": candidate_verdict.support_verdict,
            "candidate_reason": candidate_verdict.support_verdict_reason,
            "changed": changed,
        },
        trace.model_copy(update={"verdict": candidate_verdict}),
    )


def run_prototype(
    *,
    simple_frozen: Path,
    simple_run: Path,
    pilot_packet: Path,
    pilot_gold: Path,
    pilot_traces_dir: Path,
    entailer_factory: Callable[[Any], Any] = DeBERTaEntailer,
) -> dict[str, Any]:
    """Measure the single permitted non-lexical candidate against both DEV baselines."""
    config = load_default_audit_config()
    frozen = json.loads(simple_frozen.read_text(encoding="utf-8"))
    simple = json.loads(simple_run.read_text(encoding="utf-8"))
    if simple.get("frozen_file_sha256") != _sha256(simple_frozen):
        raise ValueError("Simple Logic Gold run does not bind the supplied frozen artifact")
    if simple.get("frozen_freeze_identifier") != frozen.get("freeze_identifier"):
        raise ValueError("Simple Logic Gold run/freeze identifier mismatch")
    facts_by_case = {
        case["base_case_id"]: {fact["fact_id"]: fact["text"] for fact in case["facts"]}
        for case in frozen["frozen_cases"]
    }
    entailer = entailer_factory(config.entailer)

    simple_records: list[dict[str, Any]] = []
    for atom in simple["atoms"]:
        trace = _trace_from_json_payload(atom["trace"])
        record, _ = _reverse_record(
            trace,
            facts_by_case[atom["base_case_id"]],
            entailer,
            config.contradicted_threshold,
        )
        record["expected_relation"] = atom["expected_relation"]
        record["atom_id"] = atom["atom_id"]
        simple_records.append(record)

    pilot_baseline = load_traces(pilot_traces_dir)
    requests = build_request_index(pilot_packet, config)
    if set(requests) != set(pilot_baseline):
        raise ValueError("PILOT request/traces claim IDs do not align")
    pilot_candidate: dict[str, AuditTrace] = {}
    pilot_records: list[dict[str, Any]] = []
    for claim_id, trace in sorted(pilot_baseline.items()):
        passages = {passage.passage_id: passage.text for passage in requests[claim_id].passages}
        record, candidate_trace = _reverse_record(
            trace,
            passages,
            entailer,
            config.contradicted_threshold,
        )
        pilot_records.append(record)
        pilot_candidate[claim_id] = candidate_trace

    gold = load_gold(pilot_gold)
    baseline_metrics = compute_calibration(pilot_baseline, gold, config)
    candidate_metrics = compute_calibration(pilot_candidate, gold, config)
    gold_by_id = {
        claim.claim_id: crosswalk_gold(claim.gold_verdict, claim.gold_flags)
        for claim in gold.claims
    }
    lost_correct_contradictions = [
        claim_id
        for claim_id, candidate in pilot_candidate.items()
        if gold_by_id[claim_id].support_verdict == "contradicted"
        and pilot_baseline[claim_id].verdict.support_verdict == "contradicted"
        and candidate.verdict.support_verdict != "contradicted"
    ]
    new_supported_to_contradicted = [
        claim_id
        for claim_id, candidate in pilot_candidate.items()
        if gold_by_id[claim_id].support_verdict == "supported"
        and pilot_baseline[claim_id].verdict.support_verdict != "contradicted"
        and candidate.verdict.support_verdict == "contradicted"
    ]
    changed = [record["claim_id"] for record in pilot_records if record.get("changed")]
    exact_regressions = []
    recoveries = []
    changed_but_still_miss = []
    for claim_id, candidate in pilot_candidate.items():
        gold_degree = gold_by_id[claim_id].support_verdict
        baseline_degree = pilot_baseline[claim_id].verdict.support_verdict
        candidate_degree = candidate.verdict.support_verdict
        row = {
            "claim_id": claim_id,
            "gold": gold_degree,
            "baseline": baseline_degree,
            "candidate": candidate_degree,
        }
        if baseline_degree == gold_degree and candidate_degree != gold_degree:
            exact_regressions.append(row)
        elif baseline_degree != gold_degree and candidate_degree == gold_degree:
            recoveries.append(row)
        elif baseline_degree != candidate_degree:
            changed_but_still_miss.append(row)
    return {
        "schema_version": "slg09-bidirectional-contradiction-prototype-v0.1",
        "label": (
            "DEV prototype only; not a CAL landing, validation, representative metric, or gate"
        ),
        "candidate": {
            "name": "bidirectional_high_contradiction_consistency",
            "rule": (
                "retain an A4 contradiction only when reverse NLI is also contradict at >= "
                f"{config.contradicted_threshold}"
            ),
            "contradicted_threshold": config.contradicted_threshold,
            "nonlexical": True,
            "landing_status": "not proposed",
        },
        "inputs": {
            "simple_frozen_sha256": _sha256(simple_frozen),
            "simple_run_sha256": _sha256(simple_run),
            "pilot_gold_sha256": _sha256(pilot_gold),
            "pilot_packet_tree_sha256": _tree_sha256(pilot_packet),
            "pilot_trace_directory": str(pilot_traces_dir.resolve()),
            "pilot_trace_tree_sha256": _tree_sha256(pilot_traces_dir),
            "pilot_trace_count": len(pilot_baseline),
            "audit_config_hash": hash_audit_config(config),
            "audit_config_snapshot": config.model_dump(mode="json"),
        },
        "simple_logic_gold": simple_records,
        "pilot001": {
            "records": pilot_records,
            "baseline_metrics": baseline_metrics.model_dump(mode="json"),
            "candidate_metrics": candidate_metrics.model_dump(mode="json"),
            "candidate_metric_carriers_only": (
                "Candidate AuditTrace objects are metric carriers only; they retain baseline "
                "retrieval/entailment/rule receipts and are not replayable candidate traces."
            ),
            "changed_claim_ids": changed,
            "diff": {
                "recoveries": recoveries,
                "exact_regressions": exact_regressions,
                "changed_but_still_miss": changed_but_still_miss,
            },
            "hard_stops": {
                "new_gold_supported_to_contradicted": new_supported_to_contradicted,
                "lost_correct_contradictions": lost_correct_contradictions,
                "hidden_gold_specific_rule": False,
            },
        },
    }


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simple-frozen", type=Path, required=True)
    parser.add_argument("--simple-run", type=Path, required=True)
    parser.add_argument("--pilot-packet", type=Path, required=True)
    parser.add_argument("--pilot-gold", type=Path, required=True)
    parser.add_argument("--pilot-traces", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run_prototype(
            simple_frozen=args.simple_frozen,
            simple_run=args.simple_run,
            pilot_packet=args.pilot_packet,
            pilot_gold=args.pilot_gold,
            pilot_traces_dir=args.pilot_traces,
        )
        _write_absent_or_identical(args.out, result)
    except (FileExistsError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(result["pilot001"]["hard_stops"], sort_keys=True))


if __name__ == "__main__":
    _main()
