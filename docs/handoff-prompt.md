# Claim Audit Lab Handoff Prompt

Use this prompt to start Phase 5 in a fresh chat.

```text
We are in `/Users/gammaquantum/My Drive/projects/job-hunt`.

I want to implement Claim Audit Lab Phase 5: rule checks and support assessment.

Before changing files, read these in order:

1. `AGENTS.md`
2. `log/job-hunt-log.md`
3. `portfolio/AGENTS.md`
4. `portfolio/planning/claim-audit-lab-plan.md`
5. `portfolio/planning/claim-audit-lab-control-checklist.md`
6. `portfolio/live-asset/claim-audit-lab/README.md`
7. `portfolio/live-asset/claim-audit-lab/docs/master-plan.md`
8. `portfolio/live-asset/claim-audit-lab/docs/validation-matrix-reference.md`
9. `portfolio/live-asset/claim-audit-lab/docs/phase-4-evidence-matching-plan.md`
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
- Phase 4A is complete: `audit_document(...)` returns a typed provisional `AuditReport`, `report.py` renders minimal Markdown/JSON, and `scripts/run_demo.py` produces demo outputs.
- Current tests: model, loader, extraction, evidence matching, and vertical-slice tests, 60 passing as of Phase 4A.
- First fixture family: `examples/drafts/ai-research-note.md`, `examples/evidence/ai-research-evidence.yml`, `examples/reports/ai-research-note.target.md`, and `examples/reports/ai-research-note.slice.md`.
- Second fixture family: `examples/drafts/product-readme-note.md` and `examples/evidence/product-readme-evidence.yml`.

Implementation task:

1. Plan and implement `src/claim_audit_lab/rules.py` with deterministic rule checks for the Phase 5 rows in the validation matrix.
2. Add `tests/test_rules.py` for numeric mismatch, causal overreach, comparative evidence, credential/source support, overconfident wording, source reliability/freshness warnings, date/deadline support, and future certainty.
3. Map rule outcomes to support labels and risk labels without letting candidate scores alone decide support.
4. Preserve Phase 4A behavior until the rule tests justify changing labels.
5. Keep rule flags deterministic. Rule-flag IDs should derive from rule code, claim ID, and trigger context rather than list position.
6. Update `audit_document(...)` only as needed for Phase 5 integration; broader orchestration hardening remains Phase 6.

Required behavior:

- Numeric values that differ from the supplied evidence are flagged.
- Causal wording is not fully supported by weak or merely sequential evidence.
- Comparative claims require comparison evidence.
- Credential and public-link claims require source support.
- Overconfident wording such as `always`, `never`, `eliminates`, and `guarantees` is flagged when evidence does not justify certainty.
- Low-reliability-only support and stale sources create visible warnings or lower support.
- High-risk findings are audit results, not runtime failures.

After implementing, run:

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
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
