# RC2-C Deviation 001 — Research probe import-path failure

## Preserved failure

First code-bearing RC2-C head: `08392cf3ed9e7ce5d30ed2e4ce025089335ca690`.

Dedicated workflow run `33182944946`, job `98888539343`: **FAILED**.

Observed sequence:

- frozen `tests/test_rules.py`, `rules.py`, and `policy.py` blob checks passed;
- `git diff 33a928db97316a3652d57df9cafb8ca240305233 -- src/` passed;
- the dependency probe failed immediately at module import;
- no scientific control executed and no receipt artifact was produced;
- the independent research tests were skipped after the probe step failed.

Exact failure:

`ModuleNotFoundError: No module named 'research_contract_c_rc2_c'`

## Classification

**Apparatus-only import-path deviation.**

The workflow invoked `python research_contract_c_rc2_c/dependency_probe.py`. Python therefore made the research directory, rather than the repository root, the script import root. The probe then could not import its sibling package by absolute package name.

This failure does not support or falsify the RC2-C scientific claim because execution stopped before constructing the frozen vector or evaluating any preregistered control.

## Allowed correction

Change only the workflow invocation from file-path execution to module execution:

`python -m research_contract_c_rc2_c.dependency_probe`

Do not change the frozen vector, candidate receipt, independent validator, policy object/hash, expected production outputs, acceptance criteria, falsifiers, or any file under `src/`.

The failed run remains part of the research record.
