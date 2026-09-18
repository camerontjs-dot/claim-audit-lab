# CAL V1 Two-Registry Architecture RC0 — Preregistration

Date: 2026-09-18

Classification: Draft Research / architecture freeze before implementation.

## Exact base

This successor starts from terminal M4 research state:

- M4 result head: `607ec560fd53bd56279193a8d39a48b6f80e1012`;
- exact qualified M4 implementation: `a18e07ef17e02d83930bea5344624cd9368ae2fc`;
- M4 qualification run: `35269683436`.

Inherited supported seams on this lineage include:

- semantic-family registry: CAL PR #116;
- claim compiler: CAL PR #117;
- immutable multi-instrument measurement ledger: CAL PR #119;
- shadow-observation runtime isolation: CAL PR #120.

## New evidence authorizing this architecture experiment

Composition campaign:

- terminal composition synthesis: CAL PR #174;
- common composition carrier: CAL PR #173;
- portable vectors: CAL PR #175;
- independent cross-repository consumer: Apparatus Contracts PR #104;
- independent consumer decisive run: `35363345978`.

## Architecture question

Can CAL add a separate immutable composition-module registry beside the existing semantic-family registry while preserving the existing atomic verdict path exactly, and then integrate one bounded composition module without allowing measurement, shadow observations, raw passage text, or family-routing machinery to bypass semantic authority?

## Frozen architecture

### Registry 1 — SemanticFamilyRegistry

This registry remains responsible for atomic proposition semantics.

Each selected family plugin owns only:

1. measurement;
2. source completion / warrant;
3. proposition-relative direct relation.

Selection is driven by the typed proposition's semantic family.

No family voting, winner selection, fallback borrowing, or multi-family competition is authorized.

### Registry 2 — CompositionRegistry

This registry is separate from `SemanticFamilyRegistry`.

A composition module may consume only:

- exact warranted authority identities and typed authority payload needed by the module;
- exact module-specific integration/modifier state;
- exact composition query.

A composition module must not consume:

- raw evidence passages directly;
- unverified measurement proposals;
- shadow-only measurements;
- caller order as semantic authority unless explicitly bound as qualified state;
- unrelated semantic-family plugin internals.

A composition module emits:

1. a categorical composition relation;
2. one provenance-bearing composition receipt compatible with the bounded common carrier qualified in CAL #173/#175.

### Authority firewall

The two registries have different authority roles:

`SemanticFamilyRegistry`
produces warranted atomic authority and direct atomic relations.

`CompositionRegistry`
derives bounded relations only from already-warranted authorities plus explicit qualified integration state.

A composition receipt is not itself permission to create new atomic authority.

## First integrated module

The first and only module authorized for RC0 candidate implementation is:

`quantitative_change_exact_v1`

Evidence basis: CAL PR #166.

Bounded supported behavior:

- exactly two independently warranted exact scalar-point authorities;
- same entity / metric / unit identity;
- separately established distinct temporal bindings;
- temporal rank determines old/new state, never input call order;
- exact `INCREASED`, `DECREASED`, `UNCHANGED`, and absolute `DELTA`;
- approximate values, ranges, percentage change, rates, unit conversion, uncertainty, and text-derived temporal inference remain out of jurisdiction.

## Candidate implementation constraints

Before implementation, freeze the following:

1. existing atomic `audit()` outputs must be byte-equivalent on inherited qualified fixtures;
2. no default composition module may run for an atomic proposition;
3. composition dispatch requires an explicit module identity;
4. unknown module identity fails closed;
5. duplicate module registration is rejected;
6. foreign or unwarranted authority inputs are rejected before module semantics;
7. composition input order must not substitute for temporal authority;
8. shadow ledger receipts cannot be promoted to composition inputs without a separately warranted authority;
9. every successful or unresolved composition result carries a verifiable common receipt;
10. no Contract C, Decision Engine, Gate, Evidence Bundler, or production-default behavior changes in this experiment.

## Frozen falsifiers

The implementation must be pressure-tested against at least:

- atomic-path equivalence;
- empty composition registry;
- unknown module;
- duplicate module registration;
- wrong authority family;
- unwarranted authority;
- stale/rebound authority context;
- same scalar authorities presented in reversed call order with unchanged temporal ranks;
- temporal-rank reversal;
- entity mismatch;
- metric mismatch;
- unit mismatch;
- approximate/ranged scalar input;
- modifier-state deletion;
- authority-ID deletion;
- query mutation;
- module-ID mutation;
- receipt-ID mutation;
- shadow-receipt substitution.

## Stopping rule

If the two-registry candidate preserves the inherited atomic path and the quantitative module passes the frozen falsifiers with no production widening, freeze that exact candidate for the next experiment: parent/child decomposition recomposition.

Do not add a second composition module inside this RC0 candidate merely because other research modules already exist.

No merge, release, Contract C change, or production promotion is authorized by this preregistration.
