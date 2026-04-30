# Claim Audit Lab Handoff Prompt

Use this prompt to start Phase 4A in a fresh chat.

```text
We are in `/Users/gammaquantum/My Drive/projects/job-hunt`.

I want to implement Claim Audit Lab Phase 4A: a runnable vertical slice.

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
11. `portfolio/live-asset/claim-audit-lab/docs/research-use.md`
12. `/Users/gammaquantum/My Drive/projects/coding-references/type-hints.md`
13. `/Users/gammaquantum/My Drive/projects/coding-references/test-structure.md`
14. `/Users/gammaquantum/My Drive/projects/coding-references/docstring-template.md`

Project boundary:

- Claim Audit Lab audits whether draft claims are supported by supplied evidence.
- Phase 4A should make the tool runnable for one checked-in example without pretending the final rule engine is complete.
- Do not call the tool a fact checker.
- Do not use private application materials in fixtures.
- Do not add live LLM calls or network calls in v1.
- Keep the slice deterministic and inspectable.
- Keep research-use measurement rules in `docs/research-use.md`; do not let them expand the v1 shipping path.

Current workspace:

- Live asset folder: `portfolio/live-asset/claim-audit-lab/`
- `models.py` is complete and verified for the current contracts.
- `loader.py` is complete and verified for Markdown/plain text drafts plus YAML/JSON evidence bundles.
- `claim_extraction.py` is complete and verified for conservative deterministic claim extraction.
- `evidence_matching.py` is complete and verified for deterministic candidate evidence links.
- Current tests: `tests/test_models.py`, `tests/test_loader.py`, `tests/test_claim_extraction.py`, and `tests/test_evidence_matching.py`, 53 passing as of the last implementation phase.
- First fixture family: `examples/drafts/ai-research-note.md`, `examples/evidence/ai-research-evidence.yml`, and `examples/reports/ai-research-note.target.md`.
- Second fixture family: `examples/drafts/product-readme-note.md` and `examples/evidence/product-readme-evidence.yml`.

Implementation task:

1. Build a thin runnable path: load draft/evidence -> extract claims -> match candidate evidence -> return a minimal typed audit result.
2. Implement or seed `audit_document(...)` in `src/claim_audit_lab/auditor.py`.
3. Implement a minimal Markdown renderer in `src/claim_audit_lab/report.py` that exposes summary, claim register, candidate evidence links, and limitations.
4. Add a reviewer-friendly demo entry point, likely `scripts/run_demo.py` or an equivalent documented command.
5. Add focused tests for the vertical slice, using checked-in fictional fixtures.
6. Keep final support labels conservative and clearly provisional until Phase 5 rule checks land.

Required behavior:

- A reviewer can run one local command against a checked-in fixture and see a Markdown report.
- The report includes extracted claims, candidate evidence source/excerpt IDs, scores, rationales, and limitations.
- The slice does not claim external truth verification or full rule coverage.
- High-risk or weak claims are represented as audit findings, not runtime failures.
- Empty or missing evidence behavior can stay minimal if covered later, but the code should not make future handling harder.

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
