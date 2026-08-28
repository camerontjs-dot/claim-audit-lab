# RC2-A2 Deviation 001 — Post-pytest Ruff line-length failure

## Discovery

The first code-bearing RC2-A2 Public suite run, `33142053092` at head `cc26c986c8fe689f4f544212bc850b3a6624ff95`, completed the full pytest step successfully and then failed the Ruff step.

Observed pytest result:

- `991 passed`
- `5 skipped`
- `48 deselected`
- `7 warnings`

Observed Ruff failure:

- exactly three `E501` line-length violations in `tests/research/test_contract_c_rc2_a2_basis_parity.py`;
- lines 179, 574, and 687 in the run checkout;
- no scientific assertion, fixture expectation, branch classification, policy value, threshold, or falsifier failed.

Because Ruff failed, format and mypy steps were skipped by the workflow.

## Classification

Apparatus / code-hygiene deviation only. The decisive semantic tests themselves passed on the first run, but the PR is not treated as green because the complete required workflow failed.

## Correction allowed

Only wrap the three overlong lines. Do not alter:

- frozen vectors;
- expected branch identities;
- receipt fields or semantics;
- replay logic;
- policy values;
- mutation controls;
- acceptance or falsification criteria.

## Scientific effect

None expected. A corrected full workflow is still required before assigning a research disposition.

## Preserved evidence

The failed workflow run `33142053092` and head `cc26c986c8fe689f4f544212bc850b3a6624ff95` remain part of the experiment record.