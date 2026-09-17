# CAL V1 Shadow Observation Runtime RC0 — Result

Date: 2026-09-17

Primary disposition: **SUPPORTED FOR PROMOTION**

Classification: bounded runtime-measurement-isolation result only. This record does not authorize merge, release, production promotion, secondary-instrument semantic authority, voting, consensus, confidence thresholds, instrument ranking/selection, NLI/LLM authority, new semantic families, Contract C/Decision changes, or automatic action.

## Question

Can CAL execute additional shadow measurement instruments at the live per-passage measurement seam, before warrant and relation, while preserving the existing qualified primary semantic path as the sole cause of warrant, relation, composition, deciding evidence, and terminal verdict?

Preregistration: `docs/research/CAL_V1_SHADOW_OBSERVATION_RUNTIME_RC0.md`

## Exact lineage

- repository: `camerontjs-dot/claim-audit-lab`
- parent M3 terminal result head: `5b16313855b83940f8b09ffaed4baccc15f4a51f`
- parent M3 qualified implementation: `0e573d9f1426b5db1e01beb979e246f4cdd626b2`
- preregistration commit: `72a8492b0cf9f6451304ec00c28908f23b33d8a2`
- frozen nine-test M4 falsifier suite: `e961f1fb3eaaca71d7a5266ddb377700e2d90951`
- dedicated full-history workflow: `58b298181eee5bcb236d54e377019936cc912903`
- initial runtime implementation: `77c417909630857bfb5543a909781f8a7d729d27`
- explicit first M4 engine successor freeze: `c6a60cdf16ece1bfb293bfe51473c5f8aff3141e`
- lint-only engine cleanup: `14891cf2c07cf1a7396c5803f57c62c0adeae7d1`
- test-format-only cleanup: `d32edf778fc4146fe0b3a70aa870a59e76996d76`
- exact qualified implementation head: `a18e07ef17e02d83930bea5344624cd9368ae2fc`
- exact qualified implementation tree: `eeaea3de77698cbc0cc53d94024eef49a7e870d0`
- exact lint-clean M4 engine blob: `4111545663f97b4be53cc7523071bbed394d6769`
- preserved M3 engine predecessor blob: `67a519958bcf06b289b8a13cb0246d22ccf53c5c`
- preserved M3 authority successor blob: `09761aab9e04deca724fd213a9295fc93cc3be52`
- preserved M3 measurement-ledger blob: `5e01c0a3246a90fcc42219da78b7d8a1ed5d5f74`
- Draft PR: #120

## Frozen architecture hypothesis

M4 introduces an observed runtime path around the existing semantic engine. For each admitted passage the execution order is:

```text
qualified primary plugin measurement
        ↓
observation controller
  ├─ append primary receipt to immutable M3 ledger
  └─ execute zero or more shadows and append only valid receipts
        ↓
existing primary status handling
        ↓
existing primary warrant(primary receipt only)
        ↓
existing primary relation(primary authority only)
        ↓
existing scoreless composition / verdict
```

The ordinary `audit()` compatibility path remains available and runs with no observer.

The new `audit_observed()` path returns:

- the ordinary `AuditResult`;
- the immutable `MeasurementLedger` containing accepted primary and shadow receipts;
- deterministic `ShadowObservationFailure` records for rejected or raising shadows.

A shadow receipt is never passed to `plugin.warrant()` or `plugin.relate()` by this runtime path.

## Frozen falsifiers

The nine-test M4 cohort was frozen before runtime implementation at `e961f1fb3eaaca71d7a5266ddb377700e2d90951`.

It tests:

1. no-shadow observed execution is exactly equivalent to ordinary `audit()`;
2. a valid foreign-family shadow receipt can be collected while the primary result and authority path remain unchanged;
3. reversing two shadow instruments cannot change the primary result or canonical ledger identity;
4. a tampered shadow receipt is rejected/quarantined without changing the primary result;
5. a shadow function that raises is quarantined without changing the primary result;
6. a same-family but unqualified shadow instrument cannot replace the receipt used for primary warrant/relation;
7. shadow `CLAIMED`, `UNRESOLVED`, and `NOT_APPLICABLE` statuses cannot change the primary verdict;
8. no shadow receipt identity appears in primary authority objects;
9. repeated observed execution is deterministic.

The test context includes strict-comparison, event-order, and unrelated admitted passages so the experiment exercises same-family, foreign-family, and residual evidence behavior under one evidence aperture.

## Preserved negative and intermediate evidence

### Pre-implementation capability absence

Dedicated run `35268756204` executed the frozen M4 tests against the preregistered parent before runtime implementation.

It failed during M4 test collection with an `ImportError` for the preregistered `ShadowMeasurementInstrument` API. This is classified as **BLOCKED/CAPABILITY ABSENT**, not a semantic failure. The run establishes that the tested runtime surface did not exist on the frozen parent.

### First implementation and semantic-identity sentinel

Run `35268907106` on initial implementation `77c417909630857bfb5543a909781f8a7d729d27` passed the complete M4 isolation cohort **9/9**.

The run then failed the inherited semantic-blob identity sentinel because M4 intentionally changed `engine.py` from the M3 engine blob `67a519958bcf06b289b8a13cb0246d22ccf53c5c` to the first M4 successor blob `968113227eef841b7fa706eae961eaabab6acb61`.

This was treated as a promotion-boundary signal, not bypassed. Commit `c6a60cdf16ece1bfb293bfe51473c5f8aff3141e` established an explicit M4 engine successor identity while preserving the M3 engine SHA as predecessor provenance and retaining the exact M3 identities for authority, measurement ledger, measurements, models, plugins, relations, and authority validation.

### First full successor qualification

Run `35269056413` on the explicit successor passed:

- frozen M4 isolation tests: **9 passed**;
- inherited M1/M2/M3 semantic, Contract B, compiler, and authority gates: **65 passed**;
- full repository pytest: **1058 passed, 5 skipped, 48 deselected**.

It failed only Ruff lint on three hygiene findings:

- one unused `MeasurementLedgerRefusal` import in `engine.py`;
- two overlong assertions in the frozen M4 test module.

Ruff format and mypy were skipped after lint failure. No semantic or behavioral test failed.

### Lint-only successor

Commit `14891cf2c07cf1a7396c5803f57c62c0adeae7d1` removed only the unused import. Commit `d32edf778fc4146fe0b3a70aa870a59e76996d76` wrapped only the two long assertions. Commit `a18e07ef17e02d83930bea5344624cd9368ae2fc` advanced the explicit engine content pin to lint-clean blob `4111545663f97b4be53cc7523071bbed394d6769`.

No semantic logic, verdict fixture, authority rule, relation rule, composition rule, Contract B/C behavior, or shadow-isolation expectation changed in this correction.

## Final qualification result

Dedicated full-history push workflow:

- run `35269683436` — `Research - CAL V1 shadow observation runtime RC0` — **success**.

Observed on exact qualified implementation head `a18e07ef17e02d83930bea5344624cd9368ae2fc`, tree `eeaea3de77698cbc0cc53d94024eef49a7e870d0`:

- frozen M4 shadow-isolation falsifiers: **9 passed**;
- inherited M1/M2/M3 semantic, Contract B, compiler, target-binding, ledger, and authority gates: **65 passed**;
- full repository pytest: **1058 passed, 5 skipped, 48 deselected**;
- Ruff lint: **pass**;
- Ruff format: **pass** (`68 files already formatted`);
- mypy: **pass** (`no issues found in 67 source files`).

The qualification workflow used `fetch-depth: 0` and verified the exact M3 terminal parent, M4 preregistration, and frozen M4 falsifier commit before running the gates.

## Observed evidence

Within the frozen tested scope:

- `audit_observed(context)` with no shadows produced an `AuditResult` exactly equal to ordinary `audit(context)`;
- foreign-family shadow measurements were admitted to the observation ledger without replacing or modifying the primary authority input;
- same-family but unqualified shadow receipts remained observation-only and never became the authority receipt referenced by the primary trace;
- reversing shadow execution order preserved both primary result and canonical ledger identity;
- stale/tampered shadow receipts were rejected and localized as shadow failures;
- raising shadow functions were quarantined and did not prevent the primary result from being produced;
- shadow measurement statuses could not alter conclusion, failure code, deciding passage IDs, or non-deciding passage IDs;
- repeated observed runs were deterministic;
- existing repository behavior and inherited qualification gates remained green on the exact final head.

## Inference

The evidence supports the bounded causal claim that CAL can execute additional measurement functions at the live measurement seam and preserve their observations/failures without allowing those observations to enter the existing qualified warrant/relation/composition/verdict dataflow under the tested controls.

The strongest evidence is not merely that the final verdict stayed equal. The tests also inspect receipt identity participation and show that the primary `AuthorityReceipt` continues to reference the primary measurement receipt rather than any shadow receipt. Order, failure, invalid-identity, foreign-family, same-family-unqualified, and status mutations were varied while the primary semantic output remained invariant.

This is evidence of **dataflow authority isolation**, not a proof that arbitrary same-process code is incapable of side effects outside CAL's immutable semantic objects.

## Alternative explanations considered

### Shadows could be harmless only because the test instruments are simple

Plausible. RC0 uses deterministic in-repository measurement functions and synthetic invalid/raising functions. It does not qualify NLI, LLM, remote, stateful, or adversarial code as a safe in-process shadow.

### Equality could hide covert authority through a redundant shadow

The frozen tests reduce this possibility by checking primary authority receipt identities, same-family unqualified shadows, foreign-family shadows, status mutations, and ordering. They do not establish noninterference for every possible future engine implementation.

### Quarantining exceptions may hide operational failure

Plausible. RC0 establishes semantic-result isolation, not an operations policy for latency, resource exhaustion, repeated shadow failures, alerting, or retry limits. Operational health should remain observable and separately governed.

### The observed runtime may be unnecessary product complexity

Plausible. RC0 establishes that the architecture can collect shadows safely under the tested conditions. It does not establish that any available secondary instrument provides enough information value to justify its latency or maintenance cost.

## Falsified alternatives

Within the tested scope, the following alternatives were rejected:

- shadow collection must occur after verdict production to preserve semantic isolation;
- adding a valid foreign-family shadow necessarily changes primary semantics;
- same-family shadow measurements can silently substitute for the qualified primary authority input;
- shadow order may determine canonical ledger identity;
- an invalid shadow receipt must abort the semantic run;
- a raising shadow instrument must abort the semantic run;
- a shadow's `CLAIMED`/`UNRESOLVED`/`NOT_APPLICABLE` state can alter the primary verdict merely by being observed;
- adding live shadow collection requires changing existing verdict fixtures or weakening M3 authority/ledger validation.

## What is not established

RC0 does not establish:

- that any shadow instrument is accurate, useful, calibrated, or worth running;
- that a secondary instrument should ever influence warrant, relation, composition, or verdict;
- safe voting, consensus, confidence aggregation, ranking, or winner selection;
- NLI/LLM/learned-instrument authority;
- isolation from arbitrary in-process side effects, global-state mutation, resource exhaustion, network effects, or malicious code;
- acceptable latency or compute overhead;
- independent implementation or independent reproduction;
- generic semantic coverage;
- a new semantic family;
- claim decomposition;
- retrieval/evidence-selection improvement;
- Contract C or Decision Engine changes;
- production release readiness.

The implementation and evaluator remain in one research lineage.

## Evaluator assurance

For the bounded M4 claim, the apparatus is assessed as **E2 — sensitivity/invariance validated**:

- the target property and causal isolation invariant were preregistered before implementation;
- all nine M4 falsifiers were frozen before the runtime API existed;
- the pre-implementation run demonstrated capability absence rather than silently skipping the new surface;
- the cohort exercises no-shadow equivalence, foreign-family participation, same-family unqualified participation, order mutation, invalid identity, raised exceptions, status mutation, authority receipt identity, and replay determinism;
- the inherited semantic-identity sentinel detected the intentional engine change and forced an explicit successor freeze;
- the full repository suite and static-analysis gates passed on one exact final implementation head;
- intermediate red runs were preserved and classified.

This is not E4/E5 evidence because there is no independent implementation, sealed context-free reproduction, hostile-process isolation test, or independent evaluator implementation.

## Residual uncertainty

The important unresolved question is no longer whether CAL can observe secondary instruments without immediately contaminating the primary semantic path. It is whether any particular secondary instrument has enough independent measurement value to justify promotion beyond shadow status, and what evidence would be sufficient to grant it a narrowly scoped participation right without laundering agreement, confidence, or model identity into semantic authority.

The highest-risk future step would be allowing a secondary instrument to influence warrant formation simply because it agrees with the primary instrument. Prior CAL research already showed that cross-instrument agreement can preserve shared error; M4 does not change that conclusion.

## Reconsideration triggers

Reopen this result if any of the following occur:

- a shadow receipt ID appears in primary authority or relation state;
- shadow order changes primary result or canonical ledger identity;
- invalid/raising shadows prevent production of the primary semantic result;
- a future engine refactor routes the observation ledger into `warrant()`, `relate()`, or `compose()` without a separately qualified participation policy;
- shadow execution is allowed to mutate primary context, registry, admitted evidence, or qualified primary receipt;
- operational side effects make same-process shadows unsafe in practice;
- secondary-instrument promotion requires weakening M3 authority or ledger invariants.

## Smallest justified next step

Do not let shadows vote or influence a verdict yet.

The next experiment, if pursued, should qualify **one concrete secondary instrument as a measurement candidate** against a frozen cohort with independent/held-out truth, explicit failure localization, and weak controls. Its objective should be to establish whether the instrument adds information that the primary instrument lacks while preserving the distinction between measurement quality and semantic authority.

Only after such an instrument is shown to add bounded value should CAL test a separate, explicit participation policy for whether and how that instrument may influence authority formation.