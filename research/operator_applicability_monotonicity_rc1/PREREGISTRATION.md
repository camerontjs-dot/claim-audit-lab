# Semantic Operator Applicability + Monotonicity RC1 — Preregistration

## Classification

Research Infrastructure / epistemic-machinery successor experiment.

Parent evidence is frozen PR #39. This experiment does not rerun the NLI model. It replays only frozen Cohort A receipts so that operator-policy changes cannot alter measurements.

## Live authority at start

- production main: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- PR #39 current head/base for this successor: `8f8ec3593bbfe52e26c1fa7d39372acf6458993a`
- accepted Cohort A science head: `ba1310d73ab63adf7c83de2f1e130f7f00a665af`
- accepted Cohort A Actions run: `33286159031`
- accepted Cohort A artifact id: `9724541749`
- accepted Cohort A artifact archive digest: `sha256:afb6c1bcc81aff2526e9dcc3f4bd270d68333b8a909bec69c853ab5bdc6259d0`
- accepted Cohort A RESULTS SHA256: `sha256:38cd6f29eab0ea6e0f50e737814b993aaf45a3919cacb5e02296289516e112d7`

PR #40 is a separate NLI-measurement experiment stacked on #39. RC1 must not read, modify, or depend on PR #40.

## Hypotheses

H1. A4 non-entailment is not evidence that a refutation contribution is semantically invalid. A4 may positively validate a refutation when its exact receipt-bound canonical complement is entailed, but a non-entailing or abstained probe supplies no invalidation authority.

Falsifier: a documented operator contract or receipt demonstrates that A4 non-entailment validly proves the original refutation contribution false.

H2. Removing invalidation authority alone is insufficient. If a mixed eligible state loses one arm only because that arm becomes semantically unresolved, the remaining arm must not acquire terminal authority.

Falsifier: the frozen receipt contains an independent assessment that resolves the opposite arm rather than merely removing it.

H3. The CG-23b strengthening should disappear under H1+H2 without changing NLI measurements, thresholds, production rules, or Contract C.

## Frozen counterfactual policy

1. Preserve all frozen measurements, eligibility states, passage IDs, source-boundary inputs, and receipts.
2. For recorded A4 judgments:
   - `valid` remains `valid`;
   - `invalid` becomes `unknown` because non-entailment does not prove invalidity;
   - `unknown` remains `unknown`.
3. No A4 `unknown` contribution may decide.
4. Monotonicity guard: when the eligible state is `mixed`, removing one arm only through unresolved/unknown semantic validity cannot allow the other arm to become a decided support/adverse conclusion. Guarded outcome is abstention with reason `unresolved_mixed_evidence`.
5. No new semantic operator is invented. Numeric, quantity, threshold, scope, category, and generic contradiction relations remain unvalidated unless an already-frozen applicable receipt supplies authority.

## Primary cases

- CG-23b: frozen strengthening counterexample.
- CG-12a / CG-12b: numeric/time contradiction.
- CG-24: scope/numeric contradiction.
- CG-08a / CG-08b / CG-21: source-boundary family.
- CG-09a / CG-09b / CG-22: source-boundary family.

All 33 cases are replayed as controls from frozen receipts; no new model execution occurs.

## Success is not parity

Primary questions:

- Does CG-23b stop strengthening?
- Does A4 stop manufacturing invalidity from non-entailment?
- Do numeric/scope contradictions remain unknown when no typed operator exists?
- Does the firewall avoid creating new support↔adverse transitions?
- What unresolved state remains after the firewall?

No threshold tuning. No model replacement. No production path change. No Contract C change.
