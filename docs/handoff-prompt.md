# Claim Audit Lab Handoff Prompt

Use this prompt to start the next implementation slice in a fresh chat.

```text
We are in `/Users/gammaquantum/My Drive/projects/job-hunt`.

I want to continue Claim Audit Lab with Phase 4: deterministic evidence matching.

Before changing files, read these in order:

1. `AGENTS.md`
2. `log/job-hunt-log.md`
3. `portfolio/AGENTS.md`
4. `portfolio/planning/claim-audit-lab-plan.md`
5. `portfolio/planning/claim-audit-lab-control-checklist.md`
6. `portfolio/live-asset/claim-audit-lab/README.md`
7. `portfolio/live-asset/claim-audit-lab/docs/master-plan.md`
8. `portfolio/live-asset/claim-audit-lab/docs/validation-matrix-reference.md`
9. `/Users/gammaquantum/My Drive/projects/coding-references/type-hints.md`
10. `/Users/gammaquantum/My Drive/projects/coding-references/test-structure.md`
11. `/Users/gammaquantum/My Drive/projects/coding-references/docstring-template.md`

Project boundary:

- Claim Audit Lab audits whether draft claims are supported by supplied evidence.
- It does not verify external truth.
- Do not call it a fact checker.
- Do not use private application materials in fixtures.
- Do not add live LLM calls in v1.
- Keep the first version CLI-first and deterministic.
- If the tool is used for scaffold-evaluation research, treat it as one measurement channel and freeze version/config/rules before auditing experiment outputs.

Current workspace:

- Live asset folder: `portfolio/live-asset/claim-audit-lab/`
- `models.py` is complete and verified.
- `loader.py` is complete and verified for Markdown/plain text drafts plus YAML/JSON evidence bundles.
- `claim_extraction.py` is complete and verified for conservative deterministic claim extraction.
- Current tests: `tests/test_models.py`, `tests/test_loader.py`, and `tests/test_claim_extraction.py`, 38 passing.
- First fixture draft: `examples/drafts/ai-research-note.md`
- First fixture evidence bundle: `examples/evidence/ai-research-evidence.yml`
- Loader fixtures: `tests/fixtures/`
- Research-use integrity notes now require independent validation fixtures, human-review calibration, run metadata, and no post-outcome rule tuning.

Next implementation task:

Plan and implement `portfolio/live-asset/claim-audit-lab/src/claim_audit_lab/evidence_matching.py` with focused tests in `tests/test_evidence_matching.py`.

Keep `evidence_matching.py` focused on deterministic candidate-evidence matching only. Do not implement final support labels, rule flags, audit orchestration, report rendering, or CLI behavior inside it.

Expected behavior:

- Accept extracted `Claim` objects and an `EvidenceBundle`.
- Return bounded `EvidenceCandidate` objects that preserve source IDs, excerpt IDs, scores, and short rationales.
- Match numeric claims to excerpts with the same numbers.
- Avoid making mismatched numeric values appear fully supported.
- Use transparent deterministic scoring based on numbers, dates, key terms, quoted phrases, and text overlap.
- Preserve multiple candidate sources when their scores differ, so later rule/report layers can see reliability and support differences.

First tests to add:

- Numeric claim with the same value as an evidence excerpt receives a candidate evidence link.
- Numeric claim with a different value does not receive a high candidate score.
- Candidate scores are bounded from `0.0` to `1.0`.
- Candidate evidence preserves source ID and excerpt ID.
- Multiple evidence candidates are sorted predictably and capped by `AuditConfig.max_candidate_evidence`.
- Empty evidence bundles return no candidates without crashing.

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
- `portfolio/live-asset/claim-audit-lab/README.md` if behavior changed
- `log/job-hunt-log.md`

Keep the final response concise: changed files, checks run, and the next best step.
```
