# CAL V1 Kernel Plugin Registry RC0 — Result

Date: 2026-09-17

Primary disposition: **SUPPORTED FOR PROMOTION**

Classification: bounded architecture result only. This record does not authorize merge, release, production promotion, Contract C requalification, Decision changes, new semantic families, claim parsing, NLI/LLM participation, or automatic action.

## Question

Can the frozen CAL V1 integration candidate be refactored behind an explicit semantic-family plugin/registry seam while preserving the exact currently supported semantic envelope and making missing or misrouted family machinery fail closed rather than silently falling back?

Preregistration: `docs/research/CAL_V1_KERNEL_PLUGIN_REGISTRY_RC0.md`

## Exact lineage

- repository: `camerontjs-dot/claim-audit-lab`
- parent records head: `d03d0e960ad82d889e6763fd4fb53cd24babd187`
- parent frozen implementation: `80835a57e121c66d22c68f349abf8e318de0e232`
- parent frozen implementation tree: `e6b218109233a2908e2cd558c714fb05cf9ac254`
- preregistration commit: `5131265027de3319fb527fb34a4aa9820361f752`
- implementation commit: `fadd2d0af7832b96cba959e3d843e1b9b6542bfb`
- corrected qualification head: `a5d3e1391a9e682559408e9a4df367b65f66b176`
- corrected qualification tree: `062fb665b6e6c8d564430704f54ad9fd1e42a9e2`
- Draft PR: #116

## Observed evidence

### Bounded implementation surface

The implementation added `semantic/plugins.py` and changed `semantic/engine.py` so family selection is performed through an immutable `SemanticFamilyRegistry`.

The default registry contains exactly:

- `direct_event_order`;
- `strict_comparison`.

The plugin object carries the existing measurement, authority, and relation callables. The engine still uses the existing semantic machinery after dispatch.

The five parent semantic implementation files below remained byte-identical to the frozen parent:

- `authority.py`: `3cfcfb8cc3b3a8860e119edfbe22a4d684650a86`
- `authority_validation.py`: `73ee2cc8e26cc3945558f76fa8c0992441177a97`
- `measurements.py`: `aa26d34a94488901d8a838824e0d7a23c6655f4c`
- `models.py`: `4a8ee5ddc66ad5512d675b45215a858eb8fdd7ee`
- `relations.py`: `2330f7acb64ac77ed0d26aebe7f4536062503400`

The successor-specific semantic dispatch identities were frozen as:

- `engine.py`: `67a519958bcf06b289b8a13cb0246d22ccf53c5c`
- `plugins.py`: `a2b96f192a4acafb2471785f0b51d2c656e03afc`

### Weak controls

The focused registry tests observed all preregistered controls:

1. an empty registry presented with a normally supported strict-comparison context returned `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY` with no measurement, authority, or relation trace;
2. a deliberately miswired strict-comparison plugin using the direct-event-order measurement function raised `PluginConfigurationError` on the semantic-family mismatch before warrant or relation derivation;
3. duplicate plugins for one family were rejected;
4. the default registry exposed no permission/exception or assertion/scope plugin.

### Equivalence and inherited semantic gates

The focused qualification workflow ran the registry tests together with inherited semantic behavior, authority-integrity, convergence, Contract B integration, and target-identity binding tests.

Observed result on corrected qualification head `a5d3e1391a9e682559408e9a4df367b65f66b176`:

- focused gate: **28 passed**;
- full repository pytest: **1012 passed, 5 skipped, 48 deselected**;
- Ruff lint: **pass**;
- Ruff format check: **pass** (`66 files already formatted`);
- mypy: **pass** (`no issues found in 65 source files`).

Qualification workflow:

- run `35185593338` — `Research - CAL V1 kernel plugin registry RC0` — **success**.

## Preserved failures and deviations

### First decisive run

The first run on implementation commit `fadd2d0af7832b96cba959e3d843e1b9b6542bfb` was preserved as a failure.

Public-suite run `35185128151` produced:

- **2 failed, 1009 passed, 5 skipped, 48 deselected**.

The two failures localized to qualification apparatus rather than changed verdict semantics:

1. `test_historical_goldens_only_change_the_distribution_version` attempted `git show 32275a2...` under the Public suite's default shallow checkout (`fetch-depth: 1`), so the historical commit was unavailable;
2. `test_production_semantic_core_matches_exact_successor_freeze` still pinned the parent `engine.py` blob even though RC0 deliberately changed engine dispatch.

Correction after that run:

- a dedicated RC0 qualification workflow was added with full Git history (`fetch-depth: 0`);
- the exact semantic-core identity test was changed to pin the successor `engine.py` and new `plugins.py` while continuing to pin the five untouched parent semantic files exactly.

No expected verdict, semantic family, measurement rule, warrant rule, relation table, composition rule, threshold, fixture gold, Contract B behavior, Contract C behavior, or Decision behavior was changed to obtain the corrected green run.

### Ordinary Public suite remains red

The ordinary Public suite on corrected head `a5d3e1391a9e682559408e9a4df367b65f66b176` still failed only the same historical-golden test because that workflow continues to use `fetch-depth: 1`.

Observed result:

- run `35185593331`: **1 failed, 1011 passed, 5 skipped, 48 deselected**;
- failing test: `test_historical_goldens_only_change_the_distribution_version`;
- failure mechanism: historical protected-main commit unavailable in the shallow clone.

This CI defect is inherited rather than introduced by RC0: the exact parent records head `d03d0e960ad82d889e6763fd4fb53cd24babd187` also had a failing Public-suite run (`35025064487`).

This inherited Public-suite defect is residual CI debt. It is not converted into semantic evidence for RC0 and is not silently ignored.

## Inference

The observed evidence supports the bounded claim that the currently qualified two-family CAL V1 semantic envelope can be routed through an explicit immutable semantic-family plugin registry without changing the tested verdict behavior or weakening the existing measurement, authority, relation, binding, and composition invariants.

The missing-plugin and miswired-plugin controls support a narrower safety claim: within the tested registry API, absent or foreign-family machinery fails explicitly rather than borrowing another registered family's path.

## Alternative explanations considered

### The full suite could be too weak to detect semantic drift

This remains possible in the broad sense. The conclusion therefore depends not only on the full suite but also on exact parent blob preservation for five semantic implementation files, direct plugin-stage equivalence tests, and two preregistered fail-closed weak controls.

### The registry could merely hide the old hard-coded branch

The engine no longer selects measurement functions by a family `if/else`; lookup is through the registry. The empty-registry control demonstrates that a supported proposition cannot reach a hidden fallback path in the tested engine entry point.

### The first red run could indicate a real semantic regression

The failures were localized to unavailable Git history and an intentionally changed engine blob identity. Re-running under full history with a successor-specific identity freeze produced the full green semantic and static-analysis result without changing semantic rules or expected answers.

## Falsified alternatives

Within the tested scope, the following alternatives were rejected:

- a family registry necessarily changes current CAL verdict behavior;
- a missing strict-comparison plugin can silently borrow direct-event-order or another semantic implementation;
- a plugin may emit a foreign-family measurement and continue through authority/relation processing unnoticed;
- introducing the registry seam requires widening the current semantic envelope.

## What is not established

RC0 does not establish:

- safety of arbitrary third-party plugins;
- semantic correctness of future plugins;
- automatic claim typing or decomposition;
- generic natural-language interpretation;
- NLI or LLM authority;
- population/membership correctness;
- permission/exception correctness;
- assertion/scope correctness;
- broader evidence aperture or retrieval quality;
- advanced causal-basis composition;
- production release readiness.

The implementation and evaluation were produced in the same research lineage. This is not an independent reproduction.

## Evaluator assurance

For the bounded RC0 decision, the qualification apparatus is assessed as **E2 — sensitivity/invariance validated**:

- positive/equivalence checks exercised both currently deciding families;
- missing-state and miswiring weak controls failed for the intended boundary reason;
- parent semantic implementations were pinned byte-for-byte where they were required to remain invariant;
- full repository and static-analysis checks passed under a full-history environment.

It is not E4/E5 evidence: there is no independent implementation or context-free reproduction of this successor.

## Residual uncertainty

The main remaining architectural uncertainty is no longer whether the current two families can live behind a registry seam. It is whether the next semantic capability can be added through that seam without weakening authority separation or causing family-specific assumptions to leak back into the kernel.

The ordinary Public-suite shallow-checkout defect should be repaired separately as CI hygiene; doing so is not part of this scientific disposition.

## Reconsideration triggers

Reopen this result if any of the following occur:

- a future plugin requires changing core composition or authority behavior merely to register;
- a family can decide through an absent or mismatched plugin;
- a future mutation test demonstrates hidden cross-family fallback;
- an independent reproduction finds verdict divergence from the frozen parent on the current two-family envelope;
- the registry interface becomes a source of semantic state not represented in receipts or audit output.

## Smallest justified next step

Do not add many semantic families at once.

Use this supported registry seam as the chassis for one separately preregistered successor that exercises a genuinely new boundary. The preferred next question is the **Claim Compiler**: can natural-language claim input produce a typed proposition proposal with explicit unresolved/ambiguous outcomes, while preserving manual typed input as the authority-preserving fallback and without allowing the compiler itself to become verdict authority?

A second reasonable successor is one new previously researched semantic family through the plugin seam. These should remain separate experiments unless evidence shows they must be coupled.
