# Verification notes

Last updated: 2026-05-01

## 2026-05-01: Phase 6 audit orchestration hardening

Implemented the Phase 6 auditor contract without expanding report rendering, CLI behavior, rule taxonomy, source discovery, or research-use metrics. The audit coordinator now has explicit private helpers for assessments, flattened rule flags, summary counts, evidence-bundle warnings, and report limitations.

Files updated:

- `src/claim_audit_lab/auditor.py`
- `tests/test_auditor.py`
- `tests/test_vertical_slice.py`
- `README.md`
- `docs/master-plan.md`
- `docs/phase-6-audit-orchestration-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/handoff-prompt.md`
- `docs/verification.md`
- `../../../pipeline.md`
- `../../../log/job-hunt-log.md`

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m pytest tests/test_auditor.py tests/test_vertical_slice.py -q
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff format src/claim_audit_lab/auditor.py tests/test_auditor.py tests/test_vertical_slice.py
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Results:

- Focused Phase 6/vertical-slice tests: 15 passed.
- Virtualenv compile check passed.
- `pytest`: 82 passed.
- Targeted Ruff format reformatted `tests/test_auditor.py`; final targeted format pass left all three files unchanged.
- Initial `ruff check .` caught two long test strings; after wrapping them, `ruff check .` passed.
- `ruff format --check .`: passed; 17 files already formatted.
- `mypy src`: passed across 9 source files.
- Coverage run: 82 passed; total coverage 95%.
- `auditor.py` and `tests/test_auditor.py` both report 100% coverage.
- `CAL-REQ-025` is verified by auditor contract tests.
- `CAL-REQ-012` remains planned because the full row still includes report-level coverage.
- `CAL-REQ-016` remains planned because the full row still includes CLI exit-code coverage.
- Next step is Phase 7 report rendering hardening.

## 2026-05-01: Phase 5 tie-off and Phase 6 plan

Rechecked the current Phase 5 work and added a dedicated Phase 6 audit orchestration plan. No validation matrix statuses were advanced in this planning pass because Phase 6 implementation has not started.

Files updated:

- `README.md`
- `docs/master-plan.md`
- `docs/phase-6-audit-orchestration-plan.md`
- `docs/handoff-prompt.md`
- `docs/verification.md`
- `../../../log/job-hunt-log.md`

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Results:

- Virtualenv compile check passed.
- `pytest`: 74 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed; 16 files already formatted.
- `mypy src`: passed across 9 source files.
- Coverage run: 74 passed; total coverage 95%.
- Phase 5 remains complete and ready to hand off.
- Phase 6 is now planned in `docs/phase-6-audit-orchestration-plan.md`.
- Next step is implementing Phase 6 audit orchestration hardening with `tests/test_auditor.py`.

## 2026-05-01: Phase 5 rule checks and support assessment

Implemented deterministic rule checks and lightly integrated them into the audit slice. The Phase 5 slice now returns rule-assessed support labels, risks, rule flags, summary counts, and regenerated Markdown/JSON outputs while keeping full report rendering and CLI behavior planned for later phases.

Files updated:

- `src/claim_audit_lab/models.py`
- `src/claim_audit_lab/evidence_matching.py`
- `src/claim_audit_lab/rules.py`
- `src/claim_audit_lab/auditor.py`
- `src/claim_audit_lab/report.py`
- `tests/test_models.py`
- `tests/test_evidence_matching.py`
- `tests/test_rules.py`
- `tests/test_vertical_slice.py`
- `examples/reports/ai-research-note.slice.md`
- `examples/reports/ai-research-note.slice.json`
- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/handoff-prompt.md`
- `docs/verification.md`
- `../../../log/job-hunt-log.md`

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python scripts/run_demo.py --update-fixture
.venv/bin/python -m ruff format src/claim_audit_lab/models.py src/claim_audit_lab/evidence_matching.py src/claim_audit_lab/rules.py src/claim_audit_lab/auditor.py src/claim_audit_lab/report.py tests/test_models.py tests/test_evidence_matching.py tests/test_rules.py tests/test_vertical_slice.py
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Results:

- Demo fixture refresh wrote `examples/reports/ai-research-note.slice.md` and `.json`.
- Ruff format updated 4 Python files.
- Virtualenv compile check passed.
- `pytest`: 74 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed; 16 files already formatted.
- `mypy src`: passed across 9 source files.
- Coverage run: 74 passed; total coverage 95%.
- `AuditConfig.reference_date` makes freshness checks deterministic and opt-in.
- `EvidenceCandidate.source_url` preserves source URL metadata for public-link rules.
- `assess_claim_support(...)` covers numeric mismatch, causal overreach, missing comparison evidence, credential/source support, public-link URL support, overconfident wording, low-reliability-only support, stale sources, date/deadline support, future certainty, and scope overreach.
- Empty evidence bundles preserve the existing behavior: all extracted claims are marked `needs_source` with an evidence-bundle warning.
- AI research slice labels now match the target report: `overstated`, `supported`, `partially_supported`, and `overstated`.
- `CAL-REQ-006` through `CAL-REQ-011`, `CAL-REQ-021`, and `CAL-REQ-022` are verified by Phase 5 tests.
- `CAL-REQ-024`, `CAL-REQ-029`, and `CAL-REQ-039` remain planned for later rule/report/docs/anchor coverage.
- Next step is Phase 6 audit orchestration hardening.

## 2026-04-30: Phase 4A runnable vertical slice

Implemented the provisional end-to-end slice: load draft/evidence, extract claims, match candidate evidence, return a typed `AuditReport`, and render Markdown/JSON outputs. The slice intentionally does not turn candidate scores into final support labels; Phase 5 owns rule checks and support assessment.

Files updated:

- `.gitignore`
- `src/claim_audit_lab/auditor.py`
- `src/claim_audit_lab/report.py`
- `scripts/run_demo.py`
- `tests/test_vertical_slice.py`
- `examples/reports/ai-research-note.slice.md`
- `examples/reports/ai-research-note.slice.json`
- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/handoff-prompt.md`
- `docs/verification.md`
- `../../../pipeline.md`
- `../../../log/job-hunt-log.md`

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m ruff format src/claim_audit_lab/auditor.py src/claim_audit_lab/report.py scripts/run_demo.py tests/test_vertical_slice.py
.venv/bin/python scripts/run_demo.py --update-fixture
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Results:

- Ruff format updated the new Phase 4A implementation and tests.
- Demo fixture refresh wrote `examples/reports/ai-research-note.slice.md` and `.json`.
- Virtualenv compile check passed.
- `pytest`: 60 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed.
- `mypy src`: passed.
- Coverage run: 60 passed; total coverage 97%.
- `audit_document(draft, evidence_bundle, config=None)` returns a typed `AuditReport`.
- `AuditConfig.min_overlap_score` and `AuditConfig.max_candidate_evidence` are threaded into candidate matching.
- Phase 4A labels are limited to `needs_source` and `not_audit_ready`.
- Empty evidence bundles produce a useful report and warning instead of crashing.
- Markdown and JSON renderers produce provisional slice outputs; JSON round-trips through `AuditReport`.
- Demo defaults write to gitignored `build/reports/`; checked-in fixtures only refresh with `--update-fixture`.
- The checked-in slice Markdown carries a Phase 4A provisional header and passes the forbidden capability-language gate.
- `CAL-REQ-038` is verified; full rule, report, orchestration, and CLI rows remain planned.
- Next step is Phase 5 rule checks and support assessment.

## 2026-04-30: Phase 4 deterministic evidence matching

Implemented deterministic candidate-evidence matching and kept it separate from support labels, rule flags, audit orchestration, report rendering, and CLI behavior.

Files updated:

- `src/claim_audit_lab/evidence_matching.py`
- `src/claim_audit_lab/models.py`
- `tests/test_evidence_matching.py`
- `tests/test_models.py`
- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/phase-4-evidence-matching-plan.md`
- `docs/handoff-prompt.md`
- `docs/verification.md`
- `../../../log/job-hunt-log.md`

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m ruff format src/claim_audit_lab/evidence_matching.py src/claim_audit_lab/models.py tests/test_evidence_matching.py tests/test_models.py
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Results:

- Ruff format updated `tests/test_evidence_matching.py`; the other touched files were already formatted.
- Virtualenv compile check passed.
- `pytest`: 53 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed; 13 files already formatted.
- `mypy src`: passed.
- Coverage run: 53 passed; total coverage 97%.
- Numeric matches link to matching evidence; numeric mismatch candidates stay below high-score territory.
- Product README capability, comparison, scope-limitation, and prediction-limitation claims produce candidate links without assigning support labels.
- Candidate ordering, capping, empty evidence bundles, bounded scores, source reliability/date metadata, and batch claim-ID mapping are covered.
- `CAL-REQ-005` is verified; `CAL-REQ-024` remains planned for later rule/report coverage.
- Next step is Phase 4A runnable vertical slice.

## 2026-04-30: Phase 4 evidence-matching plan and handoff prompt

Created a decision-complete Phase 4 plan and refreshed the new-session handoff prompt so implementation can start from files.

Files updated:

- `docs/phase-4-evidence-matching-plan.md`
- `docs/handoff-prompt.md`
- `README.md`
- `docs/master-plan.md`
- `docs/verification.md`
- `../../../log/job-hunt-log.md`

Checks run:

- Documentation-only planning update; no code checks were required.
- Confirmed Phase 4 remains unimplemented and the next action is to implement `src/claim_audit_lab/evidence_matching.py` with `tests/test_evidence_matching.py`.

## 2026-04-30: Phase 3A Product README fixture and Phase 4-ready stop

Added the second fictional fixture family and stopped before Phase 4 evidence-matching implementation.

Files updated:

- `examples/drafts/product-readme-note.md`
- `examples/evidence/product-readme-evidence.yml`
- `tests/test_claim_extraction.py`
- `tests/test_loader.py`
- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/handoff-prompt.md`
- `validation/pq-performance.md`
- `docs/verification.md`
- `../../../log/job-hunt-log.md`

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m ruff format tests/test_claim_extraction.py tests/test_loader.py
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Results:

- Ruff format updated `tests/test_claim_extraction.py`; `tests/test_loader.py` was unchanged.
- Virtualenv compile check passed.
- `pytest`: 41 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed; 12 files already formatted.
- `mypy src`: passed.
- Coverage run: 41 passed; total coverage 97%.
- Product README fixture loads from Markdown and YAML and extracts capability, comparative, prediction, and scope claims.
- Phase 3A is complete; next step is to plan Phase 4 deterministic evidence matching before implementation.

## 2026-04-30: Phase 3A target report review and status sync

Reviewed `examples/reports/ai-research-note.target.md` as the hand-authored target output for the AI research memo fixture.

Files updated:

- `examples/reports/ai-research-note.target.md`
- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/handoff-prompt.md`
- `examples/reports/README.md`
- `docs/verification.md`
- `../../../log/job-hunt-log.md`

Checks run:

- Documentation-only update; no code checks were required.
- Inspected the target report for required target-output sections, supplied-evidence boundary language, and renderer design questions.
- Aligned the first target-report claim type with current extraction behavior: `claim-ai001` is `scope`, not `capability`.
- Marked `CAL-REQ-037` verified from the reviewed target report; generated-report and two-example requirements remain planned.
- Confirmed the target report does not force a naming change: keep `Claim Audit Lab` and `claim-audit-lab` for now.
- Stopped before Phase 4 evidence matching.

## 2026-04-30: Git initialization, validation package, and planning updates

Added a visible top-level validation package so the pharma-equipment validation analogy is tracked as a first-class part of the repo after the first CLI-first version is made.

Later in the same planning pass, added an explicit target-report prompt, split research-use requirements into an adjunct doc, and updated the master plan so a runnable vertical slice happens before Phase 5 rule hardening.

Files updated:

- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/target-report-prompt.md`
- `docs/research-use.md`
- `docs/handoff-prompt.md`
- `examples/reports/README.md`
- `validation/README.md`
- `validation/qualification-plan.md`
- `validation/iq-installation.md`
- `validation/oq-operational.md`
- `validation/pq-performance.md`
- `validation/deviation-log.md`
- removed `docs/qualification-plan.md`
- `docs/verification.md`
- `../../../log/job-hunt-log.md`

Checks run:

- Documentation-only update; no code checks were required.
- Confirmed no existing git toplevel before initialization.
- Initialized git for `portfolio/live-asset/claim-audit-lab/`.
- Checked repository status after initialization.
- Confirmed the README, master plan, and validation matrix point to the top-level `validation/` package.
- Confirmed target-report and research-use planning are represented in project docs; no code checks were required.

## 2026-04-29: Phase 3 conservative claim extraction

Implemented deterministic claim extraction in `src/claim_audit_lab/claim_extraction.py` and added `tests/test_claim_extraction.py`.

Files updated:

- `src/claim_audit_lab/claim_extraction.py`
- `tests/test_claim_extraction.py`
- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/verification.md`
- `docs/handoff-prompt.md`
- `../../../log/job-hunt-log.md`

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format src/claim_audit_lab/claim_extraction.py tests/test_claim_extraction.py
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Results:

- Virtualenv compile check passed.
- `pytest`: 38 passed.
- `ruff check .`: passed.
- `ruff format`: reformatted the extraction module; tests were already formatted.
- `ruff format --check .`: passed; 12 files already formatted.
- `mypy src`: passed.
- Coverage run: 38 passed; total coverage 96%.
- `CAL-REQ-004` and `CAL-REQ-023` are verified by extraction tests.

## 2026-04-29: Research-use integrity planning

Updated planning and control docs so Claim Audit Lab can be used as one measurement channel for scaffold-evaluation research without appearing tuned to prove the experiment.

Files updated:

- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `README.md`
- `docs/handoff-prompt.md`
- `../../../planning/claim-audit-lab-plan.md`
- `../../../planning/claim-audit-lab-control-checklist.md`
- `../../../planning/research-proposal/research-proposal-scaffold-evaluation.md`
- `../../../../log/job-hunt-log.md`

Checks run:

- Documentation-only update; no code checks were required.

## 2026-04-28: Phase 2 loaders

Implemented `src/claim_audit_lab/loader.py`, `tests/test_loader.py`, loader fixtures under `tests/fixtures/`, and added `types-PyYAML` to dev dependencies for strict mypy coverage.

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/claim-audit --help
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Results:

- Editable install with refreshed dev dependencies passed.
- Virtualenv compile check passed.
- `pytest`: 26 passed.
- `ruff check .`: passed.
- `ruff format .`: reformatted scaffold and changed files.
- `ruff format --check .`: passed; 11 files already formatted.
- `mypy src`: passed.
- `claim-audit --help`: passed.
- Coverage run: 26 passed; total coverage 96%.
- `CAL-REQ-002` and `CAL-REQ-003` are verified by loader tests.

## 2026-04-28: Phase 1 typed model layer

Implemented `src/claim_audit_lab/models.py` and `tests/test_models.py`.

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
python3.11 -m compileall -q src tests
python3.11 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy src
.venv/bin/python -m ruff format --check src/claim_audit_lab/models.py tests/test_models.py
.venv/bin/claim-audit --help
```

Results:

- System Python compile check passed.
- Local virtual environment was created because system Python did not have `pytest`.
- Editable install with dev dependencies passed.
- Virtualenv compile check passed.
- `pytest`: 16 passed.
- `ruff check .`: passed.
- `mypy src`: passed.
- `ruff format --check` for changed files: passed.
- `claim-audit --help`: passed.

Note:

- The earlier full-project formatting warning was resolved during the Phase 2 formatting sweep.
