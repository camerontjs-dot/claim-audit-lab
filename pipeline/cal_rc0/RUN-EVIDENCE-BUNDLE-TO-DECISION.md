# Run an Evidence Bundle through CAL to Decision

This is the RC0 integration surface for exercising the maintained pipeline boundary:

```text
Contract B 1.2 evidence bundle
-> CAL RC0 strict-comparison semantics
-> Contract C 1.0
-> maintained Decision Engine supported-claim-verification policy
-> canonical Contract D 1.0
```

It is research/integration apparatus. It does not invoke Contract E, Authorization, execution, or a production effect.

## Inputs

The runner requires:

1. an exact Contract B 1.2 bundle directory;
2. a `cal-pipeline-rc0-targets-v1` declaration for the propositions CAL is asked to audit;
3. exact pinned checkouts of the RC7F-B1 and RC8J research machinery;
4. exact Contract B, C, and D authority checkouts;
5. the maintained Decision Engine checkout.

The Contract B bundle must include the factual-context extension:

`extensions/contract-b-factual-context-v1.json`

Only history links with the `declared_child` retrieval lane and review decision `accepted` participate in CAL. Retained/retrieved evidence is not silently treated as admitted evidence.

## Identity namespaces

Two identities that look related are deliberately distinct:

- `targets.case_id` is the upstream case identity used by the CAL target declaration;
- `bundle_manifest.bundle_id` is Contract B's own immutable bundle identity.

They are not required to be equal.

The cross-namespace binding is instead:

1. every target proposition ID must exist exactly in the Contract B claim set;
2. CAL consumes the exact corresponding Contract B claim text and accepted factual-context passages;
3. Contract C binds the actual Contract B version, bundle ID, and bundle hash;
4. Decision validates that exact Contract C and expected Contract B binding before emitting Contract D.

The first integration run incorrectly equated the target case ID with the Contract B bundle ID. That run is preserved as an apparatus failure. The current entrypoint keeps the namespaces separate.

## Command

The namespace-safe entrypoint is:

```bash
uv run python pipeline/cal_rc0/bundle_to_decision_entrypoint.py \
  /path/to/contract-b-bundle \
  --targets /path/to/cal-targets.json \
  --cal-root . \
  --cal-head <exact-cal-head> \
  --rc7fb1-root /path/to/exact-rc7fb1-checkout \
  --rc8j-root /path/to/exact-rc8j-checkout \
  --apparatus-b /path/to/exact-contract-b-authority \
  --apparatus-c /path/to/exact-contract-c-authority \
  --apparatus-d /path/to/exact-contract-d-authority \
  --decision-engine-root /path/to/exact-decision-engine-checkout \
  --semantic-implementation-sha <exact-cal-head> \
  --out-dir build/cal-bundle-to-decision
```

Normal authenticated CAL execution requires the existing CAL Pipeline HMAC key environment variables. `--test-keys` is permitted only for bounded integration tests.

The Contract D validator's runtime dependencies must also be installed. The CI harness installs the exact Contract D authority package, including its pinned `rfc8785==0.1.4` dependency, rather than bypassing validation.

## Outputs

For each targeted proposition, the output directory contains:

- exact Contract C JSON;
- exact canonical Contract D JSON emitted by the maintained Decision Engine CLI;
- Decision Engine input context and expected Contract B binding receipts;
- `BUNDLE-TO-DECISION-RECEIPT.json`, which records CAL conclusions, Contract C validation, Decision evaluation/effect, exact implementation pins, identity namespace handling, and the Authorization boundary.

The maintained policy used in RC0 is:

`decision-engine.contract-c.supported-claim-verification@1.0.0`

For a valid supported Contract C proposition it may emit:

```json
{
  "evaluation": {
    "state": "completed",
    "disposition": "clear"
  },
  "effect": {
    "type": "knowledge.add_verified_tag",
    "version": "1",
    "params": {
      "scope": "claim"
    }
  }
}
```

`clear` is a Decision result only. It is not Authorization and does not cause the effect to execute.

## Current supported CAL scope

The semantic decision path remains intentionally narrow:

- semantic family: `strict_comparison`;
- RC7F-B1 bounded deterministic comparison measurement;
- RC0A exact lexical-boundary resolution for lhs/rhs entities only;
- frozen RC0 non-entity span handling;
- frozen RC8J authority assessment;
- authenticated atom/proposition bindings;
- proposition-relative scoreless categorical composition.

A general raw-English claim-to-typed-target interpreter is still not part of this runner. The typed target declaration remains explicit.

## Full-pipeline smoke path

The dedicated workflow first constructs a real Contract B bundle through the Evidence Bundler RC0 handoff, then feeds that emitted bundle into this runner:

```text
Contract A fixture
-> Evidence Bundler retrieval/admission
-> exact Contract B 1.2
-> CAL
-> exact Contract C 1.0
-> maintained Decision Engine
-> exact Contract D 1.0
```

The workflow deliberately stops there. No Contract E call is made.
