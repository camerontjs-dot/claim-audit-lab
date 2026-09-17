# CAL V1 Claim Compiler RC0 — Result

Date: 2026-09-17

Primary disposition: **SUPPORTED FOR PROMOTION**

Classification: bounded interpretation-boundary result only. This record does not authorize merge, release, production promotion, generic natural-language parsing, automatic claim decomposition, learned parsing, new semantic families, raw-prose pipeline orchestration, Contract C/Decision changes, or automatic action.

## Question

Can CAL recover the exact current typed proposition target from exact Contract B claim text for the two already-qualified semantic families only, while failing closed on disagreement, partial recovery, ambiguity, and unsupported language, and without allowing interpretation to become verdict authority?

Preregistration: `docs/research/CAL_V1_CLAIM_COMPILER_RC0.md`

## Exact lineage

- repository: `camerontjs-dot/claim-audit-lab`
- parent M1 result head: `929be5baf400ec71f9209e59fbbfa87893a6dcff`
- preregistration commit: `0070d7b4a99956fce9462d2b3aac15bd7a32f49e`
- frozen corpus commit: `8c4f673651f6bf19ed0fdd883e5c08def72b1ae6`
- implementation commit: `c938f39741903064d9ab837418987e3e363dff21`
- falsifier/test commit: `398eac0be094bd1489467ff072c08ac440c60404`
- qualification-workflow commit: `f9e4034d42d88ab429fc4c304e65069f0fca4786`
- first static-quality correction: `455e9a87abfb8a88b1806589eb647682a87240b9`
- exact qualified head: `99bfbe9ec70b01d98d46d7303001096b27209e68`
- exact qualified tree: `f536922a01e9c02ba0d18075fa8e3d35c720629a`
- compiler blob at qualified head: `bc3a2181b0925462a60da34040e34561144b94b4`
- Draft PR: #117

## Observed implementation

RC0 adds a standalone proposal-only compiler at `production_v1/claim_compiler.py`. It does not modify the existing measurement, source-completion, semantic-authority, relation, composition, Contract B, Contract C, or Decision semantics.

For each currently supported family it uses two deliberately different deterministic proposal paths:

- strict comparison: bounded regex/template parser plus token parser;
- direct event order: bounded regex/template parser plus token parser.

A typed target is established only when two same-family proposal paths recover the same normalized fields and no unresolved cross-family signal is present.

Compiler terminal states are:

- `ESTABLISHED`;
- `AMBIGUOUS`;
- `EXTRACTION_UNRESOLVED`;
- `OUT_OF_JURISDICTION`.

Only `ESTABLISHED` carries a `TypedProposition` and canonical target. The receipt surface contains no conclusion, categorical relation, semantic authority, Contract C result, or Decision result.

## Frozen evaluation evidence

The corpus was frozen before implementation observation at `8c4f673651f6bf19ed0fdd883e5c08def72b1ae6`.

It contains 19 cases:

- 7 established strict-comparison cases;
- 5 established direct-event-order cases, including negative event polarity;
- 4 `EXTRACTION_UNRESOLVED` controls;
- 3 `OUT_OF_JURISDICTION` controls.

The focused RC0 suite also adds direct weak controls for:

- same-family parser disagreement -> `AMBIGUOUS`, no target;
- one-sided candidate plus unresolved peer -> `EXTRACTION_UNRESOLVED`, no target;
- cross-family unresolved signal blocking an otherwise agreed candidate;
- deterministic/content-bound receipt identity;
- exact handoff through the existing production target loader and Contract B identity/hash binding;
- absence of verdict/authority fields from compiler output.

## Final qualification result

Dedicated full-history workflow:

- run `35228779921` — `Research - CAL V1 claim compiler RC0` — **success**.

Observed on exact qualified head `99bfbe9ec70b01d98d46d7303001096b27209e68`:

- frozen compiler corpus and boundary falsifiers: **25 passed**;
- inherited semantic and Contract B gates: **28 passed**;
- full repository pytest: **1037 passed, 5 skipped, 48 deselected**;
- Ruff lint: **pass**;
- Ruff format check: **pass** (`67 files already formatted`);
- mypy: **pass** (`no issues found in 66 source files`).

The qualification workflow checks out with `fetch-depth: 0` and explicitly verifies the frozen parent, preregistration, and corpus commits are available before running the gates.

## Preserved failures and corrections

### First qualification attempt

Run `35227687204` on `f9e4034d42d88ab429fc4c304e65069f0fca4786` preserved a failure after all behavioral gates passed:

- compiler suite: **25 passed**;
- inherited semantic/Contract B gates: **28 passed**;
- full repository pytest: **1037 passed, 5 skipped, 48 deselected**;
- Ruff lint: **failed** on `CompilerStatus(str, Enum)` under rule `UP042`.

Correction: `455e9a87abfb8a88b1806589eb647682a87240b9` changed only the enum base to `StrEnum`. No fixture, parser decision rule, expected state, semantic rule, or downstream behavior was changed.

### Second qualification attempt

Run `35228293446` on `455e9a87abfb8a88b1806589eb647682a87240b9` preserved a second failure:

- compiler suite: **25 passed**;
- inherited semantic/Contract B gates: **28 passed**;
- full repository pytest: **1037 passed, 5 skipped, 48 deselected**;
- Ruff lint: **pass**;
- Ruff format check: **failed** because `claim_compiler.py` was not formatter-canonical;
- mypy: not reached.

Correction: `99bfbe9ec70b01d98d46d7303001096b27209e68` applied only Ruff's requested formatting. No logic or fixture content changed.

### Ordinary Public suite remains red

The ordinary Public suite on the exact qualified head remains red:

- run `35228780022`: **1 failed, 1036 passed, 5 skipped, 48 deselected**;
- failing test: `test_historical_goldens_only_change_the_distribution_version`;
- mechanism: the workflow uses `fetch-depth: 1`, so historical protected-main commit `32275a239b68af383a56bca843e28cbc1e343976` is unavailable to `git show`.

This defect is inherited. The exact M2 parent head `929be5baf400ec71f9209e59fbbfa87893a6dcff` also had a failing Public-suite run (`35226705372`), and the dedicated full-history qualification passes the same repository suite.

This CI debt is preserved as a separate apparatus issue rather than converted into semantic evidence or silently ignored.

## Inference

The evidence supports the bounded claim that CAL can expose a conservative proposal-only compiler for the two currently qualified semantic families while preserving the existing typed-input authority boundary.

Within the tested grammar, two agreeing deterministic proposal paths can produce the exact target shape already consumed by the current Contract B boundary. Disagreement, partial recovery, cross-family signal, and unsupported language fail closed and do not emit typed targets.

The compiler remains interpretation machinery rather than semantic/verdict authority: an established proposal still has to traverse the existing target validation, measurement, source completion, semantic authority, relation, and composition machinery before CAL can produce a conclusion.

## Alternative explanations considered

### Success may only reflect template regularity

This remains plausible. The corpus is small and controlled, and both parser implementations were authored in the same research execution. The result therefore supports a bounded grammar seam, not generic natural-language understanding.

### Two proposal paths may share blind spots

Also plausible. Exact agreement is a conservative local gate, not independent scientific agreement. A future independent parser or mutation campaign may expose shared false agreement.

### The compiler may be operationally too narrow

The experiment does not measure useful-language coverage beyond the frozen grammar. Safe abstention could be too frequent on ordinary claims even though the boundary is architecturally sound.

### A parser could accidentally become verdict authority downstream

The focused tests show the RC0 receipt exposes no verdict/authority surface and that established output is only a typed target. This does not prove every future orchestrator will preserve that separation, so orchestration remains a separate successor question.

## Falsified alternatives

Within the tested scope, the following alternatives were rejected:

- one parser path can unilaterally establish a target when its peer is unresolved;
- parser disagreement can be silently majority-voted into a target;
- an unresolved second-family signal can be ignored while another family establishes;
- unsupported ordinary or deontic language must be forced into one of the current two families;
- the compiler must change existing semantic or downstream machinery to hand off a target;
- compiler output must itself contain verdict or semantic-authority state.

## What is not established

RC0 does not establish:

- generic claim understanding;
- claim decomposition;
- arbitrary syntax or paraphrase coverage;
- independent parser agreement;
- learned parser, NLI, or LLM proposal safety;
- population/membership semantics;
- permission/exception semantics;
- assertion/scope semantics;
- retrieval or evidence-selection quality;
- automatic raw-prose pipeline execution;
- broader production release readiness.

The implementation, corpus, and tests remain within one research lineage. This is not an independent reproduction.

## Evaluator assurance

For the bounded RC0 claim, the apparatus is assessed as **E2 — sensitivity/invariance validated**:

- corpus expectations were frozen before implementation observation;
- explicit disagreement, partial-recovery, cross-family, identity, and authority-boundary controls were exercised;
- inherited semantic and Contract B gates stayed green;
- full repository and static-analysis gates passed under full Git history;
- two red static-quality attempts were preserved rather than overwritten.

This is not E4/E5 evidence because there is no independent implementation or context-free reproduction.

## Residual uncertainty

The next uncertainty is not whether a bounded proposal compiler can exist. It is whether richer measurement machinery can consume multiple heterogeneous observations without letting instrument agreement, confidence, or model output become semantic authority.

The ordinary Public-suite shallow-checkout defect should be repaired separately as CI hygiene.

## Reconsideration triggers

Reopen this result if any of the following occur:

- a mutation campaign finds false `ESTABLISHED` outputs on nearby unsupported forms;
- an independent parser disagrees systematically with the frozen compiler on established cases;
- a compiler-generated target can bypass claim-id or exact-text-hash binding;
- orchestration begins treating compiler state as semantic authority or a verdict;
- adding another family requires weakening the disagreement/fail-closed rules.

## Smallest justified next step

Do not broaden the grammar opportunistically in this RC.

Use the supported compiler seam as one input source while keeping manual typed targets as fallback, and separately test the next CAL architectural layer: a **true multi-instrument measurement ledger** in which heterogeneous instruments may append observations to one immutable audit context, but no voting, confidence score, or agreement count is allowed to become semantic authority without a separately qualified warrant rule.
