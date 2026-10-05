# Local handoff — CAL #212 quantity unit-boundary RC3

Work from live GitHub and the exact preparation PR/commit linked on #212.

## First: source custody

Do not modify unit judge code until all eight exact identities in `SOURCE_POOL_SELECTION.json` are retrieved once and frozen.

Record requested/final URL, UTC retrieval time, HTTP status, media type, raw byte count, SHA-256, transport tool/version, leak scan and partition. Preserve failures. No source replacement after observed behavior.

Commit `SOURCE_FREEZE.json` before implementation. Keep held-out bytes/labels outside the implementer's context through candidate/evaluator/policy freeze. If this ordering cannot be established, stop `INCONCLUSIVE_APPARATUS_INVALID`.

## Freeze the evaluator before candidate code

Translate `DEVELOPMENT_CASES.json` and the weak controls from #212 into an executable evaluator and commit/freeze it before changing the unit judge.

Required weak controls:
- percent-prefix substring matcher;
- numeric-only equality;
- unit stripping;
- percentage-point→percent collapse;
- basis-point→percent collapse;
- count/rate collapse;
- first-unit-wins;
- last-unit-wins;
- conversion without measure/role compatibility.

If the evaluator cannot kill all of them for their intended reason, stop `INCONCLUSIVE_EVALUATOR_NOT_DISCRIMINATING`.

## Candidate

After source freeze and evaluator freeze, create a new isolated candidate worktree. Use only exposed predecessor failures, the development matrix, and calibration sources. Do not inspect held-out bodies/labels.

Keep independent-judge mechanics and locked weights unchanged. Implement unit identity/dimension binding, not a HOL-14 string patch.

Candidate receipts must expose numeric values, exact unit spans, normalized unit identity, quantity role/dimension, measure, comparator/direction, time/scope, conversions, ambiguity and consumed spans.

## Calibration and held-out

If calibration changes the candidate, burn it and freeze a successor before held-out reveal.

Before held-out reveal freeze candidate and all judge bytes, evaluator, process catalogue, synthesis policy, and environment.

Expose held-out exactly once. Use identical successor judge bytes in R/B/C. Require zero critical false deciding results. Preserve all abstentions, misses and failures.

## Regression and handoff

Run maintained CAL suite in full `[v1]` environment. Preserve known frozen EPA scanner collision separately.

Return Draft Research PR with source freeze, evaluator/candidate/policy identities, weak-control results, development/calibration/held-out outcomes, all wrong decisions and abstentions, regression, deviations, observed evidence/inference/unknowns, #212 disposition, and next smallest V1 gate.

Reconcile #212, #205, #185, PR #211 and Apparatus #137. No merge, version, release, Contract A–E, Decision, tag or consumer-pin change.
