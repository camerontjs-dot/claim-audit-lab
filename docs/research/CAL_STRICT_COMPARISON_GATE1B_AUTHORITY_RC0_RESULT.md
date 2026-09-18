# CAL Strict Comparison Gate-1B Authority RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / source-completion and warrant discrimination.

## Frozen subject

- M4 terminal parent: `607ec560fd53bd56279193a8d39a48b6f80e1012`
- exact RC0 apparatus head: `67a58e4216308650a7f49de7963682bdc58a82f7`
- dedicated run: `35294374391`
- production `src/` verified unchanged from M4

## Disposition

**FAILED_GATE1B_STRICT_COMPARISON — CURRENT AUTHORITY FIREWALL DOES NOT CATCH MODIFIER LOSS.**

The independent M4 source-completion path correctly warrants clean strict-comparison sources, but it also warrants the modifier-bearing positive-comparison measurements that the production strict instrument emits.

## Clean controls

All three clean controls produced:

- measurement status `CLAIMED`;
- authority status `WARRANTED`.

This confirms the experiment exercised the intended production authority path.

## Unsafe warrants

Seven exact modifier-bearing sources produced a `CLAIMED` production measurement and were then **WARRANTED**:

1. `Sector A was not higher than Sector B.`
2. `Sector A was no higher than Sector B.`
3. `Sector A was probably higher than Sector B.`
4. `Sector A was allegedly higher than Sector B.`
5. `Sector A may be higher than Sector B.`
6. `Sector A could be higher than Sector B.`
7. `The report says Sector A is higher than Sector B.`

These are not measurement-only failures. The existing independent source completion re-reads the source but reconstructs the same stripped positive relation, so the loss survives into an `AuthorityReceipt(status="WARRANTED")`.

## Scope correction

Three hardening cases from the older RC7F-B1 research comparator were not in the current production strict-measurement jurisdiction:

- negated equality;
- negated same-as;
- negated multiplier.

The M4 production measurement returned `NOT_APPLICABLE` for those cases and the authority path refused them. They are therefore not counted as Gate-1B authority leaks for the current production subject.

This mismatch is preserved explicitly rather than being treated as an authority success on a measurement feature the production instrument does not implement.

## Architectural consequence

The current split:

```
measurement -> independent source completion -> warrant
```

is structurally sound, but the strict source completer is semantically too permissive. Independence alone is insufficient if the independent parser makes the same abstraction error.

The smallest justified successor is a **modifier-aware source-completion envelope** that refuses or explicitly represents at least:

- relation negation;
- epistemic modality;
- attribution/reporting.

The successor should not widen comparison grammar. It should harden the authority boundary.

## Non-claims

This result does not invalidate clean strict-comparison measurement or relation algebra. It does not authorize a production patch, merge, or release. A fresh successor must be frozen and qualified separately.
