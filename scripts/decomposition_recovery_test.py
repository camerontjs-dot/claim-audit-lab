"""The decomposition test that has not been run: does per-atom auditing recover
CAL's real authored-supported abstentions, and what does it break doing it?

Two modes, deliberately separated by a human step.

  --emit-worksheet   Reads the sealed Scaled-30 traces, selects every claim whose
                     generator intent is supportive (`states` / `entails`) but whose
                     CAL verdict is an abstention, and writes an atom-declaration
                     worksheet. It does NOT split any claim text. Declaring atoms is
                     Stage -1 and belongs to a human — see adr-v1-explicit-claim-structure:
                     "This additive API does not decompose claim text."

  --run              Takes the completed worksheet and audits each declared atom set
                     through the real explicit-claim engine, reporting recoveries AND
                     new false adverse findings. Both directions, always. A recovery
                     count on its own is not a result.

Why both directions: on the 2026-08-18 messy fixture, decomposition turned a safe
abstention into a false `contradicted` (MESSY-04). Counting only recoveries would
have scored that as a win.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

workbench_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(workbench_dir / "src"))

CAL_ROOT = workbench_dir.parent
SCALED = CAL_ROOT / "outputs" / "2026-08-02-qms-claim-generation" / "scaled-30" / "cal-audit"

SUPPORTIVE_INTENTS = ("states", "entails")
ABSTENTION_VERDICTS = ("not_checkable", None)


def emit_worksheet(out_path: Path) -> None:
    audited = json.loads((SCALED / "audited.json").read_text())

    targets = [
        r
        for r in audited
        if r.get("relationship") in SUPPORTIVE_INTENTS
        and r.get("cal_verdict") in ABSTENTION_VERDICTS
    ]
    # Claims whose intent is supportive but which CAL resolved adversely are a
    # different defect class (false adverse, not abstention). Surface them, do not
    # fold them into the abstention count.
    adverse = [
        r
        for r in audited
        if r.get("relationship") in SUPPORTIVE_INTENTS
        and r.get("cal_verdict") in ("contradicted", "unsupported")
    ]

    worksheet = {
        "worksheet_version": "decomposition-recovery-v1",
        "source": "outputs/2026-08-02-qms-claim-generation/scaled-30/cal-audit/audited.json",
        "instructions": (
            "For each claim, declare the atoms a human would say it asserts, in order. "
            "Leave `atoms` empty to exclude a claim from the run. Set `operator` to "
            "'single' for a genuinely atomic claim or 'all_of' for a conjunction. "
            "Set `declared_by` and `declared_at` before running. Atoms are your "
            "declaration, not CAL's — the run records them as operator_declared."
        ),
        "selection": {
            "supportive_intents": list(SUPPORTIVE_INTENTS),
            "abstention_verdicts": ["not_checkable"],
            "n_abstentions": len(targets),
            "n_false_adverse_excluded": len(adverse),
            "false_adverse_claim_ids": [r["claim_id"] for r in adverse],
        },
        "declared_by": None,
        "declared_at": None,
        "claims": [
            {
                "claim_id": r["claim_id"],
                "claim_text": r["claim_text"],
                "generator_intent": r["relationship"],
                "cal_verdict_baseline": r.get("cal_verdict"),
                "operator": None,
                "atoms": [],
            }
            for r in targets
        ],
    }

    out_path.write_text(json.dumps(worksheet, indent=2) + "\n")
    print(f"Wrote worksheet: {out_path}")
    print(f"  claims needing atom declaration : {len(targets)}")
    print(f"  supportive-intent false adverse  : {len(adverse)} (excluded, listed in worksheet)")
    print("\nNext: declare atoms by hand, set declared_by/declared_at, then re-run with --run.")


def run(worksheet_path: Path) -> None:
    import os

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    from claim_audit_lab.ui.reasons import derive_reason
    from claim_audit_lab.v1.config import load_default_audit_config
    from claim_audit_lab.v1.explicit_claims import (
        AtomProvenance,
        ExplicitClaimAtom,
        ExplicitClaimRequest,
    )
    from claim_audit_lab.v1.models import Passage
    from claim_audit_lab.v1.runner import run_default_explicit_claim_audit

    ws = json.loads(worksheet_path.read_text())
    if not ws.get("declared_by") or not ws.get("declared_at"):
        raise SystemExit(
            "Refusing to run: worksheet has no declared_by/declared_at. Atom declaration "
            "is a human act and the run records it as provenance — it cannot be anonymous."
        )

    declared = [c for c in ws["claims"] if c.get("atoms")]
    if not declared:
        raise SystemExit("Refusing to run: no claim has declared atoms.")

    config = load_default_audit_config()
    provenance = AtomProvenance(
        origin="operator_declared",
        reference_id=f"worksheet:{worksheet_path.name}:{ws['declared_by']}",
        reference_sha256="sha256:" + __import__("hashlib").sha256(
            worksheet_path.read_bytes()
        ).hexdigest(),
    )

    recovered, unchanged, new_adverse = [], [], []
    outcomes = Counter()

    for c in declared:
        trace_path = SCALED / "traces" / (c["claim_id"].replace("::", "__") + ".json")
        raw = json.loads(trace_path.read_text())
        passages = [
            Passage(passage_id=p["passage_id"], text=p["text"])
            for p in raw.get("passages", raw.get("retrieval", []))
            if p.get("text")
        ]
        if not passages:
            print(f"  [skip] {c['claim_id']}: sealed trace carries no passage text")
            continue

        result = run_default_explicit_claim_audit(
            ExplicitClaimRequest(
                parent_claim_id=c["claim_id"],
                parent_claim_text=c["claim_text"],
                operator=c["operator"] or ("all_of" if len(c["atoms"]) > 1 else "single"),
                atoms=[
                    ExplicitClaimAtom(
                        atom_id=f"{c['claim_id']}-a{i}",
                        claim_text=a,
                        provenance=provenance,
                    )
                    for i, a in enumerate(c["atoms"])
                ],
                passages=passages,
                audit_config=config,
            )
        )
        v = result.verdict.support_verdict
        outcomes[v] += 1
        reason = derive_reason(result, config)

        if v in ("supported", "partially_supported"):
            recovered.append((c["claim_id"], v))
        elif v in ("contradicted", "unsupported"):
            new_adverse.append((c["claim_id"], v, reason["detail"]))
        else:
            unchanged.append(c["claim_id"])

    n = len(declared)
    print("\n" + "=" * 78)
    print("DECOMPOSITION RECOVERY TEST — real engine, human-declared atoms")
    print("=" * 78)
    print(f"declared by      : {ws['declared_by']} at {ws['declared_at']}")
    print(f"claims run       : {n}")
    print(f"  recovered      : {len(recovered)}  (abstention -> supported/partially_supported)")
    print(f"  still abstains : {len(unchanged)}")
    print(f"  NEW FALSE ADVERSE : {len(new_adverse)}  <- the cost side; never omit this")
    print(f"verdict distribution: {dict(outcomes)}")
    if new_adverse:
        print("\nNew adverse findings on claims whose generator intent was supportive:")
        for cid, v, detail in new_adverse:
            print(f"  {cid}: {v} — {detail}")
    print("\nDEV probe over generator-intent labels. Not validation, not gate evidence.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit-worksheet", metavar="OUT", type=Path)
    g.add_argument("--run", metavar="WORKSHEET", type=Path)
    args = ap.parse_args()

    if args.emit_worksheet:
        emit_worksheet(args.emit_worksheet)
    else:
        run(args.run)


if __name__ == "__main__":
    main()
