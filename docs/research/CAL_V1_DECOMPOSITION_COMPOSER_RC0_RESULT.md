# CAL V1 DecompositionComposer RC0 — Terminal Result

Date: 2026-09-18

Classification: Draft Research / terminal parent-child recomposition evidence.

## Disposition

**SUPPORTED_CAL_V1_DECOMPOSITION_COMPOSER_RC0.**

The exact candidate at `7cf0d2e50562ec4ce4082d1e1c058a11025b1a48` supports bounded Contract A 2.0 parent/child recomposition for CAL V1.

## Exact lineage

- frozen two-registry terminal head: `35d7b69d2e920a24a187aad00d4877dda83c6d45`
- exact qualified two-registry code: `7f093e954c2554c3bf21c8bd72d36550414bf54b`
- DecompositionComposer preregistration: `f5bceb0ef9be328592a6c074f86fbfa70e3bcc31`
- exact qualified DecompositionComposer: `7cf0d2e50562ec4ce4082d1e1c058a11025b1a48`
- decisive run: `35367371687`

## Contract A authority

The experiment is bounded to released Contract A 2.0.0:

- immutable release identity: `contract-a-v2.0.0`;
- production promotion merge: `b59c2fbe38bae78a3a35699362c0e67d17152e4b`;
- frozen schema blob: `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`.

No decomposition operator beyond root-only and declared `all_of` is claimed.

## Decisive execution

Run `35367371687`: PASS.

Observed counts:

- DecompositionComposer falsifiers: **27 passed**;
- frozen two-registry regression: **53 passed**;
- full repository regression: **1113 passed, 5 skipped, 48 deselected**;
- static checks: PASS.

## Supported semantics

Root-only Contract A states:

- `not_decomposed`;
- `failed`;
- `unknown`;

preserve the exact root CAL outcome and emit a `single` recomposition receipt.

Declared `all_of` requires exact, complete child-result binding.

The qualified parent rule is:

1. any contradicted child -> parent `CONTRADICTED`;
2. otherwise all supported -> parent `SUPPORTED`;
3. otherwise -> parent `NOT_CHECKABLE`.

Therefore:

`ALL_OF(CONTRADICTED, NOT_CHECKABLE) -> CONTRADICTED`.

The competing unresolved-dominates-everything strategy is rejected.

## Structural firewall

The candidate refuses rather than semantically abstaining when the recomposition object is structurally invalid, including:

- missing child result;
- extra child result;
- duplicate child result;
- wrong child text binding;
- wrong root result binding;
- root result supplied to declared all_of;
- child result supplied to root-only state;
- wrong operator;
- noncontiguous declaration sequence;
- mutated child result identity;
- reused child result identity.

Each child result identity independently binds:

- proposition ID;
- proposition text hash;
- immutable audit-result hash;
- conclusion.

This prevents outcome/result swapping from being silently accepted as a different child.

## Metamorphic result

Supplied child call order is not semantic authority.

The composer reconstructs Contract A declaration order and produced an identical result/receipt when the exact same bound child outcomes were supplied in reverse call order.

Changing Contract A sequence changes receipt identity while preserving conjunction truth when the same children/outcomes remain bound.

## Receipt

Every successful recomposition emits a deterministic `DecompositionReceipt` binding:

- root identity;
- Contract A state;
- decomposition identity;
- operator;
- ordered child identities and text hashes;
- child result identities;
- child conclusions;
- parent conclusion.

Receipt mutations are detected.

## Preserved deviations

The first candidate run passed 27 decomposition tests, 53 inherited tests, and 1113 repository tests, then failed only one Ruff E501 line.

The first formatting repair accidentally wrote literal `\n` characters into the source and failed Python collection before semantic execution. That apparatus-invalid run is preserved.

The successor corrected only that transcription and passed every frozen gate.

## Architectural conclusion

CAL V1 now has three separately qualified semantic layers:

1. `SemanticFamilyRegistry` for atomic measure/warrant/direct relation;
2. `CompositionRegistry` for bounded semantic derivation from warranted atomic authority;
3. `DecompositionComposer` for exact Contract A root/child recomposition.

The next legitimate gate is cross-pipeline integration through exact Contract A child lineage, Evidence Bundler / Contract B child evidence worlds, CAL child evaluation, and parent recomposition.

## Nonclaims

This result does not establish:

- Evidence Bundler child-selection quality;
- Contract B compatibility;
- Contract C losslessness;
- Decision Engine compatibility;
- new decomposition operators;
- production merge/release authority.
