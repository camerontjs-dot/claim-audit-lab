# CAL Semantic Family Roadmap RC0

Date: 2026-09-17

Classification: Draft Research Analysis / architecture planning. This record is stacked on terminal M4 result commit `607ec560fd53bd56279193a8d39a48b6f80e1012`. It does not add a semantic family, change production behavior, authorize merge/release, or grant any secondary measurement instrument semantic authority.

## Decision question

What semantic proposition families are likely to be useful for CAL, which semantic phenomena should instead be reusable warrant/jurisdiction modifiers or composition operators, and in what order should the candidate families be pressure-tested?

The purpose is to avoid two symmetric architecture failures:

1. one generic language-understanding family that hides materially different inference rules; and
2. one plugin per linguistic construction, which duplicates scope/negation/temporal/quantifier machinery and makes cross-family behavior incoherent.

## Live starting point

On exact qualified M4 implementation `a18e07ef17e02d83930bea5344624cd9368ae2fc`, the `SemanticFamily` enum contains:

- `strict_comparison`;
- `direct_event_order`;
- `permission_exception`;
- `assertion_scope`;
- `unsupported`.

Only `strict_comparison` and `direct_event_order` are registered as deciding plugins. M4 permits additional instruments to run in shadow while preserving causal isolation from warrant/relation/composition/verdict.

Historical convergence and research evidence constrain interpretation of the other enum values:

- CAL #101 recorded strict comparison and direct event ordering as deciding, permission/exception as diagnostic/deferred, and assertion/scope as falsified do-not-use in the V1 convergence candidate.
- CAL #72 summarized comparison, direct event-event ordering, and permission+exception/temporal composition as bounded measurement candidates, while assertion/scope warrant remained unsafe/incomplete.
- CAL #71 demonstrated a bounded permission-composition measurement candidate with 50/50 supported cases recovered and zero false proposals on 14 negative/unsupported controls.
- CAL #47–#51 established substantial typed entity/population/membership machinery, including membership, subclass direction, quantifier, role binding, `only` semantics, temporal membership, interpretation unknowns, and text-to-typed extraction research.
- CAL #65/#68 showed scope/assertion measurement can be useful while authority eligibility remains unsafe under tested architectures.
- CAL #63 showed heterogeneous instruments add observations but agreement is not truth and scope/embedding noise is a major authorization hazard.

## Family criterion

A semantic phenomenon should become a proposition family only when pressure testing shows it needs a materially distinct combination of:

- typed proposition fields;
- measurement/source-completion machinery;
- warrant conditions;
- proposition-relative relation algebra.

A phenomenon should instead be a **cross-cutting modifier** when it mainly changes whether/where another family proposition is asserted, applicable, or interpretable.

A phenomenon should instead be a **composition concern** when it combines already-warranted propositions/relations rather than defining a new atomic proposition type.

This criterion is itself falsifiable. If a proposed modifier requires a distinct relation algebra, promote it to a family candidate in a successor decision. If two proposed families can share the same typed contract and relation algebra without information loss, collapse them rather than preserving taxonomy for taxonomy's sake.

# A. Proposition-family roadmap

## F0 — `strict_comparison`

Status: **SUPPORTED WITH BOUNDS / currently qualified deciding family**.

Core form: proposition-relative ordered comparison between two entities or entity-bound quantities.

Examples:

- Alpha > Beta;
- Alpha has a higher rate than Beta;
- Alpha exceeded Beta.

Keep current qualified behavior frozen while new families are tested. Future quantitative work may reveal a common lower-level quantity representation, but it must not silently widen this family.

Priority: baseline regression family.

## F1 — `direct_event_order`

Status: **SUPPORTED WITH BOUNDS / currently qualified deciding family**.

Core form: one directly expressed event occurs before/after another directly expressed event, under the narrow independently reconstructable grammar already qualified.

Examples:

- A reviewed X before B signed Y;
- A did not review X after B signed Y.

Keep current family narrow. Event existence/polarity and richer temporal interval semantics should be tested separately rather than smuggled into event order.

Priority: baseline regression family.

## F2 — `deontic_norm`

Status: **EVIDENCE-BACKED CANDIDATE**.

Proposed core: what a source normatively states about an actor/population and action, without converting that statement into operational authorization.

Candidate atomic norm kinds:

- `PERMITTED`;
- `PROHIBITED`;
- `OBLIGATORY`;
- `PERMISSION_RESTRICTED_TO` / necessary permission condition.

Examples:

- Technicians may release the batch;
- Technicians must not release the batch;
- Technicians must release the batch;
- Only qualified reviewers may approve the record.

Exception, condition, temporal applicability, attribution, and modality should begin as modifiers attached to the norm rather than being baked into the family name.

Current enum consequence: `permission_exception` is best treated as a legacy/deferred token until this candidate is tested. Do not rename it in RC0.

Priority: **P1, first new-family pressure test** because prior RC7F-D evidence is strongest.

## F3 — `population_membership`

Status: **EVIDENCE-BACKED CANDIDATE**.

Proposed core: entity/class membership and set/subclass relations with explicitly typed quantifier/direction state.

Candidate forms:

- entity is/is not a member of class;
- class A is a subclass/subset of class B;
- population-level quantified membership/restriction;
- role membership where role is treated as a class;
- necessary-condition `only` constructions when they are genuinely membership constraints.

Examples:

- Alice is a licensed reviewer;
- Contractors are not employees;
- Sterile technicians are trained personnel;
- Only members of Group A satisfy eligibility condition E.

Prior RC5B evidence makes subclass direction and invalid converses explicit. Temporal membership should begin as a temporal modifier over membership rather than a separate family.

Priority: **P1**.

## F4 — `scalar_value`

Status: **HYPOTHESIS / high-value candidate**.

Proposed core: one entity/metric has an exact or bounded value with typed unit/scale, without requiring a second compared entity.

Examples:

- Batch yield was 92.4%;
- The count was 17;
- Temperature was 5 °C;
- Version is 3.2 when version is explicitly modeled as an ordered/scalar value rather than an opaque label.

Pressure tests must separate numeric equality from tolerance/range claims, unit conversion, approximate language, and quoted/attributed values. A later `quantitative_change` feature should first be tested as composition over scalar values + temporal qualification before becoming its own family.

Priority: **P1** because many factual claims are absolute quantities and current strict comparison does not cover them.

## F5 — `event_occurrence`

Status: **HYPOTHESIS / high-value candidate**.

Proposed core: a typed event did or did not occur, independent of ordering against another event.

Examples:

- QA approved the batch;
- QA did not approve the batch;
- The system recorded the event.

This family would provide a clean home for event polarity currently embedded inside direct-event-order event sides. Attribution/speech acts can be represented as event predicates when the proposition itself is “X stated/reported Y,” while the truth of nested Y remains governed by assertion scope.

Priority: **P1** because event order already depends on event structure and pipeline claims frequently concern whether an action occurred.

## F6 — `attribute_state`

Status: **HYPOTHESIS**.

Proposed core: an entity has a typed categorical state/value that is not naturally numeric or population membership.

Examples:

- Batch status is released;
- Device mode is standby;
- Document version status is superseded;
- Supplier status is approved.

This must not become an unrestricted subject-predicate-object escape hatch. Qualification should require a closed/declared attribute domain and exact proposition binding. If the pressure test shows the same algebra as a more general typed relation family, this candidate may collapse into that family.

Priority: **P2**.

## F7 — `typed_binary_relation`

Status: **HYPOTHESIS / intentionally constrained**.

Proposed core: a declared binary relation between two entities where the relation contract explicitly declares directional properties such as inverse, symmetry, or lack of transitivity.

Examples:

- A owns B;
- A is the parent organization of B;
- A is assigned to B;
- A is the manufacturer of B.

Do not introduce an open-ended free-text predicate family. Each admitted predicate must have a typed relation contract; unsupported predicates fail closed. Identity/equivalence may eventually be a specially qualified symmetric predicate within this family rather than a new family.

Priority: **P2**.

## F8 — `spatial_relation`

Status: **HYPOTHESIS / collapse candidate**.

Proposed core: topological/directional spatial relations such as `IN`, `CONTAINS`, `NORTH_OF`, `ADJACENT_TO`.

Examples:

- Facility A is in Ontario;
- Room B is inside Zone C;
- Site A is north of Site B.

The first pressure test should ask whether this needs distinct spatial algebra or can safely be a closed-predicate subset of `typed_binary_relation`. Do not create a separate plugin merely because the vocabulary is geographic.

Priority: **P2/P3**.

## F9 — `causal_relation`

Status: **HYPOTHESIS / high semantic risk**.

Proposed core: real-world causal or contributory claims, distinct from CAL's own causal-basis/provenance accounting.

Examples:

- A caused B;
- A contributed to B;
- A prevented B;
- Removing A reduced B.

Important distinction: existing Contract-C/CAL causal-basis work explains which evidence/relations caused a CAL result. It is **not evidence that CAL can audit real-world causal propositions**.

Causal claims require unusually strong source semantics and should not be inferred from correlation, temporal order, co-occurrence, or model confidence.

Priority: **P3, last among current core candidates**.

## F10 — `quantitative_change` (provisional composition candidate)

Status: **HYPOTHESIS / do not make a family yet**.

Examples:

- Yield increased from 80% to 90%;
- Error rate fell by 3 percentage points;
- Count doubled.

Default hypothesis: represent as scalar state(s) + temporal anchoring + a qualified derivation rule. Promote to a distinct family only if that representation cannot preserve required semantics or produces unsafe cross-state inference.

Priority: after `scalar_value`.

# B. Cross-cutting warrant/jurisdiction modifiers

These are **not deciding semantic families by default**. They alter eligibility, applicability, or interpretation of a family atom.

## M1 — assertion scope and attribution

Status: **EVIDENCE-BACKED REQUIRED MODIFIER; tested architectures unsafe for promotion**.

Distinguish narrator assertion from quoted, attributed, parenthetical evidential, reported, conditional, or otherwise embedded material. CAL #65/#68 show this layer can reduce false permits dramatically while still missing the zero-false-permit requirement.

The current `assertion_scope` enum member should therefore not automatically receive a deciding plugin. Its eventual representation may be a warrant modifier/receipt rather than a family.

## M2 — polarity / negation

Required across event, membership, state, relation, causal, and deontic families. Negation must bind to the correct predicate/argument scope; string-level “not” detection is insufficient as a universal rule.

## M3 — epistemic modality

Examples: may, might, likely, allegedly, reportedly, supposedly. Modality changes assertion strength/eligibility and must not be collapsed into factual or deontic `may`.

## M4 — condition and exception

Examples: if, unless, except, excluding, save for. Existing exception research and RC7F-D show these modifiers can materially change deontic/population meaning. They should attach to the proposition/norm they qualify rather than define a universal `exception` family.

## M5 — temporal applicability / interval

Examples: before/after/until/as-of/effective-from/effective-through. This is distinct from the atomic `direct_event_order` family when it qualifies whether another proposition is applicable at a time.

## M6 — quantifier and cardinality scope

Examples: all, some, no, only, at least N, exactly N. Population work shows quantifier semantics can be authority-relevant. Quantifiers should be explicit typed fields/modifiers rather than silently inferred by generic NLI.

## M7 — entity/coreference/role binding

Exact subject/object/population identity and role binding are authority prerequisites. Ambiguous aliases/coreference should remain unresolved unless independently qualified.

## M8 — quantity/unit normalization

Unit, scale, percent vs percentage-point, magnitude and conversion state should be typed and inspectable. Normalization can serve `scalar_value`, `strict_comparison`, and `quantitative_change` without becoming a family itself.

## M9 — interpretation-authority state

Preserve distinctions such as `established`, source-level `semantic_unknown`, `extraction_unresolved`, and `insufficient_authority`. CAL #53 demonstrated why collapsing interpretation failure into semantic unknown can manufacture decisive-looking output.

# C. Composition concerns, not atomic families

## C1 — evidence conflict / mixed categorical relations

Already handled scorelessly in the qualified kernel. New families must prove that conflicting warranted support/refutation does not produce arbitrary winner selection.

## C2 — root claim composition (`all_of`, `any_of`, etc.)

Current V1 preserves `NOT_COMPOSED` for root/all-of. Child-to-root semantics require a separate experiment and should not be embedded inside a family plugin.

## C3 — cross-passage conjunction/disjunction

Some claims may require multiple passages jointly. This is a composition/aperture problem unless a family-specific test proves otherwise.

## C4 — cross-family composition

Examples: membership + deontic rule; scalar value + temporal applicability; event occurrence + event order. Do not invent cross-family inference until each atomic component is warranted and the composition rule is separately tested.

## C5 — transitivity / derived inference

Comparison transitivity, temporal transitivity, subclass inheritance, spatial containment, and causal chaining are not universally interchangeable. Each must be explicitly authorized by the relevant family contract and pressure-tested rather than supplied by a generic graph engine.

## C6 — CAL causal basis / evidence multiplicity

Keep result-causality (`single necessary`, independent alternatives, joint sufficiency, residual/non-deciding) separate from real-world causal claims in F9.

# D. Standard family qualification gauntlet

Each candidate family should advance through the same broad gates, with family-specific details frozen before execution.

## Gate 0 — typed semantic contract sufficiency

Before natural-language parsing, test the proposed typed proposition/source contract against an independent oracle or formal semantics where feasible.

Require:

- exact positive, negative, neutral/unresolved distinctions;
- invalid converse controls;
- field ablations proving material fields are necessary;
- metamorphic pairs that change only one semantic dimension;
- a plausible weak consumer that should fail for the intended semantic reason.

If the typed contract is insufficient, do not proceed to text extraction.

## Gate 1 — bounded measurement

Freeze held-out semantics before rendering text. Test one or more proposal/measurement instruments. Preserve misses and unknowns; do not make confidence or agreement authority.

## Gate 2 — independent source completion / warrant

The authority path must independently reconstruct or validate the material semantic fields from admitted source evidence rather than trusting the measurement proposal. Exact context, evidence aperture, passage, source and instrument identities remain mandatory.

## Gate 3 — proposition-relative relation

Test support/refute/irrelevant/unresolved under claim reversal, entity substitution, field mutation, polarity inversion, and same-evidence opposite-proposition controls.

## Gate 4 — cross-cutting modifier attacks

At minimum mutate:

- attribution/assertion scope;
- negation;
- epistemic modality;
- conditions/exceptions;
- temporal applicability;
- quantifier scope;
- entity/coreference binding;
- units where relevant.

A family is not qualified merely because its direct canonical sentence parses correctly.

## Gate 5 — cross-family collision controls

Near-neighbor text from every other qualified/candidate family must fail closed or route explicitly. Examples: epistemic `may` must not become deontic permission; temporal applicability must not become event ordering; membership `only` must not automatically become permission restriction.

## Gate 6 — multi-evidence composition

Exercise support-only, refute-only, irrelevant, unresolved, support+refute, support+unresolved, duplicates and evidence-order permutations. Preserve coexisting legitimate bases rather than selecting an arbitrary winner.

## Gate 7 — M4 shadow-instrument invariance

Once a primary instrument exists, add independent shadow measurements. Add/remove/reorder/fail/tamper shadows and prove primary warrant/relation/verdict state is unchanged until a later experiment explicitly qualifies secondary participation.

## Gate 8 — claim compiler

Only after typed semantics are stable, test text-to-typed-proposition proposal with at least two independent proposal paths, ambiguity, partial recovery, disagreement and out-of-jurisdiction controls. The compiler remains proposal-only.

## Gate 9 — full pipeline conformance

Re-run exact Contract B intake, CAL native result, Contract C materialization, Decision Engine consumption and provenance reconstruction. A new family is not production-ready merely because its local plugin tests pass.

## Gate 10 — independent reproduction for consequential promotion

Use a fresh/context-free or otherwise genuinely independent implementation when the promotion claim requires independence. Do not call a second implementation independent if it can see the first implementation/gold/result.

# E. Adversarial corpus dimensions shared by all families

Every family-specific pressure corpus should include, where meaningful:

- canonical positive and refuting cases;
- inverse/reversal pairs;
- entity substitution;
- predicate/action/attribute substitution;
- same words under different scope;
- quoted/attributed/evidential wrappers;
- modal hedges;
- negation attachment changes;
- condition/exception attachment changes;
- temporal changes;
- quantifier changes;
- unknown/ambiguous cases;
- cross-family lexical traps;
- irrelevant passages containing family vocabulary;
- duplicate evidence;
- conflicting evidence;
- order permutations;
- stale receipt/context/aperture/identity mutations;
- an intentionally weak plausible strategy.

No family may lower the zero-unsafe-result requirement by averaging good direct cases with unsafe scope cases.

# F. Proposed execution order

1. **Deontic norm contract pressure test** — determine whether permission/prohibition/obligation/restricted-to can share one typed family while exceptions/conditions/time remain modifiers.
2. **Population/membership requalification against current M4 kernel** — reuse prior formal contract as evidence, but fresh qualification must test the new plugin/warrant/relation boundary.
3. **Scalar value** — establish exact value/unit/range semantics before attempting quantitative change.
4. **Event occurrence** — extract the event atom/polarity problem from event-order machinery.
5. **Assertion/scope modifier successor** — structural wrapper recognition, tested across multiple families rather than as a standalone deciding family.
6. **Attribute state**.
7. **Typed binary relation**, with spatial relation as a collapse-vs-separate discriminator.
8. **Quantitative change** as composition-first experiment.
9. **Causal relation** only after scope, occurrence, temporal, and typed relation machinery are mature enough to prevent temporal/correlational shortcuts.
10. **Root/cross-family composition** as a separate programme rather than a new atomic family.

Parallel work is acceptable only where it does not contaminate held-out/evaluator independence. Promotion remains sequential and family-specific.

# G. Immediate next experiment

Start with a fresh **Deontic Norm Family Contract RC0**.

The first question is intentionally below natural-language implementation:

> Can one typed deontic contract represent `PERMITTED`, `PROHIBITED`, `OBLIGATORY`, and `PERMISSION_RESTRICTED_TO` propositions plus explicit modifier bindings without unsafe cross-mode implication, and can an independent direct consumer match a frozen formal oracle under field ablations and metamorphic mutations?

Load-bearing assumption: one deontic family is more coherent than separate permission/prohibition/obligation plugins.

Primary falsifier: a single typed contract cannot preserve the required distinctions without either (a) unsafe implication such as treating obligation as permission, (b) collapsing restriction-to into direct permission, or (c) making exception/temporal attachment family-specific in a way that prevents reuse.

Only if Gate 0 survives should a successor wire deontic measurement/warrant/relation into the current plugin kernel.

# Non-claims

This roadmap does not establish that all listed candidates deserve implementation, that the list is complete forever, that generic natural-language inference is safe, that prior research automatically qualifies a family on the current kernel, or that a future family may bypass Contract B admission, M3 authority guards, M4 shadow isolation, scoreless composition, or downstream conformance.

The list is deliberately revisable by evidence. A pressure test may collapse, split, rename, or falsify a candidate family.