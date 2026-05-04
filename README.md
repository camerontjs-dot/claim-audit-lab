# Claim Audit Lab

Claim Audit Lab is a deterministic Python CLI for auditing whether draft claims are supported by supplied evidence.

It is built for reviewers who need to see where a draft is supported, where it is too strong, where a source is missing, and what limitations should stay visible before a claim is reused.

## What It Does

Claim Audit Lab:

- loads a draft document from Markdown or plain text
- loads a supplied evidence bundle from YAML or JSON
- extracts candidate claims conservatively
- ranks supplied evidence candidates for each claim
- applies deterministic rule checks for support, overstatement, missing sources, and evidence limitations
- writes a human-review Markdown report
- optionally writes typed JSON report data

The current CLI is intentionally local and reproducible. Normal tests, examples, and demo runs require no network access, API keys, provider SDKs, or live LLM calls.

## What It Does Not Do

Claim Audit Lab does not decide whether a statement matches the outside world. It checks whether the claim is supported by the evidence bundle you supply.

It also does not:

- search the web or discover sources
- replace human source review
- score research quality as a single certainty number
- use support scores as final labels
- certify that a workflow, scaffold, or intervention works
- act as a regulated quality system

Candidate evidence scores are ranking signals only. Final support labels come from deterministic rule assessment.

## Quick Start

Use Python 3.11 or newer.

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the built-in demo:

```bash
claim-audit demo --out-dir build/reports/cli-demo
```

Audit the AI research fixture directly:

```bash
claim-audit audit examples/drafts/ai-research-note.md \
  --evidence examples/evidence/ai-research-evidence.yml \
  --out build/reports/ai-research-note.md \
  --json-out build/reports/ai-research-note.json
```

Both commands write local report files under `build/reports/` and leave checked-in example reports untouched.

## Example Reports

The repo includes two fictional draft/evidence/report families:

| Fixture | Draft | Evidence | Markdown report | JSON report |
| --- | --- | --- | --- | --- |
| AI research memo | `examples/drafts/ai-research-note.md` | `examples/evidence/ai-research-evidence.yml` | `examples/reports/ai-research-note.slice.md` | `examples/reports/ai-research-note.slice.json` |
| Product README paragraph | `examples/drafts/product-readme-note.md` | `examples/evidence/product-readme-evidence.yml` | `examples/reports/product-readme-note.slice.md` | `examples/reports/product-readme-note.slice.json` |

Current generated report summaries:

- AI research memo: 4 claims, 1 supported, 1 partially supported, 2 overstated, and 2 high-risk findings.
- Product README paragraph: 4 claims, 2 supported, 2 overstated, and 2 high-risk findings.

See `examples/reports/README.md` for the report-artifact map.

## Labels

Support labels:

- `supported`: supplied evidence directly supports the claim.
- `partially_supported`: supplied evidence supports part of the claim, but limits remain.
- `unsupported`: supplied evidence does not support the claim.
- `overstated`: the claim is stronger than the supplied evidence can support.
- `needs_source`: the claim needs a supplied source before it can be assessed.
- `not_audit_ready`: the text is not structured enough for a useful claim assessment.

Risk labels:

- `low`: no rule issue found for the current supplied evidence.
- `medium`: support is incomplete, source quality is limited, or a source is missing.
- `high`: the claim carries high-risk overstatement, mismatch, or certainty concerns.

## Report Contents

Markdown reports include:

- metadata and audit boundary
- executive summary
- limitations
- claim register
- claim-by-claim details
- stable report, claim, rule-flag, and evidence-link anchors
- candidate evidence links with reliability/date metadata
- deterministic rule flags with visible rule-flag IDs
- support-quality notes where candidate evidence caveats are useful
- explanation and rewrite guidance where useful

JSON reports follow the typed `AuditReport` model and are intended for regression checks, validation evidence, and downstream inspection.

## How The Audit Works

The pipeline is deliberately simple and inspectable:

1. `loader.py` reads draft and evidence files into strict Pydantic models.
2. `claim_extraction.py` extracts explicit claim candidates and stable claim IDs.
3. `evidence_matching.py` ranks supplied evidence excerpts for each claim.
4. `rules.py` assigns deterministic support labels, risk labels, and rule flags.
5. `auditor.py` assembles the typed audit report.
6. `report.py` renders Markdown and JSON outputs.
7. `cli.py` exposes `claim-audit audit` and `claim-audit demo`.

The implementation favors traceability over cleverness. Every public behavior should be backed by tests, checked-in examples, or an explicit validation-matrix status.

## Validation Approach

Claim Audit Lab keeps validation visible in the repo:

- `docs/validation-matrix-reference.md` maps public promises to `CAL-REQ-*` rows.
- `docs/verification.md` records verification commands and outcomes.
- `validation/README.md` describes the IQ/OQ/PQ-inspired validation package.
- `validation/deviation-log.md` is reserved for visible deviations and accepted limitations.

This is validation-inspired portfolio control. It is not a regulated compliance claim.

## Public Packaging

Phase 11 added:

- MIT license
- package metadata for public review
- `assets/social-card.svg`
- `assets/github-pin.md`
- public README positioning aligned to supplied-evidence support

Public repository and homepage URLs are intentionally omitted from package metadata until a real public remote exists.

## Development Checks

Run the normal verification chain from the repo root:

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
. .venv/bin/activate && claim-audit demo --out-dir build/reports/phase-13-smoke
```

## Repository Map

| Path | Purpose |
| --- | --- |
| `src/claim_audit_lab/` | Python package implementation |
| `tests/` | Unit, integration, CLI, report, and language-gate tests |
| `examples/drafts/` | Fictional draft inputs |
| `examples/evidence/` | Fictional supplied evidence bundles |
| `examples/reports/` | Checked-in generated and target report artifacts |
| `docs/` | Master plan, validation matrix, verification notes, phase records, research-use adjunct |
| `validation/` | Validation-inspired IQ/OQ/PQ records and deviation log |
| `assets/` | Public social and repo-pin assets |
| `scripts/run_demo.py` | Reviewer-friendly report generation helper |

## Current Status

Implemented and verified through Phase 13 traceability/report polish:

- typed model layer
- draft and evidence loaders
- conservative claim extraction
- deterministic evidence matching
- deterministic rule checks and support assessment
- audit orchestration
- Markdown and JSON report rendering
- `claim-audit` CLI
- two complete fictional example families
- Phase 10 validation sweep
- Phase 11 public README, license, metadata, and social/GitHub-pin assets
- Phase 12 IQ/OQ/PQ-inspired validation records
- Phase 13 stable Markdown anchors, visible rule-flag IDs, and support-quality notes

Next step: treat the CLI-first artifact as a release candidate unless a separate Phase 14 UI plan is explicitly promoted.

## License

MIT. See `LICENSE`.
