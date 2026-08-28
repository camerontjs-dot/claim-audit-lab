# Contract C RC2-C — CAL Evidence-to-Rule Dependency Receipt Results

## Decision under review

Determine whether current CAL v0.2 execution contains enough legitimate information to produce a compact attributable receipt connecting:

`evidence state -> rule trigger -> emitted rule result -> terminal verdict branch`

for the frozen absolute-wording/counterevidence seam, without changing production CAL semantics.

## Frozen identities

- CAL production-semantic SHA: `33a928db97316a3652d57df9cafb8ca240305233`.
- Research base / live `main` at experiment start: `18592eef336ffc7c2b6b34d8ac489843f5274583`.
- `tests/test_rules.py` blob: `ed42acb8c21843676028ccd8c2b9ecc776ad2154`.
- production `rules.py` blob: `4e2c7ebb1a7866d941fc2570757e64098359413a`.
- production `policy.py` blob: `cdd7c248b50660c0d2ed93db0f351e3c0630f67f`.
- canonical behaviorally relevant policy SHA-256: `88f007c96f3acf63a191556fe7fa46b80b37e9fcb5224ec1e90fb626a061104d`.
- preregistration commit: `11dca0384aeb7a8166bded0424624807f52ab5f5`.
- RC2-A / PR #16 frozen FAILED head: `96c55fd4721b66cf138d89f52e262696ba6b6c01`.
- RC2-A2 / PR #19 head: `a148191927074de34537d0e7bc5cc22d6fa0432f`, disposition `INCONCLUSIVE`.
- RC2-B / PR #20 tested head: `8c80f8ab9a08f209d3bf91a52e9621b8b2968694`; disposed claim that tested RC2-A obligations require reopening Contract B is `FALSIFIED` for those tested needs only.

No Contract-B change was made or justified by RC2-C.

## Preserved deviations

### Deviation 001 — import-path apparatus failure

First code-bearing head `08392cf3ed9e7ce5d30ed2e4ce025089335ca690`, workflow run `33182944946`, job `98888539343`: **FAILED before scientific execution**.

Frozen identity/no-`src` mutation checks passed. The probe then failed with `ModuleNotFoundError` because it was invoked as a file path and could not import its own research package. No scientific control ran and no receipt was produced. The exact failure and one-line module-invocation correction are preserved in `docs/research/deviation-contract-c-rc2-c-001-import-path.md`.

### Deviation 002 — negative fixture was not output-invariant

Head `769fe5602c6ca8206dead2bd62f7cd6f73c9381d`, workflow run `33183144828`, job `98889222521`: **FAILED scientifically, 6/7 controls passed**.

Frozen artifact:

- artifact `9690557500`;
- digest `sha256:02297c5a05824490efafcc095c57f7098fe733dd3b400e7364ac66edf119f8c7`.

The original seam, causal removal, both fail-closed controls, policy identity, and causal-attribution distinction passed. The irrelevant-state negative control failed because the fixture nominated the unrelated item as a support candidate. Production correctly retained that candidate in `ClaimAssessment.candidate_evidence`, so the complete production output changed even though the item was not falsely recorded as causal. The artifact explicitly recorded `falsely_recorded_causal: false` and `production_output_unchanged: false`.

The correction preserved the stronger preregistered acceptance criterion and changed only the negative fixture: the unrelated source/excerpt remained real supplied evidence-world state but was not nominated into the candidate set. The failed run and artifact remain predecessor evidence. Full record: `docs/research/deviation-contract-c-rc2-c-002-negative-fixture.md`.

## Decisive corrected execution

Research head: `1ee52f2072d324a9e2360800cc8c3e6bd3d4d789`.

Dedicated workflow:

- run `33183532960`;
- job `98890534143`;
- result: **SUCCESS**;
- artifact `9690709607`;
- artifact digest `sha256:4600762f88a1bb2b4515b18afb473641b3847d46f6764bd2608d54ee62bdea9f`.

All frozen production identity checks and `git diff ... -- src/` passed before the probe. The probe reported all seven preregistered controls `true`, and the independent research test suite passed `3 passed`.

## Observed receipt

### Original production seam

Production input retained the frozen claim and support state plus one counterevidence context.

Observed production result:

- support signal: `0.85`;
- final verdict: `overstated`;
- terminal branch: `overstated_rule_family`;
- emitted rule codes: `counterevidence_present`, `future_certainty`, `overconfident_wording`.

The compact receipt classified:

- `overconfident_wording`, rule ID `flag-a54854636b92`: causal to the overstatement branch;
- `future_certainty`, rule ID `flag-b775df53af63`: causal to the overstatement branch;
- `counterevidence_present`, rule ID `flag-91ffc8bfd394`: `residual_after_overstated_branch`.

For each causal overstatement rule the receipt preserved two dependency edges:

1. `state:claim_trigger:guarantees -> rule:<id>` with relation `required_lexical_trigger`;
2. `state:counterevidence_contexts_nonempty -> rule:<id>` with relation `causes_absolute_wording_trigger_true`.

The production helper short-circuits on the non-empty counter-context collection. The receipt therefore truthfully records:

- direct-support evidence was available;
- `direct_support_refs_examined_by_trigger` was empty on this execution;
- the counterevidence collection presence was examined;
- individual counterevidence payloads were not examined by this trigger.

This avoids laundering semantic content into a causal claim when production only tested collection state.

### Causal-removal mutation

Only counterevidence state was removed. Claim, direct evidence and support candidate score `1.0` remained fixed.

Observed production result:

- support signal: `1.0`;
- final verdict: `supported`;
- terminal branch: `supported_score_branch`;
- no rule flags;
- no evidence-to-rule dependency edges.

The result therefore discriminates terminal replay from causal contribution: the counterevidence collection state was necessary for these two overstatement rule emissions on the frozen seam.

### Irrelevant-state negative control

After the recorded fixture correction, an unrelated source/excerpt was present in the supplied evidence bundle but absent from the candidate set.

Observed:

- complete production `ClaimAssessment` remained unchanged;
- unrelated evidence was not recorded as causal.

### Missing-dependency fail closed

An independent validator imports no CAL production code.

Removing only the counterevidence dependency edges while retaining the reported `overstated` result caused independent rejection:

- `missing counterevidence dependency for flag-a54854636b92`;
- `missing counterevidence dependency for flag-b775df53af63`.

Removing the trigger-condition records caused independent rejection:

- `missing trigger condition for flag-a54854636b92`;
- `missing trigger condition for flag-b775df53af63`.

The validator did not silently reconstruct the missing cause from private CAL semantics.

### Policy identity

Mutating only `overstated_detection` from `true` to `false` retained human-readable `config_id == cal-rules-v1.2.0` but changed canonical policy hash:

- baseline: `88f007c96f3acf63a191556fe7fa46b80b37e9fcb5224ec1e90fb626a061104d`;
- mutated: `9f1bbb612ace843bba6b7425c7e3b15d546cf8571ab53fd8006683e5f41272ce`.

On the same evidence state, production then returned `partially_supported` with only `counterevidence_present`. This independently confirms PR #19's finding that config name alone is insufficient attribution identity.

## Preregistered control matrix

| Control | Result | Observation |
|---|---|---|
| Frozen original production vector | PASS | `overstated`, signal `0.85`, exact three rule codes preserved |
| Causal-removal mutation | PASS | removing only counterevidence changed `overstated -> supported`, removed dependency edges |
| Irrelevant-state negative | PASS after recorded fixture correction | complete production output unchanged; unrelated source not causal |
| Missing dependency fail closed | PASS | independent validator rejected receipt with dependency edges removed |
| Missing trigger fail closed | PASS | independent validator rejected receipt with trigger state removed |
| Policy identity | PASS | same config name, different canonical policy hash, different production behavior |
| Causal-attribution distinction | PASS | full receipt identifies counterevidence-dependent rules; terminal-only receipt cannot |

## Competing explanations

### 1. A small evidence-to-rule dependency receipt is sufficient

**Supported for this seam.** No new epistemic judgment was needed. The receipt mechanically materialized production-observed state, named rule outputs, exact policy identity and dependency edges sufficient for an independent validator to check the attributable chain.

### 2. Hidden/unretained production state makes exact attribution impossible without production instrumentation

**Falsified for this seam.** The research apparatus could materialize and independently validate the observed dependency without changing `src/` or production semantics. This does not prove every CAL rule family is equally observable.

### 3. Several causal bases may be valid and multiplicity must be preserved

**Unknown / untested.** The frozen seam contains one counterevidence candidate. RC2-C does not establish how the receipt should represent multiple independently sufficient counterevidence items, co-sufficient rule triggers, or alternative causal bases. A broader experiment must test multiplicity rather than infer uniqueness.

### 4. Exact causal attribution is unnecessary because deterministic replay is sufficient

**Weakened for an independently attributable producer receipt.** The terminal-only representation cannot establish which overstatement rules depended on counterevidence presence. To recover that relation, a downstream consumer would have to re-execute private CAL rule semantics. The lost distinction is therefore concrete: `counterevidence caused these rule emissions` versus `counterevidence was merely co-present residual state`.

This does not establish that every downstream use requires causal attribution. It establishes that any Contract-C use claiming an independently attributable contribution basis cannot recover this demonstrated distinction from terminal replay alone.

## Primary research disposition

**SUPPORTED FOR PROMOTION**

This disposition is strictly bounded: the compact dependency-receipt mechanism is justified for the **next broader CAL rule-family attribution experiment**. It does not authorize production instrumentation, `ClaimAssessment` changes, Contract C, a Contract-C version, Consumer B, Decision Engine behavior, or a Contract-B change.

## Apparatus PR #13 gate

**Do not resume the producer-sufficiency gate yet.** The narrow seam survived, but PR #19's broader exact-attribution blocker is not discharged by one rule family. The smallest next CAL experiment is a broader rule-family attribution sweep that reuses this mechanism across distinct production branches and explicitly includes multiplicity/co-sufficient-basis controls.

Minimum next discriminators should include:

- at least one non-absolute-wording rule family with a different trigger shape;
- an existing score/counterevidence branch where scalar contribution and rule contribution interact;
- multiple counterevidence or co-sufficient causal inputs so the receipt must preserve multiplicity rather than invent one winner;
- the same independent fail-closed validator boundary and canonical policy binding.

Only after that broader CAL attribution experiment survives should Apparatus #13 reconsider its producer-sufficiency gate.

## Production impact

None. No file under `src/` changed. No Contract B, Contract-C schema/version, Decision Engine, Consumer B, or production CAL semantic was changed.