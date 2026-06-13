# Verification Summary

last_updated: 2026-06-13
release: 0.2.0
engineering_status: passed
research_qualification: pending

## Boundary

This record verifies Claim Audit Lab as a deterministic supplied-evidence package. It
does not show outside-world truth checking, calibrated accuracy, regulated validation,
or production fitness.

Support scores are deterministic supplied-evidence signals, not truth probabilities.
Blind human calibration remains `0/98`.

## Required Chain

Commands run from the repository root:

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report --include='src/*' --show-missing --fail-under=95
.venv/bin/python -m build --wheel
.venv/bin/python scripts/verify_install.py
```

## Results

- `pytest`: 213 passed.
- Ruff lint: passed.
- Ruff format check: passed.
- Strict mypy: passed.
- Compileall: passed.
- Source branch coverage: 96%, above the 95% gate.
- Clean-wheel verifier: passed for `claim-audit --help`, `demo`, and `audit-bundle`.
- Runtime contract schema and demo fixtures were present in the installed wheel.
- Missing packaged resources produced typed failures in tests.
- Checked-in example Markdown and JSON reports regenerated twice with byte identity.

## Frozen Policy Checks

Automated tests cover:

- exact `cal-rules-v1.2.0` policy acceptance and config-drift rejection
- classifier priority and native/C-B unclassified behavior
- candidate admission at `0.40`
- partial support at `0.55`
- sourced support at `0.80`
- false-caution review at `0.85`
- claim-level evidence scoping
- separate counterevidence and its `0.3` penalty
- linked counterevidence preventing `supported`
- direct-evidence strong-wording suppression and conflicting-counterevidence restoration
- `overstated` and `needs_source` policy switches
- paired reproducibility options and byte-identical C-B output
- public `audit_claims(...)` orchestration

## Apparatus Round Trip

The established synthetic workflow passed on 2026-06-13:

```text
Harness fixture
  -> Evidence Bundler intake, retrieval, review, refinement, and finalize
  -> Claim Audit Lab audit-bundle
  -> resealed audited bundle plus Markdown report
```

The run audited 3 claims, skipped 0 retrieval seeds, and wrote both the audited C-B copy
and the report. The Evidence Bundler source worktree had pre-existing local changes;
the verification run did not modify or revert them.

This proves the engineering handoff. It does not qualify retrieval quality or research
measurement accuracy.

## Sealed Pilot Replay

The preserved PILOT-001 v2 set was replayed without overwriting its v0.1 outputs:

- bundles: 15
- claims: 98
- run ID: `cal-v0.2-pilot-001-v2-replay`
- timestamp: `2026-06-13T12:00:00Z`
- second replay: byte-identical
- changed verdicts: 68, each recorded in the claim-level review artifact

Overall comparison:

| version | supported | partially supported | needs source | overstated | unsupported | not checkable |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v0.1 | 2 | 30 | 2 | 1 | 63 | 0 |
| v0.2 | 0 | 12 | 2 | 2 | 26 | 56 |

The large `not_checkable` count is expected from the v0.2 boundary: C-B claims that the
sole classifier cannot assign to an auditable semantic type are preserved instead of
being forced into a support verdict.

Replay artifacts live in the MainFrame project output folder, outside this public
package history:

```text
30_projects/claim-audit-lab/outputs/v0.2-pilot-replay/
```

## Qualification Gate

Public v0.2 may ship on the engineering evidence above. Research or real-work
qualification remains blocked until blind calibration reaches:

- coarse-label agreement at least 80%
- Cohen's kappa at least 0.60
- adverse-claim recall at least 85%
- per-condition adverse-rate error within 10 percentage points

If those bars are missed, human verdicts remain primary and Claim Audit Lab stays an
exploratory measurement channel.
