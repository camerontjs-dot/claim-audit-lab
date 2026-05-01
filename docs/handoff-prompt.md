# Claim Audit Lab Handoff Prompt

Use this prompt to start Phase 6 in a fresh chat.

```text
We are in `/Users/gammaquantum/My Drive/projects/job-hunt`.

I want to implement Claim Audit Lab Phase 6: audit orchestration hardening.

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
- Phase 5 tie-off was rechecked on 2026-05-01 with compileall, pytest, ruff, mypy, and coverage passing.
- Current tests: model, loader, extraction, evidence matching, rules, and vertical-slice tests, 74 passing with 95% total coverage as of the Phase 5 tie-off.
- First fixture family: `examples/drafts/ai-research-note.md`, `examples/evidence/ai-research-evidence.yml`, `examples/reports/ai-research-note.target.md`, and `examples/reports/ai-research-note.slice.md`.
- Second fixture family: `examples/drafts/product-readme-note.md` and `examples/evidence/product-readme-evidence.yml`.

Implementation task:

1. Follow `docs/phase-6-audit-orchestration-plan.md`.
2. Harden `audit_document(draft, evidence_bundle, config=None) -> AuditReport` around the Phase 5 rule layer.
3. Add `tests/test_auditor.py` for structured trace links, empty evidence behavior, high-risk findings as valid audit results, no-claim drafts, bundle warnings, deterministic output, and summary consistency.
4. Keep rule checks in `rules.py`; Phase 6 should coordinate existing extraction, matching, rules, summaries, limitations, and warnings rather than expanding the rule taxonomy.
5. Preserve deterministic rule-flag IDs and candidate-score discipline.
6. Do not turn CLI behavior or full report rendering into Phase 6 work.

Required behavior:

- Structured `AuditReport` links claims, candidate evidence, rule flags, summary counts, evidence warnings, and limitations coherently.
- Empty evidence bundles produce `needs_source` assessments and a useful evidence-bundle warning.
- High-risk findings are audit results, not runtime failures.
- Summary counts stay consistent with the claim assessments.
- Report-level rule flags exactly flatten claim-level rule flags and point to assessed claim IDs.
- No-claim drafts return valid zero-claim reports.
- The AI research fixture keeps the Phase 5 target labels: `overstated`, `supported`, `partially_supported`, `overstated`.

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
