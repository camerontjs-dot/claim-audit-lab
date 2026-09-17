# CAL V1 Claim Compiler RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / interpretation-boundary discrimination.

This experiment is stacked on the terminal M1 kernel result at `929be5baf400ec71f9209e59fbbfa87893a6dcff`. It is not independent evidence from that lineage and it does not authorize production promotion.

## Question

Can CAL recover the exact current typed proposition target from the exact Contract B claim text for the **two already-qualified semantic families only** (`strict_comparison` and `direct_event_order`) while failing closed on disagreement, partial recovery, ambiguity, and unsupported language, and without allowing claim interpretation to become verdict authority?

## Frozen parent

- parent branch: `research/cal-v1-kernel-plugin-registry-20260917`
- parent result head: `929be5baf400ec71f9209e59fbbfa87893a6dcff`
- parent M1 disposition: bounded `SUPPORTED FOR PROMOTION` for the semantic-family registry seam only
- current canonical manual input boundary: strict typed target JSON consumed by `production_v1.bundle_input`

Manual typed target input remains the authority-preserving fallback throughout RC0.

## Prior evidence being reused as design evidence, not promotion authority

RC6 text-to-typed-authority extraction established, in a controlled synthetic setting, that:

- extraction unknown must remain distinct from semantic neutral;
- separate extraction implementations can disagree in ways strongly enriched for failure;
- exact agreement can function as a conservative risk gate;
- unresolved extraction must not be laundered into downstream semantic judgment;
- the old RC6 corpus and extractors were not independently authored and therefore did not establish general natural-language parsing.

RC0 does not import RC6's population/membership ontology into CAL V1. It only reuses those boundary lessons.

## Bounded implementation hypothesis

Introduce a proposal-only claim compiler that receives the **exact Contract B claim identity and text** and produces a content-bound compiler receipt.

The compiler may return one of four states:

- `ESTABLISHED`: two distinct deterministic proposal paths recover the same supported semantic family and byte-equivalent normalized proposition fields;
- `AMBIGUOUS`: proposal paths produce incompatible supported candidates, including cross-family disagreement;
- `EXTRACTION_UNRESOLVED`: at least one supported-family path sees relevant structure but exact typed recovery is incomplete or the two paths do not both establish the same candidate;
- `OUT_OF_JURISDICTION`: neither supported-family path recognizes the claim as belonging to the current two-family language.

Only `ESTABLISHED` may include a proposed `TypedProposition` / canonical target object. The compiler itself must never emit a CAL conclusion, categorical relation, Decision result, or semantic authority receipt.

## Candidate parser architecture

Use two deliberately different deterministic proposal paths for each currently supported family:

1. a bounded regex/template parser;
2. a token/clause parser that independently reconstructs the same typed fields.

They are separate code paths, but they are not claimed to be independent scientific consumers because they are authored in the same experiment.

### Strict comparison target schema

An established proposal must recover exactly:

- `lhs_entity`
- `rhs_entity`
- `comparison_direction`

where direction is one of the values already accepted by the relation layer (`MORE_THAN` / `GREATER_THAN` / `LESS_THAN` / `FEWER_THAN`, with the compiler preferring canonical `MORE_THAN` or `LESS_THAN`).

### Direct event-order target schema

An established proposal must recover exactly:

- `left_subject`
- `left_predicate`
- `left_object`
- `left_polarity`
- `temporal_relation`
- `right_subject`
- `right_predicate`
- `right_object`
- `right_polarity`

with temporal relation limited to `BEFORE` / `AFTER` and polarity limited to `positive` / `negative`.

Negative event polarity may be typed, but existing relation semantics remain unchanged and therefore still resolve negative-event cases as `UNRESOLVED` downstream.

## Identity and authority boundaries

For any `ESTABLISHED` output:

- `proposition_id` must equal the exact Contract B `claim_id`;
- `text_sha256` must be the SHA-256 of the exact Contract B `claim_text`;
- the generated target must be accepted unchanged by the existing strict target loader;
- changing claim text, claim identity, family, or fields must change the compiler receipt identity;
- caller-supplied proposition hashes are not accepted as compiler authority.

The compiler is interpretation proposal machinery only. Existing target validation, semantic measurement, source completion, authority validation, relation derivation, composition, Contract C, and Decision remain separate stages.

## Frozen evaluation plan

Before observing implementation results, freeze a small controlled corpus containing:

- positive strict-comparison claims covering direct `more/fewer/less/higher/lower` and `exceeded/trailed` forms;
- positive direct-event-order claims covering `before` / `after` and supported event verbs;
- polarity controls for direct event order;
- unsupported ordinary assertions that must remain out of jurisdiction;
- malformed / incomplete comparison and temporal claims that must remain extraction unresolved;
- ambiguity controls designed so two supported candidates or conflicting parses cannot be silently selected;
- mutation/metamorphic pairs for harmless whitespace/punctuation normalization, entity reversal, relation reversal, and event-order reversal.

Expected outputs are frozen before the implementation result is observed.

## Success conditions

RC0 is supported only if all of the following hold on one exact successor head:

1. every frozen `ESTABLISHED` case produces the exact preregistered family and normalized field map;
2. every frozen non-established case remains in its preregistered explicit non-established state;
3. no non-established case produces a typed target;
4. every established target passes the existing production target loader and exact Contract B identity/hash binding;
5. established target compilation is deterministic and content-addressed;
6. parser disagreement is surfaced rather than majority-voted or confidence-resolved;
7. no compiler code emits or computes a CAL verdict, categorical relation, Contract C result, Decision result, or semantic authority;
8. existing M1 semantic tests and full repository tests remain green under a qualification environment with full Git history;
9. Ruff and mypy remain green.

## Falsifiers / stop rules

Preserve a negative result if any of these occur:

- a frozen ambiguous, unresolved, or out-of-jurisdiction case receives an established typed target;
- one proposal path can unilaterally establish a target after the other disagrees or fails;
- a generated target bypasses current claim-id / text-hash binding;
- success requires changing existing measurement, authority, relation, composition, Contract B, Contract C, or Decision semantics;
- success requires broadening beyond the two currently supported families;
- compiler output itself is used as semantic authority or verdict evidence;
- expected corpus labels are changed after observing parser behavior to recover a pass.

If the bounded grammar proves too brittle, record that result rather than widening the grammar opportunistically in the same RC.

## Alternative explanations to pressure-test

- apparent success may reflect template regularity rather than useful claim interpretation;
- two code paths authored together may share the same blind spots and create false agreement;
- exact agreement may trade away too much coverage to be operationally useful;
- the current two-family target schemas may themselves be too narrow to represent ordinary claims even when language parsing succeeds;
- requiring exact Contract B claim text may make the compiler safe but too tightly coupled for later interactive use.

## Non-goals

RC0 does not test or authorize:

- generic natural-language claim understanding;
- automatic claim decomposition;
- population/membership semantics;
- permission/exception semantics;
- assertion/scope semantics;
- NLI or LLM proposal instruments;
- retrieval changes;
- evidence selection changes;
- new CAL verdicts;
- score-based terminal logic;
- automatic pipeline execution from raw prose.

## Promotion boundary

A supported RC0 would justify only this architectural step:

> CAL may expose a bounded, proposal-only compiler for its two existing semantic families, with explicit failure states and manual typed input preserved as fallback.

Any `run-claim` orchestration, broader language support, learned instrument, or new semantic family requires a separate successor decision.
