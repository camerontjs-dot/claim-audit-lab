# CAL Population Family Discriminator RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / family-boundary discrimination. Independent branch from terminal M4 result `607ec560fd53bd56279193a8d39a48b6f80e1012`. It does not depend on the Deontic Norm RC0 candidate branch and does not mutate production `src/`.

## Question

The historical RC5B population/membership contract was sufficient on its bounded 460-case domain, but it deliberately carried more than atomic population semantics: membership, directed subclasshood, predicate rules, modality, quantifiers, `only` permission constructions, group/member scope, ordered event roles, temporal membership, and polarity.

The current architectural question is therefore not “does RC5B work?” It is:

> Can CAL isolate **entity membership + directed subclasshood** as one coherent atomic `population_membership` family, while treating behavior predicates, deontic `only`, group/event scope, role binding, quantifier application to non-membership predicates, and temporal applicability as modifiers or cross-family composition rather than cloning the old umbrella schema into one plugin?

## Frozen historical evidence

Design evidence only, not current-kernel promotion authority:

- RC5B accepted science head: `c623af35bee3b5f685c9a44e6d91ced006b2d690`;
- accepted run: `33325279730`;
- corrected 460-case corpus SHA256: `92721e5144aa582ff00c10c4fc3666d43c05c5cd77e4a7669d10545c23395308`;
- result: 0/460 oracle-consumer disagreements, 13/13 ablation witnesses, 8/8 metamorphic pairs, 4/4 subclass-direction sentinels;
- accepted RC5B direct consumer blob: `988c2bd6c2e7079639a1f5759e02ed5d14fbcfb6`;
- RC6 later showed exact typed-authority recovery can fail even when the final relation is correct, so this discriminator must test typed-state identity rather than only terminal relation.

## Atomic family hypothesis

Proposed atomic state:

- entity identity;
- population/class identity;
- membership status: `MEMBER`, `NON_MEMBER`, `UNKNOWN`;
- zero or more directed subset edges `A ⊆ B`;
- optional temporal applicability binding, treated as a modifier rather than part of the membership relation algebra.

Proposed atomic query forms:

- `x ∈ A`;
- `x ∉ A`;
- `A ⊆ B` / exact directed class relation when directly asserted.

The core relation algebra must preserve:

- direct membership and non-membership;
- positive inheritance upward: `x ∈ A` and `A ⊆ B` supports `x ∈ B`;
- negative inheritance downward: `x ∉ B` and `A ⊆ B` refutes `x ∈ A`;
- invalid positive converse is not licensed: `x ∈ B` does not establish `x ∈ A`;
- invalid negative converse is not licensed: `x ∉ A` does not establish `x ∉ B`;
- unknown remains unresolved;
- edge direction matters.

## Explicit out-of-family sentinels

The following historical RC5B dimensions are **not atomic population facts by default** in RC0:

1. `only members of A may P` → deontic restricted-to proposition, potentially composed later with population membership;
2. `every member of A performs P` → quantified predicate/event/state claim, not membership merely because a population is named;
3. group-vs-member event scope → event/assertion scope concern;
4. ordered semantic roles in an event → event or typed-relation binding concern;
5. factual behavior conditioned on membership → cross-family composition;
6. temporal membership windows → population atom plus temporal applicability modifier, not a new membership relation kind.

A candidate that absorbs these into free-form population rules merely to reproduce the historical umbrella schema fails the architectural discriminator.

## Frozen weak strategies to kill

At minimum:

- **positive-converse**: `x ∈ B` + `A ⊆ B` ⇒ `x ∈ A`;
- **negative-converse**: `x ∉ A` + `A ⊆ B` ⇒ `x ∉ B`;
- **symmetric-subclass**: treat `A ⊆ B` as equivalent to `B ⊆ A`;
- **unknown-as-negative**: treat `UNKNOWN` membership as non-membership;
- **only-as-membership**: infer `x ∈ A` merely from `only A may P` without an independently established permission fact;
- **population-keyword-router**: route any proposition mentioning a population into the population family.

## Success condition

RC0 supports the narrower family boundary only if a frozen finite-set oracle and an independent direct consumer agree on all core cases and metamorphic mutations, all weak strategies are discriminated for their intended semantic error, and explicit cross-family sentinels remain outside atomic population jurisdiction.

A pass means only that `population_membership` should be narrower than historical RC5B's umbrella authority surface. It does not discard RC5B evidence; it relocates some of RC5B's validated distinctions into reusable modifier/composition layers.

## Falsifiers

Preserve a negative result if:

- membership and subclasshood cannot share one coherent typed relation algebra;
- valid negative subclass inheritance requires unsafe converse rules;
- temporal binding cannot be factored from the core atom without losing semantics;
- `only` permission or quantified behavior must be embedded in the family for atomic membership to work;
- exact typed-state fidelity is lost even when terminal relation remains correct.

## Non-claims

No natural-language extraction, current-kernel plugin, warrant implementation, production enum change, quantifier engine, temporal reasoner, deontic composition, Contract C/Decision behavior, merge, or release is authorized.