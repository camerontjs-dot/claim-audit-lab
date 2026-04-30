# Verification notes

Last updated: 2026-04-30

## 2026-04-30: Git initialization and validation package planning

Added a visible top-level validation package so the pharma-equipment validation analogy is tracked as a first-class part of the repo after the first CLI-first version is made.

Files updated:

- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `validation/README.md`
- `validation/qualification-plan.md`
- `validation/iq-installation.md`
- `validation/oq-operational.md`
- `validation/pq-performance.md`
- `validation/deviation-log.md`
- removed `docs/qualification-plan.md`
- `docs/verification.md`
- `../../../log/job-hunt-log.md`

Checks run:

- Documentation-only update; no code checks were required.
- Confirmed no existing git toplevel before initialization.
- Initialized git for `portfolio/live-asset/claim-audit-lab/`.
- Checked repository status after initialization.
- Confirmed the README, master plan, and validation matrix point to the top-level `validation/` package.

## 2026-04-29: Phase 3 conservative claim extraction

Implemented deterministic claim extraction in `src/claim_audit_lab/claim_extraction.py` and added `tests/test_claim_extraction.py`.

Files updated:

- `src/claim_audit_lab/claim_extraction.py`
- `tests/test_claim_extraction.py`
- `README.md`
- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `docs/verification.md`
- `docs/handoff-prompt.md`
- `../../../log/job-hunt-log.md`

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format src/claim_audit_lab/claim_extraction.py tests/test_claim_extraction.py
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Results:

- Virtualenv compile check passed.
- `pytest`: 38 passed.
- `ruff check .`: passed.
- `ruff format`: reformatted the extraction module; tests were already formatted.
- `ruff format --check .`: passed; 12 files already formatted.
- `mypy src`: passed.
- Coverage run: 38 passed; total coverage 96%.
- `CAL-REQ-004` and `CAL-REQ-023` are verified by extraction tests.

## 2026-04-29: Research-use integrity planning

Updated planning and control docs so Claim Audit Lab can be used as one measurement channel for scaffold-evaluation research without appearing tuned to prove the experiment.

Files updated:

- `docs/master-plan.md`
- `docs/validation-matrix-reference.md`
- `README.md`
- `docs/handoff-prompt.md`
- `../../../planning/claim-audit-lab-plan.md`
- `../../../planning/claim-audit-lab-control-checklist.md`
- `../../../planning/research-proposal/research-proposal-scaffold-evaluation.md`
- `../../../../log/job-hunt-log.md`

Checks run:

- Documentation-only update; no code checks were required.

## 2026-04-28: Phase 2 loaders

Implemented `src/claim_audit_lab/loader.py`, `tests/test_loader.py`, loader fixtures under `tests/fixtures/`, and added `types-PyYAML` to dev dependencies for strict mypy coverage.

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/claim-audit --help
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Results:

- Editable install with refreshed dev dependencies passed.
- Virtualenv compile check passed.
- `pytest`: 26 passed.
- `ruff check .`: passed.
- `ruff format .`: reformatted scaffold and changed files.
- `ruff format --check .`: passed; 11 files already formatted.
- `mypy src`: passed.
- `claim-audit --help`: passed.
- Coverage run: 26 passed; total coverage 96%.
- `CAL-REQ-002` and `CAL-REQ-003` are verified by loader tests.

## 2026-04-28: Phase 1 typed model layer

Implemented `src/claim_audit_lab/models.py` and `tests/test_models.py`.

Checks run from `portfolio/live-asset/claim-audit-lab/`:

```bash
python3.11 -m compileall -q src tests
python3.11 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy src
.venv/bin/python -m ruff format --check src/claim_audit_lab/models.py tests/test_models.py
.venv/bin/claim-audit --help
```

Results:

- System Python compile check passed.
- Local virtual environment was created because system Python did not have `pytest`.
- Editable install with dev dependencies passed.
- Virtualenv compile check passed.
- `pytest`: 16 passed.
- `ruff check .`: passed.
- `mypy src`: passed.
- `ruff format --check` for changed files: passed.
- `claim-audit --help`: passed.

Note:

- The earlier full-project formatting warning was resolved during the Phase 2 formatting sweep.
