# Research-Use Adjunct

status: planned
last_updated: 2026-04-30

Purpose: keep research-measurement rules separate from the v1 portfolio shipping plan. Claim Audit Lab may eventually be used as one measurement channel in scaffold-evaluation research, but the core project should first ship as a usable evidence-support audit tool.

## Boundary

The public v1 portfolio asset should answer:

- Can a reviewer run the tool?
- Can they inspect a claim-support report?
- Can they trace claims to supplied evidence and limitations?

The research-use adjunct answers a different question:

- If this tool is used as a measurement instrument in a separate scaffold-evaluation study, what safeguards prevent it from looking tuned to prove the study?

## Research-Use Guardrails

Before Claim Audit Lab is used on scaffold-evaluation outputs:

- Validate the tool on its own fixture set before running it on experiment outputs.
- Include fixtures where scaffolds help, do nothing, and make outputs worse.
- Include false-caution fixtures where a cautious answer should not be rewarded if it hides a well-supported conclusion.
- Freeze the tool version, rule policy, config, and validation-matrix status before evaluating experiment outputs.
- Record later rule or code changes as bug fixes, validation changes, or exploratory post-hoc analysis.
- Compare a sample of tool labels against human reviewer judgments and report disagreement patterns.
- Treat Claim Audit Lab metrics as one measurement channel, not the sole basis for research conclusions.
- Preserve outputs, configs, evidence bundles, and tool version metadata so the audit can be replayed.

Good research positioning:

> Claim Audit Lab is not designed to prove scaffolds work. It is designed to make claim-support failures visible and countable. Scaffold results should be interpreted through convergence among automated audit metrics, human review, usefulness ratings, false-caution checks, and transparent error analysis.

## Research-Use Requirement Matrix

These rows are intentionally outside the v1 shipping matrix.

| id | Requirement | Source | Scope | Method | Evidence | Acceptance criteria | Risk if missing | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAL-REQ-030 | Research-use documentation must state that Claim Audit Lab is one measurement channel, not proof that scaffolds work. | research integrity risk | `README.md`, `docs/research-use.md`, proposal methodology | inspection | research-use integrity review | Public and proposal-facing language separates the tool from the scaffold intervention and preserves human review as an external check. | The tool can look like it was built to prove the experiment. | planned |
| CAL-REQ-031 | Research measurement runs must record tool version, audit config, evidence bundle IDs, and validation-matrix status. | reproducibility need | `auditor.py`, `report.py`, CLI output metadata | test, demonstration | `tests/test_report.py`, example JSON report | JSON or run metadata makes the audit replayable and identifies the exact tool/config used. | Results become hard to reproduce or audit. | planned |
| CAL-REQ-032 | Research-use fixtures must include neutral and adverse cases, not only examples where scaffolds improve outputs. | calibration need | `examples/`, `tests/fixtures/`, validation notes | inspection, test | fixture review note, targeted tests | Validation covers scaffold-helpful, no-change, worse-output, and false-caution cases. | The validation set appears tuned to a preferred conclusion. | planned |
| CAL-REQ-033 | Human-review calibration must be planned before using tool metrics as research outcomes. | external validity need | research notes, validation docs | inspection, analysis | calibration plan, reviewer comparison table | A sample of tool labels can be compared to human judgments, and disagreements are preserved in the writeup. | Automated counts may be overtrusted. | planned |
| CAL-REQ-034 | Rule or scoring changes after seeing experiment outputs must be logged and treated as exploratory unless rerun under a new frozen version. | no post-hoc tuning rule | changelog, verification notes, research notes | inspection | change log entry, run manifest | Measurement changes after outcome review are visible and not mixed with pre-specified results. | The tool can be accused of being retuned to fit the result. | planned |
| CAL-REQ-035 | Paired draft/final audits should support counting removed, downgraded, added, and unchanged claims without hiding false caution. | scaffold proposal metrics | future research harness, `auditor.py`, reports | analysis, test | paired-output fixture tests | A paired fixture can compare pre-audit and final answers and report claim movement without treating all removals as improvements. | The experiment cannot quantify revision effects or may reward timid answers. | planned |

## Activation Rule

Do not let this adjunct block the v1 portfolio release. Activate these rows when Claim Audit Lab is actually being used to measure scaffold-evaluation outputs.
