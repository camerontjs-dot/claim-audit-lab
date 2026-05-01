# Claim Audit Lab

Python workspace for auditing whether draft claims are supported by supplied evidence.

## Status

This live-asset workspace has a package scaffold, demo fixture folders, implementation boundaries, a verified typed model layer, verified draft/evidence loaders, verified conservative claim extraction, verified deterministic evidence matching, a verified Phase 4A runnable vertical slice, verified initial deterministic rule checks and support assessment, a hand-authored AI research target report, a generated Phase 5 slice report, and two fictional draft/evidence fixture families. Full audit orchestration hardening, full report rendering, and the CLI workflow have not been built yet.

Source plan: `../../planning/claim-audit-lab-plan.md`

Control checklist: `../../planning/claim-audit-lab-control-checklist.md`

Validation matrix reference: `docs/validation-matrix-reference.md`

Validation package: `validation/README.md`

Master plan: `docs/master-plan.md`

Phase 6 plan: `docs/phase-6-audit-orchestration-plan.md`

Implementation handoff prompt: `docs/handoff-prompt.md`

## What it will do

Claim Audit Lab loads a draft document and an evidence bundle, extracts candidate claims, maps claims to supplied evidence, applies initial deterministic rule checks, and produces minimal Markdown and JSON slice reports.

The intended support labels are:

- `supported`
- `partially_supported`
- `unsupported`
- `overstated`
- `needs_source`
- `not_audit_ready`

## What it will not do

This project will not verify whether the outside world is true. It will only check whether a draft's claims are supported by the evidence supplied to the tool.

The first version will not require live LLM calls, network access, private application materials, or external fact checking.

## Research use

Claim Audit Lab can eventually be used as one measurement channel in research on scaffolded AI workflows, but that is an adjunct use case rather than the v1 shipping path. Research-use guardrails live in `docs/research-use.md`.

## Validation package

The repo keeps validation as a first-class project surface in `validation/`. After the first CLI-first public version is built, that package will hold the IQ/OQ/PQ-inspired protocols, run records, deviation log, and acceptance evidence. This is a validation-inspired portfolio control, not a regulated compliance claim.

## Local setup

Local verification commands:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
python -m compileall -q src tests
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m coverage run --branch -m pytest
python -m coverage report
```

## Phase 5 demo

After local setup, run the rule-assessed vertical-slice demo:

```bash
python scripts/run_demo.py
```

The default command writes Markdown and JSON outputs under `build/reports/` so routine reviewer runs do not dirty the worktree. To refresh the checked-in slice fixtures intentionally, run:

```bash
python scripts/run_demo.py --update-fixture
```

The Phase 5 report is still a minimal slice. Candidate evidence scores are visible for inspection, deterministic rule checks produce initial support labels and flags, and full report rendering remains planned.

## Next implementation step

Implement the Phase 6 audit orchestration plan in `docs/phase-6-audit-orchestration-plan.md` without turning candidate scores into support labels by themselves.
