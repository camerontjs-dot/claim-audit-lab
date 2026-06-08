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
