# Claim Audit Lab

Python workspace for auditing whether draft claims are supported by supplied evidence.

## Status

This live-asset workspace has a package scaffold, demo fixture folders, implementation boundaries, a verified typed model layer, verified draft/evidence loaders, verified conservative claim extraction, verified deterministic evidence matching, a verified Phase 4A runnable vertical slice, verified deterministic rule checks and support assessment, verified audit orchestration hardening, a hand-authored AI research target report, generated human-review and JSON reports for two fictional fixture families, a working `claim-audit` CLI, and a completed Phase 10 validation sweep.

Source plan: `../../planning/claim-audit-lab-plan.md`

Control checklist: `../../planning/claim-audit-lab-control-checklist.md`

Validation matrix reference: `docs/validation-matrix-reference.md`

Validation package: `validation/README.md`

Master plan: `docs/master-plan.md`

Phase 6 implementation record: `docs/phase-6-audit-orchestration-plan.md`

Implementation handoff prompt: `docs/handoff-prompt.md`

## What It Does

Claim Audit Lab loads a draft document and an evidence bundle, extracts candidate claims, maps claims to supplied evidence, applies deterministic rule checks, returns a structured `AuditReport`, and produces human-review Markdown plus typed JSON reports through Python functions, the demo script, or the `claim-audit` CLI.

Current support labels:

- `supported`: supplied evidence directly supports the claim.
- `partially_supported`: supplied evidence supports part of the claim, but limits remain.
- `unsupported`: supplied evidence does not support the claim.
- `overstated`: the claim is stronger than the supplied evidence can support.
- `needs_source`: the claim needs a supplied source before it can be assessed.
- `not_audit_ready`: the text is not structured enough for a useful claim assessment.

Current risk labels:

- `low`: no rule issue found for the current supplied evidence.
- `medium`: support is incomplete, source quality is limited, or a source is missing.
- `high`: the claim carries high-risk overstatement, mismatch, or certainty concerns.

## What It Will Not Do

This project will not decide whether a claim matches the outside world. It only checks whether a draft's claims are supported by the evidence supplied to the tool.

The first version will not require live LLM calls, network access, private application materials, or external fact checking.

## Research use

Claim Audit Lab can eventually be used as one measurement channel in research on scaffolded AI workflows, but that is an adjunct use case rather than the v1 shipping path. Research-use guardrails live in `docs/research-use.md`.

## Validation package

The repo keeps validation as a first-class project surface in `validation/`. After public packaging, that package will hold the IQ/OQ/PQ-inspired protocol execution records, deviation log, and acceptance evidence. This is a validation-inspired portfolio control, not a regulated compliance claim.

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

## Quick Start

After local setup, run the built-in CLI demo:

```bash
claim-audit demo --out-dir build/reports/cli-demo
```

To audit the AI research fixture directly:

```bash
claim-audit audit examples/drafts/ai-research-note.md \
  --evidence examples/evidence/ai-research-evidence.yml \
  --out build/reports/ai-research-note.md \
  --json-out build/reports/ai-research-note.json
```

Both commands write local Markdown and JSON outputs and require no network access, API keys, or live LLM calls.

## Demo Script

After local setup, run the rule-assessed report demo:

```bash
python scripts/run_demo.py
```

The default command writes Markdown and JSON outputs under `build/reports/` so routine reviewer runs do not dirty the worktree. To refresh the checked-in slice fixtures intentionally, run:

```bash
python scripts/run_demo.py --update-fixture
```

The report includes metadata, executive summary, limitations, claim register, claim details, evidence links, rule flags, and suggested rewrite guidance. Candidate evidence scores are visible for inspection as ranking signals only, not support labels.

## Next Implementation Step

Begin Phase 11 public packaging from `docs/phase-11-public-packaging-plan.md`: replace this stub with a public-facing README, prepare the social/GitHub-pin assets, keep supplied-evidence boundary language, and leave IQ/OQ/PQ execution for Phase 12.
