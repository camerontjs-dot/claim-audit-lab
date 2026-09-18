# CAL Event-Order Authority Pressure RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / post-qualification adversarial pressure.

## Frozen subject

- PR #96 final head: `3a4b5f24f813843eae3857ed3444fb12b1cb8182`
- candidate wrapper blob: `36a8d1fbd9e52ec743757f750f744ad4553b5698`
- source-completion blob: `88df954235069e98582e731f48e46e5b257da93f`
- pressure head: `977c2253bc7c5837ff1c23f46ad5fc0178a17d50`
- pressure run: `35295379174`

The frozen PR #96 candidate, RC7F-C measurement, RC8J evaluator, and production `src/` remained unchanged.

## Disposition

**FALSIFIED_EVENT_ORDER_AUTHORITY_MODIFIER_APERTURE_RC0.**

PR #96 remains supported for its original frozen direct grammar and mutation cohort. The stronger claim that its source-completion aperture safely excludes the harder modifier/composition surfaces from PR #140 is falsified.

## Positive controls

Positive failures: **0**.

Both direct controls completed and warranted as expected.

## Semantic completion and authority leaks

Six pressure cases independently completed and then received exact RC8J `WARRANTED`:

- `EOA-U02-EPISTEMIC`: `Perhaps Talia reviewed packet u before Ravi signed ledger c.`
- `EOA-U03-CONDITIONAL`: `If Talia reviewed packet u before Ravi signed ledger c.`
- `EOA-U04-RELATION-NEGATION`: `Talia reviewed packet u not before Ravi signed ledger c.`
- `EOA-U05-IMMEDIATE`: `... immediately before ...`
- `EOA-U06-SHORTLY`: `... shortly before ...`
- `EOA-U07-CAUSAL-TAIL`: `... before ... because QA requested it.`

Thus:

- semantic completion leaks: **6**
- unsafe warranted leaks: **6**

Reporting-prefix, third-supported-event conjunction/disjunction, multiple-cue, calendar, and narrative controls failed closed.

## Failure mechanism

The source completer is structurally bounded, but its permitted one/two-token subject and one-to-six-token object regions can absorb semantically material surrounding words:

- `Perhaps Talia` / `If Talia` become two-token subjects;
- `packet u not|immediately|shortly` becomes an expanded left object;
- the causal/context tail is absorbed into the right object.

RC8J then correctly warrants the internally coherent object it receives. The defect is therefore source completion, not RC8J identity validation.

## Smallest successor

Do not patch by adding an expanding modifier blacklist.

Test a narrower positive structural aperture:

- exactly one bare `before|after` cue;
- exactly two supported events;
- one-token subject on each side;
- one-or-two-token object on each side;
- direct positive or `did not` event polarity only;
- full-sentence match.

This intentionally sacrifices multi-token-subject and longer-object recall. Those forms remain measurement-only until separate entity/object binding machinery justifies widening.

The six pressure failures become revealed development evidence. A fresh post-freeze cohort is required.

## Non-claims

This result does not invalidate PR #96's original frozen result or RC8J. It does not authorize production change, merge, release, or promotion.
