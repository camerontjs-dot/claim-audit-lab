# Semantic Operator Applicability + Monotonicity RC1 — Results

## Classification

Research Infrastructure / epistemic-machinery successor experiment.

This is not production authorization. It does not change the CAL production path, thresholds, NLI model, Contract C, or production semantic operators.

## Frozen authority

- production main at experiment start: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- frozen parent PR #39 head: `8f8ec3593bbfe52e26c1fa7d39372acf6458993a`
- accepted Cohort A science head: `ba1310d73ab63adf7c83de2f1e130f7f00a665af`
- accepted Cohort A run: `33286159031`
- accepted Cohort A RESULTS SHA256: `sha256:38cd6f29eab0ea6e0f50e737814b993aaf45a3919cacb5e02296289516e112d7`
- accepted RC1 science head: `c105a705aa0db1f196639cdedef3f1993130ce0e`
- accepted RC1 Actions run: `33317475966`
- accepted RC1 artifact id: `9733897192`
- accepted RC1 artifact archive digest: `sha256:303c1484be86d82a40d617fc773f579f80bdc750c34e2a5c863a98932180f9e3`
- accepted RC1 RESULTS SHA256: `sha256:eebe2ced25e489f462fd8f8f3197a8d0da2692222117f2046f11f97d4e79f744`

## Apparatus deviations preserved

Several failed RC1 runs are preserved in Actions history.

Observed apparatus failures before the accepted scientific run included:

- Ruff line-length failures before scientific replay;
- literal escaped-newline corruption introduced by a repair attempt;
- a broken result-writer newline literal;
- frozen trace-path replay mismatch;
- eligibility/replay path mismatch;
- one workflow that incorrectly appeared green because a piped Python failure was masked by `tee`.

The accepted workflow was hardened with `set -o pipefail` and an explicit non-empty RESULTS assertion. The final replay also uses a copied RC1 eligibility receipt whose only changed field is the rebound trace path to the exact downloaded immutable Cohort A receipt directory.

These failures are part of the evidence record and are not rewritten away.

## Preregistered hypotheses

### H1

A4 non-entailment is not evidence that a refutation contribution is semantically invalid.

**RESULT: SUPPORTED.**

RC1 converted all 11 frozen A4 `invalid` judgments to `unknown` while leaving 3 A4 `valid` judgments valid. No measurement was changed.

Across all 33 frozen cases:

- A4 invalid → unknown: 11
- final A4 unknown judgments: 15
- final A4 valid judgments: 3
- new model execution: none
- threshold tuning: none

This removes negative decision authority from A4 non-entailment without inventing a replacement semantic operator.

### H2

Removing A4 invalidation authority alone would be insufficient; a separate mixed-state monotonicity guard would also be required to block CG-23b.

**RESULT: FALSIFIED by this frozen replay.**

The explicit monotonicity guard fired **0 times**.

CG-23b changed:

- frozen #39 explicit outcome: `supported`
- RC1 unguarded outcome: `abstain`
- RC1 guarded outcome: `abstain`

Therefore the A4 authority firewall alone was sufficient to block the strengthening counterexample in this case.

The reason is not that the adverse arm became valid. It remained semantically unresolved. Once A4 could no longer mark it invalid, the replay retained enough unknown semantic state to abstain.

### H3

CG-23b strengthening should disappear under the preregistered RC1 policy without changing measurements, thresholds, production rules, or Contract C.

**RESULT: SUPPORTED.**

CG-23b is the only terminal outcome changed by RC1 across the 33-case frozen cohort:

- #39 explicit: `supported`
- RC1: `abstain`

No support→adverse or adverse→support transition was created.

## Cohort-level result

RC1 guarded outcomes:

- supported: 5
- abstain: 28
- contradicted: 0

Relative to frozen #39, exactly one terminal outcome changed: CG-23b `supported → abstain`.

This is not evidence that RC1 has solved contradiction semantics. It is evidence that removing unjustified A4 invalidation authority prevents at least one observed false strengthening without destabilizing the rest of the frozen cohort.

## Numeric / contradiction slice

### OBSERVED

CG-12a, CG-12b, and CG-24 remain abstentions.

Their A4 non-entailment judgments became unknown rather than invalid, but no typed numeric/quantity/scope operator exists to validate the refutation.

For CG-12a and CG-12b:

- eligible state: refutation_only
- A4 status after firewall: unknown
- valid state: read_silent
- outcome: abstain

For CG-24:

- eligible state: refutation_only
- A4 statuses after firewall: unknown + unknown
- valid state: read_silent
- outcome: abstain

### INFERENCE

The firewall corrects operator overreach but does not supply missing numeric/relational authority.

That is the expected and desirable separation:

measurement exists → A4 cannot invalidate it → typed semantic validity is still unmeasured → abstain.

## Source-boundary slice

### OBSERVED

CG-08a / CG-08b / CG-21 remain abstentions after A4 invalid → unknown.

CG-09a / CG-09b / CG-22 retain one A4-valid refutation contribution plus one unknown contribution and also remain abstentions.

### INFERENCE

The source-boundary/completeness gap identified in Cohort A is not repaired by the A4 firewall. It remains a distinct missing-state/projection problem.

## What RC1 establishes

### OBSERVED

1. The frozen 33-case Cohort A can be replayed without any new model call.
2. A4 non-entailment can be stripped of invalidation authority without changing measurements.
3. That change affects only one terminal outcome in the frozen cohort.
4. The one changed outcome is exactly the known strengthening counterexample CG-23b.
5. CG-23b becomes abstention even before the explicit monotonicity guard fires.
6. Numeric/scope contradiction cases remain unknown rather than being promoted.
7. Source-boundary cases remain unresolved.
8. No new support↔adverse transition is created.

### INFERENCE

Operator applicability/authority is a real causal issue, not merely a descriptive correlation.

The minimal correction suggested by current evidence is smaller than initially hypothesized: first remove unjustified negative authority from A4. Do not yet promote a general monotonicity policy change merely because it sounded prudent.

### UNKNOWN

- whether A4 `valid` has sufficiently narrow applicability across every semantic family where it currently appears;
- what typed numeric/relational operator should validate numeric contradiction;
- how source-boundary/completeness should be represented in the explicit artifact;
- whether an independent consumer can safely use the artifact without importing legacy CAL semantics.

## Terminal disposition

**A4 negative-authority firewall: supported as a research finding.**

**General monotonicity guard requirement: not supported by this test; H2 was falsified.**

**Production promotion: not supported.**

**Next discriminating experiment: typed numeric/relational operator study, followed separately by source-boundary/scope receipt study.**
