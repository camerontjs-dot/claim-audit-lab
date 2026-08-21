"""Abstention picture + a live whole-claim vs atomic decomposition demonstration.

PART 1 derives what the sealed artifacts can actually support, and attributes what
they cannot. Figures that are not recomputed here are printed with their source file
rather than as if this script had verified them — an earlier version printed four
PILOT-001 numbers as hardcoded literals under a docstring claiming it "re-derives and
verifies" them. They were correct, but the script did not establish them.

PART 2 is a live three-case demonstration of the mechanism: a compound claim whose
evidence is split across passages abstains under whole-claim auditing and resolves
under per-atom auditing. Three hand-built cases. A demonstration of a mechanism, not
a measurement of a benefit — for that see scripts/decomposition_recovery_test.py,
which runs CAL's real abstentions and counts the cost side too.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

workbench_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(workbench_dir / "src"))

from claim_audit_lab.ui.reasons import derive_reason
from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.explicit_claims import (
    AtomProvenance,
    ExplicitClaimAtom,
    ExplicitClaimRequest,
)
from claim_audit_lab.v1.models import AuditRequest, Passage
from claim_audit_lab.v1.runner import run_default_audit, run_default_explicit_claim_audit

CAL_ROOT = workbench_dir.parent
SCALED_AUDITED = CAL_ROOT / "outputs/2026-08-02-qms-claim-generation/scaled-30/cal-audit/audited.json"
PILOT_CALIBRATION = CAL_ROOT / "outputs/pilot-001-dev-calibration/run-06-a1-landing-2026-07-16/calibration-result.json"
GOLD_AUDIT = "outputs/2026-08-04-pilot001-gold-audit/FINDINGS.md"

SUPPORTIVE_INTENTS = ("states", "entails")


def part1_abstention_picture() -> None:
    print("=" * 78)
    print("PART 1 — ABSTENTION PICTURE (derived where derivable, attributed where not)")
    print("=" * 78)

    if not SCALED_AUDITED.exists():
        raise SystemExit(f"Refusing to report: sealed Scaled-30 audit missing at {SCALED_AUDITED}")

    records = json.loads(SCALED_AUDITED.read_text())
    total = len(records)
    by_intent: dict[str, Counter] = defaultdict(Counter)
    abstentions = 0
    for r in records:
        verdict = r.get("cal_verdict")
        by_intent[r.get("relationship", "unknown")][verdict] += 1
        if verdict in ("not_checkable", None):
            abstentions += 1

    print(f"\n[Scaled-30 — {total} claims, generator-intent labels, DERIVED from sealed traces]")
    print(f"  abstention rate (`not_checkable`): {abstentions}/{total} ({abstentions / total * 100:.1f}%)")

    # Supportive-intent misses split by kind. Pooling these under "false abstention"
    # hides the worse failure: a false adverse is not an abstention.
    supportive = sum(by_intent[i].total() for i in SUPPORTIVE_INTENTS)
    missed_abstain = sum(by_intent[i]["not_checkable"] for i in SUPPORTIVE_INTENTS)
    missed_adverse = sum(
        by_intent[i][v] for i in SUPPORTIVE_INTENTS for v in ("contradicted", "unsupported")
    )
    print(f"\n  supportive-intent claims: {supportive}")
    print(f"    missed into abstention   : {missed_abstain}/{supportive} ({missed_abstain / supportive * 100:.1f}%)")
    print(f"    missed into FALSE ADVERSE: {missed_adverse}/{supportive} ({missed_adverse / supportive * 100:.1f}%)  <- worse failure, counted separately")

    print("\n  by generator intent:")
    for intent in sorted(by_intent):
        c = by_intent[intent]
        n = c.total()
        nc = c["not_checkable"]
        print(
            f"    {intent:16s} (n={n:2d}): abstain={nc:2d} ({nc / n * 100:5.1f}%) | "
            f"sup={c['supported']:2d} part={c['partially_supported']:2d} "
            f"contra={c['contradicted']:2d} unsup={c['unsupported']:2d}"
        )
    print("\n  NOTE: abstention is the CORRECT outcome for silent_adjacent and absent_element.")
    print("        The headline rate mixes correct abstentions with failures; read the split.")

    if not PILOT_CALIBRATION.exists():
        raise SystemExit(f"Refusing to report: PILOT-001 calibration missing at {PILOT_CALIBRATION}")

    cal = json.loads(PILOT_CALIBRATION.read_text())
    confusion = cal["confusion"]  # rows = human gold, cols = CAL
    gold_supported = sum(confusion["supported"].values())
    missed_nc = confusion["supported"]["not_checkable"]
    missed_contra = confusion["supported"]["contradicted"]

    print(f"\n[PILOT-001 — {cal['n_claims']} claims, human gold, DERIVED from run-06 confusion matrix]")
    print(f"  exact agreement : {cal['agreement']['n_agree']}/{cal['agreement']['n_total']} "
          f"({cal['agreement']['exact_agreement'] * 100:.1f}%)")
    print(f"  Cohen's kappa   : {cal['agreement']['cohens_kappa']:.4f}")
    print(f"  gold `supported`: {gold_supported}/{cal['n_claims']}")
    print(f"    -> CAL abstained on      : {missed_nc}/{gold_supported} ({missed_nc / gold_supported * 100:.1f}%)")
    print(f"    -> CAL called contradicted: {missed_contra}/{gold_supported}  <- false adverse on human gold")

    print(f"\n  NOT RECOMPUTED HERE — see {GOLD_AUDIT}:")
    print("    63/98 claims had zero CAL support confidence; the human found support on 56 (89%).")
    print("    That figure uses a confidence field this script does not reconstruct. Cited, not verified.")
    print("\n  Per adr-v1-human-gold-role: PILOT-001 is falsification evidence, not a gate.")


def part2_mechanism_demo() -> None:
    print("\n" + "=" * 78)
    print("PART 2 — LIVE DEMONSTRATION: WHOLE-CLAIM VS DECLARED ATOMS (3 hand-built cases)")
    print("=" * 78)

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    config = load_default_audit_config()

    provenance = AtomProvenance(
        origin="operator_declared",
        reference_id="demo:test_abstention_and_decomposition",
        reference_sha256="sha256:" + "0" * 64,
    )

    scenarios = [
        (
            "DISTRIBUTED-SUPPORT",
            "Autoclave A-102 completed the sterilization cycle at 121 C and was released by QC under SOP-402.",
            [
                "Autoclave A-102 completed the sterilization cycle at 121 C.",
                "Autoclave A-102 was released by QC under SOP-402.",
            ],
            [
                ("p1", "At 09:30, Autoclave A-102 reached 121 C and held for 30 minutes, completing the sterilization cycle."),
                ("p2", "QC signed off on the batch release for Autoclave A-102 in accordance with SOP-402."),
            ],
            "supported",
        ),
        (
            "PARTIAL-SUPPORT",
            "The bioreactor pressure reached 1.5 bar and the cooling jacket was manually activated.",
            [
                "The bioreactor pressure reached 1.5 bar.",
                "The cooling jacket was manually activated.",
            ],
            [
                ("p1", "The bioreactor sensor telemetry confirmed that pressure peaked at 1.5 bar during the run."),
                ("p2", "The agitation impeller maintained 150 RPM throughout the duration."),
            ],
            "partially_supported",
        ),
        (
            "CONTRADICTED-CONJUNCT",
            "Calibration was completed on schedule and filter integrity passed bubble point test.",
            [
                "Calibration was completed on schedule.",
                "Filter integrity passed bubble point test.",
            ],
            [
                ("p1", "Annual equipment calibration was completed on schedule on August 10."),
                ("p2", "The 0.2 micron sterile filter failed the post-use bubble point integrity test with pressure drop below specification."),
            ],
            "contradicted",
        ),
    ]

    for case_id, parent, atom_texts, passage_pairs, expected in scenarios:
        passages = [Passage(passage_id=pid, text=text) for pid, text in passage_pairs]

        whole = run_default_audit(
            AuditRequest(
                claim_id=f"{case_id}-whole",
                claim_text=parent,
                passages=passages,
                audit_config=config,
            )
        )
        atomic = run_default_explicit_claim_audit(
            ExplicitClaimRequest(
                parent_claim_id=case_id,
                parent_claim_text=parent,
                operator="all_of",
                atoms=[
                    ExplicitClaimAtom(atom_id=f"{case_id}-a{i}", claim_text=t, provenance=provenance)
                    for i, t in enumerate(atom_texts)
                ],
                passages=passages,
                audit_config=config,
            )
        )

        wv = whole.verdict.support_verdict
        av = atomic.verdict.support_verdict
        print(f"\n[{case_id}] expected {expected.upper()}")
        print(f"  whole  -> {wv:20s} {derive_reason(whole, config)['reason_code']}")
        for atom in atomic.atom_audits:
            print(f"    atom: {atom.audit_trace.verdict.support_verdict:20s} {atom.claim_text}")
        print(f"  atomic -> {av:20s} {atomic.parent_aggregation.rule_id}")

    print("\nThree authored cases. Mechanism only — not a measured benefit.")


if __name__ == "__main__":
    part1_abstention_picture()
    part2_mechanism_demo()
