# CAL V1 independent-judge candidate RC0

Status: research candidate. Not a production change and not V1 readiness.
Programme: CAL #205. Execution gate: CAL #206. Preparation: Draft PR #207 at `4f3eaadf39e2f8f9229298ce2e39dbeee8eea102`.

This directory is the research candidate. It does not import, subclass, or wrap `FixtureProbe`. The frozen kit under `research/cal_v1_independent_judges_rc0_20261004/` stays byte-for-byte. `src/`, package metadata, and existing tests stay untouched.

## Question

Can a four-lane catalogue read one immutable claim/evidence envelope, seal each lane before any other lane's conclusion is visible, and synthesize with uncalibrated toy weights so that scoped synthetic claims are decided without dropping scope, while missing evidence, unresolved polarity, attribution, and material conflict stay non-deciding?

## Catalogue

Every arm-C case dispatches the same four processes. A lane that does not understand the claim returns `not_applicable`. It does not stop the others. Unimplemented families stay `UNIMPLEMENTED` in `CATALOGUE.json`. They are not treated as not applicable.

| Process | Role | What it may decide | Dependence |
|---|---|---|---|
| `kernel_legacy` | relation | Only the frozen kernel's authored strict comparison or direct event order | Frozen semantic implementation `caa0048f8f511ec3c4aa1ce713766f2219a04bc1` |
| `original_relation` | relation | Scoped strict comparison, including polarity and role inversion | `comparison_relation.py` |
| `scope_guard` | guard | Constraint finding only. Weight zero. Violation blocks a decision | `constraint_guard.py` |
| `event_order` | relation | Closed positive event order | `event_order.py` |

The relation lane and the guard do not import each other. They are still same-author deterministic checks written against the same exposed seeds, so they are not statistically independent errors. The guard is not a second vote. No learned model, prompt, or provider is used. Toy policy weights in `POLICY.json` are rational fixtures, not calibrated production weights.

## Arms

- Arm A, routed kernel. Only `kernel_legacy` runs. Authoring refusal is explicit. The other three processes are `not_run`, which is not `not_applicable`. The kernel's own conclusion is the arm result. It is not passed through the toy threshold as a single weight-1 vote.
- Arm B, shared-lossy counterfactual. The same four lane implementations and the same code budgets receive one shared rewritten envelope. The rewrite strips a leading year, a property span between the direction and the measure, a trailing all/some age-group quantifier, and a leading allegation wrapper. This arm is not a production design.
- Arm C, original input. The same four lanes receive the original bytes on separate processes. Late synthesis runs only after every stdout receipt is sealed.

Where A and C differ, attribution is confounded: the instruments differ as well as the routing. Where B and C differ, the instruments and budgets match and the input loss differs.

## What this candidate does not claim

Natural-claim usefulness, blind gold, empirical weight calibration, provider diversity, Contract C reconstruction, or promotion of any historical family. A pass on the fourteen exposed seeds is the preregistered architecture discriminator only.
