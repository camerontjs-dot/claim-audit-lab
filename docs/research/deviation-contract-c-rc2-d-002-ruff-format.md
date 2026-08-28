# Contract C RC2-D Deviation 002 — Ruff formatter-only mismatch

## Discovery

After the eight `ruff check` findings from deviation 001 were corrected mechanically, the next full RC2-D workflow again completed the frozen production checks, decisive sweep, and independent assertions successfully.

Second-run identity:

- branch head: `d728a3008daea8cf9718d3bd9950c6fac7ae1d5a`;
- workflow run: `33192976575`;
- job: `98922875829`;
- artifact: `9694535862`;
- uploaded artifact digest: `sha256:674d9acb5786796db37c3b643bac7a37b64d825bd9dca8cb8311a722202b5ca5`;
- receipt-file SHA-256: `a953a14b8bf9a5bd9cf9060e7fb58c868df9b15c8b578d88f13a1090c4eca5fa`.

The receipt-file SHA-256 is identical to deviation 001's first-run receipt.

## Completed checks

- frozen production blob checks: success;
- no `src/` production diff: success;
- decisive attribution sweep: `all_controls_passed: true`;
- independent research assertions: `6 passed`;
- `ruff check`: `All checks passed!`.

## Failure

`ruff format --check` reported that three research files would be reformatted:

- `research_contract_c_rc2_d/sweep.py`;
- `research_contract_c_rc2_d/validator.py`;
- `tests/research/test_contract_c_rc2_d_attribution.py`.

The formatter requested only expression wrapping/compaction. It did not report a lint rule, test, semantic assertion, receipt, or production failure.

## Classification

Apparatus/code-hygiene deviation only.

## Allowed correction

Apply exactly the formatter-specified expression wrapping/compaction. Do not change any semantic input, expected output, receipt value, validator condition, causal classification, policy mutation, threshold, acceptance criterion, or falsifier.

A fresh full workflow remains required.

## Scientific effect

None observed. The decisive receipt remained byte-identical to the first run before this format-only correction.
