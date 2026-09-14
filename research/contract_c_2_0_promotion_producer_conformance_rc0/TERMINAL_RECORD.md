# Terminal Record — Contract C 2.0 Promotion Producer Conformance RC0

Terminal disposition: **`SUPPORTED_C2_PROMOTION_PRODUCER_CONFORMANCE`**

Classification: Draft Research / production-promotion conformance evidence. This record does not authorize production CAL merge, Contract C merge/release, Decision Engine production support, Contract E / Authorization, or execution.

## Exact frozen authorities

CAL producer authority:

- exact CAL V1 RC1: `a902621e8baea3063dddd7f92ba975aade305464`;
- engine blob: `636734fd1341d2ae721ae9697c7ac7652b89eecc`;
- relation blob: `e9e9401c92ee11d25a50dbc36e80aeb4c4cd220d`;
- unchanged prior RC2 materializer blob: `f9b22abff561081fb22ade8d5d7227dbdb870d72`.

Apparatus production-promotion subject:

- Draft PR #98;
- exact locally-qualified C2 promotion head: `b42c827acb0a9fe65353354d709add0e27bab307`;
- local promotion workflow run: `34804396671`;
- candidate public compatibility version: `2.0.0`;
- integrity-bearing wire profile: `contract-c-successor-candidate-a-rc2-research`;
- current global discovery during this pre-merge gate: released Contract C `1.0.0`.

Exact frozen RC2 lineage present in the promotion subject:

- wire-spec blob: `960df40619f0fbeb630c4ea8b1042ed3a293a7a3`;
- schema blob: `45ebaa1e5b7342422b4d6a19f897e72de4bb148f`;
- frozen RC1 reference validator: `03dbb5b774af523d8e6235bca86b18af5ddad5b0`;
- frozen RC2 reference validator: `ad5ed3ac71a8f8680188beb363c9d952c9922b15`;
- production RC2 adapter blob: `1d2ecd228cde807138013c33c8675c3003421d3c`;
- public C2 wrapper blob: `bb5a381f89828ddc92adfdedcc4e9d98069f436d`;
- released C1 version-registry blob preserved during qualification: `6e805e274f8b1f491bf0c10735a46962ab91d2d4`.

## Frozen experiment

The experiment was frozen before execution in this order:

exact CAL base -> exact prior materializer -> preregistration -> evaluator -> freeze receipt -> workflow execution.

Frozen experiment blobs:

- preregistration: `1a4cfec752ac4180308f08f19f4aa822653b7b6f`;
- materializer: `f9b22abff561081fb22ade8d5d7227dbdb870d72`;
- evaluator: `a3a6073645819cdb8d58fbbd55a3213c2eff780e`;
- freeze receipt: `ae935f10af2adfc4b8dc1ac41fd67c53d924ddca`.

Executed workflow head:

`30225c83e34d819e9c086bfb6783f83f11a7cc78`

## Decisive execution

- workflow run: `34804586160`;
- job: `103853825583`;
- workflow conclusion: `success`;
- artifact: `10332677500` (`contract-c-2.0-promotion-producer-conformance-rc0-34804586160`);
- artifact ZIP digest: `sha256:05bd3534b1e7569c7cf063cdbf73467032fed829a64a3bb4d7ffab6ef5fcb419`;
- frozen CAL RC1 replay controls: **14 passed**;
- exact-authority and bounded-mutation checks: PASS;
- compose-only materializer boundary: PASS;
- exact production-candidate authority checks: PASS;
- preregistered producer evaluation: PASS;
- evidence package/upload: PASS.

The evaluator emitted:

- `research_disposition = SUPPORTED_C2_PROMOTION_PRODUCER_CONFORMANCE`;
- `failures = []`;
- `producer_gate_satisfied = true`.

## Preregistered checks

All nine terminal checks were true:

1. `all_cases_production_reference_equivalent = true`;
2. `all_terminals_match_cal = true`;
3. `all_basis_groups_match_compose_only_derivation = true`;
4. `all_cases_deterministic = true`;
5. `weak_flat_control_killed = true`;
6. `unsupported_reason_not_aliased = true`;
7. `production_identity_constants_exact = true`;
8. `premerge_global_discovery_remains_c1 = true`;
9. `candidate_version_is_noncanonical_c2 = true`.

## Exercised legitimate CAL result shapes

The evaluator exercised thirteen result contexts:

- single support;
- single refutation;
- two independently sufficient supports;
- support plus neutral residual;
- minimal mixed support/refute;
- alternative-joint mixed `(S1 OR S2) AND R1`;
- symmetric alternative-joint mixed `S1 AND (R1 OR R2)`;
- four-way alternative mixed;
- completed no-deciding result;
- direct-event-order support;
- direct-event-order refutation;
- direct-event-order reporting-scope no-deciding result;
- exact `UNSUPPORTED_SEMANTIC_FAMILY` result.

For every exercised case, the production C2 adapter and exact frozen RC2 reference produced equal canonical objects, equal canonical bytes, equal local result-set identities, and equal whole-object hashes. Emitted terminal state matched CAL public terminal state, emitted basis groups matched deterministic compose-only minimal-basis derivation, and deterministic replay was stable.

Representative preserved counterexample behavior:

- alternative-joint result retained exactly `{{R1,S1},{R1,S2}}`, rather than the falsified flat `{R1,S1,S2}` form;
- symmetric alternative-joint retained exactly `{{R1,S1},{R2,S1}}`;
- four-way mixed retained all four co-minimal support/refute pairs;
- unsupported semantic family retained exact `UNSUPPORTED_SEMANTIC_FAMILY`, empty basis groups, and only `non_polarized / residual` participants.

## Evaluator discrimination

The old flat mixed strategy remained distinguishable and was killed on the alternative-joint controls.

Replacing the exact unsupported-family terminal reason with `no_deciding_relation` produced a different local result-set identity and different whole-object hash, demonstrating that the production profile does not silently alias those public states.

## Interpretation

Observed:

- `unchanged_materializer_preserved = true`;
- `new_cal_semantic_judgment_required = false`;
- `production_adapter_matches_frozen_rc2 = true`;
- `producer_gate_satisfied = true`;
- `independent_consumer_gate_satisfied_against_production_head = false` at the time of this run;
- `contract_c_2_released = false`;
- `production_promotion_merge_authorized = false`.

The smallest supported conclusion is therefore:

> Exact frozen CAL V1 RC1 can produce the exercised Contract C 2.0 promotion-profile handoffs through the already-qualified RC2 materialization without adding a new semantic judgment, and the exact production adapter preserves the frozen RC2 public object semantics and identities for those cases.

This is producer conformance for the exact promotion head only. It does not substitute for the separately required independent-consumer production-profile gate.

## Nonclaims / next gate

This record does not establish:

- independent-consumer conformance against exact production head `b42c827...`;
- completed 1.0/2.0 compatibility/adversarial matrix;
- Decision Engine C2 production support;
- canonical C2 discovery or release;
- CAL semantic correctness outside the exercised supported families;
- Evidence Bundler retrieval/completeness quality;
- Contract E / Authorization;
- execution authority.

The next justified Contract C promotion gate is a **production-profile independent-consumer conformance test using the already-frozen independent Consumer B unchanged**, with exact promotion head `b42c827acb0a9fe65353354d709add0e27bab307` as the producer/authority subject. Do not rebuild or retune Consumer B for this gate.