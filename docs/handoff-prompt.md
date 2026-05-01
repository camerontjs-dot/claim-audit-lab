# Claim Audit Lab Handoff Prompt

Use this prompt to start Phase 7 in a fresh chat.

```text
We are in `/Users/gammaquantum/My Drive/projects/job-hunt`.

I want to implement Claim Audit Lab Phase 7: report rendering hardening.

Before changing files, read these in order:

1. `AGENTS.md`
2. `log/job-hunt-log.md`
3. `portfolio/AGENTS.md`
4. `portfolio/planning/claim-audit-lab-plan.md`
5. `portfolio/planning/claim-audit-lab-control-checklist.md`
6. `portfolio/live-asset/claim-audit-lab/README.md`
7. `portfolio/live-asset/claim-audit-lab/docs/master-plan.md`
8. `portfolio/live-asset/claim-audit-lab/docs/phase-6-audit-orchestration-plan.md`
9. `portfolio/live-asset/claim-audit-lab/docs/validation-matrix-reference.md`
10. `portfolio/live-asset/claim-audit-lab/docs/phase-4-evidence-matching-plan.md`
11. `portfolio/live-asset/claim-audit-lab/examples/reports/ai-research-note.target.md`
12. `portfolio/live-asset/claim-audit-lab/examples/reports/ai-research-note.slice.md`
13. `portfolio/live-asset/claim-audit-lab/docs/research-use.md`
14. `/Users/gammaquantum/My Drive/projects/coding-references/type-hints.md`
15. `/Users/gammaquantum/My Drive/projects/coding-references/test-structure.md`
16. `/Users/gammaquantum/My Drive/projects/coding-references/docstring-template.md`

Project boundary:

- Claim Audit Lab audits whether draft claims are supported by supplied evidence.
- Do not call the tool a fact checker.
- Do not use private application materials in fixtures.
- Do not add live LLM calls or network calls in v1.
- Keep deterministic candidate matching separate from rule checks.
- Candidate scores are ranking signals, not final support labels.
- Keep research-use measurement rules in `docs/research-use.md`; do not let them expand the v1 shipping path.

Current workspace:

- Live asset folder: `portfolio/live-asset/claim-audit-lab/`
- `models.py` is complete and verified for the current contracts.
- `loader.py` is complete and verified for Markdown/plain text drafts plus YAML/JSON evidence bundles.
- `claim_extraction.py` is complete and verified for conservative deterministic claim extraction.
- `evidence_matching.py` is complete and verified for deterministic candidate evidence links.
- Phase 4A is complete: the repo has a runnable vertical slice with checked-in Markdown/JSON output.
- Phase 5 is complete: `rules.py` performs initial deterministic support assessment, `audit_document(...)` returns rule-assessed `AuditReport` values, `report.py` renders minimal Phase 5 Markdown/JSON, and `scripts/run_demo.py` produces demo outputs.
- Phase 6 is complete: `audit_document(...)` has hardened orchestration helpers, auditor-contract tests, exact report-level rule-flag flattening, summary consistency checks, empty-evidence/no-claim/high-risk behavior, deterministic structured-output coverage, and neutral Phase 6 pipeline limitation wording.
- Phase 6 tie-off was rechecked on 2026-05-01 with compileall, pytest, ruff, mypy, and coverage passing.
- Current tests: model, loader, extraction, evidence matching, rules, auditor, and vertical-slice tests, 82 passing with 95% total coverage as of the Phase 6 tie-off.
- First fixture family: `examples/drafts/ai-research-note.md`, `examples/evidence/ai-research-evidence.yml`, `examples/reports/ai-research-note.target.md`, and `examples/reports/ai-research-note.slice.md`.
- Second fixture family: `examples/drafts/product-readme-note.md` and `examples/evidence/product-readme-evidence.yml`.

Implementation task:

1. Follow the Phase 7 section of `docs/master-plan.md` and use `examples/reports/ai-research-note.target.md` as the report UX reference.
2. Harden `src/claim_audit_lab/report.py` for human-review Markdown and typed JSON output without changing the audit model contract unless a real renderer gap requires it.
3. Add `tests/test_report.py` for required sections, support labels, evidence links, rule flags, summary metrics, limitations, rewrite guidance where available, JSON validation, and report-quality language gates.
4. Keep `audit_document(...)` orchestration and rule taxonomy stable unless a renderer test exposes a narrow bug.
5. Preserve supplied-evidence boundary language and candidate-score discipline.
6. Do not turn CLI behavior, source discovery, second fixture report generation, support scoring, or research-use paired metrics into Phase 7 work.

Required behavior:

- Markdown reports contain summary, claim register, evidence links, support labels, rule flags, limitations, and rewrite guidance where applicable.
- JSON output validates against `AuditReport`.
- Reports contain no `None`, `nan`, empty placeholder sections, or forbidden capability language.
- Candidate scores are displayed as ranking signals only, not support scores.
- Report language says "supported by supplied evidence" rather than truth-verification language.
- The AI research fixture remains the first renderer-quality target; broader example-family generation stays for later phases.

After implementing, run:

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff format src/claim_audit_lab/report.py tests/test_report.py tests/test_vertical_slice.py
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

When done, update:

- `portfolio/live-asset/claim-audit-lab/docs/master-plan.md`
- `portfolio/live-asset/claim-audit-lab/docs/verification.md`
- `portfolio/live-asset/claim-audit-lab/docs/validation-matrix-reference.md`
- `portfolio/live-asset/claim-audit-lab/README.md` if implemented status changed
- `log/job-hunt-log.md`

Keep the final response concise: changed files, checks run, and the next best step.
```
