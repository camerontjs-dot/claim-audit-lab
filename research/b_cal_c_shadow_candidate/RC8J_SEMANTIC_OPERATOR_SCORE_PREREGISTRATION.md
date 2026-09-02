# RC8J Warranted Semantic-Operator Score Falsifier — Preregistration

Status: **Draft Research Infrastructure / stacked successor to PR #77**.

This experiment does not change RC8J, production CAL, Contract B, Contract C, Decision Engine policy, release state, or the existing CAL v1 relation-preserving decision model.

## Scientific question

When an already-constructed semantic atom has passed the frozen RC8J authority gate, can that `WARRANTED` state safely enter CAL's existing relation-preserving decision machinery without another authority-bearing decision-strength input?

More specifically:

> Does the existing `semantic_operator` contribution path require a scalar score that RC8J does not own or produce, such that an arbitrary caller-supplied scalar can manufacture the terminal proposition decision while warrant, evidence, channel, eligibility, semantic validity, aperture and thresholds remain fixed?

## Frozen parents

Projection parent:

- PR #77 accepted head: `57e59d8e5c565ff5e280357b322980e5c86b4cf2`;
- projection run: `33673594287`;
- artifact: `9863519617`;
- digest: `sha256:d5c649612f9a18471633ec0ddf50eb011bc17f7fd36988a44f9a8643fdb1a127`;
- disposition: `CONTRACT_C_1_0_HAS_ASSESSED_CONCLUSION_CAPACITY; RC8J_STATUS_ALONE_IS_NOT_A_PROPOSITION_CONCLUSION; NEXT_BLOCKER_IS_CAL_INTERNAL_AUTHORITY_TO_CONCLUSION_SEMANTICS`.

RC8J research authority:

- freeze commit: `8e75c6782bb95c3763d06230b9c5df2b6af44054`;
- candidate blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`;
- the accepted #76 seam proves the external frozen gate can be consumed with exact typed results;
- the frozen authority specification explicitly states that the gate is **not a confidence scorer** and returns only authority status + typed reason.

CAL relation-preserving decision machinery:

- production semantic base: `53f0885b111676794d1bd20e10b91aa58b07e9d4`;
- `src/claim_audit_lab/v1/decision_model.py` blob: `f0d9d3bc061d966ed9c8c16b3424b3dd5c3bb339`.

The module is additive/shadow machinery, not the released production verdict path. It already supports `origin="semantic_operator"` contributions and keeps support/refutation, eligibility, validity and aperture explicit.

## Existing behavior under test

For valid semantic-operator contributions, the frozen decision model uses each contribution's optional scalar `score` as decision strength:

- score absent -> `abstained / contribution_score_unmeasured`;
- score below the channel decision threshold -> abstain below threshold;
- score at or above threshold -> terminal `supported` or `contradicted` depending on the separately supplied channel;
- valid support + valid refutation -> `mixed_valid_evidence` abstention before scalar winner selection.

RC8J supplies none of:

- support/refutation channel;
- scalar decision score;
- calibrated relation probability;
- support/refutation threshold policy.

This experiment therefore treats channel, eligibility and aperture as explicit fixture stipulations so the scalar dependency can be isolated. They are not inferred from RC8J.

## Controlled fixture

Start from the accepted #76 fully bound typed seam control and require the real frozen RC8J evaluator to return exactly:

`WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED`.

Only then construct a research-only `semantic_operator` contribution in the unchanged CAL v1 decision model.

Freeze these variables across the scalar mutation series:

- exact RC8J warrant status and reason;
- claim ID;
- admitted passage ID;
- fixture channel (`support` for the primary series);
- `origin="semantic_operator"`;
- eligibility=`eligible` (fixture stipulation);
- semantic validity=`valid` solely for the purpose of testing downstream participation after a positive authority result;
- complete support/refutation apertures;
- fully measured admitted passage with direct NLI channel scores below the signal floor, so no direct-NLI contribution competes;
- signal floor `0.20`;
- support threshold `0.70`;
- refutation threshold `0.70`;
- policy/receipt identities.

The fixture must state that neither channel nor scalar score is supplied by RC8J.

## Falsifiers

### F1 — no scalar score

Use the warranted semantic-operator contribution with `score=None`, `score_method=None`, and no score receipt.

Expected:

- valid evidence state: `support_only`;
- decision: `abstained`;
- reason: `contribution_score_unmeasured`.

This establishes that warrant alone does not currently produce a terminal decision in the existing model.

### F2 — arbitrary sub-threshold scalar

Keep every field from F1 fixed except inject:

- `score=0.69`;
- a fixture-only `score_method` explicitly labelled `caller_supplied_unowned_scalar`;
- a fixture score receipt.

Expected:

- decision remains abstained;
- reason: `support_below_decision_threshold`.

### F3 — boundary scalar

Keep every field fixed except `score=0.70`.

Expected:

- decision becomes `supported`;
- reason: `support_above_threshold`.

### F4 — high scalar

Keep every field fixed except `score=0.95`.

Expected:

- decision remains `supported`;
- same threshold reason class.

### F5 — refutation symmetry

Use the exact same warrant/evidence/policy fixture but separately stipulate channel=`refutation` and `score=0.70`.

Expected:

- decision becomes `contradicted`;
- reason: `refutation_above_threshold`.

This demonstrates that RC8J `WARRANTED` does not determine proposition polarity/channel either.

### F6 — mixed warranted semantic operators

Construct two fixture-only semantic-operator contributions over the same admitted passage, one support and one refutation, both score `0.95`, both otherwise eligible/valid under positive typed warrant controls.

Expected:

- valid state: `mixed`;
- decision abstains as `mixed_valid_evidence`.

No scalar winner may erase the conflict.

### F7 — unresolved authority cannot enter as valid

Use a directed mutation of the frozen RC8J seam control that returns `UNRESOLVED`.

The experiment harness must refuse to construct a `valid` semantic-operator contribution from that result. It may record an unresolved downstream eligibility/validity placeholder for diagnostics, but it must not count the contribution as semantically valid deciding evidence.

## Hard interpretation rule

If F1 abstains, F2/F3 flip only when the arbitrary scalar crosses the fixed threshold, F5 flips polarity solely by caller-stipulated channel, and F6 preserves mixed conflict, then the supported conclusion is:

`RC8J_WARRANT_IS_NOT_DECISION_STRENGTH_OR_POLARITY; EXISTING_SEMANTIC_OPERATOR_DECISION_PATH_REQUIRES_ADDITIONAL_UNOWNED_SCORE_AND_CHANNEL_SEMANTICS`

This would falsify the shortcut:

`RC8J WARRANTED -> assign confidence/score -> ordinary threshold decision`.

It would **not** yet choose the replacement architecture.

## Decision boundary after this experiment

If the hard interpretation rule is met, the next step is normative/architectural rather than apparatus repair. At least two materially different successor hypotheses exist:

1. **Categorical warranted-relation lane:** an independently warranted support/refutation semantic relation participates categorically, with conflict/composition handled explicitly and no invented scalar confidence.
2. **Separately authorized strength lane:** semantic authority and proposition polarity are established first, but a distinct calibrated/receipt-bound decision-strength measurement is required before thresholded resolution.

Choosing which authority should decide between those architectures is not delegated to this falsifier.

## Non-claims

This experiment does not establish:

- text -> receipt population;
- correct support/refutation channel inference;
- a valid scalar semantics for semantic operators;
- that the existing 0.70 threshold is appropriate for semantic operators;
- a production CAL decision policy;
- a Contract C change;
- Decision Engine policy;
- release readiness.