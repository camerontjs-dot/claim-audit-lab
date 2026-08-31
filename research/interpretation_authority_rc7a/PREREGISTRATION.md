# Interpretation Authority RC7A — Preregistration

## Classification

Research Infrastructure / interpretation-authority contract hardening.

Parent semantic authority: Claim Audit Lab population semantics RC5B accepted science head `c623af35bee3b5f685c9a44e6d91ced006b2d690`.

Prior motivating evidence: fresh independent text-to-typed-authority reproduction PR #52 terminated `UNSAFE_OR_SEMANTICALLY_INCORRECT`; all six wrong resolved relations were in `only_permission`, where parser failure weakened membership and/or explicit permission to semantic `unknown`. That run also produced zero unsafe authority fabrications on expected-unknown cases, demonstrating that parser abstention and semantic unknown can be operationally separated but were not represented separately inside resolved authority objects.

## Exact question

> Is an explicit field-level interpretation-authority state sufficient to prevent extraction failure or insufficient source authority from being laundered into semantic `unknown`, while still allowing source-level semantic unknown to participate in the frozen deterministic semantic consumer?

This experiment does **not** test natural-language parsing quality. It removes language parsing and tests the intermediate authority boundary directly.

## Competing explanations

1. **Distinct interpretation authority is necessary and sufficient.** Source-established semantic unknown and extraction/source-authority failure require different states; a gate over those states prevents downstream semantic laundering.
2. **The distinction is unnecessary.** Collapsing extraction/source-authority failure to semantic unknown does not change any authority-relevant result in the bounded tested domain.
3. **The proposed four-state field model is incomplete.** Even with explicit statuses, an independently coded gate disagrees with a reference oracle or cannot determine whether semantic evaluation is authorized.
4. **The failure is downstream rather than representational.** Correctly gated receipts still produce wrong frozen-consumer relations.

## Frozen semantic families

RC7A is deliberately limited to three families selected from the fresh reproduction:

- `only_permission`: actual wrong resolved semantic relations;
- `role_binding`: strong independent exact recovery;
- `quantifier`: complete independent coverage failure.

The RC5B semantic consumer remains unchanged.

## Interpretation field states

Every authority-relevant field observation has exactly one status:

- `established`: the source/interpreter establishes one supported semantic value;
- `semantic_unknown`: the source explicitly establishes that the semantic value itself is unknown; valid only for schema fields whose semantic vocabulary includes `unknown`;
- `extraction_unresolved`: the construction is within contract jurisdiction but the interpreter cannot recover a unique field value;
- `insufficient_authority`: the supplied source does not warrant assigning the field at all.

`semantic_unknown` is semantic content. `extraction_unresolved` and `insufficient_authority` are interpretation-authority failures and must never be projected into a semantic value.

Each `established` or `semantic_unknown` observation must carry a non-empty source span and warrant rule identifier. Interpretation-failure states carry no semantic value.

## Authorization rule

A typed semantic case may be passed to the frozen RC5B consumer only when every authority-relevant field required by that family/query is semantically established (`established` or valid `semantic_unknown`).

If any required field is `extraction_unresolved` or `insufficient_authority`, semantic evaluation is `NOT_AUTHORIZED`; no entailment/neutral/contradiction result is emitted.

The gate must report the blocking field(s) and interpretation-authority reason(s).

## Mechanisms under test

Two independent model-free mechanisms operate over the same receipt objects:

- **reference oracle**: declaratively validates field states and constructs a semantic case only when all required fields are semantically established;
- **direct warrant gate**: independently coded procedural implementation of the proposed contract.

Neither may call the other.

A third **legacy-collapse comparator** is intentionally unsafe apparatus: where the semantic schema admits `unknown`, it substitutes `unknown` for unresolved/insufficient fields and otherwise uses preregistered family defaults. Its purpose is to establish concrete witnesses showing whether collapsing interpretation failure into semantic values can change downstream authority.

## Falsifiers

RC7A fails `CONTRACT_SUFFICIENT` if any of the following occurs:

1. direct warrant gate disagrees with the reference oracle on authorization state, blocking reasons, or projected semantic case for any frozen case;
2. any oracle-authorized projected case disagrees with the unchanged frozen RC5B consumer's expected relation;
3. no frozen witness distinguishes source-level `semantic_unknown` from `extraction_unresolved` or `insufficient_authority` at the semantic-authorization boundary;
4. a mutation from an established value to extraction/source-authority failure leaves semantic evaluation authorized;
5. a mutation from an established value to explicit `semantic_unknown` is incorrectly treated as interpretation failure on a field whose semantic schema supports unknown.

The interpretation state taxonomy is considered over-specified for **semantic authorization** if `extraction_unresolved` and `insufficient_authority` cannot be distinguished in any downstream semantic state. They may still be retained as diagnostic provenance states, but RC7A must not claim semantic irreducibility for that distinction without a witness.

## Required adversarial coverage

- exhaustive cross-product over membership and explicit-permission interpretation states in `only_permission`;
- single-field authority-loss mutations for role subject, role object, predicate, and polarity;
- single-field authority-loss mutations for population, predicate, and quantifier;
- explicit semantic-neutral authorized cases;
- explicit source-level semantic-unknown authorized cases where the frozen schema supports `unknown`;
- matched `semantic_unknown` vs `extraction_unresolved` vs `insufficient_authority` witness triples;
- field provenance validation failures (missing span/rule, illegal semantic_unknown on fields without an unknown semantic value).

## Terminal states

### CONTRACT_SUFFICIENT

All oracle/gate cases agree; all authorized projections are valid for the frozen consumer; required witness and mutation properties pass; laundering witnesses exist for the legacy-collapse comparator.

### CONTRACT_INCOMPLETE

Preserve the smallest disagreement showing that the proposed interpretation-authority representation/gate is insufficient.

### DISTINCTION_NOT_JUSTIFIED

No frozen witness demonstrates a meaningful authority difference between semantic unknown and interpretation failure.

### APPARATUS_INVALID

The corpus, oracle, frozen-consumer binding, or evaluator is internally inconsistent before the scientific comparison can be interpreted.

## Non-authorization

RC7A does not authorize a production parser, LLM extractor, production semantic operator, NLI replacement, threshold, ensemble, Contract C change, aggregation change, downstream policy change, or promotion of any research implementation.
