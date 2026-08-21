"""Generate docs/assets/traces.js from sealed CAL receipts.

Every number in the docs site demo is derived here from the sealed probe
directories, never hand-typed. Re-run to regenerate.
"""
import json, pathlib, hashlib, datetime

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROBE = ROOT / "outputs/2026-08-02-chunk-granularity-probe"
F8 = ROOT / "outputs/2026-08-02-qms-claim-generation/scaled-30/cal-audit/traces"
OUT = pathlib.Path(__file__).resolve().parents[1] / "docs/assets/traces.js"

rows = json.load(open(PROBE / "results.json"))
cases = []
for r in rows:
    doc, rel = r["source_doc_id"], r["relationship"]
    stem = f"{doc}_v{r['source_version']}__{rel}__00" if rel == "states" else f"{doc}_v{r['source_version']}__{rel}__01"
    f8p = F8 / f"{stem}.json"
    finep = PROBE / "traces" / f"{stem}__fine.json"
    if not (f8p.exists() and finep.exists()):
        continue
    f8, fine = json.load(open(f8p)), json.load(open(finep))
    cases.append({
        "id": r["claim_id"],
        "doc": doc,
        "rel": rel,
        "claim": r["claim_text"],
        "basis": r.get("author_basis", ""),
        "missKind": r["arms"]["section"]["reason"],
        "section": {
            "retrieval": [{"pid": x["passage_id"], "score": round(x["score"], 6)} for x in f8["retrieval"]],
            "rules": [x["rule_id"] for x in f8["rules_fired"]],
            "verdict": f8["verdict"]["support_verdict"],
            "reason": r["arms"]["section"]["reason"],
            "entail": r["arms"]["section"]["entail"],
            "signal": r["arms"]["section"]["signal"],
            "nPassages": r["arms"]["section"]["n_passages"],
        },
        "fine": {
            "retrieval": [{"pid": x["passage_id"], "score": round(x["score"], 6)} for x in fine["retrieval"]],
            "rules": [x["rule_id"] for x in fine["rules_fired"]],
            "verdict": fine["verdict"]["support_verdict"],
            "reason": r["arms"]["fine"]["reason"],
            "entail": r["arms"]["fine"]["entail"],
            "signal": r["arms"]["fine"]["signal"],
            "nPassages": r["arms"]["fine"]["n_passages"],
        },
        "rescued": r["arms"]["section"]["verdict"] != r["arms"]["fine"]["verdict"],
    })

floor = [c for c in cases if c["missKind"] == "no_evidence"]
ent = [c for c in cases if c["missKind"] == "no_entail_signal"]
summary = {
    "n": len(cases),
    "floorTotal": len(floor),
    "floorRescued": sum(1 for c in floor if c["rescued"]),
    "entailTotal": len(ent),
    "entailRescued": sum(1 for c in ent if c["rescued"]),
    "meanNeutralFine": round(sum(c["fine"]["entail"] for c in ent) / len(ent), 4),
    "meanNeutralSection": round(sum(c["section"]["entail"] for c in ent) / len(ent), 4),
    "fineTopMin": round(min(c["fine"]["retrieval"][0]["score"] for c in ent), 3),
    "fineTopMax": round(max(c["fine"]["retrieval"][0]["score"] for c in ent), 3),
    "retrievalFloor": 0.40,
    "supportedThreshold": 0.70,
    "generated": datetime.date.today().isoformat(),
}
payload = {"summary": summary, "cases": cases}
body = json.dumps(payload, indent=2)
digest = hashlib.sha256(body.encode()).hexdigest()[:16]
OUT.write_text(
    "// GENERATED FILE — do not edit by hand.\n"
    "// Produced by scripts/gen_docs_traces.py from sealed CAL receipts in\n"
    "// outputs/2026-08-02-chunk-granularity-probe/ and .../qms-claim-generation/.\n"
    f"// payload sha256[:16] = {digest}\n"
    f"window.CAL_TRACES = {body};\n"
)
print(f"wrote {OUT}  ({len(cases)} cases, sha {digest})")
print(json.dumps(summary, indent=2))
