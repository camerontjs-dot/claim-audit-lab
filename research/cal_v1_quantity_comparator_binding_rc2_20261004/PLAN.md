# CAL V1 RC2 — quantity comparator binding successor

Status: research preparation only. Parent issue: CAL #210. Trigger: Draft PR #209 `FALSIFIED_UNSAFE_FALSE_DECISION_RATE`.

## Decision under test

The next CAL V1 gate is not a weighting change. The predecessor false supports occurred because the quantity-relation judge matched values/year but failed to bind proposition-significant comparator semantics in ordinary constructions:

- `73 (3%) fewer than` versus a claim saying `more`;
- expenditure growth `slower than` versus a claim saying `faster`.

The existing synthesis policy did not create those errors. Do not retune it to hide them.

RC2 asks whether a bounded quantity/comparator representation can preserve operator, orientation, measure, quantity/unit and time/scope binding well enough to refuse or correctly decide these constructions without source-specific exceptions.

## Ordering invariant

1. Source identities are selected and partition roles are frozen in `SOURCE_POOL_SELECTION.json` before any comparator implementation change.
2. A local source custodian downloads the selected bytes once, records final URL/media type/status/raw SHA-256, runs leak/hygiene checks, and freezes `SOURCE_FREEZE.json`.
3. The candidate implementer may inspect development/calibration material only. Held-out bytes/claims stay sealed until candidate, evaluator and any synthesis policy bytes are frozen.
4. Exposed PR #209 failures and `DEVELOPMENT_CASES.json` may be used for implementation. They can never become held-out evidence again.
5. If calibration reveals a new semantic defect, that calibration set is burned. Freeze a successor before any held-out reveal.
6. Held-out execution is one decisive exposure. Preserve the first result.

## Required local representation

For every accepted quantity-relation measurement, the receipt must bind at least:

- claim/evidence comparator operator and orientation;
- compared roles/entities or value slots;
- measure/property;
- quantity/value and unit/dimension where material;
- time/scope qualifiers actually used;
- exact consumed claim/evidence spans;
- ambiguity/unresolved state;
- input identity and instrument identity.

A shared verb or matching numeric pair is not a relation by itself. Materially different operators must produce different local representations or explicit refusal.

## Comparator semantics

The development discriminator includes:

- `more/fewer`, `higher/lower`, `greater/less`;
- `faster/slower` with a shared growth verb;
- `increase/decrease`;
- equality/unchanged/tied;
- side swap plus direction inversion;
- parenthetical rates/percentages between value and comparator;
- non-equivalence of `not more` and `less`;
- multiple competing comparator cues;
- comparator attached to another clause/measure;
- percent versus percentage-point/rate versus count mismatch;
- measure mismatch;
- year/scope mismatch;
- non-quantity event input.

Exact exposed BJS/CMS failures are retained as development counterexamples, not hard-coded templates.

## Weak controls

The evaluator must kill at least:

1. quantity-only matching that ignores comparator;
2. shared-verb matching that ignores faster/slower;
3. comparator cue detection without role binding;
4. first-comparator-wins;
5. last-comparator-wins;
6. parenthetical comparator loss;
7. negation collapse (`not more` => `less`);
8. measure-blind numeric matching.

A self-test pass establishes only evaluator mechanics.

## Architecture preserved

RC0 mechanics remain frozen unless independently falsified:

- every process gets exact original input;
- process-local transformations and losses;
- sealed first-pass receipts before synthesis;
- failed/timeout/not-applicable distinctions;
- dependence-group clone invariance;
- hard required guards;
- material support/refute conflict cannot be averaged away.

RC2 does not widen all semantic families.

## Fresh source qualification

The preselected source set is deliberately different from the exact source identities used in #193, #203 and #209. The URLs are public and authoritative, but selection does not imply any claim label.

After raw-byte freeze:

- calibration may be read and adjudicated;
- held-out bytes/claims remain sealed from implementation;
- at least one held-out source must produce an event/non-quantity case so early routing is observable;
- quantity cases should include diverse comparator syntax, not only the exposed failure forms;
- no source replacement after observing candidate behavior.

The held-out error rule remains fail-fast on any critical false deciding result.

## Product regression

Run the maintained suite in the declared `[v1]` environment. Preserve PR #209's scanner collision on frozen EPA bytes as a separate hygiene/test-classification issue. Do not edit old frozen evidence to make the scanner green.

## Non-claims

A comparator-binding pass would not establish:
- general natural-language usefulness;
- correct weighting across all claim types;
- universal semantic-family coverage;
- Contract C suitability;
- release readiness.

It would authorize only the fresh source-disjoint natural-claim qualifier defined by #210.
