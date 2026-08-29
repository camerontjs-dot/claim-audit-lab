# Claim Audit Lab machinery audit baseline — 2026-08-29

## Scope

Research Infrastructure machinery audit against production base
`53f0885b111676794d1bd20e10b91aa58b07e9d4`.

This audit asks what code actually executes today, what newer machinery exists beside it, and which surfaces are sufficiently exercised to support the next rework.

## OBSERVED

### Released v1 execution path

The released default path is still:

`AuditRequest -> feature extraction -> bi-encoder retrieval -> retrieval-floor admission -> NLI -> MaxEntailmentAggregator -> VerdictRules -> AuditTrace`

`run_default_audit` constructs:

- `DefaultFeatureExtractor`;
- `BiEncoderRetriever`;
- `DeBERTaEntailer`;
- `MaxEntailmentAggregator`;
- `VerdictRules`;

and supplies them to `run_audit`.

The production retriever and entailer are revision-pinned:

- retriever: `sentence-transformers/all-MiniLM-L6-v2`
- revision: `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`
- entailer: `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`
- revision: `6f5cf0a2b59cabb106aca4c287eed12e357e90eb`

Both implementations refuse an empty/unpinned model revision.

### Existing test topology

The existing repository already runs the real pinned models individually:

- `tests/v1/test_retriever.py` exercises real SentenceTransformer inference, hand-checked top ranking, repeatability, and pinned-revision enforcement.
- `tests/v1/test_entailer.py` exercises real DeBERTa inference, hand-checked entail/neutral/contradict cases, byte-identical raw logits, label-order cross-check, and pinned-revision enforcement.

The ordinary `tests/v1/test_pipeline_e2e.py` does **not** integrate those two real models. It uses `StubRetriever` and `StubEntailer` while exercising the rest of the pipeline.

### Integrated real-model execution

The machinery audit adds an integrated default-pipeline smoke rather than substituting stubs.

Hosted research workflow run: `33274013299`.

The `integrated-real-model-smoke` job completed **SUCCESS**.

Artifact:
- id: `9720954184`
- archive digest: `sha256:329e99cb9d8b74f08f87f5d8cb0b5e601343cc5d7e1d38a504a37edf26955392`

Observed controls:

- exact support case -> `supported`;
- exact contradiction case -> `contradicted`;
- unrelated weather evidence -> retrieval score `-0.022063598036766052`, no passage admitted at the `0.4` retrieval floor, `A2_retrieval_empty`, terminal `not_checkable/no_evidence`;
- repeated integrated runs produced byte-identical trace JSON for each audit control.

The integrated receipt records the exact retriever revision, entailer revision, and rules-file SHA used.

### A second decision machinery already exists in the repository

The current production path is not the only epistemic machinery in `v1`.

`src/claim_audit_lab/v1/decision_model.py` explicitly describes itself as:

> a strict contribution ledger and decide-or-abstain candidate for CAL v1

and explicitly states that the legacy production pipeline condenses admitted passages to one `SupportSignal`.

The additive decision model retains:

- independent support and refutation channel measurements;
- per-contribution eligibility;
- per-contribution semantic validity;
- support/refutation aperture;
- ordered stage receipts;
- raw, eligible, and valid evidence states;
- passage-set contributions;
- explicit decision vs abstention;
- exact basis contribution IDs.

Its canonical stage order is:

`scope_identity -> decomposition -> retrieve_admit -> measure -> eligibility -> semantic_validity -> aperture -> aggregate -> resolve`.

It is extensively unit-tested and replayed against frozen historical outputs, but it does **not** alter `AuditTrace` or the released production verdict path.

### Evidence-state machinery exists separately

`v1/evidence_state.py` projects evidence into explicit states including:

- `no_evidence`;
- `unmeasured`;
- `read_silent`;
- `support_only`;
- `refutation_only`;
- `mixed`.

Tests preserve support/refutation channel provenance independently rather than collapsing them to the winning `SupportSignal`.

### RC1A result remains compatible with this split

RC1A established that richer execution/assessment/participation receipts can be captured around unchanged current v1 execution. The later production EDR correctly deferred shipping that research wrapper because no concrete current consumer required the research-only API controls.

That decision does not imply the existing semantic machinery is the intended final architecture.

## INFERENCE

The codebase currently has **two generations of epistemic machinery living side by side**:

1. the released legacy decision path centered on one aggregated `SupportSignal` plus deterministic rules;
2. an additive, more explicit contribution-ledger/state-machine candidate that retains distinctions the legacy path compresses.

This is likely the central machinery question for the next CAL phase. The right experiment is not “can current v1 run?” It can. The right experiment is whether the newer explicit state/decision machinery can become the decision substrate **without losing or silently changing the already-established measurement behavior and output contracts**.

The current integrated smoke removes one uncertainty: real-model composition itself works. Reworking CAL therefore does not require guessing whether the pinned model stack can execute end to end.

## HYPOTHESES

- The existing `decision_model.py` is a stronger starting point for CAL's next machinery than another rewrite from scratch because it already preserves raw/eligible/valid distinctions and explicit abstention.
- The legacy `SupportSignal` compression is likely the main place where information needed by the newer epistemic outputs becomes unavailable.
- The measurement layers can probably be retained while the decision substrate is replaced or shadowed.
- Some current deterministic rules encode valid eligibility/semantic policy and should be migrated as named stages rather than discarded wholesale.

## UNKNOWNS

This baseline does not establish:

- that the decision-model candidate reproduces all production verdicts where it should;
- which current rules are measurement, eligibility, semantic validity, aperture, aggregation, or final policy;
- whether current outputs can be generated directly from the candidate ledger without reconstruction;
- behavior on all existing frozen gold/diagnostic corpora under real models;
- the correct treatment of known unresolved numeric/range/composition families;
- whether a future release should replace `AuditTrace`, extend it, or emit a parallel epistemic artifact.

The full audit workflow/public suite associated with this branch has its own hosted status and remains operational evidence separate from the integrated smoke.

## NEXT

### 1. Shadow the actual production run into the explicit decision model

Build a **research-only adapter** from a real current `AuditTrace` plus explicit policy/semantic assessments into `EvidenceDecisionInput`.

Do not change production verdicts.

For a frozen corpus, emit side by side:

- current legacy verdict/reason/rules;
- projected raw evidence state;
- eligible evidence state;
- semantically valid evidence state;
- candidate decision/abstention;
- exact contribution basis.

The experiment should classify every disagreement by the stage that caused it rather than treating disagreement as a generic accuracy miss.

### 2. Bind the intended outputs to that shadow artifact

For each already-defined CAL output distinction, identify which stage/receipt supplies it and fail if the output would require guessing from a terminal verdict.

### 3. Exercise known diagnostic corpora

Use existing frozen Simple Logic Gold / construction-gold style corpora where the source objects are available, without tuning the gold.

Separate:
- retrieval miss;
- NLI measurement miss;
- eligibility/policy miss;
- semantic-operator miss;
- aggregation/composition miss;
- final decision-policy miss.

### 4. Only then choose production migration shape

Compare the smallest viable options:

- parallel epistemic artifact;
- additive trace extension;
- replacement decision substrate.

Do not select a migration shape before the shadow run shows which information is actually required and where current parity fails.
