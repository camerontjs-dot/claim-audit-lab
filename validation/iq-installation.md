# IQ: Installation Qualification

status: planned
last_updated: 2026-04-30

Purpose: verify that Claim Audit Lab can be installed and invoked in a clean local environment without hidden setup assumptions.

## Scope

This protocol covers:

- Python version compatibility
- editable local install
- dev dependency installation
- CLI availability
- absence of required network, API key, or private data for normal checks
- ignored build artifacts and local caches

## Prerequisites

- The first CLI-first version exists.
- `pyproject.toml` contains the expected package metadata and dependencies.
- Public examples use fictional or sanitized data.

## Protocol

| Step | Command or inspection | Expected result | Status | Evidence |
| --- | --- | --- | --- | --- |
| IQ-001 | Inspect `pyproject.toml` | Package metadata and dependencies are present. | planned | TBD |
| IQ-002 | `python3.11 -m venv .venv` | Virtual environment can be created. | planned | TBD |
| IQ-003 | `.venv/bin/python -m pip install -e ".[dev]"` | Editable install succeeds. | planned | TBD |
| IQ-004 | `.venv/bin/claim-audit --help` | CLI command is available and displays help. | planned | TBD |
| IQ-005 | Inspect `.gitignore` and `git status --ignored --short` | Caches, virtualenv, coverage, and build artifacts are ignored. | planned | TBD |
| IQ-006 | Inspect README setup instructions | Instructions match the current install path and commands. | planned | TBD |

## Acceptance Criteria

IQ passes when all protocol steps are `verified` or have an explicit accepted deviation in `deviation-log.md`.

## Record

Do not mark this protocol `verified` until it has been run against the first CLI-first version.
