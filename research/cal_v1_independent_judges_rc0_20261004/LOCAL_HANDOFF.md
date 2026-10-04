# Local agent: CAL V1 original-input independent judges

Execute CAL #206 under the product decision in #205. Live GitHub plus this pinned preparation kit is the entrypoint; do not reconstruct the task from old kernel-only V1 summaries.

## Bootstrap

Inspect the live issue/PR state first. Use the exact preparation commit recorded on #206. Make an isolated worktree from it, not a dirty main or another worker's tree. The control is CAL `64b6c7702696c851057c1cf0b2c105b1c81db543`. Preserve all source/product and historical apparatus bytes.

From repository root:

```sh
KIT=research/cal_v1_independent_judges_rc0_20261004
python3 "$KIT/verify_kit.py"
python3 "$KIT/contract_tests.py" --selftest
```

These are preparation checks only. Stop on a kit hash mismatch. They do not install CAL or test semantic correctness.

Read `PLAN.md`, `INVENTORY.md`, `RC0_PROTOCOL.md` and `SEMANTIC_CASES.json`. Reconcile actual catalogue gaps and shared dependencies. The historical broader family roadmap is CAL #121; it is typed research lineage, not automatic runtime registration.

## Work

Implement a separate research candidate in a new directory, for example `research/cal_v1_independent_judges_candidate_rc0_20261004/`. Freeze the candidate before the decisive run. Do not import the fixture probe as your implementation. Keep an unchanged exact kernel lane, add an independent original-text semantic relation lane and a scope/polarity/measure lane, and give event-order the same dispatch opportunity. Each process reads originals and seals its own result before any comparison.

Implement the small `collect`/`synthesize` adapter specified by the protocol. Run:

```sh
python3 "$KIT/contract_tests.py" \
  --adapter research/cal_v1_independent_judges_candidate_rc0_20261004/adapter.py
```

Use isolated dependency environments. The frozen product declares Python >=3.11 with pydantic/PyYAML/typer; optional inference and development dependencies are separate. For full maintained regression follow the frozen repository's declared extras and record exact resolved versions/model artifacts. Do not run bare Python and silently assume all optional models exist.

Then run the REAL semantic and isolation experiment from the protocol, not only callback fixtures. Compare routed baseline, shared-lossy counterfactual and original-input candidate. Require correct decisions on scoped claims outside old authoring without losing qualifiers; preserve ambiguity, actual material conflict and missing-evidence abstention. No fabricated semantic judgments, blind-cohort claim, or empirical-weight claim from this synthetic test kit.

Record input bytes available/consumed, transformations/losses, actual process/provider isolation, independent first-pass conclusions, dependencies, applicability/warrant, fixed-policy weights, exclusions/conflicts and final result. Shared model or parser dependencies remain explicit. Original root/Contract A declaration authority is unchanged.

Run maintained regressions and hygiene within the isolated environment; distinguish missing dependencies, skipped coverage and true product failures. Preserve first failures; separately identify any apparatus successor. Do not patch frozen source, tests or expected results to get a pass.

## Return

A Draft Research PR containing exact freezes, commands/logs, full result table, immutable artifact pointers, weak-control discrimination, all failure/abstention causes, changes and non-claims. Choose #206's terminal disposition and update #205/#185/Apparatus#137. Do not merge, version, release, repin consumers or expand into all families. If mechanics pass but real utility does not, say so and identify the smallest next experiment. Work until that boundary without asking for routine continuation.
