# CAL Event Occurrence Gate-1B Authority RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / independent source-completion and warrant qualification.

Parent: terminal Event Occurrence Gate-1A head `f69c1d82ef45fd8860c4c37f8e7555d4337afbfc`.
Selected measurement path: `conservative_event_hybrid`.

## Question

Can an independent authority layer reconstruct the exact event-occurrence atom from source text and refuse a measured atom whose actor, action, object, polarity, scope, or time binding has been altered?

## Frozen clean jurisdiction

Representative qualified forms include:
- direct positive occurrence;
- direct negative occurrence;
- multiple actor/action/object bindings;
- explicit time binding;
- passive positive and negative occurrence;
- selected safe extensions: open-vocabulary direct action, nominalized occurrence, and terse event-log syntax.

## Frozen mismatch falsifiers

Starting from a legitimately CLAIMED measurement, the evaluator mutates:
- actor;
- action;
- object;
- polarity;
- time;
- scope.

## Warrant contract

A candidate may warrant only if it independently reconstructs exactly one bounded event atom equal to the measured atom. It must not call the Gate-1A measurement function as source authority.

Event order remains a separate semantic family. This authority step must not infer order or occurrence from a neighboring order proposition.

## Acceptance

`SUPPORTED_GATE1B_EVENT_OCCURRENCE_RC0` requires every clean case to warrant, every frozen mutation to refuse, replay to be deterministic, a trust-measurement weak authority to be detected, and Gate-1A / production files to remain unchanged.

Broad pressure testing is deferred until all families are finalized.
