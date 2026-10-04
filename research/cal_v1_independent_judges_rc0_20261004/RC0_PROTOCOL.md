# RC0 protocol: #206

Classification: research architecture discriminator. No production change. Preparation self-tests do not execute CAL or semantic judges.

## Frozen control and allowed work

Control product `64b6c7702696c851057c1cf0b2c105b1c81db543`; tree `62c32ab15489e6c3b20e63efb500c0fa26d0084d`; semantic `caa0048f8f511ec3c4aa1ce713766f2219a04bc1`. Research candidate files belong in a new subtree, separate from this frozen kit. All `src/`, existing tests/workflows, package metadata and prior apparatus remain unchanged. Current production main is not silently repinned.

Verify `FREEZE.json` before implementation. First run the apparatus self-test. Define and commit candidate design, judge information apertures, bounded initial catalogue and semantic case expectations before candidate execution. Freeze actual candidate and model/prompt/config bytes before the decisive run. Preserve all failures and classify apparatus changes in separately identified successors.

## Mechanical adapter interface

The frozen `contract_tests.py` accepts a module path that exports:

    collect(raw: bytes, lanes: list[dict]) -> list[dict]
    synthesize(raw: bytes, receipts: list[dict], policy: dict) -> dict

`collect` invokes each lane's `call(raw)` with the identical original immutable bytes. A lane descriptor has `id`, `role` and `call`. Snapshot each receipt before invoking another callback; one callback's subsequent mutable-object edits must not alter already captured conclusions. Exceptions create explicit failed/unknown receipts without starving other lanes. Callback wiring tests do not establish OS/provider isolation.

Toy receipt fields:

- `process_id`, `input_sha256` (lowercase unprefixed SHA-256 of exact bytes)
- `execution`: completed or failed
- `applicability`: applicable, not_applicable or unknown
- `role`: relation or guard
- relation `conclusion`: supports, refutes, unresolved or not_applicable
- guard `conclusion`: satisfied, violated, unresolved or not_applicable
- `warrant`: qualified or unqualified
- `material_loss`: boolean

Extra fields such as `claimed_weight` cannot change authority. In this test fixture, warrant and applicability are supplied oracle facts. In the real candidate they require receipts and independent qualification, not a judge self-certifying itself.

Toy policy is a fixed per-process map of role, rational weight, dependence group and required flag plus a strictly positive rational threshold. This is deliberately not a production schema. The exact mechanics tested are:

- exact process set, unique identities, exact original-input binding and valid vocabulary;
- zero decision weight for failed/unknown/not-applicable/unqualified/lossy/unresolved rows, with reasons retained;
- required uncertainty blocks; genuinely not-applicable required rows do not;
- qualified required guard violation blocks;
- optional irrelevant or unresolved lanes do not veto sufficient qualified evidence;
- weight zero contributes no directional vote;
- same-dependence-group weight is capped at the maximum member weight per direction;
- simultaneously positive qualified support and refutation produce material conflict, not majority resolution;
- no support/refutation reaches a deciding result below the synthetic threshold;
- policy identity changes when weights/profile change, while sealed input receipts remain unchanged;
- all receipts, exclusions and blockers survive; fixed-receipt synthesis is order-invariant and deterministic.

The tiny profile tests implementability of declared weight behavior, not whether those numbers are proper weights for natural claims. It does not prove exhaustive input validation. The actual envelope/state model must additionally separate unsupported, not-run, timeout, failed execution and completed abstention. A missing process is never silently not applicable.

## Apparatus validation

Thirty tests exercise the adapter. Seven seeded defective systems must fail their intended checks: early routing; shared lossy fan-out; hidden failures; majority over material conflict; ignored scope guard; cloned-vote amplification; always-abstain behavior. If any intended mutant survives, the kit is not a qualified mechanical discriminator.

The included `FixtureProbe` is a test oracle, not a candidate. Do not import/subclass/copy it and report independent implementation. Write a separate adapter. No schema receipt or test count alone establishes input isolation or epistemic accuracy.

## Actual semantic vertical, required in addition

Use at least these roles across the same per-claim catalogue:

1. Exact frozen kernel as a bounded legacy lane, with its authoring limits recorded locally rather than as a global gate.
2. Independently implemented original-text claim/source relation judge, capable of testing at least one scoped seed outside the old authoring grammar without dropping its scope.
3. Independent scope/polarity/measure assessment. It returns a constraint finding, not an automatic whole-claim vote.
4. Direct event-order analysis under the same dispatch procedure on comparison and event claims.

Method diversity is not proven by filenames. Record shared model/parser/training/source dependencies. A role can use deterministic logic or a model, but exact instrument/model/prompt/config and raw outputs must be retained. Do not assume access to a paid provider or equate an unavailable model with successful evaluation. Use existing available local instruments when adequate, otherwise report the instrument boundary.

First interpret claim semantics from claim-only input; evidence cannot silently select a different intended claim. Independently interpret evidence and compare it against that interpretation, retaining ambiguity. No process gets another lane's target or conclusion before its own first-pass receipt is sealed. A later reconciliation pass is explicitly labeled and cannot replace the first pass in the record.

`SEMANTIC_CASES.json` provides synthetic exposed seeds, not a gold benchmark or blind test. Freeze full anticipated local dimensions and semantic labels before execution. Scope/property/time mismatch is unresolved or non-applicable to the requested claim, not automatic refutation. Exact same-scope opposite evidence can refute. Preserve missing-evidence and conflict abstention.

Minimum semantic result for RC0 architecture support: zero wrong deciding outcomes on the frozen seeds, preserve required ambiguity/conflict/missing-evidence abstentions, and at least one correct deciding result outside the legacy authoring grammar that demonstrably preserves its material scope. An all-abstain candidate cannot pass. Kernel-only successes do not establish the new vertical.

## Causal comparison, not just a better score

Run three separately identified arms:

- A: exact routed kernel baseline, with authoring failures explicit.
- B: the candidate's same judge implementations and budgets, but deliberately supplied a shared lossy interpretation in place of originals. This is a weak counterfactual, never the production design.
- C: original-input isolated candidate.

Where A and C differ in both representation and instruments, label attribution confounded; do not claim topology alone caused a coverage gain. The B/C paired comparison isolates loss placement with identical judges/evidence as closely as possible. Record actual token/context/model/call budgets and execution order. If deterministic specialized checks suffice, record no model was used.

Required non-interference probes: change one lane's private normalization/summary, one lane's output, and lane order. Other first-pass outputs must remain unchanged under fixed inputs/instruments. Probe process crashes/timeouts, shared mutable objects, stale context, undeclared consumed evidence, source/model clones, false self-relevance and material dissent. A receipt claiming the right input hash is insufficient: inspect actual worker/provider inputs and access boundaries. Token truncation and shared caches must be visible.

## Usefulness and abstention report

Report separately: authoring refusal, unsupported family/form, measurement miss, scope/interpretation mismatch, missing evidence/admission, material conflict, invalid provenance, process failure and synthesis insufficiency. Include correct-deciding count over all eligible claims, error count among decisions, per-family/mixed-dimension coverage, safe refusal rate and cost. Do not turn non-applicability/refusal into semantic correctness.

#193's fourteen claims and #203's twenty-six claims are exposed developmental evidence. Retain exact source/passage text for any replay; do not paraphrase to fit the old grammar. A fresh source-disjoint cohort and empirical calibration of weights are the next phases, not a claimed result here. Freeze development/calibration/test split and thresholds before revealing held-out results.

## Qualification and handoff

Run new mechanical tests plus actual isolation and semantic tests, preserved polarity/conformance regressions and maintained project checks as their required dependencies allow. Full maintained checks require the declared extras; missing models/dependencies/skips must be explicit, not counted as coverage. Record exact commands, exit codes, stdout/stderr and file hashes. Validate output absence after rejected arms, rather than merely logging a proposed stop.

Publish an append-only research evidence record with candidate commit/tree, apparatus freeze, instrument pins, all arms and first failures. Raw evidence must be durably reachable, not only summarized in an issue comment. No public secrets, private source text, local absolute paths or model credentials. The original pressure/source-redaction history is not rewritten.

Choose the exact #206 disposition. Mechanical support without semantic usefulness is `MECHANICS_SUPPORTED_SEMANTIC_UTILITY_UNESTABLISHED`. It is not V1 readiness. Update #206/#205/#185 and Apparatus #137; keep research PR Draft/unmerged. Stop before actual Contract C changes, broad family promotion, release or consumer migration.
