# Changelog

## Unreleased

Experimental v2 work. No distribution version, no rules version bump: `cal-rules-v1.13.0`
still governs the v1 engine and the shipped `audit` / `demo` path is unchanged. The v2
decision layer and the interval operator ship in the wheel because they live under `src/`,
but neither is reachable from the CLI and neither is public API.

### Added (v2 decision layer — `pipeline_rules`, experimental)

- Five total stages, per-role eligibility, `Removal` records for everything dropped, and
  table-driven stage-2 predicates and stage-4 resolution rules.
- **Not** re-exported from `claim_audit_lab.v1.impl`. Import it by full path. An earlier
  revision re-exported `run_v2`, `V2Verdict`, `ClaimFrame`, `PassageEvidence` and `Removal`,
  which put an experimental module on the package's stable surface next to the v1 protocol
  implementations.

### Added (interval algebra operator — D1 / D12, partial)

- Interval subset containment over normalized units (time, mass, volume, ratio, temperature)
  with open/closed bounds and infinite endpoints.
- `ambiguous` status. The operator abstains when either side carries more than one bound on
  the claim's dimension, because it has no *measurand binding* and cannot tell which bound
  belongs to the claim's subject.
- Wired into stage 2 as `Q4_interval_containment`, **advisory**: it records its reading and
  removes no role. See the defect below for why.

### Found and fixed (v2 pre-merge review, 2026-08-22)

Six defects in the v2 branch, found by review before it landed. Each has a regression test
naming it.

- **False *supported* from an unbound measurand.** Q4 dropped the `refute` role whenever the
  interval operator read `satisfied`. On the claim "Product storage must not exceed 25 °C"
  against a passage reading "Ambient lab temperature must not exceed 22 °C. The product
  excursion reached 40 °C.", the operator matched the ambient bound, reported `satisfied`,
  and stripped a genuinely refuting passage of its standing to refute. A false substantiation
  on evidence recording a violation is the worst verdict this system can produce. Two fixes:
  the operator now abstains when a side carries multiple bounds on the claim's dimension, and
  Q4 no longer removes a role at all until a bound can be tied to a measurand.
- **`ValueError` escaping the pipeline on a temperature tolerance.** A tolerance is a width on
  a scale, not a position on it, so the affine °F/K conversion must not apply to it.
  `98 ± 2 °F` converted the tolerance as an absolute temperature (−16.67 °C), built the
  inverted interval `[53.33, 20.0]`, and raised out of `run_v2`. Added
  `normalize_delta_to_base`.
- **Stage 2 and stage 4 were not total.** The module header claims "an exception **marks a
  passage** and every stage runs to completion"; there was no exception handling anywhere in
  the module. A predicate that raises is now recorded, marked `skipped`, and **removes no
  role**; a resolution rule that raises yields to the next rule with precedence intact.
- **Containment depended on which spelling was the claim.** Unit normalization is
  multiplicative and lossy: `2.5 percent` → `0.025`, `25000 ppm` → `0.024999999999999998`. One
  direction read `satisfied` and the reverse `inconclusive` for one physical fact. Endpoint
  comparisons are now relative-tolerance.
- **Extraction followed the pattern table, not the sentence.** `within` sat above `less than`
  in the table, so "less than 5 mg of reagent, completed within 30 days" returned the
  duration. Extraction now collects every bound and orders them by position.
- **A bare number took the next word as its unit.** "Batch 12 was held" extracted a quantity
  on a `was` dimension. The identifier denylist only inspected the *following* token, so it
  caught `21 CFR` and missed `Part 11`. A point quantity is now a measurement only when its
  unit names a recognized dimension.

Also: `is_disjoint_from` returned `True` for incomparable dimensions, which let
`not subset and disjoint -> contradiction` fire on a unit mismatch; it now returns `False`
and `is_comparable_with` is public. `within X` on a dimension with no anchor (ratio,
temperature, scalar) no longer becomes the upper bound `(-inf, X]`.

### Registered (v2 evaluation is not yet like-for-like)

- `test_adversarial_twins_x5.py` asserts a false-adverse count of zero and an agreement floor
  of 50/56, and **never executed**. Its artifacts are sealed research outputs that are not
  version controlled, so it reported as a silent skip. It is now registered in
  `tests/conftest.py::_RESEARCH_ARTIFACT_MODULES` like every other test with the same
  dependency, so the public suite deselects it visibly instead. The assertions are unchanged
  and remain unrun here — this makes the absence legible, it does not supply evidence.
- `scripts/compare_v040_vs_v2.py` compared a v0.4.0 verdict *read from a sealed trace* against
  a v2 verdict *recomputed live* with `declared_mode`, `source_boundary`,
  `claimed_material_is_a_named_gap`, `claim_scope`, `passage_scope` and `passage_texts` that
  the v1 run never had. The first three are corpus construction parameters, and on a
  constructed corpus a construction parameter is close to the label: `relation="absent_from"`
  routes to coverage mode, and R1 returns *contradicted* off the named-gap flag alone. Every
  printed block now carries a declared-input disclosure counting how many cases received each,
  and the module docstring says plainly that those subsets are not like-for-like. The script
  also exits non-zero when no corpus was found, rather than printing nothing and succeeding.

### Changed (v2 — precedence follows confidence, not pipeline position)

Two structural fixes from a design review of the PILOT-001 regression, where v2
scored 64/98 against v0.4.0's 65/98 with 3 false adverse against 2, while scoring
56/56 on constructed twins. That gap localises to stage 0 and to what stage 4 was
willing to let a stage-0 guess decide.

- **The resolution table is reordered, and mode no longer routes it.** The three
  mode-guarded rules sat on top, and `_r_coverage_bounded` fires unconditionally
  for coverage mode, so a claim the stage-0 lexicon guessed into coverage could
  not be decided by evidence at all — a passage entailing it at 0.989 lost to a
  substring match. The table now runs caller-declared facts (R1, R2), then
  measured evidence (R3 conflicting, R4 refuted, R5 supported), then the rules
  that reason about absence (R6 coverage-bounded, R7 no-evidence, R8 no-signal).
  A rule reasoning about what is absent must not run before the rules that look
  at what is present.
- **Mode now parameterises obligations instead of partitioning rules.**
  Refutation is mode-blind: a coverage claim asserts a universal negative, and
  one counterexample falsifies it whatever the boundary says. Support is the
  mode-restricted obligation: an excerpt entailing "the document does not mention
  X" establishes nothing about the document, so a coverage claim's support still
  needs a declared exhaustive source (R2). D11 is intact — it governs *silence*,
  and an explicit contradiction is not silence. A stage-0 misclassification now
  costs a note rather than the verdict.
- **An undeclared `source_boundary` is distinguished from a declared `bounded`
  one.** `None` meant "not declared" and was read as the conservative value, so
  every undeclared coverage claim terminated in `not_resolvable` regardless of
  evidence. The two now carry different reasons, and the undeclared one names the
  missing input instead of presenting itself as a finding about the source.

### Fixed (v2 — Q1 provenance failed open on a missing trust level)

`_q1_provenance` read `trust is None` as "directly constructed, therefore
primary" and passed **silently**, justified by the assumption that it "never
fires outside the apparatus intake path". A replay whose traces do not carry
`trust_levels` violates that: every background source regains the right to
refute, and the trace shows a check that looks like it passed. Q2 and Q3 already
report *not evaluated* in the same situation — this was the third one, and D17's
shape in the file written to fix D17.

Absence is now always recorded. Whether it should also withhold refutation is a
new caller parameter, `trust_policy`, because only the caller knows whether its
corpus carries a trust model at all:

- `optional` (default, unchanged behaviour) — no trust model; absence is recorded
  and the passage keeps both roles. Construction-gold corpora build passages
  directly and carry no levels; failing closed there would silence every
  legitimate refutation in them.
- `required` — the caller has a trust model, so an unlevelled passage is an
  unknown source and may not decide an adverse degree.

### Added (docs — the atomicity seam)

`docs/v2-atomicity-seam.md` specifies what CAL v2 requires of an upstream
decomposer, so the apparatus-contracts work has a fixed target. Key finding: the
contract already exists as `v1/explicit_claims.py`, and v2's **three** atomic
degrees already produce `partially_supported` through the existing `all_of`
parent table. The 11 PILOT-001 misses attributed to v2's degree vocabulary are a
missing seam, not a missing degree, and widening `Degree` would put a
compound-claim outcome into an atomic vocabulary. No decomposer belongs in CAL.

### Qualification (run against `validation/` on 2026-08-22)

The branch was run against the project's own validation package rather than only against CI.

**No revalidation trigger fires.** v2 changes no shipped-engine file, is reachable from no CLI
command, and alters no dependency, so the v0.2 IQ/OQ/PQ records stand. It is library-only code
that happens to ship.

**CAL-REQ-054 failed on arrival and is now met.** The gate holds `src/` to ≥95% branch
coverage. The branch arrived at 74% (`interval_algebra.py`) and 79% (`impl/pipeline_rules.py`),
taking the `src/` total from 93% to 91% measured the same way. Both modules are now at **100%**,
and the total sits above the pre-branch baseline. Recorded as DEV-006, closed.

**No new validation matrix row is required.** The maintenance rule is to add a row before
adding a *public capability claim*; v2 makes none — it is absent from the README, absent from
the CLI, and no longer re-exported from `claim_audit_lab.v1.impl`. A row should be added when
and if v2 becomes a selectable engine, not before.

**Two pre-existing package gaps were found and recorded, not fixed** (DEV-007, DEV-008):
`docs/verification.md` is cited 18 times across the IQ/OQ/PQ protocols and is not in the tree,
and the whole package is still stamped `verified for v0.2 engineering release` against a tree
that is now `0.4.0` / `cal-rules-v1.13.0` with a 1,085-test suite where the OQ record cites 213.
Both need a release verification run with model access to close.

**The README verification table is left alone.** It is a dated receipt for `main`
(957 passed, 49 source files, 4073 statements). This branch moves all three (1,035 selected,
51 source files, 4,559 statements), so the table must be regenerated from a CI run before any
merge that lands v2 — but overwriting a dated receipt with figures from an unreleased branch
measured in a degraded environment would itself be the deviation it exists to prevent.

### Known limits (v2, unchanged by the above)

- **No measurand binding.** The multi-bound abstention closes the demonstrated false
  substantiation; it does not close the general case. A passage carrying exactly one
  temperature bound that is still not the claim's temperature reads as unambiguous. This is
  why Q4 is advisory, and it is the precondition for ever letting it decide.
- `p_entail` / `p_contradict` are carried on `PassageEvidence` but read by no rule. Every v2
  decision still runs off argmax and its probability, as v1's do.
- Importing `pipeline_rules` pulls `claim_audit_lab.v1.impl.__init__`, which eagerly imports
  the DeBERTa entailer and therefore torch and transformers. The layer needs no model *load*,
  but it cannot be imported without the inference stack installed, which weakens the
  "scored in seconds on every corpus" property it is built for.

## 0.4.0 — 2026-08-21

First public release of the v1 retrieve→entail engine. Track A packaging: the ordinary CLI
defaults to retrieve→entail, the decision layer is frozen at `cal-rules-v1.13.0`, and a
standalone HTML audit report ships for human review.

**Not `v1.0.0`, and the leading zero is the claim being made.** The interface is unsettled and
the accuracy story is unfinished: 27/50 exact agreement against human gold on a one-shot
exploratory packet, 62/98 on the PILOT-001 DEV set, and a defect register with open entries
including two found by preparing this release. Not a PyPI publish.

`0.3.0` was declared but never released, and named several different trees while the v1 work
was in flight. The first public tag is `0.4.0` so that one version string names one tree.

### Packaging

- `Documentation` and `Changelog` project URLs added; the docs site was not discoverable from
  package metadata.
- `Typing :: Typed` classifier — the package ships `py.typed` and is `mypy --strict` clean
  across all 49 source files. `Intended Audience` classifiers added.
- **The sdist shipped 17 of 121 test files** — setuptools' default heuristic picks up
  `tests/*.py` and misses `tests/v1/`, so the sdist carried a suite that could not run. The
  full tree now ships, verified by name against `git ls-files`, and the sdist can verify
  itself.
- Wheel contents confirmed: `report.css`, `py.typed`, the frozen rules file, examples and
  schema. Neither artifact carries `outputs/`, a venv, or caches.

### Registered (D16 — A7 terminates instead of falling back to the eligible pool, 2026-08-21)

Found by the official release run over a sealed C-B bundle
(`outputs/2026-08-21-official-bundle-run/`).

A claim about chamber CH-04 was withheld as `not_checkable / out_of_scope` when the bundle
held **two** contradicting passages: CH-04 at 0.9849 and CH-07 at 0.9888. Aggregation takes
the highest score, A7 read the scope of *that* passage, found it disjoint, and withheld —
never looking at the in-scope passage that genuinely refutes the claim.

**This is D7's shape in a newer gate.** D7 is registered against A4 as "terminates instead of
falling back to the eligible pool"; A7 does the same. The fix is to check the eligible pool
for an in-scope contradiction before withholding, which is D7 — held pending D6, so it should
land with them rather than alone.

**Partly a cost of the `v1.13.0` fix, and worth saying plainly.** Before it, A7 could not see
the out-of-scope passage's scope at all, so it stood down and A4 returned `contradicted` —
the right verdict, reached by deciding on an out-of-scope passage and getting lucky that an
in-scope one also contradicted. The fix traded a right-by-accident adverse verdict for a
wrong abstention. The direction is the safer one and the one the engine is designed to fail
in, but it is still a miss.

### Registered (D15 — the rules-only replay cannot test a gate newer than its baseline, 2026-08-20)

Found while gating the D14 fix, and it invalidates a claim published earlier the same day.

`scripts/pilot001_a5_a4_landing_run09.py` replays recorded evidence through the current rules
layer, so no model runs and only a rule change can move a verdict. That is a real strength for
threshold changes. It is a trap for **new gates**: the replayed `SupportSignal` carries only
the fields that existed when the baseline was recorded.

`A5_conflicting_evidence` (landed `v1.9.0`) reads `best_entail` and `best_contradict`. The
run-08 baseline was recorded under `v1.7.0`, whose `SupportSignal` had
`label` / `max_entailment_score` / `contributing_passage_id` and nothing else. **A5's
precondition was therefore unsatisfiable on every replayed claim**, and the replay dutifully
reported zero changes — not because the gate is a no-op but because it could never fire.

Measured end to end instead (`outputs/pilot-001-dev-calibration/run-12-d14fix-end-to-end-2026-08-20/`,
sealed): **A5 moves 2 of 98**, both `supported` → `not_checkable`, both against human gold of
`supported`. **PILOT-001 exact agreement is 62/98, not the 64/98 inherited from `v1.7.0`.**

The evidence is identical either way — same passages, same labels, 0 of 98 claims differ in
entailed-set size — so this is a harness limitation, not a pipeline change.

**Rule going forward: a rules-only replay may only be cited as evidence for a gate whose
inputs already existed in the baseline it replays.** Anything newer needs an end-to-end run.
Every affected figure in the README, the benchmarks page, the research page and Brief 02 has
been corrected rather than footnoted.

### Found and fixed (D14 — A7 failed open on identifiers containing a numeral, 2026-08-20)

Found by running one realistic paragraph through the **built and clean-installed wheel** as a
release-package acceptance check. A claim about chamber `CH-04` was returned `contradicted`
on a passage about `CH-07` — the disjoint-scope family `A7_scope_mismatch` exists to
withhold.

Not a vocabulary gap: `chamber` is already in `LOCATION_HEADS` and `scope_anchors` extracts
`ch-04` from the claim. The parser tags a separated-numeral identifier as a **number**, so it
attaches as `nummod` to a following noun instead of heading the subject; with an ambiguous
verb the sentence is then left with no nominal subject at all, `scope_anchors` returns
nothing, and **A7 stands down so A4 decides**.

**It is identifiers, not quantities.** The obvious reading was "a numbers problem", so it was
measured rather than assumed (`outputs/2026-08-20-d14-identifier-parse-probe/`). Holding the
sentence fixed and swapping only the identifier: `CH-07` with quantities goes blind, `Bravo`
with **the same quantities** does not, and `CH-07` with **no quantities at all** still goes
blind. Across identifier × verb, **14 of 66 combinations go blind** — every identifier that
breaks contains a separated numeral, every purely alphabetic one is safe, and which verb
breaks it is not predictable (`CH-07` survives *showed* and fails *recorded*; `CH-7` fails
five of six). Equipment IDs, SOP numbers, batch and lot codes, and line/unit numbers are
exactly the shapes that carry scope in a regulated document.

This is **not** the D1/D4/D12 numeric-comparison family, and no blanket "avoid claims with
numbers" warning would be correct: quantities are ruled out as the trigger, the acceptance
run's own numeric claim was correctly `supported`, and the real numeric family makes CAL
*abstain* — the safe direction — so such a warning would point at the caution and stay silent
about the hazard. The warning that ships instead is narrower: when a claim's scope turns on an
identifier containing a numeral, confirm the cited passage names the same entity.

An eligibility gate that silently withholds itself when the parser slips is worse than one
that never existed, because the register reads as though the gate considered the case. Same
hazard class as the recorded A4 negator parse-quality note, now with a demonstrated adverse
consequence.

**Fixed in `cal-rules-v1.13.0`** — see the entry at the top of this file. Gating it required
a fresh end-to-end PILOT-001 run, because a rules-only replay feeds recorded features back in
and cannot test a feature change; that run is what surfaced D15.

Receipts: `outputs/2026-08-20-release-package-acceptance/` — the same run also demonstrates
byte-identical reruns of the installed wheel across Markdown, JSON, and HTML.

### Added (human-readable HTML report, 2026-08-20)

The client-facing deliverable. `claim_audit_lab.report_html` renders a standalone HTML
report for both engines; `demo` writes one by default, `audit` takes `--html-out`, and
`audit-bundle` takes `--html-report` (opt-in there, because the audited bundle is the
artifact on that path and apparatus consumers read the traces).

- **Self-contained.** The stylesheet is inlined from package data
  (`claim_audit_lab/assets/report.css`); no scripts, no external requests, renders offline.
- **Deterministic.** Nothing in the renderer reads the clock. `run_id` and `audited_at` are
  supplied by the caller or omitted, so the same audit renders the same bytes.
- **PDF is the browser's print dialog**, not a generated file. The stylesheet carries an
  `@media print` block — forced light sheet, page margins, `break-inside: avoid` on each
  claim, expanded link targets. A PDF writer would stamp `/CreationDate` and `/ID` into
  every run, so a generated PDF could not be byte-reproducible even though the audit is.
  No PDF toolchain is added to the package.
- **Provenance is mandatory on the surface.** Engine, rules version, `rules_file_sha`,
  `audit_config_hash` and library version are printed on every report, and the status band
  (`not validated software · not a GxP capability claim · verdicts are review inputs`) is
  the first thing under the title. A v0.2 report rendered without provenance says so
  explicitly rather than quietly omitting the question.
- The v1 limits list is now authored once (`_v1_known_limits`) and rendered into both
  Markdown and HTML, so the two cannot drift; backtick spans are promoted to `<code>` in
  the HTML rather than printed literally.
- Report version strings come from `claim_audit_lab.__version__` — the value the pipeline
  already stamps on every trace — rather than installed distribution metadata, which goes
  stale in an editable checkout and would make rendering environment-dependent.

### Fixed (pre-publication correction pass, 2026-08-20)

Published figures and provenance, corrected before this tree goes to a public remote. No
rules change; `cal-rules-v1.12.0` and its `rules_file_sha` are untouched.

- **Path leak.** `scripts/slg_scaled_p2_cursor.py` hard-coded an authoring machine's scratch
  path. The agent's throwaway cwd is now derived at run time from `tempfile.gettempdir()`,
  overridable with `CAL_P2_WORKDIR`.
- **A guard that covers the whole tree.** `tests/test_no_authoring_paths.py` scans every
  tracked file for authoring-machine path shapes. The existing guard in `test_report.py`
  only scanned `examples/`, which is why three separate leaks reached the tree — and the
  longest-lived one carried no `/Users/` at all, encoding the same information as
  `-Users-<user>-Desktop-` inside a temp path. The new guard matches shapes rather than
  literals and is verified against all three historical leaks. It scans itself and takes no
  exemption: its first version failed its own scan on the sample leaks in its fixtures, which
  are now assembled from fragments at run time, and a test asserts the guard is tracked so
  the scan cannot pass by silently skipping it.
- **Sealed-directory clobber (DEV-005).** `scripts/audit_construction_gold.py` wrote its
  output into the directory it read the corpus from, so re-running it overwrote a sealed
  `audit_results.json` and 33 traces without regenerating the manifest. It now takes
  `--corpus` and `--out` separately. The affected directory's manifest is left **failing on
  purpose** — re-sealing would have hidden a real loss — and the incident is recorded in
  `validation/deviation-log.md` and in `DEVIATION.md` beside the outputs.
- **Construction gold re-measured on the shipped engine.** The published 22/33 was the
  `v1.10.0` figure. Re-run on `cal-rules-v1.12.0`: **26/33**, adverse-verdict precision
  **7/7** and recall **7/7**, variant-group partition agreement **7/9**. All seven remaining
  misses are false abstentions — gold `supported` read as `not_checkable`; no false adverse
  verdict remains in the corpus. Sealed at `outputs/2026-08-20-construction-gold-v1.12.0/`.
- **PILOT-001 no-op measured rather than assumed — and then the measurement was wrong.**
  Run-11 replayed the sealed evidence through the `v1.12.0` rules layer and reproduced the
  `v1.10.0` replay byte for byte. That was recorded here as confirming no landing from
  `v1.9.0` through `v1.12.0` moves a human-gold verdict. **It confirms no such thing** — see
  the D15 entry below. Run end to end, `v1.9.0` moves 2 of 98. Corrected on the same day it
  was written.
- **Clean-wheel verification was failing, and claimed a surface it never checked.**
  `scripts/verify_install.py` installed `[v1]` and ran `claim-audit demo` without provisioning
  the spaCy pipeline, so the v1 surface check has failed since `demo` began defaulting to the
  v1 engine — while the README reported it as verified. It now provisions `en_core_web_sm`
  (copying a local install when present, else `spacy download`) and gained
  `_verify_ui_surface`, which installs the wheel with **only** `[ui]` and imports both UI
  modules. All three surfaces — v0.2, v1, ui — are now actually exercised.
- **README's "no network access required" applied to the whole verification block**,
  including the install verifier, which builds a wheel and installs from PyPI into three
  clean virtualenvs. The offline claim is now scoped to the test suite, where it is true.
- **Test and coverage counts.** README and the docs site claimed 894 tests and 96% branch
  coverage; the tree is **984 tests** and **95%** (4045 stmts, 1186 branches).
- **Sealed-output integrity.** Claimed 28/28; actually **34/35**, the thirty-fifth being
  DEV-005 above. The docs now say so and link the deviation.
- **`DECISIONS.md` 2026-07-24 entry amended.** It asserted CAL v1.0.0 was "formally accepted
  and qualified as a deterministic, unbiased research measurement instrument". No `v1.0.0`
  exists, a one-shot exploratory gate against a single coder cannot establish absence of
  bias, and the entry called the same gate both "confirmatory" and "one-shot exploratory".
  The sentence is struck and preserved, with a dated amendment at the head of the entry.
- **Stale references.** `cal-rules-v1.10.0.yaml` → `v1.12.0.yaml` on the reproducibility
  card; run dates; the `14→20→22` progression now reads `14→20→22→26`.
- `outputs/` added to `.gitignore` — sealed research outputs are deliberately not
  version-controlled, and nothing under it was tracked.

### Changed (v1 rules — `cal-rules-v1.13.0`, identifiers are not numbers)

Fixes D14, a false adverse verdict on the shipped engine. Thresholds unchanged from v1.4.0.
`rules_file_sha`: `eac9105b756de64530ff0d345ffb3a29c213281d41ff1ee211090ccdf51d7e2a`.

- A7's scope operator could not see an entity whose identifier contains a numeral. spaCy tags
  `CH-07` / `SOP-014` / `STB-2291` as **numbers**, so they attach as modifiers instead of
  heading the subject; with an ambiguous following verb the sentence is left with no nominal
  subject at all, `scope_anchors` returns nothing, and A7 stands down so A4 emits the verdict
  A7 exists to withhold.
- Identifier tokens are now normalised to letter-only placeholders before parsing and mapped
  back afterwards. **Scoped to scope extraction**, so every other feature keeps the parse it
  had and cannot move.
- Forcing `token.pos_` does not work — the parser reads tok2vec vectors, not tags (tested).
  Widening the harvest risks over-firing A7 into false abstentions. Failing closed would
  contradict `scope_mismatch`'s documented rule that an empty side is not a mismatch, which
  exists so A7 cannot suppress a subject-less true contradiction. Normalising fixes the
  parser's input instead of compensating for its output.
- **Probe: 14/66 → 3/66 blind.** The residual three are bare digits and multi-token forms
  (`07`, `Line 3`, `Unit 9`), deliberately outside the pattern — catching them would mean
  treating quantities as identifiers. Letter-initial is the guard that keeps `12-month`, `25`,
  `3rd` and `211.22` untouched.
- **No verdict moves anywhere.** Construction gold 26/33 → 26/33, adverse 7/7 and 7/7, zero
  verdict changes. A7 fires on **0 of 98** PILOT-001 claims both before and after, and
  `scope_anchors` feeds only `scope_mismatch`, which feeds only A7 — so the fix is provably a
  no-op on human gold. All **30** frozen goldens regenerated hash-only with **0** verdict or
  rule flips.
- Still open: a universal claim refuted by a specific counterexample is withheld by A7. That
  behaviour predates this change (measured both ways) and is unregistered pending an observed
  consequence.

### Changed (v1 rules — `cal-rules-v1.12.0`, A7 asks which site)

- New gate `A7_scope_mismatch`: a contradiction whose contributing passage names
  a disjoint location phrase from the claim is not licensed to decide. CAL
  returns `not_checkable` / `out_of_scope` and asks which site the claim is
  about. Same-site contradictions still fire A4. Thresholds unchanged.
- `explain` next-step is family-specific: scope mismatch, numeric-bound silence,
  C6a quantity demotion, and two-hop `read_silent` each ask a different
  question. "Find another source" is last resort.
- Public docs now distinguish 27/50 (human gold, messy extraction) from 47/50
  (constructed twin, derived keys). Neither is a `v1.0.0` tag.

### Changed (v1 rules — `cal-rules-v1.11.0`, A6 reads `source_boundary`)

- A6 now consumes the caller-declared `source_boundary`. Bounded / undeclared
  coverage claims still withhold an adverse verdict (D11). Exhaustive coverage
  claims are `supported` (`A6_absence_decidable`) unless a complement-entailment
  shows the source does address the denied material. `named_missing_material`
  plus caller-declared `claimed_material_is_a_named_gap` is `contradicted`.
  Thresholds unchanged from v1.4.0. Construction gold 22/33 → 26/33
  (exhaustive absences CG-08a/09a/07a and named-gap CG-21).

### Fixed (D5 — negative-existential negator)

- `negate_claim` abstains on `No X was P` / `None …` rather than emitting
  `No X was not P`. An abstention never demotes.

### Noted (numeric — D1 / D4 / D12)

- Quantity comparison is a different operator family from C6a equality-within-
  tolerance. Range midpoints, bound instantiation, and the entailer's refusal
  to compare 10 °C with 9 °C will not be patched inside C6a. Deferred to a
  quantity-comparison operator (or a different entailer). v2.

### Changed (Track A CLI — ordinary `audit` / `demo` default to v1)

- `claim-audit audit` and `claim-audit demo` now run engine `v1-retrieve-entail`
  with frozen rules `cal-rules-v1.10.0`. Pass `--engine v0.2-lexical` for the
  retired matcher. `audit-bundle` still follows the bundle's sealed `pipeline`
  field (default `v0.2-lexical`) so apparatus pins stay intact.
- Written v1 reports name `engine` and `rules_version` so a reviewer can see
  which pipeline produced the file. Not a validation claim and not a release tag.
- Ordinary v1 Markdown reports carry a **Known limits** section (no tagged
  `v1.0.0`, not validated, open defects named, construction-gold 22/33).

### Fixed (D13 — `explain` next step for `read_silent`)

- `read_silent` no longer tells the reviewer that a different source is needed
  whenever no passage entails the claim alone. Two or more admitted passages
  now instruct the reviewer to read the admitted set before seeking another
  source. The class name is unchanged.

### Confirmed (D8 — conjunct-scoped A3)

- Production `A3_conjunct_negation_suppressed` recovers the live PILOT-001
  wording of `rsh-475fe956a5fb-c002` (`doesn't` included). Entail 0.625 is
  `partially_supported`, not `contradicted`. Affirmative whole-compound
  contradictions still fire A3. Broader compound-negation forms remain out of
  scope.

### Measured (2026-08-20 re-score of the sealed 50-item gold)

- `claim-audit calibrate` over the 2026-07-24 packet on `cal-rules-v1.10.0`:
  exact 27/50, Cohen's κ 0.3528, AC2 0.7901 (on-scale n=22), weighted κ 0.6876.
  Two runs byte-identical. Headline statistics unchanged from v1.7.0. A5/A6 did
  not fire. Not a new confirmatory gate and not a `v1.0.0` tag.

### Changed (v1 rules — `cal-rules-v1.7.0`, A4 negation-consistency confirmation)

- Hard contradictions are retained only when the contributing premise also entails the
  structurally negated claim (DECISIONS.md § 2026-07-16 v1.7.0): the pipeline records an
  additive `AuditTrace.negation_probe` (serialized only when a probe ran) and the rules layer
  demotes unconfirmed contradictions to `not_checkable/no_entail_signal` via
  `A4_negation_consistency`. New `features.negate_claim` structural negator (abstains rather
  than guess). Closes `SLG-09`: the structured E3 suite is fully green (15/15 targets, 19/19
  atoms, 10/10 parents, 3/3 variants); PILOT-001 run-07 shows zero verdict changes across 98
  claims. Thresholds byte-identical; goldens hash-only with zero flips. DEV evidence, not a gate.

### Changed (v1 rules — `cal-rules-v1.6.0`, A1 combined structural guard)

- `sentence_type()` hardens A1 imperative detection with the accepted combined structural
  guard (DECISIONS.md § 2026-07-16): a non-root subject-bearing `VERB`/`AUX` makes the
  sentence declarative, and a subject-less verbal root is imperative only behind an
  `intj`/`advmod`/`neg`/`aux` pre-root prefix. Frozen rules bump to `cal-rules-v1.6.0.yaml`
  with byte-identical thresholds; all 27 goldens regenerated with `audit_config_hash`-only
  changes and zero verdict flips; two new A1 end-to-end fixtures added. The run-06 replay
  (`scripts/pilot001_a1_landing_run06.py`) reproduces the run-05 prototype's exact two-claim
  PILOT-001 DEV diff (62→64/98, 2 recoveries, 0 regressions, F4=0). DEV evidence, not a gate.

### Added (v1 E2 — explicit claim structure)

- Additive caller-declared `single` / `all_of` explicit-claim request and trace contracts, with
  provenance-bound atoms, independent atomic auditing, canonical request/trace serialization,
  fail-closed auditor binding, and deterministic two-axis parent aggregation. The new public
  helpers remain import-light; the default inference wrapper stays in `v1.runner`. This is an
  engineering mechanism, not validation, a release claim, or an inferred decomposition feature.

### Added (DEV structured-contract diagnostics)

- Frozen Simple Logic Gold construction, direct-lane, and structured-lane tooling with separate
  semantic-target, runtime-atom, and parent denominators; complete traces; exact repeatability;
  and stable-ID, evidence-order, irrelevant-evidence, and wording transformations.
- Three additive A1 parser-guard trials culminating in a 17-canary combined candidate. These are
  recorded-trace DEV diagnostics only; the candidate is not package behavior and cannot authorize
  a rules bump without operator sign-off.

### Added (DEV progressive human gold)

- `scripts/progressive_next_rungs.py` builds and seals separate Rung 2 atomic-polarity and Rung 3
  bounded-sufficiency reviewers. Packets are rebuilt from fixed manifests plus canonical C-B
  sources, omit target relations and answer-bearing fields, require exact passage provenance for
  direct relations, and allow retrieval gaps only when missing material is explicitly named.
- `tests/v1/test_progressive_next_rungs.py` covers rung-specific schemas, deterministic source
  rebuilding, candidate-count and packet drift, exhaustive negative/sufficiency paths, passage
  provenance, named-source retrieval gaps, self-contained HTML, and byte-stable artifacts.
- `scripts/progressive_gold_review.py` builds and validates a separate five-item Rung 1
  positive-control reviewer. The guided flow records atomicity, direct support, and exact
  rationale passage provenance; negative and uncertain paths escalate without being coerced into
  another relation. A negative answer requires every bounded candidate to have been viewed, and
  sealing first rebuilds the packet from its manifest and canonical C-B sources. The reviewer is
  project-local DEV tooling, not a package API or gate input.
- `tests/v1/test_progressive_gold_review.py` covers deterministic packet construction, self-hash
  and canonical-source drift, dependent question shape, exhaustive-negative enforcement, passage
  provenance, escalation, incomplete exports, self-contained HTML, and byte-stable artifacts.

### Added (v1 scaffolding)

- `claim_audit_lab.v1` subpackage exposing `protocols`, `models`, `features`,
  `config`, and `impl` (see DECISIONS.md § 2026-06-21 § 1).
- Pinned-revision retriever and entailer (`BiEncoderRetriever`, `DeBERTaEntailer`)
  bound to pinned HF revision SHAs in the default config. Inference bodies were
  `NotImplementedError` stubs through Phase 1; wired to real CPU inference in Phase 2
  (see *Added (v1 Phase 2 — inference layers)* below).
- Concrete `MaxEntailmentAggregator` (pure data; no external dependency).
- `VerdictRules` skeleton with the documented six-step rule order; body wired in
  Phase 1.
- Four deterministic feature-extractor signatures (`has_numerical_value`,
  `has_explicit_negation`, `has_universal_quantifier`, `has_modal_strength`); bodies
  wired in Phase 1.
- Default `AuditConfig` shipped as package data at
  `claim_audit_lab/v1/configs/v1-default.yaml`; loadable via
  `claim_audit_lab.v1.load_default_audit_config()`.
- `[v1]` optional-dependency extra in `pyproject.toml` declaring the retrieve→entail
  inference stack (`quantulum3`, `spacy`, `sentence-transformers`, `transformers`,
  `torch`). Install with `pip install -e ".[dev,v1]"`. spaCy model:
  `python -m spacy download en_core_web_sm` post-install.
- Clean-venv wheel install of `[v1]` extra exercised by
  `scripts/verify_install.py` alongside the existing v0.2 surface check.

### Pinned (v1)

- Retriever: `sentence-transformers/all-MiniLM-L6-v2` @
  `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.
- Entailer: `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli` @
  `6f5cf0a2b59cabb106aca4c287eed12e357e90eb`.
- Resolved via the HF API on 2026-06-22.

### Added (v1 Phase 2 — inference layers, B10–B13)

- Real `BiEncoderRetriever` (`sentence-transformers/all-MiniLM-L6-v2`): CPU,
  deterministic, loaded from the pinned revision SHA; embeds claim + passages once
  per call, ranks by cosine, returns top-`k` (retrieval-floor filtering stays the
  rules-layer `A2` gate's job). Process-level model cache; unpinned revision raises.
- Real `DeBERTaEntailer` (`MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`): CPU,
  `eval()` + `no_grad()`, MNLI/FEVER `(premise, claim)` tokenization, label via the
  model's `id2label`, softmax-max `score`, and **unrounded** three-class `raw_logits`
  in native class order for downstream re-thresholding. Same cache + guard.
- `claim_audit_lab.v1.impl._determinism.enforce_cpu_determinism()` — the v1 CPU
  determinism baseline (`torch.set_num_threads(1)` + `torch.manual_seed(0)`),
  enforced at module load by the retriever and entailer.
- End-to-end byte-identity over real inference: `tests/v1/test_byte_identity.py`
  (5 claims × 3 passages, real retriever + entailer + aggregator + rules) with 5
  committed golden traces under `tests/v1/fixtures/traces/inference/` (regenerate
  with `CAL_WRITE_GOLDENS=1`).
- Per-layer determinism + behaviour tests (`test_retriever.py`, `test_entailer.py`)
  and a YAML field-order/whitespace `audit_config_hash`-invariance test (B12 parity).

### Fixed (v1)

- `MaxEntailmentAggregator` no longer lets a confidently-neutral passage mask a
  real entail/contradict signal: it now ranks only support-bearing (non-neutral)
  results and abstains to neutral only when every candidate is neutral. Surfaced by
  real inference (`inf-01` / `inf-03` were flipping to `not_checkable`); the
  `SupportSignal` contract and rules layer are unchanged. Residual: genuinely
  conflicting evidence (strong entail + strong contradict on one claim) still
  carries only the higher-scoring signal — a documented, calibration-gated
  limitation; the two-signal redesign is the upgrade. See DECISIONS.md § 2026-06-29
  (neutral-masking fix).

### Added (v1 Phase 3 — apparatus intake, B14–B16)

- **B14 — `AuditRequest` normalizer.** `claim_audit_lab.v1.intake.bundle_to_requests`
  converts a loaded C-B `BundleContents` into one `AuditRequest` per auditable
  (`extracted_claim`) claim; `retrieval_seed` records are skipped. Each request
  carries the bundle's *full* passage set (the retriever, not the bundler, picks
  candidates — DECISIONS.md § 2026-06-21 § 2); passages use the globally-unique
  `{source_id}/{passage_id}` handle with raw C-B coordinates + hash preserved in
  `source_meta`. YAML is parsed once at `load_bundle`; everything downstream is
  frozen pydantic. Re-exported as `claim_audit_lab.v1.bundle_to_requests`.
- **Dual-path selector.** New optional `CBAuditConfig.pipeline`
  (`"v0.2-lexical" | "v1-retrieve-entail"`, default `v0.2-lexical`) selects which
  auditor a bundle routes through. Optional + v0.2-default, so existing/external
  bundles validate unchanged, keep their `config_hash`, and route v0.2; opting into
  v1 means writing+sealing the field. v1 inference always uses the pinned
  `load_default_audit_config()`, not the bundle's thresholds. See DECISIONS.md
  § 2026-06-29 (Phase 3 Unit 1). Routing on the selector lands in B15.
- **B15 — `audit-bundle` v1 routing + trace writeback.** `claim-audit audit-bundle`
  now branches on `CBAuditConfig.pipeline`. The `v1-retrieve-entail` path normalizes
  → runs the pinned v1 pipeline (`v1.runner.run_default_audit`) → writes
  `claims/{claim_id}.audit-trace.json` (replay-sufficient) into the audited copy and
  populates each per-claim YAML `audit` block via the v1→C-B verdict crosswalk
  (`v1.cb_writeback.cb_support_verdict`: `contradicted`→`unsupported`, `overstated`
  flag collapses a positive degree, `not_checkable` stays `not_checkable` —
  DECISIONS.md § 2026-06-29 Phase 3 Unit 2). `SHA256SUMS` + `bundle_hash` are resealed
  over the augmented file set. The default `v0.2-lexical` path is unchanged and
  byte-identical to before. Torch is imported lazily on the v1 branch only.
- **No loader change needed for v1 routing.** A v1 bundle carries a v0.2-policy-shaped
  `CBAuditConfig` + the `pipeline` field, so the existing fail-closed policy gate
  admits it untouched (Unit 1's forward note was wrong; corrected in the Unit 2 ADR).
- **B16 — apparatus round trip + typed audited loader.** The integration harness now
  builds Evidence Bundler's real `scaffold-run-minimal` fixture through its
  `build-fixture-bundle` CLI, opts the generated C-B copy into v1 while recomputing the
  audit-config and bundle integrity hashes, audits it with pinned metadata, and reloads
  the audited copy through both `load_bundle` and the new
  `claim_audit_lab.v1.load_audited`. `load_audited` returns an additive
  `AuditedBundleContents` subtype with strict `AuditTrace` objects keyed by claim ID;
  it delegates all C-B/YAML verification to `load_bundle` before validating trace JSON
  and claim bindings. The fixture has no expected-outputs file, so the test explicitly
  grounds and locks `clm-001` as C-B `supported`, v1 `supported`, no reason sub-label,
  and an `entail` signal. Runnable, path-portable instructions and the synthetic-only
  limitation are in `docs/v1-round-trip.md`.

### Changed (v1 Phase 3 — internal)

- `contracts/serialization.py`: extracted public `reseal_bundle()` + `write_sha256sums()`
  (were private in `output_writer.py`); both the v0.2 and v1 writebacks share them.
  v0.2 audited-bundle output is byte-identical pre/post the refactor.
- `contracts/audit_flags.py`: extracted public `is_material_deviation()`; `compute_flags`
  refactored onto it (behaviour identical), and the v1 writeback reuses it.

### Added (v1 Phase 4 — Unit 1 / B17 — `calibrate`)

- `claim-audit calibrate --packet --gold --config --out --traces-out --pinned-at`: runs the
  v1 pipeline over a packet of C-B bundles, scores each claim against a blind gold, and writes
  a deterministic Markdown calibration report + one `AuditTrace` JSON per claim. Synthetic
  boundary only — it does not run the sealed PILOT-001 gate and applies no pass/fail thresholds.
- Built against the **shipped two-axis verdict** (DECISIONS.md § 2026-06-29 Phase 4 Unit 1):
  a 5×5 `support_verdict` confusion matrix with `overstated`/`inferred` on a separate flags
  axis; the gold is crosswalked via the 3 explicit mappings. Report timestamp is the
  `--pinned-at` value only (no wall clock), so two runs are byte-identical.
- Metric suite (`v1/calibrate.py`, stdlib only): exact agreement; Cohen's κ + simplified-Wald
  95% CI; Gwet AC2 + ordinal quadratic weighted-κ (Decision D, prevalence-robust); 5×5
  confusion; flags table; adverse-rate `(unsupported+contradicted)/checkable` overall +
  per-condition + per-model; recall floor on starved claims. **No gate threshold is baked in**
  (Decision D stays PROPOSED → re-derived under AC2 at Unit 3).
- `claim_audit_lab.v1.config.load_audit_config(path)`: load operational knobs from a YAML path
  while still materializing verdict thresholds + `rules_file_sha` from the pinned rules file.
- The engine is torch-free (the auditor is injected); heavy inference imports stay local to the
  CLI command, so the v0.2 path never loads torch.

### Added (v1 Phase 4 — Unit 2 — synthetic dry run + report schema)

- The canonical synthetic calibration packet grew **5→12 claims** (4 conditions × 3, 2 models,
  3 starved) to exercise every report section with >2-row tables before the PILOT-001 gate. It
  reuses the five committed-golden contents under twelve claim_ids, so every CAL verdict stays
  deterministic and hand-checkable (CAL columns confined to {supported, contradicted,
  not_checkable}; the gold spans all five degrees).
- The report **section schema** is pinned for sign-off in DECISIONS.md § 2026-06-30 (8 fixed
  headers + per-section column contract + determinism contract). **PROPOSED** — not self-approved.
- Pure-metric unit tests decoupled onto a fixed 5-pair `HAND_PAIRS` (κ 0.7222 / weighted 0.94915 /
  AC2 0.95263, unchanged); packet/assembly/CLI tests assert the 12-claim numbers (exact 10/12,
  κ 0.7647 = 13/17, on-scale n=9, weighted-κ 0.9854, Gwet AC2 0.9860). Byte-identical across two
  runs. No `src/` change; no gate run; Decision D threshold still deferred to Unit 3.

### Added (v1 Phase 4 — Gold Lite ten-claim DEV rehearsal, 2026-07-11)

- `scripts/gold_lite_review.py` adds a project-local, non-public rehearsal tool that reuses
  CAL's fail-closed C-B loader, selects ten PILOT-001 parent claims by a fixed SHA-256 seed,
  verifies proposed atomic decompositions, and writes a blinded self-contained local browser
  reviewer. It hides old gold, CAL outputs, condition/model, EB role/rank, and trust labels;
  binds human rationales to passage hashes; validates additive checkpoint exports; and derives
  transparent `single` / `all_of` parent results. It does not change package source, rules,
  config, the public CLI, or the acceptance procedure.
- `tests/v1/test_gold_lite_review.py` adds 12 fast tests for deterministic selection, packet
  hash drift, blinded shape, byte-stable generation, rationale requirements, checkpoint
  handling, and compound aggregation. The real local packet is 10 parents / 17 proposed
  steps / 50 retained parent-level EB candidates with packet hash
  `sha256:7ed7cd4763efd079668296dd17e4d74a80aebfdcbd2035e53acd2699a3bc2bd8`.
- Verification: **503 passed**, Ruff check/format, mypy `--strict src`, compileall,
  **97% source branch coverage**, clean-wheel v0.2/v1 verification, two-build packet byte
  identity, and local browser smoke all green. Human review has not started; this remains DEV,
  never validation or gate evidence.
- `scripts/anthropic_api_bridge.py` and `scripts/gold_lite_model_panel.py` add an optional,
  project-local model-assistance experiment. The bridge uses the Basic Research Harness
  Anthropic SDK runtime read-only, counts each request, performs one API call, and preserves the
  raw receipt. The panel prepares blinded per-parent requests, validates exact packet/provenance
  coverage, preserves model failures, derives strict silver candidates, and writes a separate
  post hoc majority-triage sheet. It does not add an Anthropic package dependency to CAL.
- `tests/v1/test_gold_lite_model_panel.py` covers prompt blinding, pinned model tiers,
  API-supported schema constraints, packet/provenance normalization, raw receipt hashing,
  refusal handling, exact-vote aggregation, and the distinction between strict silver and
  majority assistance. The real DEV run preserved 40 receipts, validated 31, produced 2/17
  strict silver atoms, and offered 11 strong / 2 weak / 4 unresolved assistance suggestions.

### Added (v1 Phase 4 — Cross-model Gold Lite DEV comparison, 2026-07-12)

- `scripts/gold_lite_portable_panel.py` adds a provider-neutral request, receipt, validation,
  comparison, and external handoff layer around the existing fixed Gold Lite packet. It records
  protocol compliance and pairwise agreement before human review, then can add exact rate,
  categorical Cohen kappa, and confusion counts after a complete human export validates.
- `scripts/codex_cli_model_bridge.py` runs one cold Codex structured-output request in an
  ephemeral read-only session with user rules/config ignored. `scripts/mlx_model_bridge.py` runs
  the cached scaffold-study MLX checkpoints one model at a time and records revision,
  quantization, chat-template mode, token use, and explicit Qwen no-thinking mode. The bridge
  forces Hugging Face and Transformers offline mode before loading the cached checkpoints.
  Codex CLI does not expose a hard output-cap flag in this runtime, so the portable max-token
  field is recorded as advisory for Codex and enforced only by providers that support it. New
  receipts also record the bridge script SHA; the first 2026-07-12 receipts predate that additive
  provenance field and remain untouched.
- `tests/v1/test_gold_lite_portable_panel.py` covers frozen provider-neutral requests, external
  schema-visible prompts, strict/no-repair parsing, request and passage hash binding, partial
  failure preservation, pre/post-human comparison behavior, Codex isolation flags, and the local
  study-model allowlist.
- The first cross-model DEV report configures 11 model records and admits 142 atom votes. It has
  no human-accuracy result. This tooling does not change package source, rules, config, the public
  CLI, or the acceptance gate.
- Verification: **522 passed**, Ruff check and 93-file format check clean, mypy `--strict src`
  and compileall clean, **97% source branch coverage**, repeat finalization byte-identical, and
  clean-wheel v0.2/v1 install verification green.

### Fixed (Gold Lite model-panel provenance hardening, 2026-07-12)

- Anthropic and portable receipt validation now reconstructs the canonical request from the
  packet and panel manifest before accepting a response hash. Pre-execution prompt, schema,
  model/runtime, parent, or token-setting edits therefore fail closed even when the raw receipt
  faithfully hashes the edited request.
- Aggregation and comparison require the model-review artifact schema and rerun the nested review
  validator, including packet/rehearsal identity, candidate availability, and passage hashes.
  Supplied scoring targets are labelled neutral references; a reviewer string alone never creates
  human-gold provenance. Markdown denominators derive from the packet.
- The Codex bridge preflights request/receipt/event path collisions before execution, preserves and
  audits the JSONL stream, and rejects any tool-bearing item. Future receipts hash the actual
  transmitted wrapper prompt. Manifest-controlled portable paths must match generated direct
  children and cannot escape the run directory.
- The MLX bridge resolves each model to an already-cached commit snapshot before loading it
  offline, hashes the actual chat-template-rendered input, and records `stream_generate`'s native
  finish reason plus prompt/generation token counts. Future combined artifacts retain these
  runtime fingerprints; historical receipts remain unchanged and linked by their raw hash.
- Regression coverage includes mutated-but-hash-bound requests, nested provenance drift,
  model-identity/source duplication, path traversal, incomplete/tool-bearing Codex lifecycles,
  rerun collision, dynamic packet sizes, and pinned MLX stream metadata. Historical runs 03–08
  replay byte-identically. Comparison v0.2 preserves all v0.1 votes/metrics, marks 4/11 records
  runtime-provenance complete and seven `legacy-incomplete`, and repeats byte-identically.
  Verification: **532 passed**, Ruff check and 93-file format check clean, mypy `--strict src`,
  compileall, **97% source branch coverage**, and clean-wheel v0.2/v1 verification green.

### Added (v1 Phase 4 — PILOT-001 DEV prototypes, 2026-07-10)

- `scripts/pilot001_premise_granularity_run04.py` plus focused tests: a deterministic
  coarse-to-fine replay over the 16 v1.5.0 raw-neutral DEV claims. The S1 sentence and
  S1+S2 adjacent-window variants are experiment tooling only; neither changes package
  code or the frozen rules resource. Both were rejected after zero recoveries, one
  regression, and new gold-supported → CAL-`contradicted` cases.
- `scripts/pilot001_a1_imperative_run05.py` plus focused tests: a full-trace replay of a
  structural A1 prefix guard. The candidate changes exactly two false imperative stops
  and no other verdicts on the 98-claim DEV set. It is sign-off evidence, not a package
  landing; `sentence_type()` and `cal-rules-v1.5.0` remain unchanged.

### Fixed (wheel verification hygiene, 2026-07-11)

- `scripts/verify_install.py` now deletes setuptools' generated `build/` tree before
  building the verification wheel. This prevents deleted package-data files from a prior
  build from leaking into a nominally clean wheel. The installed-v1 smoke also asserts
  that the wheel contains exactly `cal-rules-v1.5.0.yaml` and no retired rules resources.
- Verification after this change: **491 tests**, Ruff check/format, mypy strict,
  compileall, **97% source branch coverage**, and the rebuilt-wheel v0.2/v1 surface checks
  all green.

### Changed (v1 — `cal-rules-v1.5.0`, Decision H absence-route Stage 1)

See DECISIONS.md § 2026-07-07. Rule **logic** changed; **thresholds unchanged** from v1.4.0.

- **Intake provenance join (D1):** every passage now carries its source `trust_level`
  (`primary`/`secondary`/`background`) in `source_meta`, joined at `v1/intake.py` from the bundle's
  `source_profiles`. This is the provenance the eligibility rules read at verdict time.
- **Eligibility suppression loop:** `VerdictRules.apply` wraps the unchanged Decision-C classifier
  (`_classify_once`) in a loop that refuses to let an ineligible source (non-`primary`, **P1**) or a
  self-negating passage on a negated claim (**P2**) solo-drive a terminal adverse degree; the
  suppressed contradiction falls through to the best remaining eligible signal, or to
  `not_checkable/no_entail_signal`. New invariant: eligibility gates adverse decisions; ineligible or
  self-agreeing evidence may flag, never decide. An absent `trust_level` (a non-bundle passage) is
  treated as eligible, so pre-D1 behaviour is preserved.
- **Rule 6d** now flags `background`-contributing positive verdicts (the provenance field finally
  arrives); the impossible `"fictional"` trust tier is removed.
- **`cal-rules-v1.4.0.yaml` → `cal-rules-v1.5.0.yaml`** (SHA-256
  `99be5382f0e058a4a514bda96c532f28ad43c11c272864e643b9ccbb8e7d6251`). All 27 goldens regenerated
  (`audit_config_hash` only; **zero verdict flips**). Stage 2 (bundle-relative absence route) was
  measured on the run-03 dev set and **held** (net-negative weighted κ). Dev-only per Decision G;
  the confirmatory gate stays a fresh blind packet.

## 0.2.0 - 2026-06-13

Claim Audit Lab v0.2 stabilizes the public package and binds the C-B research-apparatus
path to one deterministic policy.

### Added

- Packaged contract resources and demo fixtures loaded through `importlib.resources`.
- Clean-wheel verification for `--help`, `demo`, and `audit-bundle`.
- `ClaimType.unclassified`, with native extraction skipping it and C-B audits returning
  `not_checkable`.
- Public `audit_claims(...)` orchestration and shared contract serialization helpers.
- Claim-scoped C-B evidence and separately linked counterevidence.
- Default human-readable reports from `audit-bundle`.
- `--audit-run-id` and `--audited-at` for byte-identical audited bundles.
- Threshold, strong-wording, counterevidence, config-drift, classifier-parity, and
  reproducibility tests.

### Changed

- Replaced duplicate classifiers with one governed priority:
  prediction, scope, causal, comparative, credential, capability, numeric,
  interpretive, unclassified.
- Consolidated tokenization, stemming, stopwords, date/number handling, and trigger
  vocabularies.
- Bound C-B audit intake to the exact frozen `cal-rules-v1.2.0` profile.
- Defined the support signal as `max_support - 0.3 * max_counterevidence`, clamped to
  `[0, 1]`.
- Froze candidate, partial, sourced, and false-caution boundaries at `0.40`, `0.55`,
  `0.80`, and `0.85`.
- Made linked counterevidence prevent a clean `supported` verdict.
- Made strong-wording suppression require the same trigger in direct evidence and no
  conflicting counterevidence.
- Replaced `ClaimAssessment.suggested_rewrite` with populated
  `rewrite_guidance: list[str]`.
- Regenerated checked-in examples and documented scores as supplied-evidence signals,
  never truth probabilities.
- Made Ruff formatting part of the release gate.

### Removed

- Dead `AuditConfig.strictness`.
- Cross-module use of private audit helpers.
- Redundant direct `rich` dependency.
- Internal phase-number language and stale workspace paths from public output.

### Verification

- 213 tests pass.
- Ruff lint and formatting, strict mypy, and compileall pass.
- Source branch coverage is 96%.
- A clean wheel passes `--help`, `demo`, and `audit-bundle`.
- Checked-in examples regenerate byte-identically.
- The synthetic Harness -> Evidence Bundler -> Claim Audit Lab round trip passes.
- The sealed 98-claim pilot replay is byte-identical with pinned run metadata.

Research qualification remains open. Blind calibration is `0/98`; human verdicts remain
primary until the documented agreement, kappa, adverse-recall, and per-condition error
gates pass.

## 0.1.0 - 2026-05-05

Initial CLI-first public release.

- Added deterministic supplied-evidence claim auditing.
- Added Markdown and plain-text draft loading.
- Added YAML and JSON evidence-bundle loading.
- Added conservative claim extraction and evidence matching.
- Added support labels, risk labels, rule flags, Markdown reports, and typed JSON.
- Added `claim-audit audit`, `claim-audit demo`, and the first C-B `audit-bundle` path.
- Added two fictional example families and validation-inspired IQ/OQ/PQ records.
- Added MIT licensing and public package metadata.

Known v0.1 limits included no source discovery, no live model calls, no web UI, no
research calibration, and no regulated-compliance claim.
