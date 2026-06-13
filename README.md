# Claim Audit Lab

Claim Audit Lab is a deterministic Python package and CLI for auditing whether draft
claims are supported by supplied evidence.

It is designed for reviewers who need to see which claims are supported, which are too
strong, which need sources, and which cannot be usefully assessed. It does not search
for evidence or decide whether a statement matches the outside world.

## What v0.2 Does

- loads Markdown or plain-text drafts and YAML or JSON evidence bundles
- extracts conservative, typed claim candidates
- audits supplied claim lists through the public `audit_claims(...)` API
- ranks evidence and calculates deterministic supplied-evidence support signals
- flags numeric mismatch, causal overreach, unsupported comparisons, strong wording,
  missing sources, stale evidence, and other visible limitations
- writes typed JSON and human-review Markdown reports
- consumes locked C-B evidence bundles under the frozen `cal-rules-v1.2.0` policy
- keeps each C-B claim bound to its own evidence and counterevidence passages
- writes a resealed audited bundle copy without mutating the sealed input
- produces byte-identical C-B outputs when run ID and timestamp are pinned

Normal tests, examples, and demo runs are local. They require no network access, API
keys, provider SDKs, or live model calls.

## Boundary

Claim Audit Lab audits support from the evidence you supply. Match scores and support
signals are deterministic measures, not truth probabilities.

It does not:

- discover or independently verify sources
- replace human source review
- certify research findings, workflows, or interventions
- act as a regulated quality system
- claim calibrated accuracy on real work

The public v0.2 engineering gate is complete. Research qualification is not: blind human
calibration remains `0/98`. Human verdicts remain primary until the documented
agreement, kappa, recall, and condition-error gates are met.

## Quick Start

Use Python 3.11 or newer.

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the packaged demo:

```bash
claim-audit demo --out-dir build/reports/cli-demo
```

Audit a native draft and evidence bundle:

```bash
claim-audit audit examples/drafts/ai-research-note.md \
  --evidence examples/evidence/ai-research-evidence.yml \
  --out build/reports/ai-research-note.md \
  --json-out build/reports/ai-research-note.json
```

Audit a locked C-B bundle:

```bash
claim-audit audit-bundle tests/fixtures/cb/evidence-bundle-minimal \
  --out-dir build/reports/cb-demo
```

`audit-bundle` writes both a human-readable report and an audited bundle copy. For
reproducible output, provide both metadata options:

```bash
claim-audit audit-bundle tests/fixtures/cb/evidence-bundle-minimal \
  --out-dir build/reports/cb-reproducible \
  --audit-run-id cal-example-run \
  --audited-at 2026-06-13T12:00:00Z
```

Supplying only one reproducibility option is an error.

## Public Python API

The supported orchestration entry points are:

```python
from claim_audit_lab import audit_claims, audit_document, classify_claim_text
```

- `classify_claim_text(text)` applies the sole governed classifier.
- `audit_claims(claims, evidence_bundle, config=None)` audits an existing claim list.
- `audit_document(draft, evidence_bundle, config=None)` extracts and audits native draft
  claims, then returns an `AuditReport`.

`ClaimType` includes `unclassified`. Native extraction skips unclassified text; C-B
inputs preserve it and return `not_checkable`.

## Audit Semantics

The C-B path accepts only the exact frozen `cal-rules-v1.2.0` policy. Changed policy
IDs, thresholds, weights, or switches fail closed.

The deterministic support signal is:

```text
max_support - (0.3 * max_counterevidence)
```

The result is clamped to `[0, 1]`. Frozen boundaries are:

| Boundary | Value |
| --- | ---: |
| Candidate admission | `0.40` |
| Partial support | `0.55` |
| Sourced support | `0.80` |
| False-caution review | `0.85` |

Counterevidence is never eligible as support. Linked counterevidence emits
`counterevidence_present` and prevents a clean `supported` verdict. Absolute wording is
suppressed only when direct evidence contains the same trigger and no linked
counterevidence conflicts.

## Labels

Support labels:

- `supported`: direct supplied evidence clears the sourced-support boundary.
- `partially_supported`: some supplied-evidence support exists, but limits remain.
- `unsupported`: the admitted evidence signal does not clear the partial boundary.
- `overstated`: wording is stronger than the supplied evidence permits.
- `needs_source`: the claim needs supplied evidence before useful assessment.
- `not_checkable`: the claim is preserved but the classifier cannot assign an auditable
  semantic type.

Risk labels are `low`, `medium`, and `high`. Assessments also expose
`rewrite_guidance: list[str]`.

## Example Reports

The repo contains two fictional draft/evidence/report families:

| Fixture | Current v0.2 result |
| --- | --- |
| AI research memo | 4 claims: 1 supported, 1 partially supported, 2 overstated |
| Product README paragraph | 4 claims: 2 unsupported, 2 overstated |

See `examples/reports/README.md` for the artifact map.

## Validation

The repository keeps validation-inspired records visible:

- `docs/validation-matrix-reference.md` maps public promises to `CAL-REQ-*` rows.
- `docs/verification.md` records the v0.2 verification chain and results.
- `validation/` contains IQ/OQ/PQ-style records and the deviation log.

The engineering gate covers 213 tests, Ruff lint and formatting, strict mypy,
compileall, 96% source branch coverage, clean-wheel execution, deterministic examples,
and the Harness to Evidence Bundler to Claim Audit Lab round trip.

The sealed 98-claim pilot was replayed with pinned metadata. A second replay was
byte-identical, and every changed verdict is recorded in the MainFrame project outputs.
That replay is engineering evidence only. It is not human calibration.

## Development Checks

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report --include='src/*' --fail-under=95
.venv/bin/python -m build --wheel
.venv/bin/python scripts/verify_install.py
```

## Repository Map

| Path | Purpose |
| --- | --- |
| `src/claim_audit_lab/` | Package implementation and packaged runtime resources |
| `tests/` | Unit, boundary, integration, CLI, report, and contract tests |
| `examples/` | Fictional native inputs and generated reports |
| `schema/` | Repository copies of the locked C-B contract resources |
| `docs/` | Validation matrix and release verification |
| `validation/` | Qualification-style records and deviations |
| `scripts/verify_install.py` | Clean-wheel verifier |
| `CHANGELOG.md` | Release history and known limits |

## License

MIT. See `LICENSE`.
