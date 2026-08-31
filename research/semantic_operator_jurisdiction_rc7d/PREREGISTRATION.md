# RC7D Semantic Operator Jurisdiction and Composition — Preregistration

## Classification

Research Infrastructure / post-reveal diagnostic hardening.

This is **not** a context-free reproduction. Prior RC7B/RC7C evidence is an authorized input because this experiment tests architectural alternatives suggested by those observed failures.

No production authorization. Draft Research PR only.

## Prior immutable evidence inputs

- RC7B aperture head: `80c2d2f8c96025ea62e8552ecfd4621cd81ea1f4`
- RC7B A immutable implementation: `4513528130ed051b9bcc0b1b0832494baf1c2e04`
- RC7B B immutable implementation: `074363bf243717a502cb2e3269309cc94ddf5106`
- RC7C terminal evidence commit: `5b279e17afafa2a2bb68b02dd5e5c0a129570cb2`
- RC7C accepted run: `33414949503`

## Hypothesis under test

A CAL semantic layer that preserves the original source, runs multiple bounded semantic specialists, records explicit jurisdiction claims and residues, and separately governs overlap/conflict/composition can retain more correct semantic information than single-family routing **without increasing unsafe semantic authority**, provided each specialist is conservative about claiming jurisdiction.

The experiment must not assume this is true.

## Core preservation invariant

The exact input source string is immutable throughout the experiment.

Every architecture and every specialist receives the same original source string. No stage may rewrite, truncate, normalize in place, or replace the source. Derived spans/normalizations are additive records only.

Every final case record must preserve:

- `raw_source` exactly;
- SHA-256 of `raw_source`;
- every specialist receipt;
- every claimed semantic atom;
- every unclaimed/unresolved semantic atom known to the gold apparatus;
- every overlap/conflict/composition decision;
- all residues and failures.

## No LLM lane

No LLM, generative model, semantic scout, embedding router, or learned classifier is allowed in RC7D. This experiment tests whether bounded deterministic/symbolic machinery is sufficient before introducing probabilistic language interpretation.

## Specialist bank

The frozen candidate bank will contain conservative bounded specialists for:

1. `quantifier`
2. `exception`
3. `temporal`
4. `subclass`
5. `permission`
6. `role_binding`
7. `probability`
8. `quantitative`

Each specialist returns one of:

- `CLAIMED`
- `NOT_APPLICABLE`
- `UNRESOLVED`

A `CLAIMED` receipt must include:

- operator ID/version;
- exact source spans;
- typed semantic atoms;
- warrant/construction identifier;
- declared composition requirements, if any.

A specialist may not derive final entailment/neutral/contradiction.

## Architectures compared

### A. `single_router`

A deterministic front-door router selects exactly one primary specialist from the source. Only that specialist contributes semantic authority.

This is the strongest version of the architecture RC7C's jurisdiction-gate result calls into question.

### B. `broadcast_all`

Every specialist receives the original source and returns a receipt. All `CLAIMED` receipts are preserved. A composition governor determines whether claims are:

- compatible and composable;
- overlapping but redundant;
- conflicting;
- unresolved due to missing composition authority.

No claim is discarded merely because another operator also claims jurisdiction.

### C. `conservative_router_fallback`

A conservative candidate router nominates zero or more specialists. Nominated specialists run first. If any known semantic dimension remains unaccounted for in the evaluation apparatus, the architecture falls back to broadcast-all.

This is an experimental efficiency architecture, not an authoritative production design.

## Gold semantic dimensions

Each held-out case will define zero or more typed semantic dimensions from this bounded set:

- `quantifier`
- `exception`
- `temporal`
- `subclass`
- `permission`
- `role_binding`
- `probability`
- `quantitative`

Gold may contain multiple dimensions for one source.

Gold records typed atoms and composition relationships separately. The evaluator must not collapse multi-semantic cases into a single family label.

## Held-out case families

The held-out cohort will include at minimum:

- quantifier + exception;
- membership/permission + temporal;
- permission + exception;
- role binding + explicit negation;
- quantifier + probability;
- subclass + permission;
- quantitative + role/event content;
- supported semantic content plus irrelevant prose;
- ambiguous or genuinely underdetermined constructions;
- unseen paraphrases for each specialist;
- single-dimension controls;
- no-target-semantic controls.

## Composition rules under test

The candidate composition governor may only authorize compositions explicitly declared before held-out corpus construction.

At minimum test:

- quantifier + exception;
- event/role binding + negation/polarity;
- permission + temporal qualifier;
- permission + exception;
- quantifier + probability as **non-collapsible** competing layers unless an explicit probabilistic-quantifier composition is declared;
- subclass + permission as separate authority layers unless subclass inheritance is explicitly licensed.

Invalid composition is a safety failure even when component specialist claims are individually correct.

## Metrics

For each architecture:

### Information retention

- semantic-dimension recall;
- typed-atom recall;
- exact raw-source preservation;
- residue recall: proportion of gold dimensions not claimed that remain explicitly represented as unresolved/unaccounted rather than silently lost.

### Safety

- false jurisdiction claims;
- unsafe semantic atoms;
- invalid compositions;
- unsupported inheritance/generalization;
- semantic dimensions silently dropped;
- conflicts incorrectly resolved as agreement.

### Governance quality

- overlap detection recall;
- conflict detection recall;
- valid composition precision/recall;
- unresolved composition preservation;
- disagreement preservation.

### Efficiency

- specialists invoked per case;
- fraction of fallback cases for architecture C.

Efficiency is secondary to information retention and safety.

## Multiple-testing / operator-count stress test

Broadcast creates a special failure risk: the probability that at least one operator falsely claims jurisdiction can increase with operator count.

RC7D will therefore run the same cases with operator-bank prefixes of size:

- 2
- 4
- 6
- 8

The ordering is frozen before evaluation.

Primary stress metrics:

- false-claim probability per case as bank size increases;
- unsafe-atom probability per case;
- any-false-claim rate;
- any-unsafe-authority rate.

### Falsifier

If `broadcast_all` gains semantic recall primarily by increasing false jurisdiction/unsafe authority with operator count, the broad-broadcast hypothesis is falsified even if aggregate information recall improves.

## Negative controls

The evaluator will include deliberately weak alternatives:

1. `greedy_claim`: every specialist claims whenever it sees a domain keyword.
2. `router_only`: exactly one specialist, no residue.
3. `union_without_composition_governor`: preserves all specialist claims but blindly unions semantic atoms.

These controls test whether the evaluator can distinguish mere information accumulation from safe governed interpretation.

## Preregistered terminal scientific states

### `OPERATOR_BANK_SUPPORTED_WITH_BOUNDS`

All of the following:

- `broadcast_all` semantic-dimension recall >= 0.95;
- typed-atom recall >= 0.90;
- false jurisdiction claim rate <= 0.02;
- unsafe semantic atom rate = 0;
- invalid composition rate = 0;
- residue recall >= 0.95;
- overlap/conflict detection recall >= 0.90;
- no monotonic material increase in unsafe-authority rate across bank sizes 2→8;
- `broadcast_all` strictly improves retained gold dimensions over `single_router` on mixed-semantic cases;
- negative controls materially worse on safety or composition.

### `ROUTED_FALLBACK_SUPPORTED_WITH_BOUNDS`

Broadcast fails its own bounded criteria, but conservative routing + fallback satisfies the safety criteria and retains >= 0.95 of gold dimensions with fewer specialist invocations than broadcast.

### `MULTIPLE_TESTING_OVERCLAIM`

False jurisdiction/unsafe authority materially increases with operator count and the 8-operator bank exceeds the preregistered safety bounds.

### `COMPOSITION_GOVERNANCE_INSUFFICIENT`

Component claims are mostly recoverable, but invalid/unsupported composition exceeds zero or conflict/overlap handling fails materially.

### `SPECIALIST_COVERAGE_INSUFFICIENT`

Safety remains bounded but semantic-dimension recall < 0.95 because deterministic specialists cannot recover enough held-out paraphrase/construction variation.

### `HYPOTHESIS_FALSIFIED`

Single-router is at least as safe and retains at least as much correct semantic information as the governed operator-bank approaches, or operator-bank gains depend on unsafe overclaim.

### `APPARATUS_INVALID`

Evaluator/corpus/implementation defect prevents the preregistered comparison.

If multiple failure conditions apply, use the most causally specific state in this order:

`APPARATUS_INVALID` > `MULTIPLE_TESTING_OVERCLAIM` > `COMPOSITION_GOVERNANCE_INSUFFICIENT` > `SPECIALIST_COVERAGE_INSUFFICIENT` > `HYPOTHESIS_FALSIFIED`.

## Interpretation limits

This experiment can support only a bounded architecture claim over its deterministic specialist set and held-out corpus.

It cannot establish:

- arbitrary-English semantic decomposition;
- production readiness;
- independent recoverability by a fresh implementation;
- that an LLM is necessary or unnecessary in general;
- downstream policy authorization;
- Contract C promotion.

A later context-free reproduction is required before any claim of independent consumability.
