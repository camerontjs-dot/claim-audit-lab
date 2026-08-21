"""Verify the landed ``cal-rules-v1.6.0`` A1 guard against the run-05 prototype diff.

The landing plan in ``plans/adr-v1-a1-imperative-hardening.md`` requires the
*package* result — the shipped :func:`claim_audit_lab.v1.features.sentence_type`
with the combined structural guard — to reproduce the run-05 prototype's exact
two-claim diff over the PILOT-001 v1.5 DEV baseline. No model inference is
rerun: recorded retrieval/NLI evidence is replayed through the landed feature
and the current rules layer, and the script fails loudly on any deviation from
the prototype (extra changed claim, missing recovery, regression, F4 case, or
metric drift). PILOT-001 is the Decision-G adaptation set; outputs are DEV
evidence, never validation or a gate.
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
from claim_audit_lab.v1.config import (
    hash_audit_config,
    load_default_audit_config,
    load_rules_file,
)
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.models import AuditConfig, AuditRequest, AuditTrace

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

_V15_RULES_SHA = "99be5382f0e058a4a514bda96c532f28ad43c11c272864e643b9ccbb8e7d6251"
_V15_AUDIT_CONFIG_SHA = "sha256:98c6609c0b540ab477e9855342806b45ed5650a2b6e6e9745b5bdf12a9a0dbd5"
_EXPECTED_RULES_VERSION = "cal-rules-v1.6.0"

# The run-05 prototype's exact two-claim diff (run-metadata.json § changed_features).
_EXPECTED_CHANGES: dict[str, dict[str, Any]] = {
    "rsh-9a1e5f0994c2-c006": {
        "baseline_sentence_type": "imperative",
        "candidate_sentence_type": "declarative",
        "baseline_verdict": "not_checkable",
        "candidate_verdict": "supported",
        "candidate_flags": ["inferred"],
        "candidate_rules": ["B5_degree", "C6c_inferred"],
    },
    "rsh-9a1e5f0994c2-c008": {
        "baseline_sentence_type": "imperative",
        "candidate_sentence_type": "declarative",
        "baseline_verdict": "not_checkable",
        "candidate_verdict": "supported",
        "candidate_flags": ["source_scope_error"],
        "candidate_rules": ["B5_degree", "C6d_source_scope"],
    },
}


def build_package_traces(
    baseline: dict[str, AuditTrace],
    requests: dict[str, AuditRequest],
    config: AuditConfig,
) -> tuple[dict[str, AuditTrace], list[dict[str, Any]]]:
    """Reapply the current rules over the *landed package* sentence type.

    Unlike the run-05 prototype there is no candidate wrapper: the guard under
    test is ``features.sentence_type`` itself.
    """
    rules = VerdictRules(rules_file_sha=config.rules_file_sha)
    candidate = dict(baseline)
    changed: list[dict[str, Any]] = []
    for claim_id, trace in sorted(baseline.items()):
        new_type = features.sentence_type(trace.claim_text)
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


def _assert_landed_surface(config: AuditConfig) -> None:
    """Fail closed unless the shipped rules surface is the landed v1.6.0."""
    rules, current_sha = load_rules_file()
    if rules["rules_version"] != _EXPECTED_RULES_VERSION:
        raise ValueError(
            f"shipped rules_version {rules['rules_version']!r} is not {_EXPECTED_RULES_VERSION!r}"
        )
    if config.rules_file_sha == _V15_RULES_SHA:
        raise ValueError("current config still pins the v1.5 rules file; nothing landed")
    if config.rules_file_sha != current_sha:
        raise ValueError("current config does not pin the shipped rules file")


def _assert_v15_baseline(baseline: dict[str, AuditTrace], config: AuditConfig) -> None:
    """The recorded evidence must be the v1.5 DEV baseline, thresholds unchanged."""
    hashes = {trace.audit_config_hash for trace in baseline.values()}
    if hashes != {_V15_AUDIT_CONFIG_SHA}:
        raise ValueError(f"baseline hashes {sorted(hashes)} are not the v1.5 contract")
    v15_config = config.model_copy(update={"rules_file_sha": _V15_RULES_SHA})
    if hash_audit_config(v15_config) != _V15_AUDIT_CONFIG_SHA:
        raise ValueError(
            "current config differs from the v1.5 baseline beyond rules_file_sha — "
            "thresholds or model revisions drifted; the replay would not be like-for-like"
        )


def verify_landing(
    changed: list[dict[str, Any]],
    summary: dict[str, Any],
    prototype_result_path: Path,
    candidate_result_json: dict[str, Any],
) -> list[str]:
    """Return the receipt lines; raise on any deviation from the prototype."""
    observed = {row["claim_id"]: row for row in changed}
    if set(observed) != set(_EXPECTED_CHANGES):
        raise ValueError(
            f"changed-claim set {sorted(observed)} != prototype {sorted(_EXPECTED_CHANGES)}"
        )
    for claim_id, expected in _EXPECTED_CHANGES.items():
        row = observed[claim_id]
        for key, value in expected.items():
            if row[key] != value:
                raise ValueError(f"{claim_id}: {key} {row[key]!r} != prototype {value!r}")
    gates = {
        "recovered": 2,
        "regressed": 0,
        "changed_but_still_miss": 0,
        "new_gold_supported_to_cal_contradicted": 0,
    }
    for key, value in gates.items():
        if summary[key] != value:
            raise ValueError(f"diff summary {key}={summary[key]!r} != {value!r}")
    prototype = json.loads(prototype_result_path.read_text(encoding="utf-8"))
    if candidate_result_json["agreement"] != prototype["agreement"]:
        raise ValueError(
            "package agreement metrics differ from the run-05 prototype: "
            f"{candidate_result_json['agreement']!r} != {prototype['agreement']!r}"
        )
    return [
        f"changed claims: {sorted(observed)} (exact prototype match)",
        f"diff gates: {gates}",
        f"agreement: {candidate_result_json['agreement']}",
    ]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_landing_verification(args: argparse.Namespace) -> None:
    """Run the replay, verify against the prototype, and write the DEV packet."""
    if args.out.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {args.out}")
    config = load_default_audit_config()
    _assert_landed_surface(config)
    gold = load_gold(args.gold)
    baseline = load_traces(args.baseline_run / "traces")
    _assert_v15_baseline(baseline, config)
    requests = build_request_index(args.packet, config)
    if set(baseline) != set(requests):
        raise ValueError("baseline/packet claim IDs do not align")

    candidate, changed = build_package_traces(baseline, requests, config)
    baseline_result = compute_calibration(baseline, gold, config)
    candidate_result = compute_calibration(candidate, gold, config)
    rows, summary = build_diff_rows(gold, baseline, candidate)
    summary.update(
        {
            "label": "DEV landing verification, not validated and not a gate",
            "changed_features": changed,
        }
    )

    args.out.mkdir(parents=True)
    shutil.copyfile(args.gold, args.out / "gold.dev.yaml")
    write_run_artifacts(args.out, candidate_result, candidate, config, pinned_at=args.pinned_at)
    write_diff(args.out, rows, summary)
    result_json = json.loads((args.out / "calibration-result.json").read_text(encoding="utf-8"))
    receipt = verify_landing(
        changed, summary, args.prototype_run / "calibration-result.json", result_json
    )
    _write_json(
        args.out / "run-metadata.json",
        {
            "label": "DEV landing verification (adaptation set), not validated and not a gate",
            "packet": str(args.packet.resolve()),
            "gold_source": str(args.gold.resolve()),
            "gold_sha256": "sha256:" + _sha256(args.out / "gold.dev.yaml"),
            "baseline_run": str(args.baseline_run.resolve()),
            "prototype_run": str(args.prototype_run.resolve()),
            "audit_config_hash": hash_audit_config(config),
            "rules_file_sha": config.rules_file_sha,
            "baseline_audit_config_hash": _V15_AUDIT_CONFIG_SHA,
            "baseline_rules_file_sha": _V15_RULES_SHA,
            "candidate_rule": (
                "landed package feature: claim_audit_lab.v1.features.sentence_type "
                "with the combined A1 structural guard (cal-rules-v1.6.0)"
            ),
            "changed_features": changed,
            "verification_receipt": receipt,
            "summary": summary,
            "prototype_script": str(Path(__file__).resolve()),
            "prototype_script_sha256": _sha256(Path(__file__)),
            "pinned_at": args.pinned_at,
        },
    )
    (args.out / "README.md").write_text(
        _render_readme(baseline_result, candidate_result, summary, receipt),
        encoding="utf-8",
    )
    print(json.dumps({"verified": True, "receipt": receipt}, sort_keys=True))


def _render_readme(
    baseline: Any, candidate: Any, summary: dict[str, Any], receipt: list[str]
) -> str:
    receipt_lines = "\n".join(f"- {line}" for line in receipt)
    return f"""# PILOT-001 DEV calibration — run 06 A1 landing verification (2026-07-16)

**DEV RESULT — adaptation set, not validated and not a gate.** This is the
`cal-rules-v1.6.0` landing check required by
`plans/adr-v1-a1-imperative-hardening.md`: the recorded v1.5 retrieval/NLI
evidence replayed through the *landed package* `sentence_type`, required to
match the run-05 prototype's exact two-claim diff.

## Outcome

| metric | v1.5.0 baseline | landed v1.6.0 package |
|---|---:|---:|
| exact | {baseline.agreement.n_agree}/{baseline.agreement.n_total} | \
**{candidate.agreement.n_agree}/{candidate.agreement.n_total}** |
| Cohen's κ | {baseline.agreement.cohens_kappa:.4f} | \
**{candidate.agreement.cohens_kappa:.4f}** |
| weighted κ | {baseline.agreement.weighted_kappa:.4f} | \
**{candidate.agreement.weighted_kappa:.4f}** |
| Gwet AC2 | {baseline.agreement.gwet_ac2:.4f} | **{candidate.agreement.gwet_ac2:.4f}** |

- recoveries: **{summary["recovered"]}**;
- regressions: **{summary["regressed"]}**;
- changed-but-still-miss: **{summary["changed_but_still_miss"]}**;
- F4 new gold-supported → CAL-`contradicted`: \
**{summary["new_gold_supported_to_cal_contradicted"]}**.

## Verification receipt

{receipt_lines}

## Boundary

This closes the landing plan's 98-claim DEV replay requirement. It does not
commission the fresh blind packet, clear the Phase 4 gate, or authorize any
release action.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--prototype-run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--pinned-at", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    run_landing_verification(parse_args())
