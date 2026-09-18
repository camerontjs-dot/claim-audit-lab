# CAL V1 DecompositionComposer RC0 — Preregistration

Date: 2026-09-18

Classification: Draft Research / parent-child recomposition experiment.

## Exact CAL base

This experiment starts from the terminal two-registry CAL V1 research head:

- CAL PR #176 terminal record head: `35d7b69d2e920a24a187aad00d4877dda83c6d45`;
- exact qualified two-registry code candidate: `7f093e954c2554c3bf21c8bd72d36550414bf54b`;
- decisive qualification run: `35365267744`;
- disposition: `SUPPORTED_CAL_V1_TWO_REGISTRY_RC0`.

The existing atomic semantic path and CompositionRegistry are held fixed.

## Contract A authority

The parent/child semantics under test come from canonical released Contract A 2.0.0:

- immutable release identity: `contract-a-v2.0.0`;
- production promotion merge: `b59c2fbe38bae78a3a35699362c0e67d17152e4b`;
- frozen RC2 research head: `2e50567c4da2a4046a15bddfc3feee31296da3fb`;
- schema blob: `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`;
- wire-spec blob: `2e7c37fca9aa6bdd1090fb527a663bdbe606ebcb`.

Contract A 2.0.0 authorizes exactly:

- one authoritative root proposition;
- explicit decomposition state;
- for `declared`, exact `operator = all_of`;
- at least two exact ordered child proposition identities/text hashes;
- no OR, threshold, majority, weighted, or arbitrary Boolean operator vocabulary.

Contract A records a decomposition declaration. It does not certify that the decomposition is semantically correct.

## Research question

Can CAL deterministically recompose exact Contract A 2.0.0 root/child structure after child audits, without inventing missing child state, silently dropping unresolved children, or allowing child order/identity substitution?

## Frozen architecture

`DecompositionComposer` is separate from both:

- `SemanticFamilyRegistry`, which owns atomic semantic authority;
- `CompositionRegistry`, which owns bounded semantic derivation from warranted atomic authorities.

`DecompositionComposer` consumes already-produced proposition-level CAL child outcomes plus exact Contract A decomposition authority.

It does not inspect passages, measurements, atomic authority payloads, or composition-module internals.

## Supported decomposition modes

### Root-only states

For Contract A states:

- `not_decomposed`;
- `failed`;
- `unknown`;

the authoritative root remains the audit target.

RC0 treats each as a root-only `single` recomposition shape and preserves the exact Contract A decomposition state in the recomposition receipt.

No children may be supplied in a root-only shape.

The parent outcome is exactly the root CAL outcome.

### Declared `all_of`

For a valid Contract A declared `all_of` decomposition:

- every declared child must have exactly one bound CAL child result;
- no undeclared child result may be supplied;
- child identity and sequence must exactly match Contract A;
- each child-result binding must carry an immutable result digest;
- reordering supplied child-result records must not change semantics because Contract A sequence is authoritative.

The bounded truth-functional parent rule is preregistered as:

1. if any declared child is `CONTRADICTED`, parent is `CONTRADICTED`;
2. else if every declared child is `SUPPORTED`, parent is `SUPPORTED`;
3. otherwise parent is `NOT_CHECKABLE`.

This intentionally resolves the discriminator:

`ALL_OF(CONTRADICTED, NOT_CHECKABLE) -> CONTRADICTED`

because a conjunction is false once one required conjunct is established false; uncertainty about another conjunct cannot restore the conjunction.

The competing weak strategy `unresolved_dominates_everything` is frozen as a falsifier.

## Failure versus epistemic outcome

Structural/binding defects are not semantic `NOT_CHECKABLE` results.

The composer must refuse malformed or incomplete recomposition input for:

- missing declared child result;
- duplicate child result;
- extra undeclared child result;
- child proposition-ID mismatch;
- child text-hash mismatch;
- duplicate or noncontiguous declaration sequence;
- wrong operator;
- root result supplied for declared `all_of`;
- children supplied for root-only state;
- missing/blank immutable result identity;
- repeated result identity bound to different children.

Only a structurally complete, exactly bound decomposition may produce a parent semantic outcome.

## Provenance receipt

Every successful recomposition emits a deterministic `DecompositionReceipt` binding at minimum:

- exact root proposition ID and text hash;
- exact Contract A decomposition state;
- exact decomposition ID when declared;
- exact operator;
- exact ordered child proposition IDs and text hashes;
- exact immutable child CAL result identities;
- exact child conclusions;
- exact parent conclusion;
- deterministic receipt ID over the complete canonical material.

The receipt may contain no raw evidence passages and no semantic-family private state.

## Frozen positive matrix

Root-only:

- not_decomposed + supported root -> supported;
- failed + contradicted root -> contradicted;
- unknown + not-checkable root -> not-checkable.

Declared all_of:

- supported + supported -> supported;
- supported + contradicted -> contradicted;
- contradicted + not-checkable -> contradicted;
- supported + not-checkable -> not-checkable;
- not-checkable + not-checkable -> not-checkable;
- three-child all-supported -> supported;
- three-child with one contradiction -> contradicted;
- three-child with no contradiction and one unresolved -> not-checkable.

## Metamorphic and mutation controls

The evaluator must establish:

- child-call-order invariance;
- declared-sequence mutation changes receipt identity but not result only when the same exact child bindings remain associated with their declared child identities;
- child conclusion mutation changes parent semantics where logically relevant;
- child result-ID mutation changes receipt identity;
- root identity mutation changes receipt identity/refuses wrong binding;
- decomposition-ID mutation changes receipt identity;
- operator mutation refuses;
- dropping one child refuses;
- adding one child refuses;
- duplicate child refuses;
- swapping child proposition identities while retaining outcomes refuses;
- receipt mutation is detectable.

## Weak strategies that must be caught

At least:

1. `first_child_wins`;
2. `majority_vote`;
3. `unresolved_dominates_everything`;
4. `ignore_missing_child`;
5. `ignore_extra_child`;
6. `identity_blind`;
7. `input_order_is_declaration_order`;
8. `drop_result_identity`.

## Stopping rule

If the exact candidate:

- preserves the frozen #176 two-registry subject;
- passes all structural, semantic, metamorphic, and provenance controls;
- survives repository regression and static checks;

freeze that exact DecompositionComposer for the next gate:

`Contract A -> EB child selection -> Contract B -> CAL child semantics/composition -> parent recomposition`.

Do not test Contract C inside this experiment.

No merge, production promotion, release, or downstream Contract mutation is authorized.
