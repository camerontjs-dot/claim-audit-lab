# Verification notes

Last updated: 2026-05-04

## 2026-05-04: Phase 13 traceability/report polish implementation

Implemented Phase 13 without changing audit semantics, JSON schema, source discovery, live LLM/network behavior, support scores, assessment-confidence scoring, UI behavior, or research-use calibration. Markdown reports now include explicit deterministic anchors, visible rule-flag IDs, and constrained support-quality notes derived from existing assessment data.

Files updated:

- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/phase-13-traceability-report-polish-plan.md`
- `docs/handoff-prompt.md`
- `docs/verification.md`
- `src/claim_audit_lab/report.py`
- `tests/test_report.py`
- `examples/reports/ai-research-note.slice.md`
- `examples/reports/product-readme-note.slice.md`
- `../../../pipeline.md`
- `../../../log/job-hunt-log.md`

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
. .venv/bin/activate && claim-audit --help
. .venv/bin/activate && claim-audit demo --out-dir build/reports/phase-13-smoke
rg -n "fact check|fact-check|truth verifier|verify external truth|proven true|guaranteed true|verified externally|FDA|GxP|GMP|Computer System Validation|CSV validation|regulated compliance" README.md docs validation examples assets
rg -n "TODO|TBD|placeholder|localhost|/Users/|api[_-]?key|secret|token|password" README.md docs validation examples assets
```

Results:

- Editable install passed.
- Virtualenv compile check passed.
- `pytest`: 112 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed; 19 files already formatted.
- `mypy src`: passed across 9 source files.
- Coverage run: 112 passed; total coverage 96%.
- Activated `claim-audit --help` showed `audit` and `demo` subcommands.
- Activated `claim-audit demo --out-dir build/reports/phase-13-smoke` wrote ignored Markdown and JSON outputs and completed with 4 claims assessed.
- Overclaim and regulated-language scan produced expected historical, source-reference, avoid-list, boundary-language, validation disclaimer, and scan-command self-matches; no new public README or asset overclaim was introduced.
- Placeholder/private-data/local-path scan produced expected historical absolute-path handoff references, target-report placeholder language, closed placeholder-row wording, support-quality empty-section test wording, and scan-pattern self-matches; public README and assets had no placeholder links, private data, secrets, or local-only paths.

Phase outcome:

- Added explicit Markdown anchors for report, claim detail, rule-flag, and evidence-link surfaces.
- Made rule-flag IDs visible in Markdown.
- Added support-quality notes for weak, unknown, stale, mixed, or indirect candidate evidence where useful, with tests proving the section stays absent when it would be filler.
- Refreshed checked-in generated Markdown reports for both fictional report families.
- Moved `CAL-REQ-024` and `CAL-REQ-039` to `verified`.

## 2026-05-04: Phase 12 tie-off and Phase 13 planning

Confirmed Phase 12 validation package execution is tied off across the current repo-visible status files, then added the Phase 13 traceability/report-polish plan as the next implementation move.

Files updated:

- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/handoff-prompt.md`
- `docs/verification.md`
- `docs/phase-13-traceability-report-polish-plan.md`
- `../../../pipeline.md`
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
. .venv/bin/activate && claim-audit --help
. .venv/bin/activate && claim-audit demo --out-dir build/reports/phase-13-plan-smoke
rg -n "fact check|fact-check|truth verifier|verify external truth|proven true|guaranteed true|verified externally|FDA|GxP|GMP|Computer System Validation|CSV validation|regulated compliance" README.md docs validation examples assets
rg -n "TODO|TBD|placeholder|localhost|/Users/|api[_-]?key|secret|token|password" README.md docs validation examples assets
```

Results:

- Virtualenv compile check passed.
- `pytest`: 108 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed; 19 files already formatted.
- `mypy src`: passed across 9 source files.
- Coverage run: 108 passed; total coverage 96%.
- Activated `claim-audit --help` showed `audit` and `demo` subcommands.
- Activated `claim-audit demo --out-dir build/reports/phase-13-plan-smoke` wrote ignored Markdown and JSON outputs and completed with 4 claims assessed.
- Overclaim and regulated-language scan produced expected source-reference, avoid-list, boundary-language, and scan-command self-matches; no new public README or asset overclaim was introduced.
- Placeholder/private-data/local-path scan produced expected historical absolute-path handoff references, target-report placeholder language, scan-command self-matches, and the new Phase 13 handoff path; no public README or asset placeholder link, private data, secret, or local-only path was introduced.

Plan outcome:

- Added `docs/phase-13-traceability-report-polish-plan.md`.
- Phase 13 is scoped as a narrow code-and-docs polish slice: explicit Markdown anchors, visible rule-flag IDs, and support-quality notes.
- `CAL-REQ-024` and `CAL-REQ-039` remain `planned` until implementation and tests provide current evidence.

## 2026-05-04: Phase 12 validation package execution

Completed Phase 12 validation package execution without changing audit semantics, public claims, CLI behavior, report schema, source discovery, live LLM/network behavior, support scores, or assessment-confidence scoring. Phase 12 generated IQ/OQ/PQ-inspired records from current evidence and kept command/output evidence in the protocol tables rather than adding a separate evidence folder.

Files updated:

- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/handoff-prompt.md`
- `docs/verification.md`
- `validation/README.md`
- `validation/qualification-plan.md`
- `validation/iq-installation.md`
- `validation/oq-operational.md`
- `validation/pq-performance.md`
- `validation/deviation-log.md`
- `../../../pipeline.md`
- `../../../log/job-hunt-log.md`

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
python3.11 -m venv build/phase-12-iq-venv
build/phase-12-iq-venv/bin/python -m pip install -e ".[dev]"
build/phase-12-iq-venv/bin/claim-audit --help
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
. .venv/bin/activate && claim-audit --help
. .venv/bin/activate && claim-audit demo --out-dir build/reports/phase-12-validation/demo
mkdir -p build/reports/phase-12-validation/ai-research build/reports/phase-12-validation/product-readme
. .venv/bin/activate && claim-audit audit examples/drafts/ai-research-note.md --evidence examples/evidence/ai-research-evidence.yml --out build/reports/phase-12-validation/ai-research/ai-research-note.md --json-out build/reports/phase-12-validation/ai-research/ai-research-note.json
. .venv/bin/activate && claim-audit audit examples/drafts/product-readme-note.md --evidence examples/evidence/product-readme-evidence.yml --out build/reports/phase-12-validation/product-readme/product-readme-note.md --json-out build/reports/phase-12-validation/product-readme/product-readme-note.json
.venv/bin/python - <<'PY'
from pathlib import Path
from claim_audit_lab.models import AuditReport

paths = [
    Path("build/reports/phase-12-validation/ai-research/ai-research-note.json"),
    Path("build/reports/phase-12-validation/product-readme/product-readme-note.json"),
    Path("build/reports/phase-12-validation/demo/ai-research-note.cli.json"),
]
for path in paths:
    report = AuditReport.model_validate_json(path.read_text())
    print(f"{path}: ok ({len(report.claims)} claims)")
PY
rg -n "Trace|Limitations|Support Label|Rule Flags|Rewrite Guidance|supported by supplied evidence|partially supported|overstated|High-risk|Evidence Links|Claim Register" build/reports/phase-12-validation/**/*.md
rg -n "fact check|fact-check|truth verifier|verify external truth|proven true|guaranteed true|verified externally|FDA|GxP|GMP|Computer System Validation|CSV validation|regulated compliance" README.md docs validation examples assets
rg -n "TODO|TBD|placeholder|localhost|/Users/|api[_-]?key|secret|token|password" README.md docs validation examples assets
rg -n "openai|anthropic|requests|httpx|urllib|socket|dotenv|os\.environ" pyproject.toml src tests scripts
git status --ignored --short
```

Results:

- Clean IQ venv was created under ignored `build/phase-12-iq-venv/`.
- Clean IQ editable install with dev dependencies succeeded and exposed `claim-audit --help`.
- Repo-local editable reinstall passed.
- Virtualenv compile check passed.
- `pytest`: 108 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed; 19 files already formatted.
- `mypy src`: passed across 9 source files.
- Coverage run: 108 passed; total coverage 96%.
- Activated `claim-audit --help` showed `audit` and `demo` subcommands.
- Activated `claim-audit demo --out-dir build/reports/phase-12-validation/demo` wrote Markdown and JSON reports and completed with 4 claims assessed.
- AI research `claim-audit audit` wrote Markdown and JSON reports with 4 claims assessed: 1 supported, 1 partially supported, 2 overstated, and 2 high-risk findings.
- Product README `claim-audit audit` wrote Markdown and JSON reports with 4 claims assessed: 2 supported, 2 overstated, and 2 high-risk findings.
- Demo, AI research, and Product README JSON reports validated through `AuditReport.model_validate_json(...)`.
- Generated Markdown report inspection confirmed audit boundary, limitations, claim register, candidate evidence, support labels, risk labels, rule flags, and rewrite guidance where applicable.
- Overclaim and regulated-language scan produced expected historical, source-reference, avoid-list, and boundary-language matches; README and assets do not claim source discovery, outside-world assessment, regulated compliance, or research-result proof.
- Placeholder/private-data/local-path scan produced expected historical absolute-path handoff references, target-report placeholder language, closed placeholder-row wording, and scan-pattern self-matches; public README and assets had no placeholder links, private data, secrets, or local-only paths.
- Network/provider scan across package/source/test/script surfaces produced no matches.
- `git status --ignored --short` confirmed Phase 12 generated outputs, clean IQ venv, coverage, caches, egg-info, bytecode, and build artifacts are ignored.

Validation matrix status effects:

- `CAL-REQ-036` moved to `verified` because IQ/OQ/PQ-inspired records are complete, deviations/limitations are visible, and the validation package is linked from public docs without regulated-compliance claims.
- `CAL-REQ-024` remains `planned` because candidate reliability/support differences are visible in metadata and reports, but warning/report polish for support-quality differences is still a later gap.
- `CAL-REQ-039` remains `planned` because stable claim IDs, deterministic rule-flag IDs, and generated report comparisons are covered, but explicit Markdown anchor policy is still not fully documented.

Accepted limitations recorded:

- Research-use human calibration remains deferred outside v1 and belongs in `docs/research-use.md`.
- Real-world production-data qualification is out of scope for the public portfolio release; v1 uses fictional fixtures to avoid private or sensitive material.

Next step is Phase 13 planning for traceability/report-polish work around `CAL-REQ-024` and `CAL-REQ-039`.

## 2026-05-04: Phase 11 public packaging

Completed Phase 11 public packaging without changing audit semantics, adding support scores, adding source discovery, adding network calls, adding live LLM calls, or executing the IQ/OQ/PQ validation package. The README is now the public front door, the repo has MIT licensing and public package metadata, and the public asset surface includes a social-card SVG plus GitHub-pin copy.

Files updated:

- `README.md`
- `LICENSE`
- `pyproject.toml`
- `assets/social-card.svg`
- `assets/github-pin.md`
- `docs/phase-11-public-packaging-plan.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/handoff-prompt.md`
- `docs/verification.md`
- `validation/README.md`
- `../../../pipeline.md`
- `../../../log/job-hunt-log.md`

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python scripts/run_demo.py --draft examples/drafts/ai-research-note.md --evidence examples/evidence/ai-research-evidence.yml --update-fixture
.venv/bin/python scripts/run_demo.py --draft examples/drafts/product-readme-note.md --evidence examples/evidence/product-readme-evidence.yml --update-fixture
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
. .venv/bin/activate && claim-audit --help
. .venv/bin/activate && claim-audit demo --out-dir build/reports/phase-11-smoke
rg -n "fact check|fact-check|truth verifier|verify external truth|proven true|guaranteed true|verified externally|FDA|GxP|GMP|Computer System Validation|CSV validation|regulated compliance" README.md docs validation examples assets
rg -n "TODO|TBD|placeholder|localhost|/Users/|api[_-]?key|secret|token|password" README.md docs validation examples assets
rg -n "openai|anthropic|requests|httpx|urllib|socket|dotenv|os\.environ" pyproject.toml src tests scripts
rg -n "width=\"1200\" height=\"628\"|Claim Audit Lab|supplied-evidence claim audit" assets/social-card.svg assets/github-pin.md
```

Results:

- Editable install with dev dependencies passed after package metadata changes.
- Both checked-in report families were regenerated from the current renderer; generated report files were already in sync with no content diff.
- Virtualenv compile check passed.
- `pytest`: 108 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed; 19 files already formatted.
- `mypy src`: passed across 9 source files.
- Coverage run: 108 passed; total coverage 96%.
- Activated `claim-audit --help` showed `audit` and `demo` subcommands.
- Activated `claim-audit demo --out-dir build/reports/phase-11-smoke` wrote Markdown and JSON reports and completed with 4 claims assessed.
- Social-card SVG inspection confirmed 1200 x 628 dimensions and intended headline/descriptor text.
- Overclaim and regulated-language scan produced expected historical, source-reference, avoid-list, and boundary-language matches; README and assets do not claim source discovery, outside-world assessment, regulated compliance, or research-result proof.
- Placeholder/private-data/local-path scan produced expected planned-protocol `TBD` entries, historical absolute-path handoff references, target-report placeholder language, and scan-pattern self-matches; public README and assets had no placeholder links, private data, secrets, or local-only paths.
- Network/provider scan across package/source/test/script surfaces produced no matches.
- `CAL-REQ-018` and `CAL-REQ-040` are verified.
- `CAL-REQ-024` remains planned because support-quality warning/report polish is still a later gap.
- `CAL-REQ-036` remains planned for Phase 12 validation-package execution.
- `CAL-REQ-039` remains planned because stable claim IDs, deterministic rule-flag IDs, and generated report comparisons are covered, but explicit Markdown anchor policy is not fully documented.
- Next step is Phase 12 validation package execution.

## 2026-05-01: Phase 10 tie-off and Phase 11 plan

Confirmed the Phase 10 validation sweep is tied off in the README, master plan, validation matrix, verification notes, validation package notes, handoff prompt, pipeline, and job-hunt log. Added `docs/phase-11-public-packaging-plan.md` so the next session can start public packaging from a dedicated plan instead of reconstructing scope from the phase tracker.

Phase 11 remains unimplemented. The saved plan defines README rewrite scope, public asset expectations, public-copy sweeps, verification commands, matrix status rules, non-goals, and the pickup prompt. It keeps audit semantics, source discovery, live LLM/network calls, and IQ/OQ/PQ execution out of Phase 11.

Fresh verification after saving the Phase 11 plan:

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
.venv/bin/python -m pip install -e ".[dev]"
. .venv/bin/activate && claim-audit --help
```

Results: 108 tests passed; Ruff, format check, and MyPy passed; coverage remains 96%; editable install passed; `claim-audit --help` showed `audit` and `demo`.

## 2026-05-01: Phase 10 validation sweep

Completed the Phase 10 validation sweep without changing audit semantics, adding support scores, adding source discovery, adding network calls, adding live LLM calls, rewriting the public README, or executing the IQ/OQ/PQ validation package. The sweep rechecked the full deterministic CLI-first tool, corrected stale demo wording, refreshed validation-package readiness notes, and updated matrix statuses only where current evidence supports them.

Files updated:

- `scripts/run_demo.py`
- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/handoff-prompt.md`
- `docs/verification.md`
- `validation/README.md`
- `validation/oq-operational.md`
- `validation/pq-performance.md`
- `../../../pipeline.md`
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
.venv/bin/python -m pip install -e ".[dev]"
. .venv/bin/activate && claim-audit --help
rg -n "Phase 4A|Phase 5 rule-assessment slice|CLI workflow is planned|provisional|not implemented|planned in Phase 7" README.md docs examples/reports validation src tests scripts
rg -n "requests|httpx|urllib|socket|openai|anthropic|os\.environ|dotenv|network|live LLM|API keys" src tests scripts pyproject.toml README.md docs validation examples
```

Results:

- Virtualenv compile check passed.
- `pytest`: 108 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed; 19 files already formatted.
- `mypy src`: passed across 9 source files.
- Coverage run: 108 passed; total coverage 96%.
- Editable install with dev dependencies passed.
- Activated `claim-audit --help` showed `audit` and `demo` subcommands.
- Generated AI research and Product README slice reports both use the current Phase 7/8 header wording.
- Stale Phase 4A wording was found only in historical docs/tests and the demo script help text; the demo script wording was updated.
- Network/API/LLM scan found no source dependency on network clients, provider SDKs, environment secrets, or API keys; hits were boundary-language documentation and tokenization helpers.
- Validation-language scan found no GxP/GMP/CSV/FDA compliance claims. The remaining matches are guardrails, source-pattern references, or explicit avoid-list wording.
- Public example private-data/secret scanning remains covered by `tests/test_report.py`.
- `CAL-REQ-012` and `CAL-REQ-027` are verified.
- `CAL-REQ-018` remains planned for Phase 11 because the README is still a stub.
- `CAL-REQ-024` remains planned because support-quality warning/report polish is still a later gap.
- `CAL-REQ-036` remains planned for Phase 12 validation-package execution.
- `CAL-REQ-039` remains planned because stable claim IDs, deterministic rule-flag IDs, and generated report comparisons are covered, but explicit Markdown anchor policy is not fully documented.
- `CAL-REQ-040` remains planned for Phase 11 social/GitHub-pin assets.
- Next step is Phase 11 public packaging.

## 2026-05-01: Phase 9 example families

Completed the Phase 9 example-family gate without changing audit semantics, adding support scores, adding source discovery, adding network calls, adding live LLM calls, or adding extra fixture families. The Product README fixture now has checked-in Markdown and JSON reports generated through `scripts/run_demo.py`, and public examples have persistent pytest coverage for renderer sync, report-level behavior, forbidden capability language, and private-data or secret markers.

Files updated:

- `scripts/run_demo.py`
- `tests/test_report.py`
- `tests/test_vertical_slice.py`
- `examples/reports/README.md`
- `examples/reports/product-readme-note.slice.md`
- `examples/reports/product-readme-note.slice.json`
- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/handoff-prompt.md`
- `docs/verification.md`
- `../../../pipeline.md`
- `../../../log/job-hunt-log.md`

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python scripts/run_demo.py --draft examples/drafts/product-readme-note.md --evidence examples/evidence/product-readme-evidence.yml --update-fixture
.venv/bin/python -m pytest tests/test_report.py tests/test_vertical_slice.py -q
.venv/bin/python -m ruff format scripts/run_demo.py tests/test_report.py tests/test_vertical_slice.py
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Results:

- Product README fixture generation wrote `examples/reports/product-readme-note.slice.md` and `.json`.
- Product README generated report summary: 4 claims, 2 supported, 2 overstated, and 2 high-risk findings.
- Focused report/vertical-slice regression tests: 16 passed.
- Virtualenv compile check passed.
- `pytest`: 108 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed.
- `mypy src`: passed across 9 source files.
- Coverage run: 108 passed; total coverage 96%.
- `CAL-REQ-017` and `CAL-REQ-028` are verified.
- Manual review plus pytest scan found no private application materials, personal names, local-only paths, tokens, API-key markers, or common secret markers in `examples/drafts/`, `examples/evidence/`, or `examples/reports/`.
- Next step is Phase 10 validation sweep.

## 2026-05-01: Phase 8 CLI workflow

Implemented the Phase 8 `claim-audit` CLI without changing audit semantics, adding source discovery, adding support scores, generating second-family reports, or adding research-use paired metrics. The CLI now exposes `audit` and `demo` subcommands, writes Markdown and optional JSON reports, treats high-risk findings as completed audit results, and routes loader failures to clear nonzero input errors.

Files updated:

- `src/claim_audit_lab/cli.py`
- `src/claim_audit_lab/auditor.py`
- `src/claim_audit_lab/report.py`
- `tests/test_cli.py`
- `tests/test_report.py`
- `tests/test_vertical_slice.py`
- `examples/reports/ai-research-note.slice.md`
- `examples/reports/ai-research-note.slice.json`
- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/handoff-prompt.md`
- `docs/phase-8-cli-plan.md`
- `docs/verification.md`
- `../../../pipeline.md`
- `../../../log/job-hunt-log.md`

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m ruff format src/claim_audit_lab/cli.py tests/test_cli.py
.venv/bin/python -m pytest tests/test_cli.py
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m mypy src
.venv/bin/python -m pip install -e ".[dev]"
. .venv/bin/activate && claim-audit --help
. .venv/bin/activate && claim-audit demo --out-dir build/reports/cli-demo
.venv/bin/python scripts/run_demo.py --update-fixture
.venv/bin/python -m pytest tests/test_report.py tests/test_vertical_slice.py tests/test_cli.py -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Results:

- Focused CLI tests: 14 passed.
- Focused report/vertical-slice/CLI regression tests after stale header refresh: 26 passed.
- Virtualenv compile check passed.
- `pytest`: 104 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed.
- `mypy src`: passed across 9 source files.
- Editable install succeeded in the project virtualenv.
- Activated `claim-audit --help` showed `audit` and `demo` subcommands.
- Activated `claim-audit demo --out-dir build/reports/cli-demo` wrote ignored Markdown and JSON outputs and exited 0 with 2 high-risk findings.
- Coverage run: 104 passed; total coverage 96%.
- `CAL-REQ-015`, `CAL-REQ-016`, and `CAL-REQ-026` are verified.
- Next step is Phase 9 example families.

## 2026-05-01: Phase 7 report rendering hardening

Implemented the Phase 7 report renderer without adding CLI behavior, source discovery, support scores, second-family report generation, or research-use paired metrics. The Markdown renderer now produces a human-review report with metadata, executive summary, limitations, claim register, claim details, evidence links, rule flags, and suggested rewrite guidance. JSON output remains a typed `AuditReport` export.

Files updated:

- `src/claim_audit_lab/auditor.py`
- `src/claim_audit_lab/report.py`
- `src/claim_audit_lab/rules.py`
- `tests/test_report.py`
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
.venv/bin/python scripts/run_demo.py --update-fixture
.venv/bin/python -m pytest tests/test_report.py tests/test_vertical_slice.py tests/test_auditor.py -q
.venv/bin/python -m ruff format src/claim_audit_lab/auditor.py src/claim_audit_lab/report.py src/claim_audit_lab/rules.py tests/test_report.py tests/test_vertical_slice.py tests/test_auditor.py
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Results:

- Focused report/vertical-slice/auditor tests: 23 passed.
- Virtualenv compile check passed.
- `pytest`: 90 passed.
- Targeted Ruff format reformatted `src/claim_audit_lab/report.py` and `tests/test_report.py`; final format check passed.
- `ruff check .`: passed.
- `mypy src`: passed across 9 source files.
- Coverage run: 90 passed; total coverage 96%.
- `report.py` reports 98% coverage and `tests/test_report.py` reports 100% coverage.
- `CAL-REQ-001`, `CAL-REQ-013`, `CAL-REQ-014`, and `CAL-REQ-029` are verified.
- Next step is Phase 8 CLI.

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
