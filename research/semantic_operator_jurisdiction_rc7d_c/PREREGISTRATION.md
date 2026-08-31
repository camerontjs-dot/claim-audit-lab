# RC7D-C — Semantic Equivalence and Authority Retest

## Classification

Post-reveal diagnostic hardening. Not context-free. No production authorization.

RC7D-C exists because RC7D-B's exact-JSON atom scorer was observed to conflate representational differences with semantic errors, including determiner-bearing predicate/object strings. The original RC7D-B result remains preserved and is not silently rewritten.

## Frozen prior evidence

- RC7D-B evidence commit: `c1b904654578ffd6b8cade9faf42fb6dbfe33933`
- RC7D-B validator freeze: `2e070cbcc48d80384ec71075998c142240a9042c`
- RC7D candidate operator bank: `b5b04485cb1e09f025017e25cd6d008e6c5030f6`

## Apparatus defect under test

Exact JSON identity is not a valid semantic-error metric when equivalent semantic values have no frozen canonical representation. In particular, strings such as `inspect the vessel` and `inspect vessel` must not be classified as semantically contradictory merely because one retains a determiner.

RC7D-C therefore freezes an explicit semantic-equivalence contract **before** constructing its new held-out cohort.

## Semantic-equivalence contract

For comparison only. This does not alter preserved source or operator output.

1. Unicode NFKC, lowercase, trim terminal punctuation, collapse whitespace.
2. Entity and class noun-phrase slots: remove one leading `a`, `an`, or `the`.
3. Predicate slots are represented as `lemma + object/complement`. Remove one leading `a`, `an`, or `the` from the object/complement after the lemma.
4. Subclass `child` and `parent` are noun-phrase slots and use rule 2.
5. Quantifier value, permission status, polarity, exception identity, temporal relation, probability category, and quantitative category are exact symbolic values.
6. No synonym substitution, stemming beyond the already-typed predicate lemma, singular/plural conversion, word-order change, inference, inheritance, or paraphrase equivalence is allowed.
7. Quantitative evidence surface is provenance, not semantic identity. Semantic comparison uses quantitative category plus normalized numeric/proportional value where the operator supplies one. A surface string alone cannot create semantic equivalence.
8. Two atoms are equivalent only if kind and every semantic slot are equivalent under these rules.

## Authority-gate hardening candidate

A validator v2 will be frozen before the fresh RC7D-C cohort.

It may use prior RC7D-B counterexamples to harden only demonstrated generic failure classes:

- do not authorize modifier leakage into population/predicate/class slots;
- epistemic probability requires an epistemic construction, not merely the noun/adjective `probability` in an unrelated object name;
- unseen modifier markers must fail closed when they intervene inside a proposed semantic slot;
- proposal rejection never deletes the proposal or source.

The validator may not inspect RC7D-C gold labels.

## Fresh cohort

After validator v2 and equivalence contract freeze, create a new held-out cohort containing at minimum:

- determiner-preserving versus determiner-free semantically equivalent atoms;
- quantifier + exception with unseen exception markers;
- quantifier + epistemic modifiers, including modifiers embedded between population/event components;
- non-epistemic uses of words such as probability/chance/likely as names or descriptions;
- permission + temporal and permission + exception paraphrases;
- subclass + permission paraphrases;
- role binding with irrelevant modifiers and negation paraphrases;
- no-authority controls containing domain vocabulary;
- mixed-semantic cases with at least two legitimate dimensions;
- same-dimension internal conflicts;
- composition controls.

## Architecture lanes

1. `single_router_validated_v2`
2. `broadcast_validated_v2`
3. `broadcast_proposals_only`
4. `zero_authority_control`
5. `oracle_single_family_ceiling`
6. `oracle_multi_operator_ceiling`

All raw proposals and raw source remain preserved in all lanes.

## Multiple-implementation diagnostic

Retain the two independently coded deterministic quantifier readers. Compare them under semantic equivalence rather than exact JSON identity.

Disagreement may be a risk signal. Agreement is not authority and cannot bypass validator v2.

## Metrics

- proposal dimension recall/precision;
- authorized dimension recall/precision;
- semantically normalized typed-atom recall/precision;
- genuinely unsafe authorized atoms;
- false authorized dimensions;
- rejected and unresolved proposal counts;
- mixed-semantic authorized dimension retention;
- raw-source preservation;
- composition accuracy with oracle components;
- bank-size 2/4/6/8 unsafe-authority stress;
- quantifier duplicate error rate when agree/disagree under frozen equivalence.

Every reported unsafe atom must preserve both raw atom objects and the normalized comparison forms.

## Preregistered terminal states

### `PROPOSAL_AUTHORITY_ARCHITECTURE_SUPPORTED_WITH_BOUNDS`

All:

- raw source preservation = 1.0;
- broadcast proposal dimension recall >= 0.80;
- broadcast proposal dimension precision >= 0.97;
- broadcast validated atom precision >= 0.98;
- broadcast validated unsafe atom count = 0;
- broadcast validated false authorized dimension count = 0;
- broadcast validated semantic-dimension recall >= 0.65;
- broadcast validated mixed-semantic retained dimensions strictly exceed validated single routing;
- no increase above zero in unsafe authorized case rate from bank size 2 to 8;
- oracle multi-operator retention strictly exceeds oracle single-family retention;
- oracle-component composition accuracy = 1.0.

### `AUTHORITY_VALIDATOR_STILL_UNSAFE`

Any genuinely unsafe atom or false semantic dimension is authorized after semantic-equivalence scoring.

### `AUTHORITY_VALIDATOR_TOO_LOSSY`

Safety criteria pass but validated broadcast semantic-dimension recall < 0.65.

### `SPECIALIST_DISCOVERY_TOO_WEAK`

Broadcast proposal dimension recall < 0.80 with proposal dimension precision >= 0.97.

### `SPECIALIST_DISCOVERY_OVERCLAIMS`

Broadcast proposal dimension precision < 0.97.

### `COMPOSITION_DEFECT`

Oracle-perfect component composition accuracy < 1.0 or a coexist-only pair is collapsed improperly.

### `APPARATUS_INVALID`

Source mutation, gold leakage into validator, inconsistent equivalence implementation, or other apparatus defect invalidates the run.

Precedence:
`APPARATUS_INVALID` > `COMPOSITION_DEFECT` > `AUTHORITY_VALIDATOR_STILL_UNSAFE` > `SPECIALIST_DISCOVERY_OVERCLAIMS` > `SPECIALIST_DISCOVERY_TOO_WEAK` > `AUTHORITY_VALIDATOR_TOO_LOSSY` > `PROPOSAL_AUTHORITY_ARCHITECTURE_SUPPORTED_WITH_BOUNDS`.

## Claim limits

A positive result supports only this bounded deterministic proposal/authority architecture. It does not establish arbitrary-language coverage, fresh independent consumability, production readiness, or a need/lack of need for LLM machinery.
