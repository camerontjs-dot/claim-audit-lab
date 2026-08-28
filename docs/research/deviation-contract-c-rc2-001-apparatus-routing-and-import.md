# Apparatus Deviation — Contract C RC2-A D-001

## What changed

Two execution-only corrections were required after preregistration:

1. The newly introduced standalone workflow on the non-default research branch was not scheduled by GitHub. The identical producer job was therefore added to the repository's already-established `Public suite` pull-request workflow, gated to the RC2 branch.
2. The first scheduled producer job then failed before the experiment began because `python scripts/run_contract_c_rc2.py` did not place the repository root on Python's module search path, so the research-only `contract_c_rc2_research` package could not be imported. The corrected launcher adds only `PYTHONPATH=${{ github.workspace }}` for that command.

## When discovered

- Standalone-workflow routing issue: after commit `8d5e683a4b161100e599ab9c60a5917b7227a7bf` produced no scheduled run.
- Import-path issue: Public suite run `33136492004`, producer job `98737511255`, at the `Run real Contract-B to CAL producer experiment` step.

## Preserved failed run

Run `33136492004` / job `98737511255` is preserved as an apparatus failure. It successfully checked out the pinned repositories, installed dependencies, verified Contract B `1.2.0`, and demonstrated no CAL `src/` mutation relative to production `33a928db97316a3652d57df9cafb8ca240305233`. It then failed with:

`ModuleNotFoundError: No module named 'contract_c_rc2_research'`

No Contract-B experiment artifact was built, no CAL audit was executed, no RC2 candidate was projected, and no research gate was evaluated. The run therefore contributes no positive or negative scientific evidence about the primary claim.

## Scientific-impact assessment

The correction changes only CI routing/module discovery. It does **not** change:

- the primary claim;
- producer-gate definitions;
- repository production pins;
- RC1 predecessor pins;
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

Accordingly, the failed run is invalidated only as a decisive experiment run. The preregistered scientific apparatus remains unchanged.

## Corrected decisive-run requirement

A later run is decisive only if it again verifies all production pins and `git diff --exit-code 33a928db97316a3652d57df9cafb8ca240305233 -- src`, then successfully reaches the real Contract-B build/intake/audit before evaluating the producer gate.
