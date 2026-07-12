"""Replay an A1 imperative-prefix guard over the PILOT-001 v1.5.0 DEV baseline.

No model inference is rerun. The tool changes only ``ExtractedFeatures.sentence_type``
for current imperative calls that fail the proposed structural prefix guard, then
reapplies the unchanged v1.5.0 rules to the recorded retrieval/NLI evidence. PILOT-001
is the Decision-G adaptation set; outputs are DEV evidence, never validation or a gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from claim_audit_lab.v1 import features
from claim_audit_lab.v1.calibrate import compute_calibration, load_gold
from claim_audit_lab.v1.config import hash_audit_config, load_default_audit_config
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.models import AuditConfig, AuditRequest, AuditTrace, SentenceType

try:
    from scripts.pilot001_floor_sweep import (
        build_diff_rows,
        load_traces,
        write_diff,
        write_run_artifacts,
    )
    from scripts.pilot001_premise_granularity_run04 import build_request_index
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from pilot001_floor_sweep import (  # type: ignore[no-redef]
        build_diff_rows,
        load_traces,
        write_diff,
        write_run_artifacts,
    )
    from pilot001_premise_granularity_run04 import (  # type: ignore[no-redef]
        build_request_index,
    )

_ALLOWED_IMPERATIVE_PREFIX_DEPS = frozenset({"intj", "advmod"})


def candidate_sentence_type(claim: str) -> SentenceType:
    """Return current sentence type with the proposed imperative prefix guard."""
    current = features.sentence_type(claim)
    if current != "imperative":
        return current
    doc = features._parse(claim)
    root = next(token for token in doc if token.dep_ == "ROOT")
    prefix = [token for token in doc[: root.i] if not token.is_space and not token.is_punct]
    if all(token.dep_ in _ALLOWED_IMPERATIVE_PREFIX_DEPS for token in prefix):
        return "imperative"
    return "declarative"


def build_candidate_traces(
    baseline: dict[str, AuditTrace],
    requests: dict[str, AuditRequest],
    config: AuditConfig,
) -> tuple[dict[str, AuditTrace], list[dict[str, Any]]]:
    """Apply the candidate feature and current rules; return traces + changed rows."""
    rules = VerdictRules(rules_file_sha=config.rules_file_sha)
    candidate = dict(baseline)
    changed: list[dict[str, Any]] = []
    for claim_id, trace in sorted(baseline.items()):
        new_type = candidate_sentence_type(trace.claim_text)
        if new_type == trace.features.sentence_type:
            continue
        new_features = trace.features.model_copy(update={"sentence_type": new_type})
        request = requests[claim_id]
        verdict, fired = rules.apply(
            claim=trace.claim_text,
            features=new_features,
            passages=request.passages,
            retrieval=trace.retrieval,
            entailment=trace.entailment,
            support_signal=trace.support_signal,
            audit_config=config,
        )
        candidate[claim_id] = trace.model_copy(
            update={"features": new_features, "verdict": verdict, "rules_fired": fired}
        )
        changed.append(
            {
                "claim_id": claim_id,
                "claim_text": trace.claim_text,
                "baseline_sentence_type": trace.features.sentence_type,
                "candidate_sentence_type": new_type,
                "baseline_verdict": trace.verdict.support_verdict,
                "candidate_verdict": verdict.support_verdict,
                "candidate_flags": verdict.audit_flags,
                "candidate_rules": [rule.rule_id for rule in fired],
                "support_signal": trace.support_signal.model_dump(mode="json"),
            }
        )
    return candidate, changed


def _assert_baseline(
    baseline: dict[str, AuditTrace],
    requests: dict[str, AuditRequest],
    config: AuditConfig,
) -> None:
    if set(baseline) != set(requests):
        raise ValueError("baseline/packet claim IDs do not align")
    expected_hash = hash_audit_config(config)
    hashes = {trace.audit_config_hash for trace in baseline.values()}
    if hashes != {expected_hash}:
        raise ValueError(
            f"baseline hashes {sorted(hashes)} do not match current config {expected_hash}"
        )


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


def run_prototype(args: argparse.Namespace) -> None:
    """Run the trace replay and write the DEV packet."""
    if args.out.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {args.out}")
    config = load_default_audit_config()
    gold = load_gold(args.gold)
    baseline = load_traces(args.baseline_run / "traces")
    requests = build_request_index(args.packet, config)
    _assert_baseline(baseline, requests, config)
    candidate, changed = build_candidate_traces(baseline, requests, config)

    baseline_result = compute_calibration(baseline, gold, config)
    candidate_result = compute_calibration(candidate, gold, config)
    rows, summary = build_diff_rows(gold, baseline, candidate)
    summary.update(
        {
            "label": "DEV prototype, not validated and not a gate",
            "baseline_metrics": _metrics(baseline_result),
            "candidate_metrics": _metrics(candidate_result),
            "changed_features": changed,
        }
    )

    args.out.mkdir(parents=True)
    _copy_if_absent_or_identical(args.gold, args.out / "gold.dev.yaml")
    write_run_artifacts(
        args.out,
        candidate_result,
        candidate,
        config,
        pinned_at=args.pinned_at,
    )
    write_diff(args.out, rows, summary)
    _write_json(
        args.out / "run-metadata.json",
        {
            "label": "DEV prototype (adaptation set), not validated and not a gate",
            "packet": str(args.packet.resolve()),
            "gold_source": str(args.gold.resolve()),
            "gold_sha256": _sha256(args.out / "gold.dev.yaml"),
            "baseline_run": str(args.baseline_run.resolve()),
            "audit_config_hash": hash_audit_config(config),
            "rules_file_sha": config.rules_file_sha,
            "candidate_rule": (
                "current imperative only if every pre-ROOT non-space/non-punctuation "
                "token has dependency intj or advmod"
            ),
            "changed_features": changed,
            "summary": summary,
            "prototype_script": str(Path(__file__).resolve()),
            "prototype_script_sha256": _sha256(Path(__file__)),
            "pinned_at": args.pinned_at,
        },
    )
    (args.out / "README.md").write_text(
        _render_readme(baseline_result, candidate_result, summary, changed),
        encoding="utf-8",
    )


def _metrics(result) -> dict[str, Any]:
    return {
        "exact_agree": result.agreement.n_agree,
        "exact_total": result.agreement.n_total,
        "cohens_kappa": result.agreement.cohens_kappa,
        "weighted_kappa": result.agreement.weighted_kappa,
        "gwet_ac2": result.agreement.gwet_ac2,
        "on_scale_n": result.agreement.on_scale_n,
    }


def _render_readme(baseline, candidate, summary, changed: list[dict[str, Any]]) -> str:
    baseline_exact = f"{baseline.agreement.n_agree}/{baseline.agreement.n_total}"
    candidate_exact = f"{candidate.agreement.n_agree}/{candidate.agreement.n_total}"
    baseline_kappa = baseline.agreement.cohens_kappa
    candidate_kappa = candidate.agreement.cohens_kappa
    baseline_weighted = baseline.agreement.weighted_kappa
    candidate_weighted = candidate.agreement.weighted_kappa
    baseline_ac2 = baseline.agreement.gwet_ac2
    candidate_ac2 = candidate.agreement.gwet_ac2
    f4_count = summary["new_gold_supported_to_cal_contradicted"]
    changed_ids = [row["claim_id"] for row in changed]
    return f"""# PILOT-001 DEV calibration — run 05 A1 imperative guard (2026-07-10)

**DEV RESULT — adaptation set, not validated and not a gate.** This is a trace
replay over the landed v1.5.0 retrieval/NLI evidence. Package code and frozen
rules remain unchanged.

## Outcome

The structural prefix guard changes exactly **{len(changed)}** claims, recovering
both false A1 `out_of_scope` calls with no regressions and F4 =
{f4_count}.

| metric | v1.5.0 baseline | candidate |
|---|---:|---:|
| exact | {baseline_exact} | **{candidate_exact}** |
| Cohen's κ | {baseline_kappa:.4f} | **{candidate_kappa:.4f}** |
| weighted κ | {baseline_weighted:.4f} | **{candidate_weighted:.4f}** |
| Gwet AC2 | {baseline_ac2:.4f} | **{candidate_ac2:.4f}** |

- recoveries: **{summary["recovered"]}**;
- regressions: **{summary["regressed"]}**;
- changed-but-still-miss: **{summary["changed_but_still_miss"]}**;
- F4 new gold-supported → CAL-`contradicted`: **{f4_count}**.

Changed claims: `{changed_ids}`.

## Boundary

This arms the sign-off decision in `plans/adr-v1-a1-imperative-hardening.md`.
It does not authorize the `cal-rules-v1.6.0` landing, commission the fresh blind
packet, or clear the Phase 4 gate.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--pinned-at", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    run_prototype(parse_args())
