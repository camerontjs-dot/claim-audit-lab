# Research Brief 03 — Relation preservation and verification-obligation composition

**Status:** preregistered shadow experiment  
**Branch:** `research/obligation-composition-shadow`  
**Baseline:** `main` at `376a62b57b32ddd2e937be408e877ad91e6b1367`  
**Production impact:** none. The released `run_audit` path, aggregator, rule file, CLI defaults, and public verdict semantics are unchanged.

## Question

CAL currently records every admitted passage-level NLI result, then the production
aggregator condenses those observations into one `SupportSignal` before the rule
layer emits a verdict.

This experiment asks:

> Does collapsing multiple passage-level observations into one winner discard
> decision-relevant evidence that should remain available until eligibility,
> semantic validity, aperture, and claim composition have been resolved?

A second, narrower question tests the audit abstraction proposed for future CAL
work:

> When a complex claim is represented as explicitly declared verification
> obligations, does independent obligation testing prevent a strong component
> from laundering an unresolved or unsupported dependency?

The experiment does **not** test automatic claim decomposition. Obligations are
manually declared so decomposition quality cannot confound the aggregation test.

## Why this experiment is possible without redesigning CAL

Current `main` already contains the required shadow apparatus:

- `AuditTrace.entailment` retains the full per-passage NLI observations.
- `v1.evidence_state` projects independent support and refutation channels.
- `v1.decision_model` retains contribution-level eligibility, semantic validity,
  aperture, and an explicit decide-or-abstain sequence.
- `v1.explicit_claims` audits caller-declared atoms independently and composes
  `single` / `all_of` parents deterministically.
- `v1.semantic_operators` demonstrates the fail-closed pattern for an operator
  whose semantics are narrower than ordinary NLI.

The released max-winner path remains the control. The contribution ledger and
explicit-claim path are the experimental alternatives.

## Hypotheses

### H1 — Premature winner selection loses decision-relevant information

If support and refutation are both valid observations, changing only which score
is numerically largest, or changing passage order under an exact tie, should not
change the epistemic state from "both positions remain".

**Prediction:** the current max-winner control can change label under these
metamorphic transformations; the relation-preserving shadow remains `mixed` and
does not select a terminal verdict.

### H2 — Eligibility and semantic validity must be applied before resolution

A higher-scoring contribution that is explicitly ineligible or semantically
invalid should not outrank a lower-scoring eligible, valid contribution.

**Prediction:** the max-winner control may select the higher raw NLI score. The
contribution ledger filters it before resolution. An `unknown`, however, must
abstain rather than be treated as invalid.

### H3 — Evidence aperture is a decision dependency

Strong local support does not prove that the relevant evidence set was
adequately assessed.

**Prediction:** `aperture=unknown` or `incomplete` blocks a terminal shadow
decision even when a valid support contribution is above threshold.

### H4 — Explicit obligations prevent semantic averaging

For an `all_of` claim, full parent support requires every required obligation to
be supported. Strong support for seven components must not convert an unresolved
or unsupported eighth/ninth dependency into overall support.

**Prediction:** all-supported obligations produce `supported`; any unresolved or
unsupported required dependency prevents full support; a contradicted required
dependency prevents a supported parent.

## Controlled variables

The experiment deliberately does **not** change:

- retrieval;
- the NLI model;
- NLI class probabilities;
- thresholds;
- the frozen production rule file;
- claim parsing;
- source authenticity/trust inference;
- production verdicts.

Constructed inputs hold the measured passage relations fixed and vary one
decision dependency at a time.

## Case matrix

| ID | Stage | Manipulation | Production/max-winner expectation | Shadow expectation |
|---|---|---|---|---|
| A01 | aggregate | swap support/refutation score winner only | winning label flips | `mixed`; abstain |
| A02 | aggregate | reverse equal-score passage order | tie winner flips | invariant `mixed`; abstain |
| A03 | eligibility | add higher-scoring ineligible refutation | raw winner adverse | eligible support decides |
| A04 | eligibility | mark competing refutation eligibility unknown | raw winner available | abstain `eligibility_unknown` |
| B01a | validity | higher refutation explicitly invalid | raw winner adverse | valid support decides |
| B01b | validity | higher refutation validity unknown | raw winner available | abstain `semantic_validity_unknown` |
| C01a | aperture | refutation aperture unknown + strong support | support locally strong | abstain `aperture_unknown` |
| C01b | aperture | support aperture incomplete + strong support | support locally strong | abstain `aperture_incomplete` |
| D01 | obligations | all required atoms supported vs one unresolved | n/a | only complete case fully supported |
| D02 | obligations | 7 supported + 1 unresolved + 1 unsupported | n/a | parent not fully supported |
| D03 | obligations | one required atom contradicted | n/a | parent contradicted |
| E01a | control | easy valid support-only case | support | support |
| E01b | control | easy valid refutation-only case | refutation | refutation |

Pytest parameterization executes 13 named cases from this matrix.

## Acceptance gates

The experiment supports **H1** only if:

1. A01 reproduces winner sensitivity on the production aggregator while the
   shadow remains mixed in both twins.
2. A02 reproduces production order sensitivity under an exact cross-label tie
   while the shadow state and decision remain invariant.
3. Easy single-channel controls E01a/E01b still resolve normally.

It supports **H2** only if explicit `ineligible` / `invalid` contributions stop
deciding while corresponding `unknown` states cause abstention rather than
silent fallback.

It supports **H3** only if incomplete/unknown aperture blocks resolution despite
above-threshold local support.

It supports **H4** only at the **declared-structure** level. Passing D01-D03 is
not evidence that CAL can infer the correct obligation tree from natural
language.

## Falsification / stop conditions

Do not promote the shadow architecture on the basis of this experiment if any of
the following occur:

- the current max-winner path is invariant on A01/A02, so the suspected
  information-loss mechanism is not reproduced;
- the relation-preserving path changes under the same harmless metamorphic
  transformations;
- filtering invalid/ineligible evidence produces a new adverse decision;
- incomplete aperture fails to block a decision;
- obligation composition still permits full support with a required unresolved
  dependency;
- easy support/refutation controls stop resolving.

Any apparatus defect discovered while running this experiment must be fixed in a
separate commit and recorded here before interpreting the result.

## What is deliberately out of scope

This experiment does not yet implement or validate:

- automatic claim normalization/decomposition;
- automatic generation of verification obligations;
- evidence-inventory trust or authenticity assessment;
- obligation-specific retrieval;
- numeric, temporal, causal, universal, or comparison operators beyond already
  committed guarded experiments;
- competing-explanation generation;
- claim repair;
- missing-evidence request ranking;
- human-gold accuracy.

Those are downstream hypotheses. If the relation/obligation abstraction survives
this first test, each can receive its own isolated branch or experiment.

## Results

**Pending independent GitHub Actions execution.**

The result section will be amended after the branch is exercised through the
repository's public PR suite (`pytest`, Ruff, format check, and mypy). A green
suite means the preregistered experimental assertions were reproduced; it does
not mean the experimental shadow is production-ready.
