from __future__ import annotations

import argparse
import ast
import base64
import collections
import hashlib
import json
import zlib
from pathlib import Path

SEM = {"established", "semantic_unknown"}

def norm(v):
    return v.strip().lower() if isinstance(v, str) else v

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def row_error(r):
    if r.get("gold_relation") is not None:
        return not r.get("semantic_case_exact", False)
    if (r.get("gold") or {}).get("status") == "out_of_jurisdiction":
        return not r.get("ood_correct", False)
    fr = r.get("field_rows") or []
    return bool(r.get("unsafe") or r.get("invalid_output") or any(not f.get("status_exact", False) for f in fr))

def semantic_agree(a, b):
    pa = a.get("prediction") or {}
    pb = b.get("prediction") or {}
    fam = a.get("family") if a.get("family") != "out_of_jurisdiction" else None
    if fam and pa.get("status") == "receipt" and pb.get("status") == "receipt" and pa.get("family") == pb.get("family") == fam:
        af = pa.get("fields") or {}
        bf = pb.get("fields") or {}
        fields = sorted(set(af) | set(bf))
        for f in fields:
            av = af.get(f, {})
            bv = bf.get(f, {})
            if (av.get("status"), norm(av.get("value"))) != (bv.get("status"), norm(bv.get("value"))):
                return False
        return True
    return pa.get("status") == pb.get("status") and pa.get("family") == pb.get("family")

def field_rows_by_name(row):
    return {f["field"]: f for f in row.get("field_rows") or []}

def field_semantic_correct(fr):
    if not fr:
        return False
    gst = fr.get("gold_status")
    if gst in SEM:
        return bool(fr.get("value_exact"))
    return bool(fr.get("status_exact"))

def field_diagnostic_correct(fr):
    if not fr:
        return False
    if not field_semantic_correct(fr):
        return False
    gst = fr.get("gold_status")
    if gst in SEM:
        return bool(fr.get("warrant_exact") and fr.get("span_coverage") and not fr.get("span_disjoint"))
    return True

def field_unsafe(fr):
    if not fr:
        return False
    return bool(fr.get("unsafe_wrong_semantics") or fr.get("unsafe_ungrounded") or fr.get("unsafe_fabrication"))

def decode_payload(sealed_payload_path):
    source = Path(sealed_payload_path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    vals = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in {"PAYLOAD_B64", "PAYLOAD_SHA256"}:
                vals[name] = ast.literal_eval(node.value)
    raw = vals["PAYLOAD_B64"].encode("ascii")
    if len(raw) != 12787:
        raise RuntimeError(f"unexpected sealed transport length: {len(raw)}")
    repaired = raw[:3168] + b"I" + raw[3168:]
    compressed = base64.b64decode(repaired)
    compressed_sha = hashlib.sha256(compressed).hexdigest()
    if compressed_sha != "4f3ea5c6f00e85dfc60b833eac397626503338311c9305a81cc3ef6672af6aa2":
        raise RuntimeError(f"governed compressed hash mismatch: {compressed_sha}")
    plain = zlib.decompress(compressed)
    obj = json.loads(plain.decode("utf-8"))
    canon = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    semantic_sha = hashlib.sha256(canon).hexdigest()
    if semantic_sha != vals["PAYLOAD_SHA256"]:
        raise RuntimeError(f"sealed semantic hash mismatch: {semantic_sha} != {vals['PAYLOAD_SHA256']}")
    if semantic_sha != "35777672cd1a23b52864d69523ce504077b604b400fdce8adad2077fe600ac2a":
        raise RuntimeError(f"unexpected semantic payload identity: {semantic_sha}")
    return obj, {"compressed_sha256": compressed_sha, "semantic_sha256": semantic_sha}

def gold_warrant(row, field):
    gf = (((row.get("gold") or {}).get("fields") or {}).get(field) or {})
    ws = gf.get("warrants") or []
    return "|".join(sorted(ws)) if ws else "(none)"

def case_failing_keys(a, b):
    afr = field_rows_by_name(a)
    bfr = field_rows_by_name(b)
    fields = sorted(set(afr) | set(bfr))
    keys = set()
    diagnostic_only = set()
    for f in fields:
        af = afr.get(f)
        bf = bfr.get(f)
        warrant = gold_warrant(a, f)
        key = f"{a.get('family')}|{f}|{warrant}"
        sem_fail = not field_semantic_correct(af) or not field_semantic_correct(bf)
        diag_fail = not field_diagnostic_correct(af) or not field_diagnostic_correct(bf)
        if sem_fail:
            keys.add(key)
        elif diag_fail:
            diagnostic_only.add(key)
    return keys, diagnostic_only

def greedy_case_coverage(case_to_keys, max_keys=3):
    remaining = set(case_to_keys)
    chosen = []
    covered = set()
    for _ in range(max_keys):
        best_key = None
        best_cases = set()
        all_keys = sorted({k for cid in remaining for k in case_to_keys[cid]})
        for key in all_keys:
            cases = {cid for cid in remaining if key in case_to_keys[cid]}
            if len(cases) > len(best_cases):
                best_key = key
                best_cases = cases
        if not best_key or not best_cases:
            break
        chosen.append({"key": best_key, "new_cases": len(best_cases), "case_ids": sorted(best_cases)})
        covered |= best_cases
        remaining -= best_cases
    total = len(case_to_keys)
    return {
        "total_cases": total,
        "covered_cases": len(covered),
        "coverage": len(covered) / total if total else None,
        "chosen": chosen,
        "uncovered_case_ids": sorted(set(case_to_keys) - covered),
    }

def rate(n, d):
    return n / d if d else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a-predictions", required=True)
    ap.add_argument("--a-mutations", required=True)
    ap.add_argument("--b-predictions", required=True)
    ap.add_argument("--b-mutations", required=True)
    ap.add_argument("--sealed-payload", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    Arows = load_json(args.a_predictions)
    Brows = load_json(args.b_predictions)
    Amuts = load_json(args.a_mutations)
    Bmuts = load_json(args.b_mutations)
    payload, payload_identity = decode_payload(args.sealed_payload)

    A = {r["case_id"]: r for r in Arows}
    B = {r["case_id"]: r for r in Brows}
    P = {c["case_id"]: c for c in payload["cases"]}
    ids = sorted(set(A) & set(B) & set(P))
    if len(ids) != 180:
        raise RuntimeError(f"expected 180 overlapping cases, got {len(ids)}")

    cohort_counts = collections.Counter()
    family_counts = collections.defaultdict(collections.Counter)
    partition_counts = collections.defaultdict(collections.Counter)
    case_records = []
    agree_wrong_keys = {}
    agree_wrong_diag_keys = {}
    field_agg = collections.defaultdict(lambda: collections.Counter())
    failing_families = set()

    for cid in ids:
        a, b, p = A[cid], B[cid], P[cid]
        agree = semantic_agree(a, b)
        ae, be = row_error(a), row_error(b)
        if agree and not ae and not be:
            cohort = "both_correct"
        elif agree:
            cohort = "agree_but_wrong"
        else:
            cohort = "disagree"

        cohort_counts[cohort] += 1
        family = a["family"]
        partition = a["partition"]
        family_counts[family][cohort] += 1
        partition_counts[partition][cohort] += 1

        keys, diag_keys = case_failing_keys(a, b)
        if cohort == "agree_but_wrong":
            agree_wrong_keys[cid] = keys
            agree_wrong_diag_keys[cid] = diag_keys
            if keys or diag_keys:
                failing_families.add(family)

        afr, bfr = field_rows_by_name(a), field_rows_by_name(b)
        for f in sorted(set(afr) | set(bfr)):
            af, bf = afr.get(f), bfr.get(f)
            warrant = gold_warrant(a, f)
            key = f"{family}|{f}|{warrant}"
            c = field_agg[key]
            c["occurrences"] += 1
            c[f"cohort:{cohort}"] += 1
            c[f"partition:{partition}"] += 1
            asem = field_semantic_correct(af)
            bsem = field_semantic_correct(bf)
            adiag = field_diagnostic_correct(af)
            bdiag = field_diagnostic_correct(bf)
            if not asem:
                c["a_semantic_errors"] += 1
            if not bsem:
                c["b_semantic_errors"] += 1
            if not adiag:
                c["a_diagnostic_errors"] += 1
            if not bdiag:
                c["b_diagnostic_errors"] += 1
            if not asem and not bsem:
                c["shared_semantic_errors"] += 1
            if field_unsafe(af):
                c["a_unsafe_fields"] += 1
            if field_unsafe(bf):
                c["b_unsafe_fields"] += 1
            av = ((a.get("prediction") or {}).get("fields") or {}).get(f, {})
            bv = ((b.get("prediction") or {}).get("fields") or {}).get(f, {})
            if (av.get("status"), norm(av.get("value"))) != (bv.get("status"), norm(bv.get("value"))):
                c["semantic_disagreements"] += 1

        disagree_subtype = None
        if cohort == "disagree":
            if ae and be:
                disagree_subtype = "both_wrong"
            elif ae:
                disagree_subtype = "a_wrong_b_correct"
            elif be:
                disagree_subtype = "a_correct_b_wrong"
            else:
                disagree_subtype = "both_correct_but_different"
        case_records.append({
            "case_id": cid,
            "family": family,
            "partition": partition,
            "cohort": cohort,
            "disagree_subtype": disagree_subtype,
            "text": p.get("text"),
            "query": p.get("query"),
            "a_error": ae,
            "b_error": be,
            "a_unsafe": bool(a.get("unsafe")),
            "b_unsafe": bool(b.get("unsafe")),
            "a_wrong_relation": bool(a.get("wrong_relation")),
            "b_wrong_relation": bool(b.get("wrong_relation")),
            "a_authorized": bool(a.get("authorized")),
            "b_authorized": bool(b.get("authorized")),
            "a_relation": a.get("pred_relation"),
            "b_relation": b.get("pred_relation"),
            "gold_relation": a.get("gold_relation"),
            "semantic_failure_keys": sorted(keys),
            "diagnostic_only_failure_keys": sorted(diag_keys),
        })

    partition_error_rates = {}
    for impl, rows in (("A", A), ("B", B)):
        partition_error_rates[impl] = {}
        for part in ("construction", "paraphrase", "authority_boundary", "out_of_jurisdiction"):
            rs = [rows[cid] for cid in ids if rows[cid]["partition"] == part]
            errs = sum(row_error(r) for r in rs)
            partition_error_rates[impl][part] = {"cases": len(rs), "errors": errs, "error_rate": rate(errs, len(rs))}
        c = partition_error_rates[impl]["construction"]["error_rate"]
        p = partition_error_rates[impl]["paraphrase"]["error_rate"]
        partition_error_rates[impl]["paraphrase_minus_construction"] = (p - c) if p is not None and c is not None else None

    coverage = greedy_case_coverage(agree_wrong_keys, 3)
    diag_coverage = greedy_case_coverage(agree_wrong_diag_keys, 3)

    field_rows = []
    for key, counts in field_agg.items():
        family, field, warrant = key.split("|", 2)
        row = {"key": key, "family": family, "field": field, "warrant": warrant, **dict(counts)}
        occ = counts["occurrences"]
        row["a_semantic_error_rate"] = rate(counts["a_semantic_errors"], occ)
        row["b_semantic_error_rate"] = rate(counts["b_semantic_errors"], occ)
        row["semantic_disagreement_rate"] = rate(counts["semantic_disagreements"], occ)
        row["agree_but_wrong_case_rate"] = rate(counts["cohort:agree_but_wrong"], occ)
        field_rows.append(row)
    field_rows.sort(key=lambda r: (
        -(r.get("cohort:agree_but_wrong", 0)),
        -(r.get("shared_semantic_errors", 0)),
        -(r.get("semantic_disagreements", 0)),
        r["key"],
    ))

    AM = {m["name"]: m for m in Amuts}
    BM = {m["name"]: m for m in Bmuts}
    mut_names = sorted(set(AM) & set(BM))
    mutation_records = []
    mut_sig_counts = collections.Counter()
    failed_mutations = []
    for name in mut_names:
        a, b = AM[name], BM[name]
        sig = f"{a['family']}|{','.join(sorted(a.get('expected_changed_fields') or []))}"
        status = "both_pass" if a["passed"] and b["passed"] else ("a_only" if a["passed"] else ("b_only" if b["passed"] else "both_fail"))
        if status != "both_pass":
            mut_sig_counts[sig] += 1
            failed_mutations.append(name)
        before = a.get("before") or {}
        after = a.get("after") or {}
        mutation_records.append({
            "name": name,
            "family": a["family"],
            "expected_changed_fields": a.get("expected_changed_fields"),
            "a_observed_changed_fields": a.get("observed_changed_fields"),
            "b_observed_changed_fields": b.get("observed_changed_fields"),
            "a_passed": a["passed"],
            "b_passed": b["passed"],
            "status": status,
            "signature": sig,
            "before_text": ((P.get((before.get("case_id"))) or {}).get("text") if before.get("case_id") else None),
            "after_text": ((P.get((after.get("case_id"))) or {}).get("text") if after.get("case_id") else None),
        })

    top_mut_sigs = []
    remaining = sum(mut_sig_counts.values())
    covered = 0
    for sig, n in mut_sig_counts.most_common(3):
        top_mut_sigs.append({"signature": sig, "failed_mutations": n})
        covered += n
    mut_coverage = rate(covered, remaining)

    agree_wrong_count = cohort_counts["agree_but_wrong"]
    top3_coverage = coverage["coverage"] or 0
    para_penalty_a = partition_error_rates["A"]["paraphrase_minus_construction"] or 0
    para_penalty_b = partition_error_rates["B"]["paraphrase_minus_construction"] or 0
    distinct_keys = len({k for ks in agree_wrong_keys.values() for k in ks})
    families = {r["family"] for r in case_records if r["cohort"] == "agree_but_wrong" and (r["semantic_failure_keys"] or r["diagnostic_only_failure_keys"])}
    chosen_keys = {x["key"] for x in coverage["chosen"]}
    residual_families = {
        r["family"] for r in case_records
        if r["cohort"] == "agree_but_wrong"
        and not chosen_keys.intersection(r["semantic_failure_keys"])
        and (r["semantic_failure_keys"] or r["diagnostic_only_failure_keys"])
    }
    concentrated = agree_wrong_count >= 10 and top3_coverage >= 0.60
    distributed_surface = para_penalty_a >= 0.10 and para_penalty_b >= 0.10 and len(families) >= 2 and distinct_keys >= 6
    mutation_concentrated = (mut_coverage or 0) >= 0.60
    mixed = concentrated and distributed_surface and len(residual_families) >= 2

    if mixed:
        state = "MIXED_LOCALIZED_AND_DISTRIBUTED"
    elif concentrated and mutation_concentrated and not distributed_surface:
        state = "CONCENTRATED_CONSTRUCTION_GAPS"
    elif distributed_surface and not concentrated:
        state = "DISTRIBUTED_LINGUISTIC_LIMITATION"
    else:
        state = "INCONCLUSIVE_LOCALIZATION"

    results = {
        "scientific_state": state,
        "payload_identity": payload_identity,
        "case_count": len(ids),
        "cohort_counts": dict(cohort_counts),
        "family_cohort_counts": {k: dict(v) for k, v in sorted(family_counts.items())},
        "partition_cohort_counts": {k: dict(v) for k, v in sorted(partition_counts.items())},
        "partition_error_rates": partition_error_rates,
        "agree_but_wrong_semantic_key_greedy_coverage": coverage,
        "agree_but_wrong_diagnostic_key_greedy_coverage": diag_coverage,
        "agree_but_wrong_distinct_semantic_keys": distinct_keys,
        "agree_but_wrong_families": sorted(families),
        "residual_families_outside_top3_semantic_keys": sorted(residual_families),
        "failed_mutations": len(failed_mutations),
        "mutation_failure_signature_top3_coverage": mut_coverage,
        "top_mutation_failure_signatures": top_mut_sigs,
        "preregistered_predicates": {
            "concentrated": concentrated,
            "distributed_surface": distributed_surface,
            "mutation_concentrated": mutation_concentrated,
            "mixed": mixed,
        },
    }

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "CASE_COHORTS.json").write_text(json.dumps(case_records, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "FIELD_CONSTRUCTION_AGGREGATES.json").write_text(json.dumps(field_rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "MUTATION_LOCALIZATION.json").write_text(json.dumps(mutation_records, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    top_fields = field_rows[:12]
    both_correct = [r for r in case_records if r["cohort"] == "both_correct"]
    agree_wrong = [r for r in case_records if r["cohort"] == "agree_but_wrong"]
    disagree = [r for r in case_records if r["cohort"] == "disagree"]
    disagree_sub = collections.Counter(r["disagree_subtype"] for r in disagree)

    lines = [
        "# RC7B Failure Localization Results",
        "",
        f"Terminal localization state: **`{state}`**",
        "",
        "## Cohorts",
        "",
        f"- both correct: {len(both_correct)}",
        f"- agree but wrong: {len(agree_wrong)}",
        f"- disagree: {len(disagree)}",
        f"- disagreement subtypes: `{dict(disagree_sub)}`",
        "",
        "## Surface-generalization penalty",
        "",
        f"- A construction error rate: {partition_error_rates['A']['construction']['error_rate']:.3f}",
        f"- A paraphrase error rate: {partition_error_rates['A']['paraphrase']['error_rate']:.3f}",
        f"- A paraphrase penalty: {para_penalty_a:.3f}",
        f"- B construction error rate: {partition_error_rates['B']['construction']['error_rate']:.3f}",
        f"- B paraphrase error rate: {partition_error_rates['B']['paraphrase']['error_rate']:.3f}",
        f"- B paraphrase penalty: {para_penalty_b:.3f}",
        "",
        "## Agree-but-wrong concentration",
        "",
        f"- semantic failing-key top-3 coverage: {top3_coverage:.3f}",
        f"- semantic failing-key distinct count: {distinct_keys}",
        f"- affected families: {sorted(families)}",
        f"- residual families outside top-3 keys: {sorted(residual_families)}",
        "",
        "Greedy keys:",
    ]
    for x in coverage["chosen"]:
        lines.append(f"- `{x['key']}`: +{x['new_cases']} unique agree-but-wrong cases")
    lines += ["", "## Mutation localization", "", f"- failed by either implementation: {len(failed_mutations)} / {len(mut_names)}", f"- top-3 mutation-signature coverage: {mut_coverage:.3f}" if mut_coverage is not None else "- top-3 mutation-signature coverage: n/a"]
    for x in top_mut_sigs:
        lines.append(f"- `{x['signature']}`: {x['failed_mutations']} failures")
    lines += ["", "## Highest-signal field × warrant keys", ""]
    for r in top_fields:
        lines.append(
            f"- `{r['key']}`: occurrences={r['occurrences']}, agree_wrong={r.get('cohort:agree_but_wrong',0)}, "
            f"A_sem_err={r.get('a_semantic_errors',0)}, B_sem_err={r.get('b_semantic_errors',0)}, "
            f"shared_sem_err={r.get('shared_semantic_errors',0)}, disagreements={r.get('semantic_disagreements',0)}"
        )
    lines += ["", "## Representative agree-but-wrong cases", ""]
    for r in agree_wrong[:12]:
        text = (r.get("text") or "").replace("\n", " ")
        lines.append(f"- `{r['case_id']}` [{r['family']}/{r['partition']}]: {text}")
        lines.append(f"  - semantic failure keys: {r['semantic_failure_keys']}")
        if r["diagnostic_only_failure_keys"]:
            lines.append(f"  - diagnostic-only failure keys: {r['diagnostic_only_failure_keys']}")
    lines += ["", "## Representative disagreement cases", ""]
    for r in disagree[:12]:
        text = (r.get("text") or "").replace("\n", " ")
        lines.append(f"- `{r['case_id']}` [{r['disagree_subtype']}; {r['family']}/{r['partition']}]: {text}")
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "This analysis localizes observed failures. It does not establish that adding rules will repair them, and it does not establish that language interpretation is intrinsically probabilistic.",
        "",
        "No production authorization.",
        "",
    ]
    (out / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(results, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
