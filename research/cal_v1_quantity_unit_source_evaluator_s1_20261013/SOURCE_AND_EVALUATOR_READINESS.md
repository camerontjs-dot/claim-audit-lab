# CAL #212: RC3 source and receipt readiness, separate successor S1

**Evidence class:** OWNER / CUSTODIAN PREPARATION ONLY. **Qualification:** NOT_RUN. **Candidate:** NOT_BUILT. **Status:** BLOCKED_SOURCE_REPRESENTATION_AND_ISOLATED_EXECUTION.

This additive successor is stacked on frozen #213 at `49d31eb428233e0233b931fe303dc58d5857836a`. Do not amend #213, its source freeze, its evaluator/self-test, or #209/#211. It does not replace the #213 scientific cohort and is not a permission to score a modified cohort.

## Source-fitness decision

Exact #213 `SOURCE_FREEZE.json` blob `d39a22e6fb9c4249fd47454c94794efa8c1bc1de` records eight one-fetch 200 responses, with source/body Git blobs independently visible in the #213 tree. HTTP success establishes transport, not selected representation or suitability.

* `QURC3-H01` requested BIS Annual Economic Report 2026 PDF at `https://www.bis.org/publ/arpdf/ar2026e.pdf`, but the one frozen result ended at `https://www.bis.org/publications/aer-2026`, `text/html; charset=utf-8`, 139,978 bytes, SHA-256 `c025d43c921f9402050b20fc052ab434177d552e33883223ce8c2081b23bdcdd`, Git blob `5c8af24c23426de5221db56c4c6e35cb46eff757`.
* Direct read of that **frozen Git blob**, not a second publisher fetch: it is an HTML landing page with `<!DOCTYPE html>`, title `BIS Annual Economic Report 2026`, and a link to a distinct PDF at `https://www.bis.org/publications/aer-2026_0.pdf`. The captured HTML has no `percent` or `percentage points` textual occurrences. This cannot be treated as the selected report PDF or as qualified report-text quantitative evidence. A correct response code, matching title, and nonempty content are insufficient.
* Other frozen HTML documents had their expected source titles and HTML structure in a representation-level spot check, including the calibration Bank of Canada, Fed, and Statistics Canada pages and the held-out Statistics Canada/NASA pages. This check **does not adjudicate quantitative claim content, completeness, chart/table extraction, or source legitimacy**. The two `application/pdf` rows (`QURC3-C04`, `QURC3-H02`) have recorded MIME/size/identity only in this review; a local parser/render check of those exact frozen bytes is still required, not an origin refetch.
* `SOURCE_CUSTODY_DEVIATIONS.md` blob `126837b132498626ee8783b101b9564c37ec9c84` preserves the first Git publication hygiene failure and unchanged raw response bytes; header/curl receipts remain local, with cookie-bearing headers excluded. No candidate-result-triggered substitution is authorized.
* Historical `SOURCE_POOL_SELECTION.json` says `SELECTED_NOT_BYTES_FROZEN`; later `SOURCE_FREEZE.json` establishes acquisition. This is chronology, not permission to edit the older selection status.

**Disposition of this readiness check:** source representation unsuitable for the selected H01 PDF. Do **not** execute or relabel #213's original held-out cohort. #212 permits preparing a **separately identified** source/evaluator successor. Its new source selection, partition, representations, byte freeze, and execution authority must be established **before** changed-cohort scoring. The PDF link found inside H01 does not become a silent substitute. No publication of held-out labels or new report-derived claims has occurred in this readiness record.

## Receipt-versus-evaluator finding

The declared #212 / #213 `PLAN.md` requirement includes value(s), lexical unit offsets, normalized unit, dimension/role, measure, comparator, time/scope, **exact consumed spans**, conversion identity and unresolved state independently for claim and evidence.

The frozen `unit_contract_tests.py` blob `3cd87c389af76fd46225324050ce132279a83800` has `expected()` returning `[[0,len(sentence)]]` for each non-event `claim_unit_spans` and `evidence_unit_spans`. This is the whole **input-scope** span, not an exact **lexical unit-token** span. Example `The rate was 10%.`: lexical `%` is `[15,16)`, full text is `[0,17)`. Fifteen relation-oriented test methods do not assert lexical offsets or actual consumed bases. The nine seeded weak controls do fail the existing self-test, but their failure is not receipt-contract assurance.

**Decision:** version the evaluator successor instead of editing `unit_contract_tests.py` or its hosted self-test. A valid V2 receipt distinguishes `input_scope`, `unit_lexical_span` and `consumed_evidence_spans`. Lexical ranges are UTF-8-decoded original-string Unicode codepoint `[start,end)` offsets, with recorded encoding/original-byte identity to enable reconstruction. Do not reinterpret a full-sentence span as a lexical token.

## V2 semantic checks required before evaluator freeze

1. Exact unit tokens `%`, `percent`, `percentage point(s)`, `basis point(s)`, `bp/bps`, and ambiguous `pp`. No prefix match inside `percentage`, plural swallowing, or arbitrary abbreviation acceptance.
2. Numeric-unit pairing and two-endpoint role binding. A year token is scope, not a quantitative value. Multiple units must be assigned to their associated measures.
3. Distinct **lexical unit identity** (percent vs percentage point vs basis point) and **quantity role** (rate level, relative percent change, absolute point change, count). `100 basis points = 1 percentage point` only for compatible absolute rate/change measures; the corresponding relative-percent statement is not thereby equivalent.
4. Comparator/direction/negation, measure/property and time/scope remain material under unit conversion. Distinguish conversion **available** from conversion **applied**; record rejection cause.
5. Original input scope, consumed claim/evidence spans, lexical token spans and value spans are separate, bounded and round-trip to the cited input. Endpoint arithmetic must cite both endpoints; `U16` must not bind the wrong `score` quantity to the `margin` claim.
6. Event-only `U18` is not-applicable, with empty quantitative measurements; unknown or unsupported interpretations refuse explicitly.
7. Positive, mutation, invariance, missing-span, semantic weak-control and independently inspected oracle checks. A structurally valid wrong span/role/measure/conversion must fail for that semantic reason. Passing a schema parser alone is not sufficient.

Receipt validation can establish reported token/span fidelity; it does **not** independently prove which text actually influenced a black-box analyzer. Claims about actual consumption need traceable local processing records and selective intervention/metamorphic tests, with the residual gap stated.

## Existing machinery and controlled scope

Use the exact RC2 comparator baseline `ce7348ae9a9e9b0fd03290e044516f3c302e06b0`, `quantity_binding.py` Git blob `05b1e7616cac8401656c8e777a6395f88d705a8c`, adapter `559306c69b56ad1f9725193a6188f2e986cf3a3b`; copy to a **new** candidate path only after prerequisites. Preserve policy SHA-256 `93c0ce49f0df91afda34c9513cca44345fda78f5297a5f48c55118277dad61d3`; policy Git blob `bf131991814a6a897f292eebac1d0ef765de10ce`, catalogue `fcd7b7964dea5a4e8bdd5cd3bd8c86f40bd97be1`. Existing Python/regex/native evidence receipts and registered conversion arithmetic are sufficient machinery for the bounded experiment; no mandatory dependency/platform change is justified.

The unmodified #213 `DEVELOPMENT_CASES.json` blob `ac467ee96b879612ad686caa741afcfdcc4f7c00` carries 19 **exposed** cases. `U19` is exposed predecessor failure only. The new V2 receipt evaluator must be frozen and independently self-tested before candidate semantic changes. A successful development run permits only the authorized fresh held-out unit qualifier, with first false deciding result terminal. No release, integration, repin or synthesized weight change.

## Execution/readiness blockers and non-claims

At the initial review, the authorized host was **offline** for the remote file tool. The required environment entrypoint and root workflow could not then be inspected; actual local Git worktree, worker isolation, full `[v1]` dependency environment and runtime read logs are **NOT_VERIFIED**. No locally isolated candidate, custodian runner, calibration or held-out scoring happened. Historical #213 hosted self-test `37251742482` is green but `candidate_executed:false`; public suite `37251742424` is red on inherited research/raw-fixture authoring-path scan (976 passed, five skipped, 48 deselected).

The separate actor-launcher authority remains with apparatus-contracts #173; its recorded safety stop cannot be bypassed to manufacture a blind run. A public repository and a sparse checkout do not enforce ignorance. The accompanying custodian-only launch manifest is **NOT_LAUNCHABLE**, and the derived builder packet must be given only through a validated isolated snapshot, never by a full #213 checkout.

**Research disposition:** no quantity candidate evaluated; no new scientific `SUPPORTED`/`FALSIFIED` claim. Preparation blocked on separately frozen source/evaluator successor plus observed isolation/environment. No primary research disposition is manufactured from this preflight.

## Subsequent owner-only correction and evidence, October 14

The authorized Mac was later available. Both local workflow convention files were read, and a dedicated clean owner-verification worktree was created. The original eight source bodies matched their recorded SHA-256/byte lengths. In separate, preselected S1 source custody, the report-PDF URL resolved as `application/pdf` (133 pages, 5,361,365 bytes), raw SHA-256 `c930831fbf7804dceb46e5311ebaefe24b6e8f709b09f1c739a1a9e1c4438966`. The raw S1 response stays custodian-local; `SOURCE_FREEZE_S1.json` identifies it. Eight S1 retained/new representations passed bounded mechanical parsing checks, not complete semantic extraction qualification. A six-file copy-only development packet was materialized with no Git metadata and no held-out bytes, but **effective executor isolation was not established**. Hosted V2 evaluator self-test `38502596463` passed 19 reference cases and 10 mutants; no candidate was executed or held-out labels revealed. These new observations do not retrospectively change the initial offline observation, original #213 freeze, or the remaining builder/actor admission gate.

The publicly recorded path-leak scanner failed on inherited frozen fixture paths and on newly introduced S1 environment identifiers. This successor removes its own machine identifiers without altering inherited historical evidence or the scan policy; the observed initial failure remains preserved in CI.
