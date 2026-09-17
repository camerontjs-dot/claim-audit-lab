# CAL V1 Kernel Plugin Registry RC0

Date: 2026-09-17

Status: **PREREGISTERED / NOT YET EXECUTED**

## Question

Can the frozen CAL V1 integration candidate be refactored behind an explicit semantic-family plugin/registry seam while preserving the exact currently supported semantic envelope and making missing or misrouted family machinery fail closed rather than silently falling back?

## Frozen parent

- repository: `camerontjs-dot/claim-audit-lab`
- parent records head: `d03d0e960ad82d889e6763fd4fb53cd24babd187`
- frozen implementation: `80835a57e121c66d22c68f349abf8e318de0e232`
- frozen implementation tree: `e6b218109233a2908e2cd558c714fb05cf9ac254`
- semantic implementation SHA recorded by the parent: `847cc970642bb648dc994b929c2053b5c9d4648c`

This successor is stacked on the records head so the frozen candidate and its local qualification record remain visible and unchanged.

## Intended bounded change

Introduce an explicit immutable registry of semantic-family plugins used by the CAL audit engine.

Each plugin owns the existing callable seams for:

1. measurement;
2. semantic authority / warrant;
3. proposition-relative relation derivation.

The default registry must contain exactly the two already-supported deciding families:

- `strict_comparison`;
- `direct_event_order`.

No new semantic family, parser, entailer, threshold, retrieval behavior, Contract B behavior, Contract C behavior, Decision behavior, or verdict rule is introduced in RC0.

## Invariants

1. Existing public one-argument `audit(context)` behavior remains available.
2. Existing measurement, authority, relation, and composition implementations remain the semantic machinery; RC0 only changes how the engine selects them.
3. Unsupported families remain `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY`.
4. A missing plugin must not fall through to another family.
5. A plugin whose measurement emits a different semantic family must fail explicitly.
6. Existing proposition/evidence-world binding, authority-integrity, unresolved-precedence, mixed-relation, and unsupported-family behavior must remain unchanged.
7. Retrieval remains outside CAL.
8. Contract C remains a separate downstream materialization boundary.

## Falsifiers

RC0 is falsified if any of the following are observed:

- any existing focused CAL V1 semantic/integrity regression changes unexpectedly;
- full repository tests expose a semantic regression attributable to the registry change;
- a missing family plugin produces a deciding result;
- a misrouted plugin can emit a foreign-family measurement without explicit refusal;
- the default registry supports any family beyond the two frozen deciding families;
- an unsupported family reaches the historical retrieve/entail/rules path or another family plugin;
- the change requires modifying measurement semantics, authority semantics, relation tables, or composition rules to become green.

## Acceptance evidence

Required before any supported disposition:

- focused plugin-registry tests;
- existing production semantic and authority-integrity tests;
- full `pytest` suite;
- `ruff check src tests`;
- `ruff format --check src`;
- `mypy`;
- exact branch/head identity recorded in the PR;
- failures and deviations preserved.

A green workflow alone is not a research disposition.

## Weak controls

The test surface must include at least:

- an empty registry presented with a normally supported proposition family; it must not borrow another family implementation;
- a deliberately miswired strict-comparison plugin whose measurement function is the direct-event-order instrument; the invariant mismatch must be rejected before semantic authority or relation derivation.

## Stop rule

Stop RC0 when:

- all acceptance evidence is observed; or
- any falsifier is observed; or
- making the branch green would require semantic widening or changing the frozen parent behavior.

Do not repair a decisive semantic failure by adding new family rules, new measurement patterns, NLI, claim parsing, or new verdict logic inside this PR.

## Nonclaims

Even if supported, RC0 will not establish:

- generic plugin safety for arbitrary third-party code;
- automatic claim typing;
- NLI/LLM participation;
- broader semantic-family coverage;
- population/membership or permission/exception correctness;
- advanced causal-basis composition;
- production promotion, merge, release, or authorization.

## Successor if supported

Use the proven registry seam as the chassis for a separately bounded successor that introduces the Claim Compiler and/or one new researched semantic family. Do not combine those scientific questions into this RC0.
