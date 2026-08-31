"""Pre-held-out runtime qualification. No scientific gold or held-out cases."""
from __future__ import annotations

import json
from pathlib import Path

from research.language_instrument_ablation_rc7e.contract import source_sha
from research.language_instrument_ablation_rc7e.evaluator import evaluator_controls
from research.language_instrument_ablation_rc7e.instruments import (
    RC7DBaseline, QuantulumInstrument, StanzaFamily, CoreNLPFamily, SuParSDP, DebertaNLI, OWLRLReasoner, instrument_identities,
)

OUT=Path("research/language_instrument_ablation_rc7e/results")
SMOKE = "Only reviewers may approve the packet before 2026-09-01. Dana reviewed the dossier. She said, \"The packet is ready.\" Exactly 3 auditors signed the release."


def main() -> None:
    OUT.mkdir(parents=True,exist_ok=True)
    receipts=[]
    receipts.append(RC7DBaseline().run(SMOKE))
    receipts.append(QuantulumInstrument().run(SMOKE))
    stanza=StanzaFamily()
    receipts.append(stanza.ud_receipt(SMOKE))
    receipts.append(stanza.constituency_receipt(SMOKE))
    core=CoreNLPFamily()
    try:
        receipts.extend([core.openie_receipt(SMOKE),core.natlog_receipt(SMOKE),core.sutime_receipt(SMOKE),core.coref_quote_receipt(SMOKE)])
    finally: core.close()
    supar=SuParSDP(); receipts.append(supar.run(SMOKE))
    typed=[row for r in receipts for row in r.get("candidate_atoms",[]) if row.get("scorable")]
    receipts.append(DebertaNLI().measure(SMOKE,typed[:12]))
    receipts.append(OWLRLReasoner().infer(SMOKE,{"subclass":[]}))
    controls=evaluator_controls()
    raw_ok=all(r["raw_source"]==SMOKE and r["raw_source_sha256"]==source_sha(SMOKE) for r in receipts)
    result={
        "phase":"PRE_HELD_OUT_RUNTIME_QUALIFICATION",
        "scientific_result":False,
        "raw_source_sha256":source_sha(SMOKE),
        "raw_source_preserved":raw_ok,
        "evaluator_controls":controls,
        "identities":instrument_identities(),
        "instrument_status":{r["instrument_id"]:{"status":r["status"],"runtime":r.get("runtime",{}),"proposed_dimensions":r.get("proposed_dimensions",[])} for r in receipts},
        "receipts":receipts,
    }
    (OUT/"QUALIFICATION.json").write_text(json.dumps(result,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({"raw_source_preserved":raw_ok,"evaluator_controls":controls,"status":result["instrument_status"]},indent=2))
    if not raw_ok or not controls["all_passed"]:
        raise SystemExit(2)

if __name__=="__main__":main()
