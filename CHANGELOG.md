# Changelog

## Unreleased

CAL v1 build is in flight on branch `cal-v1-skeleton`. See
[`DECISIONS.md`](DECISIONS.md) § 2026-06-21 for the design lock and the project's
`plans/claim-audit-lab-v1-build-plan.md` for the build sequence. v0.2.0 stays the
shipped surface — apparatus consumers are pinned there — until v1 clears the
acceptance gate.

### Added (v1 scaffolding)

- `claim_audit_lab.v1` subpackage exposing `protocols`, `models`, `features`,
  `config`, and `impl` (see DECISIONS.md § 2026-06-21 § 1).
- Pinned-revision retriever and entailer (`BiEncoderRetriever`, `DeBERTaEntailer`)
  bound to pinned HF revision SHAs in the default config. Inference bodies were
  `NotImplementedError` stubs through Phase 1; wired to real CPU inference in Phase 2
  (see *Added (v1 Phase 2 — inference layers)* below).
- Concrete `MaxEntailmentAggregator` (pure data; no external dependency).
- `VerdictRules` skeleton with the documented six-step rule order; body wired in
  Phase 1.
- Four deterministic feature-extractor signatures (`has_numerical_value`,
  `has_explicit_negation`, `has_universal_quantifier`, `has_modal_strength`); bodies
  wired in Phase 1.
- Default `AuditConfig` shipped as package data at
  `claim_audit_lab/v1/configs/v1-default.yaml`; loadable via
  `claim_audit_lab.v1.load_default_audit_config()`.
- `[v1]` optional-dependency extra in `pyproject.toml` declaring the retrieve→entail
  inference stack (`quantulum3`, `spacy`, `sentence-transformers`, `transformers`,
  `torch`). Install with `pip install -e ".[dev,v1]"`. spaCy model:
  `python -m spacy download en_core_web_sm` post-install.
- Clean-venv wheel install of `[v1]` extra exercised by
  `scripts/verify_install.py` alongside the existing v0.2 surface check.

### Pinned (v1)

- Retriever: `sentence-transformers/all-MiniLM-L6-v2` @
  `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.
- Entailer: `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli` @
  `6f5cf0a2b59cabb106aca4c287eed12e357e90eb`.
- Resolved via the HF API on 2026-06-22.

### Added (v1 Phase 2 — inference layers, B10–B13)

- Real `BiEncoderRetriever` (`sentence-transformers/all-MiniLM-L6-v2`): CPU,
  deterministic, loaded from the pinned revision SHA; embeds claim + passages once
  per call, ranks by cosine, returns top-`k` (retrieval-floor filtering stays the
  rules-layer `A2` gate's job). Process-level model cache; unpinned revision raises.
- Real `DeBERTaEntailer` (`MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`): CPU,
  `eval()` + `no_grad()`, MNLI/FEVER `(premise, claim)` tokenization, label via the
  model's `id2label`, softmax-max `score`, and **unrounded** three-class `raw_logits`
  in native class order for downstream re-thresholding. Same cache + guard.
- `claim_audit_lab.v1.impl._determinism.enforce_cpu_determinism()` — the v1 CPU
  determinism baseline (`torch.set_num_threads(1)` + `torch.manual_seed(0)`),
  enforced at module load by the retriever and entailer.
- End-to-end byte-identity over real inference: `tests/v1/test_byte_identity.py`
  (5 claims × 3 passages, real retriever + entailer + aggregator + rules) with 5
  committed golden traces under `tests/v1/fixtures/traces/inference/` (regenerate
  with `CAL_WRITE_GOLDENS=1`).
- Per-layer determinism + behaviour tests (`test_retriever.py`, `test_entailer.py`)
  and a YAML field-order/whitespace `audit_config_hash`-invariance test (B12 parity).

### Fixed (v1)

- `MaxEntailmentAggregator` no longer lets a confidently-neutral passage mask a
  real entail/contradict signal: it now ranks only support-bearing (non-neutral)
  results and abstains to neutral only when every candidate is neutral. Surfaced by
  real inference (`inf-01` / `inf-03` were flipping to `not_checkable`); the
  `SupportSignal` contract and rules layer are unchanged. Residual: genuinely
  conflicting evidence (strong entail + strong contradict on one claim) still
  carries only the higher-scoring signal — a documented, calibration-gated
  limitation; the two-signal redesign is the upgrade. See DECISIONS.md § 2026-06-29
  (neutral-masking fix).

### Added (v1 Phase 3 — apparatus intake, B14–B16)

- **B14 — `AuditRequest` normalizer.** `claim_audit_lab.v1.intake.bundle_to_requests`
  converts a loaded C-B `BundleContents` into one `AuditRequest` per auditable
  (`extracted_claim`) claim; `retrieval_seed` records are skipped. Each request
  carries the bundle's *full* passage set (the retriever, not the bundler, picks
  candidates — DECISIONS.md § 2026-06-21 § 2); passages use the globally-unique
  `{source_id}/{passage_id}` handle with raw C-B coordinates + hash preserved in
  `source_meta`. YAML is parsed once at `load_bundle`; everything downstream is
  frozen pydantic. Re-exported as `claim_audit_lab.v1.bundle_to_requests`.
- **Dual-path selector.** New optional `CBAuditConfig.pipeline`
  (`"v0.2-lexical" | "v1-retrieve-entail"`, default `v0.2-lexical`) selects which
  auditor a bundle routes through. Optional + v0.2-default, so existing/external
  bundles validate unchanged, keep their `config_hash`, and route v0.2; opting into
  v1 means writing+sealing the field. v1 inference always uses the pinned
  `load_default_audit_config()`, not the bundle's thresholds. See DECISIONS.md
  § 2026-06-29 (Phase 3 Unit 1). Routing on the selector lands in B15.
- **B15 — `audit-bundle` v1 routing + trace writeback.** `claim-audit audit-bundle`
  now branches on `CBAuditConfig.pipeline`. The `v1-retrieve-entail` path normalizes
  → runs the pinned v1 pipeline (`v1.runner.run_default_audit`) → writes
  `claims/{claim_id}.audit-trace.json` (replay-sufficient) into the audited copy and
  populates each per-claim YAML `audit` block via the v1→C-B verdict crosswalk
  (`v1.cb_writeback.cb_support_verdict`: `contradicted`→`unsupported`, `overstated`
  flag collapses a positive degree, `not_checkable` stays `not_checkable` —
  DECISIONS.md § 2026-06-29 Phase 3 Unit 2). `SHA256SUMS` + `bundle_hash` are resealed
  over the augmented file set. The default `v0.2-lexical` path is unchanged and
  byte-identical to before. Torch is imported lazily on the v1 branch only.
- **No loader change needed for v1 routing.** A v1 bundle carries a v0.2-policy-shaped
  `CBAuditConfig` + the `pipeline` field, so the existing fail-closed policy gate
  admits it untouched (Unit 1's forward note was wrong; corrected in the Unit 2 ADR).
- **B16 — apparatus round trip + typed audited loader.** The integration harness now
  builds Evidence Bundler's real `scaffold-run-minimal` fixture through its
  `build-fixture-bundle` CLI, opts the generated C-B copy into v1 while recomputing the
  audit-config and bundle integrity hashes, audits it with pinned metadata, and reloads
  the audited copy through both `load_bundle` and the new
  `claim_audit_lab.v1.load_audited`. `load_audited` returns an additive
  `AuditedBundleContents` subtype with strict `AuditTrace` objects keyed by claim ID;
  it delegates all C-B/YAML verification to `load_bundle` before validating trace JSON
  and claim bindings. The fixture has no expected-outputs file, so the test explicitly
  grounds and locks `clm-001` as C-B `supported`, v1 `supported`, no reason sub-label,
  and an `entail` signal. Runnable, path-portable instructions and the synthetic-only
  limitation are in `docs/v1-round-trip.md`.

### Changed (v1 Phase 3 — internal)

- `contracts/serialization.py`: extracted public `reseal_bundle()` + `write_sha256sums()`
  (were private in `output_writer.py`); both the v0.2 and v1 writebacks share them.
  v0.2 audited-bundle output is byte-identical pre/post the refactor.
- `contracts/audit_flags.py`: extracted public `is_material_deviation()`; `compute_flags`
  refactored onto it (behaviour identical), and the v1 writeback reuses it.

### Added (v1 Phase 4 — Unit 1 / B17 — `calibrate`)

- `claim-audit calibrate --packet --gold --config --out --traces-out --pinned-at`: runs the
  v1 pipeline over a packet of C-B bundles, scores each claim against a blind gold, and writes
  a deterministic Markdown calibration report + one `AuditTrace` JSON per claim. Synthetic
  boundary only — it does not run the sealed PILOT-001 gate and applies no pass/fail thresholds.
- Built against the **shipped two-axis verdict** (DECISIONS.md § 2026-06-29 Phase 4 Unit 1):
  a 5×5 `support_verdict` confusion matrix with `overstated`/`inferred` on a separate flags
  axis; the gold is crosswalked via the 3 explicit mappings. Report timestamp is the
  `--pinned-at` value only (no wall clock), so two runs are byte-identical.
- Metric suite (`v1/calibrate.py`, stdlib only): exact agreement; Cohen's κ + simplified-Wald
  95% CI; Gwet AC2 + ordinal quadratic weighted-κ (Decision D, prevalence-robust); 5×5
  confusion; flags table; adverse-rate `(unsupported+contradicted)/checkable` overall +
  per-condition + per-model; recall floor on starved claims. **No gate threshold is baked in**
  (Decision D stays PROPOSED → re-derived under AC2 at Unit 3).
- `claim_audit_lab.v1.config.load_audit_config(path)`: load operational knobs from a YAML path
  while still materializing verdict thresholds + `rules_file_sha` from the pinned rules file.
- The engine is torch-free (the auditor is injected); heavy inference imports stay local to the
  CLI command, so the v0.2 path never loads torch.

### Added (v1 Phase 4 — Unit 2 — synthetic dry run + report schema)

- The canonical synthetic calibration packet grew **5→12 claims** (4 conditions × 3, 2 models,
  3 starved) to exercise every report section with >2-row tables before the PILOT-001 gate. It
  reuses the five committed-golden contents under twelve claim_ids, so every CAL verdict stays
  deterministic and hand-checkable (CAL columns confined to {supported, contradicted,
  not_checkable}; the gold spans all five degrees).
- The report **section schema** is pinned for sign-off in DECISIONS.md § 2026-06-30 (8 fixed
  headers + per-section column contract + determinism contract). **PROPOSED** — not self-approved.
- Pure-metric unit tests decoupled onto a fixed 5-pair `HAND_PAIRS` (κ 0.7222 / weighted 0.94915 /
  AC2 0.95263, unchanged); packet/assembly/CLI tests assert the 12-claim numbers (exact 10/12,
  κ 0.7647 = 13/17, on-scale n=9, weighted-κ 0.9854, Gwet AC2 0.9860). Byte-identical across two
  runs. No `src/` change; no gate run; Decision D threshold still deferred to Unit 3.

### Added (v1 Phase 4 — Gold Lite ten-claim DEV rehearsal, 2026-07-11)

- `scripts/gold_lite_review.py` adds a project-local, non-public rehearsal tool that reuses
  CAL's fail-closed C-B loader, selects ten PILOT-001 parent claims by a fixed SHA-256 seed,
  verifies proposed atomic decompositions, and writes a blinded self-contained local browser
  reviewer. It hides old gold, CAL outputs, condition/model, EB role/rank, and trust labels;
  binds human rationales to passage hashes; validates additive checkpoint exports; and derives
  transparent `single` / `all_of` parent results. It does not change package source, rules,
  config, the public CLI, or the acceptance procedure.
- `tests/v1/test_gold_lite_review.py` adds 12 fast tests for deterministic selection, packet
  hash drift, blinded shape, byte-stable generation, rationale requirements, checkpoint
  handling, and compound aggregation. The real local packet is 10 parents / 17 proposed
  steps / 50 retained parent-level EB candidates with packet hash
  `sha256:7ed7cd4763efd079668296dd17e4d74a80aebfdcbd2035e53acd2699a3bc2bd8`.
- Verification: **503 passed**, Ruff check/format, mypy `--strict src`, compileall,
  **97% source branch coverage**, clean-wheel v0.2/v1 verification, two-build packet byte
  identity, and local browser smoke all green. Human review has not started; this remains DEV,
  never validation or gate evidence.
- `scripts/anthropic_api_bridge.py` and `scripts/gold_lite_model_panel.py` add an optional,
  project-local model-assistance experiment. The bridge uses the Basic Research Harness
  Anthropic SDK runtime read-only, counts each request, performs one API call, and preserves the
  raw receipt. The panel prepares blinded per-parent requests, validates exact packet/provenance
  coverage, preserves model failures, derives strict silver candidates, and writes a separate
  post hoc majority-triage sheet. It does not add an Anthropic package dependency to CAL.
- `tests/v1/test_gold_lite_model_panel.py` covers prompt blinding, pinned model tiers,
  API-supported schema constraints, packet/provenance normalization, raw receipt hashing,
  refusal handling, exact-vote aggregation, and the distinction between strict silver and
  majority assistance. The real DEV run preserved 40 receipts, validated 31, produced 2/17
  strict silver atoms, and offered 11 strong / 2 weak / 4 unresolved assistance suggestions.

### Added (v1 Phase 4 — PILOT-001 DEV prototypes, 2026-07-10)

- `scripts/pilot001_premise_granularity_run04.py` plus focused tests: a deterministic
  coarse-to-fine replay over the 16 v1.5.0 raw-neutral DEV claims. The S1 sentence and
  S1+S2 adjacent-window variants are experiment tooling only; neither changes package
  code or the frozen rules resource. Both were rejected after zero recoveries, one
  regression, and new gold-supported → CAL-`contradicted` cases.
- `scripts/pilot001_a1_imperative_run05.py` plus focused tests: a full-trace replay of a
  structural A1 prefix guard. The candidate changes exactly two false imperative stops
  and no other verdicts on the 98-claim DEV set. It is sign-off evidence, not a package
  landing; `sentence_type()` and `cal-rules-v1.5.0` remain unchanged.

### Fixed (wheel verification hygiene, 2026-07-11)

- `scripts/verify_install.py` now deletes setuptools' generated `build/` tree before
  building the verification wheel. This prevents deleted package-data files from a prior
  build from leaking into a nominally clean wheel. The installed-v1 smoke also asserts
  that the wheel contains exactly `cal-rules-v1.5.0.yaml` and no retired rules resources.
- Verification after this change: **491 tests**, Ruff check/format, mypy strict,
  compileall, **97% source branch coverage**, and the rebuilt-wheel v0.2/v1 surface checks
  all green.

### Changed (v1 — `cal-rules-v1.5.0`, Decision H absence-route Stage 1)

See DECISIONS.md § 2026-07-07. Rule **logic** changed; **thresholds unchanged** from v1.4.0.

- **Intake provenance join (D1):** every passage now carries its source `trust_level`
  (`primary`/`secondary`/`background`) in `source_meta`, joined at `v1/intake.py` from the bundle's
  `source_profiles`. This is the provenance the eligibility rules read at verdict time.
- **Eligibility suppression loop:** `VerdictRules.apply` wraps the unchanged Decision-C classifier
  (`_classify_once`) in a loop that refuses to let an ineligible source (non-`primary`, **P1**) or a
  self-negating passage on a negated claim (**P2**) solo-drive a terminal adverse degree; the
  suppressed contradiction falls through to the best remaining eligible signal, or to
  `not_checkable/no_entail_signal`. New invariant: eligibility gates adverse decisions; ineligible or
  self-agreeing evidence may flag, never decide. An absent `trust_level` (a non-bundle passage) is
  treated as eligible, so pre-D1 behaviour is preserved.
- **Rule 6d** now flags `background`-contributing positive verdicts (the provenance field finally
  arrives); the impossible `"fictional"` trust tier is removed.
- **`cal-rules-v1.4.0.yaml` → `cal-rules-v1.5.0.yaml`** (SHA-256
  `99be5382f0e058a4a514bda96c532f28ad43c11c272864e643b9ccbb8e7d6251`). All 27 goldens regenerated
  (`audit_config_hash` only; **zero verdict flips**). Stage 2 (bundle-relative absence route) was
  measured on the run-03 dev set and **held** (net-negative weighted κ). Dev-only per Decision G;
  the confirmatory gate stays a fresh blind packet.

## 0.2.0 - 2026-06-13

Claim Audit Lab v0.2 stabilizes the public package and binds the C-B research-apparatus
path to one deterministic policy.

### Added

- Packaged contract resources and demo fixtures loaded through `importlib.resources`.
- Clean-wheel verification for `--help`, `demo`, and `audit-bundle`.
- `ClaimType.unclassified`, with native extraction skipping it and C-B audits returning
  `not_checkable`.
- Public `audit_claims(...)` orchestration and shared contract serialization helpers.
- Claim-scoped C-B evidence and separately linked counterevidence.
- Default human-readable reports from `audit-bundle`.
- `--audit-run-id` and `--audited-at` for byte-identical audited bundles.
- Threshold, strong-wording, counterevidence, config-drift, classifier-parity, and
  reproducibility tests.

### Changed

- Replaced duplicate classifiers with one governed priority:
  prediction, scope, causal, comparative, credential, capability, numeric,
  interpretive, unclassified.
- Consolidated tokenization, stemming, stopwords, date/number handling, and trigger
  vocabularies.
- Bound C-B audit intake to the exact frozen `cal-rules-v1.2.0` profile.
- Defined the support signal as `max_support - 0.3 * max_counterevidence`, clamped to
  `[0, 1]`.
- Froze candidate, partial, sourced, and false-caution boundaries at `0.40`, `0.55`,
  `0.80`, and `0.85`.
- Made linked counterevidence prevent a clean `supported` verdict.
- Made strong-wording suppression require the same trigger in direct evidence and no
  conflicting counterevidence.
- Replaced `ClaimAssessment.suggested_rewrite` with populated
  `rewrite_guidance: list[str]`.
- Regenerated checked-in examples and documented scores as supplied-evidence signals,
  never truth probabilities.
- Made Ruff formatting part of the release gate.

### Removed

- Dead `AuditConfig.strictness`.
- Cross-module use of private audit helpers.
- Redundant direct `rich` dependency.
- Internal phase-number language and stale workspace paths from public output.

### Verification

- 213 tests pass.
- Ruff lint and formatting, strict mypy, and compileall pass.
- Source branch coverage is 96%.
- A clean wheel passes `--help`, `demo`, and `audit-bundle`.
- Checked-in examples regenerate byte-identically.
- The synthetic Harness -> Evidence Bundler -> Claim Audit Lab round trip passes.
- The sealed 98-claim pilot replay is byte-identical with pinned run metadata.

Research qualification remains open. Blind calibration is `0/98`; human verdicts remain
primary until the documented agreement, kappa, adverse-recall, and per-condition error
gates pass.

## 0.1.0 - 2026-05-05

Initial CLI-first public release.

- Added deterministic supplied-evidence claim auditing.
- Added Markdown and plain-text draft loading.
- Added YAML and JSON evidence-bundle loading.
- Added conservative claim extraction and evidence matching.
- Added support labels, risk labels, rule flags, Markdown reports, and typed JSON.
- Added `claim-audit audit`, `claim-audit demo`, and the first C-B `audit-bundle` path.
- Added two fictional example families and validation-inspired IQ/OQ/PQ records.
- Added MIT licensing and public package metadata.

Known v0.1 limits included no source discovery, no live model calls, no web UI, no
research calibration, and no regulated-compliance claim.
