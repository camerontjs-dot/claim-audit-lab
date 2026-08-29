# RC0B Candidate B: bounded additive state/receipt

Research-only mechanism. It does not alter CAL semantic measurement, thresholds, rules, Contract B/C, or production traces.

Inputs:
- retained evidence identities;
- fixed per-passage semantic measurements;
- source trust fact;
- explicit proposition-specific assessment execution/value;
- explicit policy identity;
- execution outcome.

Derived receipt:
- source fact and assessment state remain separate;
- participation per evidence item is retained/deciding/residual/excluded/unresolved;
- policy effects are named;
- execution failure is recorded separately from terminal epistemic state;
- distributed partial evidence is retained with aggregation=unresolved when no validated composition rule exists;
- exact causal-basis labels are emitted only after one-at-a-time removal replay; otherwise causal structure is unavailable.

Frozen shadow policies for the strong counterfactual:
- ALLOW_PRIMARY_OR_SECONDARY: primary and secondary may decide when eligibility is performed-positive.
- PRIMARY_ONLY: only primary may decide when eligibility is performed-positive.

No trust level is itself a proposition-specific assessment. not-performed, not-applicable, performed-unknown, performed-adverse, performed-positive, and failed remain distinct.
