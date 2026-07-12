# Claim Audit Lab — Design Decisions

This file tracks design and architectural decisions for Claim Audit Lab. CHANGELOG.md tracks releases; this file tracks the *why* behind significant changes, especially those driven by integration with other components or the research apparatus.

---

## 2026-05-08 — C-B accommodation plan (Apparatus contracts v1.0.0)

**Decision:** Claim Audit Lab will be extended to consume the v1.0.0 C-B handoff contract (Evidence Builder → CAL) defined in the **Apparatus Contracts** repo (`handoff-contract-v1.0.0`). This is Phase 1 of the apparatus handoff-contracts work.

**Why:** When CAL was built, the handoff contracts had not yet been formalized. The v1.0.0 lock now defines the on-disk bundle artifact CAL must consume from upstream. CAL's current `EvidenceBundle` is in-memory only and does not match the C-B structure. Without accommodation, the apparatus does not close the loop and the research proposal cannot use CAL as its measurement instrument.

**Adaptation strategy:** Add a parallel `BundleLoader` in v0.2.x that ingests a C-B `evidence-bundle-{bundle_id}/` directory tree and adapts it to current internal models. The shipped CLI surface (`claim-audit audit`, `claim-audit demo`) stays unchanged; a new `claim-audit audit-bundle <bundle-dir>` path opens. Plan v2.0.0 to make C-B the native bundle format once the apparatus has produced its first end-to-end run and the v1.0.0 contract has been validated.

**Concrete obligations against v1.0.0 contract (Phase 1 work):**

| Obligation | Driver |
|---|---|
| Rename `SupportLabel.not_audit_ready` → `not_checkable` | Amendment 3 in the contract — vocabulary alignment |
| Add `overstated_detection` rule to the audit pipeline | Six-value `audit_support_verdict` (Amendment 2) |
| Add `needs_source_detection` rule to the audit pipeline | Six-value `audit_support_verdict` (Amendment 2) |
| Add `false_caution_flag` logic — detect when scaffold over-hedges relative to evidence support | Research proposal's secondary metric; surfaced through C-B |
| Add `deviation_flag` logic — detect when audit verdict contradicts `scaffold_support_status` | C-B `claims/{claim_id}.yaml` `audit.deviation_flag` field |
| Persist audit verdicts to `claims/{claim_id}.yaml` files when ingesting from C-B | C-B requires audit fields be written back to the bundle |
| Implement C-B intake validator — verify `bundle_hash`, `schema_version`, `.contract-version` pin | Contract integrity verification protocol |
| Emit `audit_config.yaml` with `config_hash`, `change_log`, `frozen_at_utc` for any audit run produced from a C-B bundle | Frozen-state requirement (research proposal) |
| Add `schema/vocabulary.yaml` (byte-identical copy of canonical) and `schema/.contract-version` (pin to "1.0.0") | Vocabulary distribution model (Amendment 1) |
| Add C-B-related tests to the existing IQ/OQ/PQ validation pattern under `validation/` | Phase 4 engineering validation |

**Backward compatibility:** v0.1.0's CLI, schemas, and shipped fixtures remain functional. The new C-B path is additive in v0.2.x. The `not_audit_ready` → `not_checkable` rename is the only breaking change to v0.1.0 callers; address with a deprecation warning that accepts both names for one minor version.

**Out of scope for v1.0.0 contract compliance:**
- Reviewer sign-off mechanics — block stays null per Amendment 4
- Re-validation of CAL's own scoring on v0.1.0 fixtures (the existing IQ/OQ/PQ stands; new fixtures cover the new paths)
- Performance optimization

**Pickup point:** Read the apparatus handoff-contracts plan § Phase 1 and the **Apparatus Contracts** repo's `handoff-contract-v1.0.0` end to end before starting code. The schema-gap audit table in the contracts plan enumerates every divergence between v0.1.0 and v1.0.0 C-B; treat it as the work checklist.

**Rejected alternative:** v2.0.0 bump with C-B as native format from the start. Rejected because v0.1.0 is shipped and has known users (the portfolio audience); breaking the CLI surface before the apparatus has even produced its first run would be premature. Revisit after first end-to-end apparatus run.

---

## 2026-05-11 — C-B accommodation closure

**Decision:** Close CAL C-B accommodation Units 1-7 as complete for the synthetic engineering handoff path.

**What closed:** CAL now pins the locked v1.0.0 vocabulary, loads and validates C-B bundles fail-closed, adapts only `extracted_claim` records into the existing CAL pipeline, writes audited C-B output copies without mutating sealed inputs, exposes `claim-audit audit-bundle`, and documents the IQ/OQ/PQ-inspired validation addendum.

**Round-trip evidence:** The synthetic C-A fixture in Evidence Bundler verifies, builds a C-B fixture bundle, and runs through CAL `audit-bundle` to produce a reloadable audited output copy. The output claim `clm-001` receives `audit_support_verdict: supported`, with `false_caution_flag: false` and `deviation_flag: false`.

**Boundary:** This closes the engineering handoff for synthetic fixtures only. It does not validate full Evidence Bundler retrieval/review quality, human calibration, or research-measurement validity. Those remain future validation gates before confirmatory apparatus use.

---

## 2026-05-17 — Accept C-B v1.1.0 vocabulary passthrough (`format_only` workflow condition)

**Decision:** Claim Audit Lab accepts the v1.1.0 Apparatus Contracts vocabulary as a backward-compatible passthrough. The canonical contract added `format_only` as a fourth value to `workflow_condition` on 2026-05-15 (a portfolio-level decision). CAL ingests v1.0.0 and v1.1.0 C-B bundles identically; the new value flows through `BundleManifest`, `ClaimAuditUnit`, and the audited output copy without any semantic change in audit rules, scoring, or output shape.

**Why:** The portfolio-level decision binds consumer updates to the same change-control event as the canonical bump. Without acceptance, the portfolio-root `scripts/audit_workspace.py` reports vocabulary drift (canonical SHA `30e2ac74…05526bb` vs. CAL's stale embedded copy SHA `ec7a2305…cabc553a748f`), and any harness-produced v1.1.0 bundle is rejected at intake against the v1.0.0 pin. The contract change is explicitly "vocabulary passthrough only — no schema or behavioral changes" — CAL's job is to accept v1.1.0 inputs and not corrupt them, not to act differently on `format_only`.

**What changed:**

- `schema/vocabulary.yaml` — replaced with the byte-identical canonical v1.1.0 copy (SHA-256 `30e2ac74144185c8009d8224ecb67dd628b0b74244647c9051104334d05526bb`).
- `schema/.contract-version` — bumped from `1.0.0` to `1.1.0`.
- `src/claim_audit_lab/contracts/cb_models.py` — `ContractVersion` `TypeAlias` widened from `Literal["1.0.0"]` to `Literal["1.0.0", "1.1.0"]` (so existing v1.0.0 bundles still validate at the Pydantic field level); `WorkflowCondition` `TypeAlias` extended from three values to four with `format_only` inserted between `baseline` and `provenance_scaffold`.
- `src/claim_audit_lab/contracts/bundle_loader.py` — `CONTRACT_VERSION` bumped to `"1.1.0"`; new `SUPPORTED_CONTRACT_VERSIONS: frozenset[str] = frozenset({"1.0.0", "1.1.0"})` records the closed set of accepted bundle versions; `_verify_contract_version` switches from strict equality (`bundle_version != consumer_version`) to membership (`bundle_version not in SUPPORTED_CONTRACT_VERSIONS`). The `consumer_version` string is preserved in the failure message for diagnostics. The error-text shape (`"CONTRACT_VERSION mismatch: ..."`) is preserved so the existing `vocabulary_drift` deviation classifier and the deviation-text assertion in `test_cb_bundle_loader.py` keep working.

**Why the loader change is in scope under "passthrough only":** The Pydantic Literal widening handles the YAML `schema_version` field, but the on-disk `CONTRACT_VERSION` sentinel file goes through a separate strict-string-equality check at intake. After the consumer pin bumps to `1.1.0`, that check would reject every existing v1.0.0 bundle even though the contract change explicitly preserves them. The dual-version acceptance is the minimum surgery that makes "existing artifacts remain valid" literally true at the file level. The writer-side CONTRACT_VERSION (Bundler) commits to a single emit version (now `1.1.0`); the reader-side (CAL) accepts the closed set of vocabulary-passthrough-compatible versions.

**No assertion changes in CAL tests.** All 136 CAL tests pass unchanged. The fixture under `tests/fixtures/cb/evidence-bundle-minimal/` stays byte-identical with `CONTRACT_VERSION = 1.0.0` and `schema_version = 1.0.0` — the passthrough is the point. The existing assertions `manifest.schema_version == "1.0.0"` and `claim.schema_version == "1.0.0"` exercise the v1.0.0-still-loads path.

**Pre-merge verification (2026-05-17, this branch):**

- `.venv/bin/ruff check .` → all checks pass.
- `.venv/bin/python -m pytest` → 136 passed in 0.57s. No regressions.
- `.venv/bin/python -m compileall src` → no errors.
- Bundler side `test_phase4_handoff_demo` (which shells out to `claim-audit audit-bundle`) goes green after this CAL update; before this update it failed with `"CONTRACT_VERSION mismatch: bundle has '1.1.0', CAL pins '1.0.0'"`.

**Cross-component coordination:**

- Portfolio decision: the v1.1.0 MINOR bump (2026-05-15).
- Canonical contract: **Apparatus Contracts** `schema/vocabulary.yaml` (`contract_version: "1.1.0"`).
- Bundler parallel acceptance: **Evidence Bundler** `DECISIONS.md` § ADR-012.
- Workspace audit tooling updated so its canonical-version pin tracks `1.1.0` and includes the harness schema dir.

**Backward compatibility:** v0.1.0 / v0.2.x CLI surface is unchanged. C-B bundles produced by v1.0.0 Bundlers still ingest cleanly. No callers see a change in audit rule behavior, output shape, or deviation classification.

**Rejected alternative:** Bump `CONTRACT_VERSION` to `"1.1.0"` and reject v1.0.0 bundles. Loses backward compatibility with already-shipped Bundler outputs (e.g., the Phase 4 / Phase 5 demo bundles), contradicts the portfolio decision's "Existing artifacts remain valid" requirement, and breaks the CAL synthetic round-trip fixture without justification.

---

## 2026-06-19 — Lexical matcher falsified; retrieve→entail direction adopted

Blind PILOT-001 audit calibration scored 4/98 exact agreement, Cohen's κ ≈ -0.006, with CAL rating 0/98 `supported` versus the human's 80/98. Falsifies the v0.2 bag-of-stemmed-terms support matcher as a measurement instrument. Initial direction (retrieve → NLI entail → deterministic rules; CAL stays independent of the Evidence Bundler) recorded same day in the scaffold-claims-study submodule copy of this file. Consolidated and extended into the 2026-06-21 v1 design lock below.

---

## 2026-06-21 — CAL v1 design lock — PROPOSED

**Status:** Proposed (lock-before-build). Locks the design for `cal-rules-v1.3.0` and CAL package version `v1.0.0`. Consolidates the 2026-06-19 retrieve→entail direction with the full v1 design surface (architecture, contracts, taxonomy retirement, feature extractors, CLI, reproducibility, sync model).

**Decision (summary):** CAL v1 is a **three-layer, protocol-driven, deterministic verifier** built around a single versioned JSON contract: **retrieve → entail → aggregate + rules**. Swappable inference cores behind protocols. Deterministic linguistic feature extractors replace the regex-driven `ClaimType` taxonomy. Calibration is a first-class CLI workflow. v0.2 is retired ([`retired-prototypes/v0.2-lexical-matcher/`](../retired-prototypes/v0.2-lexical-matcher/README.md)). The standalone CAL repo is canonical; consumers (Scaffold Claims Study, Biotech RAG Assistant) pin to a CAL release rather than edit the submodule working tree.

**For implementers and reviewers:** Follow the concrete coding conventions, required imports, base model patterns, v1 protocols, provenance rules, and tooling config documented in the sibling plan note [`../plans/v1-coding-conventions.md`](../plans/v1-coding-conventions.md). This makes it easy to review the build plan while staying consistent with existing `models.py`, `v1/models.py`, `v1/protocols.py`, and contract layers.

### Why (the lexical matcher was falsified)

The blind PILOT-001 audit calibration (98 claims, single-coder gold, packet-relative coding rules) scored **4/98 exact agreement, Cohen's κ ≈ -0.006**. CAL `cal-rules-v1.2.0` rated **0/98 `supported`**; the human rated **80/98**. Root cause was structural, not a tuning miss: the bag-of-stemmed-terms matcher's non-numeric term-score ceiling was `0.45`, but `supported` required `0.80` — the verdict was **unreachable for text claims by design**. 55 of 98 claims starved at support `0.00`; 41 of those had a supporting passage in the supplied bundle the matcher could not see (median lexical coverage 0.43 against the ideal span; 0/41 cleared the 0.40 admission gate). Synonym/stemming expansion recovered 0/41 in offline probe — the gap is semantic, not lexical. Full analysis: knowledge-vault note `10_knowledge/agents/evals/2026-06-18__agents__note__cal-semantic-support-calibration-and-retrieve-entail-redesign.md`.

Offline local probes on the PILOT-001 bundles (CPU, sentence-transformers + HF cache):

- Embeddings recover *recall* but not *support*: bi-encoder cosine put all 41 starved claims ≥0.40 (median 0.66), but cosine separates topic, not support (human-supported 0.66 vs unsupported 0.57 — Δ0.09).
- NLI entailment separates *support*: `DeBERTa-v3-base-mnli-fever-anli` gives human-supported **0.97** vs unsupported/contradicted **0.16** (Δ0.81) and recovers **33/41** of the starved claims (median 0.90) where the matcher saw 0/41.
- Corroborated by the literature (FEVER three-label scheme judged against supplied evidence; similarity ≠ entailment; NLI scores 2.2% — below chance — on negated examples).

### 1. Three layers behind protocols

```
JSON input  →  Retriever  →  Entailer  →  Aggregator + Rules  →  JSON trace
```

- `Retriever(claim: str, passages: list[Passage]) -> list[(Passage, retrieval_score)]`. v1 impl: pinned bi-encoder (`sentence-transformers/all-MiniLM-L6-v2`, recorded HF revision SHA). Returns top-K candidates by cosine; does not decide support.
- `Entailer(claim: str, premise: str) -> (label, entailment_score, raw_logits)`. v1 impl: `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli` (pinned HF revision SHA, CPU, deterministic). 3-class entailment/neutral/contradiction → supported/contradicted/NEI. Base is sufficient for a v1 attempt — 33/41 recall with the rule layer backstopping the ~6 hard residuals. Known ceiling: strong on MNLI/FEVER (0.90/0.78), weaker on adversarial ANLI-r3 (~0.50); DeBERTa-v3-large is a documented upgrade if build-time validation shows the hard residual is too large.
- `Aggregator(entailment_results: list[EntailResult]) -> support_signal`. v1 impl: max-entailment over candidates (rationale recorded in trace). Concatenated-premise and M×N alternatives are documented but deferred; v1 picks max and instruments the residual for the v2 question.
- `Rules(claim, features, retrieval, entailment, support_signal, audit_config) -> Verdict + RuleTrace`. Deterministic. Carries the glass-box rationale. This is the only layer that produces a final verdict.

Each protocol lives in `src/claim_audit_lab/v1/protocols.py` as a `typing.Protocol`; the v1 implementations live in `src/claim_audit_lab/v1/impl/{retriever,entailer,aggregator,rules}.py`. Swapping a layer for benchmarking does not touch the others.

### 2. Independence from the Evidence Bundler (non-negotiable)

CAL must not consume the bundler's support/counter classification — a verifier that inherits the judgment of the component it verifies cannot catch that component's errors. The current v0.2 `match_scoped_evidence` admits bundler-linked counterevidence at overlap `0.0`; that coupling is removed under v1. The bundler's claim→passage links become an independent **cross-check** signal (`corroborated` / `weak-link` / `coverage-gap`), recorded in the trace but **never an input to the verdict**.

### 3. Versioned JSON input/output contract

- The C-B `evidence-bundle-{bundle_id}/` directory shape on disk is unchanged (apparatus interop preserved); intake produces a single normalized **`AuditRequest`** JSON object (pydantic model) for the inference pipeline. Internal code never touches YAML directly after intake.
- Every audit emits an **`AuditTrace`** JSON object alongside the per-claim YAML write-back. The trace records: input claim, retrieved passages with scores, per-passage entailment results with raw logits, extracted features, rules fired with reasons, model revision SHAs, `audit_config` hash, rules-file SHA, library version, and a final verdict + label distribution. **Reproducibility property:** the trace is sufficient to replay the verdict deterministically without re-running the models, given the same `audit_config`.
- Contracts live in `apparatus-contracts` (extending C-B v1.1.0) so consumers can validate against the same schema CAL emits.

### 4. Retire the `ClaimType` regex taxonomy

The `_CLAIM_TYPE_PATTERNS` regex tuples in [`classifiers.py`](src/claim_audit_lab/classifiers.py) are removed in v1. Symptom-of-failure: every new domain (most recently biotech / GMP — see the `legacy-biotech-regex` branch) required hand-extending the term lists with no principled stopping point. Closed-vocabulary regex was the wrong abstraction for an open-vocabulary semantic problem.

The signal the taxonomy was load-bearing for (rule gating on "what kind of claim is this?") collapses under retrieve→entail because NLI gives the support signal directly. The residual gating that v0.2 actually used reduces to a small set of **claim features**, each extracted by a linguistically grounded module:

| Feature | Extractor (v1) | Replaces |
|---|---|---|
| `has_numerical_value(claim) -> list[Quantity]` | `quantulum3` (value + unit) | regex `\d+%` patterns |
| `has_explicit_negation(claim) -> bool` | spaCy dep-parse, `neg` edges | regex word lists |
| `has_universal_quantifier(claim) -> bool` | closed-set lexicon (`all` / `every` / `always` / `never` / `no` / `none`) with linguistically justified scope check | regex word lists |
| `has_modal_strength(claim) -> {asserts, hedges, prescribes}` | closed-set modal verb lexicon + dep-parse for subject scope | regex word lists |

Features are pure functions, individually testable, and their outputs are recorded in the trace. The biotech vocabulary on the `legacy-biotech-regex` branch is preserved as a reference for the modal-strength and universal-quantifier closed-set design.

### 5. Deterministic rules retained as the glass-box layer

The rule layer carries the verdict, the rationale, and the failure modes NLI cannot handle:

- **Numeric / date agreement** — exact match where parsed via `quantulum3`; tolerance is `audit_config`-driven, never hardcoded.
- **Strength-wording** (`overstated`) — modal-strength feature interacts with entailment confidence; an over-asserted claim with weak entailment downgrades to `overstated`.
- **Negation / absence family** — NLI inverts negation/absence (2.2%, below chance, per Geiger et al. 2020 MoNLI). Deterministic backstop: if `has_explicit_negation` AND NLI says `entail`, flip to `contradict` (and vice versa) unless the passage is itself the negation.
- **`supported`/`partially_supported` boundary** — NLI does not separate these well (0.97 vs 0.75 overlap in probe). Rule layer uses universal-quantifier + scope features to disambiguate.

### 6. `audit_config` becomes the single source of tunables

One YAML file `audit_config.yaml` parameterizes everything tunable: retrieval `top_k`, retrieval score floor for admission, entailment threshold for `supported`, entailment threshold for `contradicted`, aggregation strategy, rule selection, rules-file SHA, model revision SHAs (retriever + entailer). All thresholds the v0.2 review found dead are either revived as live config or removed. `audit_config_hash` is recorded in every trace. Changing any tunable changes the hash; v1's frozen-rules discipline extends to the full config.

### 7. CLI: per-op + composed

```
cal retrieve     --request request.json --out retrieved.json
cal entail       --retrieved retrieved.json --out entailed.json
cal verdict      --entailed entailed.json --rules cal-rules-v1.3.0.yaml --out audit.json
cal audit-bundle <bundle-dir>          # convenience: full chain, current contract
cal calibrate    --packet PATH --gold gold.yaml --out calibration-report.md
```

`audit-bundle` keeps the v0.2 surface as the contract entry point (apparatus consumers do not change). The per-op commands are new and let benchmarking A/B retrievers without rerunning entailment, A/B aggregation strategies without re-running the model, or apply a new rules file without re-running anything stochastic.

### 8. Distinguish `no_entail_signal` from `out_of_scope`

The v0.2 `not_checkable` label conflated two meaningfully different cases. v1 separates them in the verdict ladder:

- `out_of_scope` — claim type intentionally not handled (e.g., first-person subjective preferences); v1's small documented exclusion list.
- `no_entail_signal` — NLI was inconclusive across all retrieved passages (neutral max, low confidence); CAL has the right tools for the question but the evidence does not answer it. This is the case most worth measuring in scaffold research.

Both are surfaced to the apparatus-contracts vocabulary as a sub-classification under `not_checkable` so the existing six-value contract is preserved at the C-B boundary; the v1 trace carries the finer label.

### 9. Reproducibility, first-class

- Model revisions pinned by HF revision SHA (not just model name); SHAs in the trace.
- Inference deterministic (no batch-size-dependent outputs, fixed torch seeds where stochastic, CPU only for v1).
- `cal-rules-v1.3.0.yaml` carries a SHA recorded in every trace.
- Acceptance gate: byte-identical traces on the calibration packet across runs in the same `audit_config`.

### 10. Calibration as a built-in workflow

`cal calibrate --packet PATH --gold gold.yaml` runs verdicts over the packet, computes exact agreement, Cohen's κ, per-class confusion, and a per-condition adverse-rate report; writes a calibration report. Closes the loop currently glued together with `score_calibration.py` in the scaffold-study analysis dir.

### 11. Sync model (standalone CAL canonical)

- Standalone [CAL workbench](.) is the **source of truth**. Releases go out from here; GitHub `main` is authoritative.
- Consumers (Scaffold Claims Study, Biotech RAG Assistant) **pin to a CAL release tag or commit SHA** via git submodule and do not edit the submodule working tree. Tests against unreleased CAL changes use a CAL feature branch pinned in the consumer, not a working-tree diff.
- Drift detection: each consumer's README carries a "CAL pin status" block (`v1.0.0`, `canonical-SHA`, `behind: 0`). A drift between submodule pin and canonical `main` shows as `behind: N` in the consumer README.
- Cross-asset uses (biotech-rag-assistant deferred generation phase, regulated-systems QRM note) build against the same canonical release. Build once, serve both.

### Acceptance test

Re-run the blind PILOT-001 calibration via `score_calibration.py` (or the new `cal calibrate`):

1. **Recall floor:** the 41 starved claims recover (≥35/41 in a supported verdict slot under v1).
2. **κ moves materially:** baseline κ ≈ -0.006; v1 target κ ≥ 0.4 (single-coder exploratory; reported as the pilot, not "validated").
3. **Per-condition adverse rate sane:** no condition stuck at 0/n or n/n; the model-dominance signal stays the same shape.
4. **Reproducibility:** two consecutive `cal calibrate` runs produce byte-identical traces.
5. **No regression on v0.2 fixtures that should still pass:** the synthetic round-trip fixture remains green; vocabulary passthrough at C-B remains green.

If 1-3 do not clear, the design is not yet correct; do not bump `v1.0.0`. The probe data already exists (33/41 NLI recovery in offline run); the gate is engineering follow-through, not a research bet.

Qualification threshold framed against SourceCheckup (Wu et al. 2025, *Nat. Commun.* 16:3615 — 88.7% verifier-vs-3-physician), reported honestly as an exploratory single-coder pilot, **not** "validated." Caveat (2026-06-19 research): SourceCheckup's verifier is **GPT-4 (LLM-as-judge), not a deterministic NLI** — CAL (CPU-only, deterministic) must not assume that agreement ceiling; calibrate the threshold independently.

### Package versioning

- `cal-rules-v1.2.0` → `cal-rules-v1.3.0` (frozen-rules discipline).
- Python package: `v0.2.x` → `v1.0.0` (major; public API breaks because per-op CLI is new, internal pipeline is new, `ClaimType` is removed).
- `audit-bundle` CLI keeps argument shape and output writeback unchanged so apparatus consumers can pin to `v1.0.0` without code changes.

### Cross-asset

The same measurable semantic-support check gates the biotech-rag-assistant's deferred generation phase (regulated-systems QRM note). Build once, serve both.

### Rejected alternatives

- *Lexical / synonym-map expansion* — semantics is not lexis; recovered 0/41 against the ideal span.
- *Trust the bundler's links (admit linked support, skip CAL retrieval)* — couples the verifier to the verified, destroying the independent cross-check that is CAL's reason to exist.
- *DeBERTa-v3-large / negation fine-tuning now* — deferred as documented upgrades; base + rules clears the bar for a v1 qualification attempt while staying CPU-light and glass-box.
- *Keep v0.2 contracts; swap matcher only* — would unblock the scaffold acceptance gate faster, but leaves the regex taxonomy and YAML-soup contracts in place; v2 would just repeat this work. Rejected: the redesign is justified now.
- *From-scratch rewrite (new repo, new history)* — discards the engineering shell (mypy-strict, frozen-rules discipline, byte-identical examples, C-B integration) that v0.2 got right. Rejected: rebuild the inference core in-place.
- *Drop the deterministic rule layer entirely, return raw NLI* — loses the negation/absence backstop and the glass-box rationale; loses interpretability of overstated/numeric-mismatch. Rejected on independence/interpretability grounds.
- *LLM-as-judge verifier (GPT-4 / Claude as the entailer)* — gives up determinism, reproducibility, CPU-only operation, and offline-from-artifacts; also creates a circular reasoning risk if CAL ever audits LLM outputs from the same family. Rejected for v1; documented as an explicit non-goal.

### Pickup point for the build

Read in order: this ADR, the retired prototype README (`retired-prototypes/v0.2-lexical-matcher/README.md`), and the falsification analysis note in the knowledge vault. Then start the v1 package under `src/claim_audit_lab/v1/` with the protocols + skeleton tests; do not delete v0.2 source until v1 passes the acceptance test.

---

## 2026-06-22 — Phase 0 Unit 1: v1 dependency floors — PROPOSED

**Status:** Proposed. Sign-off required before closing Phase 0 Unit 1; the floors below become part of the v1 reproducibility surface (changing a floor changes which versions a clean install may pick up).

**Decision:** Declare the v1 inference stack as a `[v1]` optional-dependency extra in `pyproject.toml` with the following lower-bound floors:

| Package | Floor | Resolved on 2026-06-22 |
|---|---|---|
| `quantulum3` | `>=0.4` | `0.10.0` |
| `spacy` | `>=3.7` | `3.8.14` |
| `sentence-transformers` | `>=3.0` | `5.6.0` |
| `transformers` | `>=4.40` | `5.12.1` |
| `torch` | `>=2.2` | `2.12.1` |

Floors picked so that: `quantulum3 >= 0.4` gives stable value+unit extraction (used by `has_numerical_value`); `spacy >= 3.7` gives stable dep-parse `neg` edges (used by `has_explicit_negation`); `sentence-transformers >= 3.0` gives the clean `SentenceTransformer(revision=...)` API; `transformers >= 4.40` gives stable DeBERTa-v3 tokenizer + model support; `torch >= 2.2` is the first release with reliable Apple Silicon CPU wheels.

**Why:** CAL v1 is CPU-only and deterministic by design (DECISIONS.md § 2026-06-21 § 9). The dependency stack must (a) provide the linguistic primitives Phase 1 wires (numbers, dep-parse, modal lexicons) and the inference primitives Phase 2 wires (bi-encoder retrieve + NLI entailment), (b) install cleanly into a Python 3.11 venv on Apple Silicon (Cameron's primary environment), and (c) leave v0.2's install surface untouched so apparatus consumers pinned to v0.2.0 are not affected. The `[v1]` extra makes the heavy stack opt-in.

**What changed:**

- `pyproject.toml` `[project.optional-dependencies]` adds `v1 = [...]`.
- `pyproject.toml` `[tool.setuptools.package-data]` adds `"v1/configs/*.yaml"` so the default config ships in the wheel.
- `scripts/verify_install.py` extended with a `_verify_v1_surface()` step that performs a clean-venv wheel install with the `[v1]` extra and asserts `from claim_audit_lab.v1 import ...` plus `BiEncoderRetriever`, `DeBERTaEntailer`, `MaxEntailmentAggregator`, `VerdictRules` resolve. A `--skip-v1` flag preserves the fast turnaround for changes that don't touch the v1 surface.
- `CHANGELOG.md` carries an `Unreleased` block describing the v1 scaffolding additions.
- `README.md` adds a `v1 in progress` section pointing at the design lock + build plan and showing the install + default-config usage.

**Backward compatibility:** v0.2 install path `pip install -e ".[dev]"` is unchanged; v0.2 CLI surface (`claim-audit demo`, `claim-audit audit`, `claim-audit audit-bundle`) is unchanged; v0.2 tests still pass (213 v0.2 + 25 v1 = 238 in the new baseline).

**Verification evidence (2026-06-22):**

- `pip install --dry-run -e ".[v1]"` resolved cleanly; full install resolved to versions listed above.
- `python scripts/verify_install.py` (both v0.2 and v1 surfaces) green from a wheel install.
- `pytest` 238 passed; ruff lint + format clean; mypy strict clean over 33 source files; compileall clean; coverage 96% on `src/`.

**Rejected alternatives:**

- *Pin exact versions instead of floors* — locks the install into a single resolution; clashes with downstream consumers that pin other things in the same venv. Floors with explicit notes are the v0.2 convention.
- *Make v1 deps unconditional (no `[v1]` extra)* — would force v0.2 apparatus consumers to install torch + transformers even though they don't use v1 yet. Rejected on consumer-cost grounds.
- *Add `sklearn` to the floor* — `quantulum3` optionally uses scikit-learn for disambiguation; CAL's use case (extracting numbers from short claims) doesn't need it. Re-evaluate if disambiguation precision turns out to be load-bearing for the gate.

**Sign-off pending:** Cameron — confirm the five floors above before Phase 0 Unit 1 closes.

---

## 2026-06-22 — Phase 0 Unit 2: pinned HF model revisions — PROPOSED

**Status:** Proposed. Sign-off required before closing Phase 0 Unit 2; these SHAs become THE reproducibility property for v1 audit traces. Changing either SHA changes every trace.

**Decision:** Pin the v1 retriever and entailer to specific HF revision SHAs in the shipped default config:

| Role | Model ID | HF revision SHA | Resolved |
|---|---|---|---|
| Retriever | `sentence-transformers/all-MiniLM-L6-v2` | `1110a243fdf4706b3f48f1d95db1a4f5529b4d41` | 2026-06-22 |
| Entailer | `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli` | `6f5cf0a2b59cabb106aca4c287eed12e357e90eb` | 2026-06-22 |

Both SHAs are the `main`-branch revision SHAs returned by the HF API (`GET https://huggingface.co/api/models/<model_id>`) on 2026-06-22.

**Why:** DECISIONS.md § 2026-06-21 § 9 makes byte-identical trace reproducibility a v1 acceptance condition. A tag or branch name can move (HF model authors push new weights); an SHA cannot. Pinning by SHA is the only way to make "same `audit_config` → same trace" durable across time. Recording the SHAs in the shipped YAML (not just in code) means downstream consumers see the same pin we built against.

**What changed:**

- `src/claim_audit_lab/v1/configs/v1-default.yaml` created with the two pinned SHAs, the v1-design-lock thresholds (`top_k=5`, `retrieval_floor=0.40`, `supported_threshold=0.70`, `contradicted_threshold=0.70`), `aggregation: max_entailment`, and a placeholder `rules_file_sha` (`"0" * 64`) to be replaced when Phase 1 commits `cal-rules-v1.3.0.yaml`.
- `src/claim_audit_lab/v1/configs/__init__.py` added so `importlib.resources` resolves the package-data namespace cleanly in both editable and wheel installs.
- `src/claim_audit_lab/v1/config.py` created exposing `load_default_audit_config() -> AuditConfig`, which reads the YAML via `importlib.resources.files("claim_audit_lab.v1.configs")`.
- `src/claim_audit_lab/v1/__init__.py` re-exports `config` and `load_default_audit_config` at the v1 package surface.
- `tests/v1/test_config.py` added with five tests: round-trip via the public API, pinned-SHA assertions, design-lock-default assertions, JSON round-trip, and a direct resource read via `importlib.resources` to prove wheel-install reachability.
- `scripts/verify_install.py` v1 surface check now also calls `load_default_audit_config()` and asserts the two pinned SHAs to catch a wheel-install regression early.

**Backward compatibility:** No v0.2 effect. v0.2 callers don't import from `claim_audit_lab.v1`.

**Verification evidence (2026-06-22):** as in Unit 1; specifically `tests/v1/test_config.py` 5/5 green and the wheel-install check confirms the pinned SHAs survive a clean install.

**Rejected alternatives:**

- *Pin by tag* — HF tags can be retargeted by model authors. Documented HF best practice for reproducible inference is SHA pinning.
- *Don't pin in the default config; require callers to supply SHAs* — defeats the "build once, serve both" sync model (DECISIONS.md § 2026-06-21 § 11). Apparatus consumers pin to a CAL release; the release ships the pinned default. Callers can still override per audit; the default is the published baseline.
- *Pin to a specific quantized variant of DeBERTa* — would speed up CPU inference but introduces a non-canonical weight set the literature doesn't characterize. Defer until Phase 2 measures base-on-CPU latency on the calibration packet.

**Sign-off pending:** Cameron — confirm the two SHAs above before Phase 0 Unit 2 closes. (Both SHAs are recorded in three load-bearing places: this ADR, `src/claim_audit_lab/v1/configs/v1-default.yaml`, and the assertion in `scripts/verify_install.py`.)

## 2026-06-25 — Phase 1 Unit 2: rule body + calibrated thresholds — ACCEPTED

**Status:** Accepted. Ratifies [Decision C](../plans/adr-v1-rule-order.md) (the canonical rule order, accepted 2026-06-25) as built, plus the threshold-sourcing model and three interpretation calls made during implementation. Closes build-register **B8**; **B9** (StubEntailer + end-to-end fixtures) is the next session.

**Decision C, as built.** `VerdictRules.apply` (`v1/impl/rules.py`) implements the three-phase order — Phase A gates (A1 scope → A2 retrieval-empty → A3 negation/absence backstop → A4 hard-contradiction, short-circuit), Phase B degree mapping, Phase C adjustments (6a numeric, 6b strength/scope, 6c inferred, 6d source-scope, 6f false-caution) under the **composition rule** (within Phase C the degree moves adverse-only and `contradicted` is terminal; the final degree is the most-adverse proposal, so the outcome is order-independent). Every rule that fires appends a `RuleFired(rule_id, reason)`; no degree changes without one.

**Threshold sourcing — the rules file is the single source, materialized into `AuditConfig`.** The verdict thresholds (`retrieval_floor`, `supported_threshold`, `contradicted_threshold`) plus the new `numeric_tolerance` now live **only** in the versioned rules file `cal-rules-v1.3.0.yaml`. `load_default_audit_config()` reads the operational `v1-default.yaml` (model pins, `top_k`, `aggregation`), materializes the thresholds from the rules file, and stamps `rules_file_sha`. Because there is one authored copy they cannot drift; `verify_rules_consistency()` re-checks a config against the shipped rules file (a tampered threshold or stale SHA raises). This replaces the `"0"*64` placeholder from the 2026-06-22 Phase 0 Unit 2 ADR and supersedes that ADR's statement that the thresholds are authored in `v1-default.yaml`.

- `cal-rules-v1.3.0.yaml` SHA-256: **`8e0ae3ab4b47d9ae048aca49776931afc9d551a17d830d95b61c2e8a46dac552`** (`numeric_tolerance: 0.0`, exact — provisional until a gate run shows it too strict; changing any value rebumps this SHA).

**Interface change.** `Rules.apply` gained `passages: list[Passage]` (protocols.py + impl). Decision C's 6a (compare the claim's quantity to the *supporting passage's*), 6d (passage `trust_level`), and A3 ("does the passage assert the un-negated content") all need passage text, which the originally-locked signature did not carry. This is an internal layer interface, not the C-B JSON contract; the orchestrator already holds the passages. `@runtime_checkable` only checks method presence, so the protocol-conformance tests are unaffected.

**Three calls made during implementation (flagged, not silent):**

1. **Weak contradiction → `unsupported`.** A `contradict` label *below* `contradicted_threshold` (which A4 lets through) maps to `unsupported` — evidence leans against but not decisively. Decision C did not cover this case; the reading also gives the otherwise-unemitted `unsupported` degree a home, satisfying the "every label producible" boundary.
2. **6e `citation_status` deferred.** The v1 input contract (`AuditRequest`) carries no citation, so `citation_status` stays `not_applicable`. A contract field + its own follow-up ADR are prerequisites.
3. **Gate-3 absence routing deferred.** Only the well-defined MoNLI backstop is coded (negated claim + `entail` + non-negated passage → `contradicted`). The gold 4b/4c/4d routing (out-of-scope vs correctly-stated packet absence) needs an *absence-claim* feature the four extractors do not provide — deferred to an ADR per the phase-doc stop-rule (no regex escape hatch). Gold 4a remains the documented accepted divergence; `support_score` derivation stays a Phase-4 (`cal calibrate`) concern, not a `Verdict` field.

**What changed:**

- `src/claim_audit_lab/v1/configs/cal-rules-v1.3.0.yaml` — new; the frozen rules file (single source of the verdict thresholds).
- `src/claim_audit_lab/v1/config.py` — `load_default_audit_config()` materializes thresholds from the rules file + stamps `rules_file_sha`; adds `load_rules_file()`, `verify_rules_consistency()`, `RulesConsistencyError`.
- `src/claim_audit_lab/v1/configs/v1-default.yaml` — thresholds removed (now sourced from the rules file); operational settings + the two pinned model SHAs retained.
- `src/claim_audit_lab/v1/models.py` — `AuditConfig` gains `numeric_tolerance`.
- `src/claim_audit_lab/v1/impl/rules.py` — `VerdictRules.apply` implemented; the stale six-step docstring replaced.
- `src/claim_audit_lab/v1/protocols.py` — `Rules.apply` gains `passages`.
- `tests/v1/test_rules.py` — new (full branch + composition + integrity coverage); `tests/v1/test_config.py` — updated for materialization + a tamper test.

**Verification evidence (2026-06-25):** full suite **303 passed**; `ruff check` / `ruff format --check` clean; `mypy --strict src` clean; `compileall` clean; coverage **99%** on `src/*` (rules.py 99%, config.py 100%), gate `--fail-under=95` PASS; `scripts/verify_install.py` green (clean wheel install). Committed locally on `cal-v1-skeleton`; **not pushed** (git-history scrub pending).

**Build-register:** B8 now cites [adr-v1-rule-order.md](../plans/adr-v1-rule-order.md). B9 (StubEntailer + end-to-end fixtures + byte-identical trace; the trace test needs `audit_config_hash`/B12 or a deterministic stand-in) is the next session.

## 2026-06-25 — Phase 1 Unit 3: StubEntailer + end-to-end pipeline + byte-identical traces — ACCEPTED

**Status:** Accepted. Closes build-register **B9** and completes **Phase 1** (the deterministic core now runs end-to-end and is proven byte-reproducible). Three open decisions from the Unit 3 brief were settled with the operator before any code; recorded here.

**Three decisions settled.**

1. **`audit_config_hash` — the real B12 hash, pulled forward (not a stand-in).** `AuditTrace.audit_config_hash` is produced by a new `hash_audit_config()` (`v1/config.py`): a deterministic `sha256:` digest over the config's canonical JSON (`model_dump(mode="json")`, `sort_keys=True`, no incidental whitespace), reusing `contracts.serialization.hash_text` so the `sha256:` convention matches the bundle-tree / audit-config-file hashes. Order-independent and ~5 lines; pulling the small B12 hash forward makes the byte-identity test verify the real field rather than a placeholder.
2. **End-to-end assembly — a production dependency-injected orchestrator (not a test-only harness).** `run_audit(request, *, feature_extractor, retriever, entailer, aggregator, rules) -> AuditTrace` lives in `src/claim_audit_lab/v1/pipeline.py` and depends only on the layer protocols. The *same* function drives the Phase-1 stubs and the Phase-2 real models, so byte-identity is a property of shipped code and Phase 2 swaps `BiEncoderRetriever` / `DeBERTaEntailer` in unchanged. Retrieval is supplied by an injected `StubRetriever`; no real retriever is built here (that is Phase 2 / B10).
3. **Stub placement — `tests/v1/testing/` (test-only), no ADR ceremony.** `StubEntailer` / `StubRetriever` are test-only and do not ship in the wheel. Because the DI orchestrator already lets any consumer inject its own fake via the `Entailer` / `Retriever` protocol, shipping ours is convenience, not necessity; promotion to an importable `src/claim_audit_lab/v1/testing/` is deferred until a real library consumer (apparatus host / DecisionEngine) needs it. No forward-commitment ADR is taken now — this is a lightweight decision log, revisited on demand.

**What was built:**

- `src/claim_audit_lab/v1/pipeline.py` — new; the `run_audit` DI orchestrator (features → retrieve → entail-each-passage → aggregate → rules → assemble trace). Deliberately **not** re-exported from `v1/__init__.py` (kept off the existing import path to minimise blast radius); import as `claim_audit_lab.v1.pipeline.run_audit`.
- `src/claim_audit_lab/v1/config.py` — adds `hash_audit_config()` (the real B12 config hash).
- `tests/v1/testing/{__init__,stubs}.py` — new; the test-only `StubRetriever` (canned scores, ranks + `top_k`, **no floor filtering** — the A2 gate owns the floor) and `StubEntailer` (canned `EntailResult`s keyed by `passage_id`).
- `tests/v1/test_pipeline_e2e.py` — new; 16 synthetic fixtures (real `DefaultFeatureExtractor` + stub entail/retrieve) reaching every gate A1–A4, every Phase B degree exit, every Phase C adjustment 6a/6b/6c/6d/6f, the composition case (`6a→contradicted` stays terminal under a `6b` overreach → `contradicted` + `overstated`), and all three `not_checkable` reasons; plus the two-run + golden byte-identity test.
- `tests/v1/fixtures/traces/*.json` — new; 16 committed golden `AuditTrace`s (the replay baseline; regenerate with `CAL_WRITE_GOLDENS=1`).
- `tests/v1/test_config.py` — adds two `hash_audit_config` tests (prefix + determinism; content-sensitivity).

**Discovered risk (logged, not fixed here).** `quantulum3`'s unit-disambiguation classifier fails to load in the venv (`ModuleNotFoundError: No module named '_loss'` — a scikit-learn 1.8→1.9 pickle mismatch). It only triggers for *ambiguous* units (e.g. "records per hour", "mg"); `percent` / dimensionless numbers skip it, so the fixtures and the whole suite are green. But a real-world numeric claim with an ambiguous unit would crash the feature extractor. An environment / dependency-pin concern for Phase 2 (real inference), out of scope for B9 — flagged for the Phase 2 entry. **→ Resolved 2026-06-29; see the addendum at the end of this file (the "fails to load" framing was overstated — corrected there).**

**`library_version`** is sourced from `claim_audit_lab.__version__` (currently `"0.2.0"` — honest; v1 is additive inside the 0.2.0 package).

**Verification evidence (2026-06-25):** full suite **340 passed** (+37: 35 e2e + 2 config-hash); `ruff check` / `ruff format --check` clean; `mypy --strict src` clean; `compileall` clean; coverage **97%** on `src/*` (pipeline.py 100%, config.py 100%, rules.py 99%), gate `--fail-under=95` PASS; `scripts/verify_install.py` green (clean wheel, v0.2 + v1 surfaces). Byte-identity: two harness runs per fixture identical, and identical to the 16 committed goldens. Committed locally on `cal-v1-skeleton`; **not pushed** (git-history scrub pending).

**Build-register:** B9 done. **Phase 1 complete.** Next: **Phase 2 (B10–B13)** — wire `BiEncoderRetriever` + `DeBERTaEntailer` and verify byte-identity survives real inference.

## 2026-06-29 — Phase 1 Unit 3 addendum: quantulum3 pinned to deterministic no-classifier mode — ACCEPTED

**Status:** Accepted. Resolves the quantulum3 classifier risk flagged in the Unit 3 entry above, before Phase 2 (operator decision), and closes that carry-forward.

**Correction to the original framing.** The B9 note called it a hard "fails to load" crash; on re-verification that overstated the steady state. With scikit-learn **1.9.0** and quantulum3's bundled **1.8.0** classifier pickle, the classifier normally **loads and runs**, emitting scikit-learn's `InconsistentVersionWarning` ("…may lead to breaking code or invalid results. Use at your own risk."). The `ModuleNotFoundError: No module named '_loss'` unpickle failure seen in B9 is **real but intermittent / import-order-sensitive** — it surfaces in some process states with identical versions. So the actual problem is twofold: (a) an ML model in CAL's numeric path running under a version combo its own library disclaims as possibly invalid, and (b) a latent, environment-sensitive crash. Both are unacceptable for a byte-reproducible auditor; neither depends on the crash reproducing.

**Fix.** `src/claim_audit_lab/v1/features.py` sets `quantulum3.classifier.USE_CLF = False` at import — quantulum3's supported, designed-in deterministic mode (`no_classifier.py`: static symbol/surface tables + a fixed word-overlap tiebreak; no sklearn, no model artifact). `disambiguate.py` reads the flag at call time, so the module-global assignment governs every CAL parse.

**Zero verdict impact (verified).** quantulum3 extracts the numeric *value* before unit disambiguation, and rule 6a compares `quantity.value` only — the `unit` is trace-only metadata no verdict reads. Disabling the classifier changes only the `unit` string for ambiguous-unit numbers. Confirmed: the 16 existing golden traces are **byte-unchanged** (percent / dimensionless never invoke disambiguation), and ambiguous-unit values parse correctly and deterministically (`5 mg/kg` → 5.0, `250 mL` → 250.0, `900 records per hour` → 900.0; two runs identical).

**Why not the alternatives.** *Build / regenerate the classifier ourselves* — feasible (quantulum3 bundles the training corpus + `train_classifier()`), but rejected: a **20 MB** sklearn-version-specific binary committed to the repo, re-breaking on every sklearn bump, an ML model back in the deterministic path, all to sharpen a trace field no verdict reads. *Pin scikit-learn < 1.9* — brittle; fights Phase 2's torch / transformers / sentence-transformers constraints.

**What changed:**
- `src/claim_audit_lab/v1/features.py` — `USE_CLF = False` at import (+ rationale comment).
- `tests/v1/test_features.py` — guard (`USE_CLF is False`) + ambiguous-unit value-correctness + determinism tests.
- `tests/v1/test_pipeline_e2e.py` + `tests/v1/fixtures/traces/17-numeric-ambiguous-unit.json` — a 17th end-to-end fixture (mg/kg numeric crux) locking the real-world ambiguous-unit path through `run_audit`.

**Latent gap surfaced (separate follow-up, not fixed here).** Rule 6a compares raw values, so it treats "5 mg" == "5 g" and "5000 mg" ≠ "5 g". If unit-aware numeric comparison is ever needed for a verdict, the fix is a small **deterministic CAL-owned unit map + conversion** in 6a — never the ML classifier.

**Verification evidence (2026-06-29):** full suite **346 passed** (+6); `ruff` / `ruff format --check` / `mypy --strict src` / `compileall` clean; coverage **97%** on `src/*` (gate ≥95% PASS); `scripts/verify_install.py` green (clean wheel, v0.2 + v1, scikit-learn 1.9). The 16 prior goldens byte-unchanged; the new fixture's golden byte-identical across two runs. Committed locally on `cal-v1-skeleton`; **not pushed** (git-history scrub pending).

## 2026-06-29 — Phase 2: inference layers (B10–B13) + CPU determinism baseline — ACCEPTED

**Status:** Accepted. Closes build-register **B10**, **B11**, **B13** and completes **Phase 2** (the v1 pipeline is now a real, deterministic, byte-reproducible measurement instrument over real models). **B12** was pulled forward into B9 (the config hash) and is reaffirmed below. The byte-identity property the calibration gate (Phase 4) depends on now holds over *real* inference, not just stubs.

### ADR — § Phase 2 Unit 1: CPU determinism baseline (the sign-off the phase doc required)

**Decision.** v1 inference runs **CPU-only**, single-threaded, with a fixed seed: `torch.set_num_threads(1)` + `torch.manual_seed(0)`, enforced at module load by a shared `claim_audit_lab.v1.impl._determinism.enforce_cpu_determinism()` that both the retriever and the entailer call on import. Models load in `eval()` mode; the entailer forward pass runs under `torch.no_grad()`. No CUDA/MPS paths are taken.

**Why.** The byte-identical-trace property (§ 2026-06-21 § 9) has to survive real model inference. On CPU the two run-to-run variance sources are multi-threaded reduction ordering and seeded init; pinning the thread count and the seed removes both. Verified empirically: two consecutive real-inference runs over every Phase-2 fixture produce byte-identical `RetrievalResult` scores, `EntailResult.raw_logits`, and full `AuditTrace` JSON — on Apple Silicon (ARM, darwin 25.5), so the documented `transformers` ARM determinism edge case did **not** bite; no version pin or seed-reset hack was needed.

**Raw logits.** `EntailResult.raw_logits` carries the **unrounded** three-class output in the model's native class order (`id2label` = `{0: entailment, 1: neutral, 2: contradiction}`), so a downstream consumer can re-derive the label under a different threshold without re-running the model. A test re-derives the label by argmax over the recorded logits and confirms it matches the entailer's own output — proof the logits are captured in the right order.

### B12 reaffirmed (done in B9), with a doc-parity test added

`audit_config_hash` was implemented in B9 as `hash_audit_config(config) -> str` (`v1/config.py`): deterministic `sha256:` over canonical JSON (`model_dump(mode="json")`, `sort_keys=True`, no incidental whitespace). The Phase-2 doc asked for an explicit "two configs differing only in YAML field order / whitespace → same hash" test; the B9 tests proved invariance via `model_copy`, not YAML reordering. Added `test_hash_audit_config_is_yaml_field_order_and_whitespace_invariant` (`tests/v1/test_config.py`) to close that parity gap directly at the YAML boundary. Note the name differs from the phase doc's `compute_audit_config_hash` — the B9 name `hash_audit_config` is canonical; no second hash function was introduced.

### Retrieval floor stays the A2 gate's job (not the retriever's)

The phase doc's Unit-1 text says the retriever returns "top-k passages by cosine ≥ `retrieval_floor`", but the `Retriever.retrieve(claim, passages, top_k)` protocol carries no floor argument, and the Phase-1 `StubRetriever` (the established contract reference) deliberately does **no** floor filtering — the rules-layer `A2_retrieval_empty` gate owns the floor (§ 2026-06-21 § 5). `BiEncoderRetriever` matches the stub: it ranks all passages by cosine and returns the top `top_k`, floor-unfiltered. Following the protocol over the doc's prose keeps the orchestrator and the A2 gate semantics unchanged.

### Finding (deferred, operator-decided 2026-06-29): `MaxEntailmentAggregator` masks the entailment/contradiction signal

Real inference surfaced a **pre-existing latent bug in the Phase-1 aggregator** that the stub fixtures could never expose. `MaxEntailmentAggregator.aggregate` picks the candidate with the highest softmax `score` **across any label** (`max(results, key=lambda r: r.score)`) and reports it as the support signal — but the rules layer reads `support_signal.label` / `.max_entailment_score` expecting the strongest *entailment* signal (the field name says as much). When a confidently-**neutral** passage outscores a confidently-**entail** or confidently-**contradict** passage, the real signal is masked:

- `inf-01` (claim verbatim-supported by p1, entail 0.9946) → aggregator picks p2 (neutral 0.998) → `not_checkable / no_entail_signal`. Should be `supported`.
- `inf-03` (claim contradicted by p1, contradict 0.9961) → aggregator picks p2 (neutral 0.998) → `not_checkable`; the `A4_hard_contradiction` gate never sees the contradiction. Should be `contradicted`.

The stub fixtures hid this because their canned logits always gave the entail passage the top score. This degrades verdict quality broadly under real inference and would distort Phase-4 calibration.

**Decision (operator, 2026-06-29): defer + document.** It is out of Phase-2 scope (B10–B13 = wire models + prove byte-identity, which is green either way), it touches a locked Phase-1 layer, and a correct fix interacts with the `A4` contradiction gate (the aggregator condenses to a single signal, so "prefer entail" risks masking a real contradiction) — it needs its own ADR + sign-off, not a freelance change. The B13 goldens are committed as the real pipeline currently produces them: honest reproducibility anchors that will change deliberately when the aggregator is fixed. **Follow-up:** a scoped ADR to redesign the aggregator → support-signal contract so the entailment and contradiction signals are not masked by neutral confidence (candidate: surface entail-max and contradict-max separately, or rank by relevance-then-label rather than raw softmax). Filed for the operator; not a Phase-3 prerequisite, but should land before Phase 4 calibration.

**→ RESOLVED 2026-06-29 (Option A, neutral-blind max) — see the next entry.** The operator chose the simpler single-signal fix over the two-signal redesign after weighing cost/risk; two-signal stays in reserve as the calibration-gated upgrade.

## 2026-06-29 — Aggregator neutral-masking fix (Option A: neutral-blind max) — ACCEPTED

**Status:** Accepted. Resolves the `MaxEntailmentAggregator` masking finding from the Phase 2 entry above, before Phase 3. Operator chose **Option A (neutral-blind max)** over **Option B (two-signal `SupportSignal`)** after weighing cost/risk.

**Root cause.** `EntailResult.score` is the softmax probability of the passage's *argmax* label. For a neutral passage that score means "confident this passage is irrelevant", not "confident the claim is unsupported". The old aggregator ranked candidates by raw `score` across all labels, so a confidently-neutral passage outranked a confidently-entail/contradict one — masking the real signal (e.g. `inf-01` entail 0.9946 masked by neutral 0.998 → `not_checkable`; `inf-03` contradict 0.9961 masked by neutral 0.998 → `not_checkable`, the `A4` gate never seeing the contradiction). The stub fixtures hid it because their canned logits always gave the decision-relevant passage the top score.

**Fix (Option A).** `MaxEntailmentAggregator.aggregate` now selects the highest-scoring **support-bearing** (`entail`/`contradict`) result; only when *every* candidate is neutral does it fall back to the highest-scoring neutral (a `neutral` signal the rules read as `no_entail_signal`). One sentence: *"the strongest support-or-contradiction signal wins; neutral passages don't count."* The `SupportSignal` contract is **unchanged** (same three fields), so the **rules layer is untouched** and the `A4`/`B5` logic reads `label`/`max_entailment_score` exactly as before — this is why Option A carries none of the two-signal redesign's rules-rewiring or `test_rules.py` risk.

**Why Option A over Option B (two-signal).** Two-signal (carry best-entail *and* best-contradict separately; rules apply A4-on-contradict-max, B5-on-entail-max) is the maximally-correct design and the only one that also resolves the *conflicting-evidence* case below — but it changes the `SupportSignal` trace contract (rewriting the `support_signal` block in all 22 committed goldens), rewires Phase A/B of `rules.py`, and rebuilds the `test_rules.py` branch fixtures (the verdict layer's safety net) at the same time. The operator judged that cost/risk disproportionate to closing a rare, ambiguous case, and chose the surgical fix. Option A is a strict subset of Option B's behaviour, so nothing is foreclosed: if Phase-4 calibration shows conflicting-evidence cases move the numbers, we upgrade then.

**Residual (documented, Phase-4-gated).** When one passage strongly *entails* and another strongly *contradicts* the same claim, the single-signal contract can carry only one; the higher-scoring wins and the other is not surfaced. Genuinely conflicting evidence — narrow (needs two strong opposing passages in top-k), ambiguous (reasonable systems disagree), and in practice a real direct contradiction usually scores highest anyway. Locked in `test_aggregator_conflicting_evidence_higher_score_wins` so the behaviour is explicit, not accidental. Two-signal is the fix if calibration shows it matters.

**What changed:**
- `src/claim_audit_lab/v1/impl/aggregator.py` — neutral-blind selection + rationale docstring. `SupportSignal` contract, protocols, and `rules.py` untouched.
- `tests/v1/test_protocols.py` — 4 new aggregator tests (neutral-doesn't-mask-entail, neutral-doesn't-mask-contradict, all-neutral fallback, conflicting-evidence residual); the existing `test_aggregator_picks_highest_score` still passes unchanged.
- `tests/v1/test_byte_identity.py` — added an `expected_verdict` per fixture asserted end-to-end, so the corrected verdicts (`inf-01` → `supported`, `inf-03` → `contradicted`) are guarded independently of the goldens.
- `tests/v1/fixtures/traces/inference/inf-01-*.json`, `inf-03-*.json` — regenerated (the two corrected verdicts). The other 3 inference goldens and **all 17 stub goldens are byte-unchanged** (single-passage / all-neutral traces select the same value as before — the contract didn't move).

**Verification evidence (2026-06-29):** full suite **382 passed** (+4 aggregator tests); `ruff` / `ruff format --check` / `mypy --strict src` / `compileall` clean; coverage **97%** on `src/*` (aggregator.py 100%; gate ≥95% PASS); `scripts/verify_install.py` green. Only `inf-01`/`inf-03` goldens changed; two real-inference runs per fixture byte-identical. Committed locally on `cal-v1-skeleton`; **not pushed** (git-history scrub pending).

**Build-register:** no register ID (post-Phase-2 correctness fix on a Phase-1 layer). **Phase 3 unblocked.** The two-signal redesign remains available as a calibration-gated upgrade if the conflicting-evidence residual proves material.

**What was built:**

- `src/claim_audit_lab/v1/impl/_determinism.py` — new; the shared CPU determinism baseline (`enforce_cpu_determinism()`), called at module load by the retriever + entailer.
- `src/claim_audit_lab/v1/impl/retriever.py` — `BiEncoderRetriever` wired: real `SentenceTransformer(model_id, revision=<sha>, device="cpu")`, claim + passages embedded once per call (L2-normalized), cosine ranking, top-`k`, floor-unfiltered. Process-level model cache (`functools.cache` keyed by model id + revision). Unpinned revision → `ValueError`.
- `src/claim_audit_lab/v1/impl/entailer.py` — `DeBERTaEntailer` wired: real `AutoModelForSequenceClassification` + `AutoTokenizer` from the pinned revision, `tokenizer(premise, claim)` MNLI/FEVER order, `eval()` + `no_grad()` forward pass, label via `config.id2label`, softmax-max `score`, unrounded `raw_logits`. Same process-level cache + unpinned-revision guard.
- `src/claim_audit_lab/v1/config.py` — unchanged (B12 hash already present from B9).
- `tests/v1/test_retriever.py` — new; 3-claim × 5-passage fixture (hand-checked top-k ordering), determinism (byte-identical scores), pinned-revision load, top-k truncation, empty-passages, unpinned-revision raise.
- `tests/v1/test_entailer.py` — new; 5-pair fixture (3 entail / 1 neutral / 1 contradict, hand-checked labels), byte-identical `raw_logits` across runs, raw-logits→label cross-check, unpinned-revision raise.
- `tests/v1/test_byte_identity.py` + `tests/v1/fixtures/traces/inference/inf-0{1..5}-*.json` — new; 5-claim × 3-passage end-to-end fixture over real retriever + entailer + aggregator + rules, two-run byte-identity + committed goldens (regenerate with `CAL_WRITE_GOLDENS=1`).
- `tests/v1/test_config.py` — adds the YAML field-order/whitespace hash-invariance test (B12 doc parity).
- `tests/v1/test_protocols.py` — removed the obsolete `test_inference_methods_raise_not_implemented_during_skeleton` (the inference bodies are now wired); the structural-conformance + aggregator tests remain.

**Inference timing (Apple Silicon, CPU, single-threaded):** retriever load + first encode ≈ 2s; entailer load + first pair ≈ 3.4s (one-time per process via the cache). Steady-state DeBERTa-v3-base is ~0.5–2s per pair, well under the phase doc's 30s/pair blocker threshold; the full new v1 suite (model load + all fixtures) runs in ≈ 24s.

**Verification evidence (2026-06-29):** full suite **378 passed** (+32: B10/B11/B13 tests + the B12 parity test, minus the removed skeleton test); `ruff check` / `ruff format --check` / `mypy --strict src` / `compileall` clean; coverage **97%** on `src/*` (retriever.py / entailer.py / `_determinism.py` 100%; gate `--fail-under=95` PASS); `scripts/verify_install.py` green (clean wheel, v0.2 + v1 surfaces, both pinned SHA assertions pass). Byte-identity: two real-inference runs per fixture identical, and identical to the 5 committed inference goldens. Committed locally on `cal-v1-skeleton`; **not pushed** (git-history scrub pending).

**Build-register:** B10, B11, B13 done; B12 reaffirmed (done in B9). **Phase 2 complete.** Next: **Phase 3 (apparatus intake)** wires this pipeline behind the existing `audit-bundle` CLI surface. Open follow-up before Phase 4: the aggregator masking ADR (above).

## 2026-06-29 — Phase 3 Unit 1 (B14): AuditRequest normalizer + dual-path coexistence — ACCEPTED

**Status:** Accepted. First unit of Phase 3 (apparatus intake). Wires the loaded C-B bundle into v1's `AuditRequest` contract and establishes how the v0.2 and v1 auditors coexist behind the unchanged `audit-bundle` CLI. Routing (Unit 2) and the apparatus round-trip (Unit 3) build on this.

### Decision 1 — The `pipeline` selector lives on `CBAuditConfig`, optional, default `v0.2-lexical`

The selector that decides which auditor a bundle routes through is `CBAuditConfig.pipeline: "v0.2-lexical" | "v1-retrieve-entail"` (new `AuditPipeline` literal in `contracts/cb_models.py`), **optional with a `v0.2-lexical` default**.

**Why on the bundle's audit-config rather than a CLI flag or the v1 `AuditConfig`.** Pipeline choice is an *audit-policy* decision — the same class as the thresholds and rule switches already frozen in `audit_config.yaml` — so it belongs with the sealed policy the bundle carries, read at intake to branch routing, A/B-comparable per bundle, and hash-covered like any other policy field. A CLI flag would make the routing a per-invocation accident rather than a sealed property of the audited artifact; putting it on the v1 `AuditConfig` is wrong because that config is CAL's *inference* config (model pins, thresholds), not a per-bundle routing choice, and it isn't materialized from the bundle.

**Why this does not violate the "C-B on-disk shape unchanged" boundary.** The field is *optional* with a v0.2 default, so:
- A bundle that omits it (every existing/external bundle, including the `evidence-bundle-minimal` fixture) validates unchanged, keeps its existing `audit_config.config_hash` (the hash is over the *file*; a defaulted field absent from the file doesn't change those bytes), and routes v0.2 — the safe default. Verified: the full v0.2 suite is green and `audit-bundle` over the fixture is byte-reproducible across runs after the field was added.
- A bundle that opts into v1 *writes* `pipeline: v1-retrieve-entail` into `audit_config.yaml` and seals it into `config_hash` exactly like any other policy field. Whoever seals the audit policy owns the choice.
- `audit_policy_drift` (the v0.2 fail-closed policy gate) is a closed allowlist that does not reference `pipeline`, so the new field neither trips drift nor is silently accepted as drift. Teaching the loader's policy gate to admit a `v1-retrieve-entail` bundle is **Unit 2's** concern, not Unit 1's.

**The bundle's `CBAuditConfig` thresholds are not v1's thresholds.** When v1 runs, its `AuditConfig` is the pinned `load_default_audit_config()` (model revisions + rules-file-materialized thresholds), **not** derived from the bundle's `CBAuditConfig`. The bundle's scoring/rule_policies are a v0.2 artifact; v1 sources verdict numbers from its own versioned rules file (§ 2026-06-21 § 6). So a v1-selecting bundle is a v0.2-policy-shaped `CBAuditConfig` (to pass the loader's existing gate) **plus** `pipeline: v1-retrieve-entail` — coherent, and the normalizer takes the v1 inference config as an explicit argument rather than reading it off the bundle.

### Decision 2 — The normalizer is pipeline-agnostic; `retrieval_seed` claims are skipped

`claim_audit_lab.v1.intake.bundle_to_requests(bundle: BundleContents, audit_config: AuditConfig) -> list[AuditRequest]` is a pure transformation over the already-loaded, already-verified `BundleContents`. It does **not** branch on `pipeline` — it always produces the requests, and the CLI router (Unit 2) decides whether to consume them. This keeps the normalizer simple and means the request shape is available whichever path runs.

- **One request per *auditable* claim.** Only `extracted_claim` records become requests; `retrieval_seed` records are topic prompts, not checkable statements, and are skipped — mirroring `contracts/adapter.py` and the C-B type boundary in `cb_models.py`. ("Every claim round-trips" in the phase plan = every auditable claim; the minimal fixture's one claim is `extracted_claim`.)
- **The retriever, not the bundler, picks candidates** (§ 2026-06-21 § 2). Every request carries the bundle's *full* passage set; the C-B `evidence_passages`/`counterevidence_passages` curation does not pre-filter what v1 sees.
- **YAML is parsed once.** `load_bundle` does the only YAML parse (and all fail-closed intake checks); everything downstream of `bundle_to_requests` is frozen pydantic. The F1–F15 "YAML soup" finding is fixed by construction.

### Decision 3 — v1 passage handle is `{source_id}/{passage_id}`, raw coordinates preserved in `source_meta`

C-B `passage_id` is unique only *within* a source (`bundle_loader._verify_loaded_consistency` keys passages by `(source_id, passage_id)`), but the pipeline keys passages by `Passage.passage_id`. So the v1 handle is the globally-unique `{source_id}/{passage_id}` — reusing the exact convention already in `adapter._excerpt_id`. The raw `source_id`, `passage_id`, and `passage_hash` (plus `section` when present) are preserved in `Passage.source_meta` so a trace entry cross-references back to `evidence/{source_id}/passages/{passage_id}.yaml` and its integrity hash. Passages are flattened in deterministic order (sorted by `source_id`, then load order within a source) so the trace stays byte-reproducible.

**What changed:**
- `src/claim_audit_lab/contracts/cb_models.py` — new `AuditPipeline` literal + optional `CBAuditConfig.pipeline` field (default `v0.2-lexical`); exported.
- `src/claim_audit_lab/v1/intake.py` — new; `bundle_to_requests` + the passage normalizer.
- `src/claim_audit_lab/v1/__init__.py` — re-exports `intake` + `bundle_to_requests`.
- `tests/v1/test_intake.py` — new; 6 tests: one-request-per-extracted-claim, full-passage-set + preserved provenance, determinism, `retrieval_seed` skip, sectionless-passage key omission, `pipeline` default.

**Verification evidence (2026-06-29):** full suite **388 passed** (+6); `ruff check` / `ruff format --check` / `mypy --strict src` / `compileall` clean; coverage **97%** on `src/*` (`intake.py` 100%; gate `--fail-under=95` PASS); `scripts/verify_install.py` green (clean wheel, v0.2 + v1 surfaces). v0.2 `audit-bundle` over `evidence-bundle-minimal` byte-identical across two pinned-metadata runs (path unchanged). Committed locally on `cal-v1-skeleton`; **not pushed** (git-history scrub pending).

**Build-register:** B14 done. Next: **Unit 2 (B15)** — branch `audit-bundle` on `CBAuditConfig.pipeline`, run the v1 pipeline, write `claims/{claim_id}.audit-trace.json` into the audited copy, and reseal `SHA256SUMS` + `bundle_hash`. This is where the loader's v0.2 policy gate gets taught to admit a `v1-retrieve-entail` bundle.

## 2026-06-29 — Phase 3 Unit 2 (B15): `audit-bundle` v1 routing + trace writeback — ACCEPTED

**Status:** Accepted. Second unit of Phase 3. `audit-bundle` now branches on `CBAuditConfig.pipeline`: the default `v0.2-lexical` path is byte-unchanged, and a `v1-retrieve-entail` bundle runs the real v1 pipeline and writes a replay-sufficient `AuditTrace` into the audited copy.

### Decision 1 — The loader's v0.2 policy gate did **not** need teaching (Unit 1's forward note was wrong)

The Unit 1 ADR predicted Unit 2 would teach `_verify_supported_audit_policy` to admit a v1 bundle. **It turned out not to.** `audit_policy_drift` (`policy.py`) is a closed allowlist over `config_id` + `scoring` + `rule_policies`; it never references `pipeline`. A v1-selecting bundle carries a **v0.2-policy-shaped `CBAuditConfig`** (`config_id: cal-rules-v1.2.0`, the exact v0.2 thresholds) **plus** `pipeline: v1-retrieve-entail`, so it passes the existing gate untouched. This is coherent because v1 sources its verdict thresholds from the pinned `load_default_audit_config()` (the rules file), **not** from the bundle's `CBAuditConfig` (Unit 1 Decision) — the bundle's v0.2-shaped policy block is vestigial to v1 and exists only to satisfy the unchanged C-B contract + the loader's integrity checks. No `policy.py` / `bundle_loader.py` change shipped. (If a future bundle needs a genuinely different audit policy under v1, *that* is when the gate gets a pipeline-aware branch — not now.)

### Decision 2 — v1→C-B verdict crosswalk for the per-claim YAML

The audited copy keeps the C-B on-disk shape: each `claims/{claim_id}.yaml` gets its `audit` block populated so a consumer reading the flat C-B contract still sees a verdict, **and** a new `claims/{claim_id}.audit-trace.json` carries the full two-axis v1 detail. The two-axis v1 `Verdict` is flattened to the six-value C-B `audit_support_verdict` deterministically (`v1/cb_writeback.cb_support_verdict`):

| v1 `support_verdict` (+ flags) | C-B `audit_support_verdict` | rationale |
|---|---|---|
| `supported` / `partially_supported` | same | vocabularies coincide |
| `supported`/`partially_supported` **+ `overstated` flag** | `overstated` | the two-axis flag collapses onto the flat degree axis |
| `unsupported` | `unsupported` | coincide |
| `contradicted` | `unsupported` | C-B has no `contradicted`; strongest C-B negative; finer label kept in the trace |
| `not_checkable` (any reason) | `not_checkable` | § 2026-06-21 § 8 — finer reason lives in the trace; v1 collapsed `needs_source` into `not_checkable`/`no_evidence` (`models.VerdictReason`), so v1 **never emits the C-B `needs_source` degree** |

`overstated` only collapses a *positive* degree — it never rewrites `unsupported`/`contradicted`/`not_checkable`. The other C-B audit fields: `audit_confidence` ← `support_signal.max_entailment_score` (the [0,1] number, since the v1 `audit_confidence` is a high/med/low literal that doesn't fit the C-B float); `false_caution_flag` ← `"false_caution" in audit_flags`; `deviation_flag` ← the shared `audit_flags.is_material_deviation(scaffold_status, cb_verdict)` (same set both paths use); `audit_notes` ← a deterministic one-line summary pointing at the trace file.

### Decision 3 — Shared reseal; v1 path is report-free; heavy imports are lazy

- **Reseal factored, not reinvented.** `_reseal_output_bundle` / `_write_sha256sums` moved out of `output_writer.py` into public `serialization.reseal_bundle()` / `write_sha256sums()`; both the v0.2 and v1 writebacks call them. Proven behaviour-preserving: v0.2 `audit-bundle` output is **byte-identical pre/post the refactor**. The new trace JSON files are picked up automatically — `iter_handoff_files` is `rglob`-based, so they're hashed into both `SHA256SUMS` and `bundle.bundle_hash` with no special-casing. `audit_config.yaml` is untouched by writeback, so its hash is not recomputed.
- **No markdown report on the v1 path.** The `AuditTrace` JSON *is* the per-claim report (glass-box, replay-sufficient); a second rendered artifact would only add a surface to drift. The v0.2 path still writes its `…-audit-report.md`.
- **Torch stays off the v0.2 path.** The v1 inference imports (`v1.runner.run_default_audit`, which pulls `sentence-transformers`/`transformers`/`torch` via the impl layers) are imported **inside** the CLI's v1 branch, so a `v0.2-lexical` invocation never loads them. `run_default_audit` reads model revisions + rules SHA off the request's own `audit_config`.

**What changed:**
- `src/claim_audit_lab/cli.py` — `audit_bundle` split into `_audit_bundle_v0_2` (existing body, unchanged behaviour) + `_audit_bundle_v1` (lazy-imported v1 path); branch on `contents.audit_config.pipeline`.
- `src/claim_audit_lab/v1/runner.py` — new; `run_default_audit(request)` assembles the pinned default pipeline.
- `src/claim_audit_lab/v1/cb_writeback.py` — new; `cb_support_verdict` crosswalk + `write_audited_bundle_v1` (trace JSON + per-claim YAML population + reseal).
- `src/claim_audit_lab/contracts/serialization.py` — new public `reseal_bundle` / `write_sha256sums`.
- `src/claim_audit_lab/contracts/output_writer.py` — uses `reseal_bundle`; private reseal helpers removed.
- `src/claim_audit_lab/contracts/audit_flags.py` — new public `is_material_deviation` (shared by both paths; `compute_flags` refactored onto it, behaviour identical).
- `tests/v1/test_cb_writeback.py` (14) + `tests/v1/test_cli_v1.py` (3, real inference, incl. two-run byte-identity).

**Verification evidence (2026-06-29):** full suite **405 passed** (+17); `ruff check` / `ruff format --check` / `mypy --strict src` / `compileall` clean; coverage **97%** on `src/*` (gate ≥95% PASS; `runner.py` 100%, `cb_writeback.py` 95%, `cli.py` 95%, `audit_flags.py` 100%); `scripts/verify_install.py` green (v0.2 + v1 surfaces). v0.2 `audit-bundle` output **byte-identical pre/post the reseal refactor**; v1 `audit-bundle` byte-identical across two pinned-metadata runs; the audited v1 bundle reloads cleanly through the fail-closed loader. Committed locally on `cal-v1-skeleton`; **not pushed** (git-history scrub pending).

**Build-register:** B15 done. Next: **Unit 3 (B16)** — apparatus round-trip with the Evidence Bundler `scaffold-run-minimal` fixture: bundler build → CAL v1 `audit-bundle` → reload via both the C-B loader and a new `v1.intake.load_audited` helper that surfaces the traces; assert one claim's verdict; `docs/v1-round-trip.md`.

## 2026-06-29 — Phase 3 Unit 3 (B16): typed audited loader + apparatus round trip — ACCEPTED

**Status:** Accepted. Third and final unit of Phase 3. The real Evidence Bundler synthetic fixture now builds to C-B, opts into CAL v1 with every integrity hash recomputed, audits through the unchanged `audit-bundle` CLI, and reloads through both the existing C-B loader and a typed v1 audited-bundle API.

### Decision 1 — `load_audited` returns an additive `BundleContents` subtype

`claim_audit_lab.v1.intake.load_audited(bundle_dir, *, deviations_dir=None) -> AuditedBundleContents` is the smallest public typed API that preserves the current loader surface. `AuditedBundleContents` subclasses `BundleContents`, so callers retain direct access to `manifest`, `audit_config`, `validation_set_ref`, `claims`, `passages`, and `source_profiles`; the only addition is `traces: dict[str, AuditTrace]`, keyed by `claim_id`. This is preferable to a positional tuple (ambiguous public shape) or a nested wrapper (forces existing `BundleContents` consumers through a second access path).

`load_audited` does **not** implement a second C-B or YAML loader. It calls `contracts.bundle_loader.load_bundle` first, so contract version, C-B schemas, supported policy, `audit_config_hash`, `SHA256SUMS`, bundle hash, and vocabulary pin all fail closed through the established API. Only after that succeeds does it parse `claims/*.audit-trace.json` through strict, extra-forbidding `AuditTrace.model_validate_json`. It requires one trace per `extracted_claim` and checks filename → `trace.claim_id` → C-B claim plus exact `claim_text` binding. Trace-layer failures raise `AuditedBundleError`, a `BundleIntegrityError` subtype, so callers may retain the existing broad integrity-error catch.

### Decision 2 — B16 locks an observed synthetic label expectation; it does not invent an expected-output artifact

Evidence Bundler's sealed `tests/fixtures/scaffold-run-minimal/` contains only the C-A fixture inputs; a filename/content search confirms there is **no expected-outputs file**. The extracted `clm-001` proposition and its sole synthetic passage directly agree: both say accelerated approval applications should include 30-day accelerated stability data in the submission package. The pinned CAL v1 round trip deterministically produces C-B `supported`, v1 `supported`, `support_verdict_reason=None`, and an `entail` support signal. The B16 test locks those categorical outputs without pinning the incidental probability score. This is engineering evidence for the sealed handoff only; the fixture itself says it is synthetic, not FDA guidance or regulatory advice.

**What changed:**
- `src/claim_audit_lab/v1/intake.py` — public `AuditedBundleContents`, `AuditedBundleError`, and `load_audited`; all C-B/YAML work remains delegated to `load_bundle`.
- `src/claim_audit_lab/v1/__init__.py` — re-exports the typed audited-loader surface.
- `tests/v1/testing/bundles.py` — shared deterministic v1 opt-in/reseal helper.
- `tests/v1/test_intake.py` — typed-loader success, missing/invalid/misbound trace, and fail-closed ordering coverage.
- `tests/v1/test_apparatus_round_trip.py` — real Evidence Bundler CLI → CAL v1 → dual-loader integration test, with portable environment/sibling discovery.
- `docs/v1-round-trip.md` + validation-matrix row CAL-REQ-046 — runnable public sequence, expected-label basis, and synthetic limitation.

**Verification evidence (2026-06-29):** targeted B16/loader/routing/writeback checks **56 passed**; full suite **411 passed** (+6); `ruff check` / `ruff format --check` / `mypy --strict src` / `compileall` clean; source branch coverage **97%** (`--fail-under=95` PASS); `scripts/verify_install.py` green. The documented Evidence Bundler → CAL command sequence ran clean, and explicit reloads through `load_bundle` + `load_audited` produced C-B `supported`, v1 `supported`, no reason sub-label. Dedicated v0.2 + v1 pinned-metadata byte-identity checks both passed. Evidence Bundler remained read-only and clean.

**Build-register:** B16 done; Phase 3 complete. Next recorded project action: **Phase 4 Unit 1 (B17)** — build the `cal calibrate` command against the synthetic calibration boundary before any PILOT-001 gate run.

## 2026-06-29 — Phase 4 Unit 1 (B17): `calibrate` command (synthetic boundary) — ACCEPTED

**Status:** Accepted. First unit of Phase 4. A `calibrate` command runs the v1 pipeline over a packet of C-B bundles, scores every claim against a blind human gold, and writes a deterministic Markdown calibration report plus one `AuditTrace` JSON per claim. This unit builds the *instrument*; it deliberately does **not** run the sealed PILOT-001 gate (Unit 3) and applies **no** pass/fail thresholds.

### Decision 1 — Built against the shipped two-axis verdict, not the stale flat 6×6

The Phase-4 plan's Unit 1 checklist (and the STALE acceptance-test procedure § Step 4) specify Cohen's κ + a flat **6×6** confusion matrix + `adverse = unsupported+contradicted+overstated`. That text predates Decision A (the two-axis `Verdict` already shipped in `v1/models.py`, commit `2099ee1`) and is flagged superseded by the build plan's own "Plan-consistency defects" #3/#4. The instrument therefore measures CAL's **emitted** `support_verdict` (5 ordinal degrees) → a **5×5** confusion matrix, with `overstated`/`inferred` reported on a separate flags axis. The gold is crosswalked into the same two-axis space via the 3 explicit mappings (`reasonable_inference`→`supported`+`inferred`; `overconfident`→flag `overstated`; `missing_needed`→`citation_status`). The label set is sourced from the `support_verdict` `Literal`, **not** the embedded `vocabulary.yaml` (still v1.1.0): `calibrate` never crosses the C-B boundary, so the contract `contradicted`/`needs_source` split-brain (Part 6 of `v1-pre-coding-decisions.md`) is orthogonal and untouched.

### Decision 2 — Full metric suite computed; Decision D gate thresholds deferred to Unit 3

The report computes exact agreement; **Cohen's κ** (kept for continuity with the −0.006 baseline); **Gwet AC2** and **ordinal quadratic weighted-κ** (Decision D's prevalence-robust metrics — κ is paradox-prone at the gold's 82% `supported` prevalence); the 5×5 confusion; a flags table; and adverse-rate `= (unsupported+contradicted)/checkable` overall + per-condition + per-model (Decision 4's single definition, `overstated` *out*). Ordinal weighted-κ/AC2 run on the on-scale subset (positions `supported=4, partially_supported=3, unsupported=1, contradicted=0`; `not_checkable` off-scale). Decision D stays **PROPOSED**: no AC2/κ **threshold** is baked in — the gate threshold must be re-derived under AC2 at Unit 3 (κ≥0.4 does not transfer). The κ confidence interval is a **simplified asymptotic Wald** interval; confirming the exact Bonett & Bergsma (2008) variance is a gate-time sign-off item. Metrics are pure functions over integer counts (stdlib only; no new deps) and were validated against hand-worked values (κ=0.7222, weighted-κ≈0.9492, AC2≈0.9526 on the synthetic packet).

### Decision 3 — Engine in `v1/calibrate.py`; thin command on the existing app; torch injected

The metric/crosswalk/render/assembly logic lives in `v1/calibrate.py` and is **torch-free**: the pipeline is injected as an `auditor` callable, so the engine is covered by fast unit tests and the CLI passes the real `run_default_audit` (heavy imports stay local to the command, mirroring `_audit_bundle_v1`). The phase doc's literal `src/.../v1/cli.py` filename was not followed — the repo has a single top-level Typer app with v1 logic in `v1/` modules, so the command attaches there (consistent with `audit-bundle`→`_audit_bundle_v1`). A packet is a directory whose immediate subdirectories are C-B bundles; each is loaded via the fail-closed `load_bundle` and normalized via the existing `bundle_to_requests`. The gold↔packet claim sets must match exactly (no silent drops). `--config` is loaded by a new `v1.config.load_audit_config(path)` that reads operational knobs from the file but still materializes verdict thresholds + `rules_file_sha` from the pinned rules file.

> **⚠ Naming gap (flag for sign-off):** the phase docs invoke `cal calibrate`, but the only console script is `claim-audit` (`pyproject [project.scripts]`). The command therefore runs as **`claim-audit calibrate`**. Whether to add a `cal` entry point is a public-CLI-shape decision deferred to Phase 5 (per-op CLI).

**Sign-off needed (per Evidence Standard; not self-approved):** (1) the report's exact section schema — provisional here, ADR sign-off due at Unit 2 so future diffs are meaningful; (2) the public CLI shape (`claim-audit calibrate`); (3) the `cal` vs `claim-audit` name; (4) the κ-CI variance method at gate time.

**What changed:**
- `src/claim_audit_lab/v1/calibrate.py` — new; gold contract + crosswalk + pure metrics (`cohens_kappa`/`cohens_kappa_ci`/`weighted_kappa`/`gwet_ac2`/`confusion_matrix`/`adverse_rate`) + `compute_calibration` + `run_calibration` + `render_report`.
- `src/claim_audit_lab/v1/config.py` — new `load_audit_config(path)` (shared `_materialize_audit_config` helper; runs `verify_rules_consistency`).
- `src/claim_audit_lab/cli.py` — new `calibrate` command (lazy torch import) + `_write_traces`.
- `tests/v1/testing/bundles.py` — `build_calibration_packet` + the 5 `CALIBRATION_CASES` (reuse the committed inference goldens' verdict spread).
- `tests/v1/fixtures/calibration-synthetic/{gold.yaml,audit-config.yaml}` — committed static gold + operational config; the packet is built on demand by the helper.
- `tests/v1/test_calibrate.py` — 31 tests: metric units (hand-checked), crosswalk, gold-loader strictness, assembly + alignment errors, render fixed-order + pinned-timestamp, `run_calibration` over the real packet (stub auditor), and real-inference CLI + two-run byte-identity.

**Verification evidence (2026-06-29):** full suite **442 passed** (+31); `ruff check` / `ruff format --check` / `mypy --strict src` / `compileall` clean; source branch coverage **97%** (`calibrate.py` 99%, `config.py` 100%, the new CLI command fully covered; `--fail-under=95` PASS); `scripts/verify_install.py` green. `claim-audit calibrate` over the synthetic 5-claim packet produces exact agreement 4/5, κ=0.7222, recall floor 1/1, and is **byte-identical across two runs** (report + all traces). Committed locally on `cal-v1-skeleton`; **not pushed** (git-history scrub pending).

**Build-register:** B17 done (synthetic boundary). Next: **Unit 2** — the synthetic dry-run / report-schema ADR sign-off; then **Unit 3 (B18)** — the sealed PILOT-001 gate (do not start before the procedure is rewritten against Decisions A/B/D/E and Decision D's AC2 threshold is re-derived).

## 2026-06-30 — Phase 4 Unit 2: report section schema + synthetic dry run — ACCEPTED (§1–7 instrument schema, additively extensible)

**Status:** ACCEPTED. The synthetic dry run is **done + green**, and Cameron **signed off 2026-06-30** on the §1–7 instrument schema in Decision 1 as *additively extensible* (Unit 1 deferred the schema here so future report `diff`s are meaningful — Evidence Standard: public artifact shape). Freezing the instrument now is what makes the gate's reproducibility check trustworthy; extending it is a separate, additive step. **Two additive extensions are explicitly deferred to Unit 3 and must not be silently dropped:** (a) a `## Gate result` section — Unit 2 deliberately bakes in no threshold; (b) a `citation_status` axis — the crosswalk computes `missing_needed`→`citation_status` but §1–7 renders no citation row, so citation is currently **unscored** (acceptable because **no gate acceptance condition scores citation**; revisit only if the gate rewrite decides to calibrate it). No engine logic changed, no gate was run, and Decision D's gate **threshold** stays PROPOSED/deferred to Unit 3.

### Decision 1 — The calibration report's section schema (ACCEPTED 2026-06-30, additively extensible)

`render_report` output is frozen to **8 fixed headers in fixed order** (a `diff` catches drift), each with a fixed column contract. Every number derives from integer counts; the only timestamp is `--pinned-at` (never the wall clock); floats are fixed-precision — so two runs are byte-identical.

Header block: `# CAL v1 Calibration Report`, then `Generated: <pinned_at>` · `Library: claim_audit_lab <ver>` · `Rules: <rules_version> (sha: <rules_file_sha>)` · `audit_config_hash: <sha256:…>` · `Claims scored: <n>`.

1. `## 1. Recall floor on starved claims` — four `n/starved_total` buckets: supported, partially_supported, adverse (= unsupported+contradicted), not_checkable.
2. `## 2. Agreement and reliability` — exact agreement `n_agree/n_total (pct, 1dp)`; Cohen's κ (4dp); `95% CI (asymptotic Wald) [lo, hi]` (4dp); `Gwet AC2 (quadratic, on-scale n=N)` (4dp); `Weighted kappa (quadratic, on-scale)` (4dp).
3. `## 3. Support-verdict confusion (gold rows x CAL columns)` — 5×5 Markdown table, header `| gold \ CAL | supported | partially_supported | unsupported | contradicted | not_checkable |`, integer cells, gold rows × CAL columns in that fixed label order.
4. `## 4. Flags axis (gold vs CAL counts)` — `| flag | gold | CAL |` over the six audit flags in fixed order: overstated, inferred, source_scope_error, false_caution, missed_counterevidence, coverage_loss.
5. `## 5. Per-condition adverse rate` — `| condition | CAL adverse/checkable | gold adverse/checkable |`, one row per condition, sorted by condition name.
6. `## 6. Per-model adverse rate` — same shape, one row per model, sorted by model name.
7. `## Trace metadata` — `Retriever: <model_id>@<sha>`; `Entailer: <model_id>@<sha>`; determinism note; `Overall adverse (CAL): a/c; (gold): a/c`.

**Metric definitions pinned:** adverse = unsupported+contradicted; checkable = total − not_checkable. Ordinal weighted-κ + Gwet AC2 use quadratic weights over the **on-scale subset** (exclude any pair where either side is `not_checkable`), positions supported=4, partially_supported=3, unsupported=1, contradicted=0. Cohen's κ + exact agreement + the 5×5 confusion use all five labels.

### Decision 2 — 12-claim dry-run packet (4 conditions × 3, 2 models, 3 starved)

The canonical synthetic packet grew **5→12 in place** to exercise every section with **>2-row** tables (the 5-claim packet's per-condition/per-model tables can't catch the multi-row sort/render bugs the 98-claim gate will hit). It **reuses the five committed-golden contents under twelve claim_ids** so every CAL verdict stays deterministic and hand-checkable — no new claims, no re-derived goldens (that would be Phase 2 work). Honest limitation, documented in the fixture: CAL's emitted columns are confined to {supported, contradicted, not_checkable}; the hand-authored gold spans all five degrees, so the 5×5 confusion + on-scale weighted/AC2 path are still fully rendered. The flags axis shows gold-side counts vs CAL=0 (all five goldens emit no flags / `not_applicable` citation). Hand-checked **and** machine-confirmed (stub engine + real-model CLI agree): exact **10/12**, Cohen's κ **13/17 = 0.7647**, on-scale n=9, weighted-κ **0.9854**, Gwet AC2 **0.9860**; recall floor 2 supported / 1 adverse of 3; overall adverse CAL 5/9, gold 5/10; per-condition (CAL) A 2/3 · B 0/1 · C 2/3 · D 1/2; per-model (CAL) x 2/5 · y 3/4.

**Sign-off status (per Evidence Standard):** (1) the report **section schema** (Decision 1) — **ACCEPTED 2026-06-30** (§1–7, additively extensible; the two additive Unit-3 extensions in the Status line are tracked, not silent). Still open: (2) the public CLI shape `claim-audit calibrate` + the `cal` vs `claim-audit` name (deferred to Phase 5); (3) the κ-CI variance method (Wald → Bonett-Bergsma 2008) at gate time. Decision D's AC2 gate **threshold** remains PROPOSED — re-derive at Unit 3, do **not** inherit κ≥0.4.

**What changed:**
- `tests/v1/testing/bundles.py` — five base contents extracted as named constants; `CALIBRATION_CASES` 5→12 cycling them (4×3); builder logic unchanged (already generic over N bundles).
- `tests/v1/fixtures/calibration-synthetic/gold.yaml` — rewritten to 12 claims (gold_version `synthetic-2`), 4 conditions, 2 models, 3 starved, flags spread; header records the hand-checked aggregates + the CAL-column limitation.
- `tests/v1/test_calibrate.py` — pure-metric unit tests decoupled onto a fixed 5-pair `HAND_PAIRS` (values unchanged: κ 0.7222 / weighted 0.94915 / AC2 0.95263); packet/assembly/render/CLI assertions moved to the 12-claim numbers (κ 0.7647, exact 10/12, on-scale n=9, weighted 0.9854, AC2 0.9860, 4-row condition + 2-row model tables, partially_supported→not_checkable confusion cell).
- No `src/` change.

**Verification evidence (2026-06-30):** full suite **444 passed**; `ruff` / `ruff format --check` / `mypy --strict src` / `compileall` clean; source branch coverage **97%** (`--fail-under=95` PASS); `scripts/verify_install.py` green (both surfaces, clean wheel). `claim-audit calibrate` over the 12-claim packet: exact 10/12, κ 0.7647, recall 2/3, all 6 sections in fixed order with 4-row condition + 2-row model tables, **byte-identical report + all 12 traces across two runs** (manual `diff` empty + `test_calibrate_cli_is_byte_identical_across_runs`). Committed locally on `cal-v1-skeleton`; **not pushed** (git-history scrub pending).

**Build-register:** Phase 4 instrument validated on the synthetic boundary. Next: **Unit 3 (B18)** — the sealed PILOT-001 gate. Do **not** start before the acceptance procedure is rewritten against Decisions A/B/D/E and Decision D's AC2 threshold is re-derived (κ≥0.4 does not transfer). *(Superseded 2026-07-02: Decision G reclassifies PILOT-001 as the dev set; the gate moves to a fresh blind packet — see the next entries.)*

## 2026-07-02 — Decisions F + G: rule-semantics fixes (`cal-rules-v1.4.0`) + PILOT-001 → dev set — ACCEPTED

**Status:** Accepted (Cameron, review session 2026-07-02). Ratifies [adr-v1-rules-v1.4.0-semantic-fixes.md](../plans/adr-v1-rules-v1.4.0-semantic-fixes.md) (Decision F) and [adr-v1-pilot-001-dev-set.md](../plans/adr-v1-pilot-001-dev-set.md) (Decision G), plus the 2026-07-02 amendment to [adr-v1-lexicons.md](../plans/adr-v1-lexicons.md) (five new closed sets). Pre-gate correctness work on Phase-1/2 layers; no build-register ID.

**Why.** A pre-gate review probe (invented regulatory-style claims through the real pinned pipeline — no PILOT-001 material) showed the rule layer degrading or inverting correct NLI signals (≥0.95 entail) in 4/5 human-supported cases, two of them to `contradicted`. Root cause: lexical proxies deciding when to override the semantic signal — `verbatim = term_set(claim) ⊆ term_set(passage)` (the falsified v0.2 primitive) drove 6b's degree downgrade; A3's passage check reused the claim side's clause-level-only negation detector; 6a compared incomparable quantities at exact tolerance. The v0.2 category error, re-imported one layer up. New design-surface invariant: **no deterministic rule may flip or downgrade a degree on a lexical-overlap signal — overlap may flag, never decide.**

**What changed (Decision F):**

- **A3** — passage side now uses the broad `expresses_negation` (clause `neg` + determiner *no* + absence lexemes + `X-free`/`free of` forms); a passage expressing the same absence no longer flips an agreeing entail to `contradicted`. Claim side unchanged (narrow clause-level detector). `v1/features.py`, `v1/impl/rules.py`.
- **6b** — trigger is now a strength *comparison* (gold H2/H3): claim strong (`deontic_strength(claim)=="strong"` — the old PRESCRIBE set minus *should/ought* — or scope-gated universal) **and** passage `scope_strength=="weak"` (weak-deontic/hedge/partial-scope lexeme, no strong/universal lexeme). Plain assertive evidence never triggers; the not-verbatim proxy is gone. Trace `modal_strength` unchanged.
- **6a** — quantities compare only when **comparable** (equal unit names; year-like 1900–2100 unitless integers only against year-like); no comparable quantity → abstain. Claim-level approximation markers (*approximately/about/roughly/…*) widen tolerance to `approx_numeric_tolerance` (0.05, authored in the rules file, materialized into `AuditConfig`). Crux semantics + exact default unchanged.
- **Pipeline (F4)** — only retrieval results ≥ `retrieval_floor` are entailed; the full ranking is still recorded and A2 still reads it. A sub-floor passage can no longer win aggregation and reach A4 (NLI is miscalibrated off-topic). Side effect: fewer forward passes.
- **Verbatim (F5)** — 6c's flag trigger moves to `content_lemma_set` (spaCy lemmas minus DET/AUX/PART/PUNCT/NUM/SYM + stopwords; *approved/approves* unify). `term_set` has no remaining v1-rules callers.
- **Flag guard (F6)** — `inferred`/`false_caution` are dropped when the final degree is adverse (`overstated` retained; the composition fixture locks `contradicted`+`overstated`).
- **Calibration report** — additive `## 7. Rule fire rates` (per-rule claims-fired over the packet; the dev-iteration instrument + the "no Phase C rule dominates" sanity check). `v1/calibrate.py` (`RuleFireTally`, `_rule_fire_tallies`).
- **Rules file** — `cal-rules-v1.3.0.yaml` **removed**, `cal-rules-v1.4.0.yaml` added. SHA-256: **`2fb6711ebfe28d3defb4213e02f000315ec6117bc1a5754c6aa24d9863b93dcd`**.

**Decision G (process):** PILOT-001 (98 claims, single-coder gold) is **reclassified as the development set** — it was adaptation-contaminated by design (probes, thresholds, gold-heuristic study all fit to it). Dev iteration against it is now legitimate and labeled *dev*; the **confirmatory gate moves to a fresh blind packet** (fresh scaffold-run claims, pre-registered procedure, second coder on a subset to price the human agreement ceiling before Decision D's AC2 threshold is set). B18 and the Unit-3 brief re-point at this ADR.

**Golden-trace churn (deliberate, enumerated):** all 22 prior goldens regenerated — `audit_config_hash` changes unconditionally (new `rules_file_sha` + new `approx_numeric_tolerance` field) and entailment lists shrink where distractors sat below the floor (e.g. `inf-05` 3 retrieved / 0 entailed). **Zero verdict flips across all 22** (fixture inputs updated for two retargeted cases: e2e-07's passage gains *typically* so the composition case still exercises 6a+6b; hand-built 6a test features now carry real `unit="percentage"` values). Five new Decision-F regression goldens lock the probe cases end-to-end (18 agreeing-absence, 19 strong-claim-paraphrase, 20 approx-numeric, 21 year-abstain, 22 sub-floor-contradict-filtered). The 12-claim synthetic packet's verdicts, κ 0.7647, and all §1–6 aggregates are unchanged.

**Verification evidence (2026-07-02):** full suite **477 passed** (+33); `ruff check` / `ruff format --check` / `mypy --strict src` / `compileall` clean; source branch coverage **97%** (gate ≥95% PASS); `scripts/verify_install.py` green (clean wheel, v0.2 + v1 surfaces). Review probe re-run post-fix: **5/5 cases now match the human expectation** (previously 1/5). Two-run byte-identity green on stub and real-inference fixtures; `claim-audit calibrate` over the 12-claim packet byte-identical across runs with §7 rendered. Committed locally on `cal-v1-skeleton`; **not pushed** (git-history scrub pending).

**Next:** dev-set iteration on PILOT-001 (gold-join shim + starved list + pilot config from the Unit-3 prep, now dev tooling), rule-ablation review of the §7 fire rates, then commission the fresh blind packet per Decision G and rewrite the acceptance procedure against it.

## 2026-07-07 — Decision H (Stage 1): absence-route eligibility layer (`cal-rules-v1.5.0`) — ACCEPTED + LANDED

**Status:** Accepted + landed (Cameron, 2026-07-07) after the run-03 dev evidence and the STOP #1 three-call sign-off. Ratifies [adr-v1-absence-route.md](../plans/adr-v1-absence-route.md) (Decision H); execution governed by [absence-route-execution-plan.md](../plans/absence-route-execution-plan.md). **Stage 1 only** — Stage 2 (the bundle-relative absence route) was measured on run-03 and **held**. Pre-gate correctness work on the Phase-1 rule layer + the Phase-3 intake; no build-register ID.

**Why.** The run-01/02/03 dev misses are an **eligibility failure, not a recall failure**. Intake (`_to_passage`) never joined the passage to its `source_profile`, so `source_meta["trust_level"]` never arrived → rule 6d was **dead, not idle** (its guard field was always absent), and `A4`'s Phase-A short-circuit let a `background` fiction source solo-decide a contradiction (7 of 8 A4 fires in run-01). Max aggregation handed the verdict to the loudest raw NLI signal regardless of source or claim shape. run-03 (dev per Decision G) measured the fix: F4 clean by construction; Stage 2 net-negative on weighted κ → held.

**What changed (Stage 1):**

- **D1 — intake provenance join.** `_normalize_passages` passes each source's `bundle.source_profiles[source_id].trust_level` into `_to_passage`, which carries `trust_level` (`primary`/`secondary`/`background`) in `source_meta` unconditionally. Bundle passages therefore always carry the tier; only directly-constructed (non-intake) passages may lack it. `v1/intake.py`.
- **Rules — eligibility suppression loop.** `VerdictRules.apply` now wraps the unchanged Decision-C classifier (extracted verbatim to `VerdictRules._classify_once`) in a loop: it seeds from the pipeline's raw `support_signal`, and when the resulting degree is adverse and its contributing passage may not decide it, drops that passage's result and re-aggregates the eligible pool. **P1 (eligibility, D2):** a source whose `trust_level` is *present and not* `primary` may not solo-drive a terminal adverse degree — an **absent** `trust_level` (a non-bundle passage) is treated as eligible, so the gate never fires outside the apparatus path and pre-D1 behaviour is preserved. **P2 (A3-negation mirror, D3):** a negated claim whose contradicting passage itself expresses the negation agrees with the claim (MoNLI double-negation) → suppressed. **Landing** is emergent: an empty/all-neutral pool → B5 → `not_checkable/no_entail_signal` (never adverse). New invariant (extends Decision F): **eligibility gates adverse decisions; ineligible or self-agreeing evidence may flag, never decide.** `v1/impl/rules.py`.
- **6d** now receives real `trust_level` values (D1) and begins flagging `background`-contributing positive verdicts (0/98 → 19/98 on the dev packet). The impossible `"fictional"` member is deleted from `_BACKGROUND_TRUST_LEVELS` — the C-B vocabulary is `primary`/`secondary`/`background` (`contracts/cb_models.py`), and no valid bundle can carry `"fictional"`.
- **Rules file** — `cal-rules-v1.4.0.yaml` **removed**, `cal-rules-v1.5.0.yaml` added. **Thresholds are byte-identical to v1.4.0** (only the logic changed). SHA-256: **`99be5382f0e058a4a514bda96c532f28ad43c11c272864e643b9ccbb8e7d6251`**. `config.RULES_FILE_RESOURCE` bumped.
- **Stage 2 — HELD.** run-03 measured it net-negative on the ADR's own metric (weighted κ −0.118; recover : c008-like = 6 : 3, one being a gold-`contradicted` → `supported` distance-3 over-recovery). Not landed; it remains an explicit, documented option in the ADR.

**Golden-trace churn (deliberate, enumerated):** all 27 goldens (22 stub + 5 real-inference) regenerated — `audit_config_hash` changes unconditionally (new `rules_file_sha`; `fe43c923…` → `98c6609c…`). **Zero verdict flips, zero `rules_fired` changes.** The suppression loop is inert on the synthetic fixtures: none has a non-primary source driving an adverse verdict; `11-source-scope-error` already carried `trust_level: background` and stays `supported` + `source_scope_error` (positive verdicts are never suppressed); no fixture matches the P2 contradict-on-self-negation shape. One fixture *input* update: `test_source_scope_error_flag_for_background_passage`'s `trust_level` moved `fictional` → `background` (fictional is now impossible by design). New tests: intake join (`trust_level` on every passage; a background source round-trips); P1 suppression → eligible entail wins (c016 shape); P1 landing → `not_checkable` (c008 shape); P2 absence mirror.

**run-03 dev evidence (Decision G — never a gate):** F4 = **0/0** (no new gold-supported → CAL-`contradicted`, by construction). exact 63 → **62** (stage-1) → **68** (stage-1+2); weighted κ 0.3811 → **0.2319** → **0.1139**; AC2 0.8818 → **0.9515** → **0.9228**. Stage 1 is a **safety/provenance fix, not a metric win**: 0/4 gold-supported absence misses recover to `supported`; weighted κ falls because eligibility also suppresses the one *coincidentally-correct* fiction contradiction (`rsh-9a1e5f0994c2-c009`, gold `contradicted`) and moves the c008-family off-scale (on-scale n 77 → 70). **New finding:** P1 suppression *exposes* a surviving primary entail to A3, which flips it → `rsh-475fe956a5fb-c002` lands `contradicted` via a **primary** source (A3 never fired in run-01). Canary = 3 (c003/c005 subject-scope-shaped; c002 is the A3 artifact). Full evidence: `outputs/pilot-001-dev-calibration/run-03-absence-2026-07-07/` + the run-03 script committed at workbench `5cc216d`.

**Verification evidence (2026-07-07):** full suite **484 passed** (+5); `ruff check .` / `ruff format --check .` / `mypy --strict src` clean; source branch coverage **97%** (gate ≥95% PASS); `scripts/verify_install.py` green (clean wheel, v0.2 + v1 surfaces — the packaged `cal-rules-v1.5.0.yaml` loads from the wheel). Two-run byte-identity green on stub + real-inference fixtures and the `claim-audit calibrate` CLI. Committed locally on `cal-v1-skeleton`; **not pushed** (git-history scrub pending).

**Next:** draft the flag-based, non-lexical **subject-scope ADR** (the c003/c005 primary-source false-adverse cases) and **file the c002/A3 interaction** as its own defect (STOP #1 call 3 — draft only, don't build); then premise granularity → A1 imperative hardening → 6b passage inspection. The confirmatory gate remains a fresh blind packet per Decision G — PILOT-001 numbers never gate.
