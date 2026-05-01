# Claim Audit Lab Handoff Prompt

Use this prompt to start Phase 9 in a fresh chat.

```text
We are in `/Users/gammaquantum/My Drive/projects/job-hunt`.

I want to implement Claim Audit Lab Phase 9: example families.

Before changing files, read these in order:

1. `AGENTS.md`
2. `log/job-hunt-log.md`
3. `portfolio/AGENTS.md`
4. `portfolio/planning/claim-audit-lab-plan.md`
5. `portfolio/planning/claim-audit-lab-control-checklist.md`
6. `portfolio/live-asset/claim-audit-lab/README.md`
7. `portfolio/live-asset/claim-audit-lab/docs/master-plan.md`
8. `portfolio/live-asset/claim-audit-lab/docs/validation-matrix-reference.md`
9. `portfolio/live-asset/claim-audit-lab/docs/phase-8-cli-plan.md`
10. `portfolio/live-asset/claim-audit-lab/examples/reports/ai-research-note.target.md`
11. `portfolio/live-asset/claim-audit-lab/examples/reports/ai-research-note.slice.md`
12. `portfolio/live-asset/claim-audit-lab/docs/research-use.md`
13. `/Users/gammaquantum/My Drive/projects/coding-references/type-hints.md`
14. `/Users/gammaquantum/My Drive/projects/coding-references/test-structure.md`
15. `/Users/gammaquantum/My Drive/projects/coding-references/docstring-template.md`

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
- `rules.py` is complete and verified for deterministic support assessment.
- `audit_document(...)` is hardened through Phase 6 and returns typed `AuditReport` values with summary counts, flattened rule flags, warnings, and limitations.
- Phase 7 is complete: `report.py` renders human-review Markdown and typed JSON; `tests/test_report.py` covers required sections, labels, evidence links, rule flags, rewrite guidance, JSON validation, fixture sync, and language gates.
- Phase 8 is complete: `claim-audit audit` and `claim-audit demo` work after editable install; `tests/test_cli.py` covers help, output paths, malformed input, high-risk exit success, demo behavior, checked-in fixture protection, and language gates.
- Current tests: model, loader, extraction, evidence matching, rules, auditor, report, vertical-slice, and CLI tests; 104 passing with 96% total coverage as of the Phase 8 tie-off.
- First fixture family: `examples/drafts/ai-research-note.md`, `examples/evidence/ai-research-evidence.yml`, `examples/reports/ai-research-note.target.md`, `examples/reports/ai-research-note.slice.md`, and `examples/reports/ai-research-note.slice.json`.
- Second fixture family seed: `examples/drafts/product-readme-note.md` and `examples/evidence/product-readme-evidence.yml`.

Implementation task:

1. Follow the Phase 9 section of `docs/master-plan.md`.
2. Generate Markdown and JSON report artifacts for the Product README fixture family.
3. Add or update focused tests so the second-family reports are generated, round-trip through `AuditReport`, and preserve supplied-evidence boundary language.
4. Review public example data for fictional/sanitized content, no tokens, no private application material, and no local-only paths.
5. Update `docs/validation-matrix-reference.md` only from actual evidence. Phase 9 should target `CAL-REQ-017` and `CAL-REQ-028`; do not advance unrelated rows unless new evidence exists.
6. Keep audit semantics stable unless the second fixture exposes a narrow bug.

Required behavior:

- At least two complete fictional example families have draft, evidence, Markdown report, and JSON report artifacts.
- Generated reports require no network access, API keys, or live LLM calls.
- Candidate scores remain ranking signals, not support scores.
- No support-score or assessment-confidence score is added in Phase 9.

After implementing, run:

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff format <changed python files>
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
- `portfolio/live-asset/claim-audit-lab/README.md` if public example instructions changed
- `log/job-hunt-log.md`
- `pipeline.md`

Keep the final response concise: changed files, checks run, and the next best step.
```
