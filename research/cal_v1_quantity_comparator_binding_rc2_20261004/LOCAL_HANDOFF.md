# Local handoff — CAL #210 quantity comparator binding RC2

Work only from live GitHub and the exact preparation PR/commit linked on #210.

## Stop before implementation until source freeze exists

The source identities/partition roles are preselected in `SOURCE_POOL_SELECTION.json`.

First, in a clean source-custody worktree/process:

1. Download each exact selected URL once using a recorded transport command/user-agent.
2. Record requested/final URL, retrieval UTC time, status, media type, exact raw byte count and SHA-256.
3. Run leak/security/hygiene scans before any public commit. Do not publish tokens, credentials, session IDs, private URLs, machine paths or irrelevant dynamic secrets.
4. If the returned page contains incidental public client tokens outside all future evidence spans, preserve the original locally, create an explicit redaction/deviation record before publication, and bind both pre/post-redaction identities. Do not silently rewrite.
5. No source replacement after retrieval. A blocked/failed retrieval stays a result unless a predeclared fallback fetches the same canonical source.
6. Freeze `SOURCE_FREEZE.json` and source custody bytes/receipts before changing comparator judge code.
7. Keep held-out bytes/claims inaccessible to the candidate implementer until candidate/evaluator/policy freeze. Use a separate local agent/worktree/context if practical. Document the actual isolation boundary and any contamination.

If you cannot establish that ordering, stop `INCONCLUSIVE_APPARATUS_INVALID`.

## Development candidate

After the source freeze commit:

- start a new isolated candidate worktree from that exact freeze;
- use only PR #209 and `DEVELOPMENT_CASES.json` plus calibration material for implementation;
- do not inspect held-out bytes/labels;
- preserve RC0 fan-out/isolation/synthesis mechanics unless separately falsified;
- do not retune weights merely to cure the exposed false supports;
- implement a bounded comparator-aware quantity relation representation, not BJS/CMS-specific strings.

Candidate output for the frozen evaluator should expose enough state to verify comparator/orientation, measure, years/scope, consumed spans and ambiguity.

Run:

```sh
python research/cal_v1_quantity_comparator_binding_rc2_20261004/comparator_contract_tests.py --selftest
python research/cal_v1_quantity_comparator_binding_rc2_20261004/comparator_contract_tests.py --adapter <candidate_adapter.py>
```

The self-test is evaluator evidence only. The adapter pass is exposed-development conformance only.

## Calibration and held-out

Use calibration sources only after source freeze. If calibration reveals a new semantic defect, burn that calibration set and freeze a new candidate. Never patch after held-out reveal.

Before decisive held-out execution freeze:

- comparator candidate bytes;
- all other judge bytes;
- evaluator;
- process catalogue;
- synthesis policy/weights/thresholds;
- held-out manifest;
- environment/dependencies.

Then reveal held-out exactly once.

Require:
- zero critical false deciding results;
- comparator collision controls preserved;
- at least one non-quantity/event case so R versus C routing is observable;
- K/R/B/C only where meaningful, with same successor judge bytes in R/B/C;
- all wrong decisions and abstentions preserved.

## Regression

Install the declared `[v1]` extra and required model assets before claiming full regression. Classify the known frozen-source path-scanner collision separately; do not edit predecessor evidence bytes.

## Return

Draft Research PR only, with exact source freeze, candidate/evaluator identities, development and calibration outcomes, held-out first run, weak controls, regression receipt, deviations, and one #210 disposition.

Reconcile #210, #205, #185, PR #209 and Apparatus #137. No merge, version, contract change, release or consumer repin.
