# CAL V1 Target Authoring / Conformance RC0 — Deviation 01

Date: 2026-10-01

## Trigger

The first RC0 qualification workflow failed after the decisive target-authoring/conformance matrix had completed successfully.

Exact failed execution:

- candidate head: `eef6c41832926aa6a3e68d0b65c313a75fff901d`
- workflow run: `36897815125`
- job: `110489146677`
- failed step: `Ordinary CAL regression and static checks`

## Observed failure

The step invoked:

```text
uv run pytest -q
```

Pytest collection then produced 35 existing-test import errors with:

```text
ModuleNotFoundError: No module named 'scripts'
```

The failure occurred during general repository regression collection. It did not occur in the target-authoring/conformance evaluator.

## Evidence before failure

The same exact run had already completed these steps successfully:

1. exact frozen trusted-target oracle checkout;
2. exact Evidence Bundler checkout;
3. protected CAL V1 boundary verification;
4. focused target-authoring unit controls;
5. frozen-oracle qualification matrix;
6. candidate distribution build;
7. clean-installed wheel author/conform exercise;
8. maintained regression model installation.

No terminal research disposition was assigned from this partial run.

## Diagnosis

The maintained public suite invokes pytest as:

```text
uv run python -m pytest -q
```

Using `python -m pytest` preserves the repository root on the module search path required by existing tests that import the repository-root `scripts/` namespace.

The RC0 research workflow used a different invocation. The observed failure is therefore classified as:

`QUALIFICATION_REGRESSION_IMPORT_ENVIRONMENT_DEFECT`

## Bounded correction

Change only the general regression/static-check command form to match the maintained public suite:

- `uv run python -m pytest -q`
- `uv run python -m ruff check src tests`
- `uv run python -m ruff format --check src`
- `uv run python -m mypy`

Do not change:

- target authoring or conformance implementation;
- focused unit controls;
- frozen-oracle qualification matrix;
- mutation cases;
- acceptance thresholds;
- frozen semantic implementation;
- DecompositionComposer;
- existing `run-bundle` behavior;
- parent-bound runtime;
- Contract C authority.

## Effect on interpretation

This correction does not repair or tune the scientific evaluator after seeing its result. It restores the ordinary regression gate to the repository's maintained invocation so that pre-existing tests can be collected.

The failed first run remains part of the evidence record. The full workflow must rerun from a new exact head before any research disposition is assigned.
