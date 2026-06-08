# Verification Summary

last_updated: 2026-05-11

Purpose: record the current public release verification for Claim Audit Lab.

## Release Candidate

Claim Audit Lab `0.1.0` is verified as a deterministic CLI-first portfolio artifact.

This verification does not claim that the tool checks outside-world truth, performs source discovery, provides regulated validation, or is calibrated as a research measurement instrument.

The v1 validation package is complete for the public fictional-fixture CLI scope. Real-data fixture qualification and human-review calibration are future validation gates before real-case, sensitive-material, production-like, or research-measurement use.

## C-B Accommodation Addendum

On 2026-05-11, Claim Audit Lab's C-B accommodation was verified against locked Apparatus Contracts v1.0.0 and a synthetic Evidence Bundler fixture round trip. This verifies the engineering handoff path only: C-B schema intake, hash checking, adapter behavior, audited output-copy writing, CLI exposure, and documentation. It does not claim real retrieval quality, human-review calibration, or research-measurement validity.

Commands run from `live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m pytest tests/test_cb_models.py
.venv/bin/python -m pytest tests/test_cb_bundle_loader.py
.venv/bin/python -m pytest tests/test_cb_adapter.py
.venv/bin/python -m pytest tests/test_cb_output_writer.py
.venv/bin/python -m pytest tests/test_cli.py
.venv/bin/python -m pytest
.venv/bin/ruff check .
.venv/bin/python -m compileall src
.venv/bin/claim-audit audit-bundle tests/fixtures/cb/evidence-bundle-minimal --out-dir build/unit6-cli-smoke
```

Synthetic cross-component round trip:

```bash
cd ../evidence-bundler
.venv/bin/evidence-bundler verify-intake tests/fixtures/scaffold-run-minimal
.venv/bin/evidence-bundler build-fixture-bundle tests/fixtures/scaffold-run-minimal --output build/unit7-roundtrip/evidence-bundle-minimal

cd ../claim-audit-lab
.venv/bin/claim-audit audit-bundle ../evidence-bundler/build/unit7-roundtrip/evidence-bundle-minimal --out-dir build/unit7-roundtrip
.venv/bin/python - <<'PY'
from pathlib import Path
from claim_audit_lab.contracts.bundle_loader import load_bundle

contents = load_bundle(
    Path("build/unit7-roundtrip/evidence-bundle-minimal-audited"),
    deviations_dir=Path("build/unit7-roundtrip/deviations-check"),
)
claim = contents.claims[0]
print(claim.claim_id)
print(claim.audit.audit_support_verdict)
print(claim.audit.false_caution_flag)
print(claim.audit.deviation_flag)
PY
```

Results:

- C-B model tests: 5 passed.
- C-B bundle-loader tests: 7 passed.
- C-B adapter tests: 5 passed.
- C-B output-writer tests: 4 passed.
- CLI tests: 16 passed.
- Full CAL test suite: 136 passed.
- `ruff check .`: passed.
- `compileall src`: passed.
- `claim-audit audit-bundle tests/fixtures/cb/evidence-bundle-minimal --out-dir build/unit6-cli-smoke`: wrote `build/unit6-cli-smoke/evidence-bundle-minimal-audited`; 1 claim audited; 0 retrieval seeds skipped.
- Evidence Bundler C-A intake: `Intake verified: tests/fixtures/scaffold-run-minimal`.
- Evidence Bundler C-B fixture writer: wrote `build/unit7-roundtrip/evidence-bundle-minimal`; bundle id `41973898-948c-58b4-8982-61d62ec81500`.
- CAL round-trip audit: wrote `build/unit7-roundtrip/evidence-bundle-minimal-audited`; 1 claim audited; 0 retrieval seeds skipped.
- Reload check for audited output: `clm-001`, `supported`, `False` false-caution flag, `False` deviation flag.

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
- Validation package review found no open v1 validation failures; future real-data and research-use validation gates are recorded in `validation/deviation-log.md`.

## Public Repo Contents

The public repository contains the release-facing project surface:

- package metadata and license files
- implementation under `src/`
- tests and test fixtures under `tests/`
- C-B contract pins and vocabulary under `schema/`
- fictional draft/evidence/report examples under `examples/`
- public validation docs under `docs/` and `validation/`
- public assets under `assets/`
- reviewer demo script under `scripts/`
