# Claim Audit Lab Handoff Prompt

Use this prompt to start Phase 11 in a fresh chat.

```text
We are in `/Users/gammaquantum/My Drive/projects/job-hunt`.

I want to implement Claim Audit Lab Phase 11: public packaging.

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
10. `portfolio/live-asset/claim-audit-lab/docs/phase-11-public-packaging-plan.md`
11. `portfolio/live-asset/claim-audit-lab/docs/verification.md`
12. `portfolio/live-asset/claim-audit-lab/examples/reports/ai-research-note.slice.md`
13. `portfolio/live-asset/claim-audit-lab/examples/reports/product-readme-note.slice.md`
14. `portfolio/live-asset/claim-audit-lab/validation/README.md`
15. `portfolio/live-asset/claim-audit-lab/docs/research-use.md`
16. `/Users/gammaquantum/My Drive/projects/coding-references/type-hints.md`
17. `/Users/gammaquantum/My Drive/projects/coding-references/test-structure.md`
18. `/Users/gammaquantum/My Drive/projects/coding-references/docstring-template.md`

Project boundary:

- Claim Audit Lab audits whether draft claims are supported by supplied evidence.
- Do not call the tool a fact checker.
- Do not use private application materials in fixtures or public copy.
- Do not add live LLM calls, network calls, source discovery, support scores, or assessment-confidence scoring in Phase 11.
- Candidate scores are ranking signals, not final support labels.
- Keep research-use measurement rules in `docs/research-use.md`; do not let them expand the v1 shipping path.
- Do not execute the IQ/OQ/PQ validation package in Phase 11; Phase 12 owns that pass.

Current workspace:

- Live asset folder: `portfolio/live-asset/claim-audit-lab/`
- `models.py`, `loader.py`, `claim_extraction.py`, `evidence_matching.py`, `rules.py`, `auditor.py`, `report.py`, and `cli.py` are implemented and verified for the current deterministic CLI-first scope.
- `claim-audit audit` and `claim-audit demo` work after editable install.
- AI research and Product README both have draft, evidence, Markdown report, and JSON report artifacts.
- Phase 10 is complete: the full verification chain and editable-install smoke test passed with 108 tests and 96% total coverage.
- `CAL-REQ-012` and `CAL-REQ-027` were marked verified in Phase 10.
- `CAL-REQ-018` remains planned because Phase 11 owns the public README rewrite.
- `CAL-REQ-024`, `CAL-REQ-039`, `CAL-REQ-036`, and `CAL-REQ-040` remain planned with documented gaps or later-phase ownership.

Implementation task:

1. Follow `portfolio/live-asset/claim-audit-lab/docs/phase-11-public-packaging-plan.md` and the Phase 11 section of `portfolio/live-asset/claim-audit-lab/docs/master-plan.md`.
2. Replace the README stub with a public-facing README that accurately explains what the tool does, what it does not do, quick start commands, labels, report sections, validation approach, limitations, and next steps.
3. Prepare social card / GitHub-pin assets that match the supplied-evidence support framing and do not overclaim.
4. Keep the checked-in example reports synchronized if README examples or packaging copy requires report regeneration.
5. Update `docs/validation-matrix-reference.md` only from actual evidence. `CAL-REQ-018` can be verified only when the public README matches implemented behavior. `CAL-REQ-040` can be verified only when the public assets exist and pass review.
6. Keep IQ/OQ/PQ execution planned for Phase 12.

Required behavior:

- Normal tests and demo/example runs require no network access, API keys, or live LLM calls.
- Public copy uses supplied-evidence support language, not truth-verification language.
- Qualification language is validation-inspired portfolio control, not GxP/GMP/CSV/FDA compliance.
- Candidate scores remain ranking signals, not support scores.

After implementing, run:

.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
.venv/bin/python -m pip install -e ".[dev]"
. .venv/bin/activate && claim-audit --help

When done, update:

- `portfolio/live-asset/claim-audit-lab/docs/master-plan.md`
- `portfolio/live-asset/claim-audit-lab/docs/verification.md`
- `portfolio/live-asset/claim-audit-lab/docs/validation-matrix-reference.md`
- `portfolio/live-asset/claim-audit-lab/README.md`
- `log/job-hunt-log.md`
- `pipeline.md`

Keep the final response concise: changed files, checks run, and the next best step.
```
