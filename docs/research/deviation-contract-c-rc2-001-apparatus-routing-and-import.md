# Apparatus Deviations — Contract C RC2-A D-001 / D-002

## D-001 — workflow routing and RC2 launcher import

### What changed

Two execution-only corrections were required after preregistration:

1. The newly introduced standalone workflow on the non-default research branch was not scheduled by GitHub. The identical producer job was therefore added to the repository's already-established `Public suite` pull-request workflow, gated to the RC2 branch.
2. The first scheduled producer job then failed before the experiment began because `python scripts/run_contract_c_rc2.py` did not place the repository root on Python's module search path, so the research-only `contract_c_rc2_research` package could not be imported. The corrected launcher adds only `PYTHONPATH=${{ github.workspace }}` for that command.

### When discovered

- Standalone-workflow routing issue: after commit `8d5e683a4b161100e599ab9c60a5917b7227a7bf` produced no scheduled run.
- Import-path issue: Public suite run `33136492004`, producer job `98737511255`, at the `Run real Contract-B to CAL producer experiment` step.

### Preserved failed run

Run `33136492004` / job `98737511255` is preserved as an apparatus failure. It successfully checked out the pinned repositories, installed dependencies, verified Contract B `1.2.0`, and demonstrated no CAL `src/` mutation relative to production `33a928db97316a3652d57df9cafb8ca240305233`. It then failed with:

`ModuleNotFoundError: No module named 'contract_c_rc2_research'`

No Contract-B experiment artifact was built, no CAL audit was executed, no RC2 candidate was projected, and no research gate was evaluated. The run therefore contributes no positive or negative scientific evidence about the primary claim.

## D-002 — frozen RC1 control working directory

### What changed

The first corrected real RC2 run (`33136632726`, producer job `98737952427`) successfully executed the production-boundary experiment and the RC2 representation tests, but the frozen RC1 regression step reported `15 passed, 1 failed` because the unchanged RC1 test `test_independent_projector_uses_only_candidate_package` opens `contract_c_rc1_research/independent_projector.py` using a repository-root-relative path. The workflow had invoked the frozen test file from the RC2 repository root.

The correction changes only the invocation directory: run the unchanged frozen RC1 test suite from `_predecessor/cal-rc1` with that frozen checkout as `PYTHONPATH`.

### Preserved failure

Run `33136632726` remains preserved. The failing RC1 control was:

`FileNotFoundError: contract_c_rc1_research/independent_projector.py`

This was not a changed semantic assertion. The same run had already completed the real B -> CAL experiment, produced the RC2 artifact set, and passed `9/9` RC2 representation/firewall tests. The RC1 rerun result is therefore treated as an apparatus invocation failure pending a clean rerun, not as evidence that the RC1 semantic falsifier changed behavior.

## Scientific-impact assessment

Neither correction changes:

- the primary claim;
- producer-gate definitions;
- repository production pins;
- RC1 predecessor pins or RC1 test bytes;
- the frozen mixed-format input fixture;
- Contract-B version or semantics;
- CAL production code or audit semantics;
- semantic obligations;
- candidate profile rules;
- falsifiers;
- thresholds;
- destination-policy firewall controls;
- ablation criteria;
- expected outcomes.

The changes are limited to CI routing, Python module discovery, and the working directory from which unchanged frozen RC1 tests execute.

## Corrected decisive-run requirement

A later run is accepted as the complete RC2-A receipt only if it:

1. verifies all production and predecessor pins;
2. verifies `git diff --exit-code 33a928db97316a3652d57df9cafb8ca240305233 -- src`;
3. successfully executes the real Contract-B build/intake/audit and RC2 producer gate;
4. passes the RC2 representation/firewall suite;
5. passes all 16 unchanged frozen RC1 semantic falsifier tests from the frozen RC1 repository root;
6. uploads the complete frozen evidence artifact set.
