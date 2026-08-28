# Contract C RC2-D — Rule-Family Attribution and Co-Sufficient Basis Sweep

## Terminal result

**SUPPORTED FOR PROMOTION**

This disposition is strictly bounded to the frozen CAL v0.2 production-semantic state and the six examined rule/branch families and multiplicity controls described below.

It means only that the tested causal-attribution receipt mechanism is sufficiently supported across this frozen examined scope to resume the bounded producer-information-sufficiency question in `camerontjs-dot/apparatus-contracts#13`.

It does **not** establish Contract C, define a Contract-C schema or version, authorize a production exporter, establish Consumer B reproducibility, establish Decision Engine behavior, or reopen Contract B.

## A. Frozen identities

### Production and policy

- CAL live `main` at experiment start: `18592eef336ffc7c2b6b34d8ac489843f5274583`.
- frozen production-semantic SHA: `33a928db97316a3652d57df9cafb8ca240305233`.
- delta from semantic SHA to experiment-start `main`: `.github/pull_request_template.md` only.
- `tests/test_rules.py` blob: `ed42acb8c21843676028ccd8c2b9ecc776ad2154`.
- `src/claim_audit_lab/rules.py` blob: `4e2c7ebb1a7866d941fc2570757e64098359413a`.
- `src/claim_audit_lab/policy.py` blob: `cdd7c248b50660c0d2ed93db0f351e3c0630f67f`.
- frozen canonical behaviorally relevant policy SHA-256: `88f007c96f3acf63a191556fe7fa46b80b37e9fcb5224ec1e90fb626a061104d`.
- human-readable policy `config_id`: `cal-rules-v1.2.0`, explicitly not sufficient as the policy identity by itself.

### Preregistration and execution

- research PR: CAL #22, Draft Research PR.
- branch: `research/contract-c-rule-family-attribution-rc2-d`.
- preregistration commit: `08394c797f23035f76c719931ff59ddb66ec20ee`.
- decisive execution head: `967fb164b7087a0d03bdd170b5b3a5b63568c6f7`.
- decisive workflow: `Contract C RC2-D rule-family attribution`.
- decisive run: `33193182042`.
- decisive job: `98923586037`.
- decisive artifact: `9694629616`, `contract-c-rc2-d-rule-family-attribution`.
- decisive artifact ZIP SHA-256: `7e8a133e49fd66186bb74cb1c9beeaed7733e7c9793798bb04d48e2ee3e09c3f`.
- decisive `attribution-sweep.json` SHA-256: `a953a14b8bf9a5bd9cf9060e7fb58c868df9b15c8b578d88f13a1090c4eca5fa`.

The decisive receipt SHA is identical to the receipts emitted before each of the two preserved hygiene-only failed runs. The formatting corrections therefore did not change the scientific output.

## B. Rule-family map

### 1. `threshold_no_rule`

Production form: scalar threshold branch with no rule firing.

- input: one direct-support candidate at score `0.80` for a capability claim;
- trigger/evaluation: support-signal maximum `0.80` equals the frozen sourced-support threshold `0.80`;
- emitted rules: none;
- terminal branch: `supported_score_branch` / `supported`;
- causal mutation: remove the candidate;
- mutation outcome: support signal `0.0`, `unsupported`;
- attribution: the candidate is a single necessary causal input for the target branch in this frozen case;
- irrelevant-state control: adding an unrelated source to the evidence world while leaving the candidate set unchanged produced byte-equivalent assessment output and no dependency edge for that source;
- residual/non-deciding state: none in the target receipt.

### 2. `credential_needs_source`

Production form: explicit priority rule override dependent on claim type, policy, and absence of direct support context.

- input/trigger: credential claim with `direct_contexts_empty = true` and `needs_source_detection = true`;
- emitted rule: `credential_missing_source`;
- terminal branch: `needs_source_rule_family` / `needs_source`;
- causal mutation: add legitimate direct-support candidate/context;
- mutation outcome: rule disappears and verdict becomes `supported` with support signal `0.90`;
- policy control: with `config_id` unchanged, set `needs_source_detection = false`; the policy hash changes and verdict becomes `unsupported`;
- receipt representation: direct-context absence -> rule emission -> priority terminal override;
- residual/non-deciding state: none in the target receipt.

### 3. `low_reliability_residual`

Production form: emitted limiting rule that is present but non-deciding because the scalar threshold already fixes the terminal branch.

- input: direct-support candidate at score `0.60` with low reliability;
- trigger: all direct support low/unknown;
- emitted rule: `low_reliability_only`;
- terminal branch: `support_between_thresholds` / `partially_supported`;
- causal mutation: change only reliability from low to high while preserving score/text/IDs/policy;
- mutation outcome: `low_reliability_only` disappears but terminal verdict remains `partially_supported` at support signal `0.60`;
- receipt representation: scalar evidence -> threshold branch; low-reliability state -> emitted residual rule;
- residual/non-deciding state: `rule:low_reliability_only` explicitly classified residual rather than promoted into the terminal causal basis.

### 4. `unclassified_not_checkable`

Production form: early return before governed rule-family execution.

- input/trigger: `claim_type = unclassified`;
- emitted rules: none;
- terminal branch: `unclassified_early_return` / `not_checkable`;
- causal mutation: change only the claim type to governed `capability` with the empty evidence state preserved;
- mutation outcome: terminal result becomes `needs_source`;
- receipt representation: explicit unclassified state -> early return;
- generic assessment state: eligibility, semantic validity, aperture/completeness, temporal/applicability, and citation remain `not_performed` rather than being inferred from the early return.

### 5. `absolute_wording_joint`

Production form: priority overstatement rule family requiring an absolute lexical trigger and counter-context presence under the frozen policy.

Baseline:

- claim contains `guarantees`;
- direct-support score `1.0`;
- counterevidence candidate present at score `0.5`;
- support signal `0.85`;
- emitted rules: `future_certainty`, `overconfident_wording`, and `counterevidence_present`;
- terminal branch: `overstated_rule_family` / `overstated`.

Mutations:

- lexical trigger present, counter-context absent -> `supported`, no rules;
- counter-context present, lexical trigger absent -> `partially_supported`, only `counterevidence_present`;
- neither mutable contributor present -> `supported`, no rules;
- same `config_id`, `overstated_detection = false` -> policy hash changes, terminal result becomes `partially_supported` with only `counterevidence_present`.

Receipt representation:

- `state:absolute_lexical_trigger` and `state:counterevidence_contexts_nonempty` are a jointly required/co-sufficient basis for the target `overstated` branch under the frozen remaining state;
- `future_certainty` and `overconfident_wording` are causal rule results for that terminal family;
- `counterevidence_present` is retained but classified as terminally residual after the higher-priority overstatement branch.

This preserves the RC2-C observation that the tested helper reacts to counter-context collection presence, without pretending it inspected individual counterevidence payload content.

### 6. `tied_independent_support`

Production form: scalar threshold branch with two tied/co-maximal support candidates.

Baseline:

- A score `0.80` and B score `0.80`;
- support signal `0.80`;
- terminal branch `supported_score_branch` / `supported`;
- no rule flags.

Mutations:

- A alone -> `supported`;
- B alone -> `supported`;
- neither -> `unsupported`.

Receipt representation:

- A and B are preserved as two independently sufficient alternatives;
- both are explicitly retained in the co-maximal contributor set;
- the receipt does not encode A+B as a jointly necessary pair and does not select an arbitrary winner.

## C. Multiplicity map

| Causal shape | Frozen case(s) | Observed classification |
| --- | --- | --- |
| Single necessary cause | `threshold_no_rule`, `credential_needs_source`, `unclassified_not_checkable` | tested |
| Independent sufficient alternatives | `tied_independent_support` | tested |
| Jointly sufficient / co-sufficient | `absolute_wording_joint` | tested within fixed surrounding state |
| Redundant / non-deciding | `low_reliability_residual`; also `counterevidence_present` is terminally residual after overstatement | tested |
| Co-maximal/tied state | `tied_independent_support` | tested and both contributors preserved |
| Unavailable requested multiplicity shape | none among the preregistered required shapes | none recorded |

## D. Observed evidence

Direct outputs from the decisive workflow:

1. frozen `tests/test_rules.py`, `rules.py`, and `policy.py` blob checks succeeded;
2. `git diff --exit-code 33a928db97316a3652d57df9cafb8ca240305233 -- src/` succeeded;
3. all six preregistered family cases executed;
4. the sweep reported `all_controls_passed: true`;
5. all ten encoded controls returned `true`;
6. independent research assertions completed `6 passed`;
7. Ruff check passed;
8. Ruff format check reported all four research files already formatted;
9. the decisive receipt SHA-256 was `a953a14b8bf9a5bd9cf9060e7fb58c868df9b15c8b578d88f13a1090c4eca5fa`;
10. no production `src/` semantics changed.

The ten controls that directly passed were:

- all generic assessments explicitly `not_performed`;
- false-independent theory rejected;
- false-joint theory rejected;
- irrelevant evidence-world state output-invariant and non-causal;
- missing dependency edges fail closed;
- missing generic assessment fails closed;
- policy hash mismatch fails closed;
- same-`config_id` policy mutations change both hash and behavior;
- full receipt suite validates;
- tied co-maxima are preserved.

Negative validator observations were also explicit:

- deleting the `citation` generic-assessment state produced `generic assessment missing: citation`;
- deleting dependency edges produced `dependency edges missing` and `causal member lacks dependency edge`;
- relabeling tied independent support as joint was rejected because each member alone still produced the target;
- relabeling the absolute-wording joint basis as independent was rejected because neither isolated member produced the target;
- retaining the baseline hash with a behaviorally mutated canonical policy produced `policy hash mismatch`.

## E. Inference

The observations support a bounded common attribution mechanism whose causal vocabulary is driven by intervention results rather than field presence or terminal replay alone.

Within the frozen examined CAL v0.2 scope, one receipt family can truthfully distinguish:

- a single necessary cause;
- independent sufficient alternatives;
- a jointly required/co-sufficient basis;
- residual emitted state that does not decide the terminal branch;
- tied/co-maximal contributors without arbitrary winner selection;
- generic assessment families that were not executed.

The results also support binding exact behaviorally relevant policy state, not merely `config_id`, because two same-`config_id` policy mutations changed behavior and changed the canonical policy hash.

This is enough to remove the specific RC2-C blocker that broader current-rule-family attribution and multiplicity were untested. It is not evidence that a production CAL exporter already possesses every field needed to emit such receipts. That separate producer-information-sufficiency question belongs to Apparatus #13.

## F. Falsified alternatives

The decisive mutations reject the following simpler receipt theories within the tested scope:

1. **Terminal replay alone establishes causal contribution.** It does not. The low-reliability rule can disappear while the terminal result remains unchanged.
2. **Two present contributors may be encoded as jointly necessary without interventions.** The tied support case falsifies that shortcut: each contributor alone is sufficient.
3. **A joint basis may be encoded as independent alternatives.** The absolute-wording control falsifies that shortcut: neither isolated mutable contributor produces `overstated`.
4. **A compact receipt may choose one arbitrary contributor among tied co-maxima.** The independent-support control requires both tied contributors to remain represented.
5. **Every emitted rule is terminally causal.** `low_reliability_only` and `counterevidence_present` provide counterexamples in the tested branch structures.
6. **`config_id` alone is sufficient policy identity.** Same-`config_id` behavior-changing policy mutations produced distinct canonical hashes and outcomes.

## G. Unknowns and bounds

The experiment does not establish:

- whether a future Contract-C production exporter can derive every supported receipt field from legitimately possessed CAL production state without new epistemic judgment or prohibited instrumentation;
- whether this causal vocabulary is complete for every CAL rule interaction, future policy, or future v0.2-compatible extension outside the six frozen cases;
- exhaustive/minimal causal graphs beyond the tested interventions;
- independent Consumer B reproduction from a Contract-C specification;
- a Contract-C schema, version, compatibility class, or canonical serialization;
- Decision Engine consumer sufficiency or downstream decision behavior;
- new generic eligibility, semantic-validity, aperture/completeness, temporal/applicability, or citation assessments;
- any reason to reopen Contract B.

The validator is implementation-independent from CAL production in the narrow sense that it imports no `claim_audit_lab` implementation. It is not a clean-room Consumer B and must not be cited as one.

## H. Terminal disposition

**SUPPORTED FOR PROMOTION**

Meaning only:

> The tested attribution mechanism is sufficiently supported across the frozen examined CAL rule-family/multiplicity scope to resume the bounded Apparatus #13 producer-sufficiency question.

## I. Apparatus #13 consequence

**APPARATUS CONTRACT-C PRODUCER-SUFFICIENCY MAY RESUME**

Evidence basis:

- the predecessor single-seam causal chain was reproduced as one member of a broader frozen sweep;
- materially different threshold, rule-override, residual-rule, early-return, tied-independent, and jointly required causal forms were discriminated by intervention;
- available multiplicity forms were represented without inventing a unique winner or promoting residual presence to causation;
- behaviorally relevant policy mutation was detected despite unchanged `config_id`;
- missing required receipt state failed closed;
- generic unperformed stages remained `not_performed`;
- production semantics remained unchanged.

This consequence reopens only the question of whether the producer has sufficient legitimate information to emit a bounded Contract-C result package. It does not answer that question in advance.

## J. GitHub mutations and preserved deviations

### Research record

- created branch `research/contract-c-rule-family-attribution-rc2-d` from `18592eef336ffc7c2b6b34d8ac489843f5274583`;
- opened CAL Draft Research PR #22;
- applied labels `research` and `experiment:preregistered` before terminal disposition;
- froze preregistration at `08394c797f23035f76c719931ff59ddb66ec20ee`;
- added research-only sweep, independent validator, assertions, and dedicated workflow outside production `src/`;
- no production source, policy threshold, Contract-B behavior, Contract-C version, exporter, Consumer B, or Decision Engine behavior was changed.

### Preserved deviation 001

First code-bearing run:

- head `3b3f37ed2948d990657badcf5efff5f8db7997f4`;
- run `33192646035`;
- job `98921758366`;
- artifact `9694405647`;
- receipt SHA-256 `a953a14b8bf9a5bd9cf9060e7fb58c868df9b15c8b578d88f13a1090c4eca5fa`;
- scientific controls and six assertions passed;
- workflow failed only eight Ruff lint/import-order/line-length findings;
- preserved in `docs/research/deviation-contract-c-rc2-d-001-code-hygiene.md`.

### Preserved deviation 002

Second run after the lint-only correction:

- head `d728a3008daea8cf9718d3bd9950c6fac7ae1d5a`;
- run `33192976575`;
- job `98922875829`;
- artifact `9694535862`;
- receipt SHA-256 remained `a953a14b8bf9a5bd9cf9060e7fb58c868df9b15c8b578d88f13a1090c4eca5fa`;
- scientific controls, six assertions, and `ruff check` passed;
- workflow failed only `ruff format --check` expression wrapping;
- preserved in `docs/research/deviation-contract-c-rc2-d-002-ruff-format.md`.

### Decisive execution

- decisive head `967fb164b7087a0d03bdd170b5b3a5b63568c6f7`;
- dedicated run `33193182042`: success;
- job `98923586037`: success;
- artifact `9694629616`;
- receipt SHA-256 remained `a953a14b8bf9a5bd9cf9060e7fb58c868df9b15c8b578d88f13a1090c4eca5fa`.

The failed runs remain part of the public evidence lineage. They were not rewritten as successful runs or removed.
