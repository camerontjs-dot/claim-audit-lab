"""PILOT-001 absence-route prototype rerun (run 03) — Decision H, Stage 1 (+ optional Stage 2).

DEV TOOLING. PILOT-001 is the Decision-G development set: every artifact this
script writes is *dev*, never validated and never a gate.

This is the run-03 harness specified by
``plans/absence-route-execution-plan.md`` (§4). It measures, in-process over the
sealed 98-claim packet, what argument alone cannot settle about the absence
route:

* **Stage 1** — a suppression loop *around* signal selection (no edits to any
  packaged rule). Each iteration re-aggregates the floor-admitted entailment
  pool with the stock ``MaxEntailmentAggregator`` and applies the stock
  ``VerdictRules`` (``cal-rules-v1.4.0``). If the resulting degree is adverse
  and its contributing passage is ineligible (``trust_level != "primary"``,
  **P1**) or is a MoNLI double-negation mirror (**P2**), that passage is removed
  and the pool re-aggregated. Ineligible passages stay in the trace; they just
  cannot decide. Landing is emergent: an empty/all-neutral pool aggregates to
  neutral → B5 → ``not_checkable/no_entail_signal`` (never adverse).
* **Stage 2** (variant ``stage-1+2`` only) — the bundle-relative absence route
  (**S2**, gold heuristic 4): a negated claim that Stage 1 landed at
  ``not_checkable/no_entail_signal`` with no eligible primary passage asserting
  the negated content returns ``supported``.

The provenance signal Stage 1 needs is joined prototype-side (**D1**): intake
drops ``trust_level``, so ``enrich_requests_with_trust`` re-adds it before
audit. **No package source or packaged config is edited** — the entire
prototype lives in this one script (the real landing is ``cal-rules-v1.5.0``,
governed by §7 of the plan, only after this run's evidence and a second go).

Provenance honesty: unlike run-02, the ``audit_config_hash`` does **not** change
(the config is untouched; the *logic* changed). Run-03 traces are
distinguishable from run-01's only by their ``rules_fired`` and directory, so
``run-metadata.json`` records the script's own SHA-256, the workbench HEAD, the
stage2 flag per variant, the dev label, the gold SHA, the packet path, and the
pinned timestamp.

Two deviations from the plan-as-written, approved 2026-07-07 after pre-flight
verification against the run-01 traces (documented in the run README):

1. **Smoke case ``c016`` → ``c002``.** The plan's §4.6 ``rsh-bffa73dfe56a-c016``
   smoke assertion ("→ supported, P1 fired") was a floor-0.30 observation (run-02
   README): at floor 0.40 the contradicting fiction passage is below floor, so
   c016 is already ``supported`` with no fiction contradict to suppress and P1
   cannot fire. The real "fiction contradict decides an absence claim" case in
   that bundle is ``c017``; the clean loop-plus-eligible-signal case is
   ``rsh-475fe956a5fb-c002``, which this script smoke-tests instead.
2. **§5.1 gold-supported-absence-miss recipe gains a negation filter.** The
   literal recipe ``A4-8 ∩ gold-supported-slot`` yields 5 because it admits the
   primary-driven, non-absence canary ``rsh-475fe956a5fb-c003`` (``neg=False``);
   restricting to ``has_explicit_negation`` yields the intended 4. ``c003``
   stays tracked as the canary (§5.3 quantity 3).

Usage (from the workbench venv; smoke first, always)::

    python scripts/pilot001_absence_route_run03.py --packet ... --gold ... \\
      --baseline-run ... --out ... --pinned-at 2026-07-07T00:00:00Z --smoke
    python scripts/pilot001_absence_route_run03.py --packet ... --gold ... \\
      --baseline-run ... --out ... --pinned-at 2026-07-07T00:00:00Z
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# The reusable run-02 tooling is imported as a sibling module. Its argparse is
# under ``__main__`` so importing it is side-effect-free, and its module top is
# deliberately torch-free (this script relies on that: heavy inference layers are
# imported lazily in ``make_prototype_auditor``).
from pilot001_floor_sweep import (  # noqa: E402  (sibling script, sys.path[0])
    _assert_baseline_config,
    _sha256,
    _write_json,
    build_diff_rows,
    load_traces,
    write_diff,
    write_run_artifacts,
)

from claim_audit_lab.contracts.bundle_loader import BundleContents, load_bundle
from claim_audit_lab.v1.calibrate import (
    CalibrationGold,
    CalibrationResult,
    compute_calibration,
    crosswalk_gold,
    load_gold,
)
from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.features import expresses_negation
from claim_audit_lab.v1.impl.aggregator import MaxEntailmentAggregator
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.intake import bundle_to_requests
from claim_audit_lab.v1.models import (
    AuditConfig,
    AuditRequest,
    AuditTrace,
    RuleFired,
    Verdict,
)

_ADVERSE = frozenset({"unsupported", "contradicted"})
# Raw gold verdicts that occupy a positive/support slot (§5.1).
_GOLD_SUPPORTED_SLOT = frozenset({"supported", "partially_supported", "reasonable_inference"})
_EXPECTED_GOLD_SHA = "31a1451b6e2633d4e948fe5e1cccbea85491fce96683d200633bda2e21f0930b"
_FICTION_PREFIX = "src-fictional-compliance-review-note/"
_DEV_LABEL = "dev (adaptation set), not validated and not a gate"

# New rule ids — stable from prototype through the v1.5.0 landing (§3).
_P1 = "P1_eligibility_suppressed"
_P2 = "P2_absence_mirror_suppressed"
_S2 = "S2_absence_bundle"


# --------------------------------------------------------------------------- #
# §4.2 — D1 provenance join (prototype-side enrichment)                        #
# --------------------------------------------------------------------------- #
def enrich_requests_with_trust(contents: BundleContents, config: AuditConfig) -> list[AuditRequest]:
    """``bundle_to_requests`` + the D1 provenance join, prototype-side.

    Fails loudly (``KeyError``) if a passage's source has no profile — the
    fail-closed loader guarantees it cannot happen, so a raise means the world
    changed.
    """
    trust = {sid: profile.trust_level for sid, profile in contents.source_profiles.items()}
    enriched: list[AuditRequest] = []
    for request in bundle_to_requests(contents, config):
        passages = [
            passage.model_copy(
                update={
                    "source_meta": {
                        **passage.source_meta,
                        "trust_level": trust[passage.source_meta["source_id"]],
                    }
                }
            )
            for passage in request.passages
        ]
        enriched.append(request.model_copy(update={"passages": passages}))
    return enriched


# --------------------------------------------------------------------------- #
# §4.4 — prototype rules (protocol-compatible wrapper — the heart of run-03)   #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class AbsenceRoutePrototypeRules:
    """Suppression loop around the stock verdict rules.

    Matches ``VerdictRules.apply``'s signature so ``run_audit`` needs no changes;
    the incoming ``support_signal`` is deliberately ignored (the loop
    re-aggregates the pool itself). The trace's ``support_signal`` therefore
    stays the raw aggregator signal the pipeline stamped; the suppression story
    lives entirely in ``rules_fired``.
    """

    stock: VerdictRules
    stage2: bool

    def apply(  # noqa: PLR0913 (signature is fixed by the Rules protocol)
        self,
        *,
        claim: str,
        features: Any,
        passages: Any,
        retrieval: Any,
        entailment: Any,
        support_signal: Any,
        audit_config: Any,
    ) -> tuple[Verdict, list[RuleFired]]:
        aggregator = MaxEntailmentAggregator()
        by_id = {passage.passage_id: passage for passage in passages}
        pool = list(entailment)
        suppressions: list[RuleFired] = []
        while True:
            signal = aggregator.aggregate(pool)
            verdict, fired = self.stock.apply(
                claim=claim,
                features=features,
                passages=passages,
                retrieval=retrieval,
                entailment=pool,
                support_signal=signal,
                audit_config=audit_config,
            )
            suppression = _stage1_guard(
                verdict, signal, by_id.get(signal.contributing_passage_id), features
            )
            if suppression is None:
                fired = [*suppressions, *fired]
                if self.stage2:
                    stage2 = _stage2_absence(verdict, features, by_id, entailment)
                    if stage2 is not None:
                        verdict, s2_fired = stage2
                        fired = [*fired, s2_fired]
                return verdict, fired
            suppressions.append(suppression)
            pool = [r for r in pool if r.passage_id != signal.contributing_passage_id]


def _stage1_guard(
    verdict: Verdict, signal: Any, contributing: Any, features: Any
) -> RuleFired | None:
    """Return a suppression ``RuleFired`` if the adverse degree may not stand, else None.

    P1 (eligibility, D2) is checked before P2 (A3-mirror, D3); at most one
    suppression is returned per iteration.
    """
    if verdict.support_verdict not in _ADVERSE or contributing is None:
        return None
    trust = contributing.source_meta.get("trust_level")
    if trust != "primary":  # P1 — eligibility precondition (D2)
        return RuleFired(
            rule_id=_P1,
            reason=(
                f"{signal.label} {signal.max_entailment_score:.2f} from "
                f"{contributing.passage_id} (trust_level={trust!r}) may not "
                "solo-decide an adverse degree → suppressed, re-aggregating"
            ),
        )
    if (
        features.has_explicit_negation
        and signal.label == "contradict"
        and expresses_negation(contributing.text)
    ):  # P2 — A3-mirror (D3)
        return RuleFired(
            rule_id=_P2,
            reason=(
                f"negated claim; contradicting passage {contributing.passage_id} "
                "itself expresses the negation (agrees with the claim) — MoNLI "
                "mirror → suppressed, re-aggregating"
            ),
        )
    return None


def _stage2_absence(
    verdict: Verdict, features: Any, by_id: dict[str, Any], entailment: Any
) -> tuple[Verdict, RuleFired] | None:
    """Stage 2 (variant b): bundle-relative absence route, gold heuristic 4."""
    if not features.has_explicit_negation:
        return None
    if not (
        verdict.support_verdict == "not_checkable"
        and verdict.support_verdict_reason == "no_entail_signal"
    ):
        return None
    asserting = [
        r
        for r in entailment
        if r.label == "contradict"
        and by_id[r.passage_id].source_meta.get("trust_level") == "primary"
        and not expresses_negation(by_id[r.passage_id].text)
    ]
    if asserting:
        return None
    return (
        Verdict(support_verdict="supported", audit_confidence="medium"),
        RuleFired(
            rule_id=_S2,
            reason=(
                "negated/absence claim; no eligible (primary) passage asserts the "
                "negated content across the bundle → supported (gold heuristic 4, "
                "bundle-relative)"
            ),
        ),
    )


# --------------------------------------------------------------------------- #
# §4.5 — prototype auditor (mirrors runner.run_default_audit, rules swapped)   #
# --------------------------------------------------------------------------- #
def make_prototype_auditor(stage2: bool):
    """Return an ``auditor(request) -> AuditTrace`` using the prototype rules.

    Heavy inference layers are imported here (not at module top) so importing
    this module stays cheap; the model constructors are ``functools.cache``d, so
    both variants load each model once across the whole process.
    """
    from claim_audit_lab.v1.impl.entailer import DeBERTaEntailer
    from claim_audit_lab.v1.impl.features import DefaultFeatureExtractor
    from claim_audit_lab.v1.impl.retriever import BiEncoderRetriever
    from claim_audit_lab.v1.pipeline import run_audit

    def audit(request: AuditRequest) -> AuditTrace:
        config = request.audit_config
        return run_audit(
            request,
            feature_extractor=DefaultFeatureExtractor(),
            retriever=BiEncoderRetriever(revision=config.retriever),
            entailer=DeBERTaEntailer(revision=config.entailer),
            aggregator=MaxEntailmentAggregator(),
            rules=AbsenceRoutePrototypeRules(
                stock=VerdictRules(rules_file_sha=config.rules_file_sha),
                stage2=stage2,
            ),
        )

    return audit


# --------------------------------------------------------------------------- #
# §4.3 — calibration loop (mirrors run_calibration, swaps the request builder) #
# --------------------------------------------------------------------------- #
def run_prototype_calibration(
    packet_dir: Path,
    gold: CalibrationGold,
    config: AuditConfig,
    *,
    auditor,
    deviations_dir: Path,
) -> tuple[CalibrationResult, dict[str, AuditTrace]]:
    """As ``v1.calibrate.run_calibration`` but with the D1-enriched request builder."""
    traces: dict[str, AuditTrace] = {}
    for bundle_dir in sorted(
        p for p in packet_dir.iterdir() if p.is_dir() and (p / "bundle_manifest.yaml").is_file()
    ):
        contents = load_bundle(bundle_dir, deviations_dir=deviations_dir)
        for request in enrich_requests_with_trust(contents, config):
            if request.claim_id in traces:
                raise ValueError(f"duplicate claim_id across packet: {request.claim_id}")
            traces[request.claim_id] = auditor(request)
    return compute_calibration(traces, gold, config), traces


# --------------------------------------------------------------------------- #
# §5.1 — measurement sets, derived mechanically from run-01 traces + gold      #
# --------------------------------------------------------------------------- #
def derive_measurement_sets(
    baseline: dict[str, AuditTrace], gold_by_id: dict[str, Any]
) -> dict[str, list[str]]:
    """A4-8 set, its fiction-driven subset, and the 4 gold-supported absence misses."""
    a4 = sorted(
        cid
        for cid, t in baseline.items()
        if any(r.rule_id == "A4_hard_contradiction" for r in t.rules_fired)
    )
    fiction = sorted(
        cid
        for cid in a4
        if (baseline[cid].support_signal.contributing_passage_id or "").startswith(_FICTION_PREFIX)
    )
    # CORRECTION (approved): the plan's literal recipe omits the negation filter and
    # so admits the non-absence, primary-driven canary c003; restrict to
    # has_explicit_negation to recover the intended 4.
    misses = sorted(
        cid
        for cid in a4
        if gold_by_id[cid].gold_verdict in _GOLD_SUPPORTED_SLOT
        and baseline[cid].features.has_explicit_negation
    )
    raw_misses = sorted(cid for cid in a4 if gold_by_id[cid].gold_verdict in _GOLD_SUPPORTED_SLOT)
    return {
        "a4_hard_contradiction_set": a4,
        "fiction_driven_subset": fiction,
        "gold_supported_absence_misses": misses,
        "gold_supported_absence_misses_raw_recipe_no_negation_filter": raw_misses,
    }


# --------------------------------------------------------------------------- #
# §5.3 — the three quantities argument cannot settle                          #
# --------------------------------------------------------------------------- #
def rule_fire_counts(traces: dict[str, AuditTrace]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for t in traces.values():
        for r in t.rules_fired:
            counts[r.rule_id] = counts.get(r.rule_id, 0) + 1
    return dict(sorted(counts.items()))


def recover_split(stage1: dict[str, AuditTrace], misses: list[str]) -> dict[str, Any]:
    """Quantity 1 — Stage-1 recover (supported) vs safe-land (not_checkable) vs other."""
    detail = {cid: stage1[cid].verdict.support_verdict for cid in misses}
    recovered = [cid for cid, v in detail.items() if v == "supported"]
    safe_landed = [cid for cid, v in detail.items() if v == "not_checkable"]
    other = {cid: v for cid, v in detail.items() if v not in ("supported", "not_checkable")}
    return {
        "n_misses": len(misses),
        "recovered_to_supported": recovered,
        "safe_landed_not_checkable": safe_landed,
        "other": other,
        "per_claim": detail,
    }


def stage2_net_effect(
    s1: dict[str, AuditTrace],
    s12: dict[str, AuditTrace],
    s1_res: CalibrationResult,
    s12_res: CalibrationResult,
    gold_by_id: dict[str, Any],
) -> dict[str, Any]:
    """Quantity 2 — Stage-2 recoveries vs c008-likes + metric deltas."""
    lifted = [
        cid
        for cid in s12
        if s12[cid].verdict.support_verdict == "supported"
        and s1[cid].verdict.support_verdict != "supported"
    ]
    recoveries, c008_likes = [], []
    for cid in lifted:
        neg = s12[cid].features.has_explicit_negation
        gv = gold_by_id[cid].gold_verdict
        flags = list(gold_by_id[cid].gold_flags)
        if gv in _GOLD_SUPPORTED_SLOT:
            recoveries.append(cid)
        elif neg and (
            gv in ("unsupported", "contradicted", "not_checkable") or "missing_needed" in flags
        ):
            c008_likes.append({"claim_id": cid, "gold_verdict": gv, "gold_flags": flags})
    left_pool = [
        cid
        for cid in s12
        if s12[cid].verdict.support_verdict == "not_checkable"
        and s1[cid].verdict.support_verdict != "not_checkable"
    ]
    reentered_pool = [
        cid
        for cid in s12
        if s12[cid].verdict.support_verdict != "not_checkable"
        and s1[cid].verdict.support_verdict == "not_checkable"
    ]
    return {
        "delta_weighted_kappa": s12_res.agreement.weighted_kappa - s1_res.agreement.weighted_kappa,
        "delta_gwet_ac2": s12_res.agreement.gwet_ac2 - s1_res.agreement.gwet_ac2,
        "delta_exact": s12_res.agreement.n_agree - s1_res.agreement.n_agree,
        "lifted_to_supported": sorted(lifted),
        "recoveries_gold_supported_absence": sorted(recoveries),
        "c008_likes": c008_likes,
        "left_weighted_pool_to_not_checkable": sorted(left_pool),
        "reentered_weighted_pool": sorted(reentered_pool),
    }


def canary(traces: dict[str, AuditTrace], gold_by_id: dict[str, Any]) -> list[dict[str, str]]:
    """Quantity 3 — CAL adverse where gold is non-adverse (by P1's construction, primary-driven)."""
    out = []
    for cid, t in traces.items():
        v = t.verdict.support_verdict
        gv = crosswalk_gold(
            gold_by_id[cid].gold_verdict, gold_by_id[cid].gold_flags
        ).support_verdict
        if v in _ADVERSE and gv not in _ADVERSE:
            src = (t.support_signal.contributing_passage_id or "").split("/", 1)[0]
            out.append(
                {
                    "claim_id": cid,
                    "cal_verdict": v,
                    "gold_verdict": gold_by_id[cid].gold_verdict,
                    "contributing_source": src,
                    "rules_fired": ";".join(r.rule_id for r in t.rules_fired),
                }
            )
    return sorted(out, key=lambda r: r["claim_id"])


def verdict_flips_outside(
    baseline: dict[str, AuditTrace], variant: dict[str, AuditTrace], a4_set: list[str]
) -> list[dict[str, str]]:
    """§5.4 sanity — verdict-degree changes vs run-01 outside the A4-8 set."""
    a4 = set(a4_set)
    flips = []
    for cid in variant:
        b = baseline[cid].verdict.support_verdict
        c = variant[cid].verdict.support_verdict
        if b != c and cid not in a4:
            flips.append({"claim_id": cid, "run01": b, "variant": c})
    return sorted(flips, key=lambda r: r["claim_id"])


# --------------------------------------------------------------------------- #
# §4.6 step 2 — smoke (corrected: c016 → c002)                                 #
# --------------------------------------------------------------------------- #
# (variant, claim_id) -> (verdict, reason, {must-fire}, {must-not-fire})
_SMOKE_BUNDLES = ["rsh-06d68ece6bbd", "rsh-475fe956a5fb"]
_SMOKE_EXPECT: dict[tuple[str, str], tuple[str, str | None, set[str], set[str]]] = {
    # c008 — the only non-neutral entailment is the fiction contradict 0.9946.
    ("stage-1", "rsh-06d68ece6bbd-c008"): ("not_checkable", "no_entail_signal", {_P1}, {_S2}),
    ("stage-1+2", "rsh-06d68ece6bbd-c008"): ("supported", None, {_P1, _S2}, set()),
    # c003 — canary: primary-driven A4, trust-only leaves it alone (by design).
    ("stage-1", "rsh-475fe956a5fb-c003"): (
        "contradicted",
        None,
        {"A4_hard_contradiction"},
        {_P1, _P2, _S2},
    ),
    ("stage-1+2", "rsh-475fe956a5fb-c003"): (
        "contradicted",
        None,
        {"A4_hard_contradiction"},
        {_P1, _P2, _S2},
    ),
    # c002 (replaces c016) — P1 suppresses the fiction contradict 0.9897; the
    # surviving primary entail 0.6250 then trips A3 (its passage does not express
    # negation) → contradicted, primary-driven. S2 cannot fire (not not_checkable).
    ("stage-1", "rsh-475fe956a5fb-c002"): (
        "contradicted",
        None,
        {_P1, "A3_negation_backstop"},
        {_S2, _P2},
    ),
    ("stage-1+2", "rsh-475fe956a5fb-c002"): (
        "contradicted",
        None,
        {_P1, "A3_negation_backstop"},
        {_S2, _P2},
    ),
}


def run_smoke(packet: Path, gold: CalibrationGold, config: AuditConfig, out: Path) -> int:
    """Audit the pinned smoke claims (both variants) and assert the §4.6 predictions."""
    targets = {cid for _, cid in _SMOKE_EXPECT}
    deviations = out / "smoke-deviations"
    results: dict[tuple[str, str], AuditTrace] = {}
    for variant, stage2 in (("stage-1", False), ("stage-1+2", True)):
        auditor = make_prototype_auditor(stage2)
        for name in _SMOKE_BUNDLES:
            contents = load_bundle(packet / name, deviations_dir=deviations)
            for request in enrich_requests_with_trust(contents, config):
                if request.claim_id in targets:
                    results[(variant, request.claim_id)] = auditor(request)

    failures = 0
    for key in sorted(_SMOKE_EXPECT):
        variant, cid = key
        want_verdict, want_reason, must, must_not = _SMOKE_EXPECT[key]
        trace = results.get(key)
        checks: list[str] = []
        ok = True
        if trace is None:
            ok = False
            checks.append("NOT AUDITED")
        else:
            fired = {r.rule_id for r in trace.rules_fired}
            got_verdict = trace.verdict.support_verdict
            got_reason = trace.verdict.support_verdict_reason
            if got_verdict != want_verdict:
                ok = False
                checks.append(f"verdict={got_verdict}!={want_verdict}")
            if want_reason is not None and got_reason != want_reason:
                ok = False
                checks.append(f"reason={got_reason}!={want_reason}")
            missing = must - fired
            present_forbidden = must_not & fired
            if missing:
                ok = False
                checks.append(f"missing={sorted(missing)}")
            if present_forbidden:
                ok = False
                checks.append(f"forbidden={sorted(present_forbidden)}")
            checks.append(f"[{got_verdict}/{got_reason} fired={sorted(fired)}]")
        failures += 0 if ok else 1
        print(f"  {'PASS' if ok else 'FAIL'}  {variant:9} {cid}  {' '.join(checks)}", flush=True)

    if failures:
        print(
            f"\nSMOKE FAILED ({failures} assertion(s)). Do not run the full pass.", file=sys.stderr
        )
        print(
            "Per §4.6: if this fails a correct transcription, STOP and report — the "
            "plan's model of the code is wrong somewhere.",
            file=sys.stderr,
        )
    else:
        print("\nSMOKE PASSED — all assertions hold. Safe to run the full pass.", flush=True)
    return 1 if failures else 0


# --------------------------------------------------------------------------- #
# §4.6 step 3 + §5 — full run                                                  #
# --------------------------------------------------------------------------- #
def _git_state(repo: Path) -> dict[str, Any]:
    def run(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
        ).stdout.strip()

    dirty = bool(run("status", "--porcelain"))
    return {"workbench_head": run("rev-parse", "HEAD"), "workbench_dirty": dirty}


def run_full(args: argparse.Namespace, config: AuditConfig, gold: CalibrationGold) -> int:
    baseline = load_traces(args.baseline_run / "traces")
    baseline_hash = _assert_baseline_config(baseline, config)
    baseline_result = compute_calibration(baseline, gold, config)
    gold_by_id = {c.claim_id: c for c in gold.claims}

    args.out.mkdir(parents=True, exist_ok=True)
    copied_gold = args.out / "gold.dev.yaml"
    shutil.copyfile(args.gold, copied_gold)

    sets = derive_measurement_sets(baseline, gold_by_id)

    variants = {}
    for variant, stage2 in (("stage-1", False), ("stage-1+2", True)):
        print(f"starting variant {variant} (stage2={stage2})", file=sys.stderr, flush=True)
        variant_dir = args.out / variant
        auditor = make_prototype_auditor(stage2)
        result, traces = run_prototype_calibration(
            args.packet, gold, config, auditor=auditor, deviations_dir=variant_dir / "deviations"
        )
        write_run_artifacts(variant_dir, result, traces, config, pinned_at=args.pinned_at)
        rows, summary = build_diff_rows(gold, baseline, traces)
        summary = {
            "variant": variant,
            "stage2": stage2,
            "audit_config_hash": result.audit_config_hash,
            **summary,
        }
        write_diff(variant_dir, rows, summary)
        variants[variant] = {"result": result, "traces": traces, "summary": summary}
        print(
            f"finished {variant}: exact={result.agreement.n_agree}/{result.agreement.n_total}; "
            f"wκ={result.agreement.weighted_kappa:.4f}; AC2={result.agreement.gwet_ac2:.4f}; "
            f"F4_new_gold_supported_to_contradicted={summary['new_gold_supported_to_cal_contradicted']}",
            file=sys.stderr,
            flush=True,
        )

    s1, s12 = variants["stage-1"], variants["stage-1+2"]

    # §5.2 — F4 hard safety gate
    f4 = {v: variants[v]["summary"]["new_gold_supported_to_cal_contradicted"] for v in variants}
    f4_pass = all(n == 0 for n in f4.values())

    # §5.3 — the three quantities
    quantity1 = recover_split(s1["traces"], sets["gold_supported_absence_misses"])
    quantity2 = stage2_net_effect(
        s1["traces"], s12["traces"], s1["result"], s12["result"], gold_by_id
    )
    quantity3 = {v: canary(variants[v]["traces"], gold_by_id) for v in variants}

    # §5.4 — sanity
    sanity = {
        v: {
            "rule_fire_counts": rule_fire_counts(variants[v]["traces"]),
            "verdict_flips_outside_a4_set": verdict_flips_outside(
                baseline, variants[v]["traces"], sets["a4_hard_contradiction_set"]
            ),
        }
        for v in variants
    }

    metadata: dict[str, Any] = {
        "label": _DEV_LABEL,
        "run": "run-03-absence-route",
        "governing_plan": "plans/absence-route-execution-plan.md",
        "authority": "plans/adr-v1-absence-route.md (ACCEPTED 2026-07-07)",
        "script": str(Path(__file__).resolve()),
        "script_sha256": _sha256(Path(__file__)),
        "packet": str(args.packet.resolve()),
        "gold_source": str(args.gold.resolve()),
        "gold_copy": str(copied_gold.resolve()),
        "gold_sha256": _sha256(copied_gold),
        "baseline_run": str(args.baseline_run.resolve()),
        "baseline_audit_config_hash": baseline_hash,
        "note_audit_config_hash": (
            "UNCHANGED from run-01 by design — config is untouched, the logic changed. "
            "Run-03 traces are distinguished from run-01 only by rules_fired + directory."
        ),
        "pinned_at": args.pinned_at,
        # workbench repo root = scripts/.. — record its HEAD + dirty flag (§4.6 step 4)
        **_git_state(Path(__file__).resolve().parents[1]),
        "variants": {
            v: {
                "stage2": variants[v]["summary"]["stage2"],
                "output": str((args.out / v).resolve()),
                "exact_agree": variants[v]["result"].agreement.n_agree,
                "exact_total": variants[v]["result"].agreement.n_total,
                "cohens_kappa": variants[v]["result"].agreement.cohens_kappa,
                "weighted_kappa": variants[v]["result"].agreement.weighted_kappa,
                "gwet_ac2": variants[v]["result"].agreement.gwet_ac2,
                "on_scale_n": variants[v]["result"].agreement.on_scale_n,
            }
            for v in variants
        },
        "baseline_run01": {
            "exact_agree": baseline_result.agreement.n_agree,
            "exact_total": baseline_result.agreement.n_total,
            "cohens_kappa": baseline_result.agreement.cohens_kappa,
            "weighted_kappa": baseline_result.agreement.weighted_kappa,
            "gwet_ac2": baseline_result.agreement.gwet_ac2,
            "on_scale_n": baseline_result.agreement.on_scale_n,
        },
        "measurement_sets": sets,
        "f4_new_gold_supported_to_cal_contradicted": f4,
        "f4_pass": f4_pass,
        "quantity1_stage1_recover_vs_safe_land": quantity1,
        "quantity2_stage2_net_effect": quantity2,
        "quantity3_eligibility_canary": {
            v: {"count": len(quantity3[v]), "claims": quantity3[v]} for v in variants
        },
        "sanity": sanity,
        "deviations_from_plan": {
            "smoke_c016_to_c002": (
                "Plan §4.6 smoke asserted rsh-bffa73dfe56a-c016 → supported+P1; that "
                "was a floor-0.30 (run-02) observation. At floor 0.40 c016 is already "
                "supported with no admitted fiction contradict, so P1 cannot fire. "
                "Smoke uses rsh-475fe956a5fb-c002 (the clean loop+eligible-signal "
                "case) plus the unchanged c008 and c003."
            ),
            "sec5_1_negation_filter": (
                "Plan §5.1 recipe 'A4-8 ∩ gold-supported-slot' yields 5 (admits the "
                "non-absence, primary-driven canary c003, neg=False). Added "
                "has_explicit_negation to recover the intended 4; c003 stays tracked "
                "solely as the canary (quantity 3)."
            ),
            "approved": "Cameron, 2026-07-07, after pre-flight verification",
        },
    }
    _write_json(args.out / "run-metadata.json", metadata)
    _write_json(args.out / "baseline-result.json", baseline_result.model_dump(mode="json"))
    (args.out / "README.md").write_text(
        _render_readme(metadata, baseline_result, variants), encoding="utf-8"
    )

    print(
        f"\nrun-03 complete. F4 {'PASS (0/0)' if f4_pass else 'FAIL — STOP, do not tune (§5.2)'}. "
        f"canary(stage-1)={len(quantity3['stage-1'])} (trigger >2 ⇒ draft subject-scope ADR).",
        flush=True,
    )
    return 0 if f4_pass else 2


def _fmt_pct(n: int, d: int) -> str:
    return f"{n}/{d} ({100 * n / d:.1f}%)" if d else f"{n}/0"


def _ids(ids: list[str]) -> str:
    """Render a claim-id list as inline code, or an em dash when empty."""
    return "`" + "`, `".join(ids) + "`" if ids else "—"


def _render_readme(
    metadata: dict[str, Any],
    baseline: CalibrationResult,
    variants: dict[str, dict[str, Any]],
) -> str:
    s1r = variants["stage-1"]["result"].agreement
    s12r = variants["stage-1+2"]["result"].agreement
    b = baseline.agreement
    q1 = metadata["quantity1_stage1_recover_vs_safe_land"]
    q2 = metadata["quantity2_stage2_net_effect"]
    q3 = metadata["quantity3_eligibility_canary"]
    sets = metadata["measurement_sets"]
    f4 = metadata["f4_new_gold_supported_to_cal_contradicted"]
    dev = metadata["deviations_from_plan"]
    misses = sets["gold_supported_absence_misses"]
    rec, safe = q1["recovered_to_supported"], q1["safe_landed_not_checkable"]
    q2rec = q2["recoveries_gold_supported_absence"]
    left, reent = q2["left_weighted_pool_to_not_checkable"], q2["reentered_weighted_pool"]
    c1, c12 = q3["stage-1"]["count"], q3["stage-1+2"]["count"]
    f4_status = "PASS" if metadata["f4_pass"] else "FAIL (STOP per §5.2)"

    def metric_row(label: str, fn) -> str:
        return f"| {label} | {fn(b)} | {fn(s1r)} | {fn(s12r)} |"

    lines = [
        "# PILOT-001 dev calibration — run 03 absence route (2026-07-07)",
        "",
        "**DEV RESULT — adaptation set, not validated and not a gate.** PILOT-001 is the",
        "development set per Decision G. This is a prototype rerun that measures the",
        "Decision-H absence route (Stage 1, and Stage 2 as an explicit option) in-process",
        "over the sealed packet. It amends **no** packaged rule, config, or golden; the real",
        "landing (`cal-rules-v1.5.0`) is governed by §7 of the execution plan and needs a",
        "second, explicit go.",
        "",
        "## Provenance and isolation",
        "",
        f"- **Packet (read-only, sealed):** `{metadata['packet']}` (15 bundles, 98 claims).",
        "- **Gold:** run-01's `gold.dev.yaml`, copied byte-for-byte.",
        f"  SHA-256 `{metadata['gold_sha256']}`.",
        f"- **Baseline:** run-01 traces at `{metadata['baseline_run']}`, config hash",
        f"  `{metadata['baseline_audit_config_hash']}`.",
        "- **Config/models/rules:** UNCHANGED `cal-rules-v1.4.0` (SHA-256",
        "  `2fb6711ebfe28d3defb4213e02f000315ec6117bc1a5754c6aa24d9863b93dcd`), floor",
        "  0.40, same MiniLM retriever + DeBERTa entailer, CPU deterministic. The",
        "  `audit_config_hash` is therefore **identical to run-01** —",
        f"  {metadata['note_audit_config_hash']}",
        f"- **Prototype:** `{metadata['script']}`,",
        f"  SHA-256 `{metadata['script_sha256']}`; workbench HEAD",
        f"  `{metadata['workbench_head']}` (dirty={metadata['workbench_dirty']});",
        f"  report time pinned `{metadata['pinned_at']}`.",
        "",
        "The prototype is a suppression loop around the stock aggregator + rules: it joins the",
        "dropped `trust_level` at intake (D1), refuses to let a non-`primary` source solo-decide",
        "an adverse degree (P1/D2), mirrors the A3 negation backstop on the contradict direction",
        "(P2/D3), and — in `stage-1+2` — routes bundle-relative absence to `supported` (S2). The",
        "trace keeps the raw aggregator `support_signal`; the whole story lives in `rules_fired`.",
        "",
        "## Headline metrics",
        "",
        "| metric | run-01 (v1.4.0) | stage-1 | stage-1+2 |",
        "|---|---:|---:|---:|",
        metric_row("exact agreement", lambda a: _fmt_pct(a.n_agree, a.n_total)),
        metric_row("Cohen's κ", lambda a: f"{a.cohens_kappa:.4f}"),
        metric_row("weighted κ (quadratic)", lambda a: f"{a.weighted_kappa:.4f}"),
        metric_row("Gwet AC2 (quadratic)", lambda a: f"{a.gwet_ac2:.4f}"),
        metric_row("on-scale n", lambda a: str(a.on_scale_n)),
        "",
        "**F4 hard safety gate** (new gold-supported → CAL `contradicted`, must be 0):",
        f"stage-1 = {f4['stage-1']}, stage-1+2 = {f4['stage-1+2']} — {f4_status}.",
        "",
        "## The three quantities (§5.3)",
        "",
        "### 1. Stage-1 recover vs safe-land — over the 4 gold-supported absence misses",
        f"Misses (A4-8 ∩ gold-supported-slot ∩ negation): {_ids(misses)}.",
        "",
        f"- **recovered → `supported`:** {len(rec)} {_ids(rec)}",
        f"- **safe-landed → `not_checkable`:** {len(safe)} {_ids(safe)}",
        f"- **other:** {q1['other'] or '—'}",
        "",
        "### 2. Stage-2 net effect (stage-1+2 vs stage-1)",
        f"- Δ weighted κ = {q2['delta_weighted_kappa']:+.4f}; "
        f"Δ AC2 = {q2['delta_gwet_ac2']:+.4f}; Δ exact = {q2['delta_exact']:+d}.",
        f"- recoveries (gold-supported absence → `supported`): {len(q2rec)} {_ids(q2rec)}.",
        f"- **c008-likes** (gold `unsupported`/`missing_needed` absence → `supported`): "
        f"{len(q2['c008_likes'])} — {q2['c008_likes'] or '—'}.",
        f"- left weighted pool → `not_checkable`: {_ids(left)}; re-entered: {_ids(reent)}.",
        "",
        "c008-likes are cases where the absence route is arguably *righter* than the gold's",
        "`missing_needed` adjudication (a κ-ceiling tension, not a bug). S2 deliberately does not",
        "upgrade `partially_supported`.",
        "",
        "### 3. Eligibility-scope canary (primary-source false-adverse survivors)",
        f"- stage-1: **{c1}** — trigger is >2 ⇒ *draft* a flag-based, non-lexical",
        "  subject-scope ADR (do not build).",
        f"- stage-1+2: **{c12}**.",
        "",
        _canary_table(q3["stage-1"]["claims"]),
        "",
        "## Deviations from the plan-as-written (approved 2026-07-07)",
        "",
        f"1. **Smoke c016 → c002.** {dev['smoke_c016_to_c002']}",
        f"2. **§5.1 negation filter.** {dev['sec5_1_negation_filter']}",
        "",
        "## Artifacts",
        "",
        "Each `stage-1/` and `stage-1+2/` directory holds `calibration-report.md`, 98",
        "`traces/*.json`, `audit-config.yaml`, `calibration-result.json`, `per-claim-diff.csv`,",
        "and `diff-summary.json`. Root: `run-metadata.json` (provenance, measurement sets, all",
        "three quantities, F4, sanity), `baseline-result.json`, and this README.",
    ]
    return "\n".join(lines) + "\n"


def _canary_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "_No primary-source false-adverse survivors._"
    out = ["| claim | CAL | gold (raw) | source | rules |", "|---|---|---|---|---|"]
    out += [
        f"| `{r['claim_id']}` | {r['cal_verdict']} | {r['gold_verdict']} "
        f"| {r['contributing_source']} | {r['rules_fired']} |"
        for r in rows
    ]
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--pinned-at", required=True)
    parser.add_argument("--smoke", action="store_true", help="run the pinned smoke assertions only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_default_audit_config()
    if config.retrieval_floor != 0.40:
        raise ValueError(f"expected shipped retrieval_floor 0.40, got {config.retrieval_floor}")
    gold_sha = _sha256(args.gold)
    if gold_sha != _EXPECTED_GOLD_SHA:
        raise ValueError(f"gold SHA mismatch: {gold_sha} != {_EXPECTED_GOLD_SHA} (aborting)")
    gold = load_gold(args.gold)

    if args.smoke:
        args.out.mkdir(parents=True, exist_ok=True)
        print("=== run-03 SMOKE (both variants) ===", flush=True)
        return run_smoke(args.packet, gold, config, args.out)
    return run_full(args, config, gold)


if __name__ == "__main__":
    sys.exit(main())
