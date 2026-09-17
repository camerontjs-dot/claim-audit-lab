# CAL Deontic Norm Family Contract RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / semantic-family discrimination. Stacked on terminal M4 result commit `607ec560fd53bd56279193a8d39a48b6f80e1012`. Roadmap context is recorded separately in Draft PR #121.

No production `src/` mutation, semantic-family enum change, plugin registration, Contract C/Decision change, release, or merge is authorized by this experiment.

## Question

Can one typed deontic proposition family preserve the distinctions among:

- `PERMITTED`;
- `PROHIBITED`;
- `OBLIGATORY`;
- `PERMISSION_RESTRICTED_TO`;

while carrying explicit exception, condition, and temporal bindings **without** unsafe cross-mode implication or modifier erasure?

This Gate-0 experiment deliberately removes natural-language parsing. It tests the semantic contract before any new CAL plugin is built.

## Prior evidence

Prior CAL research is design evidence, not automatic current-kernel qualification:

- RC7F-D / PR #71 produced a bounded permission-composition measurement candidate with 50/50 supported cases recovered, 0 false proposals on 14 negative/unsupported controls, and exact exception/temporal attachment on the frozen cohort.
- PR #72 classified permission + exception/temporal composition as a bounded measurement candidate while assertion/scope warrant remained unsafe.
- Population/interpretation-authority work showed that extraction failure, semantic unknown, and source-authority failure must remain distinct rather than being laundered into a semantic value.

The new question is narrower and more architectural: **is one deontic family contract coherent before we spend effort on text measurement and warrant?**

## Proposed typed contract

Each norm has:

- `mode`: one of the four modes above;
- `subject`: exact actor/population symbol;
- `action`: exact action symbol;
- `exceptions`: zero or more exact excluded symbols;
- `condition`: optional exact condition symbol;
- `temporal_relation`: optional relation symbol;
- `temporal_reference`: optional reference symbol.

The modifier fields are intentionally not named `permission_exception` state. They are bindings on the proposition scope. This tests the hypothesis that exception/condition/time can be reusable modifier structure rather than defining a separate family for each combination.

## Conservative formal semantics

For the **same exact subject, action, and modifier scope**:

- a norm supports the same mode;
- `PERMITTED` and `PROHIBITED` refute one another;
- `OBLIGATORY` and `PROHIBITED` refute one another;
- `OBLIGATORY` does **not** automatically support `PERMITTED` in RC0;
- `PERMISSION_RESTRICTED_TO` does **not** automatically support direct permission for the named population;
- all other cross-mode relations remain unresolved.

If subject, action, or modifier scope differs, RC0 returns unresolved rather than inventing overlap/disjointness, condition implication, temporal implication, or population membership.

This is intentionally weaker than full deontic logic. Any stronger implication requires later evidence.

## Independent oracle shape

Freeze a small possible-assignment oracle separate from the direct candidate consumer.

For one exact semantic scope, use independent boolean variables for:

- permission `P`;
- prohibition `F`;
- obligation `O`;
- restricted-to `R`.

Source constraints:

- `PERMITTED`: `P=true`, `F=false`;
- `PROHIBITED`: `F=true`, `P=false`, `O=false`;
- `OBLIGATORY`: `O=true`, `F=false`, while `P` remains unconstrained;
- `PERMISSION_RESTRICTED_TO`: `R=true`, while `P/F/O` remain unconstrained.

A query is `SUPPORTS` if true in every source-compatible assignment, `REFUTES` if false in every source-compatible assignment, otherwise `UNRESOLVED`.

Different semantic scope returns `UNRESOLVED` before mode evaluation.

## Frozen weak controls

The evaluator must kill at least these plausible weak strategies:

1. **ought-implies-may**: treat `OBLIGATORY -> PERMITTED` as `SUPPORTS`;
2. **restriction-grants-permission**: treat `PERMISSION_RESTRICTED_TO -> PERMITTED` as `SUPPORTS`;
3. **ignore-modifiers**: compare only mode/subject/action and erase exception, condition, and temporal bindings;
4. **exact-mode-only**: support identical modes but never emit explicit refutation for permission/prohibition or obligation/prohibition conflicts.

A weak control that fails only because of syntax/import/provenance does not count as semantic discrimination.

## Frozen cohort requirements

Include direct and mutation cases for:

- all four exact-mode supports;
- permission <-> prohibition conflict;
- obligation <-> prohibition conflict;
- obligation vs permission in both directions;
- restricted-to vs direct permission in both directions;
- subject substitution;
- action substitution;
- exception change/removal;
- condition change/removal;
- temporal relation change/removal;
- temporal reference change;
- compound modifier exact-match and one-field mutations;
- the same conflict relations under modifiers;
- deterministic replay.

The corpus is semantics-first typed data. No parser or model output establishes gold.

## Metamorphic requirements

Freeze paired cases where changing exactly one semantic dimension changes the oracle relation. At minimum:

- query permission -> prohibition changes support to refutation;
- query prohibition -> permission under an obligation source changes refutation to unresolved;
- exact restricted-to -> direct permission changes support to unresolved;
- exception mutation changes support to unresolved;
- condition mutation changes support to unresolved;
- temporal relation/reference mutation changes support to unresolved;
- subject mutation changes support to unresolved;
- action mutation changes support to unresolved.

## Success condition

`SUPPORTED FOR PROMOTION` is permitted only if, on one exact frozen successor:

- the formal oracle is internally deterministic;
- every frozen weak control is rejected for the intended semantic reason;
- the direct candidate consumer matches the oracle on every frozen case;
- every metamorphic pair exhibits the preregistered relation change;
- deterministic repeat is exact;
- no production `src/` file changes;
- repository/static gates used by the experiment are green.

A pass supports only the typed deontic family contract as input to a later measurement/warrant experiment.

## Falsifiers / stop rules

Preserve a negative result if:

- one contract cannot preserve the four modes without unsafe implication;
- modifier bindings must be erased or embedded into mode names to obtain agreement;
- the weak controls cannot be discriminated;
- candidate success requires changing the frozen oracle/cohort after candidate exposure;
- stronger deontic logic is required to make the current contract appear coherent;
- production semantics must change during this Gate-0 experiment.

## Non-claims

RC0 does not establish natural-language extraction, source-completion warrant, operational authorization, universal deontic logic, nested rules, exception entailment, temporal reasoning, population overlap, Contract E authority, production plugin readiness, or pipeline promotion.