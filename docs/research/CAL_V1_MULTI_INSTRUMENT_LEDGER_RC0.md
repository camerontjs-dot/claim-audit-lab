# CAL V1 Multi-Instrument Measurement Ledger RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / measurement-boundary hardening.

This experiment is stacked on the terminal M2 claim-compiler result record at `a002ae6ccba7af544de978c0b55bc1a3c37fdb89`. It is not independent evidence from that lineage and it does not authorize production promotion.

## Question

Can CAL introduce a production measurement-ledger primitive that preserves multiple heterogeneous measurement receipts under one immutable `AuditContext`, with deterministic order-independent identity and full evidence-aperture binding, while preventing any aggregate property, agreement count, confidence, or foreign-family observation from becoming semantic authority?

## Frozen parent

- parent branch: `research/cal-v1-claim-compiler-rc0-20260917`
- parent result-record head: `a002ae6ccba7af544de978c0b55bc1a3c37fdb89`
- exact M2 qualified implementation head: `99bfbe9ec70b01d98d46d7303001096b27209e68`
- current measurement receipt implementation: `production_v1/semantic/measurements.py`
- current authority implementation: `production_v1/semantic/authority.py`
- current engine authority path: semantic-family plugin -> one measurement receipt -> independent source completion -> warrant -> relation

The existing engine verdict path remains the behavioral baseline throughout RC0.

## Prior evidence being reused as design evidence, not promotion authority

CAL Measurement Envelope RC0 (#95) supported an information-preserving family-neutral envelope in research apparatus:

- multiple measurement receipts could bind to one exact audit context;
- each receipt preserved the full admitted evidence aperture and its exact consumed subset;
- insertion order did not change canonical ledger identity;
- measurement authority state remained unevaluated;
- attempts to launder measurement into warrant state failed closed.

RC7E heterogeneous language-instrument ablation (#63) showed that heterogeneous instruments can add genuinely useful observations while agreement is not a safe authority rule. In that held-out cohort, cross-family agreement still contained substantial error and no safe-gain authority subset was established.

RC0 therefore tests storage and authority separation, not ensemble decision quality.

## Baseline seam to falsify

Live parent code shows `complete_and_warrant()` verifies receipt identity, aperture, instrument identity, source reconstruction, and measured/source semantic equality. It does **not** independently verify that `receipt.semantic_family == context.proposition.semantic_family`; that invariant is currently enforced by `SemanticFamilyPlugin.warrant()` in the normal engine path.

A multi-family measurement ledger would make foreign-family observations first-class objects under the same context. RC0 therefore preregisters a direct authority attack:

> A valid foreign-family measurement receipt bound to the same `AuditContext` must not be warrantable merely because its own source reconstruction and instrument identity are internally valid.

If the frozen parent accepts that attack, preserve the failure and repair only the missing authority-boundary guard. Do not solve it by forbidding heterogeneous observations from the ledger.

## Bounded implementation hypothesis

Add an immutable `MeasurementLedger` production primitive with these properties:

- binds to one exact `AuditContext` hash;
- preserves the exact full admitted passage-ID aperture;
- accepts only valid `MeasurementReceipt` objects whose context/aperture/receipt identity verify against that context;
- may contain receipts from more than one semantic family because measurement is observation, not authority;
- preserves every receipt exactly rather than voting, averaging, ranking, or collapsing them;
- canonicalizes receipt ordering so append order cannot change ledger identity;
- rejects duplicate receipt identity;
- exposes no warrant, categorical relation, CAL conclusion, Contract C result, Decision result, or aggregate authority score.

No existing measurement algorithm is promoted or replaced. RC0 will use the two already-qualified bounded production measurement instruments as heterogeneous controls:

- `rc7fb1-strict-comparison`;
- `rc7fc-event-order`.

## Authority hardening hypothesis

If the preregistered foreign-family attack succeeds on the frozen parent, add the smallest authority check needed so direct authority consumption independently refuses a receipt whose semantic family differs from the proposition family.

The guard must live at or below the authority boundary. Relying only on the plugin caller is insufficient once receipts can exist in a family-neutral ledger.

No measurement proposal, source-completion grammar, warrant semantics, relation rule, composition rule, or verdict rule may change to obtain a pass.

## Frozen evaluation plan

Before implementation correction, add tests that exercise:

1. empty ledger identity bound to an exact audit context;
2. strict-comparison and direct-event-order receipts coexisting under one context when both consume admitted passages;
3. order-independent canonical ledger identity for append order `[strict,event]` versus `[event,strict]`;
4. exact preservation of full available passage aperture and each receipt's consumed passage subset;
5. duplicate receipt rejection;
6. foreign/stale audit-context receipt rejection;
7. stale receipt-identity mutation rejection;
8. receipt aperture omission/rebinding rejection;
9. no authority/verdict/decision fields or aggregate confidence/vote surface on the ledger;
10. current proposition-family receipt can still traverse the existing authority path unchanged;
11. foreign-family receipt bound to the same context is refused by direct authority consumption;
12. existing M1/M2 semantic, Contract B, compiler, full repository, Ruff, and mypy gates remain green.

The authority attack in item 11 should be executed against the preregistered frozen-parent behavior before any corrective guard is accepted as evidence.

## Success conditions

RC0 is supported only if all of the following hold on one exact successor head:

- heterogeneous receipts coexist without altering or deleting their raw measurement payloads;
- ledger identity is deterministic and append-order independent;
- every receipt remains bound to the same exact audit context and full evidence aperture;
- no ledger operation authorizes, scores, votes, or resolves measurements;
- duplicate, foreign, stale, and aperture-mutated receipts fail closed;
- foreign-family direct authority consumption fails closed at the authority boundary itself;
- the currently warranted same-family production path remains behaviorally unchanged;
- no semantic family is added or widened;
- no existing expected semantic/verdict fixture is changed;
- full-history repository tests and static-analysis gates remain green.

## Falsifiers / stop rules

Preserve a negative result if any of these occur:

- ledger insertion order changes canonical identity;
- a receipt can enter the ledger with stale context, stale aperture, or stale identity;
- a ledger field or helper computes a vote, aggregate confidence, winning family, or warrant state;
- foreign-family measurement becomes warrantable under the proposition context;
- fixing foreign-family warranting requires changing family semantics rather than adding a boundary guard;
- current same-family verdict behavior changes;
- expected semantic fixtures are changed after observing behavior;
- success requires integrating NLI, LLMs, or a new semantic family in this RC.

## Alternative explanations to pressure-test

- a ledger may be architectural ceremony if the engine still consumes only one receipt;
- order-independent hashing may hide semantically meaningful execution order if future instruments depend on prior outputs;
- allowing cross-family measurements may increase attack surface even if authority is guarded;
- the two existing deterministic instruments are heterogeneous only in semantic principle, not in implementation technology;
- preserving every observation may create operational burden without improving later decisions.

RC0 does not claim to resolve those broader questions. Its purpose is to establish a safe observation container and hard authority boundary before richer instruments are introduced.

## Non-goals

RC0 does not test or authorize:

- measurement voting or ensemble selection;
- confidence thresholds;
- NLI authority;
- LLM proposal instruments;
- learned parsers;
- new semantic families;
- claim decomposition;
- retrieval changes;
- evidence selection changes;
- changes to scoreless composition;
- Contract C changes;
- Decision Engine changes;
- automatic action.

## Promotion boundary

A supported RC0 would justify only this architectural step:

> CAL may preserve multiple heterogeneous measurement receipts in one immutable, context-bound, order-independent ledger while semantic authority remains a separate explicitly qualified boundary.

Engine integration of multiple instruments, instrument selection policy, or any rule that allows more than the current primary instrument to participate in warrant formation requires a separate successor experiment.
