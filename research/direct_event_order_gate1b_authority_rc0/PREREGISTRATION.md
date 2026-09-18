# CAL Direct Event Order Gate-1B Authority RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / source-completion and warrant discrimination.

## Frozen subject

This study tests the pre-existing M4 authority firewall.

- M4 terminal parent: `607ec560fd53bd56279193a8d39a48b6f80e1012`
- direct-event-order instrument identity remains `rc7fc-event-order / rc7fc-event-order-1`
- hardening evidence: PR #140, hardening head `02b1e44392b3ff477c3407bcf25d939e3377db17`, run `35292276872`

PR #140 established that raw direct-event-order measurement can emit a plain two-event order atom while dropping reporting, epistemic, conditional, temporal-relation modifier, causal-tail, or third-event structure.

## Question

Can the already-independent source-completion/warrant layer reject those lossy measurements while continuing to warrant clean supported two-event sources?

## Cohorts

### WARRANT

Clean direct two-event BEFORE / AFTER sources, including event polarity.

### REFUSE_AFTER_LOSSY_MEASUREMENT

Exact hardening counterexamples known to produce CLAIMED raw measurements:
- reporting wrapper;
- epistemic `Perhaps`;
- conditional `If`;
- `not before`;
- `immediately before`;
- `shortly before`;
- causal tail;
- third-event conjunction;
- third-event disjunction.

Each counterexample must reproduce a CLAIMED measurement and then be refused by `complete_and_warrant()`.

## Acceptance

`SUPPORTED_GATE1B_DIRECT_EVENT_ORDER` only if every clean case warrants and every lossy measurement is refused.

No `src/` changes are permitted. No repair inside RC0.

## Non-claims

A pass does not establish a complete temporal logic or general modifier handling. It establishes only that the frozen independent source-completion firewall catches these known measurement-loss cases.
