# Claim Audit Lab Master Plan

status: active
last_updated: 2026-04-30
asset: portfolio/live-asset/claim-audit-lab

Purpose: keep one living plan for Claim Audit Lab from first implementation through public packaging. Update this file as the build moves, and use it as the first planning read after `README.md`.

## Current State

Claim Audit Lab has a scaffold, a verified typed contract layer, verified draft/evidence loaders, and verified conservative claim extraction. Evidence matching and the audit engine itself have not been built yet.

Current durable files:

- `README.md`: public-facing stub and project boundary.
- `docs/validation-matrix-reference.md`: requirement matrix, fixture coverage, and acceptance rules.
- `validation/`: first-class validation package with IQ/OQ/PQ-inspired protocols, run records, and deviation log.
- `docs/verification.md`: checks run and verification notes.
- `docs/handoff-prompt.md`: next implementation prompt for deterministic evidence matching.
- `examples/drafts/ai-research-note.md`: first fictional draft fixture.
- `examples/evidence/ai-research-evidence.yml`: first fictional evidence fixture.
- `tests/fixtures/`: loader-focused plain text, JSON, empty-evidence, malformed-evidence, and missing-field fixtures.
- `src/claim_audit_lab/`: module skeleton.
- `src/claim_audit_lab/models.py`: strict Pydantic contract layer.
- `src/claim_audit_lab/loader.py`: path-aware draft and evidence bundle loader.
- `src/claim_audit_lab/claim_extraction.py`: conservative deterministic claim extraction.
- `tests/test_models.py`: first model validation tests.
- `tests/test_loader.py`: loader behavior and malformed-input tests.
- `tests/test_claim_extraction.py`: extraction behavior, classification, stable ID, and dedupe tests.

Immediate next step:

1. Implement `src/claim_audit_lab/evidence_matching.py`.
2. Add `tests/test_evidence_matching.py`.
3. Cover deterministic numeric matching, mismatched values, source/excerpt traceability, bounded candidate scores, and reliability-preserving candidate evidence.
4. Verify with compile, pytest, ruff, mypy, and coverage.
5. Update `docs/verification.md` and `log/job-hunt-log.md`.

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
- Do not rename the repo until the first report experience is visible enough to judge the name against the artifact.

## Research Use Integrity

Claim Audit Lab may be used as one measurement tool in the scaffold-evaluation research proposal, but it must not look or behave like a custom scoring machine built to prove that scaffolds work.

Use these guardrails before using it on research outputs:

- Validate the tool on its own fixture set before running it on scaffold-experiment outputs.
- Include fixtures where scaffolds help, do nothing, and make outputs worse.
- Include false-caution fixtures where a cautious answer should not be rewarded if it hides a well-supported conclusion.
- Freeze the tool version, rule policy, config, and validation-matrix status before evaluating experiment outputs.
- Record any later rule or code changes as bug fixes, validation changes, or exploratory post-hoc analysis.
- Compare a sample of tool labels against human reviewer judgments and report disagreement patterns.
- Treat Claim Audit Lab metrics as one measurement channel, not the sole basis for research conclusions.
- Preserve outputs, configs, evidence bundles, and tool version metadata so the audit can be replayed.

Good research positioning:

> Claim Audit Lab is not designed to prove scaffolds work. It is designed to make claim-support failures visible and countable. Scaffold results should be interpreted through convergence among automated audit metrics, human review, usefulness ratings, false-caution checks, and transparent error analysis.

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
- Research-use integrity rules explain version freeze, independent validation fixtures, human-review comparison, and no post-hoc tuning.

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

### Phase 4: Evidence Matching

Status: current.

Primary files:

- `src/claim_audit_lab/evidence_matching.py`
- `tests/test_evidence_matching.py`

Build:

- Transparent deterministic scoring.
- Match on numbers, dates, key terms, quoted phrases, and overlap.
- Preserve source IDs, excerpt IDs, reliability labels, and scores.
- Keep matching separate from support assessment.

Exit gate:

- Matching numeric claims link to matching evidence.
- Differing values do not appear fully supported.
- Multiple candidate evidence sources preserve reliability and support differences.
- Candidate scores remain bounded.
- `CAL-REQ-005` and `CAL-REQ-024` are covered.

### Phase 5: Rule Checks And Support Assessment

Status: planned.

Primary files:

- `src/claim_audit_lab/rules.py`
- `tests/test_rules.py`

Build:

- Rule checks stay separate from evidence matching.
- Map findings to support labels and risk labels.
- Flag unsupported numbers, dates, deadlines, public-link claims, credentials, causal overreach, unsupported comparisons, overconfident language, stale sources, low-reliability-only support, and future certainty.

Exit gate:

- Every rule check in the plan has at least one test.
- Every support label can be produced by a fixture or direct unit test before public release.
- Risk labels are constrained and tested.
- `CAL-REQ-006` through `CAL-REQ-011`, `CAL-REQ-021`, `CAL-REQ-022`, and rule parts of `CAL-REQ-029` are covered.

### Phase 6: Audit Orchestration

Status: planned.

Primary files:

- `src/claim_audit_lab/auditor.py`
- `tests/test_auditor.py`

Build:

- Implement `audit_document(draft, evidence_bundle, config=None) -> AuditReport`.
- Coordinate extraction, matching, rules, summary metrics, limitations, and evidence bundle warnings.
- Treat high-risk findings as valid audit results, not runtime failures.
- Empty evidence bundles return useful output rather than crashing.

Exit gate:

- Structured `AuditReport` includes trace links among claims, evidence, rule flags, summary metrics, and limitations.
- Empty evidence bundle produces `needs_source` or `unsupported` outcomes with a clear warning.
- High-risk findings do not make the audit fail.
- `CAL-REQ-012`, `CAL-REQ-016`, and `CAL-REQ-025` are covered.

### Phase 7: Reports

Status: planned.

Primary files:

- `src/claim_audit_lab/report.py`
- `tests/test_report.py`
- `examples/reports/`

Build:

- Markdown report renderer for human review.
- JSON report export for inspection and tests.
- Required sections: summary, claim register, evidence links, support labels, rule flags, limitations, and rewrite guidance where applicable.
- Report language must preserve the boundary between supplied-evidence support and truth verification.

Exit gate:

- Markdown reports contain required sections.
- JSON output validates against `AuditReport`.
- Reports contain no `None`, `nan`, empty placeholder sections, or forbidden capability language.
- `CAL-REQ-001`, `CAL-REQ-013`, `CAL-REQ-014`, and report portions of `CAL-REQ-029` are covered.

### Phase 8: CLI

Status: planned.

Primary files:

- `src/claim_audit_lab/cli.py`
- `tests/test_cli.py`

Build:

- `claim-audit audit <draft> --evidence <bundle> --out <report.md>`
- Optional `--json-out <report.json>`.
- `claim-audit demo` if useful for public reviewers.
- Clear success and failure semantics.

Exit gate:

- `claim-audit --help` works after editable install.
- Malformed inputs exit nonzero and explain the problem.
- Completed audits exit successfully even when high-risk claims are found.
- `CAL-REQ-015`, `CAL-REQ-016`, and `CAL-REQ-026` are covered.

### Phase 9: Example Families

Status: planned.

Primary folders:

- `examples/drafts/`
- `examples/evidence/`
- `examples/reports/`

Build at least two complete fictional examples:

- AI research memo: numeric, causal, scope, interpretive.
- Application answer or product README paragraph: credential, capability, public-link, comparative, prediction, and stale-source behavior.

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
- Run the research-use integrity review before the tool is used as a measurement instrument.

Exit gate:

- `python -m pytest`
- `python -m ruff check .`
- `python -m ruff format .`
- `python -m mypy src`
- `python -m coverage run --branch -m pytest`
- `python -m coverage report`
- `docs/verification.md` records commands and outcomes.
- Independent validation fixtures, false-caution checks, and human-review calibration plans are documented.

### Phase 11: Public Packaging

Status: planned.

Primary files:

- `README.md`
- `docs/verification.md`
- `validation/`
- `examples/reports/*`
- optional assets such as screenshots or social card

Build:

- Replace README stub with public-facing README.
- Add quick start, example output, system design, data model, rule checks, validation, limitations, and next steps.
- Link the first-class validation package without implying regulated compliance.
- Regenerate example reports.
- Run public-data and local-path sweep.
- Prepare GitHub/LinkedIn positioning.
- If referenced in the scaffold proposal, describe it as a validated measurement aid rather than proof of the experiment.

Exit gate:

- README matches implemented behavior.
- No placeholder links, local-only paths, secrets, or private data.
- Public copy says "supported by supplied evidence", not "fact checked".
- Qualification language is framed as validation-inspired portfolio control, not GxP, GMP, CSV, or FDA compliance.
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
- The qualification pass is visible in the repo but does not claim regulated compliance.
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

Before Claim Audit Lab is used on any scaffold-evaluation outputs:

- Create or identify the exact tool version used for measurement.
- Export the audit config and validation-matrix status with the results.
- Keep experiment prompts, model outputs, evidence bundles, and audit reports separate.
- Do not tune claim extraction, matching, or rules after seeing outcome differences unless the new run is clearly marked exploratory.
- Include human review for at least a calibration sample, with disagreements preserved rather than hidden.
- Report tool limitations and known failure modes alongside aggregate metrics.

## Update Protocol

At the end of each meaningful work session:

1. Update the current phase status in this file.
2. Update `docs/verification.md` with checks run and outcomes.
3. Update `docs/validation-matrix-reference.md` statuses only where evidence exists.
4. Update `README.md` if implemented behavior or public instructions changed.
5. Update `/Users/gammaquantum/My Drive/projects/job-hunt/log/job-hunt-log.md`.
6. Leave the next best step explicit.

## Next Work Queue

1. Build deterministic claim extraction.
2. Add claim-extraction tests for vague content, claim types, stable IDs, and duplicate handling.
3. Add second fictional fixture family before rule logic gets too tuned to the AI research memo.
4. Build evidence matching.
5. Build rule checks.
6. Build audit orchestration.
7. Build Markdown and JSON reports.
8. Build CLI.
9. Add research-use integrity fixtures and calibration notes.
10. Run validation sweep.
11. Replace README stub with public README.
12. Run the post-build qualification package.

## Open Decisions

| Decision | Current leaning | When to decide |
| --- | --- | --- |
| Constrain `source_type` | Resolved: constrained in Phase 1. | Done. |
| Second fixture family | Application answer or product README paragraph. | Before Phase 5. |
| `demo` CLI command | Useful for public review, but not essential. | During Phase 8. |
| Public repo name | Keep `claim-audit-lab` for now. | During Phase 11. |
| Public product name | Keep `Claim Audit Lab` as the working name; test "claim stress test" as framing, not necessarily the title. | During README/public packaging. |
| Support score | Potentially useful if presented as evidence-support, not percent truth; requires explicit deterministic scoring rules and tests. | After labels, rules, and reports are implemented. |
| Research measurement freeze | Freeze tool version, config, rules, and validation status before evaluating scaffold-experiment outputs. | Before any research-output audit run. |
| Human calibration sample | Compare tool labels to human reviewer judgments before relying on aggregate experiment metrics. | During validation sweep or research harness planning. |
| Post-build validation package | Use a lightweight IQ/OQ/PQ-inspired package as visible repo evidence after the first CLI-first version is made. | After public packaging, before relying on the tool as a research measurement channel. |
| Streamlit UI | Defer. | After v1 CLI is solid. |
| Source lookup mode | Potentially useful as source-assisted audit, but keep it separate from the deterministic supplied-evidence audit path. | After v1 reports and CLI are strong. |
