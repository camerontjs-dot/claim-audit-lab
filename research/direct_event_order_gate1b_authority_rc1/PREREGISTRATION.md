# CAL Direct Event Order Gate-1B Authority RC1 — Preregistration

Date: 2026-09-17

Classification: Draft Research / successor source-completion and warrant qualification.

Parent: exact M4 terminal `607ec560fd53bd56279193a8d39a48b6f80e1012`.

Predecessor:
- PR #143
- disposition `FAILED_GATE1B_DIRECT_EVENT_ORDER`
- six production-measurement claims survived the existing source completer and were incorrectly warranted.

## Question

Can a stricter independent source-completion layer preserve clean direct two-event BEFORE/AFTER semantics while refusing sources whose epistemic, conditional, temporal-modifier, negation, or causal-tail state is not represented in the order atom?

## Frozen boundaries

RC1 may change only research-side authority/source-completion machinery.

It may not:
- change the production event-order measurement;
- widen event grammar;
- change BEFORE/AFTER relation algebra;
- change production `src/`;
- treat temporal modifiers as equivalent to plain BEFORE/AFTER;
- rely on the measurement proposal as source authority.

## Required clean jurisdiction

The candidate must independently reconstruct and warrant:
- direct BEFORE;
- direct AFTER;
- negative left-event polarity;
- negative right-event polarity.

## Required refusals after CLAIMED production measurement

- epistemic `Perhaps`;
- conditional `If`;
- `not before`;
- `immediately before`;
- `shortly before`;
- causal tail after the second event.

## Warrant contract

A candidate may warrant only when:
1. the measurement receipt verifies against the exact context;
2. the exact production event-order instrument identity is present;
3. exactly one named passage was consumed;
4. independent source completion reconstructs exactly two supported events and exactly one unmodified BEFORE/AFTER cue;
5. reconstructed fields equal measurement fields.

## Acceptance

`SUPPORTED_GATE1B_DIRECT_EVENT_ORDER_RC1` requires all clean cases warrant, all six lossy measurement cases reproduce `CLAIMED` and are refused, replay is exact, the frozen weak permissive authority is rejected, and production `src/` is unchanged.

Broader end-stage pressure testing is deferred until every family is finalized.
