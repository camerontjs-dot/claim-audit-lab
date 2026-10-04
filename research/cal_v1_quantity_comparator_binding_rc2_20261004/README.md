# CAL V1 quantity comparator binding RC2 preparation

Research infrastructure for CAL #210. This directory is frozen before comparator implementation.

Contents:

- `PLAN.md` — scientific boundary and ordering.
- `SOURCE_POOL_SELECTION.json` — exact preselected source identities and calibration/held-out roles. Raw bytes are not frozen here.
- `DEVELOPMENT_CASES.json` — exposed comparator-binding development cases.
- `comparator_contract_tests.py` — evaluator/interface test and weak-control self-test.
- `LOCAL_HANDOFF.md` — local source-custody and implementation procedure.
- `FREEZE.json` — SHA-256 bindings for preparation files, excluding itself.

A green self-test does not establish comparator correctness or natural-claim usefulness.
