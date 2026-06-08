# IQ: Installation Qualification

status: verified
last_updated: 2026-05-11

Purpose: verify that Claim Audit Lab can be installed and invoked in a clean local environment without hidden setup assumptions.

This is a validation-inspired record for a non-regulated portfolio context. It is not intended to demonstrate FDA, EMA, GxP, GMP, CSV, or regulated-compliance status.

## Scope

This protocol covers:

- Python version compatibility
- editable local install
- dev dependency installation
- CLI availability
- C-B contract-path CLI availability
- absence of required network, API key, or private data for normal checks
- ignored build artifacts and local caches

## Prerequisites

- The first CLI-first version exists.
- `pyproject.toml` contains the expected package metadata and dependencies.
- Public examples use fictional or sanitized data.

## Protocol

| Step | Command or inspection | Expected result | Date run | Result | Evidence reference | Status |
| --- | --- | --- | --- | --- | --- | --- |
| IQ-001 | Inspect `pyproject.toml` | Package metadata and dependencies are present. | 2026-05-04 | Metadata, Python requirement, dependencies, dev extras, package discovery, and `claim-audit` script entry point are present. | `pyproject.toml`; `docs/verification.md` | verified |
| IQ-002 | Create a clean local virtual environment under ignored `build/`. | Clean virtual environment can be created. | 2026-05-04 | Clean local venv created under ignored `build/`. | command result; `git status --ignored --short` showing `build/` ignored | verified |
| IQ-003 | Install with `python -m pip install -e ".[dev]"`. | Editable install succeeds with dev dependencies. | 2026-05-04 | Clean venv install and repo-local editable reinstall both completed successfully. | command results; `docs/verification.md` | verified |
| IQ-004 | Run `claim-audit --help`. | CLI command is available and displays help. | 2026-05-04 | Help output displayed `audit` and `demo` subcommands. | command results; `docs/verification.md` | verified |
| IQ-005 | Inspect `.gitignore` and `git status --ignored --short` | Caches, virtualenv, coverage, and build artifacts are ignored. | 2026-05-04 | `.venv/`, `.coverage`, caches, `build/`, egg-info, and bytecode artifacts are ignored; no tracked changes from generated output. | `.gitignore`; `git status --ignored --short` | verified |
| IQ-006 | Inspect README setup instructions | Instructions match the current install path and commands. | 2026-05-04 | README quick start uses Python 3.11+, editable install, `claim-audit demo`, and current `claim-audit audit DRAFT --evidence --out --json-out` syntax. | `README.md` Quick Start | verified |
| IQ-007 | Run `claim-audit audit-bundle --help`. | C-B contract-path CLI command is available and documents `--out-dir`. | 2026-05-11 | Help output displayed `audit-bundle` and its output directory option. | `tests/test_cli.py`; `docs/verification.md` C-B accommodation addendum | verified |

## Acceptance Criteria

IQ passes when all listed install, setup, CLI, ignored-artifact, and README-alignment checks are `verified` or have an explicit accepted deviation in `deviation-log.md`.

## Record

IQ passed on 2026-05-04 against the completed CLI-first version. The C-B accommodation addendum passed on 2026-05-11 for CLI command availability. No IQ-blocking deviations were recorded.
