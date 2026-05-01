# Claim Audit Lab Handoff Prompt

Use this prompt to start Phase 10 in a fresh chat.

```text
We are in `/Users/gammaquantum/My Drive/projects/job-hunt`.

I want to implement Claim Audit Lab Phase 10: validation sweep.

Before changing files, read these in order:

1. `AGENTS.md`
2. `log/job-hunt-log.md`
3. `pipeline.md`
4. `portfolio/AGENTS.md`
5. `portfolio/planning/claim-audit-lab-plan.md`
6. `portfolio/planning/claim-audit-lab-control-checklist.md`
7. `portfolio/live-asset/claim-audit-lab/README.md`
8. `portfolio/live-asset/claim-audit-lab/docs/master-plan.md`
9. `portfolio/live-asset/claim-audit-lab/docs/validation-matrix-reference.md`
10. `portfolio/live-asset/claim-audit-lab/docs/verification.md`
11. `portfolio/live-asset/claim-audit-lab/examples/reports/ai-research-note.slice.md`
12. `portfolio/live-asset/claim-audit-lab/examples/reports/product-readme-note.slice.md`
13. `portfolio/live-asset/claim-audit-lab/docs/research-use.md`
14. `/Users/gammaquantum/My Drive/projects/coding-references/type-hints.md`
15. `/Users/gammaquantum/My Drive/projects/coding-references/test-structure.md`
16. `/Users/gammaquantum/My Drive/projects/coding-references/docstring-template.md`

Project boundary:

- Claim Audit Lab audits whether draft claims are supported by supplied evidence.
- Do not call the tool a fact checker.
- Do not use private application materials in fixtures.
- Do not add live LLM calls or network calls in v1.
- Candidate scores are ranking signals, not final support labels.
- Do not add support-score or assessment-confidence scoring in Phase 10.
- Keep research-use measurement rules in `docs/research-use.md`; do not let them expand the v1 shipping path.

Current workspace:

- Live asset folder: `portfolio/live-asset/claim-audit-lab/`
- `models.py` is complete and verified for the current contracts.
- `loader.py` is complete and verified for Markdown/plain text drafts plus YAML/JSON evidence bundles.
- `claim_extraction.py` is complete and verified for conservative deterministic claim extraction.
- `evidence_matching.py` is complete and verified for deterministic candidate evidence links.
- `rules.py` is complete and verified for deterministic support assessment.
- `audit_document(...)` is hardened through Phase 6 and returns typed `AuditReport` values with summary counts, flattened rule flags, warnings, and limitations.
- Phase 7 is complete: `report.py` renders human-review Markdown and typed JSON.
- Phase 8 is complete: `claim-audit audit` and `claim-audit demo` work after editable install.
- Phase 9 is complete: AI research and Product README both have draft, evidence, Markdown report, and JSON report artifacts; `tests/test_report.py` locks both generated families to current renderer output and scans public examples for private-data or secret markers.
- Current tests: model, loader, extraction, evidence matching, rules, auditor, report, vertical-slice, and CLI tests; 108 passing with 96% total coverage as of the Phase 9 tie-off.

Implementation task:

1. Follow the Phase 10 section of `docs/master-plan.md`.
2. Run the full validation sweep: compileall, pytest, ruff check, ruff format check, mypy, coverage run, and coverage report.
3. Inspect README, generated reports, example drafts/evidence, and validation docs for overclaiming language, stale phase wording, local-only paths, placeholder links, private data, or hidden network/API-key assumptions.
4. Update `docs/validation-matrix-reference.md` only from actual evidence. Phase 10 should document current public v1 gaps instead of marking planned rows verified by intention.
5. Keep audit semantics stable unless the sweep exposes a narrow bug.

Required behavior:

- Normal tests and demo/example runs require no network access, API keys, or live LLM calls.
- Markdown and JSON reports remain stable and inspectable.
- Public copy uses supplied-evidence support language, not truth-verification language.
- Candidate scores remain ranking signals, not support scores.

After implementing, run:

.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report

When done, update:

- `portfolio/live-asset/claim-audit-lab/docs/master-plan.md`
- `portfolio/live-asset/claim-audit-lab/docs/verification.md`
- `portfolio/live-asset/claim-audit-lab/docs/validation-matrix-reference.md`
- `portfolio/live-asset/claim-audit-lab/README.md` if public instructions or status changed
- `log/job-hunt-log.md`
- `pipeline.md`

Keep the final response concise: changed files, checks run, and the next best step.
```
