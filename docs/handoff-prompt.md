# Claim Audit Lab Handoff Prompt

Use this prompt to resume after Phase 13 implementation.

```text
We are in `/Users/gammaquantum/My Drive/projects/job-hunt`.

I want to resume Claim Audit Lab after Phase 13 traceability/report polish.

Before changing files, read these in order:

1. `AGENTS.md`
2. `log/job-hunt-log.md`
3. `pipeline.md`
4. `portfolio/AGENTS.md`
5. `portfolio/live-asset/claim-audit-lab/README.md`
6. `portfolio/live-asset/claim-audit-lab/docs/master-plan.md`
7. `portfolio/live-asset/claim-audit-lab/docs/validation-matrix-reference.md`
8. `portfolio/live-asset/claim-audit-lab/docs/verification.md`
9. `portfolio/live-asset/claim-audit-lab/docs/phase-13-traceability-report-polish-plan.md`
10. `portfolio/live-asset/claim-audit-lab/validation/README.md`
11. `portfolio/live-asset/claim-audit-lab/examples/reports/ai-research-note.slice.md`
12. `portfolio/live-asset/claim-audit-lab/examples/reports/product-readme-note.slice.md`

Project boundary:

- Claim Audit Lab audits whether draft claims are supported by supplied evidence.
- Do not call the tool a fact checker.
- Do not use private application materials in fixtures or public copy.
- Do not add live LLM calls, network calls, source discovery, support scores, or assessment-confidence scoring unless a new phase explicitly promotes that scope.
- Candidate scores are ranking signals, not final support labels.
- Keep research-use measurement rules in `docs/research-use.md`; do not let them expand the v1 shipping path.

Current workspace:

- Live asset folder: `portfolio/live-asset/claim-audit-lab/`
- `models.py`, `loader.py`, `claim_extraction.py`, `evidence_matching.py`, `rules.py`, `auditor.py`, `report.py`, and `cli.py` are implemented and verified for the deterministic CLI-first scope.
- `claim-audit audit` and `claim-audit demo` work after editable install.
- AI research and Product README both have draft, evidence, generated Markdown report, and generated JSON report artifacts.
- Phase 11 is complete: public README, MIT license, package metadata, social-card SVG, GitHub-pin copy, refreshed generated reports, and public-copy scans are done.
- Phase 12 is complete: IQ/OQ/PQ-inspired records are executed, `CAL-REQ-036` is verified, and accepted v1 limitations are recorded in `validation/deviation-log.md`.
- Phase 13 is complete: Markdown reports have explicit deterministic anchors, visible rule-flag IDs, support-quality notes where useful, and refreshed checked-in reports.
- `CAL-REQ-024` and `CAL-REQ-039` are verified.

Recommended next task:

1. Treat Claim Audit Lab as a CLI-first release candidate.
2. Review the README, example reports, validation package, and GitHub-facing assets as a final public-release pass.
3. Decide whether Phase 14 UI work should remain deferred or become a separately planned phase.

If implementation resumes, preserve the supplied-evidence boundary and the validation-inspired, non-regulated language. Keep source discovery, LLM assistance, network calls, support scores, assessment-confidence scores, UI work, and research-use calibration outside the release candidate unless a new plan explicitly promotes them.

Use the normal verification chain before changing status rows:

.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
. .venv/bin/activate && claim-audit --help
. .venv/bin/activate && claim-audit demo --out-dir build/reports/release-candidate-smoke

Keep the final response concise: changed files, checks run, matrix-status changes, and the next best step.
```
