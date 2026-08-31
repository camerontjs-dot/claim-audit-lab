from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from research.population_semantics_contract_rc5b.consumer import relation as frozen_relation

from . import gate, oracle
from .build_corpus import build
from .legacy import collapse


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    payload = build()

    disagreements = []
    authorized_consumer_errors = []
    authorized_rows = []
    blocked_rows = []
    legacy_laundering = []
    status_counts = Counter()

    for item in payload["cases"]:
        receipt = item["receipt"]
        o = oracle.evaluate(receipt)
        g = gate.evaluate(receipt)
        if o != g:
            disagreements.append({"case_id": item["case_id"], "oracle": o, "gate": g, "receipt": receipt})
            continue
        status_counts[o["authorization"]] += 1
        if o["authorization"] == "AUTHORIZED":
            try:
                rel = frozen_relation(o["case"])
                authorized_rows.append({"case_id": item["case_id"], "relation": rel, "case": o["case"], "tags": item["tags"]})
            except Exception as exc:
                authorized_consumer_errors.append({"case_id": item["case_id"], "error": repr(exc), "case": o["case"]})
        else:
            blocked_rows.append({"case_id": item["case_id"], "blockers": o["blockers"], "tags": item["tags"]})
            try:
                legacy_case = collapse(receipt)
                legacy_relation = frozen_relation(legacy_case)
                legacy_laundering.append({
                    "case_id": item["case_id"],
                    "blockers": o["blockers"],
                    "legacy_relation": legacy_relation,
                    "legacy_case": legacy_case,
                })
            except Exception as exc:
                legacy_laundering.append({"case_id": item["case_id"], "blockers": o["blockers"], "legacy_error": repr(exc)})

    invalid_results = []
    for item in payload["invalid_cases"]:
        row = {"case_id": item["case_id"], "oracle_rejected": False, "gate_rejected": False}
        for name, fn in (("oracle", oracle.evaluate), ("gate", gate.evaluate)):
            try:
                fn(item["receipt"])
            except Exception as exc:
                row[f"{name}_rejected"] = True
                row[f"{name}_error"] = repr(exc)
        invalid_results.append(row)

    mutation_results = []
    for m in payload["mutations"]:
        before = oracle.evaluate(m["before"])
        after = oracle.evaluate(m["after"])
        passed = before["authorization"] == "AUTHORIZED"
        if m["target_status"] == "semantic_unknown":
            passed = passed and after["authorization"] == "AUTHORIZED"
        else:
            passed = passed and after["authorization"] == "NOT_AUTHORIZED"
        mutation_results.append({"name": m["name"], "passed": passed, "before": before["authorization"], "after": after["authorization"]})

    witness = {}
    for target in ("semantic_unknown", "extraction_unresolved", "insufficient_authority"):
        m = next(x for x in payload["mutations"] if x["name"] == f"only_membership_to_{target}")
        out = oracle.evaluate(m["after"])
        witness[target] = {"authorization": out["authorization"], "blockers": out["blockers"]}
        if out["authorization"] == "AUTHORIZED":
            witness[target]["relation"] = frozen_relation(out["case"])

    contract_sufficient = (
        not disagreements
        and not authorized_consumer_errors
        and all(r["oracle_rejected"] and r["gate_rejected"] for r in invalid_results)
        and all(r["passed"] for r in mutation_results)
        and witness["semantic_unknown"]["authorization"] == "AUTHORIZED"
        and witness["extraction_unresolved"]["authorization"] == "NOT_AUTHORIZED"
        and witness["insufficient_authority"]["authorization"] == "NOT_AUTHORIZED"
        and len(legacy_laundering) > 0
    )

    if disagreements or authorized_consumer_errors:
        state = "CONTRACT_INCOMPLETE"
    elif not (witness["semantic_unknown"]["authorization"] == "AUTHORIZED" and witness["extraction_unresolved"]["authorization"] == "NOT_AUTHORIZED"):
        state = "DISTINCTION_NOT_JUSTIFIED"
    elif not all(r["oracle_rejected"] and r["gate_rejected"] for r in invalid_results):
        state = "APPARATUS_INVALID"
    else:
        state = "CONTRACT_SUFFICIENT" if contract_sufficient else "CONTRACT_INCOMPLETE"

    results = {
        "scientific_state": state,
        "corpus_sha256": payload["sha256"],
        "case_count": len(payload["cases"]),
        "invalid_case_count": len(payload["invalid_cases"]),
        "mutation_count": len(payload["mutations"]),
        "oracle_gate_disagreements": len(disagreements),
        "authorized_consumer_errors": len(authorized_consumer_errors),
        "authorization_counts": dict(status_counts),
        "invalid_cases_rejected_by_both": sum(r["oracle_rejected"] and r["gate_rejected"] for r in invalid_results),
        "mutations_passed": sum(r["passed"] for r in mutation_results),
        "legacy_laundering_witnesses": len(legacy_laundering),
        "semantic_unknown_vs_failure_witness": witness,
        "semantic_note": "extraction_unresolved and insufficient_authority are both semantically NOT_AUTHORIZED in RC7A; their distinction is diagnostic/provenance, not claimed semantically irreducible.",
    }

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    (out / "DISAGREEMENTS.json").write_text(json.dumps(disagreements, indent=2, sort_keys=True) + "\n")
    (out / "AUTHORIZED.json").write_text(json.dumps(authorized_rows, indent=2, sort_keys=True) + "\n")
    (out / "BLOCKED.json").write_text(json.dumps(blocked_rows, indent=2, sort_keys=True) + "\n")
    (out / "LEGACY_LAUNDERING.json").write_text(json.dumps(legacy_laundering, indent=2, sort_keys=True) + "\n")
    (out / "INVALID_CASES.json").write_text(json.dumps(invalid_results, indent=2, sort_keys=True) + "\n")
    (out / "MUTATIONS.json").write_text(json.dumps(mutation_results, indent=2, sort_keys=True) + "\n")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
