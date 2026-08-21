"""D11 shadow: can an adverse verdict on a *source-coverage* claim be gated structurally?

The defect (D11): ``A4_hard_contradiction`` returns ``contradicted`` on an absence
claim whose source is silent on the claimed material — three times on the
construction corpus, at an entailment score of 0.978 that gives no warning.

**A rejected design, recorded because it was nearly built.** The obvious
discriminator is lexical: "The procedure does not cover deviations detected after
batch release" is refuted by nothing that mentions *release*, whereas
"Relocation ... does not require requalification" is refuted by a passage naming
*relocation*. Measured, that separates the cases perfectly — it suppresses
exactly the three false adverse verdicts and keeps the one true one. It is also
precisely what DECISIONS.md forbids:

    no deterministic rule may flip or downgrade a degree on a lexical-overlap
    signal — overlap may flag, never decide.

That invariant exists because the v0.2 lexical matcher was falsified (4/98,
κ≈0), and because the same category error was then re-imported one layer up into
6b. A third import is not worth 2 points of agreement.

**What this probe measures instead** is a claim-side *structural* feature, the
same kind as ``has_explicit_negation`` or ``has_universal_quantifier``: a claim
is a **source-coverage claim** when clause-level negation scopes a *coverage
predicate* whose *subject refers to a document*. That is a property of the claim
alone — it never compares claim terms to passage terms — and it gates an adverse
decision, which is the sanctioned pattern (Decision H: "eligibility gates adverse
decisions").

SHADOW ONLY. Changes nothing; reports what the gate would do on both corpora.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.features import _parse

# A document, not a thing in the world. "The guidance does not address X" is a
# claim about a text; "The formulation does not contain X" is a claim about an
# object, and evidence can refute the second directly.
SOURCE_NOUNS = frozenset(
    {
        "guidance",
        "guideline",
        "procedure",
        "document",
        "standard",
        "policy",
        "protocol",
        "specification",
        "sop",
        "regulation",
        "section",
        "annex",
        "manual",
        "instruction",
        "chapter",
        "clause",
        "text",
        "requirement",
    }
)
# Predicates about the *presence of content in a text*. Deliberately excludes
# object-level verbs like "require" or "apply", where a document can genuinely
# assert the opposite and evidence can genuinely refute the claim.
COVERAGE_VERBS = frozenset(
    {
        "address",
        "cover",
        "mention",
        "prescribe",
        "specify",
        "state",
        "discuss",
        "describe",
        "define",
        "include",
        "list",
        "contain",
        "name",
        "reference",
    }
)


def _subject_of(tok: Any) -> Any | None:
    """The predicate's subject, walking up conjuncts when it is elided."""
    node = tok
    for _ in range(4):
        for child in node.children:
            if child.dep_ in {"nsubj", "nsubjpass"}:
                return child
        if node.dep_ == "conj" and node.head is not node:
            node = node.head
            continue
        return None
    return None


def is_source_coverage_claim(claim: str) -> dict[str, Any]:
    """True when clause-level negation scopes a coverage predicate on a document."""
    doc = _parse(claim)
    for tok in doc:
        if tok.dep_ != "neg" or tok.head.pos_ not in {"VERB", "AUX"}:
            continue
        predicate = tok.head
        subject = _subject_of(predicate)
        subj_lemma = subject.lemma_.lower() if subject is not None else None
        verb_ok = predicate.lemma_.lower() in COVERAGE_VERBS
        subj_ok = subj_lemma in SOURCE_NOUNS if subj_lemma else False
        if verb_ok and subj_ok:
            return {
                "applies": True,
                "predicate": predicate.lemma_.lower(),
                "subject": subj_lemma,
            }
        return {
            "applies": False,
            "predicate": predicate.lemma_.lower(),
            "subject": subj_lemma,
            "why": f"verb_ok={verb_ok} subj_ok={subj_ok}",
        }
    return {"applies": False, "why": "no clause-level negation"}


def run_construction() -> list[dict[str, Any]]:
    R = Path(__file__).resolve().parents[2] / "outputs" / "2026-08-19-construction-gold"
    corpus = {c["case_id"]: c for c in json.loads((R / "corpus.json").read_text())["cases"]}
    results = json.loads((R / "audit_results.json").read_text())
    return [
        {
            "id": row["case_id"],
            "claim": corpus[row["case_id"]]["claim_text"],
            "gold": row["gold"],
            "cal": row["cal"],
            **is_source_coverage_claim(corpus[row["case_id"]]["claim_text"]),
        }
        for row in results["rows"]
    ]


def run_pilot(baseline: Path, current: Path | None) -> list[dict[str, Any]]:
    now: dict[str, str] = {}
    if current is not None:
        now = {r["claim_id"]: r["after"] for r in json.loads(current.read_text())["rows"]}
    rows = []
    for path in sorted((baseline / "traces").glob("*.json")):
        t = json.loads(path.read_text())
        rows.append(
            {
                "id": t["claim_id"],
                "claim": t["claim_text"],
                "cal": now.get(t["claim_id"], t["verdict"]["support_verdict"]),
                **is_source_coverage_claim(t["claim_text"]),
            }
        )
    return rows


_ADVERSE = {"contradicted", "unsupported"}


def report(name: str, rows: list[dict[str, Any]]) -> None:
    print(f"\n=== {name} ===")
    hits = [r for r in rows if r["applies"]]
    print(f"claims                       : {len(rows)}")
    print(f"source-coverage absence claims: {len(hits)}  {[r['id'] for r in hits]}")
    changed = [r for r in hits if r["cal"] in _ADVERSE]
    print(f"  ... currently adverse       : {len(changed)}   <- what the gate would change")
    for r in changed:
        gold = f" gold={r['gold']}" if "gold" in r else ""
        print(
            f"     {r['id']}{gold}: {r['cal']} -> not_checkable   [{r['subject']}/{r['predicate']}]"
        )
    kept = [r for r in rows if not r["applies"] and r["cal"] in _ADVERSE]
    print(f"  adverse verdicts KEPT       : {len(kept)}")
    for r in kept:
        gold = f" gold={r['gold']}" if "gold" in r else ""
        print(f"     {r['id']}{gold}: {r['cal']}  ({r.get('why')})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--baseline-run", type=Path)
    ap.add_argument("--current-verdicts", type=Path)
    args = ap.parse_args()
    report("construction gold (33)", run_construction())
    if args.baseline_run:
        report("PILOT-001 (98)", run_pilot(args.baseline_run, args.current_verdicts))


if __name__ == "__main__":
    main()
