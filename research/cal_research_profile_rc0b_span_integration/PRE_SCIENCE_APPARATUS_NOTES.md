# RC0B Pre-Science Apparatus Deviation

## Preserved failed run

GitHub Actions run `34133179604` executed on frozen RC0B apparatus head `28cc7b10cfc11fa8d02103119d2ef1ceaae62319`.

Observed before failure:

- exact frozen dependency identity checks: PASS;
- production/frozen-parent mutation guard: PASS;
- frozen RC0 seam/falsifier suite: 12/12 PASS, zero unsafe results;
- RC0B candidate integration cases: **not executed**.

The RC0B evaluator stopped during exact Contract B validation with:

`FAIL: artifact path does not exist: research/cal_research_profile_rc0b_span_integration/run-output/contract-b-bundle`

The bundle had been created under the repository checkout, but the inherited Contract B validation helper launches the validator with the Apparatus Contracts checkout as its working directory. The new RC0B runner supplied a repository-relative bundle path, so the validator resolved it relative to the wrong working directory.

Artifact from the failed apparatus run:

- artifact ID: `10022913751`
- digest: `sha256:bfce137a324861188f47fa7074e001337f703d62afc3c5b5febcd1fac9e65c46`

## Classification

`PRE_SCIENCE_APPARATUS_FAILURE_RELATIVE_PATH`

This run is not evidence for or against the RC0A span candidate because Contract B validation failed before `_candidate_rows` and therefore before any controlled candidate integration case, weak role-misattachment control, or stale-span receipt control executed.

## Permitted repair

Only filesystem path resolution is changed for the successor execution. `integration_runner_r1.py` resolves the five CLI `Path` arguments to absolute paths and then invokes the frozen evaluator in `integration_runner.py` unchanged.

Frozen and unchanged across the repair:

- RC0 runtime;
- RC0 smoke helper;
- RC0A resolver;
- RC0B preregistration;
- RC0B cohort and expected outcomes;
- RC0B integration adapter;
- RC0B original evaluator logic;
- RC7F-B1;
- RC8J;
- Contract B/C authorities.

The first run that passes Contract B validation after this mechanical repair is the first eligible RC0B scientific execution.
