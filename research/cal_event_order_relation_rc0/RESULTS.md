# CAL Event-Ordering Proposition Relation RC0 — Results

## Classification

Draft Research Infrastructure / authority-to-conclusion evidence record.

No production `src/**` mutation, release, merge, tag, promotion, Contract B/C amendment, Decision Engine change, Contract E change, or operational authorization is supported by this result.

## Exact lineage

- parent Event-Ordering Authority RC0 head: `3a4b5f24f813843eae3857ed3444fb12b1cb8182`
- parent Draft PR: #96
- exact relation candidate freeze before cohort: `94ea0c7531aeb852520f34bd56393b63a4b5ac75`
- frozen `relation.py` blob: `70f9eff65330c4182b5ac3bd1a11d13059326ed6`
- frozen decisive `candidate.py` blob: `7e964d85eb80298b9b0d5b84eff32e14bed4b013`
- exact RC7F-C measurement head: `e8d33913db66ad21027dffdf731d50f7a0977c8f`
- RC7F-C implementation blob: `3e29b0e2ec5d9ba2d873d1584e76635147e421aa`
- exact RC8J head: `8e75c6782bb95c3763d06230b9c5df2b6af44054`
- RC8J implementation blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`

The candidate was frozen before the decisive cohort was added. A pre-science composition-identity seam is preserved in `DEVELOPMENT_NOTES.md`; the frozen decisive wrapper requires exact proposition-projection equality for all composed relations.

## Decisive execution

- run: `34433673413`
- apparatus conclusion: PASS
- artifact id: `10135390633`
- artifact digest: `sha256:7b0a07ba824dc97cce56fa167c4d7085b7e513ad5cfa99a8317d1c8f7c6144b1`
- scientific disposition: `SUPPORTED_WITH_BOUNDS`

Terminal summary:

```json
{
  "diagnostic_metadata_invariant": true,
  "mixed_order_invariant": true,
  "relation_control_failures": 0,
  "research_disposition": "SUPPORTED_WITH_BOUNDS",
  "unsafe_nonwarranted_deciding_relation": false,
  "weak_claim_id_control_valid": true
}
```

## OBSERVED

### Proposition-relative temporal relations

All six preregistered relation controls matched their expected bounded semantics:

1. same event pair + same direction -> `SUPPORTS -> supported`;
2. same event pair + opposite direction -> `REFUTES -> contradicted`;
3. swapped event pair + inverse direction -> `SUPPORTS -> supported`;
4. swapped event pair + same direction -> `REFUTES -> contradicted`;
5. different event pair -> `IRRELEVANT -> abstained`;
6. warranted negative-event atom -> `UNRESOLVED -> abstained`.

`relation_control_failures = 0`.

### Claim-ID-only weak seam is real

Using a deliberately weak consumer that verifies only atom authority and matching `claim_id`:

- the exact base proposition derived `SUPPORTS`;
- mutating the same-ID proposition direction derived `REFUTES`.

`weak_claim_id_control_valid = true`.

This demonstrates why claim identity alone is insufficient proposition identity.

### Exact proposition binding closed the tested substitution seam

A separately authenticated exact proposition receipt refused:

- `BEFORE -> AFTER` substitution under the stale receipt;
- left-event substitution under the stale receipt;
- exact claim-text mutation under the stale receipt;
- wrong proposition key;
- proposition MAC tampering;
- swapped-inverse proposition under the stale receipt.

A freshly issued exact receipt for the swapped-inverse proposition was accepted and correctly derived `SUPPORTS`.

### Portable event-atom warrant remained bound to the exact authority subject

The authenticated event warrant refused stale replay after:

- temporal relation mutation;
- consistent proposal + field-warrant mutation;
- source identity substitution;
- claim identity substitution;
- atom identity substitution;
- wrong warrant key;
- warrant MAC tampering.

A producer attempt to issue a new warrant for a non-warranted changed case was also refused.

### Scoreless composition remained fail-closed

- `SUPPORTS + REFUTES` -> `abstained / mixed_categorical_relations`;
- reversing input order produced the identical conclusion and basis relation set;
- `SUPPORTS + IRRELEVANT` -> supported;
- `SUPPORTS + UNRESOLVED` -> `abstained / unresolved_categorical_relation`;
- composing relations derived against different exact proposition projections was refused;
- a caller-modified non-warranted deciding relation was refused.

### Scalar/diagnostic metadata remained causally inert

Adding diagnostic fields such as `score`, `confidence`, and `reader_agreement_count` outside the authenticated semantic projection did not change the derived relation.

The proposition, relation-derivation, and composition APIs expose no `score`, `confidence`, `threshold`, `channel`, or caller-supplied `relation_hint` parameter. A scalar argument on the temporal proposition constructor was rejected.

## INFERENCE

Within this bounded direct affirmative event-order fragment, CAL can carry a second semantic family through:

`measurement -> independent source completion -> RC8J semantic authority -> authenticated portable atom warrant -> authenticated exact proposition -> proposition-relative categorical relation -> scoreless fail-closed composition`.

The strongest evidence is not merely that the positive examples passed. It is that both demonstrated weak seams were separately closed:

1. source-disagreeing caller-stipulated semantics could be warranted by RC8J without independent source completion in the parent experiment; and
2. same-claim proposition substitution can change a temporal relation when exact proposition content is not authenticated.

The candidate blocks the tested versions of both attacks while preserving non-deciding `IRRELEVANT` and `UNRESOLVED` states.

## IMPORTANT LIMITS / ALTERNATIVE EXPLANATIONS

This is still a narrow synthetic/direct grammar. The result could reflect the simplicity of exact event tuples rather than robust temporal-language understanding.

Negative event semantics were intentionally withheld from deciding relation logic. Cross-passage event identity, temporal transitivity, coreference, reported-speech scope, event intervals, simultaneous/overlap relations, and evidence completeness remain untested.

The bounded HMAC mechanism establishes a research authentication boundary only. It does not establish production key management, issuer trust, rotation, revocation, or production cryptographic architecture.

## NOT ESTABLISHED

- arbitrary temporal language;
- negative-event proposition logic;
- cross-passage temporal inference;
- temporal transitivity;
- event coreference;
- source/evidence completeness;
- root / `all_of` composition;
- Contract C temporal projection;
- Decision Engine behavior on temporal Contract C outputs;
- learned/NLI participation;
- production CAL architecture;
- production authentication/key management;
- merge, release, tag, promotion, or operational authorization.

## Terminal disposition

**`SUPPORTED_WITH_BOUNDS`** for the exact bounded event-order proposition-relative relation architecture.

The smallest justified successor is a downstream conformance test: determine whether the existing Contract C 1.0 producer/validator and maintained Decision Engine can consume this second semantic-family conclusion without hidden strict-comparison assumptions or schema laundering. Do not change Contract C or Decision Engine to make the test pass before first observing the current boundary.
