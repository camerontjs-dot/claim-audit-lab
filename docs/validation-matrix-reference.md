# Validation Matrix Reference Sheet

Purpose: define the first validation matrix for Claim Audit Lab, using regulated-validation and traceability-matrix patterns while keeping the project boundary honest.

Claim Audit Lab validates its own behavior. It does not validate external truth. A passing row means the tool behaved as expected for a known fixture, rule, report, or CLI path.

## Source Patterns To Borrow

Use these references as design inputs, not as claims that this project is regulated software.

| Source | Useful Pattern | Adaptation for Claim Audit Lab |
| --- | --- | --- |
| [Kaye GxP Dictionary: Validation Matrix](https://www.kayeinstruments.com/en/knowledge-library/gxp-dictionary/v/validation-matrix) | A validation matrix links validation requirements to systems, processes, tests, criteria, documents, and responsibilities. | Keep each project requirement tied to an implementation area, test case, report artifact, and owner/status. |
| [Ofni Systems: Requirements Traceability Matrix](https://www.ofnisystems.com/services/validation/traceability-matrix/) | An RTM prevents requirements from being lost and traces requirements to specific test protocols or test steps. | Every functional promise in the README should have at least one matrix row and at least one test or example report proving current behavior. |
| [NASA Appendix D: Requirements Verification Matrix](https://www.nasa.gov/reference/appendix-d-requirements-verification-matrix/) | Requirements should have unique identifiers, clear sources, and defined verification methods. | Give each project requirement a stable `CAL-REQ-*` ID and record whether it is verified by inspection, analysis, test, or demonstration. |
| [NASA Appendix E: Validation Requirements Matrix](https://www.nasa.gov/reference/appendix-e-creating-the-validation-plan-with-a-validation-requirements-matrix/) | Validation planning should connect requirements to stakeholder needs and validation products such as tests, peer reviews, simulations, and feedback. | Tie rows back to the target user question: can a reviewer see which draft claims are supported, weakly supported, missing sources, or overstated? |
| [GMP SOP sample: Matrices and Bracketing in Process Validation](https://www.gmpsop.com/guidance-samples/Guidance-033-Matrices-and-Bracketing-in-Process-Validation-sample.pdf) | Matrixing and bracketing can justify representative coverage without testing every possible combination. | Use representative fixture families: numeric, causal, comparative, credential, capability, scope, stale-source, malformed-input, and report-quality cases. |
| [Research Validation Matrix example](https://www.researchgate.net/figure/Research-validation-matrix_fig5_337329738) | Research matrices map challenges or objectives to validation methods. | Treat each product promise as a validation objective, then map it to evidence from tests, demo fixtures, and reports. |
| [Content Validation Matrix](http://excolo.com/content-validation-matrix/) | Matrix rows can test whether content serves intended purposes. | Use report-quality rows to check public copy and generated report language for overclaiming. |
| [Q-matrix Validation](https://bookdown.org/mehdirajeb/CDM/q-matrix-validation.html) | Q-matrix validation checks whether item-skill relationships are correctly represented. | Use a claim-type matrix to confirm that fixture claims exercise the intended rule skills. |
| [Deibel Laboratories: Method/Matrix Validation](https://deibellabs.com/services/method-validation/) | Method validation depends on the matrix where the method is applied. | Validate behavior against specific input matrices: Markdown draft plus YAML evidence, malformed YAML, empty evidence, and mixed-reliability sources. |
| [Ground Motion Simulation Validation Matrix](https://ir.canterbury.ac.nz/bitstreams/3004001b-742e-413a-89c4-54e2b0dcb908/download) | Technical validation matrices can track components, uncertainties, and model assumptions. | Include limitations and assumption checks when evidence matching is deterministic and approximate. |
| [Autonomy Validation Matrix](https://chrishood.com/autonomy-validation-matrix-how-to-define-autonomous-systems/) | A matrix can distinguish what a system actually does from what it appears to do. | Keep capability claims narrow: the tool audits evidence support; it does not fact-check reality. |
| [NRC TRAC-M Validation Test Matrix](https://www.nrc.gov/reading-rm/doc-collections/nuregs/contract/cr6720/index) | Safety-oriented software validation uses explicit test matrices for qualification. | Maintain a test matrix that makes coverage and gaps visible before public packaging. |

## Matrix Method

Each validation row should answer:

- What requirement or promise are we validating?
- Where did the requirement come from?
- Which module or artifact owns the behavior?
- What type of validation is appropriate?
- What fixture, test, or report proves it?
- What acceptance criterion must be true?
- What risk remains if the row fails?

Suggested verification methods:

- `inspection`: read code, README, fixtures, or generated report for required content.
- `analysis`: inspect structured output, schema, counts, labels, or trace links.
- `test`: run automated pytest coverage.
- `demonstration`: run the CLI against example data and inspect generated output.

## Required Columns

| Column | Purpose |
| --- | --- |
| `id` | Stable requirement ID. Use `CAL-REQ-###`. |
| `requirement` | One behavioral or documentation promise. |
| `source` | README, plan, checklist, user need, or public positioning risk. |
| `scope` | Module, fixture, report, CLI path, or documentation artifact. |
| `method` | `inspection`, `analysis`, `test`, `demonstration`, or a combination. |
| `evidence` | Test name, fixture path, generated report path, command, or review note. |
| `acceptance_criteria` | Observable pass condition. |
| `risk_if_missing` | Why this matters. |
| `status` | `planned`, `implemented`, `verified`, `blocked`, or `deferred`. |

## Starter Validation Matrix

| id | Requirement | Source | Scope | Method | Evidence | Acceptance criteria | Risk if missing | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAL-REQ-001 | The tool must state that it audits support from supplied evidence, not external truth. | README, project boundary | README, generated reports | inspection, test | `README.md`; report-quality tests | Public copy and reports avoid `true`, `false`, `fact checked`, `verified`, and `proven` as capability claims. | Portfolio asset overclaims and undermines trust. | planned |
| CAL-REQ-002 | Evidence bundles must be loaded from YAML or JSON into typed models. | plan inputs | `loader.py`, `models.py` | test | `tests/test_loader.py`, `tests/test_models.py` | Valid YAML and JSON fixtures load; malformed YAML and missing required fields fail with path-aware loader errors. | Audit results may be built on malformed evidence. | verified |
| CAL-REQ-003 | Drafts must be loaded from Markdown or plain text. | plan inputs | `loader.py` | test | `tests/test_loader.py` | Markdown and text fixtures produce a `DraftDocument` with stable ID/content and file path metadata. | CLI cannot run against expected user inputs. | verified |
| CAL-REQ-004 | Claim extraction must be conservative and avoid inventing claims. | plan workflow | `claim_extraction.py` | test, analysis | `tests/test_claim_extraction.py` | Vague or non-claim sentences are ignored; explicit numeric, causal, comparative, credential, prediction, capability, scope, and interpretive claims are extracted with stable IDs and paragraph/sentence locations. | Tool fabricates audit targets and creates noise. | verified |
| CAL-REQ-005 | Numeric claims must be matched against supplied evidence when numbers agree. | validation cases | `evidence_matching.py` | test | `tests/test_evidence_matching.py` | The `52` workflow-output claim links to `source-001` / `excerpt-002`, and the `18` to `11` reduction claim links to `source-001` / `excerpt-001` with high bounded scores. | Core traceability promise is weak. | verified |
| CAL-REQ-006 | Numeric claims with unsupported or differing values must be flagged. | validation cases | `rules.py`, `auditor.py` | test | `tests/test_rules.py`, `tests/test_auditor.py` | Mismatched numeric claim receives `unsupported`, `partially_supported`, or a rule flag explaining the difference. | The tool misses high-risk factual drift. | planned |
| CAL-REQ-007 | Causal claims supported only by correlational evidence must not be labeled fully supported. | rule policy | `rules.py`, `auditor.py` | test | `tests/test_rules.py` | Causal wording plus weak/correlational evidence yields `partially_supported` or `overstated`. | Tool lets causal overclaims pass. | planned |
| CAL-REQ-008 | Comparative claims require comparison evidence. | rule policy | `rules.py` | test | `tests/test_rules.py` | Comparative wording without comparison source gets a rule flag. | Draft can claim superiority without support. | planned |
| CAL-REQ-009 | Credential and public-link claims require source support. | rule policy | `rules.py`, `models.py` | test | `tests/test_rules.py` | Credential claims without source and public-link claims without URL are flagged. | Public portfolio/application copy can imply unsupported credentials. | planned |
| CAL-REQ-010 | Overconfident wording must be flagged when support is partial or weak. | rule policy | `rules.py` | test | `tests/test_rules.py` | Words such as `always`, `never`, `eliminates`, or `guarantees` trigger a flag when evidence does not justify certainty. | Report fails to catch the exact risk the asset is meant to demonstrate. | planned |
| CAL-REQ-011 | Source reliability and freshness must affect warnings or support assessment. | rule policy | `rules.py`, `models.py` | test | `tests/test_rules.py` | Low-reliability-only support and stale sources produce visible warnings or lower support. | Report hides evidence quality limitations. | planned |
| CAL-REQ-012 | Empty evidence bundles must produce a useful audit result, not a crash. | validation cases | `auditor.py`, `report.py` | test | `tests/test_auditor.py`, `tests/test_report.py` | Claims receive `needs_source` or `unsupported`; summary explains no evidence was supplied. | A common user error breaks the tool. | planned |
| CAL-REQ-013 | Markdown reports must contain claim register, evidence links, support labels, rule flags, summary metrics, limitations, and rewrite guidance where applicable. | outputs, README structure | `report.py` | test, demonstration | `tests/test_report.py`; `examples/reports/*.md` | Generated report has required sections and no `None`, `nan`, or empty placeholder sections. | Human-facing output is not audit-ready. | planned |
| CAL-REQ-014 | JSON reports must follow the expected schema and be suitable for tests. | outputs | `report.py`, `models.py` | test | `tests/test_report.py` | JSON output round-trips or validates against the `AuditReport` model. | Automated validation and inspection become brittle. | planned |
| CAL-REQ-015 | CLI malformed-input failures must be clear and nonzero. | CLI sketch | `cli.py`, `loader.py` | test, demonstration | `tests/test_cli.py` | Malformed evidence file exits nonzero and explains the file/validation issue. | Users cannot distinguish bad input from audit findings. | planned |
| CAL-REQ-016 | CLI high-risk findings must still exit successfully when the audit completes. | validation cases | `cli.py`, `auditor.py` | test, demonstration | `tests/test_cli.py` | High-risk claims appear in output, but process exit code is success. | CI or users treat valid audit findings as tool failure. | planned |
| CAL-REQ-017 | Example data must be fictional or sanitized. | project boundary | `examples/` | inspection | fixture review note | No private application materials, real sensitive data, tokens, or local-only paths appear in examples. | Public asset leaks private context or looks careless. | planned |
| CAL-REQ-018 | README must match implemented behavior. | packaging gate | `README.md`, tests, reports | inspection | publish checklist | README quick start, labels, limitations, and validation section match current commands and outputs. | Portfolio copy promises behavior the package does not have. | planned |
| CAL-REQ-019 | Typed models must enforce strict schema contracts. | handoff prompt, model contract | `models.py` | test | `tests/test_models.py` | Unknown fields, blank required IDs/text, invalid constrained labels, out-of-range candidate scores, and impossible config values are rejected; empty evidence bundles remain valid. | Downstream audit logic receives malformed or ambiguous data. | verified |
| CAL-REQ-020 | Evidence source IDs and excerpt IDs must be unique within a bundle. | handoff prompt, traceability need | `models.py` | test | `tests/test_models.py` | Duplicate source IDs fail; duplicate excerpt IDs fail across the whole evidence bundle. | Claim-to-evidence links become ambiguous or misleading. | verified |
| CAL-REQ-021 | Date and deadline claims without matching evidence must be flagged. | rule policy | `rules.py`, `auditor.py` | test | `tests/test_rules.py`, `tests/test_auditor.py` | Date or deadline claims with no supporting source receive a rule flag or non-supported label. | Time-sensitive claims can pass without traceable support. | planned |
| CAL-REQ-022 | Future predictions stated as certainty must be flagged or caveated. | rule policy | `rules.py` | test | `tests/test_rules.py` | Prediction wording such as `will always` or certainty about future outcomes produces an overstatement or uncertainty flag. | Speculative claims sound more certain than the evidence allows. | planned |
| CAL-REQ-023 | Duplicate or near-duplicate claims must not inflate extracted claim counts. | validation cases | `claim_extraction.py` | test, analysis | `tests/test_claim_extraction.py` | Repeated exact and near-duplicate sentences are deduplicated during extraction, with the first canonical claim retained until the model supports grouping metadata. | Reports overstate issue counts or hide repeated unsupported claims. | verified |
| CAL-REQ-024 | Multiple candidate evidence sources must preserve reliability and support differences. | validation cases | `evidence_matching.py`, `rules.py`, `report.py` | test, analysis | `tests/test_evidence_matching.py`, `tests/test_rules.py`, `tests/test_report.py` | Candidate evidence links retain source IDs, excerpt IDs, scores, reliability labels, and source dates; warnings when support quality differs remain for the rule/report layers. | The report hides uncertainty or treats weak and strong sources as equivalent. | planned |
| CAL-REQ-025 | The audit pipeline must return a structured report with trace links and limitations. | public function contract | `auditor.py`, `models.py` | test, analysis | `tests/test_auditor.py` | `audit_document(...)` returns an `AuditReport` whose assessments link claims, candidate evidence, rule flags, summary metrics, and limitations. | The system cannot be inspected or validated beyond prose output. | planned |
| CAL-REQ-026 | The project must install locally and expose the planned CLI command. | MVP definition, tooling baseline | `pyproject.toml`, `cli.py` | demonstration, test | `pip install -e ".[dev]"`; `claim-audit --help`; `tests/test_cli.py` | Editable install succeeds and the `claim-audit` command is available without manual path hacks. | A public reviewer cannot run the portfolio asset cleanly. | planned |
| CAL-REQ-027 | Normal tests and v1 CLI behavior must not require live LLM calls, API keys, or network access. | project boundary, control checklist | `src/`, `tests/`, `README.md` | inspection, test | dependency review; test run without secrets | The normal test suite and example CLI run complete with checked-in fixtures and no required network credentials. | The project becomes harder to reproduce and risks hidden external dependencies. | planned |
| CAL-REQ-028 | Public v1 examples must include at least two complete fictional draft/evidence/report families. | MVP definition, demo data plan | `examples/`, `report.py`, `README.md` | inspection, demonstration | `examples/drafts/*`; `examples/evidence/*`; `examples/reports/*` | At least two fictional or sanitized example runs produce Markdown and JSON report artifacts before public packaging. | The demo may be overfit to one scenario and fail to show general behavior. | planned |
| CAL-REQ-029 | Core support labels and risk labels must be constrained, documented, and exercised. | outputs, README, handoff prompt | `models.py`, `rules.py`, `report.py`, `README.md` | test, inspection | `tests/test_models.py`, rule/report tests, README label section | Every support label and risk label is defined in typed models, explained in public docs, and covered by at least one fixture or test before public release. | Label meanings drift or public docs describe states the tool cannot produce. | planned |
| CAL-REQ-036 | The finished CLI-first tool should have a visible first-class validation package using validation-inspired IQ/OQ/PQ structure without claiming regulated compliance. | pharma equipment validation analogy, repo visibility requirement | `validation/README.md`, `validation/qualification-plan.md`, `validation/iq-installation.md`, `validation/oq-operational.md`, `validation/pq-performance.md`, `validation/deviation-log.md`, `README.md`, `docs/verification.md`, example reports | inspection, demonstration | qualification pass notes, README link, validation matrix row coverage | The repo exposes the validation package at top level, records IQ/OQ/PQ-style checks after the tool is built, documents deviations and revalidation triggers, and avoids GxP/GMP/CSV/FDA compliance claims. | The validation approach stays hidden in chat or is overstated as compliance. | planned |
| CAL-REQ-037 | A hand-authored target report must define the desired AI research memo output before final report rendering is coded. | UX/design control | `docs/target-report-prompt.md`, `examples/reports/ai-research-note.target.md` | inspection | `examples/reports/ai-research-note.target.md`; `docs/verification.md` target report review note | Target report is clearly marked hand-authored, uses supplied-evidence language, includes required report sections, and surfaces design questions before renderer implementation. | Report design gets locked in by code before the desired reviewer experience is understood. | verified |
| CAL-REQ-038 | A runnable vertical slice must produce a minimal Markdown report before full rule and CLI hardening. | portfolio reviewability | `auditor.py`, `report.py`, demo entry point, checked-in fixtures | demonstration, test | `tests/test_vertical_slice.py`; `scripts/run_demo.py --update-fixture`; `examples/reports/ai-research-note.slice.md`; `examples/reports/ai-research-note.slice.json` | A reviewer can run one documented local command against checked-in fixtures and see extraction, naive matching, `audit_document()`, minimal Markdown output, and typed JSON output while support labels remain explicitly provisional. | The repo remains internally rigorous but not inspectable as a working artifact. | verified |
| CAL-REQ-039 | Claim IDs, rule-flag IDs, and report anchors must be deterministic across reruns for the same inputs. | traceability need | `claim_extraction.py`, `rules.py`, `report.py` | test, analysis | stable-ID tests; generated report comparison | Claim IDs derive from stable input content; rule-flag IDs derive from rule code plus claim-specific trigger context; generated anchors remain stable across reruns. | Reports cannot be compared, linked, or used as reliable validation evidence. | planned |
| CAL-REQ-040 | Public packaging must include social card or GitHub-pin assets that match the repo positioning. | portfolio release bar | README, assets folder, public packaging checklist | inspection | release checklist; asset review | Social/GitHub-pin assets exist, avoid overclaiming, and align with the README and report experience. | Public presentation lags behind the project quality bar set by prior portfolio assets. | planned |

## Fixture Coverage Matrix

Use this as a compact design check before writing tests.

| Fixture family | Claim types covered | Expected labels or flags | Minimum evidence artifact |
| --- | --- | --- | --- |
| AI research memo | numeric, causal, scope, interpretive | `supported`, `partially_supported`, `overstated` | `examples/evidence/ai-research-evidence.yml` |
| Application answer | credential, capability, public-link, comparative | `supported`, `needs_source`, `unsupported` | sanitized or fictional evidence bundle |
| Product README paragraph | capability, scope, comparative, prediction | `partially_supported`, `overstated`, freshness warning | `examples/drafts/product-readme-note.md`, `examples/evidence/product-readme-evidence.yml` |
| Malformed evidence | none | loader validation error | malformed YAML/JSON fixture |
| Empty evidence bundle | any extracted claims | `needs_source`, bundle warning | empty-but-valid evidence fixture |
| Mixed reliability sources | numeric, causal, interpretive | reliability warning, partial support | high/medium/low reliability excerpts |
| Date or deadline note | numeric, prediction, scope | date/deadline missing-source flag, stale-source warning | dated source plus missing-date claim |
| Duplicate claim draft | numeric, capability, interpretive | dedupe or grouping behavior, honest summary counts | repeated or near-duplicate draft claims |

## Acceptance Rules

The validation matrix is strong enough for the first public version when:

- Every README capability claim maps to at least one `CAL-REQ-*` row.
- Every core label has at least one fixture that produces it.
- Every rule check in the plan has at least one automated test.
- Every example report is generated from checked-in fictional data.
- Report-quality tests prevent placeholders and overclaiming language.
- Known limitations are visible in the README and generated reports.
- Every model invariant listed in the first implementation prompt has a direct test.
- Public v1 has at least two complete fictional example runs with checked-in Markdown and JSON outputs.
- Normal tests and example runs require no network access, API key, or live LLM call.
- Research-use requirements are tracked separately in `docs/research-use.md` and do not block v1 portfolio release.

## Maintenance Rules

- Add a new matrix row before adding a new public capability claim.
- Update `status` only from current evidence, not intention.
- Prefer one requirement per row. Split compound rows when acceptance criteria become blurry.
- Keep source references stable enough that future sessions can trace why a row exists.
- Treat deleted or renamed tests as validation drift until the matrix is updated.
- Before publishing, scan for claims that imply truth verification rather than supplied-evidence support.
- Keep `validation/README.md` linked from the README and master plan so the post-build validation approach stays visible in the repo.
- Keep research-measurement rows `CAL-REQ-030` through `CAL-REQ-035` in `docs/research-use.md` until the project is actively used as a measurement instrument.
