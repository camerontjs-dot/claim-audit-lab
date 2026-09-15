# CAL V1 candidate reconciliation — preregistration

## Classification

Research Infrastructure / qualification reconciliation. This record does not change CAL production semantics, candidate source bytes, package version, Contract B/C authority, or release state.

## Question

Can exact frozen CAL V1 production-intent candidate `4d1b8909f7e2e52c33cf99632be8565f2685f948` remain the same qualification subject after the hosted Public suite failure, once the history-dependent migration test is executed with the Git history it explicitly requires?

## Frozen candidate authority

- repository: `camerontjs-dot/claim-audit-lab`
- candidate commit: `4d1b8909f7e2e52c33cf99632be8565f2685f948`
- candidate tree: `cb51b4e1e20292af2890257e995a8cd199f88a20`
- protected-main comparison commit: `32275a239b68af383a56bca843e28cbc1e343976`
- distribution: `0.6.0`
- runtime profile: `cal-v1-production-v1`
- qualified semantic implementation: `a902621e8baea3063dddd7f92ba975aade305464`
- qualified wheel identity recorded by promotion PR #111: `sha256:7092be03648afc8af18c54fb46c0c44915361fa6e55c3c08e054f12ea1381973`

No candidate file may be changed by this reconciliation.

## Observed contradiction entering this run

The hosted PR Public suite reached pytest and failed only at `tests/production/test_historical_golden_version_migration.py::test_historical_goldens_only_change_the_distribution_version` while the recorded full-history local qualification passed the historical public suite.

The failing test invokes `git show 32275a239b68af383a56bca843e28cbc1e343976:<golden>`. The ordinary Public suite used `actions/checkout@v4` without full-history checkout, so the comparison commit was not guaranteed to exist in the runner object database.

This is the hypothesis under test. It is not yet promoted into a terminal conclusion by this record.

## Fixed apparatus repair

The reconciliation workflow must:

1. check out this research-infrastructure branch with full Git history;
2. fetch the exact frozen candidate and comparison commit explicitly;
3. verify the candidate tree is exactly `cb51b4e1e20292af2890257e995a8cd199f88a20`;
4. create a detached worktree at exact candidate `4d1b8909...`;
5. verify `32275a2...` exists from inside that worktree before pytest;
6. execute the focused historical-golden migration test first;
7. only if that passes, execute the canonical public pytest, Ruff lint, Ruff format, and mypy gates using the repository's declared uv/spaCy environment;
8. never edit candidate bytes to make the run green.

## Falsifiers

The candidate cannot be reconciled by this apparatus repair if any of the following occurs after the required Git objects are confirmed present:

- the focused historical migration assertion fails;
- any CAL semantic/production test fails;
- Ruff or mypy fails for the exact candidate;
- the candidate tree does not match the frozen tree;
- execution requires modifying candidate bytes.

A runner/quota/platform failure before the candidate tests execute is an apparatus result, not a candidate result.

## Allowed terminal interpretations

- `RECONCILED_SAME_CANDIDATE`: exact frozen candidate passes the repaired history-aware apparatus; candidate identity remains unchanged.
- `CANDIDATE_FAILURE_REQUIRES_REVIEW`: a candidate test fails after apparatus prerequisites are proven available; do not patch in place.
- `APPARATUS_BLOCKED`: the repaired run cannot reach candidate testing because of runner/platform/apparatus failure.

This task does not authorize merge, release, tag creation, PyPI publication, semantic-family expansion, Contract C promotion, Decision execution, or MainFrame mutation.
