# Research Results 05 — CAL Contract-B consumer seam

**Branch:** `research/obligation-composition-shadow`  
**Draft PR:** #1  
**Preregistration:** `docs/research/brief-05-cal-consumer-seam.md` and issue #4  
**Canonical tri-repo discussion:** `camerontjs-dot/apparatus-contracts#1`  
**Code-bearing head:** `9018bd826eeb938e5c300316affa2c13ae0db9fa`  
**GitHub Actions:** Public suite run #17 (`33029867798`)  
**Production impact:** none

## Executive result

Rung 05 supports a clean CAL-side ownership boundary:

> Contract-B metadata may be retained as evidence-world context, but proposition-specific semantic measurement and decision eligibility are CAL-owned states and must not be silently equated with upstream labels.

The most diagnostic metamorphic test changed only the Contract-B `trust_level` from `primary` to `secondary` while freezing claim text, passage text, retrieval score, entailment response, aggregation, features, and CAL config.

Observed:

- retrieval trace: unchanged;
- entailment trace: unchanged;
- aggregate semantic signal: unchanged;
- final verdict: changed;
- the change was attributable to CAL rule `P1_eligibility_suppressed`.

This locates the trust-dependent behavior in the CAL policy layer rather than in the evidence semantics or Contract-B handoff itself.

## Public-suite result

Public suite run #17 passed completely:

- **996 passed**;
- **5 skipped**;
- **48 research-artifact tests deselected**;
- **7 existing Torch JIT deprecation warnings**;
- Ruff: all checks passed;
- Ruff format: 50 files already formatted;
- mypy: success, no issues in 49 source files.

Relative to the Rung 04 baseline of 988 passing tests, Rung 05 added eight passing consumer-seam tests.

## H05-1 — Nomination-lane invariance

**Result: supported for CAL v1.**

The same admitted passage was moved from C-B `evidence_passages` to `counterevidence_passages` without changing its text, identity, or source.

Observed:

- `v1.intake.bundle_to_requests()` produced the same `AuditRequest.passages` set and claim text;
- the legacy adapter changed support/counter scopes when the upstream container changed.

Interpretation:

- the current v1 intake already implements the desired seam: EB support/counter containers are not semantic channel restrictions;
- the legacy scoped adapter is historical coupling and should not define new CAL work.

This aligns with the Evidence Bundler shadow result that nomination rank/score/role may remain auditable upstream while being blinded from the CAL semantic measurement view.

## H05-2 — Semantic measurement independence from trust tier

**Result: supported.**

Primary and secondary variants used identical claim text, passage text, passage identity, retrieval admission and score, deterministic entailer response, aggregator, features, and audit config. Only `Passage.source_meta["trust_level"]` differed.

Observed:

- retrieval records were equal;
- entailment records were equal;
- aggregate support signals were equal.

The v1 `Entailer` protocol receives claim text, premise text, and passage ID only. Trust metadata therefore does not alter the measured semantic relation in this path.

## H05-3 — Current P1 is a CAL policy dependency

**Result: supported.**

Using the same weak refutation signal:

```text
primary trust
  semantic measurement: contradict, 0.50
  final degree: unsupported

secondary trust
  semantic measurement: contradict, 0.50
  CAL rule P1_eligibility_suppressed fires
  final result: not_checkable / no_entail_signal
```

The evidence did not change what it said. CAL changed what the evidence was allowed to establish.

The current rule may ultimately be defensible as a conservative policy for a particular audit context, but Contract B itself does not define `secondary` or `background` as proposition-ineligible. Therefore the transformation should be understood as:

```text
Contract fact: trust_level = secondary
        ↓
CAL policy / assessment
        ↓
eligible | ineligible | unknown
```

not `secondary == ineligible`.

## H05-4 — Explicit assessment separation

**Result: supported in the additive shadow model.**

The same measured refutation was supplied with one of three receipt-bound `EligibilityAssessment` states.

| Explicit assessment | Result |
|---|---|
| `eligible` | decided `contradicted` |
| `ineligible` | abstained `no_eligible_contribution` |
| `unknown` | abstained `eligibility_unknown` |

The evidence contribution and measurement remain present in every case. Only explicit decision participation changes.

`EvidenceDecisionInput` does not contain `trust_level`, `source_reliability`, or an implicit `authority` field. CAL can therefore retain contract facts in the intake ledger while requiring a named, receipt-bound assessment before those facts affect eligibility.

## H05-5 — No invented context

**Result: supported for the tested shadow boundary.**

A passage ID deliberately containing the word `secondary` produced no automatic eligibility state. With explicit eligibility left `unknown`, the shadow abstained `eligibility_unknown`.

## Legacy adapter finding

The legacy Contract-B adapter maps `primary → high`, `secondary → medium`, and `background → low` into CAL source reliability. Rung 05 does not prove those mappings are wrong for every use case. It establishes that they are semantic promotions, not lossless contract translations. For new CAL work they should be treated as legacy behavior to supersede, not canonical handoff semantics.

## Symmetry with the Evidence Bundler seam experiment

The independently developed EB shadow on `camerontjs-dot/evidence-bundler#4` reached the complementary result:

- preserve mechanical/context facts upstream;
- retain nomination/admission history;
- blind nomination rank/score/role from semantic measurement;
- carry aperture/search/count facts without an upstream completeness conclusion;
- keep proposition-specific CAL judgments out of the minimal handoff.

Rung 05 provides the consumer-side mirror:

- v1 can consume the full admitted evidence set without honoring EB semantic lanes;
- semantic measurement can remain independent of trust metadata;
- a trust-dependent decision currently enters only through a named CAL rule;
- the additive shadow can replace implicit metadata equivalence with explicit eligibility receipts.

Together these results support the candidate seam:

```text
EB / Contract B
  facts + provenance + admission + coverage facts
            │
            ▼
CAL intake ledger
  preserve those facts verbatim
            │
            ▼
CAL semantic measurement
  claim/passage relation, upstream nomination blinded
            │
            ▼
CAL assessment receipts
  eligibility / validity / temporal applicability /
  authority applicability / completeness
            │
            ▼
CAL decision participation and verdict
```

## What is now supported

Promote as research constraints:

1. fail-closed Contract-B integrity verification before audit;
2. full admitted-passage intake for CAL v1 regardless of EB support/counter nomination lane;
3. separation of evidence semantics from source/trust metadata;
4. explicit CAL ownership of proposition-specific decision eligibility;
5. receipt-bound `eligible | ineligible | unknown` rather than implicit trust equivalence in the shadow architecture;
6. unknown eligibility causes abstention;
7. retain Contract-B facts even when a later CAL judgment makes a contribution non-deciding.

## What remains unresolved

Rung 05 does **not** establish the correct policy for secondary/background evidence; whether trust should affect positive decisions, adverse decisions, both, or neither; how authority differs from source class; which factual context fields need a future Contract-B extension; whether CAL results should remain copied/resealed C-B artifacts or become separate immutable CAL receipts; or whether the EB minimal-context shadow survives real tri-repository CAL execution.

## Next discriminating test

Do not invent another minimal handoff representation. Use the exact Evidence Bundler shadow fixture and implementation from pinned EB head `b4ca9111f5957ef7e7955e2c5024f2280ee19eb5`.

Make CAL consume the same evidence world through current-C-B-shaped V0, EB minimal-context V1, and full-sidecar V2. V0 should fail explicitly for unavailable decision state; V1 should build a pre-assessment ledger without defaults; V1 and V2 should produce the same pre-assessment measurement view; V2's supplied CAL judgments must not become authoritative upstream facts; nomination-only mutations must not change semantic measurement; mechanical-fact mutations must change relevant CAL context; and CAL-produced assessments must be independently receipt-bound.

That true tri-repository execution is the highest-value remaining seam test.
