# CAL Epistemic Methodology RC1A: Real-Execution Receipt Capture and Replay - Final Research Result

## Terminal result

**PRIMARY RESEARCH DISPOSITION: SUPPORTED FOR PROMOTION**

**ARCHITECTURE RESULT:** A bounded receipt/capture wrapper is sufficient for the frozen RC1A requirements around current CAL v1.

This is a research disposition and a bounded architecture finding, not production authorization. The stopping rule fired after the first bounded candidate cleared the frozen apparatus. No staged decomposition, CAL v2, or historical-v2 comparison was built.

## Exact identities

- starting live `main`: `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`
- branch: `research/epistemic-receipt-capture-rc1a-20260829`
- Draft research PR: `#33`
- evaluator freeze SHA: `9b0d03a830367dc527c94663187e51cebe56cd16`
- evaluator blob: `a0db04b322632d2d52dfb0bdf53824881d3e7b07`
- acceptance specification blob: `ada5214745cf3bc23ccc9b6ffb93fe60d885380d`
- regression manifest blob: `a639a78dcdcfaabed21669cbd3bf269797fefaf7`
- acceptance entry-point blob: `504c5b1957d1c6e57d689e4dfc55a82fe0bc9443`
- hosted research-workflow blob: `18ad092cab55278a853ac601a0d30a6e6bd940eb`
- frozen v1 trace-corpus tree: `7d6735da5f23f78efae479d3c99c1fd2f075f935`
- frozen Contract-B fixture tree: `5bcfa0a27877cb7ceebf22cd8960e907f6f92083`
- candidate SHA: `5133264a44b1ef395542b286f298188ec6bbe96a`
- candidate blob `docs/research/rc1a_candidate.py`: `782f4f7cf5635672b55fcb3e292db584ce5ba464`
- final research execution SHA: `5133264a44b1ef395542b286f298188ec6bbe96a`
- candidate scientific workflow run: `33270560829`
- candidate receipt artifact id: `9719975531`
- candidate receipt artifact digest: `sha256:365ae8b755633f85470e883123ab5848000fffdf117f8bd74f2fa7dcf10ad5b4`
- extracted candidate receipt JSON SHA-256: `c0d542958f1f22f09e55f85a734a5655270da47afa0d525b60d6ce0f8b7c7803`

The candidate SHA is also the terminal scientific execution SHA because the first bounded candidate satisfied the preregistered stopping rule. Later commits are evidence-record compression only.

### Protected production identities reverified by the frozen evaluator

- `src/claim_audit_lab/contracts/contract_c.py`: `d6b32a44ef11109fe0ee91efa212d3904badf58c`
- `src/claim_audit_lab/v1/configs/cal-rules-v1.13.0.yaml`: `ac8147f6624164e9081a4ec365cd3920c25df96d`
- `src/claim_audit_lab/v1/impl/aggregator.py`: `b1f9e2309ae3d024bc609b83cc546acb30be6e9b`
- `src/claim_audit_lab/v1/impl/entailer.py`: `aaf9415e74ec2f04357ecf5346491d92f3e2d0d3`
- `src/claim_audit_lab/v1/impl/retriever.py`: `279a287e10f5466b8d2985291080bc0183c72a52`
- `src/claim_audit_lab/v1/impl/rules.py`: `bc388d64a5a53db0d33610ab6ff84bd93a811b46`
- `src/claim_audit_lab/v1/intake.py`: `d8b304a4259ec128e656f07ca628d8a0a88ddd69`
- `src/claim_audit_lab/v1/models.py`: `755e0ef1757055905f3c8b76b7edc5e8ddc1fefd`
- `src/claim_audit_lab/v1/pipeline.py`: `dd67d0d35590d3052826ad697ce9fd11222fff6f`
- `src/claim_audit_lab/v1/runner.py`: `db53f49745876b6158da0c233fb80916bbeaabaf`
- `tests/fixtures/cb/evidence-bundle-minimal`: `5bcfa0a27877cb7ceebf22cd8960e907f6f92083`
- `tests/v1/fixtures/traces`: `7d6735da5f23f78efae479d3c99c1fd2f075f935`
- `tests/v1/test_pipeline_e2e.py`: `48a22cfab82ea0a2abd8d1c80d0da32a3dacd260`
- `tests/v1/testing/stubs.py`: `c7fa94569234caaf5f2134f672737097e5c70111`

Contract C remained unchanged on implementation blob `d6b32a44ef11109fe0ee91efa212d3904badf58c`; that exporter declares Contract C `1.0.0`.

## Frozen apparatus

### Successful execution cases

The normalized-request lane covered: supported; partially supported; unsupported; contradicted; not-checkable/no evidence; not-checkable/evidence but no entailment signal; conflicting evidence; filtered/non-deciding evidence; inference-shaped support; and exhaustive source-boundary/absence behavior.

Gate 13 separately loaded the frozen Contract-B fixture through the current `load_bundle` and `bundle_to_requests` path and required the exact resulting `AuditRequest` object to enter the wrapper and unchanged `run_audit` delegate.

### Failure-injection case

The wrapper-owned injector raised `RuntimeError("RC1A_INJECTED_WRAPPER_FAILURE")` at `pre_run`. Passing required actual injector traversal, zero `run_audit` calls, no normal trace, explicit execution state/stage/type/message, and no fabricated epistemic conclusion.

### Invariance surfaces

- semantic measurement: canonical JSON over `features`, `retrieval`, `entailment`, `support_signal`, and `negation_probe`;
- verdict: canonical JSON over the complete current `Verdict`;
- full trace: exact `AuditTrace.model_dump_json(indent=2) + "\n"` bytes;
- real-execution identity: wrapper returns the same `AuditTrace` object returned by the observed unchanged `run_audit` delegate, not a reconstructed copy.

### Causal replay

Without replay exact causal basis had to be unavailable. With replay, baseline plus one-at-a-time removals were required. Removing `p-1` changed `supported` to `not_checkable/no_entail_signal` and established necessity. Removing `p-2` left `supported` unchanged and therefore could not be marked necessary.

## Weak-control results

| Control | Expected defect | Observed failed gates | Result |
| --- | --- | --- | --- |
| W1 | RC1-style post-hoc sidecar does not prove real capture | Gates 1, 13 | rejected |
| W2 | source trust masquerades as proposition assessment | Gate 5 | rejected |
| W3 | terminal reason without typed assessment/participation | Gates 5, 6, 12 | rejected |
| W4 | causal necessity echoed without intervention | Gate 10 | rejected |
| W5 | policy identity logged without policy effect | Gate 7 | rejected |
| W6 | missing epistemic state silently defaulted | Gate 12 | rejected |

All six weak controls were rejected before candidate implementation at the designated freeze commit and remained rejected during the candidate run. No weak control cleared its forbidden property.

## Candidate result

| Gate | Result | Frozen claim established |
| --- | --- | --- |
| 1 | PASS | unchanged `run_audit` invoked; exact returned trace object preserved |
| 2 | PASS | direct/wrapped semantic measurements identical |
| 3 | PASS | direct/wrapped complete verdict identical |
| 4 | PASS | direct/wrapped full trace identical |
| 5 | PASS | six assessment execution/value states distinct, including actual assessment failure |
| 6 | PASS | deciding/residual/excluded/unresolved participation reconstructed |
| 7 | PASS | named policy counterfactual changes derived effect/participation with v1 semantics fixed |
| 8 | PASS | genuine execution failure distinct from completed epistemic non-decision and assessment states |
| 9 | PASS | distributed evidence retained with unresolved aggregation and no invented composition |
| 10 | PASS | exact causal necessity only after intervention |
| 11 | PASS | irrelevant metadata mutation invariant |
| 12 | PASS | missing epistemically meaningful state fails closed |
| 13 | PASS | exact current normalized v1 request boundary used, not post-hoc `emit_receipt(trace, supplied_state)` |

## Production invariance receipts

For every frozen success case the direct and wrapped identities were equal. Each cell below is `direct = wrapped`.

| Case | Semantic measurement SHA-256 | Verdict SHA-256 | Full trace SHA-256 |
| --- | --- | --- | --- |
| `supported` | `681e8553ffab4c515eece6b7f8ecf907f4fe8a340fedf01a63ae2fc668759c7f` | `a6d92747bb8865341371e04da8afa56999b7f38a83645d0109123b7c88f5f6ec` | `3aff857b68d1f989f828f8f570b13cfa97e71ad7da2261e0fb0a9dc6a1ff6442` |
| `partially-supported` | `8b71789236d817a62387487e294c1a260e13d782e88d761b2980c1fe95195486` | `ca399419a804ef7b68e613a896c1c4ae4bf240b80b1b4263f5d61aba0ff36ce1` | `be01af557a4a8c05186177b691ab8f189a986f90f7cf29c4ade69f9a8ef9b696` |
| `unsupported` | `05ccf3f0c85fdcd97ae0e05091f907e84eae7421ef07c5bec58d418b0abf988f` | `ff2ec77c22bbc4181e26464c5227c34d847a5c08a8dd6a427809f935ff87c8ba` | `aee61c836a68bc944b2907814d4afcc94129e104fa14b7bc19fb07a399818767` |
| `contradicted` | `b4a742621f0a8ff42518a303d08d5d30a1bfa94fab49564bec83391d08db885c` | `7d1587119ca738ab18332c302b5c763cf3f86dc49979dafdd705c851278284b7` | `f02eaf58a140494a7c9307c8d9f8b11a876cad455940da5554813164a04a479e` |
| `not-checkable-no-evidence` | `907b82322921008e8f6f2e3c9b7f9a028ec128b4142d7319791adf7a98dfc48a` | `c0dfab61b13a3cd65de90891aa8ac9ee2640bf797bba014f95fc42976bacf564` | `3225c6b938fa2d018b4d93424f614bfa7121dd02a7b6d8e04a3ec443c17de9dc` |
| `not-checkable-no-entail` | `23e341a228f5100dbe329da28aeac57617d255317653b499ba72b6b50e120b0f` | `e6ef2ca70eb817bc841c50ecdaea4f2dad0127fd80ace0b33404e89002c114de` | `189802d2be98ca37d167840cb415f8349e4625a5fe1b38d866dfc3bfc759e698` |
| `conflicting-evidence` | `ac76ad43a6f41bf031ba9cc5ba8ef64d3c80428ee552eb84f9703abc7fdf0c35` | `6151de5e5c3e696ecfdde4f4193380785a2a90a5961a0ae1a7f4376ab7a33054` | `b23c5e7294974db2d2cd402b00a51443aca13e553631e03c48e5a78b28ebc123` |
| `filtered-non-deciding` | `a26eadc7cc4e711db44d84d41a46a634e79ae8c262379c9dd72c1566eef1755f` | `e6ef2ca70eb817bc841c50ecdaea4f2dad0127fd80ace0b33404e89002c114de` | `13d835a78745518e93988e616b224b3bc63469fcc1e84b9134849399f47d19e1` |
| `inference-shaped` | `bc08237f1f949e38ea919b9785aad447da471db83c01dbc51604deb66557e602` | `9e06371bc760df34cfa544cf1cc0d69ec8f47131e38b641eab35518d854740d3` | `396029fe468e19fd6d1c331841b88c8e31bcbbe32ac2b7820d4053616c4f56ad` |
| `absence-exhaustive-source-boundary` | `bef93967d1d8ed312a97ef1a48122e7f2de21904b6eacb69eb3a9949fa4a4e59` | `74a8215c850bd3e815cde9bbe0ccb9ea047f2ff22c10543b6e3af9e781c9d99d` | `e48026333fc23e47871855e16aff8e767c38dc20000d727cb6030325b3d9fb52` |

Gate 1 was stronger than hash equality: the wrapped trace had to be the exact object returned by the observed `run_audit` call.

## Failure capture receipt

The injected wrapper failure recorded:

- execution state: `wrapper_failure`
- stage: `pre_run`
- failure type: `RuntimeError`
- message: `RC1A_INJECTED_WRAPPER_FAILURE`
- `run_audit` calls: zero
- normal trace: absent
- epistemic conclusion: absent

Frozen Gate 8 required this signature to remain distinct from successful CAL `not_checkable`, performed-unknown, explicit not-performed, and successful execution with unresolved aggregation. Gate 5 separately exercised an actual assessment exception and preserved `failed` as distinct from the other five assessment states.

## Falsification audit before acceptance

1. **Could the candidate pass without observing claimed state?** No for the frozen claim. Gate 1 observed real `run_audit`; Gate 5 required live assessor invocation and an actual assessor exception; W1 rejected a precomputed-trace sidecar.
2. **Could state be reconstructed from information supplied after execution?** The plan was supplied before execution, but performed outcomes were not. Outcomes were produced by an assessor invoked inside the wrapper call before receipt completion.
3. **Could trust metadata masquerade as assessment?** W2 failed; performed assessment remained independently executed.
4. **Could failure be relabeled from a completed run?** No. The injected path had to raise before `run_audit`, with zero calls and no trace.
5. **Could invariance hash the wrong surface?** The evaluator compared explicit semantic-measurement fields, complete verdict, complete trace, and separately required trace object identity. This does not claim invariance for nonexistent future fields.
6. **Could causal basis be inferred from participation?** W4 failed; causal basis was unavailable without replay, and replay required actual additional `run_audit` calls.
7. **Could unresolved aggregation hide invented composition?** Gate 9 required both passages retained, `aggregation = unresolved`, and `composed_result = null`.
8. **Small counterexamples:** reconstructed trace, skipped assessor/trust shortcut, silent assessment default, causal echo without replay, and policy-ID-only logging were all frozen discriminators.

The frozen apparatus already contained metamorphic/counterfactual evidence: policy counterfactual (Gate 7), removal intervention (Gate 10), irrelevant-metadata mutation (Gate 11), missing-state mutation (Gate 12), and W1-W6. No acceptance rule was added or loosened after candidate exposure.

## Deviations

- A local clone/precheck path was unavailable because the execution environment could not resolve external GitHub networking. Connected GitHub state plus hosted GitHub Actions were used instead. This occurred before freeze and did not alter the apparatus.
- An attempted MainFrame Conduit execution surface returned an MCP/SSE `404`; no Conduit task was created. Hosted GitHub Actions became the execution surface.
- The first branch-creation connector invocation used an unsupported argument shape and produced no repository mutation; the branch was then created from the explicit live `main` SHA.
- No post-freeze evaluator defect was observed. No frozen evaluator/spec/manifest/acceptance-test/workflow file was modified after freeze.
- The live comparison from base through the candidate showed additive-only changes: research apparatus/records, one research-only candidate module, and one acceptance test; no existing production file was changed.

## OBSERVED

1. Live `main` at task start was `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`, matching the predecessor production base.
2. Evaluator freeze occurred at `9b0d03a830367dc527c94663187e51cebe56cd16` before any RC1A candidate existed; the hosted freeze receipt recorded `candidate_present: false`.
3. W1-W6 were rejected before candidate implementation and again during candidate execution.
4. The first and only bounded candidate scientific commit was `5133264a44b1ef395542b286f298188ec6bbe96a`.
5. The candidate cleared Gates 1-13 without frozen-apparatus modification.
6. All ten direct/wrapped success cases had identical semantic-measurement, complete-verdict, and full-trace identities.
7. The wrapper-owned failure produced `wrapper_failure` at `pre_run` with explicit RuntimeError identity and no normal trace/conclusion.
8. All six assessment states and all four participation categories remained distinct.
9. Policy counterfactual, causal intervention, irrelevant-metadata mutation, fail-closed missing state, unresolved distributed evidence, and real Contract-B request-boundary checks cleared.
10. Contract C and all protected production objects retained their frozen identities.
11. RC1A scientific workflow run `33270560829` succeeded.
12. Public production suite run `33270560858` on the candidate SHA succeeded: pytest, Ruff check, Ruff format check, and mypy all passed.

## INFERENCE

For the exact current CAL v1 base and frozen RC1A requirements, the minimum RC0B epistemic state is observable/capturable from a thin research-only execution wrapper without changing `run_audit`, the v1 trace, semantic measurements, verdict logic, Contract B, or Contract C.

RC1's apparatus failure therefore does not imply that stronger execution decomposition is needed. RC1A supplied the missing real-capture evidence. The evidence does not justify a fuller staged pipeline.

## HYPOTHESES STILL LIVE

- A productionized bounded mechanism could take more than one packaging form, such as an opt-in wrapper or additive receipt service; RC1A did not choose among them.
- A concrete downstream consumer may eventually require state Contract C 1.0.0 cannot express, including generic performed-positive; that would require a separate compatibility experiment.
- Additional policies or richer causal/aggregation questions may require more state than RC1A froze.

## UNKNOWNS

- production deployment ergonomics, API ownership, persistence, migration, and operational observability;
- substantive correctness of a real assessor, as opposed to execution/value-state capture;
- downstream Contract C compatibility for the research receipt;
- any new multi-passage composition semantics;
- exhaustive behavior across every heavyweight model/runtime failure mode;
- sufficiency for future CAL releases or changed trace schemas.

RC1A used the current production regression architecture with deterministic retriever/entailer protocol adapters for reproducible wrapper-invariance testing. It does not claim exhaustive heavyweight runtime coverage.

## FALSIFIED ALTERNATIVES

- W1 RC1-style post-hoc supplied-state sidecar;
- W2 trust-as-assessment shortcut;
- W3 terminal-reason-only mechanism;
- W4 causal echo without intervention;
- W5 policy-ID-only logging;
- W6 silent epistemic defaults;
- synthetic/reconstructed trace as proof of real execution identity.

## ARCHITECTURE RESULT

**A bounded receipt/capture wrapper is sufficient for the frozen RC1A requirements around current CAL v1.**

No stronger decomposition is justified by RC1A.

## PRIMARY RESEARCH DISPOSITION

**SUPPORTED FOR PROMOTION**

This means only that the bounded capability demonstrated here is sufficiently supported to enter a separate production-promotion decision. It does not authorize a production merge.

## SMALLEST NEXT EVIDENCE-PRODUCING STEP

Do not run a broader architecture experiment. Open a separate production-promotion decision/EDR asking: **what is the smallest production change, if any, justified by RC0B + RC1A?** Compare only bounded additive packaging choices. Preserve unchanged v1 semantics and Contract C unless a concrete downstream incompatibility is demonstrated. Any production implementation must be a new, separately authorized production PR.

## Hosted CI status, separate from scientific disposition

- RC1A scientific workflow on candidate SHA `5133264a44b1ef395542b286f298188ec6bbe96a`: **SUCCESS**, run `33270560829`.
- Public production suite on the same candidate SHA: **SUCCESS**, run `33270560858`.

CI status is operational evidence and is not the disposition oracle.

## NON-AUTHORIZATION

RC1A does **not** authorize:

- production merge;
- CAL v2;
- historical-v2 promotion;
- Contract B changes;
- Contract C changes;
- Evidence Bundler changes;
- Decision Engine changes;
- model changes;
- threshold changes;
- rules/config changes;
- release/version changes;
- new aggregation/composition semantics.

The Draft research PR is an evidence record and must not be merged.
