"""RC7E pre-held-out runtime qualification v2.

No scientific gold and no held-out corpus are imported here.
"""
from __future__ import annotations

import json
import resource
from pathlib import Path

from research.language_instrument_ablation_rc7e.contract import source_sha
from research.language_instrument_ablation_rc7e.evaluator import evaluator_controls
from research.language_instrument_ablation_rc7e.instruments import (
    CoreNLPFamily,
    OWLRLReasoner,
    QuantulumInstrument,
    RC7DBaseline,
    StanzaFamily,
)
from research.language_instrument_ablation_rc7e.qualified_instruments import (
    ProvenancedDebertaNLI,
    QualifiedSuParSDP,
    instrument_identities_v2,
)

OUT = Path("research/language_instrument_ablation_rc7e/results")
SMOKE = (
    "Only reviewers may approve the packet before 2026-09-01. "
    "Dana reviewed the dossier. She said, \"The packet is ready.\" "
    "Exactly 3 auditors signed the release."
)


def _tagged_typed(receipts):
    rows = []
    for receipt in receipts:
        for row in receipt.get("candidate_atoms", []):
            if row.get("scorable") and isinstance(row.get("atom"), dict):
                tagged = dict(row)
                tagged["proposal_instrument_id"] = receipt["instrument_id"]
                rows.append(tagged)
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    receipts = [RC7DBaseline().run(SMOKE), QuantulumInstrument().run(SMOKE)]

    stanza = StanzaFamily()
    receipts.append(stanza.ud_receipt(SMOKE))
    receipts.append(stanza.constituency_receipt(SMOKE))

    core = CoreNLPFamily()
    try:
        receipts.extend(
            [
                core.openie_receipt(SMOKE),
                core.natlog_receipt(SMOKE),
                core.sutime_receipt(SMOKE),
                core.coref_quote_receipt(SMOKE),
            ]
        )
    finally:
        core.close()

    receipts.append(QualifiedSuParSDP().run(SMOKE))
    receipts.append(ProvenancedDebertaNLI().measure(SMOKE, _tagged_typed(receipts)[:16]))
    receipts.append(OWLRLReasoner().infer(SMOKE, {"subclass": []}))

    controls = evaluator_controls()
    raw_ok = all(
        r["raw_source"] == SMOKE and r["raw_source_sha256"] == source_sha(SMOKE)
        for r in receipts
    )
    failures = {
        r["instrument_id"]: r.get("runtime", {}).get("error", "unknown runtime failure")
        for r in receipts
        if r.get("runtime", {}).get("load_status") == "FAILED"
    }
    status = {
        r["instrument_id"]: {
            "status": r["status"],
            "runtime": r.get("runtime", {}),
            "proposed_dimensions": r.get("proposed_dimensions", []),
        }
        for r in receipts
    }
    result = {
        "phase": "PRE_HELD_OUT_RUNTIME_QUALIFICATION_V2",
        "scientific_result": False,
        "raw_source_sha256": source_sha(SMOKE),
        "raw_source_preserved": raw_ok,
        "evaluator_controls": controls,
        "identities": instrument_identities_v2(),
        "instrument_status": status,
        "runtime_failures": failures,
        "process_max_rss_kb": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "receipts": receipts,
        "qualification_rule": "raw source + evaluator controls must pass and every selected runtime must avoid load_status=FAILED",
    }
    (OUT / "QUALIFICATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "raw_source_preserved": raw_ok,
                "evaluator_controls": controls,
                "runtime_failures": failures,
                "status": status,
                "process_max_rss_kb": result["process_max_rss_kb"],
            },
            indent=2,
        )
    )
    if not raw_ok or not controls["all_passed"] or failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
