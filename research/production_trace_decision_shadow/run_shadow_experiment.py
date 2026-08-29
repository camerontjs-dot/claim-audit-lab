#!/usr/bin/env python3
"""Run the preregistered real-production-trace -> explicit-decision shadow experiment.

This file orchestrates existing CAL machinery. It does not implement a second
candidate decision function and does not read the E2E fixture's expected model
outputs or expected verdicts.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.models import AuditRequest, AuditTrace
from claim_audit_lab.v1.runner import run_default_audit
from research.production_trace_decision_shadow.metamorphic_controls import run_controls
from scripts.decision_model_replay import build_report
from scripts.evidence_state_eligibility_shadow import build_eligibility_report
from scripts.evidence_state_operator_shadow import build_operator_report

BASE_SHA = "53f0885b111676794d1bd20e10b91aa58b07e9d4"
CORPUS_PATH = "tests/v1/test_pipeline_e2e.py"
CORPUS_BLOB = "48a22cfab82ea0a2abd8d1c80d0da32a3dacd260"
REPLAY_BLOB = "cb26ba5a5ba9174dedbd686ea10dffcaae1a80db"
DECISION_MODEL_BLOB = "f0d9d3bc061d966ed9c8c16b3424b3dd5c3bb339"
SIGNAL_FLOOR = 0.20
SUPPORT_THRESHOLD = 0.70
REFUTATION_THRESHOLD = 0.70


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def _load_fixture_module(project: Path) -> ModuleType:
    tests_path = project / "tests"
    if str(tests_path) not in sys.path:
        sys.path.insert(0, str(tests_path))
    path = project / CORPUS_PATH
    spec = importlib.util.spec_from_file_location("cal_shadow_frozen_e2e_cases", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen diagnostic corpus module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _assert_frozen_objects(project: Path) -> dict[str, str]:
    observed = {
        CORPUS_PATH: _git("hash-object", str(project / CORPUS_PATH)),
        "scripts/decision_model_replay.py": _git(
            "hash-object", str(project / "scripts/decision_model_replay.py")
        ),
        "src/claim_audit_lab/v1/decision_model.py": _git(
            "hash-object", str(project / "src/claim_audit_lab/v1/decision_model.py")
        ),
    }
    expected = {
        CORPUS_PATH: CORPUS_BLOB,
        "scripts/decision_model_replay.py": REPLAY_BLOB,
        "src/claim_audit_lab/v1/decision_model.py": DECISION_MODEL_BLOB,
    }
    if observed != expected:
        raise RuntimeError(
            "frozen apparatus/corpus drifted from preregistration: "
            + _canonical_json({"expected": expected, "observed": observed})
        )
    return observed


def _source_id(passage_id: str) -> str:
    return passage_id.split("/", 1)[0]


def _trust_map(request: AuditRequest) -> tuple[dict[str, str], list[dict[str, str]]]:
    trust: dict[str, str] = {}
    conflicts: list[dict[str, str]] = []
    for passage in request.passages:
        value = passage.source_meta.get("trust_level")
        if value is None:
            continue
        source_id = _source_id(passage.passage_id)
        prior = trust.get(source_id)
        if prior is not None and prior != value:
            conflicts.append(
                {
                    "source_id": source_id,
                    "first": prior,
                    "second": value,
                    "passage_id": passage.passage_id,
                }
            )
        trust[source_id] = value
    return trust, conflicts


def _agreement(legacy: str, candidate: str) -> bool:
    if legacy == candidate and legacy in {"supported", "contradicted"}:
        return True
    return legacy == "not_checkable" and candidate == "abstain"


def _measurement_invariant(trace: AuditTrace, candidate: dict[str, Any]) -> bool:
    by_id = {
        item["passage_id"]: (item["support_score"], item["refutation_score"])
        for item in candidate["inputs"]["measurements"]
    }
    expected = {
        item.passage_id: (item.p_entail, item.p_contradict) for item in trace.entailment
    }
    return by_id == expected


def _admission_invariant(trace: AuditTrace, candidate: dict[str, Any]) -> bool:
    return tuple(sorted(candidate["inputs"]["admitted_passage_ids"])) == tuple(
        sorted(item.passage_id for item in trace.entailment)
    )


def _unknown_validity(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in candidate["inputs"]["contributions"]
        if item["eligibility"]["status"] == "eligible"
        and item["validity"]["status"] == "unknown"
    ]


def _aggregation_diverged(trace: AuditTrace, candidate: dict[str, Any]) -> bool:
    state = candidate["valid"]["state"]
    label = trace.support_signal.label
    expected = {
        "entail": "support_only",
        "contradict": "refutation_only",
        "neutral": "read_silent",
    }[label]
    return state != expected


def _first_divergence(
    trace: AuditTrace,
    replay_row: dict[str, Any],
) -> str | None:
    candidate = replay_row["candidate"]
    if not _admission_invariant(trace, candidate):
        return "retrieve_admit"
    if not _measurement_invariant(trace, candidate):
        return "measure"
    if candidate["raw"]["state"] != candidate["eligible"]["state"]:
        return "eligibility"
    if (
        candidate["eligible"]["state"] != candidate["valid"]["state"]
        or _unknown_validity(candidate)
    ):
        return "semantic_validity"
    if any(item["status"] != "complete" for item in candidate["inputs"]["apertures"]):
        return "aperture"
    if _aggregation_diverged(trace, candidate):
        return "aggregate"
    if not _agreement(trace.verdict.support_verdict, replay_row["candidate_outcome"]):
        return "resolve"
    return None


def _taxonomy(
    trace: AuditTrace,
    replay_row: dict[str, Any],
    first_divergence: str | None,
) -> tuple[str | None, str]:
    if _agreement(trace.verdict.support_verdict, replay_row["candidate_outcome"]):
        return None, "no_terminal_disagreement"
    candidate = replay_row["candidate"]
    if not _admission_invariant(trace, candidate):
        return "retrieval_admission_difference", "implementation_behavior"
    if not _measurement_invariant(trace, candidate):
        return "measurement_nli_difference", "implementation_behavior"
    if replay_row["adapter_exclusions"]:
        return "adapter_projection_insufficiency", "lost_information"
    if first_divergence == "eligibility":
        return "eligibility_difference", "explicit_policy"
    unknown_validity = _unknown_validity(candidate)
    if unknown_validity:
        operators = {item["validity"]["operator"] for item in unknown_validity}
        if operators & {"refutation_operator_unmeasured", "C6a_numeric_rule_unmeasured"}:
            return "unmeasured_state", "unknown_state"
        return "semantic_validity_operator_difference", "unknown_state"
    if first_divergence == "semantic_validity":
        return "semantic_validity_operator_difference", "explicit_policy"
    if first_divergence == "aperture":
        return "aperture_completeness_difference", "unknown_state"
    if first_divergence == "aggregate":
        return "aggregation_composition_difference", "lost_information"
    if first_divergence == "resolve":
        return "final_decision_policy_difference", "explicit_policy"
    return "unknown_unclassified", "unknown_state"


def _output_coverage(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    legacy_degree_gaps = sum(
        row["legacy"]["verdict"]["support_verdict"] in {"partially_supported", "unsupported"}
        for row in rows
    )
    unknown_validity_cases = sum(
        bool(_unknown_validity(row["explicit"]["candidate"])) for row in rows
    )
    noncomplete_aperture = sum(
        any(
            item["status"] != "complete"
            for item in row["explicit"]["candidate"]["inputs"]["apertures"]
        )
        for row in rows
    )
    return [
        {
            "output": "legacy verdict / reason / flags / citation status / confidence",
            "source": "AuditTrace.verdict",
            "direct": True,
            "legacy_trace_sufficient": True,
            "explicit_model_direct": False,
            "requires_guessing": False,
            "finding": "legacy trace emits the complete current verdict record; explicit decision model does not model flags, citation status, or audit confidence",
        },
        {
            "output": "five-valued support degree",
            "source": "AuditTrace.verdict.support_verdict",
            "direct": True,
            "legacy_trace_sufficient": True,
            "explicit_model_direct": False,
            "requires_guessing": False,
            "observed_counterexamples": legacy_degree_gaps,
            "finding": "candidate terminal vocabulary contains only supported/contradicted plus abstention; partial/unsupported are not representable as terminal degrees",
        },
        {
            "output": "retrieval/admission state and NLI measurements",
            "source": "AuditTrace.retrieval + AuditTrace.entailment",
            "direct": True,
            "legacy_trace_sufficient": True,
            "explicit_model_direct": True,
            "requires_guessing": False,
            "finding": "same admitted passage IDs and p_entail/p_contradict values are receipt-bound into candidate inputs",
        },
        {
            "output": "raw support/refutation evidence state",
            "source": "EvidenceDecisionTrace.raw",
            "direct": True,
            "legacy_trace_sufficient": True,
            "explicit_model_direct": True,
            "requires_guessing": False,
            "finding": "derivable deterministically from the recorded independent channel probabilities at the preregistered signal floor",
        },
        {
            "output": "eligibility state",
            "source": "EvidenceDecisionTrace.eligible",
            "direct": True,
            "legacy_trace_sufficient": False,
            "explicit_model_direct": True,
            "requires_guessing": False,
            "finding": "production AuditTrace drops passage source_meta; this experiment must bind the original AuditRequest as a separate receipt to replay current P1 trust eligibility",
        },
        {
            "output": "semantic validity / operator state",
            "source": "EvidenceDecisionTrace.valid + contribution validity assessments",
            "direct": True,
            "legacy_trace_sufficient": "partial",
            "explicit_model_direct": True,
            "requires_guessing": False,
            "observed_unknown_cases": unknown_validity_cases,
            "finding": "recorded A3/A4 outcomes can be translated; unmeasured refutation/operator semantics remain explicit unknown and non-deciding",
        },
        {
            "output": "aperture / completeness",
            "source": "EvidenceDecisionInput.apertures",
            "direct": True,
            "legacy_trace_sufficient": False,
            "explicit_model_direct": True,
            "requires_guessing": True,
            "observed_noncomplete_cases": noncomplete_aperture,
            "finding": "existing replay only proves completeness over preserved at-floor contribution status; general source/passage-set completeness is not measured by normal AuditTrace",
        },
        {
            "output": "contribution ledger and exact decision basis IDs",
            "source": "EvidenceDecisionInput.contributions + DecisionOutcome.basis_contribution_ids",
            "direct": True,
            "legacy_trace_sufficient": "partial",
            "explicit_model_direct": True,
            "requires_guessing": False,
            "finding": "direct channel contributions are trace-derived; semantic-operator/set contributions require explicit operator receipts and are not fabricated",
        },
        {
            "output": "ordered stage receipts",
            "source": "EvidenceDecisionInput.stage_receipts",
            "direct": True,
            "legacy_trace_sufficient": False,
            "explicit_model_direct": True,
            "requires_guessing": False,
            "finding": "existing replay receipt-binds the stage handoffs, but multiple early stages share one AuditTrace receipt rather than independent execution-state receipts",
        },
        {
            "output": "execution failure distinct from epistemic insufficiency",
            "source": "outside normal AuditTrace / EvidenceDecisionTrace",
            "direct": False,
            "legacy_trace_sufficient": False,
            "explicit_model_direct": False,
            "requires_guessing": False,
            "finding": "missing required stage receipt fails model construction distinctly, but neither current normal trace nor decision trace has a typed execution-failure outcome",
        },
    ]


def _recommended_shape(rows: list[dict[str, Any]]) -> dict[str, Any]:
    has_degree_gap = any(
        row["legacy"]["verdict"]["support_verdict"] in {"partially_supported", "unsupported"}
        for row in rows
    )
    has_unknowns = any(row["comparison"]["taxonomy"] == "unmeasured_state" for row in rows)
    return {
        "A_parallel_epistemic_artifact": {
            "fit": "supported_as_smallest_next_change",
            "why": "preserves current production verdict/flags/citation semantics while exposing richer evidence states without pretending missing validity/aperture state was measured",
        },
        "B_add_explicit_states_to_existing_trace": {
            "fit": "plausible_follow_up_not_yet_authorized",
            "why": "request metadata, generic aperture, and execution state are not all present in AuditTrace; adding only observed missing receipts could remove shadow reconstruction seams",
        },
        "C_replace_legacy_decision_substrate": {
            "fit": "not_supported_by_this_experiment",
            "why": (
                "candidate does not directly represent all current terminal degrees/flags/citation outputs"
                if has_degree_gap
                else "replacement has no demonstrated advantage sufficient to justify production semantic risk"
            ),
        },
        "blocking_unknowns_present": has_unknowns,
    }


def run(output_dir: Path) -> dict[str, Any]:
    project = Path(__file__).resolve().parents[2]
    frozen_objects = _assert_frozen_objects(project)
    module = _load_fixture_module(project)
    cases = tuple(getattr(module, "CASES"))
    if len(cases) != 25:
        raise RuntimeError(f"expected complete frozen CASES collection of 25, observed {len(cases)}")

    config = load_default_audit_config()
    if config.supported_threshold != SUPPORT_THRESHOLD or config.contradicted_threshold != REFUTATION_THRESHOLD:
        raise RuntimeError("current production decision thresholds differ from preregistered 0.70/0.70")

    output_dir.mkdir(parents=True, exist_ok=True)
    case_root = output_dir / "cases"
    rows: list[dict[str, Any]] = []
    adapter_exclusions: list[dict[str, Any]] = []

    for case in cases:
        case_dir = case_root / case.claim_id
        trace_dir = case_dir / "traces"
        trace_dir.mkdir(parents=True, exist_ok=True)
        request = AuditRequest(
            claim_id=case.claim_id,
            claim_text=case.claim,
            passages=case.passages,
            audit_config=config,
        )
        request_path = case_dir / "audit-request.json"
        request_path.write_text(request.model_dump_json(indent=2) + "\n", encoding="utf-8")

        trace = run_default_audit(request)
        trace_path = trace_dir / f"{case.claim_id}.json"
        trace_path.write_text(trace.model_dump_json(indent=2) + "\n", encoding="utf-8")

        trust_by_source, trust_conflicts = _trust_map(request)
        eligibility = build_eligibility_report(
            trace_dir,
            signal_floor=SIGNAL_FLOOR,
            trust_by_source=trust_by_source,
        )
        eligibility_path = case_dir / "eligibility-shadow.json"
        eligibility_path.write_text(json.dumps(eligibility, indent=2) + "\n", encoding="utf-8")

        operator = build_operator_report(eligibility, [])
        operator_path = case_dir / "operator-shadow.json"
        operator_path.write_text(json.dumps(operator, indent=2) + "\n", encoding="utf-8")

        replay = build_report(
            eligibility_path,
            operator_path,
            support_threshold=SUPPORT_THRESHOLD,
            refutation_threshold=REFUTATION_THRESHOLD,
        )
        replay_row = replay["rows"][0]
        first_divergence = _first_divergence(trace, replay_row)
        taxonomy, difference_kind = _taxonomy(trace, replay_row, first_divergence)
        agreement = _agreement(trace.verdict.support_verdict, replay_row["candidate_outcome"])

        per_case_exclusions = list(replay_row["adapter_exclusions"])
        if trust_conflicts:
            per_case_exclusions.extend(
                {"reason": "request-side trust mapping conflict", **item} for item in trust_conflicts
            )
        if per_case_exclusions:
            adapter_exclusions.append(
                {"claim_id": case.claim_id, "exclusions": per_case_exclusions}
            )

        row = {
            "claim_id": case.claim_id,
            "corpus_case_name": case.name,
            "request_receipt_sha256": _sha_file(request_path),
            "trace_receipt_sha256": _sha_file(trace_path),
            "eligibility_receipt_sha256": _sha_file(eligibility_path),
            "operator_receipt_sha256": _sha_file(operator_path),
            "legacy": {
                "verdict": trace.verdict.model_dump(mode="json"),
                "rules_fired": [item.model_dump(mode="json") for item in trace.rules_fired],
                "retrieval": [item.model_dump(mode="json") for item in trace.retrieval],
                "admitted_passage_ids": [item.passage_id for item in trace.entailment],
                "nli_measurements": [item.model_dump(mode="json") for item in trace.entailment],
                "support_signal": trace.support_signal.model_dump(mode="json"),
                "audit_config_hash": trace.audit_config_hash,
                "library_version": trace.library_version,
                "negation_probe": (
                    trace.negation_probe.model_dump(mode="json") if trace.negation_probe else None
                ),
            },
            "explicit": {
                "candidate_outcome": replay_row["candidate_outcome"],
                "candidate": replay_row["candidate"],
                "eligibility_row": eligibility["rows"][0],
                "operator_row": operator["rows"][0],
                "adapter_exclusions": per_case_exclusions,
            },
            "comparison": {
                "agreement": agreement,
                "taxonomy": taxonomy,
                "first_divergence_stage": first_divergence,
                "difference_kind": difference_kind,
                "legacy_outcome": trace.verdict.support_verdict,
                "candidate_outcome": replay_row["candidate_outcome"],
                "candidate_reason": replay_row["candidate"]["decision"]["reason_code"],
            },
        }
        rows.append(row)
        (case_dir / "comparison.json").write_text(
            json.dumps(row, indent=2) + "\n", encoding="utf-8"
        )

    metamorphic = run_controls()
    legacy_counts = Counter(row["legacy"]["verdict"]["support_verdict"] for row in rows)
    candidate_counts = Counter(row["explicit"]["candidate_outcome"] for row in rows)
    taxonomy_counts = Counter(
        row["comparison"]["taxonomy"] for row in rows if row["comparison"]["taxonomy"]
    )
    first_divergence_counts = Counter(
        row["comparison"]["first_divergence_stage"]
        for row in rows
        if row["comparison"]["first_divergence_stage"]
    )
    agreements = sum(bool(row["comparison"]["agreement"]) for row in rows)

    not_checkable_split = Counter()
    for row in rows:
        if row["legacy"]["verdict"]["support_verdict"] != "not_checkable":
            continue
        candidate = row["explicit"]["candidate"]
        key = "|".join(
            [
                candidate["raw"]["state"],
                candidate["eligible"]["state"],
                candidate["valid"]["state"],
                candidate["decision"]["reason_code"],
            ]
        )
        not_checkable_split[key] += 1

    support_to_adverse = sum(
        row["legacy"]["verdict"]["support_verdict"] in {"supported", "partially_supported"}
        and row["explicit"]["candidate_outcome"] == "contradicted"
        for row in rows
    )
    adverse_to_support = sum(
        row["legacy"]["verdict"]["support_verdict"] in {"unsupported", "contradicted"}
        and row["explicit"]["candidate_outcome"] == "supported"
        for row in rows
    )
    raw_evidence_excluded = sum(
        len(row["explicit"]["candidate"]["raw"]["contribution_ids"])
        > len(row["explicit"]["candidate"]["valid"]["contribution_ids"])
        for row in rows
    )
    valid_but_aperture_blocked = sum(
        bool(row["explicit"]["candidate"]["valid"]["contribution_ids"])
        and row["explicit"]["candidate"]["decision"]["reason_code"]
        in {"aperture_unknown", "aperture_incomplete"}
        for row in rows
    )
    mixed_valid = sum(row["explicit"]["candidate"]["valid"]["state"] == "mixed" for row in rows)
    unclassifiable = sum(row["comparison"]["taxonomy"] == "unknown_unclassified" for row in rows)

    coverage = _output_coverage(rows)
    gaps = [
        item
        for item in coverage
        if item["requires_guessing"] or item["explicit_model_direct"] is False
    ]
    if not metamorphic["all_passed"]:
        disposition = "DECISION_MODEL_FALSIFIED"
    elif adapter_exclusions and len(adapter_exclusions) == len(rows):
        disposition = "APERTURE_INSUFFICIENT"
    elif gaps or adapter_exclusions:
        disposition = "SHADOW_COMPATIBLE_WITH_GAPS"
    else:
        disposition = "SHADOW_COMPATIBLE"

    report = {
        "schema_version": "cal-production-trace-decision-shadow-v0.1",
        "experiment_class": "Research Infrastructure / epistemic-machinery",
        "production_behavior_changed": False,
        "threshold_tuning_performed": False,
        "base_sha": BASE_SHA,
        "execution_head_sha": _git("rev-parse", "HEAD"),
        "frozen_objects_git_blob_sha": frozen_objects,
        "corpus": {
            "identity": CORPUS_PATH + "::CASES",
            "git_blob_sha": CORPUS_BLOB,
            "n_cases": len(cases),
            "labels": "pre-existing synthetic software-regression expectations; not consumed as evaluation/tuning gold",
            "model_measurements": "regenerated by current real pinned production retriever + entailer",
        },
        "policy": {
            "signal_floor": SIGNAL_FLOOR,
            "support_threshold": SUPPORT_THRESHOLD,
            "refutation_threshold": REFUTATION_THRESHOLD,
            "selection": "preregistered before execution; production/replay defaults; no search",
        },
        "summary": {
            "total_claims": len(rows),
            "legacy_verdict_counts": dict(sorted(legacy_counts.items())),
            "candidate_outcome_counts": dict(sorted(candidate_counts.items())),
            "agreement_count": agreements,
            "agreement_rate": agreements / len(rows),
            "disagreement_count": len(rows) - agreements,
            "disagreements_by_taxonomy": dict(sorted(taxonomy_counts.items())),
            "first_divergence_stage_counts": dict(sorted(first_divergence_counts.items())),
            "legacy_not_checkable_by_explicit_state": dict(sorted(not_checkable_split.items())),
            "support_to_adverse_transitions": support_to_adverse,
            "adverse_to_support_transitions": adverse_to_support,
            "raw_evidence_present_but_excluded_cases": raw_evidence_excluded,
            "valid_evidence_but_aperture_blocked_cases": valid_but_aperture_blocked,
            "mixed_valid_support_refutation_cases": mixed_valid,
            "adapter_exclusion_claims": len(adapter_exclusions),
            "unclassifiable_cases": unclassifiable,
        },
        "adapter_exclusions": adapter_exclusions,
        "metamorphic": metamorphic,
        "output_coverage": coverage,
        "migration_shapes": _recommended_shape(rows),
        "epistemic_record": {
            "OBSERVED": [
                "real production run_default_audit generated every comparison trace",
                "candidate replay consumed the same admitted passage IDs and recorded p_entail/p_contradict measurements",
                "production AuditTrace does not retain passage source_meta, so request metadata is separately receipt-bound for eligibility replay",
                "unmeasured semantic validity remains explicit unknown in the existing replay adapter",
            ],
            "INFERENCE": [
                "parallel epistemic artifact is the smallest production shape compatible with preserving current outputs while exposing richer evidence state",
                "typed request/eligibility/aperture/execution receipts are candidates for a later additive trace change only where the coverage audit shows an observed gap",
            ],
            "HYPOTHESIS": [
                "a later bounded trace-extension experiment could eliminate request-side and execution-state sidecars without replacing current decision semantics"
            ],
            "UNKNOWN": [
                "correct generic semantic-validity operators for refutation shapes not measured by current production trace",
                "general passage-set/source completeness outside the existing at-floor replay aperture",
                "whether a future candidate policy should represent current partially_supported/unsupported degrees or leave them to a separate reporting layer",
            ],
        },
        "terminal_disposition": disposition,
        "rows": rows,
    }

    report_path = output_dir / "RESULTS.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (output_dir / "RESULTS.sha256").write_text(
        _sha_file(report_path) + "  RESULTS.json\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.output_dir)
    print(
        json.dumps(
            {
                "terminal_disposition": report["terminal_disposition"],
                "summary": report["summary"],
                "metamorphic": {
                    "n_controls": report["metamorphic"]["n_controls"],
                    "n_passed": report["metamorphic"]["n_passed"],
                    "all_passed": report["metamorphic"]["all_passed"],
                },
                "result_sha256": _sha_file(args.output_dir / "RESULTS.json"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
