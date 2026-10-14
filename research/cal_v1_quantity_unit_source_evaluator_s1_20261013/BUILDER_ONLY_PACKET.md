# CAL quantity/unit S1 — builder-only constrained task

**Not a runnable launch by itself.** The custodian must first freeze an exact executable V2 evaluator, valid successor source cohort and environment, and deliver this file in a mechanically allowlisted **copy-only** snapshot. Do not use this GitHub repository, PR, surrounding conversation or its checkout as the builder workspace. Do not paste any owner or custodian report into the builder.

## Objective

From the frozen RC2 quantity comparator baseline, create a **new research-only** quantity/unit adapter that can decide warranted percent/percentage-point/basis-point comparisons, refuse incompatible units/roles/measures/scope, and report its actual lexical and consumed spans. Preserve existing unrelated guards, architecture and synthesis policy. This is not CAL product promotion.

## Permitted information (materialized independently, never discovered by search)

Before calibration, the staging authority may provide **only** these pinned files, under neutral copy paths:

- `input/baseline/quantity_binding.py`: Git blob `05b1e7616cac8401656c8e777a6395f88d705a8c`, from comparator baseline `ce7348ae9a9e9b0fd03290e044516f3c302e06b0`.
- `input/baseline/candidate_adapter.py`: Git blob `559306c69b56ad1f9725193a6188f2e986cf3a3b` from that same baseline.
- `input/development/DEVELOPMENT_CASES.json`: Git blob `ac467ee96b879612ad686caa741afcfdcc4f7c00`; all 19 cases are **exposed development evidence**.
- `input/development/unit_contract_tests_v1.py`: Git blob `3cd87c389af76fd46225324050ce132279a83800`. Historical relation-oriented evaluator only; does **not** qualify lexical/consumed receipt offsets.
- `input/development/receipt_contract_tests_v2.py`: **PENDING**, required exact frozen blob and successful self-test before launch; no implementation change may outrun this freeze.
- `input/BUILDER_ONLY_PACKET.md`: this exact file, blob to be pinned by the custodian on its release.
- Any smallest required non-answer-bearing standard-library/runtime dependency must be approved as an exact blob/installed distribution and declared before launch.

Later **only when explicitly admitted by the custodian**: four calibration raw representations through exact pinned files `input/calibration/C01.bin` through `C04.bin`. The staging authority must cross-check against these Git blob identities before admission: `edcf44f41b9d0350f63ef7924158341c87d38c03`, `0a5b8cd02b2320bd03de2d14a903c353ff087ed5`, `c320b38b48ad9cdce5cd67e839a50c4ca3a74351`, `6d46235ee343a6612d687cf0dae2cda2d53ba3d9` respectively. Original transport/source metadata remains with custodian. Source calibration must not silently authorize claims about unsupported HTML, chart or PDF extractions.

The nine previously defined weak-control failure modes and the exposed development cases are authorized. No undisclosed expected answers are.

## Prohibited information and access

No GitHub browsing, network/DNS, git object store, repository clone, shared `main` worktree, historical issue/PR narratives, source-selection or source-freeze registers, source-fitness report, calibration labels beyond explicitly disclosed development/calibration, hidden/held-out source bodies, held-out labels, scoring scripts/results, answer-bearing history, prior candidacy attempts beyond the pinned baseline, home directories, other project worktrees, or inherited user/project chat context.

An absent path in sparse checkout is **not** proof of enforced denial. The trusted controller must expose only the allowlisted copy snapshot, with no repository credentials or network. Record attempts to access denied files/resources and stop on contamination.

## Required V2 receipt, separately for original claim and original authorized evidence

Preserve the historical top-level fields `status`, `relation`, `claim_unit`, `evidence_unit`, `claim_measure`, `evidence_measure`, `claim_years`, `evidence_years`, `conversion`, `ambiguity` for V1 development comparisons, but **do not reuse** V1's whole-sentence `*_unit_spans` as lexical spans.

Add `receipt_v2`:
```json
{
  "input_scope": {"claim": [0, 0], "evidence": [0, 0]},
  "quantities": {
    "claim": {"unit_tokens": [], "numeric_tokens": [], "quantity_role": "unknown", "measure": null, "comparator": "unknown", "time_scope": [], "consumed_spans": [], "conversion_available": [], "conversion_applied": null, "ambiguity_reason": null},
    "evidence": {"unit_tokens": [], "numeric_tokens": [], "quantity_role": "unknown", "measure": null, "comparator": "unknown", "time_scope": [], "consumed_spans": [], "conversion_available": [], "conversion_applied": null, "ambiguity_reason": null}
  }
}
```
Here `[0,0]` is **shape only, not an expected offset**. Actual `input_scope` is `[0,len(original_string))`, not a unit span. Every `unit_tokens` item has `{"span":[start,end],"normalized_identity":"percent|percentage_point|basis_point|unknown"}` with exact nonempty lexical slice in the original text, possibly multiple tokens. Every `numeric_tokens` item has `{"span":[start,end],"value":"..."}` bound to the quantitative measurement; years/clock times are not quantity values. `quantity_role` is distinct from lexical identity and uses the frozen development roles (`percent_level`, `percent_relative_change`, `percentage_point_change`, `basis_point_change`, `count`, `rate`, `unknown`, `not_applicable`). A complete receipt also binds measure/property, comparator including negation, time scope, actual consumed input spans, registered conversion identity/decision and unresolved reason. Spans are half-open offsets in decoded original-input Unicode codepoints; record source representation identity separately.

One evidence clause may contain multiple lexical units. Do not select the wrong measure because its number matches; endpoint arithmetic must retain both endpoints. Conversion cannot erase measure, role, comparator or time mismatch. Percent, percentage points and basis points are not string prefixes of one another. `pp` is unknown unless independently registered for this bounded instrument. For event-only input, return `not_applicable` with no quantitative measurements. Missing material state must refuse, not invent a default.

## Execution and stop

Use ordinary exposed development tests only. Record exact files read, writes, commands, environment/dependency versions, test failures, every changed line and input/output receipt. Do not access calibration until the custodian's separate release. If calibration changes the candidate, treat calibration as burned and issue an exact successor freeze **before** held-out reveal.

The builder must submit new candidate paths/bytes and an immutable candidate/evaluator/catalogue/policy/dependency/read-log freeze receipt to the custodian. It must **not** fetch, open, score, or receive the decisive held-out material. The custodian alone executes the authorized one-time reveal and comparison after verifying these identities, with identical successor judge bytes in all R/B/C arms. Any observed critical false deciding result ends the frozen attempt. No patch-and-rescore. No claim of blind qualification when the enforced information boundary or read logs are missing.

**Allowed builder terminal:** DEVELOPMENT_READY_FOR_CUSTODIAN_REVIEW, DEVELOPMENT_FAILED, CONTAMINATED_STOP, or BLOCKED with an exact cause. These are not scientific held-out dispositions.
