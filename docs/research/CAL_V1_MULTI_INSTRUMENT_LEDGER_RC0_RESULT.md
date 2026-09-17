# CAL V1 Multi-Instrument Measurement Ledger RC0 — Result

Date: 2026-09-17

Primary disposition: **SUPPORTED FOR PROMOTION**

Classification: bounded measurement-boundary and authority-hardening result only. This record does not authorize merge, release, production promotion, multi-instrument verdict participation, voting, confidence thresholds, learned/NLI/LLM authority, new semantic families, Contract C/Decision changes, or automatic action.

## Question

Can CAL introduce a production measurement-ledger primitive that preserves multiple heterogeneous measurement receipts under one immutable `AuditContext`, with deterministic order-independent identity and full evidence-aperture binding, while preventing any aggregate property, agreement count, confidence, or foreign-family observation from becoming semantic authority?

Preregistration: `docs/research/CAL_V1_MULTI_INSTRUMENT_LEDGER_RC0.md`

## Exact lineage

- repository: `camerontjs-dot/claim-audit-lab`
- parent M2 result head: `a002ae6ccba7af544de978c0b55bc1a3c37fdb89`
- preregistration commit: `95ea3a73d2ec26ef36c7fb653b8eb56c4839413c`
- initial direct authority falsifier freeze: `bf1be56ae63a1891179018d05c56ab5d661dd3b9`
- dedicated qualification-workflow commit: `d44f139c24c23ad6212e892e94c32ae0d025840e`
- complete ten-test falsifier freeze: `8af6664bcaff19677b8367641ac942acb8bbce94`
- initial ledger implementation: `068674fc1ab2dd224ccd01aa3ac756c7c7f379d2`
- authority-boundary guard: `ed3528d2bd972a110516b800ea9676d404ad4dfd`
- diagnostic-localization correction: `2bd89ce938036424b376b4c76143b96c6e873ea3`
- workflow frozen-history strengthening: `d1f0fd89b7f956a971b48822644f22fd5a938249`
- explicit M3 semantic successor freeze: `d2887d71f9b7493cde732a1db3d09e73c989e347`
- formatter-only ledger correction: `6fc5f6efc1121d49c0ac4b1d78cfafe1059c3365`
- exact qualified implementation head: `0e573d9f1426b5db1e01beb979e246f4cdd626b2`
- exact qualified tree: `1253feaeca3322935f1356c636ba0302c64ae74e`
- exact authority successor blob: `09761aab9e04deca724fd213a9295fc93cc3be52`
- exact formatted measurement-ledger blob: `5e01c0a3246a90fcc42219da78b7d8a1ed5d5f74`
- preserved M1 authority predecessor blob: `3cfcfb8cc3b3a8860e119edfbe22a4d684650a86`
- Draft PR: #119

## Observed baseline authority defect

The preregistration identified a latent boundary seam in the frozen parent: `complete_and_warrant()` verified measurement receipt identity, audit context, evidence aperture, consumed passage, instrument identity, independent source completion, and measured/source semantic equality, but did not itself require the measurement receipt semantic family to match the proposition semantic family. The normal plugin wrapper enforced that invariant, so the direct authority boundary had been relying on its caller.

The direct attack was frozen before the correction and then executed against the parent behavior.

Baseline run `35263871059` produced **1 passed, 1 failed**. The failure was the intended falsifier:

- `test_foreign_family_measurement_cannot_be_warranted_directly`
- observed failure: `DID NOT RAISE AuthorityRefusal`

The supplied foreign-family receipt was otherwise valid, bound to the same `AuditContext`, and independently reconstructable from its admitted event-order passage. This established that the caller-level guard was insufficient as an authority boundary.

## Implemented successor

### Immutable measurement ledger

RC0 adds `production_v1/semantic/measurement_ledger.py` as an observation-only container.

The ledger:

- binds to one exact `AuditContext` hash;
- preserves the exact full admitted passage-ID aperture;
- accepts existing `MeasurementReceipt` objects only after receipt verification against that context;
- may contain receipts from different semantic families;
- preserves each receipt's raw measurement payload and exact consumed subset;
- canonicalizes receipts by receipt identity so append order cannot change ledger identity;
- rejects duplicate receipt identity;
- rejects foreign/stale audit contexts, stale receipt identity, and aperture mutation;
- exposes no authority, warrant, relation, conclusion, decision, confidence, vote, winner, or aggregate-score surface.

The existing engine does not consume this ledger in RC0. No measurement algorithm, relation rule, composition rule, or verdict rule was widened.

### Authority-boundary hardening

The only semantic change to an existing production module is the preregistered guard in `authority.py`:

```python
if receipt.semantic_family is not context.proposition.semantic_family:
    raise AuthorityRefusal(
        "SEMANTIC_AUTHORITY_UNRESOLVED",
        "measurement/proposition semantic-family mismatch",
    )
```

The PR patch confirms this is the only change to `authority.py` relative to the M2 parent.

## Frozen evaluation evidence

The complete falsifier suite was frozen at `8af6664bcaff19677b8367641ac942acb8bbce94` before the ledger implementation.

It tests:

1. exact empty-ledger context/aperture binding;
2. coexistence of strict-comparison and direct-event-order receipts under one context;
3. append-order-independent identity;
4. duplicate receipt rejection;
5. foreign-context receipt rejection;
6. stale receipt-identity mutation rejection;
7. aperture omission/rebinding rejection;
8. absence of authority/verdict/aggregation API;
9. preservation of the same-family direct authority path;
10. refusal of direct foreign-family authority consumption.

The mixed test context also preserves an unrelated admitted passage so the tests can distinguish the full available aperture from each instrument's consumed subset.

## Preserved failures and corrections

### Baseline unsafe authority attack

Run `35263871059`: **negative evidence preserved**. The foreign-family direct authority attack succeeded because `complete_and_warrant()` did not independently enforce proposition-family agreement.

This was repaired only at the authority boundary; the ledger was not made family-exclusive to hide the defect.

### First post-implementation run

Run `35264152716`: **9/10 focused tests passed**. The sole failure was diagnostic localization, not unsafe acceptance: a foreign-context receipt was refused by the existing verifier as `stale or foreign measurement context`, while the frozen ledger test expected the ledger boundary to localize the refusal as `measurement audit-context mismatch`.

Correction `2bd89ce938036424b376b4c76143b96c6e873ea3` added an explicit ledger precheck for that already-invalid condition. No acceptance rule, semantic family behavior, or expected fixture changed.

### Semantic identity sentinel

Run `35264358228`: the complete M3 focused suite passed **10/10**, but the inherited semantic-blob sentinel correctly failed **2 tests** because M3 intentionally changed `authority.py` from predecessor blob `3cfcfb8c...` to successor blob `09761aab...`.

This was treated as a promotion-boundary signal, not bypassed. The exact PR patch was inspected and confirmed that `authority.py` changed only by the preregistered family-match guard.

The successor freeze at `d2887d71f9b7493cde732a1db3d09e73c989e347` therefore:

- preserves the M1 authority blob explicitly as predecessor provenance;
- pins the M3 authority successor blob;
- pins the new ledger blob;
- continues pinning every untouched semantic implementation to its predecessor blob identity.

No semantic/verdict fixture was rewritten.

### Formatter-only failure

Run `35264642980` then passed:

- M3 focused suite: **10 passed**;
- inherited M1/M2 semantic, Contract B, and compiler gates: **54 passed**;
- full repository pytest: **1048 passed, 5 skipped, 48 deselected**;
- Ruff lint: **pass**;

It failed only Ruff format on one line in `measurement_ledger.py`; mypy was therefore skipped.

Correction `6fc5f6efc1121d49c0ac4b1d78cfafe1059c3365` applied Ruff's requested one-line formatting. Because the ledger is content-pinned, `0e573d9f1426b5db1e01beb979e246f4cdd626b2` then advanced the explicit ledger blob identity from the pre-format blob to the formatted blob. No logic changed.

## Final qualification result

Dedicated full-history push workflow:

- run `35265186361` — `Research - CAL V1 multi-instrument ledger RC0` — **success**.

Observed on exact qualified head `0e573d9f1426b5db1e01beb979e246f4cdd626b2`:

- frozen M3 ledger and authority falsifiers: **10 passed**;
- inherited M1/M2 semantic, Contract B, and compiler gates: **54 passed**;
- full repository pytest: **1048 passed, 5 skipped, 48 deselected**;
- Ruff lint: **pass**;
- Ruff format: **pass** (`68 files already formatted`);
- mypy: **pass** (`no issues found in 67 source files`).

The qualification workflow uses `fetch-depth: 0` and explicitly verifies the frozen parent, preregistration, initial authority-attack freeze, and complete ten-test falsifier freeze before running the gates.

## Inference

The evidence supports the bounded claim that CAL can preserve heterogeneous measurement observations under one immutable audit context without making the observation container an authority mechanism.

It also supports a specific hardening conclusion: semantic-family agreement with the proposition is an invariant that must be enforced at the authority boundary itself, not only by the normal plugin caller. The frozen direct attack falsified the weaker caller-only design, and the corrected boundary passes both the attack and the pre-existing same-family path.

The result does **not** establish that multiple measurements should jointly influence a verdict. It establishes only that CAL now has a safe place to preserve them and a stronger firewall preventing a foreign-family observation from becoming warranted merely because it is internally valid.

## Alternative explanations considered

### The ledger may be architectural ceremony

Plausible. The production engine still consumes one measurement receipt per passage/family path, so RC0 does not demonstrate decision-quality gain from the ledger. Its demonstrated value is provenance-preserving observation storage and the attack surface it exposed.

### Order-independent identity may be too strong for future sequential instruments

Plausible. RC0 instruments are independent observations. If future instruments explicitly depend on prior instrument output, execution-order provenance would need a different contract rather than being silently folded into this ledger.

### The two instruments are not technologically heterogeneous

Correct. They are distinct semantic-family instruments but both are deterministic in-repository code. RC0 therefore does not establish safety for learned/NLI/LLM instruments.

### The authority defect may have been unreachable in the normal engine

Before M3, the normal plugin path did guard the family. That does not remove the boundary defect: `complete_and_warrant()` was a callable authority surface that accepted a valid foreign-family receipt directly. The stronger boundary makes the invariant local and independently enforceable.

## Falsified alternatives

Within the tested scope, the following alternatives were rejected:

- plugin-level family validation alone is a sufficient authority boundary;
- a valid foreign-family measurement can safely be warranted under another proposition family;
- heterogeneous measurement preservation requires voting or selecting a winning family;
- ledger identity may depend on insertion order;
- a measurement can enter the ledger with stale context, stale identity, or incomplete aperture binding;
- adding the ledger requires changing existing measurement, relation, composition, or verdict behavior.

## What is not established

RC0 does not establish:

- useful multi-instrument verdict participation;
- safe voting, consensus, ranking, or confidence aggregation;
- NLI, LLM, or learned-instrument authority;
- independent measurement implementations;
- generic semantic coverage;
- a new semantic family;
- claim decomposition;
- retrieval/evidence-selection improvement;
- Contract C or Decision changes;
- production release readiness.

The implementation and evaluator remain in one research lineage. This is not an independent reproduction.

## Evaluator assurance

For the bounded RC0 claim, the apparatus is assessed as **E2 — sensitivity/invariance validated**:

- the direct unsafe authority attack was preregistered and frozen before correction;
- the complete ten-test suite was frozen before ledger implementation;
- the evaluator demonstrably detected the unsafe parent behavior;
- identity, context, aperture, duplicate, mutation, order, and forbidden-authority-surface controls were exercised;
- the semantic identity sentinel independently detected the intentional authority implementation change;
- full repository and static-analysis gates passed on one exact final head;
- all intermediate red runs were preserved and classified rather than overwritten.

This is not E4/E5 evidence because there is no independent implementation or context-free reproduction.

## Residual uncertainty

The next unresolved question is no longer whether CAL can store heterogeneous observations safely. It is whether additional instruments can participate in the runtime without creating a covert authority policy.

The highest-risk assumption is that an instrument-selection or participation policy can be introduced while preserving the rule that **measurement agreement, confidence, and model identity are not themselves warrant**.

## Reconsideration triggers

Reopen this result if any of the following occur:

- a ledger receipt can bypass exact audit-context or aperture binding;
- append order changes canonical ledger identity for independent observations;
- any ledger helper begins selecting, scoring, voting, or authorizing observations;
- a foreign-family receipt can again traverse direct authority consumption;
- multi-instrument engine integration requires weakening the authority-family guard;
- the new ledger becomes a hidden substitute for evidence-world construction or semantic composition.

## Smallest justified next step

Do not yet let multiple instruments vote on a verdict.

Run a separate successor experiment for **controlled multi-instrument runtime participation**: allow the engine to collect a primary qualified measurement plus one or more shadow measurements into the ledger, prove that shadow observations cannot alter warrant/relation/verdict output, and establish an explicit participation policy boundary before testing any proposal for secondary-instrument promotion.
