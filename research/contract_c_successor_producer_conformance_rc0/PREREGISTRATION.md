# Contract C successor producer conformance RC0

**Classification:** Draft Research producer-conformance experiment. This is not a production CAL mutation, Contract C promotion, official version assignment, merge, release, tag, Decision Engine change, Contract E change, or operational authorization.

## Exact bases

CAL producer candidate:

- repo: `camerontjs-dot/claim-audit-lab`
- exact RC1 head: `a902621e8baea3063dddd7f92ba975aade305464`
- RC1 qualification: `SUPPORTED_BOUNDED_RC1_QUALIFICATION`

Apparatus successor candidate authority:

- repo: `camerontjs-dot/apparatus-contracts`
- Draft PR #91 exact candidate head: `242351af7214c23dce76edd06299f55c038cd3f0`
- candidate profile: `research-non-deciding-rc0`

Apparatus promotion qualification RC0:

- Draft PR #92 terminal: `INCONCLUSIVE`
- version class if promoted: `MAJOR`
- sole blocker: maintained or promotion-ready producer conformance for the exact successor was not established.

## Question

Can the existing qualified CAL RC1 producer boundary deterministically project legitimate CAL-owned state into the exact Apparatus Contract C successor semantics **without adding a new epistemic or causal judgment in the exporter**?

The current CAL RC1 package already exposes `project_contract_c_successor()`. This experiment tests that exporter as a system under test. It does not assume the exporter is correct because its output validates structurally.

## Existing producer boundary under test

The exact frozen RC1 `projection.py`:

- emits candidate sentinel `research-non-deciding-rc0`;
- maps `SUPPORTS -> support`, `REFUTES -> counterevidence`, all other traces -> `non_deciding`;
- derives causal membership from the terminal `AuditResult`;
- derives `causal_form` from conclusion/failure plus the number of causal IDs.

The exact source must not change during this experiment.

## Preregistered conformance controls

### C1. Direct candidate validity

For legitimate `audit(context)` results, the exporter output must validate against the exact Apparatus successor candidate without relabelling `non_deciding`.

### C2. Determinism

Same exact `AuditContext`, exact `AuditResult`, and exact semantic implementation identity must produce byte-identical canonical Contract C state and the same `result_set_id`.

### C3. Single deciding + neutral residual

A legitimate strict-comparison case with one SUPPORTS relation and one irrelevant/non-deciding passage must project:

- support contribution in causal basis;
- neutral contribution as residual;
- `single_necessary`;
- reported verdict `supported`.

### C4. Duplicate independently sufficient support

A legitimate case with two separately sufficient SUPPORTS passages must remain supported after ablating either passage individually. If the full projection emits both as causal `independent_sufficient_alternatives`, that multiplicity is supported by the producer's own composition behavior.

### C5. Minimal mixed pair

A legitimate case with exactly one SUPPORTS and one REFUTES passage must be `MIXED_RELATIONS`. Ablating either relation changes the terminal conclusion away from mixed. A two-member `jointly_sufficient` basis is therefore supported for that exact pair.

## Decisive non-invention falsifier

### F1. Mixed duplicate redundancy

Construct a legitimate CAL context containing:

- two distinct SUPPORTS passages, each separately sufficient for support;
- one REFUTES passage, separately sufficient for contradiction.

The full CAL result is `MIXED_RELATIONS`.

Then ablate each of the two support passages separately and rerun normal `audit()`.

If removing either one support passage still leaves one SUPPORTS + one REFUTES and therefore the same terminal `MIXED_RELATIONS`, that removed support passage is **not necessary** to the mixed terminal state.

Under released Contract C semantics, `jointly_sufficient` represents the demonstrated jointly required/co-sufficient form. Therefore an exporter that places all three contributions in one `jointly_sufficient` causal basis despite the ablation result adds unsupported causal necessity/multiplicity semantics.

This is a producer-conformance failure even if the resulting JSON validates structurally under the Apparatus candidate.

The experiment must preserve that result rather than narrowing the tested cohort after observation.

## Additional integrity controls

- exact CAL RC1 projection source blob must remain unchanged;
- exact CAL RC1 engine/relation source blobs must remain unchanged;
- experiment may add files only under this research directory plus its workflow;
- Apparatus candidate files are consumed from exact commit `242351...`;
- Contract-B index used for validation must be derived mechanically from the same CAL `EvidenceWorld`, not hand-edited to make validation pass;
- exporter output must preserve exact proposition/evidence references and result identity;
- no destination-policy or Authorization semantics may enter the exporter.

## Dispositions

- `SUPPORTED FOR PROMOTION`: all controls pass and F1 does not expose semantic invention.
- `FALSIFIED`: F1 or another preregistered safety/semantic control shows the exporter cannot safely represent the exact successor boundary.
- `INCONCLUSIVE`: apparatus/evaluator invalid or required evidence cannot discriminate.
- `SUPERSEDED`: exact producer or contract candidate changed before disposition.

A structurally valid Contract C object is not sufficient evidence for producer conformance.
