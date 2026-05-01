# Phase 11 Public Packaging Plan

status: planned
last_updated: 2026-05-01
phase: 11

Purpose: make Claim Audit Lab ready for public portfolio review without changing audit semantics. Phase 11 is a packaging, documentation, and public-positioning slice; it should make the existing CLI-first tool understandable, runnable, and visually presentable.

## Starting State

Phase 10 is complete. The full deterministic verification chain and editable-install smoke test passed with 108 tests and 96% total coverage. `CAL-REQ-012` and `CAL-REQ-027` are verified. The README is still a stub, and public packaging rows remain planned.

Current implemented behavior:

- `claim-audit audit` loads a draft and supplied evidence bundle, produces Markdown, and can also write typed JSON.
- `claim-audit demo` runs checked-in fictional fixtures and writes output under `build/reports/` by default.
- The repository includes two fictional draft/evidence/report families: AI research memo and Product README paragraph.
- Normal tests, examples, and demo runs require no network access, API keys, live LLM calls, or private application materials.
- Candidate evidence scores are ranking signals only; support labels come from deterministic rule assessment.

## In Scope

- Replace the README stub with a public-facing README that matches implemented behavior.
- Add or prepare public portfolio assets, including social card and GitHub-pin material.
- Make quick start and example commands copy/paste accurate for a reviewer.
- Explain the supplied-evidence boundary clearly: the tool audits support from provided evidence; it does not verify external truth.
- Explain labels, report sections, rule checks, validation approach, limitations, and next steps.
- Link the validation package as validation-inspired portfolio control, not regulated compliance.
- Regenerate checked-in example reports only if README examples or packaging copy requires output changes.
- Run public-copy scans for placeholder links, private data, local-only paths, secrets, and overclaiming.
- Update the validation matrix only from evidence created in this phase.
- Keep `docs/handoff-prompt.md`, `docs/verification.md`, `docs/master-plan.md`, `README.md`, `pipeline.md`, and `log/job-hunt-log.md` synchronized at the end.

## Out Of Scope

- No audit semantic changes.
- No support scores or assessment-confidence scores.
- No source discovery, web search, provider SDKs, live LLM calls, or network calls.
- No new fixture family unless public packaging exposes a concrete gap.
- No IQ/OQ/PQ protocol execution; Phase 12 owns the formal validation-package pass.
- No claim that Claim Audit Lab is a fact checker, truth verifier, regulated validation system, or proof that scaffolded workflows work.

## Requirement Targets

Phase 11 should be able to verify:

- `CAL-REQ-018`: README matches implemented behavior.
- `CAL-REQ-040`: public packaging includes social card or GitHub-pin assets aligned with repo positioning.

Phase 11 should keep planned unless new evidence actually closes them:

- `CAL-REQ-024`: support-quality warning/report polish.
- `CAL-REQ-036`: executed validation package.
- `CAL-REQ-039`: explicit Markdown anchor policy if not fully documented and tested.

## Work Packages

### 1. README Rewrite

Create a public README with these sections:

- Project name and one-sentence positioning.
- What it does.
- What it does not do.
- Quick start.
- Example commands.
- Example output summary with links to checked-in reports.
- How the audit works at a high level.
- Inputs and data model.
- Support labels and risk labels.
- Rule checks and limitations.
- Validation approach.
- Repository map.
- Development and verification commands.
- Current status and next steps.

Acceptance checks:

- Commands work after editable install.
- README references only files that exist.
- README does not promise source discovery, outside-world truth verification, live LLM behavior, or regulated compliance.
- README explains candidate scores as ranking signals, not final support labels.

### 2. Public Assets

Prepare an `assets/` surface for public packaging. Recommended deliverables:

- `assets/social-card.svg`: 1200 x 628 source card for GitHub/LinkedIn surfaces.
- `assets/social-card.png`: exported PNG if tooling is available in the session.
- `assets/github-pin.md`: short repo-pin copy, topics, About text, and LinkedIn Featured caption.

Asset positioning:

- Headline: `Claim Audit Lab`
- Descriptor: `supplied-evidence claim audit`
- Supporting language should emphasize traceable support, deterministic checks, inspectable reports, and no network/API-key requirement.
- Avoid truth-verification, fact-checking, proof, compliance, or research-result language.

Acceptance checks:

- Asset files exist and are linked from the README or packaging notes.
- Text remains legible and consistent with the README.
- Social/GitHub-pin copy maps to implemented behavior.

### 3. Report And Example Sync

Review checked-in reports:

- `examples/reports/ai-research-note.slice.md`
- `examples/reports/ai-research-note.slice.json`
- `examples/reports/product-readme-note.slice.md`
- `examples/reports/product-readme-note.slice.json`

Regenerate only when needed:

```bash
python scripts/run_demo.py --draft examples/drafts/ai-research-note.md --evidence examples/evidence/ai-research-evidence.yml --update-fixture
python scripts/run_demo.py --draft examples/drafts/product-readme-note.md --evidence examples/evidence/product-readme-evidence.yml --update-fixture
```

Acceptance checks:

- Checked-in reports match the current renderer.
- Reports remain free of private data, secrets, placeholder copy, and forbidden capability language.

### 4. Public-Copy Sweep

Run scans after README/assets are drafted:

```bash
rg -n "fact check|fact-check|truth|true|false|proven|guarantee|guaranteed|verified externally|FDA|GxP|GMP|CSV|compliance" README.md docs validation examples assets
rg -n "TODO|TBD|placeholder|localhost|/Users/|api[_-]?key|secret|token|password" README.md docs validation examples assets
rg -n "openai|anthropic|requests|httpx|urllib|socket|dotenv|os\.environ" README.md pyproject.toml src tests scripts docs validation examples
```

Review matches manually. Some terms are allowed when they appear as explicit boundary language or avoid-list examples.

### 5. Verification

Run the normal verification chain:

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
.venv/bin/python -m pip install -e ".[dev]"
. .venv/bin/activate && claim-audit --help
```

If assets are generated, also verify the image dimensions and readability before treating `CAL-REQ-040` as verified.

## End-Of-Phase Updates

Update these files at the end of Phase 11:

- `README.md`
- `docs/master-plan.md`
- `docs/verification.md`
- `docs/validation-matrix-reference.md`
- `docs/handoff-prompt.md`
- `validation/README.md` if public packaging affects validation wording
- `../../../pipeline.md`
- `../../../log/job-hunt-log.md`

Expected final status:

- Phase 11 marked complete.
- Phase 12 validation package execution becomes the next implementation step.
- `CAL-REQ-018` verified if README matches behavior.
- `CAL-REQ-040` verified if public assets exist and pass review.
- Remaining planned rows keep explicit rationale.

## Pickup Prompt

Use this in the next session:

```text
Start Claim Audit Lab Phase 11 public packaging. Read `portfolio/live-asset/claim-audit-lab/docs/phase-11-public-packaging-plan.md` first, then follow the handoff in `portfolio/live-asset/claim-audit-lab/docs/handoff-prompt.md`. Implement only packaging/docs/assets work: public README, social/GitHub-pin assets, public-copy sweeps, verification, and status sync. Do not change audit semantics, add source discovery, add live LLM/network calls, execute IQ/OQ/PQ, or call the tool a fact checker.
```
