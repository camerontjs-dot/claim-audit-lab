"""Prototype coarse-to-fine premise granularity on the PILOT-001 DEV set.

The shipped v1.5.0 pipeline remains passage-level. This tool reuses a complete
v1.5.0 baseline and only revisits claims whose raw passage-level support signal
is neutral and whose final reason is ``no_entail_signal``. It splits the already
floor-admitted parent passages into deterministic spaCy sentence spans, runs the
pinned entailer over those fragments, and evaluates two variants:

* ``s1`` — single sentences only;
* ``s1-s2`` — single sentences plus adjacent two-sentence windows.

All other baseline traces are reused byte-for-byte in memory. PILOT-001 is the
Decision-G development set: outputs are DEV evidence, never validation or a gate.
Fragment IDs are prototype-only and intentionally expose the unresolved trace-
contract question documented in ``plans/adr-v1-premise-granularity.md``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Literal

import spacy
from spacy.language import Language

from claim_audit_lab.contracts.bundle_loader import load_bundle
from claim_audit_lab.v1.calibrate import (
    CalibrationGold,
    CalibrationResult,
    compute_calibration,
    crosswalk_gold,
    load_gold,
)
from claim_audit_lab.v1.config import hash_audit_config, load_default_audit_config
from claim_audit_lab.v1.impl.aggregator import MaxEntailmentAggregator
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.intake import bundle_to_requests
from claim_audit_lab.v1.models import (
    AuditConfig,
    AuditRequest,
    AuditTrace,
    EntailResult,
    Passage,
    RuleFired,
)

try:
    from scripts.pilot001_floor_sweep import (
        build_diff_rows,
        load_traces,
        write_diff,
        write_run_artifacts,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    # Direct ``python scripts/<tool>.py`` execution puts ``scripts/`` rather
    # than the repository root on sys.path. Tests/imported use take the branch
    # above; the operator-facing command uses this sibling-module fallback.
    from pilot001_floor_sweep import (  # type: ignore[no-redef]
        build_diff_rows,
        load_traces,
        write_diff,
        write_run_artifacts,
    )

VariantName = Literal["s1", "s1-s2"]

_SPACY_MODEL = "en_core_web_sm"
_VARIANTS: tuple[VariantName, ...] = ("s1", "s1-s2")


def is_fallback_target(trace: AuditTrace) -> bool:
    """Return whether the trace is a true parent-level NLI-dilution candidate."""
    return (
        trace.support_signal.label == "neutral"
        and trace.verdict.support_verdict == "not_checkable"
        and trace.verdict.support_verdict_reason == "no_entail_signal"
        and bool(trace.entailment)
    )


def build_premise_fragments(
    passage: Passage,
    nlp: Language,
    *,
    window_sizes: tuple[int, ...] = (1,),
) -> list[Passage]:
    """Split ``passage`` into deterministic sentence-window ``Passage`` objects.

    Every spaCy sentence containing at least one alphabetic token is retained.
    No claim-aware or lexical-overlap filter is applied. Window text is sliced
    from the original passage so whitespace/content are attributable to exact
    1-based sentence bounds.
    """
    if not window_sizes or any(width < 1 for width in window_sizes):
        raise ValueError("window_sizes must contain positive integers")
    if len(set(window_sizes)) != len(window_sizes):
        raise ValueError("window_sizes must not contain duplicates")

    doc = nlp(passage.text)
    retained = [
        (ordinal, sentence)
        for ordinal, sentence in enumerate(doc.sents, start=1)
        if any(token.is_alpha for token in sentence)
    ]
    fragments: list[Passage] = []
    for width in window_sizes:
        for offset in range(len(retained) - width + 1):
            window = retained[offset : offset + width]
            start_ordinal, start_span = window[0]
            end_ordinal, end_span = window[-1]
            text = passage.text[start_span.start_char : end_span.end_char].strip()
            if not text:
                continue
            fragment_id = f"{passage.passage_id}#s{start_ordinal:04d}-{end_ordinal:04d}"
            fragments.append(
                Passage(
                    passage_id=fragment_id,
                    text=text,
                    source_meta={
                        **passage.source_meta,
                        "parent_passage_id": passage.passage_id,
                        "premise_sentence_start": str(start_ordinal),
                        "premise_sentence_end": str(end_ordinal),
                        "premise_window_size": str(width),
                    },
                )
            )
    return fragments


def build_request_index(packet: Path, config: AuditConfig) -> dict[str, AuditRequest]:
    """Load the fail-closed packet and return one request per claim ID."""
    requests: dict[str, AuditRequest] = {}
    bundle_dirs = sorted(path for path in packet.iterdir() if path.is_dir())
    if not bundle_dirs:
        raise ValueError(f"no bundle directories found in {packet}")
    for bundle_dir in bundle_dirs:
        contents = load_bundle(bundle_dir)
        for request in bundle_to_requests(contents, config):
            if request.claim_id in requests:
                raise ValueError(f"duplicate packet claim_id: {request.claim_id}")
            requests[request.claim_id] = request
    return requests


def entail_fragments(
    request: AuditRequest,
    baseline: AuditTrace,
    nlp: Language,
    entailer: Any,
) -> tuple[list[Passage], list[EntailResult]]:
    """Entail all S1/S2 fragments for the baseline-admitted parent passages."""
    admitted_parent_ids = {result.passage_id for result in baseline.entailment}
    parent_by_id = {passage.passage_id: passage for passage in request.passages}
    missing = sorted(admitted_parent_ids - set(parent_by_id))
    if missing:
        raise ValueError(f"baseline entailment IDs missing from request: {missing}")

    fragments: list[Passage] = []
    results: list[EntailResult] = []
    for parent_result in baseline.entailment:
        parent = parent_by_id[parent_result.passage_id]
        parent_fragments = build_premise_fragments(parent, nlp, window_sizes=(1, 2))
        fragments.extend(parent_fragments)
        results.extend(
            entailer.entail(request.claim_text, fragment.text, fragment.passage_id)
            for fragment in parent_fragments
        )
    return fragments, results


def build_variant_trace(
    request: AuditRequest,
    baseline: AuditTrace,
    fragments: list[Passage],
    fragment_results: list[EntailResult],
    config: AuditConfig,
    rules: VerdictRules,
    *,
    variant: VariantName,
) -> AuditTrace:
    """Return a prototype trace for one target claim and one fragment variant."""
    widths = {"1"} if variant == "s1" else {"1", "2"}
    selected_fragments = [
        fragment for fragment in fragments if fragment.source_meta["premise_window_size"] in widths
    ]
    selected_ids = {fragment.passage_id for fragment in selected_fragments}
    selected_results = [result for result in fragment_results if result.passage_id in selected_ids]
    combined_results = [*baseline.entailment, *selected_results]
    aggregator = MaxEntailmentAggregator()
    signal = aggregator.aggregate(combined_results)
    verdict, fired = rules.apply(
        claim=request.claim_text,
        features=baseline.features,
        passages=[*request.passages, *selected_fragments],
        retrieval=baseline.retrieval,
        entailment=combined_results,
        support_signal=signal,
        audit_config=config,
    )
    premise_rule = RuleFired(
        rule_id="PG_premise_fallback",
        reason=(
            f"parent-level support signal neutral; evaluated {len(selected_fragments)} "
            f"deterministic premise fragments under variant={variant}"
        ),
    )
    return baseline.model_copy(
        update={
            "entailment": combined_results,
            "support_signal": signal,
            "rules_fired": [premise_rule, *fired],
            "verdict": verdict,
        }
    )


def summarize_variant(
    gold: CalibrationGold,
    baseline: dict[str, AuditTrace],
    candidate: dict[str, AuditTrace],
    baseline_result: CalibrationResult,
    candidate_result: CalibrationResult,
    target_ids: set[str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build the standard diff plus premise-specific safety/metric fields."""
    rows, summary = build_diff_rows(gold, baseline, candidate)
    gold_by_id = {claim.claim_id: claim for claim in gold.claims}

    new_adverse_to_supported: list[str] = []
    correct_not_checkable_regressed: list[str] = []
    supported_target_recoveries: list[str] = []
    partial_target_recoveries: list[str] = []
    for claim_id in sorted(target_ids):
        gold_claim = gold_by_id[claim_id]
        gold_degree = crosswalk_gold(gold_claim.gold_verdict, gold_claim.gold_flags).support_verdict
        baseline_degree = baseline[claim_id].verdict.support_verdict
        candidate_degree = candidate[claim_id].verdict.support_verdict
        if gold_degree in {"unsupported", "contradicted"} and candidate_degree == "supported":
            new_adverse_to_supported.append(claim_id)
        if (
            gold_degree == "not_checkable"
            and baseline_degree == "not_checkable"
            and candidate_degree != "not_checkable"
        ):
            correct_not_checkable_regressed.append(claim_id)
        if gold_degree == "supported" and candidate_degree == "supported":
            supported_target_recoveries.append(claim_id)
        if gold_degree == "partially_supported" and candidate_degree == "partially_supported":
            partial_target_recoveries.append(claim_id)

    summary.update(
        {
            "fallback_targets": len(target_ids),
            "supported_target_recoveries": supported_target_recoveries,
            "partially_supported_target_recoveries": partial_target_recoveries,
            "new_gold_adverse_to_cal_supported": len(new_adverse_to_supported),
            "new_gold_adverse_to_cal_supported_claim_ids": new_adverse_to_supported,
            "baseline_correct_not_checkable_regressed": len(correct_not_checkable_regressed),
            "baseline_correct_not_checkable_regressed_claim_ids": (correct_not_checkable_regressed),
            "baseline_metrics": _metric_payload(baseline_result),
            "candidate_metrics": _metric_payload(candidate_result),
            "metric_delta": {
                "exact_agree": (
                    candidate_result.agreement.n_agree - baseline_result.agreement.n_agree
                ),
                "cohens_kappa": (
                    candidate_result.agreement.cohens_kappa - baseline_result.agreement.cohens_kappa
                ),
                "weighted_kappa": (
                    candidate_result.agreement.weighted_kappa
                    - baseline_result.agreement.weighted_kappa
                ),
                "gwet_ac2": (
                    candidate_result.agreement.gwet_ac2 - baseline_result.agreement.gwet_ac2
                ),
            },
            "deciding_fragment_claims": sorted(
                claim_id
                for claim_id in target_ids
                if "#s" in (candidate[claim_id].support_signal.contributing_passage_id or "")
            ),
        }
    )
    return rows, summary


def _metric_payload(result: CalibrationResult) -> dict[str, Any]:
    return {
        "exact_agree": result.agreement.n_agree,
        "exact_total": result.agreement.n_total,
        "cohens_kappa": result.agreement.cohens_kappa,
        "weighted_kappa": result.agreement.weighted_kappa,
        "gwet_ac2": result.agreement.gwet_ac2,
        "on_scale_n": result.agreement.on_scale_n,
    }


def _assert_baseline(
    baseline: dict[str, AuditTrace],
    requests: dict[str, AuditRequest],
    gold: CalibrationGold,
    config: AuditConfig,
) -> None:
    expected_ids = {claim.claim_id for claim in gold.claims}
    for name, observed in (("baseline", set(baseline)), ("packet", set(requests))):
        missing = sorted(expected_ids - observed)
        extra = sorted(observed - expected_ids)
        if missing or extra:
            raise ValueError(f"{name}/gold alignment failed: missing={missing}, extra={extra}")
    expected_hash = hash_audit_config(config)
    hashes = {trace.audit_config_hash for trace in baseline.values()}
    if hashes != {expected_hash}:
        raise ValueError(
            "baseline is not the current shipped config: "
            f"trace_hashes={sorted(hashes)}, expected={expected_hash}"
        )
    mismatched_claims = sorted(
        claim_id
        for claim_id, request in requests.items()
        if request.claim_text != baseline[claim_id].claim_text
    )
    if mismatched_claims:
        raise ValueError(f"packet/baseline claim-text mismatch: {mismatched_claims}")


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _copy_if_absent_or_identical(source: Path, destination: Path) -> None:
    if destination.exists():
        if source.read_bytes() != destination.read_bytes():
            raise FileExistsError(f"refusing to replace non-identical {destination}")
        return
    shutil.copyfile(source, destination)


def _render_readme(
    baseline: CalibrationResult,
    summaries: dict[VariantName, dict[str, Any]],
    *,
    target_gold_counts: Counter[str],
) -> str:
    lines = [
        "# PILOT-001 DEV calibration — run 04 premise granularity (2026-07-10)",
        "",
        "**DEV RESULT — adaptation set, not validated and not a gate.** PILOT-001 is",
        "the development set under Decision G. The packaged baseline is v1.5.0; the two",
        "premise variants are prototype-only and do not change package code or frozen rules.",
        "",
        "## Baseline",
        "",
        f"- Exact: **{baseline.agreement.n_agree}/{baseline.agreement.n_total}**.",
        f"- Cohen's κ: **{baseline.agreement.cohens_kappa:.4f}**.",
        f"- Weighted κ: **{baseline.agreement.weighted_kappa:.4f}**.",
        f"- Gwet AC2: **{baseline.agreement.gwet_ac2:.4f}**.",
        f"- Raw-neutral fallback targets: **{sum(target_gold_counts.values())}** "
        f"(gold: {dict(sorted(target_gold_counts.items()))}).",
        "",
        "The landed package baseline is verdict/rule-fire identical on all 98 claims to",
        "Decision-H run-03 Stage 1; only the expected v1.5.0 audit-config hash differs.",
        "",
        "## Variant results",
        "",
        "| variant | exact | weighted κ | AC2 | recovered | regressed | F4 | adverse→supported |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for variant in _VARIANTS:
        summary = summaries[variant]
        metrics = summary["candidate_metrics"]
        lines.append(
            "| "
            f"{variant} | {metrics['exact_agree']}/{metrics['exact_total']} | "
            f"{metrics['weighted_kappa']:.4f} | {metrics['gwet_ac2']:.4f} | "
            f"{summary['recovered']} | {summary['regressed']} | "
            f"{summary['new_gold_supported_to_cal_contradicted']} | "
            f"{summary['new_gold_adverse_to_cal_supported']} |"
        )

    lines.extend(
        [
            "",
            "## Safety and disposition",
            "",
        ]
    )
    for variant in _VARIANTS:
        summary = summaries[variant]
        lines.extend(
            [
                f"### {variant}",
                "",
                f"- Supported-target recoveries: "
                f"{summary['supported_target_recoveries'] or 'none'}.",
                f"- Partially-supported-target recoveries: "
                f"{summary['partially_supported_target_recoveries'] or 'none'}.",
                f"- F4 new gold-supported → CAL-contradicted: "
                f"{summary['new_gold_supported_to_cal_contradicted']}.",
                f"- New gold-adverse → CAL-supported: "
                f"{summary['new_gold_adverse_to_cal_supported']} "
                f"{summary['new_gold_adverse_to_cal_supported_claim_ids']}.",
                f"- Baseline-correct not_checkable regressions: "
                f"{summary['baseline_correct_not_checkable_regressed']} "
                f"{summary['baseline_correct_not_checkable_regressed_claim_ids']}.",
                "",
            ]
        )

    lines.extend(
        [
            "The trace-contract blocker remains even if a variant looks better: fragment IDs",
            "are not first-class request/retrieval objects in v1. A package landing requires",
            "Cameron's explicit choice of sentence-span provenance and a fresh rules/package",
            "unit. None of these DEV numbers commission or clear the fresh blind gate.",
            "",
            "## Artifacts",
            "",
            "- `baseline-v1.5/` — current packaged calibration report + 98 traces.",
            "- `variant-s1/` and `variant-s1-s2/` — report, traces, config, result,",
            "  per-claim diff, and summary.",
            "- `run-metadata.json` — provenance, target IDs, model/config pins, fragment",
            "  counts, and variant summaries.",
            "",
        ]
    )
    return "\n".join(lines)


def run_experiment(args: argparse.Namespace) -> None:
    """Execute the two premise variants and write DEV evidence artifacts."""
    config = load_default_audit_config()
    gold = load_gold(args.gold)
    baseline = load_traces(args.baseline_run / "traces")
    requests = build_request_index(args.packet, config)
    _assert_baseline(baseline, requests, gold, config)
    baseline_result = compute_calibration(baseline, gold, config)

    variant_dirs = {variant: args.out / f"variant-{variant}" for variant in _VARIANTS}
    existing = [path for path in variant_dirs.values() if path.exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite existing variant outputs: {existing}")
    args.out.mkdir(parents=True, exist_ok=True)
    gold_copy = args.out / "gold.dev.yaml"
    _copy_if_absent_or_identical(args.gold, gold_copy)

    target_ids = {claim_id for claim_id, trace in baseline.items() if is_fallback_target(trace)}
    gold_by_id = {claim.claim_id: claim for claim in gold.claims}
    target_gold_counts = Counter(
        crosswalk_gold(
            gold_by_id[claim_id].gold_verdict,
            gold_by_id[claim_id].gold_flags,
        ).support_verdict
        for claim_id in target_ids
    )

    nlp = spacy.load(_SPACY_MODEL, disable=["ner"])
    from claim_audit_lab.v1.impl.entailer import DeBERTaEntailer

    entailer = DeBERTaEntailer(revision=config.entailer)
    rules = VerdictRules(rules_file_sha=config.rules_file_sha)
    candidates: dict[VariantName, dict[str, AuditTrace]] = {
        variant: dict(baseline) for variant in _VARIANTS
    }
    fragment_counts: dict[str, dict[str, int]] = {}
    total_targets = len(target_ids)
    for index, claim_id in enumerate(sorted(target_ids), start=1):
        print(
            f"premise fallback {index}/{total_targets}: {claim_id}",
            file=sys.stderr,
            flush=True,
        )
        fragments, fragment_results = entail_fragments(
            requests[claim_id], baseline[claim_id], nlp, entailer
        )
        counts = Counter(fragment.source_meta["premise_window_size"] for fragment in fragments)
        fragment_counts[claim_id] = {
            "s1": counts["1"],
            "s2": counts["2"],
            "nli_calls": len(fragment_results),
        }
        for variant in _VARIANTS:
            candidates[variant][claim_id] = build_variant_trace(
                requests[claim_id],
                baseline[claim_id],
                fragments,
                fragment_results,
                config,
                rules,
                variant=variant,
            )
        _write_json(
            args.out / "progress.json",
            {
                "label": "DEV prototype, not validated and not a gate",
                "completed": index,
                "total": total_targets,
                "last_claim_id": claim_id,
                "fragment_counts": fragment_counts,
            },
        )

    summaries: dict[VariantName, dict[str, Any]] = {}
    for variant in _VARIANTS:
        result = compute_calibration(candidates[variant], gold, config)
        output_dir = variant_dirs[variant]
        write_run_artifacts(
            output_dir,
            result,
            candidates[variant],
            config,
            pinned_at=args.pinned_at,
        )
        rows, summary = summarize_variant(
            gold,
            baseline,
            candidates[variant],
            baseline_result,
            result,
            target_ids,
        )
        summary["variant"] = variant
        write_diff(output_dir, rows, summary)
        summaries[variant] = summary

    model_meta = nlp.meta
    metadata = {
        "label": "DEV prototype (adaptation set), not validated and not a gate",
        "packet": str(args.packet.resolve()),
        "gold_source": str(args.gold.resolve()),
        "gold_copy": str(gold_copy.resolve()),
        "gold_sha256": _sha256(gold_copy),
        "baseline_run": str(args.baseline_run.resolve()),
        "baseline_audit_config_hash": hash_audit_config(config),
        "baseline_metrics": _metric_payload(baseline_result),
        "fallback_trigger": (
            "raw support_signal neutral + final not_checkable/no_entail_signal + "
            "at least one parent entailment"
        ),
        "target_claim_ids": sorted(target_ids),
        "target_gold_counts": dict(sorted(target_gold_counts.items())),
        "fragment_counts": fragment_counts,
        "fragment_nli_calls_total": sum(counts["nli_calls"] for counts in fragment_counts.values()),
        "spacy": {
            "library_version": spacy.__version__,
            "model": _SPACY_MODEL,
            "model_version": model_meta.get("version"),
        },
        "retriever": config.retriever.model_dump(mode="json"),
        "entailer": config.entailer.model_dump(mode="json"),
        "rules_file_sha": config.rules_file_sha,
        "prototype_script": str(Path(__file__).resolve()),
        "prototype_script_sha256": _sha256(Path(__file__)),
        "pinned_at": args.pinned_at,
        "variants": summaries,
        "trace_contract_warning": (
            "prototype fragment IDs are not first-class AuditRequest/retrieval objects; "
            "do not land without the premise-span provenance decision"
        ),
    }
    _write_json(args.out / "run-metadata.json", metadata)
    (args.out / "README.md").write_text(
        _render_readme(
            baseline_result,
            summaries,
            target_gold_counts=target_gold_counts,
        ),
        encoding="utf-8",
    )
    (args.out / "progress.json").unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--pinned-at", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    run_experiment(parse_args())
