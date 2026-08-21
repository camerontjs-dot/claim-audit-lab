"""Preregistered SLG-09 negation-consistency trial (DEV; no landing).

Measures the candidate in ``plans/adr-v1-slg09-negation-consistency.md``: an
A4-decided ``contradicted`` verdict is retained only if the pinned entailer also
entails the structurally negated claim from the same contributing premise;
otherwise it safe-lands ``not_checkable/no_entail_signal``. A3 contradictions
are untouched. One script, zero package/rules/config/gold changes; outputs are
DEV evidence under the Decision-G boundary, never validation or a gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from claim_audit_lab.v1 import features
from claim_audit_lab.v1.calibrate import compute_calibration, load_gold
from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.impl.entailer import DeBERTaEntailer
from claim_audit_lab.v1.models import AuditTrace

try:
    from scripts.pilot001_floor_sweep import build_diff_rows, load_traces
    from scripts.pilot001_premise_granularity_run04 import build_request_index
    from scripts.simple_logic_gold_structured_lane import _write_absent_or_identical
    from scripts.slg_entailer_bakeoff import _DIRECT_SHA, _FREEZE_SHA
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from pilot001_floor_sweep import build_diff_rows, load_traces  # type: ignore[no-redef]
    from pilot001_premise_granularity_run04 import (  # type: ignore[no-redef]
        build_request_index,
    )
    from simple_logic_gold_structured_lane import (  # type: ignore[no-redef]
        _write_absent_or_identical,
    )
    from slg_entailer_bakeoff import _DIRECT_SHA, _FREEZE_SHA  # type: ignore[no-redef]

_A4 = "A4_hard_contradiction"
_VERBAL_POS = frozenset({"VERB", "AUX"})
_UNIVERSAL_FIRST_TOKENS = frozenset({"all", "every", "each"})
_DO_SUPPORT = {"VBZ": "does", "VBP": "do", "VBD": "did"}
_SLG_TRUE_REFUTATIONS = ("SLG-02-a1", "SLG-05-a1", "SLG-08-a2")
_SLG_TARGET = "SLG-09-a2"


def negate_claim(claim: str) -> str | None:
    """Return the structural sentential negation of ``claim``, or None to abstain.

    Rule order per the preregistration: compound guard; clause-level negation
    removal; universal-quantifier prefixing; copular-root insertion; auxiliary
    insertion; finite do-support. Anything else abstains — an abstention retains
    the original contradiction (fail-safe direction).
    """
    if ";" in claim or features.is_compound_claim(claim):
        return None
    doc = features._parse(claim)
    tokens = list(doc)

    def rebuild(parts: list[str]) -> str:
        return "".join(parts).strip()

    for tok in tokens:
        if tok.dep_ == "neg" and tok.head.pos_ in _VERBAL_POS:
            parts = [t.text + t.whitespace_ for t in tokens if t.i != tok.i]
            return rebuild(parts)

    first_alpha = next((t for t in tokens if not t.is_space and not t.is_punct), None)
    if (
        first_alpha is not None
        and first_alpha.lower_ in _UNIVERSAL_FIRST_TOKENS
        and features.has_universal_quantifier(claim)
    ):
        stripped = claim.strip()
        return "Not " + stripped[0].lower() + stripped[1:]

    roots = [t for t in tokens if t.dep_ == "ROOT"]
    if not roots:
        return None
    root = roots[0]

    if root.pos_ == "AUX" or root.lemma_ == "be":
        parts = []
        for t in tokens:
            parts.append(t.text + t.whitespace_)
            if t.i == root.i:
                parts[-1] = t.text + " not" + (" " if t.whitespace_ else "")
        return rebuild(parts)

    auxes = [c for c in root.children if c.dep_ in {"aux", "auxpass", "cop"}]
    if auxes:
        first_aux = min(auxes, key=lambda t: t.i)
        parts = []
        for t in tokens:
            parts.append(t.text + t.whitespace_)
            if t.i == first_aux.i:
                parts[-1] = t.text + " not" + (" " if t.whitespace_ else "")
        return rebuild(parts)

    if root.pos_ == "VERB" and root.tag_ in _DO_SUPPORT:
        parts = []
        for t in tokens:
            if t.i == root.i:
                parts.append(f"{_DO_SUPPORT[root.tag_]} not {root.lemma_}{t.whitespace_}")
            else:
                parts.append(t.text + t.whitespace_)
        return rebuild(parts)

    return None


def probe_decision(probe_label: str | None) -> str:
    """Map a probe outcome to the preregistered retention decision."""
    if probe_label is None:
        return "retain-abstained"
    return "retain-confirmed" if probe_label == "entail" else "demote"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if item.is_file():
            digest.update(str(item.relative_to(path)).encode())
            digest.update(item.read_bytes())
    return digest.hexdigest()


def _probe(
    entailer: DeBERTaEntailer, premise: str, claim: str
) -> tuple[str | None, dict[str, Any]]:
    negated = negate_claim(claim)
    if negated is None:
        return None, {"negated_claim": None, "abstained": True}
    result = entailer.entail(negated, premise, passage_id="neg-probe")
    return result.label, {
        "negated_claim": negated,
        "abstained": False,
        "probe_label": result.label,
        "probe_score": result.score,
        "probe_raw_logits": list(result.raw_logits),
    }


def _slg_rows(
    direct: dict[str, Any], facts: dict[str, str], entailer: DeBERTaEntailer
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for atom in direct["atoms"]:
        trace = atom["trace"]
        fired = {rule["rule_id"] for rule in trace["rules_fired"]}
        if atom["cal_observed_relation"] != "refutes" or _A4 not in fired:
            continue
        contrib = trace["support_signal"]["contributing_passage_id"]
        premise = facts[contrib]
        label, record = _probe(entailer, premise, trace["claim_text"])
        decision = probe_decision(label)
        simulated = "insufficient" if decision == "demote" else "refutes"
        rows.append(
            {
                "atom_id": atom["atom_id"],
                "claim_text": trace["claim_text"],
                "contributing_fact_id": contrib,
                "contributing_fact_text": premise,
                "expected_relation": atom["expected_relation"],
                "baseline_relation": atom["cal_observed_relation"],
                "decision": decision,
                "simulated_relation": simulated,
                "simulated_match": simulated == atom["expected_relation"],
                **record,
            }
        )
    return rows


def _pilot_rows(
    baseline: dict[str, AuditTrace],
    passages: dict[str, dict[str, str]],
    entailer: DeBERTaEntailer,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for claim_id, trace in sorted(baseline.items()):
        fired = {rule.rule_id for rule in trace.rules_fired}
        if trace.verdict.support_verdict != "contradicted" or _A4 not in fired:
            continue
        contrib = trace.support_signal.contributing_passage_id
        premise = passages[claim_id][contrib]
        label, record = _probe(entailer, premise, trace.claim_text)
        decision = probe_decision(label)
        rows.append(
            {
                "claim_id": claim_id,
                "claim_text": trace.claim_text,
                "contributing_passage_id": contrib,
                "decision": decision,
                **record,
            }
        )
    return rows


def build_trial_payload(project_root: Path) -> dict[str, Any]:
    """Run both preregistered surfaces and evaluate the stop rules."""
    slg_dir = project_root / "outputs/simple-logic-gold/v0.1-frozen-rev01-2026-07-15"
    frozen_path = slg_dir / "frozen-gold.json"
    direct_path = slg_dir / "direct-cal-run-02.json"
    if _sha256(frozen_path) != _FREEZE_SHA:
        raise ValueError("frozen-gold raw SHA-256 drift")
    if _sha256(direct_path) != _DIRECT_SHA:
        raise ValueError("direct-cal-run-02 raw SHA-256 drift")
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    direct = json.loads(direct_path.read_text(encoding="utf-8"))
    facts = {
        fact["fact_id"]: fact["text"] for case in frozen["frozen_cases"] for fact in case["facts"]
    }

    run06 = project_root / "outputs/pilot-001-dev-calibration/run-06-a1-landing-2026-07-16"
    packet = (
        project_root.parent
        / "scaffold-claims-study/workbench/reproduce/build/pilot-001-v2-audit/bundles"
    )
    gold = load_gold(run06 / "gold.dev.yaml")
    config = load_default_audit_config()
    baseline = load_traces(run06 / "traces")
    requests = build_request_index(packet, config)
    passages = {
        claim_id: {p.passage_id: p.text for p in request.passages}
        for claim_id, request in requests.items()
    }

    entailer = DeBERTaEntailer(revision=config.entailer)
    slg_rows = _slg_rows(direct, facts, entailer)
    pilot_rows = _pilot_rows(baseline, passages, entailer)

    candidate = dict(baseline)
    for row in pilot_rows:
        if row["decision"] != "demote":
            continue
        trace = baseline[row["claim_id"]]
        verdict = trace.verdict.model_copy(
            update={"support_verdict": "not_checkable", "reason": "no_entail_signal"}
        )
        candidate[row["claim_id"]] = trace.model_copy(update={"verdict": verdict})
    baseline_result = compute_calibration(baseline, gold, config)
    candidate_result = compute_calibration(candidate, gold, config)
    _, diff_summary = build_diff_rows(gold, baseline, candidate)

    slg_by_id = {row["atom_id"]: row for row in slg_rows}
    s1_losses = [
        atom_id for atom_id in _SLG_TRUE_REFUTATIONS if slg_by_id[atom_id]["decision"] == "demote"
    ]
    s2_target_demoted = slg_by_id[_SLG_TARGET]["decision"] == "demote"
    s3_new_f4 = diff_summary["new_gold_supported_to_cal_contradicted"]
    gold_by_id = {claim.claim_id: claim.gold_verdict for claim in gold.claims}
    s4_losses = [
        row["claim_id"]
        for row in pilot_rows
        if row["decision"] == "demote" and gold_by_id.get(row["claim_id"]) == "contradicted"
    ]
    stop_rules = {
        "S1_lost_true_refutations": s1_losses,
        "S2_target_demoted": s2_target_demoted,
        "S3_new_gold_supported_to_contradicted": s3_new_f4,
        "S4_lost_correct_pilot_contradictions": s4_losses,
    }
    if s1_losses or s4_losses:
        verdict = "reject"
    elif not s2_target_demoted:
        verdict = "no-benefit"
    else:
        verdict = "keep-candidate"

    def _metrics(result: Any) -> dict[str, Any]:
        return {
            "exact_agree": result.agreement.n_agree,
            "exact_total": result.agreement.n_total,
            "cohens_kappa": result.agreement.cohens_kappa,
            "weighted_kappa": result.agreement.weighted_kappa,
            "gwet_ac2": result.agreement.gwet_ac2,
            "on_scale_n": result.agreement.on_scale_n,
        }

    return {
        "schema_version": "slg09-negation-consistency-trial-v0.1",
        "label": (
            "Preregistered DEV trial only; not validation, gate evidence, or landing authority"
        ),
        "adr": "plans/adr-v1-slg09-negation-consistency.md",
        "bindings": {
            "frozen_gold_sha256": _FREEZE_SHA,
            "direct_baseline_sha256": _DIRECT_SHA,
            "run06_trace_tree_sha256": _tree_sha256(run06 / "traces"),
            "pilot_packet_tree_sha256": _tree_sha256(packet),
            "audit_config_rules_file_sha": config.rules_file_sha,
        },
        "slg": {
            "rows": slg_rows,
            "baseline_comparable_matches": direct["summary"].get("matching_comparable_atoms"),
        },
        "pilot": {
            "rows": pilot_rows,
            "baseline_metrics": _metrics(baseline_result),
            "candidate_metrics": _metrics(candidate_result),
            "diff_summary": {
                key: diff_summary[key]
                for key in (
                    "recovered",
                    "regressed",
                    "changed_but_still_miss",
                    "new_gold_supported_to_cal_contradicted",
                )
            },
        },
        "stop_rules": stop_rules,
        "trial_verdict": verdict,
    }


def run_trial(project_root: Path, output_dir: Path) -> dict[str, Any]:
    """Build the payload twice, require byte identity, write absent-or-identical."""
    first = build_trial_payload(project_root)
    second = build_trial_payload(project_root)
    canonical_first = json.dumps(first, sort_keys=True)
    canonical_second = json.dumps(second, sort_keys=True)
    if canonical_first != canonical_second:
        raise ValueError("trial payload is not repeat-run byte-identical")
    _write_absent_or_identical(output_dir / "trial-summary.json", first)
    (output_dir / "README.md").write_text(_render_readme(first), encoding="utf-8")
    return first


def _render_readme(payload: dict[str, Any]) -> str:
    slg_lines = "\n".join(
        f"- `{row['atom_id']}` (gold `{row['expected_relation']}`): {row['decision']}"
        + (
            f" — probe `{row.get('probe_label')}`@{row.get('probe_score', 0):.4f}"
            if not row["abstained"]
            else " — negator abstained"
        )
        for row in payload["slg"]["rows"]
    )
    pilot_lines = (
        "\n".join(
            f"- `{row['claim_id']}`: {row['decision']}"
            + (" — negator abstained" if row["abstained"] else "")
            for row in payload["pilot"]["rows"]
        )
        or "- (no A4-decided contradictions in the baseline)"
    )
    stop = payload["stop_rules"]
    return f"""# SLG-09 negation-consistency trial — 2026-07-16

**Preregistered DEV trial ({payload["adr"]}); not validation or a gate.**

## Verdict: `{payload["trial_verdict"]}`

## SLG surface

{slg_lines}

## PILOT surface

{pilot_lines}

## Stop rules

- S1 lost true refutations: {stop["S1_lost_true_refutations"] or "none"}
- S2 target SLG-09-a2 demoted: {stop["S2_target_demoted"]}
- S3 new gold-supported → contradicted: {stop["S3_new_gold_supported_to_contradicted"]}
- S4 lost correct PILOT contradictions: {stop["S4_lost_correct_pilot_contradictions"] or "none"}

A `keep-candidate` verdict authorizes nothing by itself; any landing is a separate
operator decision with its own full verification unit.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    workbench = Path(__file__).resolve().parents[1]
    payload = run_trial(workbench.parent, args.out)
    print(
        json.dumps(
            {"trial_verdict": payload["trial_verdict"], "stop_rules": payload["stop_rules"]},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
