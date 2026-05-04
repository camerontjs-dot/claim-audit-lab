# Claim Audit Lab Handoff Prompt

Use this prompt to start Phase 12 in a fresh chat.

```text
We are in `/Users/gammaquantum/My Drive/projects/job-hunt`.

I want to implement Claim Audit Lab Phase 12: validation package execution.

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
11. `portfolio/live-asset/claim-audit-lab/validation/README.md`
12. `portfolio/live-asset/claim-audit-lab/validation/qualification-plan.md`
13. `portfolio/live-asset/claim-audit-lab/validation/iq-installation.md`
14. `portfolio/live-asset/claim-audit-lab/validation/oq-operational.md`
15. `portfolio/live-asset/claim-audit-lab/validation/pq-performance.md`
16. `portfolio/live-asset/claim-audit-lab/validation/deviation-log.md`
17. `portfolio/live-asset/claim-audit-lab/examples/reports/ai-research-note.slice.md`
18. `portfolio/live-asset/claim-audit-lab/examples/reports/product-readme-note.slice.md`
19. `portfolio/live-asset/claim-audit-lab/docs/research-use.md`

Project boundary:

- Claim Audit Lab audits whether draft claims are supported by supplied evidence.
- Do not call the tool a fact checker.
- Do not use private application materials in fixtures or public copy.
- Do not add live LLM calls, network calls, source discovery, support scores, or assessment-confidence scoring in Phase 12.
- Candidate scores are ranking signals, not final support labels.
- Keep research-use measurement rules in `docs/research-use.md`; do not let them expand the v1 shipping path.

Current workspace:

- Live asset folder: `portfolio/live-asset/claim-audit-lab/`
- `models.py`, `loader.py`, `claim_extraction.py`, `evidence_matching.py`, `rules.py`, `auditor.py`, `report.py`, and `cli.py` are implemented and verified for the deterministic CLI-first scope.
- `claim-audit audit` and `claim-audit demo` work after editable install.
- AI research and Product README both have draft, evidence, generated Markdown report, and generated JSON report artifacts.
- Phase 11 is complete: public README, MIT license, package metadata, social-card SVG, GitHub-pin copy, refreshed generated reports, and public-copy scans are done.
- `CAL-REQ-018` and `CAL-REQ-040` are verified.
- `CAL-REQ-024`, `CAL-REQ-036`, and `CAL-REQ-039` remain planned with explicit gap rationale.

Implementation task:

1. Execute the IQ/OQ/PQ-inspired validation package from `validation/README.md` and the Phase 12 section of `docs/master-plan.md`.
2. Fill in the validation protocol records only from current commands, test results, report artifacts, and inspection evidence.
3. Record deviations or accepted limitations in `validation/deviation-log.md` instead of hiding gaps.
4. Update `docs/validation-matrix-reference.md` only from actual evidence. `CAL-REQ-036` can be verified only when the validation package execution records are complete.
5. Keep audit semantics, source discovery, live LLM/network calls, and support scoring out of Phase 12.

Required behavior:

- Normal tests and demo/example runs require no network access, API keys, or live LLM calls.
- Public copy uses supplied-evidence support language, not truth-verification language.
- Qualification language is validation-inspired portfolio control, not regulated compliance.
- Candidate scores remain ranking signals, not support scores.

After implementing, run:

.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
. .venv/bin/activate && claim-audit --help
. .venv/bin/activate && claim-audit demo --out-dir build/reports/phase-12-smoke

When done, update:

- `portfolio/live-asset/claim-audit-lab/docs/master-plan.md`
- `portfolio/live-asset/claim-audit-lab/docs/verification.md`
- `portfolio/live-asset/claim-audit-lab/docs/validation-matrix-reference.md`
- `portfolio/live-asset/claim-audit-lab/validation/`
- `log/job-hunt-log.md`
- `pipeline.md`

Keep the final response concise: changed files, checks run, deviations recorded, and the next best step.
```
