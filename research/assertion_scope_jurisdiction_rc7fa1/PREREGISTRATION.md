# RC7F-A1 Stacked Scope / Semantic Warrant Hardening — Preregistration

Status: **FROZEN BEFORE SUCCESSOR CANDIDATE AND BEFORE HELD-OUT COHORT**

## Exact parent evidence

- repository: `camerontjs-dot/claim-audit-lab`
- RC7F-A terminal evidence: `120268d34247f8dd448ba3af22420d3ecbe7c8de`
- RC7F-A apparatus freeze: `9532da3eafff25102d59f880215e5ad1ab02cf9a`
- RC7F-A held-out freeze: `54f16a68eb1f3effe819b82483aa8f69ba7083b7`
- accepted scientific run: `33452771124`
- parent terminal token: `MORE_SCOPE_RESEARCH_JUSTIFIED`

The parent is immutable evidence. RC7F-A1 does not repair it or reinterpret its terminal result.

## Observed parent failures

RC7F-A reduced the allow-all baseline from 68 false permits to 2 while preserving direct positive/negative assertion recall at 1.0. The two unsafe permits were punctuation-bearing evidential adverbs:

- `Supposedly, ...`
- `Purportedly, ...`

The parent rule required a literal trailing space after those markers.

The parent also produced two fail-closed nested cases with the wrong single subtype, indicating that one flat `scope_status` may discard relevant enclosing scope structure even when final authority eligibility remains safe.

## Question

Can the smallest bounded non-LLM successor:

1. eliminate punctuation-boundary evidential leakage; and
2. represent all detected enclosing scope as an ordered `scope_path`,

while preserving direct assertion recall and achieving **zero unsafe false permits** on a fresh semantics-first held-out cohort?

## Design principle

This experiment obeys the CAL design rule:

> CAL may know that it observed something without claiming that it knows the thing is true. When warrant is incomplete, abstention is a successful outcome.

The already-measured local event is an observation. `authority_eligible` is a separate semantic-warrant judgment.

## Candidate boundary

The candidate may change only research apparatus under `research/assertion_scope_jurisdiction_rc7fa1/` plus its dedicated workflow.

Production `src/` must remain unchanged relative to parent evidence.

Allowed successor changes:

- replace literal-space evidential markers with token-boundary + punctuation-tolerant matching for a preregistered bounded family;
- collect nested enclosing scope into an ordered outer-to-inner `scope_path` rather than returning on first matched non-assertive scope;
- derive `authority_eligible` fail-closed: only an empty/non-restrictive scope path plus supported positive/negative assertion polarity is eligible;
- preserve explicit `UNRESOLVED` for ambiguous or unsupported framing.

The candidate must not discover semantic events. It receives the event observation and exact source anchor as input.

No generative LLM, LLM judge, or model-generated gold is allowed.

## Preregistered evidential family

Punctuation-tolerant unresolved markers:

- `supposedly`
- `purportedly`
- `reportedly`
- `allegedly`

They qualify only as standalone evidential adverbs at a lexical boundary. Domain nouns or longer words containing these strings must not trigger.

## Scope-path vocabulary

The candidate may emit ordered entries drawn from:

- `UNRESOLVED_EVIDENTIAL`
- `ATTRIBUTED`
- `CONDITIONAL_ANTECEDENT`
- `CONDITIONAL_CONSEQUENT`
- `DEONTIC`
- `EPISTEMIC`
- `QUANTIFIED`

The path records detected enclosing scope. It is not itself a truth claim.

A legacy summary `scope_status` may be emitted for diagnostics, but authority eligibility must be computed from the scope path and polarity, not from a single classifier short-circuit.

## Pre-held-out qualification

Before candidate freeze, qualification must cover:

- direct positive and negative assertions remain eligible;
- `Supposedly,`, `Supposedly:`, `Purportedly,`, `Reportedly,`, `Allegedly,` fail closed;
- ordinary words/domain labels containing marker substrings do not trigger;
- quoted and reporting-verb attribution;
- conditional antecedent and consequent;
- nested conditional + attribution;
- nested attribution + epistemic;
- nested conditional + epistemic;
- deontic and quantified scope;
- invalid anchors fail closed;
- candidate has no case-id input.

Implementation defects found during qualification may be repaired before apparatus freeze and must be preserved in the apparatus history.

## Held-out construction

Held-out cases may exist only after apparatus/evaluator freeze.

Gold is semantics-first and mechanically generated from formal wrappers; candidate output must not create or revise gold.

Required held-out families:

1. direct asserted positive/negative;
2. evidential adverbs with comma, colon, semicolon, dash, and parenthetical punctuation;
3. evidential lexical/domain traps;
4. attribution via quotes and reporting complements;
5. conditionals, both anchored positions;
6. epistemic scope;
7. deontic scope;
8. quantifier scope;
9. nested two-layer scope combinations;
10. nested three-layer scope combinations;
11. deliberately unsupported/ambiguous framing;
12. meaning-preserving punctuation transformations;
13. meaning-changing direct-vs-scoped pairs.

Identical normalized source text may not have incompatible gold scope-path or eligibility.

## Metrics

Primary:

- unsafe false permits;
- direct assertion recall;
- authority-eligibility precision;
- exact scope-path accuracy;
- scope membership precision/recall;
- unresolved rate.

Metamorphic:

- punctuation-preserving scope stability;
- meaning-changing direct-vs-scoped pair accuracy.

Safety is primary. A safe unresolved/miss is preferable to false authority.

## Success criterion

`SCOPE_WARRANT_CANDIDATE_READY_FOR_HARDENING` requires all of:

- unsafe false permits = `0`;
- direct asserted positive/negative recall = `1.0`;
- authority-eligibility precision = `1.0`;
- exact scope-path accuracy >= `0.95`;
- punctuation-preserving scope stability = `1.0` on resolved supported cases;
- meaning-changing pair accuracy = `1.0`;
- no evaluator/cohort invariant failure;
- no candidate change after held-out exposure.

`MORE_SCOPE_RESEARCH_JUSTIFIED` applies when the candidate remains fail-closed but has bounded scope-path or recall residue.

`SCOPE_ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE` applies on unsafe false permits, invalid apparatus, or a failure that prevents a trustworthy scientific result.

## Nonclaims

This experiment does not establish source reliability, universal truth, operational permission, production Contract E semantics, production CAL behavior, or a universal scope ontology.

## Next gate

If successful, treat stacked scope as a candidate semantic-warrant input and test it later in the broader capability envelope. Do not equate semantic warrant with operational authorization.
