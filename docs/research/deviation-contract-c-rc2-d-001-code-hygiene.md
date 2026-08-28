# Contract C RC2-D Deviation 001 — Post-evidence Ruff failure

## Discovery

The first code-bearing RC2-D workflow completed the frozen production-identity checks, the decisive attribution sweep, and the independent receipt assertions successfully, then failed only in the research-code hygiene step.

Frozen first-run identity:

- branch head: `3b3f37ed2948d990657badcf5efff5f8db7997f4`;
- workflow: `Contract C RC2-D rule-family attribution`;
- run: `33192646035`;
- job: `98921758366`;
- artifact: `9694405647`;
- uploaded artifact digest: `sha256:796bd94d22ccc28a5d9aa94c47a6255c294096d1ac83d34e9266ff613d2ab194`;
- receipt-file SHA-256 printed by the workflow: `a953a14b8bf9a5bd9cf9060e7fb58c868df9b15c8b578d88f13a1090c4eca5fa`.

## Scientific steps that completed before the failure

The frozen sweep reported `all_controls_passed: true` for all ten encoded controls and exercised all six preregistered families.

The dedicated independent assertion file completed `6 passed in 0.17s`.

The workflow also verified the frozen `tests/test_rules.py`, `rules.py`, and `policy.py` blobs and verified no diff under production `src/` relative to the frozen production-semantic SHA.

## Failure

`ruff check` reported exactly eight code-hygiene findings:

- two import-order/format findings (`I001`), one in `research_contract_c_rc2_d/sweep.py` and one in the research test;
- six line-length findings (`E501`), all in `research_contract_c_rc2_d/sweep.py`.

`ruff format --check` did not execute because `ruff check` exited non-zero first.

No production vector, mutation outcome, receipt semantic, causal classification, policy value, threshold, expected verdict, acceptance criterion, falsifier, validator rule, or artifact result failed.

## Classification

Apparatus/code-hygiene deviation only.

The first-run scientific receipt is preserved as evidence but is not being presented as a fully green decisive workflow.

## Allowed correction

Only apply the mechanical formatting/import-order changes identified by Ruff. Do not alter:

- frozen inputs or expected production outcomes;
- causal classifications;
- receipt fields or dependency semantics;
- policy identity or policy mutations;
- validator logic;
- acceptance/falsification criteria.

A fresh full workflow is required after the mechanical correction.

## Scientific effect

None expected. If the corrected run changes any scientific output or control result, that change must be treated as a new material deviation rather than folded into this record.
