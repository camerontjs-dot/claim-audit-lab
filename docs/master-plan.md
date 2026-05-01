# Claim Audit Lab Master Plan

status: active
last_updated: 2026-05-01
asset: portfolio/live-asset/claim-audit-lab

Purpose: keep one living plan for Claim Audit Lab from first implementation through public packaging. Update this file as the build moves, and use it as the first planning read after `README.md`.

## Current State

Claim Audit Lab has a scaffold, a verified typed contract layer, verified draft/evidence loaders, verified conservative claim extraction, verified deterministic evidence matching, a verified Phase 4A runnable vertical slice, verified deterministic rule checks and support assessment, verified audit orchestration hardening, verified Phase 7 report rendering, a verified Phase 8 CLI workflow, a reviewed hand-authored AI research target report, a generated human-review AI research report, and two fictional draft/evidence fixture families. The next implementation slice is completing generated report artifacts for the second fixture family.

Current durable files:

- `README.md`: public-facing stub and project boundary.
- `docs/validation-matrix-reference.md`: requirement matrix, fixture coverage, and acceptance rules.
- `docs/target-report-prompt.md`: prompt for hand-writing the AI research memo target report before renderer implementation.
- `docs/phase-4-evidence-matching-plan.md`: implemented Phase 4 design record for deterministic evidence matching.
- `docs/phase-6-audit-orchestration-plan.md`: implemented Phase 6 contract for hardening `audit_document(...)`.
- `examples/reports/ai-research-note.target.md`: reviewed hand-authored target report and future golden-file reference for the AI research memo fixture.
- `docs/research-use.md`: adjunct for scaffold-evaluation measurement rules, outside the v1 shipping path.
- `validation/`: first-class validation package with IQ/OQ/PQ-inspired protocols, run records, and deviation log.
- `docs/verification.md`: checks run and verification notes.
- `docs/handoff-prompt.md`: next implementation prompt for Phase 9 example families.
- `examples/drafts/ai-research-note.md`: first fictional draft fixture.
- `examples/evidence/ai-research-evidence.yml`: first fictional evidence fixture.
- `examples/drafts/product-readme-note.md`: second fictional draft fixture for product-copy claims.
- `examples/evidence/product-readme-evidence.yml`: second fictional evidence fixture with dated test-output and limitation sources.
- `tests/fixtures/`: loader-focused plain text, JSON, empty-evidence, malformed-evidence, and missing-field fixtures.
- `src/claim_audit_lab/`: module skeleton.
- `src/claim_audit_lab/models.py`: strict Pydantic contract layer.
- `src/claim_audit_lab/loader.py`: path-aware draft and evidence bundle loader.
- `src/claim_audit_lab/claim_extraction.py`: conservative deterministic claim extraction.
- `src/claim_audit_lab/evidence_matching.py`: deterministic candidate-evidence matching.
- `src/claim_audit_lab/auditor.py`: Phase 6-hardened audit orchestration returning typed `AuditReport` values with rule-assessed labels.
- `src/claim_audit_lab/report.py`: Phase 7 human-review Markdown and typed JSON report rendering.
- `src/claim_audit_lab/rules.py`: deterministic rule checks and support assessment.
- `src/claim_audit_lab/cli.py`: Phase 8 `claim-audit` CLI with `audit` and `demo` subcommands.
- `scripts/run_demo.py`: reviewer-friendly report demo entry point.
- `examples/reports/ai-research-note.slice.md`: generated Phase 7 human-review report.
- `examples/reports/ai-research-note.slice.json`: generated Phase 7 typed report data.
- `tests/test_models.py`: first model validation tests.
- `tests/test_loader.py`: loader behavior and malformed-input tests.
- `tests/test_claim_extraction.py`: extraction behavior, classification, stable ID, and dedupe tests.
- `tests/test_evidence_matching.py`: numeric, product-fixture, ordering, capping, metadata, and batch-matching tests.
- `tests/test_rules.py`: deterministic rule checks, label mapping, freshness, and rule-ID tests.
- `tests/test_auditor.py`: Phase 6 auditor contract, trace-link, summary, deterministic-output, and edge-case tests.
- `tests/test_report.py`: Phase 7 report sections, label, evidence-link, JSON, fixture-sync, and language-gate tests.
- `tests/test_cli.py`: Phase 8 CLI help, output, malformed-input, high-risk-success, demo, and language-gate tests.
- `tests/test_vertical_slice.py`: reviewer demo, output path, JSON round-trip, and language-gate tests.

Immediate next step:

1. Complete Phase 9 example families.
2. Generate Markdown and JSON reports for the Product README fixture without changing audit semantics.
3. Preserve local-only behavior: no network calls, API keys, or live LLM calls in normal tests or demo runs.

## Project Boundary

Claim Audit Lab audits support from supplied evidence.

It does not:

- verify external truth
- call statements true or false
- call itself a fact checker
- replace source review
- require live LLM calls in v1
- require network access for normal tests or demo runs
- use private application materials in public fixtures

Preferred wording:

- "supported by supplied evidence"
- "partially supported"
- "not supported by the provided evidence"
- "requires a source"
- "the tool cannot verify the source itself"

Avoid capability wording such as:

- "true"
- "false"
- "fact checked"
- "verified"
- "proven"

## User Experience Direction

The public experience should feel like a claim stress test, not a truth oracle. A user may ask a natural question such as "is this supported?" or "how true is this?", but the tool should translate that into an evidence-support audit:

- Which parts of the claim are supported by the available evidence?
- Which parts are weak, missing, overstated, too broad, or not audit-ready?
- What exact evidence, rule, or limitation caused the claim to break down?
- What rewrite would make the claim better match the evidence?

Avoid presenting a single unsupported "percent true" number. If a numeric score is added, split it into at least two concepts:

- `support_score`: how strongly the available evidence supports the claim or subclaim.
- `assessment_confidence`: how confident the tool is in its own assessment, based on evidence coverage, rule clarity, source quality, and ambiguity.

The strongest future UX pattern is atomic claim decomposition. Instead of scoring a complex sentence as one blob, the system should break it into smaller auditable subclaims, score each subclaim, identify the weakest supported part, and then produce an overall support assessment.

Example:

- Claim: "The checklist clearly eliminates unsupported claims in multi-step AI research workflows."
- Supported component: unsupported claims decreased in the test set.
- Breaking points: "eliminates", broad workflow generalization, and future certainty.
- Final answer: `overstated`, with a support score and suggested rewrite only after scoring rules are implemented and tested.

Current naming:

- Working project name: `Claim Audit Lab`.
- Public framing to preserve: "claim stress test" and "evidence-support audit".
- The reviewed target report did not force a naming change.
- Keep the public product name as `Claim Audit Lab` for now.
- Keep the repo/package name as `claim-audit-lab` for now.

## Research Use Adjunct

Research-measurement rules live in `docs/research-use.md`. They should not block v1 portfolio shipping unless Claim Audit Lab is actually being used as a measurement instrument for a scaffold-evaluation study.

## Definition Of Done

The first public version is ready when:

- The package installs locally with `python -m pip install -e ".[dev]"`.
- The CLI command `claim-audit` is available.
- The CLI can audit at least two fictional draft/evidence examples.
- The audit engine returns typed `AuditReport` models.
- Markdown and JSON reports are generated from checked-in examples.
- Tests cover models, loaders, extraction, matching, rules, auditor, reports, and CLI behavior.
- Report-quality tests prevent placeholder output and forbidden capability language.
- The README explains what the tool does, what it does not do, how to run it, labels, rule checks, validation cases, and limitations.
- Example fixtures are fictional or sanitized.
- Normal tests and examples require no API keys, network calls, or live LLM calls.
- `docs/validation-matrix-reference.md` statuses reflect actual evidence, not intention.
- `validation/README.md` is linked from the README, master plan, and validation matrix before the post-build qualification pass.
- Social card and GitHub-pin assets are complete enough for the public repo.

## Phase Plan

### Phase 0: Planning And Scaffold

Status: complete.

Delivered:

- Live asset folder created.
- Package scaffold created.
- README stub created.
- First fictional draft and evidence fixtures created.
- Validation matrix reference created and expanded.
- Implementation handoff prompt created.

Exit gate:

- Scaffold compiles.
- Project boundary is visible in README and planning docs.

### Phase 1: Typed Contract Layer

Status: complete.

Primary files:

- `src/claim_audit_lab/models.py`
- `tests/test_models.py`
- `examples/evidence/ai-research-evidence.yml`

Build:

- `StrictBaseModel` using Pydantic v2 and `ConfigDict(extra="forbid")`.
- Literal label aliases for support labels, risk labels, claim types, source reliability, strictness, and any source-type labels we decide to constrain.
- Input models: `EvidenceExcerpt`, `EvidenceSource`, `EvidenceBundle`, `DraftDocument`.
- Config model: `AuditConfig`.
- Intermediate models: `Claim`, `EvidenceCandidate`, `RuleFlag`.
- Output models: `ClaimAssessment`, `AuditSummary`, `AuditReport`.

Validation requirements:

- Reject unknown fields.
- Reject blank IDs and blank required text.
- Reject invalid constrained labels.
- Reject duplicate source IDs.
- Reject duplicate excerpt IDs across an evidence bundle.
- Allow empty evidence bundles.
- Bound candidate scores from `0.0` to `1.0`.
- Require positive `freshness_days`.
- Bound `min_overlap_score` from `0.0` to `1.0`.
- Require `max_candidate_evidence >= 1`.
- Ensure `AuditReport` serializes to a JSON-shaped dict.

Exit gate:

- `python3.11 -m compileall -q src tests`
- `python3.11 -m pytest`
- `CAL-REQ-019`, `CAL-REQ-020`, and the model portion of `CAL-REQ-029` are implemented or verified.

### Phase 2: Loaders

Status: complete.

Primary files:

- `src/claim_audit_lab/loader.py`
- `tests/test_loader.py`
- malformed fixture files under `examples/evidence/` or `tests/fixtures/`

Build:

- Load Markdown and plain text drafts into `DraftDocument`.
- Load YAML and JSON evidence bundles into `EvidenceBundle`.
- Keep parsing errors separate from audit findings.
- Provide clear validation errors that identify the file and bad field where practical.

Exit gate:

- Valid Markdown, plain text, YAML, and JSON inputs load.
- Malformed YAML/JSON exits through a clear loader error.
- Missing required fields fail.
- Empty but valid evidence bundles load.
- `CAL-REQ-002`, `CAL-REQ-003`, and loader portions of `CAL-REQ-015` are covered.

### Phase 3: Conservative Claim Extraction

Status: complete.

Primary files:

- `src/claim_audit_lab/claim_extraction.py`
- `tests/test_claim_extraction.py`

Build:

- Deterministic first-pass extraction.
- Prefer missing vague content over inventing claims.
- Identify numeric, causal, comparative, credential, prediction, capability, scope, and interpretive claims.
- Track stable claim IDs and source spans or paragraph references where practical.
- Handle duplicate or near-duplicate claims without inflating summary counts.

Exit gate:

- Fixture claims extract predictably.
- Vague/non-claim sentences are ignored.
- Every claim type has at least one test fixture before public release.
- `CAL-REQ-004`, `CAL-REQ-023`, and extraction parts of `CAL-REQ-029` are covered.

### Phase 3A: Target Report And Fixture Design

Status: complete.

Primary files:

- `docs/target-report-prompt.md`
- `examples/reports/ai-research-note.target.md`
- `examples/drafts/`
- `examples/evidence/`
- `docs/research-use.md`

Build:

- Hand-authored aspirational AI research memo Markdown report exists before report rendering is coded.
- Target report is clearly marked as hand-authored target output, not generated output.
- Added a second fictional Product README fixture family before evidence matching and rule design are tuned around the AI research memo.
- Public-facing name/framing reviewed after the target report; keep `Claim Audit Lab` with "claim stress test" / "evidence-support audit" framing for now.
- Keep research-measurement rules in `docs/research-use.md` rather than the v1 shipping path.
- Add or confirm the stable ID design note before Phase 4 lands.

Exit gate:

- `examples/reports/ai-research-note.target.md` exists, has been reviewed, and is useful as a UX spec and future golden-file reference.
- The second fixture family has at least a draft and evidence bundle.
- The public-facing name/framing decision is recorded or deliberately deferred with a dated reason.
- Research-use requirements are discoverable in `docs/research-use.md` but are not v1 shipping gates.

### Phase 4: Evidence Matching

Status: complete.

Primary files:

- `docs/phase-4-evidence-matching-plan.md`
- `src/claim_audit_lab/evidence_matching.py`
- `tests/test_evidence_matching.py`

Build:

- Transparent deterministic scoring.
- Match on numbers, dates, key terms, quoted phrases, and overlap.
- Preserve source IDs, excerpt IDs, reliability labels, and scores.
- Keep matching separate from support assessment.

Delivered:

- `match_evidence(...)` returns sorted, capped `EvidenceCandidate` links for one claim.
- `match_claims_to_evidence(...)` returns a dictionary keyed by stable claim IDs.
- Candidate scoring uses deterministic number, date, term, phrase, comparison, and limitation signals.
- Candidate links preserve source reliability and source date metadata.
- Numeric mismatch candidates are capped below high-score territory.

Exit gate:

- Matching numeric claims link to matching evidence.
- Differing values do not appear fully supported.
- Multiple candidate evidence sources preserve reliability and support differences.
- Candidate scores remain bounded.
- `CAL-REQ-005` is covered.
- The evidence-matching portion of `CAL-REQ-024` is covered, but the row remains planned until rule/report portions are covered.

### Phase 4A: Runnable Vertical Slice

Status: complete.

Primary files:

- `src/claim_audit_lab/auditor.py`
- `src/claim_audit_lab/report.py`
- `scripts/run_demo.py` or equivalent reviewer-friendly entry point
- `tests/test_vertical_slice.py` or focused auditor/report tests
- `examples/reports/ai-research-note.slice.md`
- `examples/reports/ai-research-note.slice.json`

Build:

- Wire a trivial-but-complete path: extraction -> naive candidate matching -> `audit_document()` -> minimal Markdown report.
- Keep final rule quality deliberately thin; deeper rule checks still belong in Phase 5.
- Let a reviewer run one documented local command and see a checked-in fixture produce report output before the CLI is complete.
- Use only `needs_source` and `not_audit_ready` in Phase 4A so candidate scores do not harden into support semantics before Phase 5.
- Keep the vertical slice deterministic and offline.

Delivered:

- `audit_document(draft, evidence_bundle, config=None) -> AuditReport` wires extraction, candidate matching, provisional assessments, summary counts, and limitations.
- `AuditConfig` is threaded into candidate matching, including overlap threshold and candidate cap behavior.
- Minimal Markdown and JSON renderers expose summary, claim register, candidate evidence links, and limitations.
- `scripts/run_demo.py` writes default demo outputs to gitignored `build/reports/` and only refreshes checked-in slice fixtures with `--update-fixture`.
- `examples/reports/ai-research-note.slice.md` and `.json` are checked-in provisional outputs with a visible Phase 4A caveat.
- `tests/test_vertical_slice.py` gates provisional labels, config behavior, empty-evidence behavior, JSON round-trip, demo-script output, and forbidden capability language in the checked-in slice report.

Exit gate:

- A fresh local install can run the demo entry point against checked-in fixtures.
- The report output includes at least a summary, claim register, candidate evidence links, and limitations.
- The slice does not claim full rule coverage or external truth verification.
- `audit_document()` exists early, even if later phases harden the internals.

### Phase 5: Rule Checks And Support Assessment

Status: complete.

Primary files:

- `src/claim_audit_lab/rules.py`
- `tests/test_rules.py`

Build:

- Rule checks stay separate from evidence matching.
- Map findings to support labels and risk labels.
- Flag unsupported numbers, dates, deadlines, public-link claims, credentials, causal overreach, unsupported comparisons, overconfident language, stale sources, low-reliability-only support, and future certainty.

Delivered:

- `assess_claim_support(...)` returns deterministic `ClaimAssessment` values from a claim, supplied evidence bundle, candidate evidence, and optional config.
- `AuditConfig.reference_date` makes freshness checks opt-in and deterministic.
- `EvidenceCandidate.source_url` preserves source URL metadata for public-link rules.
- Rule flags use deterministic IDs derived from claim ID, rule code, and pinned trigger context.
- The AI research slice now matches the target report labels: `overstated`, `supported`, `partially_supported`, and `overstated`.
- Empty evidence bundles keep the Phase 4A behavior: all extracted claims are marked `needs_source` with an evidence-bundle warning.
- `audit_document(...)` lightly integrates rule assessment, flattens report-level rule flags, and rebuilds summary counts for support labels and high-risk claims.
- The minimal slice renderer shows Phase 5 support labels and rule flags while leaving full report rendering to Phase 7.

Exit gate:

- Every rule check in the plan has at least one test.
- Every Phase 5-emitted support label can be produced by a fixture or direct unit test.
- `not_audit_ready` remains in the model vocabulary, but Phase 5 rule-assessed outputs do not emit it in normal runs.
- Risk labels are constrained and tested.
- `CAL-REQ-006` through `CAL-REQ-011`, `CAL-REQ-021`, `CAL-REQ-022`, and rule parts of `CAL-REQ-029` are covered.

Tie-off verification:

- Rechecked on 2026-05-01 with compileall, pytest, ruff, mypy, and coverage.
- Current result: 74 pytest tests passed and total coverage is 95%.

### Phase 6: Audit Orchestration Hardening

Status: complete.

Primary files:

- `docs/phase-6-audit-orchestration-plan.md`
- `src/claim_audit_lab/auditor.py`
- `tests/test_auditor.py`

Build:

- Harden `audit_document(draft, evidence_bundle, config=None) -> AuditReport` after the Phase 5 rule-assessed slice.
- Coordinate extraction, matching, rules, summary metrics, limitations, and evidence bundle warnings.
- Treat high-risk findings as valid audit results, not runtime failures.
- Empty evidence bundles return useful output rather than crashing.
- Keep Phase 6 focused on orchestration. Do not add new rule taxonomy, full report rendering, CLI behavior, source discovery, or research-use paired-output metrics.

Delivered:

- `audit_document(...)` now uses private helpers for assessments, flattened rule flags, summary counts, evidence-bundle warnings, and report limitations.
- `tests/test_auditor.py` verifies typed report output, trace links, exact rule-flag flattening order, summary consistency, empty evidence behavior, high-risk findings as valid audit results, no-claim drafts, config-threaded matching, deterministic output, and limitation wording.
- Report-level limitations now use neutral Phase 6 pipeline wording while preserving the supplied-evidence and candidate-score boundaries.
- Pure auditor-contract assertions moved out of `tests/test_vertical_slice.py`, which now stays focused on renderer/demo behavior.

Exit gate:

- Structured `AuditReport` includes trace links among claims, evidence, rule flags, summary metrics, and limitations.
- Empty evidence bundle produces `needs_source` or `unsupported` outcomes with a clear warning.
- High-risk findings do not make the audit fail.
- No-claim drafts produce valid zero-claim reports.
- Report-level rule flags exactly flatten claim-level rule flags.
- Summary counts are derived from `ClaimAssessment` values and tested for consistency.
- `CAL-REQ-025` is verified by trace-link and limitation tests.
- `CAL-REQ-012` remains planned unless report coverage exists too, or the matrix row is split to isolate the auditor-level empty-evidence behavior.
- `CAL-REQ-016` remains planned for CLI coverage unless the row is split to isolate auditor-level high-risk behavior.

Tie-off verification:

- Rechecked on 2026-05-01 with compileall, pytest, ruff format, ruff check, ruff format check, mypy, and coverage.
- Current result: 82 pytest tests passed and total coverage is 95%.

### Phase 7: Report Rendering Hardening

Status: complete.

Primary files:

- `src/claim_audit_lab/report.py`
- `tests/test_report.py`
- `examples/reports/`

Build:

- Full Markdown report renderer for human review, guided by `examples/reports/ai-research-note.target.md`.
- JSON report export for inspection and tests.
- Required sections: summary, claim register, evidence links, support labels, rule flags, limitations, and rewrite guidance where applicable.
- Report language must preserve the boundary between supplied-evidence support and truth verification.

Delivered:

- `render_markdown_report(...)` now emits a human-review report with metadata, executive summary, limitations, claim register, claim details, evidence links, and suggested rewrite guidance.
- `render_json_report(...)` remains tied directly to the typed `AuditReport` contract.
- `tests/test_report.py` verifies required report sections, labels, evidence links, rule flags, rewrite guidance, JSON round-trip, fixture synchronization, empty/warning reports, optional candidate fields, and language gates.
- `examples/reports/ai-research-note.slice.md` and `.json` were regenerated from the Phase 7 renderer.
- Candidate scores remain ranking signals and are not promoted into support labels or support scores.

Exit gate:

- Markdown reports contain required sections.
- JSON output validates against `AuditReport`.
- Reports contain no `None`, `nan`, empty placeholder sections, or forbidden capability language.
- `CAL-REQ-001`, `CAL-REQ-013`, `CAL-REQ-014`, and `CAL-REQ-029` are verified.

Tie-off verification:

- Rechecked on 2026-05-01 with compileall, pytest, ruff format, ruff check, ruff format check, mypy, and coverage.
- Current result: 90 pytest tests passed and total coverage is 96%.

### Phase 8: CLI

Status: complete.

Primary files:

- `src/claim_audit_lab/cli.py`
- `tests/test_cli.py`

Build:

- `claim-audit audit <draft> --evidence <bundle> --out <report.md>`
- Optional `--json-out <report.json>`.
- `claim-audit demo` if useful for public reviewers.
- Clear success and failure semantics.

Delivered:

- `claim-audit audit` loads a Markdown/plain-text draft plus YAML/JSON evidence bundle, runs `audit_document(...)`, writes Markdown output, optionally writes JSON output, and reports claim/risk counts without using candidate scores as support indicators.
- `claim-audit demo --out-dir <dir>` runs the AI research fixture and writes Markdown plus JSON reports to a requested directory, defaulting to `build/reports/`.
- Loader failures print clear path-aware errors and exit 1; Typer argument errors remain parser failures; completed audits with high-risk findings exit 0.
- `tests/test_cli.py` covers help output, happy path, Markdown-only output, output-directory creation, missing files, unsupported draft types, malformed YAML, schema validation failure, high-risk findings, demo behavior, checked-in fixture protection, and forbidden capability language.

Exit gate:

- `claim-audit --help` works after editable install.
- Malformed inputs exit nonzero and explain the problem.
- Completed audits exit successfully even when high-risk claims are found.
- `CAL-REQ-015`, `CAL-REQ-016`, and `CAL-REQ-026` are covered.

Tie-off verification:

- Rechecked on 2026-05-01 with editable install, activated `claim-audit --help`, CLI demo, compileall, pytest, ruff format, ruff check, ruff format check, mypy, and coverage.
- Current result: 104 pytest tests passed and total coverage is 96%.

### Phase 9: Example Families

Status: planned.

Primary folders:

- `examples/drafts/`
- `examples/evidence/`
- `examples/reports/`

Build at least two complete fictional examples:

- AI research memo: numeric, causal, scope, interpretive.
- Product README paragraph: capability, scope, comparative, prediction, stale-source, and limitation behavior. The draft/evidence seed for this family belongs in Phase 3A; Phase 9 completes generated report artifacts.

Additional fixture families:

- malformed evidence
- empty evidence bundle
- mixed reliability sources
- date or deadline note
- duplicate claim draft

Exit gate:

- At least two full example runs have Markdown and JSON outputs.
- Example data review confirms no private application materials, tokens, or local-only paths.
- `CAL-REQ-017` and `CAL-REQ-028` are covered.

### Phase 10: Validation Sweep

Status: planned.

Primary files:

- `docs/validation-matrix-reference.md`
- `docs/verification.md`
- test suite

Build:

- Run pytest, ruff, mypy, and coverage.
- Update matrix statuses from actual evidence.
- Document known gaps instead of silently ignoring them.
- Scan README, reports, and examples for overclaiming language.

Exit gate:

- `python -m pytest`
- `python -m ruff check .`
- `python -m ruff format .`
- `python -m mypy src`
- `python -m coverage run --branch -m pytest`
- `python -m coverage report`
- `docs/verification.md` records commands and outcomes.
- Public v1 validation gaps are documented or explicitly deferred.

### Phase 11: Public Packaging

Status: planned.

Primary files:

- `README.md`
- `docs/verification.md`
- `validation/`
- `examples/reports/*`
- screenshots
- social card / GitHub-pin assets

Build:

- Replace README stub with public-facing README.
- Add quick start, example output, system design, data model, rule checks, validation, limitations, and next steps.
- Link the first-class validation package without implying regulated compliance.
- Regenerate example reports.
- Run public-data and local-path sweep.
- Create repo social card / GitHub-pin assets so this matches the existing portfolio bar.
- Prepare GitHub/LinkedIn positioning.
- If referenced in the scaffold proposal, describe it as a validated measurement aid rather than proof of the experiment.

Exit gate:

- README matches implemented behavior.
- No placeholder links, local-only paths, secrets, or private data.
- Public copy says "supported by supplied evidence", not "fact checked".
- Qualification language is framed as validation-inspired portfolio control, not GxP, GMP, CSV, or FDA compliance.
- Social card / GitHub-pin assets are present and match the README positioning.
- `CAL-REQ-018` is verified.

### Phase 12: Validation Package Execution

Status: planned.

Primary files:

- `validation/README.md`
- `validation/qualification-plan.md`
- `validation/iq-installation.md`
- `validation/oq-operational.md`
- `validation/pq-performance.md`
- `validation/deviation-log.md`
- `docs/validation-matrix-reference.md`
- `docs/verification.md`
- `README.md`
- generated Markdown and JSON example reports

Build:

- Apply the validation package after the first CLI-first version exists.
- Confirm intended use: supplied-evidence support audit, not truth verification.
- Run IQ-style checks: clean local install, CLI availability, documented dependencies, and no hidden network or API-key requirement.
- Run OQ-style checks: expected operating range and edge cases, including malformed evidence, empty evidence, numeric mismatch, causal overstatement, comparative claims, stale or low-reliability evidence, and report language.
- Run PQ-style checks: at least two complete fictional or sanitized full audit examples with stable Markdown and JSON reports.
- Record deviations, accepted limitations, and revalidation triggers in `validation/deviation-log.md`, `docs/verification.md`, and the validation matrix.

Exit gate:

- Every README capability claim maps to a validation matrix row.
- Every core label and rule family is covered by a test, example report, or explicit deferred status.
- Example reports include trace links, limitations, and no truth-verification language.
- The validation pass is visible in the repo but does not claim regulated compliance.
- `CAL-REQ-036` is covered.

### Phase 13: Later Extensions

Status: deferred.

Only consider after the CLI-first deterministic version is solid:

- Streamlit interface for upload and report browsing.
- FastAPI wrapper.
- Source-assisted claim audit: optional source discovery that searches for candidate sources, extracts relevant excerpts, and converts them into an evidence bundle for the normal audit pipeline.
- Atomic claim decomposition and weakest-link scoring for complex claims, using typed subclaims and reportable component scores.
- Optional LLM-assisted claim extraction behind a clear adapter boundary.
- Richer source metadata and citation formatting.
- More fixture families and validation sweeps.

Do not let these pull scope into v1.

Source discovery should stay separate from support assessment. A later `--search` or web UI flow may let a user ask "is this supported?" and have the tool look for candidate sources, but generated reports must disclose that sources were discovered automatically and that the tool assessed support from retrieved excerpts rather than proving external truth.

## Cross-Cutting Considerations

### Traceability

Every claim assessment should be traceable:

- draft document ID
- claim ID
- claim text
- claim type
- evidence source IDs
- evidence excerpt IDs
- candidate scores
- rule flag IDs
- support label
- risk label
- limitation or warning where needed

This is the core portfolio signal. The project should feel auditable.

### Identifier Stability

IDs should be deterministic across reruns for the same input content.

- `Claim.id` is currently generated as `claim-` plus the first 12 characters of a SHA-256 digest over `document.id` and normalized claim text.
- `RuleFlag.id` should be generated deterministically from the rule code, claim ID, and the specific triggering condition, not from list position.
- Generated report anchors should use stable IDs so Markdown and JSON reports can be compared across runs.
- If the ID strategy changes, record it in `docs/verification.md` and treat changed golden outputs as validation drift until reviewed.

### Label Discipline

`supported` means supported by supplied evidence. It never means true.

When evidence is stale, incomplete, low-reliability, or only indirectly related, the report should say so. Partial support and overstated language are not failures of the tool; they are the main behavior the tool exists to reveal.

### Scoring Discipline

Numeric scoring can make the output easier to understand, but it must not imply truth certainty. Do not expose a final percent score until the scoring inputs, aggregation rules, and tests are explicit.

If scoring is added, prefer:

- support labels first
- support score second
- assessment confidence separately
- component-level scores for decomposed claims where practical
- a visible weakest-link reason when one unsupported component drives the overall label

Scoring should be deterministic in v1-style runs and backed by golden fixtures. A polished score with unclear math is less valuable than a transparent label with traceable reasons.

### Determinism

V1 should be deterministic. Tests should not depend on a model provider, network access, API key, current news, or hidden state.

### Fictional Data

Public fixtures must be fictional or sanitized. Avoid private job materials, real sensitive application content, tokens, local paths, or anything that would make the project feel careless when published.

### Error Semantics

Bad inputs are tool failures and should exit nonzero in the CLI.

High-risk claims are audit findings and should not exit nonzero if the audit completed. This distinction matters for trust and for possible CI usage.

### Source Type

`source_type` is constrained in `models.py` so later rule and report logic can distinguish source families without free-text drift. The first label set is:

- `report`
- `article`
- `documentation`
- `test_output`
- `local_note`
- `public_profile`
- `unknown`

This should stay lightweight. Add new source types only when a fixture or rule needs them.

### README And Report Language

The README and generated reports need the same boundary language as the models and tests. A polished report that overclaims would undermine the whole point.

Add report-quality checks before public packaging for:

- forbidden capability language
- `None`
- `nan`
- empty placeholder sections
- missing limitations
- unsupported labels that do not appear in the label definitions

### Validation Matrix Maintenance

Update `docs/validation-matrix-reference.md` only from current evidence.

Allowed statuses:

- `planned`: intended, not yet implemented.
- `implemented`: code or artifact exists, not fully verified.
- `verified`: acceptance criteria met by recorded evidence.
- `blocked`: cannot proceed without a decision or dependency.
- `deferred`: intentionally out of v1 scope.

### Post-Build Qualification

After Phase 11, use the first-class `validation/` package to run a lightweight IQ/OQ/PQ-inspired pass over the finished CLI-first tool. The validation package should make installation behavior, operating range behavior, representative full-run behavior, deviations, and revalidation triggers visible in the repo.

Do not describe this as regulated validation. The useful signal is disciplined traceability and reproducibility, not a compliance claim.

### Research Evaluation Use

Research-measurement rules live in `docs/research-use.md`. Do not let those requirements expand v1 scope unless the tool is actively being used as a scaffold-evaluation measurement instrument.

## Update Protocol

At the end of each meaningful work session:

1. Update the current phase status in this file.
2. Update `docs/verification.md` with checks run and outcomes.
3. Update `docs/validation-matrix-reference.md` statuses only where evidence exists.
4. Update `README.md` if implemented behavior or public instructions changed.
5. Update `/Users/gammaquantum/My Drive/projects/job-hunt/log/job-hunt-log.md`.
6. Leave the next best step explicit.

## Next Work Queue

1. Build CLI.
2. Run validation sweep.
3. Replace README stub with public README and required social/GitHub-pin assets.
4. Run the post-build validation package.

## Open Decisions

| Decision | Current leaning | When to decide |
| --- | --- | --- |
| Constrain `source_type` | Resolved: constrained in Phase 1. | Done. |
| Second fixture family | Resolved: Product README paragraph fixture is seeded. | Done. |
| Runnable demo entry point | Resolved: `scripts/run_demo.py` writes default outputs to `build/reports/`; checked-in fixtures refresh only with `--update-fixture`. | Done. |
| Public repo name | Resolved for now: keep `claim-audit-lab`. | Revisit only if later report or packaging review makes the name misleading. |
| Public product name | Resolved for now: keep `Claim Audit Lab`; use "claim stress test" and "evidence-support audit" as framing. | Revisit only if public packaging review finds clearer wording. |
| Support score | Potentially useful if presented as evidence-support, not percent truth; requires explicit deterministic scoring rules and tests. | After labels, rules, and reports are implemented. |
| Research measurement freeze | Tracked in `docs/research-use.md`, not a v1 shipping gate. | Before any research-output audit run. |
| Human calibration sample | Tracked in `docs/research-use.md`, not a v1 shipping gate. | Before relying on aggregate research metrics. |
| Post-build validation package | Use a lightweight IQ/OQ/PQ-inspired package as visible repo evidence after the first CLI-first version is made. | After public packaging, before relying on the tool as a research measurement channel. |
| Social card / GitHub pin | Required public packaging checklist item. | Phase 11. |
| Streamlit UI | Defer. | After v1 CLI is solid. |
| Source lookup mode | Potentially useful as source-assisted audit, but keep it separate from the deterministic supplied-evidence audit path. | After v1 reports and CLI are strong. |
