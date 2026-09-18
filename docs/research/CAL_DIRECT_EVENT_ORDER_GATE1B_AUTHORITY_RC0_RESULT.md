# CAL Direct Event Order Gate-1B Authority RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / source-completion and warrant discrimination.

## Frozen subject

- M4 terminal parent: `607ec560fd53bd56279193a8d39a48b6f80e1012`
- exact RC0 apparatus head: `39dd9fc4b69a8ef7fa507e8b00589c066d61bc19`
- dedicated run: `35294442949`
- production `src/` verified unchanged from M4

## Disposition

**FAILED_GATE1B_DIRECT_EVENT_ORDER — CURRENT AUTHORITY FIREWALL DOES NOT CATCH ALL MODIFIER/COMPOSITION LOSS.**

The production measurement and independent source-completion seam correctly warrant clean two-event order sources, and production measurement already blocks some hardening surfaces. But six modifier-bearing sources are still measured as `CLAIMED` and then incorrectly `WARRANTED`.

## Clean controls

All three clean controls produced:
- measurement `CLAIMED`;
- authority `WARRANTED`.

## Unsafe warrants inside the current production measurement jurisdiction

The following sources produced a `CLAIMED` production measurement and were then `WARRANTED`:

1. `Perhaps Talia reviewed packet u before Ravi signed ledger c.`
2. `If Talia reviewed packet u before Ravi signed ledger c.`
3. `Talia reviewed packet u not before Ravi signed ledger c.`
4. `Talia reviewed packet u immediately before Ravi signed ledger c.`
5. `Talia reviewed packet u shortly before Ravi signed ledger c.`
6. `Talia reviewed packet u before Ravi signed ledger c because QA requested it.`

## Surfaces already blocked before authority

Three older RC7F-C hardening cases were `UNRESOLVED` at the current production measurement seam and therefore refused before warrant:

- report-attributed order;
- third-event conjunction;
- third-event disjunction.

They are not counted as authority leaks.

## Architectural consequence

Independence alone is insufficient when both measurement and source completion accept the same lossy abstraction.

The smallest justified successor is an event-order source-completion envelope that refuses or explicitly represents:
- epistemic wrappers;
- conditional wrappers;
- temporal-relation negation;
- fine-grained temporal modifiers not represented by BEFORE/AFTER;
- causal/compositional tails attached to either event.

The successor must not widen event-order grammar or alter relation algebra.

## Non-claims

This result does not invalidate clean direct-event-order semantics. It does not authorize production changes, merge, or release. A fresh successor must be qualified separately.
