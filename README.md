# Claim Audit Lab

Python workspace for auditing whether draft claims are supported by supplied evidence.

## Status

This live-asset workspace has a package scaffold, demo fixture folders, implementation boundaries, a verified typed model layer, verified draft/evidence loaders, and verified conservative claim extraction. Evidence matching and the audit engine have not been built yet.

Source plan: `../../planning/claim-audit-lab-plan.md`

Control checklist: `../../planning/claim-audit-lab-control-checklist.md`

Validation matrix reference: `docs/validation-matrix-reference.md`

Validation package: `validation/README.md`

Master plan: `docs/master-plan.md`

Implementation handoff prompt: `docs/handoff-prompt.md`

## What it will do

Claim Audit Lab will load a draft document and an evidence bundle, extract candidate claims, map claims to supplied evidence, apply rule checks, and produce Markdown and JSON reports.

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

Claim Audit Lab can be used as one measurement channel in research on scaffolded AI workflows, but it should not be treated as proof that a scaffold works. Research-use runs should freeze the tool version and config, validate against independent fixtures, compare a calibration sample against human review, and report disagreements or limitations.

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

## Next implementation step

Build `src/claim_audit_lab/evidence_matching.py`, then add matching tests for numeric overlap, mismatched values, source/excerpt traceability, bounded candidate scores, and reliability-preserving candidate evidence.
