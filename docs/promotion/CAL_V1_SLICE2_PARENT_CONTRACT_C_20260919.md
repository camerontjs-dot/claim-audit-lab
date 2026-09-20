# CAL V1 Slice 2 — Parent Recomposition → Frozen Contract C Qualification

## Classification

Stacked Production / Promotion candidate on exact Slice 1 commit
`61cab64149cb6119e4dbe1fe18496f3ccf89002f`.

This candidate is for controlled local-pipeline use only unless later promotion
evidence supports a stronger state. It does not authorize merge, release, tag,
Contract C SemVer assignment, Decision Engine mutation, Authorization, or execution.

## Objective

Determine whether the exact qualified CAL V1 parent path can be exposed in a
production-shaped runtime without changing frozen CAL semantic behavior:

```text
Contract B 1.2
  → trusted/prevalidated CAL child targets
  → native CAL child results
  → frozen DecompositionComposer
  → parent conclusion/receipt
  → exact frozen parent-bound Contract C candidate
```

## Exact authorities

CAL:
- Slice 1 base: `61cab64149cb6119e4dbe1fe18496f3ccf89002f`
- frozen prototype: `e24e405f5336ee024674f39dba97255bb58a2dd9`
- semantic source: `7cf0d2e50562ec4ce4082d1e1c058a11025b1a48`
- semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`
- DecompositionComposer blob: `268d0dc4dd22ddde3848141d62b7d719e48d374d`

Contract C:
- frozen candidate commit: `c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec`
- candidate blob: `df6b6ed410f52cafaeadfe1578d770f480a34b09`
- profile: `contract-c-cal-v1-parent-recomposition-rc0`
- RC2 authority: `b42c827acb0a9fe65353354d709add0e27bab307`
- RC2 validator blob: `1d2ecd228cde807138013c33c8675c3003421d3c`
- current-CAL resolver: `1d33e0612befcf8016816197c90c062373796df9`

## Hard boundary

Allowed:
- byte-identical promotion of the already-qualified DecompositionComposer;
- orchestration that runs exact child targets through existing Slice 1;
- exact binding of native child result bytes into the frozen composer;
- invocation of the exact externally pinned Contract C authority;
- packaging/CLI plumbing and fail-closed authority checks.

Prohibited:
- any active semantic-family change;
- retriever change;
- target compiler/target-authoring promotion;
- new decomposition operator or widened composition behavior;
- reinterpretation of CAL conclusions;
- private state hidden inside Contract C;
- Contract C schema/validator/semantic modification;
- Decision policy change;
- Contract D change.

The child target files remain trusted/prevalidated inputs. This work does not
resolve PR #182's target-authoring/conformance gap.

## Acceptance evidence

The exact candidate must show all of the following:

1. promoted DecompositionComposer blob equals the qualified frozen blob;
2. frozen PIPE01–PIPE04 producer cases emit byte-identical Contract C objects
   through the production-shaped projection;
3. parent outcomes remain:
   - PIPE01: supported
   - PIPE02: contradicted
   - PIPE03: not_checkable
   - PIPE04: contradicted;
4. child omission rejects;
5. supplied child-result order is invariant while declared sequence mutation rejects;
6. stale decomposition receipt rejects against fixed authority;
7. native child-result substitution rejects;
8. exact Contract-B world substitution rejects;
9. whole-object replay/coherent reseal rejects against fixed external authority;
10. deterministic replay is byte-identical;
11. exact external authority substitution fails closed;
12. a clean-installed wheel exposes and successfully executes
    `claim-audit-v1-parent` against the exact frozen authority checkouts;
13. ordinary repository regression remains green.

## Falsifiers / stop rule

Stop and preserve the counterexample if satisfying the path requires:
- changing the frozen composer or active CAL semantic implementation;
- widening the public terminal grammar beyond the frozen Contract C candidate;
- weakening Contract-B/Contract-A/native-child identity checks;
- changing the frozen Contract C candidate or RC2 authority;
- inventing a target-authoring rule;
- introducing a new semantic default.

Harness/environment defects may be repaired only if the scientific subject,
expected behavior, mutations, and exact external authorities remain unchanged.
The first failed run remains preserved.

## Allowed terminal states

- `QUALIFIED_FOR_CONTROLLED_LOCAL_PIPELINE_PARENT_BOUND_RUNS`
- `FALSIFIED_PRODUCTION_PARENT_PATH`
- `INCONCLUSIVE_QUALIFICATION`
- `BLOCKED_AUTHORITY_OR_ENVIRONMENT`
