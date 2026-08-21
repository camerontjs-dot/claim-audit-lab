"""Replay the preregistered E3 A1 secondary-predicate candidate without inference.

This is DEV craft evidence only.  It never changes package features, rules,
configuration, gold, or preserved traces.  The candidate is intentionally fixed
by the trial preregistration, including its known negative-imperative canary.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from claim_audit_lab.v1 import features
from claim_audit_lab.v1.calibrate import compute_calibration, load_gold
from claim_audit_lab.v1.config import hash_audit_config, load_default_audit_config
from claim_audit_lab.v1.explicit_claims import (
    AtomAuditTrace,
    ExplicitClaimRequest,
    ExplicitClaimTrace,
    aggregate_explicit_claim_verdicts,
    hash_explicit_claim_request,
    serialize_explicit_claim_trace,
)
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.models import AuditRequest, AuditTrace, SentenceType

try:
    from scripts.pilot001_floor_sweep import build_diff_rows, load_traces
    from scripts.pilot001_premise_granularity_run04 import build_request_index
    from scripts.simple_logic_gold_structured_lane import (
        _canonical_json,
        _write_absent_or_identical,
        load_structured_inputs,
        run_structured_suite,
        suite_is_green,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from pilot001_floor_sweep import build_diff_rows, load_traces  # type: ignore[no-redef]
    from pilot001_premise_granularity_run04 import (  # type: ignore[no-redef]
        build_request_index,
    )
    from simple_logic_gold_structured_lane import (  # type: ignore[no-redef]
        _canonical_json,
        _write_absent_or_identical,
        load_structured_inputs,
        run_structured_suite,
        suite_is_green,
    )

_E3_RESULT_SHA256 = "c571f9e19e3cf73a3db4d767fbff1432c175cce94afc6ab6cab6b79579075648"
_ALLOWED_IMPERATIVE_PREFIX_DEPS = frozenset({"intj", "advmod"})
_SUBJECT_DEPS = frozenset({"nsubj", "nsubjpass", "expl"})
_VERBAL_POS = frozenset({"VERB", "AUX"})
_CANARIES: tuple[tuple[str, SentenceType], ...] = (
    (
        "The guidance links annual reviews to statistical process control and trend analysis.",
        "declarative",
    ),
    (
        "Change control systems must document impacts and involve the quality unit.",
        "declarative",
    ),
    ("Valve V1 passed inspection.", "declarative"),
    ("Valve V2 passed inspection.", "declarative"),
    ("Valve V3 passed inspection.", "declarative"),
    ("Validate the system before release.", "imperative"),
    ("Please validate the system before release.", "imperative"),
    ("Kindly validate the system before release.", "imperative"),
    ("Never release the batch.", "imperative"),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_sentence_type(claim: str) -> SentenceType:
    """Apply the fixed prefix guard plus non-root subject-bearing predicate guard."""
    current = features.sentence_type(claim)
    if current != "imperative":
        return current
    doc = features._parse(claim)
    root = next(token for token in doc if token.dep_ == "ROOT")
    prefix = [token for token in doc[: root.i] if not token.is_space and not token.is_punct]
    if not all(token.dep_ in _ALLOWED_IMPERATIVE_PREFIX_DEPS for token in prefix):
        return "declarative"
    if any(
        token is not root
        and token.pos_ in _VERBAL_POS
        and any(child.dep_ in _SUBJECT_DEPS for child in token.children)
        for token in doc
    ):
        return "declarative"
    return "imperative"


def canary_report() -> dict[str, Any]:
    """Return fixed canary outcomes and parser receipts."""
    records: list[dict[str, Any]] = []
    for claim, expected in _CANARIES:
        doc = features._parse(claim)
        observed = candidate_sentence_type(claim)
        records.append(
            {
                "claim": claim,
                "expected": expected,
                "current": features.sentence_type(claim),
                "candidate": observed,
                "match": observed == expected,
                "parse": [
                    {
                        "text": token.text,
                        "pos": token.pos_,
                        "dep": token.dep_,
                        "head": token.head.text,
                    }
                    for token in doc
                ],
            }
        )
    failures = [
        {"claim": record["claim"], "expected": record["expected"], "observed": record["candidate"]}
        for record in records
        if not record["match"]
    ]
    return {
        "denominator": len(records),
        "matching": len(records) - len(failures),
        "failures": failures,
        "records": records,
    }


def _validate_source_trace(request: ExplicitClaimRequest, trace: ExplicitClaimTrace) -> None:
    if trace.request_sha256 != hash_explicit_claim_request(request):
        raise ValueError("preserved explicit trace does not bind the assembled request")
    if (
        trace.parent_claim_id != request.parent_claim_id
        or trace.parent_claim_text != request.parent_claim_text
        or trace.operator != request.operator
    ):
        raise ValueError("preserved explicit trace parent binding drift")
    if trace.audit_config_hash != hash_audit_config(request.audit_config):
        raise ValueError("preserved explicit trace config binding drift")
    if len(trace.atom_audits) != len(request.atoms):
        raise ValueError("preserved explicit trace atom count drift")
    for request_atom, trace_atom in zip(request.atoms, trace.atom_audits, strict=True):
        if (
            request_atom.atom_id != trace_atom.atom_id
            or request_atom.claim_text != trace_atom.claim_text
            or request_atom.provenance != trace_atom.provenance
        ):
            raise ValueError("preserved explicit trace atom binding drift")


def _trace_map(suite: dict[str, Any]) -> dict[str, ExplicitClaimTrace]:
    results = [suite["baseline"], suite["exact_baseline_rerun"]["result"]]
    results.extend(item["result"] for item in suite["metamorphic"].values())
    results.append(suite["wording_variants"]["result"])
    mapped: dict[str, ExplicitClaimTrace] = {}
    for result in results:
        for parent in result["frozen_parents"]:
            trace = ExplicitClaimTrace.model_validate_json(
                json.dumps(parent["explicit_trace"], ensure_ascii=False)
            )
            previous = mapped.get(trace.request_sha256)
            if previous is not None and serialize_explicit_claim_trace(
                previous
            ) != serialize_explicit_claim_trace(trace):
                raise ValueError("duplicate preserved request hash has non-identical traces")
            mapped[trace.request_sha256] = trace
    return mapped


def _candidate_explicit_trace(
    request: ExplicitClaimRequest,
    source: ExplicitClaimTrace,
    rules: VerdictRules,
) -> tuple[ExplicitClaimTrace, list[dict[str, Any]]]:
    _validate_source_trace(request, source)
    changed: list[dict[str, Any]] = []
    atom_audits: list[AtomAuditTrace] = []
    for request_atom, source_atom in zip(request.atoms, source.atom_audits, strict=True):
        source_audit = source_atom.audit_trace
        new_type = candidate_sentence_type(request_atom.claim_text)
        if new_type == source_audit.features.sentence_type:
            candidate_audit = source_audit
        else:
            new_features = source_audit.features.model_copy(update={"sentence_type": new_type})
            verdict, fired = rules.apply(
                claim=request_atom.claim_text,
                features=new_features,
                passages=request.passages,
                retrieval=source_audit.retrieval,
                entailment=source_audit.entailment,
                support_signal=source_audit.support_signal,
                audit_config=request.audit_config,
            )
            candidate_audit = AuditTrace.model_validate(
                source_audit.model_copy(
                    update={"features": new_features, "verdict": verdict, "rules_fired": fired}
                ).model_dump(mode="python")
            )
            changed.append(
                {
                    "request_sha256": source.request_sha256,
                    "parent_claim_id": request.parent_claim_id,
                    "atom_id": request_atom.atom_id,
                    "claim_text": request_atom.claim_text,
                    "baseline_sentence_type": source_audit.features.sentence_type,
                    "candidate_sentence_type": new_type,
                    "baseline_verdict": source_audit.verdict.support_verdict,
                    "candidate_verdict": verdict.support_verdict,
                    "candidate_rules": [rule.rule_id for rule in fired],
                }
            )
        atom_audits.append(
            AtomAuditTrace(
                atom_id=request_atom.atom_id,
                claim_text=request_atom.claim_text,
                provenance=request_atom.provenance,
                audit_trace=candidate_audit,
            )
        )
    aggregation = aggregate_explicit_claim_verdicts(
        request.operator, [atom.audit_trace.verdict for atom in atom_audits]
    )
    candidate = ExplicitClaimTrace(
        request_sha256=hash_explicit_claim_request(request),
        parent_claim_id=request.parent_claim_id,
        parent_claim_text=request.parent_claim_text,
        operator=request.operator,
        atom_audits=atom_audits,
        parent_aggregation=aggregation,
        verdict=aggregation.verdict,
        audit_config_hash=source.audit_config_hash,
        library_version=source.library_version,
    )
    return candidate, changed


def replay_e3(
    *,
    preserved_suite_path: Path,
    frozen_path: Path,
    structure_path: Path,
    variants_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Replay the fixed A1 candidate across the complete preserved E3 suite."""
    if _sha256(preserved_suite_path) != _E3_RESULT_SHA256:
        raise ValueError("preserved E3 suite raw SHA-256 drift")
    preserved = json.loads(preserved_suite_path.read_text(encoding="utf-8"))
    traces = _trace_map(preserved)
    inputs = load_structured_inputs(frozen_path, structure_path, variants_path)
    config = load_default_audit_config()
    rules = VerdictRules(rules_file_sha=config.rules_file_sha)
    changed: list[dict[str, Any]] = []

    def runner(request: ExplicitClaimRequest) -> ExplicitClaimTrace:
        request_sha = hash_explicit_claim_request(request)
        if request_sha not in traces:
            raise ValueError(f"preserved E3 suite lacks request {request_sha}")
        candidate, request_changes = _candidate_explicit_trace(request, traces[request_sha], rules)
        changed.extend(request_changes)
        return candidate

    suite = run_structured_suite(inputs, runner)
    unique_changes = {(item["request_sha256"], item["atom_id"]): item for item in changed}
    summary = {
        "input_suite_sha256": _E3_RESULT_SHA256,
        "audit_config_hash": hash_audit_config(config),
        "baseline_scores": suite["baseline_scores"],
        "exact_baseline_rerun": {
            key: suite["exact_baseline_rerun"][key]
            for key in ("serialized_byte_identical", "baseline_sha256", "rerun_sha256")
        },
        "metamorphic_invariance": {
            name: value["invariance"] for name, value in suite["metamorphic"].items()
        },
        "wording_score": suite["wording_variants"]["frozen_semantic_targets"],
        "suite_is_green": suite_is_green(suite),
        "changed_trace_atoms": [unique_changes[key] for key in sorted(unique_changes)],
    }
    return suite, summary


def _metrics(result: Any) -> dict[str, Any]:
    return {
        "exact_agree": result.agreement.n_agree,
        "exact_total": result.agreement.n_total,
        "cohens_kappa": result.agreement.cohens_kappa,
        "weighted_kappa": result.agreement.weighted_kappa,
        "gwet_ac2": result.agreement.gwet_ac2,
        "on_scale_n": result.agreement.on_scale_n,
    }


def replay_pilot(*, baseline_run: Path, packet: Path, gold_path: Path) -> dict[str, Any]:
    """Replay the fixed candidate over all 98 preserved PILOT-001 DEV traces."""
    config = load_default_audit_config()
    baseline = load_traces(baseline_run / "traces")
    requests = build_request_index(packet, config)
    gold = load_gold(gold_path)
    gold_claim_ids = {claim.claim_id for claim in gold.claims}
    if set(baseline) != set(requests) or set(baseline) != gold_claim_ids:
        raise ValueError("PILOT baseline, requests, and gold do not align")
    expected_hash = hash_audit_config(config)
    if {trace.audit_config_hash for trace in baseline.values()} != {expected_hash}:
        raise ValueError("PILOT trace config binding drift")
    rules = VerdictRules(rules_file_sha=config.rules_file_sha)
    candidate = dict(baseline)
    changed: list[dict[str, Any]] = []
    for claim_id, trace in sorted(baseline.items()):
        new_type = candidate_sentence_type(trace.claim_text)
        if new_type == trace.features.sentence_type:
            continue
        new_features = trace.features.model_copy(update={"sentence_type": new_type})
        request: AuditRequest = requests[claim_id]
        verdict, fired = rules.apply(
            claim=trace.claim_text,
            features=new_features,
            passages=request.passages,
            retrieval=trace.retrieval,
            entailment=trace.entailment,
            support_signal=trace.support_signal,
            audit_config=config,
        )
        candidate[claim_id] = AuditTrace.model_validate(
            trace.model_copy(
                update={"features": new_features, "verdict": verdict, "rules_fired": fired}
            ).model_dump(mode="python")
        )
        changed.append(
            {
                "claim_id": claim_id,
                "claim_text": trace.claim_text,
                "baseline_sentence_type": trace.features.sentence_type,
                "candidate_sentence_type": new_type,
                "baseline_verdict": trace.verdict.support_verdict,
                "candidate_verdict": verdict.support_verdict,
                "candidate_rules": [rule.rule_id for rule in fired],
            }
        )
    baseline_result = compute_calibration(baseline, gold, config)
    candidate_result = compute_calibration(candidate, gold, config)
    rows, diff = build_diff_rows(gold, baseline, candidate)
    return {
        "label": "DEV replay only; not validation or gate evidence",
        "audit_config_hash": expected_hash,
        "baseline_metrics": _metrics(baseline_result),
        "candidate_metrics": _metrics(candidate_result),
        "changed_features": changed,
        "diff_summary": diff,
        "changed_rows": [
            row for row in rows if row["baseline_verdict"] != row["candidate_verdict"]
        ],
    }


def build_trial_payload(project_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run both recorded-trace replays and return summary plus candidate E3 suite."""
    e3_dir = (
        project_root
        / "outputs/simple-logic-gold/v0.1-frozen-rev01-2026-07-15/e3-structured-direct-v0.1"
    )
    frozen_dir = e3_dir.parent
    e3_suite, e3_summary = replay_e3(
        preserved_suite_path=e3_dir / "structured-direct-run-01.json",
        frozen_path=frozen_dir / "frozen-gold.json",
        structure_path=e3_dir / "explicit-structure-v0.1.yaml",
        variants_path=e3_dir / "wording-variants-v0.1.yaml",
    )
    run05_metadata = json.loads(
        (
            project_root
            / "outputs/pilot-001-dev-calibration/run-05-a1-imperative-2026-07-10/run-metadata.json"
        ).read_text(encoding="utf-8")
    )
    pilot_summary = replay_pilot(
        baseline_run=Path(run05_metadata["baseline_run"]),
        packet=Path(run05_metadata["packet"]),
        gold_path=Path(run05_metadata["gold_source"]),
    )
    canaries = canary_report()
    e3_scores = e3_summary["baseline_scores"]
    e3_expected = (
        e3_scores["frozen_semantic_targets"]["matching"] == 14
        and e3_scores["runtime_construction_atoms"]["matching"] == 18
        and e3_scores["frozen_parents"]["matching"] == 9
        and e3_summary["exact_baseline_rerun"]["serialized_byte_identical"] is True
        and all(
            not layer["failures"]
            for transform in e3_summary["metamorphic_invariance"].values()
            for layer in transform.values()
        )
        and e3_summary["wording_score"]["matching"] == 3
    )
    pilot_metrics = pilot_summary["candidate_metrics"]
    pilot_diff = pilot_summary["diff_summary"]
    pilot_expected = (
        pilot_metrics["exact_agree"] == 64
        and pilot_metrics["exact_total"] == 98
        and pilot_diff["recovered"] == 2
        and pilot_diff["regressed"] == 0
        and pilot_diff["new_gold_supported_to_cal_contradicted"] == 0
        and len(pilot_summary["changed_features"]) == 2
    )
    criteria = {
        "canaries": not canaries["failures"],
        "e3_replay": e3_expected,
        "pilot_dev_replay": pilot_expected,
    }
    summary = {
        "schema_version": "e3-a1-secondary-predicate-trial-v0.1",
        "label": "DEV craft trial only; not validation, gate evidence, or landing authority",
        "candidate_rule": {
            "allowed_pre_root_dependencies": sorted(_ALLOWED_IMPERATIVE_PREFIX_DEPS),
            "secondary_subject_dependencies": sorted(_SUBJECT_DEPS),
            "secondary_verbal_pos": sorted(_VERBAL_POS),
        },
        "canaries": canaries,
        "e3": e3_summary,
        "pilot_001_dev": pilot_summary,
        "criteria": criteria,
        "all_criteria_pass": all(criteria.values()),
        "recommended_verdict": "keep" if all(criteria.values()) else "iterate",
        "next_hypothesis": (
            "permit parser dependency neg in the pre-root imperative modifier set, then rerun the "
            "same fixed canaries and trace replays"
            if not criteria["canaries"]
            else None
        ),
    }
    return summary, e3_suite


def run_trial(project_root: Path, output_dir: Path) -> dict[str, Any]:
    """Execute once from recorded evidence and write absent-or-identical artifacts."""
    summary, e3_suite = build_trial_payload(project_root)
    _write_absent_or_identical(output_dir / "trial-summary.json", summary)
    _write_absent_or_identical(output_dir / "e3-candidate-suite.json", e3_suite)
    return summary


def main() -> None:
    workbench = Path(__file__).resolve().parents[1]
    project_root = workbench.parent
    output_dir = project_root / "outputs/2026-07-15-e3-a1-secondary-predicate-guard"
    summary = run_trial(project_root, output_dir)
    print(
        _canonical_json(
            {
                "criteria": summary["criteria"],
                "recommended_verdict": summary["recommended_verdict"],
            }
        )
    )


if __name__ == "__main__":
    main()
