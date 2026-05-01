# Claim Audit Lab Handoff Prompt

Use this prompt to start Phase 8 in a fresh chat.

```text
We are in `/Users/gammaquantum/My Drive/projects/job-hunt`.

I want to implement Claim Audit Lab Phase 8: CLI.

Before changing files, read these in order:

1. `AGENTS.md`
2. `log/job-hunt-log.md`
3. `portfolio/AGENTS.md`
4. `portfolio/planning/claim-audit-lab-plan.md`
5. `portfolio/planning/claim-audit-lab-control-checklist.md`
6. `portfolio/live-asset/claim-audit-lab/README.md`
7. `portfolio/live-asset/claim-audit-lab/docs/master-plan.md`
8. `portfolio/live-asset/claim-audit-lab/docs/validation-matrix-reference.md`
9. `portfolio/live-asset/claim-audit-lab/docs/phase-6-audit-orchestration-plan.md`
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
- `rules.py` is complete and verified for initial deterministic support assessment.
- `audit_document(...)` is hardened through Phase 6 and returns typed `AuditReport` values with summary counts, flattened rule flags, warnings, and limitations.
- Phase 7 is complete: `report.py` renders human-review Markdown and typed JSON; `tests/test_report.py` covers required sections, labels, evidence links, rule flags, rewrite guidance, JSON validation, fixture sync, and language gates.
- Current tests: model, loader, extraction, evidence matching, rules, auditor, report, and vertical-slice tests, 90 passing with 96% total coverage as of the Phase 7 tie-off.
- First fixture family: `examples/drafts/ai-research-note.md`, `examples/evidence/ai-research-evidence.yml`, `examples/reports/ai-research-note.target.md`, `examples/reports/ai-research-note.slice.md`, and `examples/reports/ai-research-note.slice.json`.
- Second fixture family: `examples/drafts/product-readme-note.md` and `examples/evidence/product-readme-evidence.yml`.

Implementation task:

1. Follow the Phase 8 section of `docs/master-plan.md`.
2. Implement the `claim-audit` CLI entry point in `src/claim_audit_lab/cli.py` using the existing loader, auditor, and report renderer.
3. Add `tests/test_cli.py` for help output, successful Markdown/JSON report writes, malformed evidence failures, and high-risk audit findings that still exit successfully.
4. Keep `audit_document(...)`, rule taxonomy, report rendering, source discovery, and research-use paired metrics stable unless a CLI test exposes a narrow integration bug.
5. Preserve supplied-evidence boundary language and candidate-score discipline.
6. Do not generate the second fixture report family unless the Phase 8 section is explicitly expanded.

Required behavior:

- `claim-audit --help` works after editable install.
- A normal fixture run writes Markdown and JSON reports to requested paths.
- Malformed input fails clearly and exits nonzero.
- Completed audits with high-risk findings exit successfully.
- Normal CLI behavior requires no network access, API keys, or live LLM calls.

After implementing, run:

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff format src/claim_audit_lab/cli.py tests/test_cli.py
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
- `portfolio/live-asset/claim-audit-lab/README.md` if implemented behavior or public instructions changed
- `log/job-hunt-log.md`

Keep the final response concise: changed files, checks run, and the next best step.
```
