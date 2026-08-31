# RC7D-D — Deterministic Multi-Reader Semantic Operator Experiment

## Classification

Post-reveal diagnostic hardening. Not context-free. No LLM or learned model. No production authorization.

## Frozen prior evidence

- RC7D-C evidence commit: `6f0fa7dfc1b8417664a602f36b802a62428dffc1`
- RC7D-C validator/equivalence freeze: `d01a7b0da3a19010162c08544835d4aed6b11950`
- original RC7D operator candidate: `b5b04485cb1e09f025017e25cd6d008e6c5030f6`

## Question

Can multiple independently coded deterministic readers for the same semantic operator increase semantic-dimension discovery and authorized coverage while the separate authority gate keeps unsafe semantic authorization at zero?

This is the deterministic analogue of ensemble disagreement machinery. Agreement is never treated as truth. The union of proposals is a discovery mechanism only.

## Candidate architecture

For each semantic dimension, preserve proposals from:

- the original frozen reader;
- a separately coded alternate deterministic reader where RC7D-C showed meaningful coverage loss.

At minimum alternate readers for:

- quantifier;
- exception;
- probability;
- permission;
- role binding;
- subclass;
- quantitative.

Temporal may remain single-reader if no materially distinct implementation is justified.

Every reader receives the exact unedited source. Proposals are never overwritten. Each proposal records reader ID.

## Proposal union

For a dimension:

- all reader proposals are retained;
- semantically equivalent proposals may be marked `agreement` after frozen semantic normalization;
- disagreements remain explicit;
- duplicate agreement does not increase semantic authority by itself;
- every proposed atom is independently validated before authority.

## Authority validator v3

Freeze before the held-out cohort.

May extend v2 only for generic semantic constructions identified by prior evidence, including:

- additional explicit exception surfaces;
- additional epistemic-modality surfaces;
- quantitative proportion/minority forms;
- robust exclusion of modifiers from semantic slots;
- event extraction under quantified/quantitative subjects where the event relation is independently warranted.

The validator may not inspect the held-out cohort or gold.

## New held-out cohort

Construct only after multi-reader candidate + validator v3 freeze.

At least 72 cases, including:

- mixed quantifier + exception;
- mixed quantifier + probability;
- permission + exception;
- permission + temporal;
- subclass + permission;
- quantitative + event;
- role binding positive/negative/passive;
- no-authority domain-vocabulary traps;
- novel paraphrases not enumerated in either reader's patterns;
- contradictory same-dimension assertions;
- irrelevant prose.

At least 50% of mixed cases must use surface forms not present verbatim in either reader source code.

## Architectures compared

1. `single_reader_broadcast`: original one-reader-per-dimension bank + validator v3.
2. `multi_reader_broadcast`: union of original + alternate reader proposals + validator v3.
3. `agreement_only`: authorize only atoms proposed equivalently by at least two readers, after validator v3.
4. `zero_authority`: preserve all proposals, authorize none.

## Metrics

- proposal semantic-dimension recall/precision;
- authorized semantic-dimension recall/precision;
- authorized typed-atom recall/precision;
- unsafe authorized atoms/cases;
- false authorized dimensions;
- proposal disagreements per dimension;
- error rate among proposal agreements;
- error rate among disagreements;
- mixed-semantic authorized retention;
- raw-source preservation;
- operator-count and reader-count stress;
- rejected/unresolved proposals preserved;
- composition accuracy with oracle-perfect component inputs.

## Falsifiers

The multi-reader hypothesis fails if:

- multi-reader proposal recall does not exceed single-reader proposal recall by at least 0.08; or
- multi-reader authorized semantic-dimension recall does not exceed single-reader authorized recall by at least 0.08; or
- any unsafe atom/false semantic dimension becomes authorized; or
- gains depend on agreement-only gating while agreement still contains semantic errors.

## Terminal states

### `DETERMINISTIC_MULTI_READER_SUPPORTED_WITH_BOUNDS`

All:
- raw-source preservation = 1.0;
- multi-reader proposal dimension recall >= 0.82 and precision >= 0.97;
- multi-reader authorized dimension recall >= 0.68;
- authorized typed-atom precision >= 0.99;
- zero unsafe authorized atoms;
- zero false authorized dimensions;
- proposal recall gain >= 0.08 over single-reader;
- authorized recall gain >= 0.08 over single-reader;
- mixed-semantic authorized retention higher than single-reader;
- oracle composition accuracy = 1.0.

### `MULTI_READER_OVERCLAIM`
Any unsafe atom or false semantic dimension is authorized by the multi-reader lane.

### `MULTI_READER_NO_COVERAGE_GAIN`
Safety holds but preregistered recall gains over single-reader are not reached.

### `MULTI_READER_DISCOVERY_STILL_INSUFFICIENT`
Multi-reader gains over single-reader but proposal recall remains < 0.82 or authorized recall < 0.68.

### `AGREEMENT_GATE_UNSAFE`
Agreement-only lane authorizes any semantically wrong atom, demonstrating again that agreement is not a validity proof.

### `APPARATUS_INVALID`
Gold leakage, source mutation, invalid equivalence, or other apparatus defect.

Precedence:
`APPARATUS_INVALID` > `MULTI_READER_OVERCLAIM` > `AGREEMENT_GATE_UNSAFE` > `MULTI_READER_NO_COVERAGE_GAIN` > `MULTI_READER_DISCOVERY_STILL_INSUFFICIENT` > `DETERMINISTIC_MULTI_READER_SUPPORTED_WITH_BOUNDS`.

## Scope

Even success supports only bounded deterministic multi-reader discovery plus separate authority validation. It does not establish arbitrary-English coverage, independent consumability, or production readiness. A later fresh context-free reproduction remains mandatory before promotion.
