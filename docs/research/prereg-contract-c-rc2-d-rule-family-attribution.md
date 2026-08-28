# Contract C RC2-D — Rule-Family Attribution and Co-Sufficient Basis Sweep

## Task class

Draft Research experiment. Production impact: none.

This experiment asks whether the compact causal-attribution mechanism supported by CAL PR #21 on one absolute-wording/counterevidence seam generalizes across materially different current CAL v0.2 rule/branch families, and whether mutation evidence can be represented without inventing unique causes when production admits multiple sufficient or jointly required bases.

Success authorizes only reconsideration of the bounded producer-information-sufficiency question on `camerontjs-dot/apparatus-contracts#13`. It does not authorize Contract C, a Contract-C schema/version, Consumer B, or production instrumentation.

## Frozen authority and predecessor state

Durable governance is external to this branch. Live GitHub and immutable artifacts are authoritative for experiment state.

Verified predecessor state before branch creation:

- CAL PR #21: closed/unmerged, primary disposition `SUPPORTED FOR PROMOTION`, strictly bounded to the frozen absolute-wording/counterevidence seam.
- CAL PR #19: `INCONCLUSIVE`; deterministic verdict replay survived but exact evidence-to-rule causal attribution remained unresolved.
- CAL PR #20: `FALSIFIED` for the bounded claim that the missing RC2-A obligations require reopening Contract B.
- Apparatus PR #13: open Draft Research PR and blocked pending broader CAL attribution/multiplicity evidence.
- Apparatus issue #8: living state records CAL #21 as terminal and requires this broader attribution sweep before reassessing #13.

## Frozen production identities

- research base / live CAL `main` at branch creation: `18592eef336ffc7c2b6b34d8ac489843f5274583`;
- production-semantic SHA: `33a928db97316a3652d57df9cafb8ca240305233`;
- the only delta from the production-semantic SHA to the research base is `.github/pull_request_template.md`;
- `tests/test_rules.py` blob: `ed42acb8c21843676028ccd8c2b9ecc776ad2154`;
- `src/claim_audit_lab/rules.py` blob: `4e2c7ebb1a7866d941fc2570757e64098359413a`;
- `src/claim_audit_lab/policy.py` blob: `cdd7c248b50660c0d2ed93db0f351e3c0630f67f`;
- canonical behaviorally relevant policy SHA-256: `88f007c96f3acf63a191556fe7fa46b80b37e9fcb5224ec1e90fb626a061104d`.

The policy hash is over recursively key-sorted compact JSON plus one trailing LF. `config_id` alone is explicitly insufficient identity.

## Claim under review

A compact research receipt derived only from legitimate frozen CAL production state plus observed causal interventions can preserve, where applicable:

`evidence/input state -> trigger state -> rule/policy evaluation -> emitted rule result -> terminal branch`

while distinguishing:

- causally necessary state;
- independently sufficient alternative bases;
- jointly sufficient / co-required bases;
- terminally residual state;
- merely present/non-deciding state;
- tied/co-maximal computational contributors;
- generic rich assessment families that production did not execute and therefore remain `not_performed`.

The receipt may report a causal classification only when the preregistered production mutations support it. Field population or branch replay alone is not causal evidence.

## Heaviest assumption

The main assumption under test is that one receipt vocabulary can describe materially different CAL rule/branch families without hiding incompatible semantics or inventing causal structure.

## Frozen existing production vectors

The exact source bytes are frozen by the `tests/test_rules.py` blob above. The decisive sweep will replay these existing vectors by name where they discriminate the question:

1. `test_frozen_support_threshold_boundaries` — threshold/scalar terminal branch and no-rule path.
2. `test_credential_claim_without_source_needs_source` — direct-support-presence-dependent explicit `needs_source` rule override.
3. `test_low_reliability_only_support_lowers_assessment` — rule-driven limiting state.
4. `test_unclassified_claim_is_not_checkable` — governed-family early return with no rule family executed.
5. `test_linked_counterevidence_restores_absolute_wording_flags` — RC2-C predecessor seam used only for the jointly-required control and predecessor parity.
6. `test_counterevidence_reduces_signal_and_prevents_supported_verdict` — scalar counterevidence/residual-rule distinction where useful.

A derived low-score low-reliability control is frozen from the same capability vector with only candidate score changed to `0.60`; it is used to test a residual emitted flag whose removal must not change the `partially_supported` terminal branch.

## Frozen multiplicity controls

These are research-only perturbations of existing production semantics, not new production behavior.

### M1 — independently sufficient + tied/co-maximal support alternatives

Claim: `The tool can generate audit summaries.` / `capability`.

Two distinct evidence sources each contain exactly `The tool can generate audit summaries.`. Two candidates are both score `0.80`, high reliability, same frozen date class, distinct source/excerpt IDs.

Required production observations:

- A+B -> `supported`;
- A alone -> `supported`;
- B alone -> `supported`;
- neither -> `unsupported`;
- A and B are both scalar co-maxima in A+B.

If observed, the receipt must represent A and B as independent sufficient alternatives and preserve the co-maximal set. It must not represent A+B as a jointly necessary pair or choose one arbitrary winner.

### M2 — jointly sufficient absolute-wording basis

Baseline is the frozen PR #21 seam:

- claim: `The tool guarantees audit summaries.` / `prediction`;
- direct evidence repeats that wording at score `1.0`;
- counterevidence candidate score `0.5`;
- policy unchanged.

Interventions:

- lexical trigger present, counterevidence absent;
- lexical trigger absent (`The tool can generate audit summaries.`), counterevidence present;
- both lexical trigger and counterevidence absent.

The target result is the `overstated` branch. Support for a joint classification requires baseline -> `overstated`, while neither isolated mutable state produces `overstated` under the frozen remaining conditions.

This control explicitly tests the conjunction already implicit in RC2-C rather than assuming two dependency edges are equivalent to a joint causal statement.

### M3 — redundant/non-deciding emitted rule

Claim/evidence are the capability direct-support vector with candidate score `0.60` and low source reliability. Baseline is expected to emit `low_reliability_only` while the scalar threshold already yields `partially_supported`.

Intervention: change only source/candidate reliability to high while preserving text, IDs, score, policy and evidence count.

Support for residual classification requires the rule to disappear while the terminal verdict remains `partially_supported`.

## Structurally distinct family set

The decisive set is intentionally small:

- `threshold_no_rule`: scalar threshold branch, no rule firing;
- `credential_needs_source`: explicit priority rule override with evidence/direct-support presence as trigger state;
- `low_reliability_residual`: emitted rule present but terminally non-deciding under a lower scalar branch;
- `unclassified_not_checkable`: early return before governed rule-family execution;
- `absolute_wording_joint`: priority overstatement branch with a jointly required mutable trigger/counterevidence basis;
- `tied_independent_support`: independent sufficient alternatives plus tied/co-maximal scalar state.

If a requested causal shape is not representable by current production semantics under these frozen perturbations, record it unavailable rather than changing production or inventing a semantic judgment.

## Generic assessment-state rule

For every case, the research receipt will explicitly carry these generic rich assessment families as `not_performed`:

- eligibility;
- semantic validity;
- aperture/completeness;
- temporal/applicability;
- citation.

This is not a new assessment. CAL PR #17 established that the current locked-B v0.2 path does not perform these generic stages; narrow production rules must remain narrow named rule receipts rather than being relabeled as generic assessments.

## Receipt and validator design

Research machinery must remain outside `src/`.

The producer-side probe may import CAL production code to observe actual execution and run causal mutations.

A separate validator must import no `claim_audit_lab` production implementation. It receives receipt bytes only and checks:

- canonical policy hash/config binding;
- required terminal, rule, trigger, mutation and assessment-state fields;
- mutation logic supporting the declared causal class;
- independent alternatives are not encoded as joint necessity;
- joint classifications have baseline target outcome and isolated-member non-target outcomes;
- residual classifications show removal without target-branch change;
- tied/co-maximal members are not collapsed;
- generic assessment families are explicitly `not_performed`;
- missing required state fails closed.

The validator validates the internal causal claim against frozen observed mutation outcomes. It does not independently re-run CAL and must not be described as a clean-room Consumer B.

## Required mutations

Across the selected cases, execute the smallest available interventions needed to discriminate attribution:

- remove one hypothesized causal input/candidate;
- alter only a trigger condition where required;
- toggle a behaviorally relevant policy switch while keeping `config_id` fixed;
- remove required receipt state/edges and require independent validator rejection;
- add unrelated evidence-world state outside the candidate set and verify no false causal edge;
- preserve/remove a residual emitted flag while confirming terminal invariance;
- preserve all tied scalar maxima.

## Policy-identity control

At least one case must be rerun with a behaviorally relevant policy mutation while `config_id == cal-rules-v1.2.0` remains unchanged. The canonical policy hash must change and the affected production result/rule behavior must change. A receipt retaining the baseline hash for the mutated behavior must fail validation.

## Acceptance criteria

Assign support only if all of the following survive on the frozen decisive head:

1. every selected structurally distinct family executes as preregistered or is explicitly recorded unavailable for a production-semantic reason;
2. receipt causal classifications agree with the actual mutation outcomes;
3. residual/non-deciding state is not promoted into a terminal causal basis;
4. every available multiplicity shape is represented truthfully;
5. exact behaviorally relevant policy identity detects a same-`config_id` behavior mutation;
6. the five generic rich assessment families remain `not_performed`;
7. deleting required receipt state causes the independent validator to fail closed;
8. unrelated evidence-world state does not create false dependency edges;
9. `src/`, production verdict semantics and Contract-B behavior remain unchanged;
10. failed/deviating runs and unavailable shapes are preserved.

A requested multiplicity shape that current production genuinely cannot realize is an unresolved evidence requirement, not permission to manufacture it.

## Falsifiers

Use an allowed terminal disposition rather than repairing the theory if the decisive evidence shows any material case where:

- branch replay succeeds but causal mutation contradicts the receipt attribution;
- multiple sufficient bases require inventing one winner;
- a claimed joint basis is not actually joint under intervention;
- a receipt requires information CAL does not legitimately possess;
- behaviorally distinct policy states remain receipt-identical;
- attribution requires a new epistemic judgment;
- materially different rule families need incompatible causal semantics that the common receipt vocabulary hides;
- available production vectors/perturbations are insufficient to test the generalization.

## Allowed terminal dispositions

Exactly one:

- `SUPPORTED FOR PROMOTION`
- `FALSIFIED`
- `INCONCLUSIVE`
- `SUPERSEDED`

`SUPPORTED FOR PROMOTION` means only that the tested attribution mechanism is sufficiently supported across this frozen rule-family/multiplicity scope to resume the bounded Apparatus #13 producer-sufficiency question.

## Hard boundaries

Do not modify production `src/`, thresholds or policy to make attribution easier; reopen Contract B; assign a Contract-C schema/version; create a production exporter; run Consumer B; change Decision Engine behavior; collapse unknown/not-performed/failed states; merge this experimental implementation as production; or erase negative evidence.
