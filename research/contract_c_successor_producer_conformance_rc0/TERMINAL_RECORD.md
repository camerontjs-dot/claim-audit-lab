# Contract C successor producer conformance RC0 terminal record

## Terminal disposition

**`FALSIFIED`**

The existing frozen CAL RC1 `project_contract_c_successor()` is not supported as a production/promotion-ready producer for the exact Apparatus successor candidate tested here.

This is a research disposition. It does not mutate CAL production, assign an official Contract C version, promote Contract C, merge, release, tag, change Decision Engine, or authorize execution.

## Exact lineage

CAL producer candidate:

- base: `a902621e8baea3063dddd7f92ba975aade305464`
- frozen projection blob: `9bc152275759304be03b84014c56bd434549a64a`
- frozen engine blob: `636734fd1341d2ae721ae9697c7ac7652b89eecc`
- frozen relation blob: `e9e9401c92ee11d25a50dbc36e80aeb4c4cd220d`
- decisive research head: `a4f2a767a242d92dca7daf7cf042c8e8d1d79e1f`

Apparatus authority:

- exact successor candidate: `242351af7214c23dce76edd06299f55c038cd3f0`
- candidate validator blob: `bbab0e94d56f2983ed6d5cc510bf26efa4a55e21`
- candidate schema-delta blob: `bdd511aac6a26fd0bdaa07c353a29757b478b283`

Decisive run:

- run: `34726677711`
- job: `103641897133`
- artifact: `10307489383`
- artifact digest: `sha256:c5189ac571ca6217bdd62ad30e8b3b72357f032491feda47bb1e8520c7779637`

Frozen CAL producer controls replayed: `14 passed`.

## Controls that passed

The exporter was not broadly broken.

Observed controls:

1. **Single deciding support + neutral residual**
   - legitimate CAL conclusion: `supported`;
   - output channels: `p1=support`, `p2=non_deciding`;
   - causal form: `single_necessary`;
   - basis: `p1` only;
   - output validated against the exact Apparatus candidate.

2. **Determinism**
   - same exact CAL context/result/semantic implementation identity produced byte-identical canonical output and identical `result_set_id`.

3. **Two independently sufficient supports**
   - full CAL result: `supported`;
   - ablating either support individually still produced `supported`;
   - exporter emitted both support contributions as `independent_sufficient_alternatives`;
   - exact candidate validation passed.

4. **Minimal mixed pair**
   - one support + one refute produced `MIXED_RELATIONS`;
   - support alone produced `supported`;
   - refute alone produced `contradicted`;
   - exporter emitted the two-member basis as `jointly_sufficient`;
   - exact candidate validation passed.

These controls show that the failure below is not explained by generic validator incompatibility or a universally wrong multiplicity mapper.

## Decisive falsifier

A legitimate CAL context contained:

- `p1`: SUPPORTS;
- `p2`: SUPPORTS;
- `p3`: REFUTES.

The full normal `audit()` result was `NOT_CHECKABLE / MIXED_RELATIONS`.

The exporter emitted:

- `causal_form = jointly_sufficient`;
- causal basis passages `[p1, p2, p3]`.

The resulting object was structurally valid under the exact Apparatus successor candidate.

Then normal CAL `audit()` was rerun after separately ablating each support:

- remove `p1`, retain `p2 + p3` -> still `MIXED_RELATIONS`;
- remove `p2`, retain `p1 + p3` -> still `MIXED_RELATIONS`.

Therefore each duplicate support is individually unnecessary to the terminal mixed state.

Released Contract C defines `jointly_sufficient` as the demonstrated jointly required/co-sufficient form. Marking all three passages as one jointly-sufficient causal basis therefore overstates causal necessity/multiplicity relative to CAL's own ablation behavior.

Preregistered check:

`exporter_avoids_unsupported_joint_causal_claim = false`

The evaluator disposition is therefore `FALSIFIED`.

## Why structural validation did not catch this

The Apparatus candidate correctly validates structural/reference integrity and the allowed causal vocabulary. It cannot infer whether a producer's chosen causal basis was actually warranted by the producer's epistemic/composition state.

This result therefore distinguishes:

- **contract structural validity:** PASS;
- **producer semantic attribution validity:** FAIL.

A valid Contract C object is not, by itself, evidence that the producer was entitled to assert its causal basis.

## Architectural implication

This is not yet evidence that the two-leaf `non_deciding` channel delta itself is wrong.

It does show that the current flat producer projection is insufficient for at least one legitimate CAL state. The mixed-redundant state has Boolean form equivalent to:

`(support_1 OR support_2) AND refute`

Current flat basis machinery cannot truthfully encode that state by simply placing all three contributions in one `jointly_sufficient` set. Choosing only one support+refute pair would instead create an artificial unique winner and discard the co-maximal alternative from the causal basis.

The next smallest discriminating question is therefore whether existing Contract C basis machinery can represent this alternative-joint structure without a schema change, or whether the successor needs a minimal causal-expression extension such as explicit alternative minimal basis groups.

Do not repair the exporter by selecting one arbitrary minimal pair.
