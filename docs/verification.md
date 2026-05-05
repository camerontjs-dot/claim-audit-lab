# Verification Summary

last_updated: 2026-05-05

Purpose: record the current public release verification for Claim Audit Lab.

## Release Candidate

Claim Audit Lab `0.1.0` is verified as a deterministic CLI-first portfolio artifact.

This verification does not claim that the tool checks outside-world truth, performs source discovery, provides regulated validation, or is calibrated as a research measurement instrument.

## Checks Run

Commands run from the repository root:

```bash
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
. .venv/bin/activate && claim-audit --help
. .venv/bin/activate && claim-audit demo --out-dir build/reports/release-candidate-smoke
.venv/bin/python -m build --sdist --wheel
tar -tzf dist/claim_audit_lab-0.1.0.tar.gz | rg "(CHANGELOG.md|MANIFEST.in|examples/drafts/ai-research-note.md|validation/README.md|assets/social-card.svg|scripts/run_demo.py)"
rg -n "fact check|fact-check|truth verifier|verify external truth|proven true|guaranteed true|verified externally|FDA|GxP|GMP|Computer System Validation|CSV validation|regulated compliance" README.md CHANGELOG.md docs validation examples assets
rg -n "TODO|TBD|placeholder|localhost|/Users/|api[_-]?key|secret|token|password|INSERT|your-|coming soon" README.md CHANGELOG.md docs validation examples assets
rg -n "openai|anthropic|requests|httpx|urllib|socket|dotenv|os\.environ" pyproject.toml src tests scripts README.md CHANGELOG.md
git status --short --ignored
```

## Results

- Editable install passed with dev dependencies.
- Virtualenv compile check passed.
- `pytest`: 112 passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed; 19 files already formatted.
- `mypy src`: passed across 9 source files.
- Coverage run: 112 passed; total coverage 96%.
- Activated `claim-audit --help` showed `audit` and `demo` subcommands.
- Activated `claim-audit demo --out-dir build/reports/release-candidate-smoke` wrote ignored Markdown and JSON outputs and completed with 4 claims assessed.
- `python -m build --sdist --wheel` built `claim_audit_lab-0.1.0.tar.gz` and `claim_audit_lab-0.1.0-py3-none-any.whl`.
- Source distribution inspection confirmed release-facing docs, example data, validation records, assets, and the demo script are included.
- Public-language scans produced only expected validation disclaimers, guardrails, source-reference matches, or scan-command self-matches.
- Placeholder/private-data/local-path scans produced only expected validation-history wording or scan-command self-matches.
- Network/API/LLM scan produced no package, source, test, script, README, or changelog dependency on network clients, provider SDKs, environment secrets, or API keys.

## Public Repo Contents

The public repository contains the release-facing project surface:

- package metadata and license files
- implementation under `src/`
- tests and test fixtures under `tests/`
- fictional draft/evidence/report examples under `examples/`
- public validation docs under `docs/` and `validation/`
- public assets under `assets/`
- reviewer demo script under `scripts/`
