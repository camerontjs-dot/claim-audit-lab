# RC7E Semantic Capability Envelope

Status: **POST-HOC ANALYSIS OF FROZEN EVIDENCE**

This document does not alter the RC7E apparatus, cohort, accepted scientific run, or terminal disposition. It decomposes the already-accepted RC7E result into a capability map. It is not an independent evaluation and must not be counted as a new held-out result.

## Frozen evidence basis

- accepted scientific run: `33448511982`
- scientific run head / held-out cohort freeze: `0ba6a30d4168f92198cd18443ce290b666761987`
- apparatus freeze: `05f6570cbfc46aad7941b791aa7345209494da69`
- immutable RC7E evidence commit: `34e9bcafad2c63c9b0761ffc456532344bc75b88`
- artifact: `9779020469`
- artifact digest: `sha256:983de37ca9c9f0c55a8b610e526d84e186f333311ed7529494974b212f090459`
- RC7E terminal disposition: `MORE_NON_LLM_INSTRUMENT_RESEARCH_JUSTIFIED`

## Capability vocabulary

The envelope deliberately avoids a single scalar claim that CAL "understands X% of language."

- `SUPPORTED_AT_DIMENSION_LEVEL`: all tested gold instances of the dimension were observed and authorized with no false authorization of that dimension. This does **not** establish atom-level semantic correctness outside the tested cohort.
- `PARTIAL`: the dimension is observable but one or more tested gold instances were missed before or during authorization.
- `OBSERVABLE_ONLY`: the portfolio detects the semantic structure, but the frozen authority layer has no jurisdiction to authorize that dimension as a proposition.
- `SCOPE_UNSAFE`: the semantic structure is highly observable, but current scope/assertion handling converts observations into false authority often enough that authorization is unsafe.
- `UNOBSERVED`: no tested direct proposal instrument observed the gold dimension.
- `UNEVALUATED`: reserved for semantic capabilities not exercised by the cohort.

## Frozen dimension-level envelope

| Dimension | Gold cases | Proposal hit | Authorized hit | False proposal dims | False authorized dims | State |
|---|---:|---:|---:|---:|---:|---|
| attribution | 3 | 3/3 (1.000) | 0/3 (0.000) | 0 | 0 | `OBSERVABLE_ONLY` |
| comparison | 4 | 0/4 (0.000) | 0/4 (0.000) | 0 | 0 | `UNOBSERVED` |
| conditional | 4 | 4/4 (1.000) | 0/4 (0.000) | 0 | 0 | `OBSERVABLE_ONLY` |
| coreference | 4 | 4/4 (1.000) | 0/4 (0.000) | 3 | 0 | `OBSERVABLE_ONLY` |
| event_ordering | 4 | 0/4 (0.000) | 0/4 (0.000) | 0 | 0 | `UNOBSERVED` |
| exception | 10 | 10/10 (1.000) | 10/10 (1.000) | 0 | 0 | `SUPPORTED_AT_DIMENSION_LEVEL` |
| permission | 18 | 13/18 (0.722) | 10/18 (0.556) | 0 | 0 | `PARTIAL` |
| probability | 8 | 8/8 (1.000) | 8/8 (1.000) | 1 | 0 | `SUPPORTED_AT_DIMENSION_LEVEL` |
| quantifier | 16 | 16/16 (1.000) | 15/16 (0.938) | 0 | 0 | `PARTIAL` |
| quantitative | 14 | 14/14 (1.000) | 11/14 (0.786) | 3 | 0 | `PARTIAL` |
| role_binding | 25 | 25/25 (1.000) | 23/25 (0.920) | 53 | 20 | `SCOPE_UNSAFE` |
| subclass | 8 | 8/8 (1.000) | 8/8 (1.000) | 0 | 0 | `SUPPORTED_AT_DIMENSION_LEVEL` |
| temporal | 8 | 8/8 (1.000) | 8/8 (1.000) | 1 | 0 | `SUPPORTED_AT_DIMENSION_LEVEL` |

## Interpretation

### Strong observation / bounded authority

`exception`, `probability`, `subclass`, and `temporal` are supported at the **dimension level** on this cohort. This is intentionally narrower than claiming complete semantic competence.

### Observable but not yet authority-bearing

`attribution`, `conditional`, and `coreference` were all detected in every gold case, but the frozen RC7E authority layer does not authorize those dimensions. This is positive measurement evidence, not a defect to be patched by simply widening jurisdiction.

### Partial jurisdictions

`permission`, `quantifier`, and `quantitative` are partially recovered. Permission is the clearest remaining bounded semantic residue: 13/18 gold permission dimensions were observed and 10/18 were authorized. Quantifier and quantitative dimensions were widely observed but lost some recall during authority filtering.

### Scope/assertion failure

`role_binding` is the central RC7E safety failure. The portfolio detected all 25 gold role-binding cases, but also proposed role binding in 53 cases where it was not a gold dimension and authorized it falsely in 20 cases.

The repeated pattern is a locally valid predicate/argument observation embedded under another semantic operator: quantification, probability/modality, permission/deontic language, conditionals, attribution, exceptions, comparison/quantity constructions, or related scope. The measurement may be locally correct while the narrator-level assertion is not warranted.

This motivates a distinct scope/assertion-status layer between semantic observation and semantic authority.

### Genuine measurement blind spots

`comparison` and `event_ordering` were missed in all four tested gold cases each. These are not primarily authority-filter failures in RC7E; the tested portfolio lacked a bounded instrument that proposed those dimensions.

## Layered competence model

RC7E supports treating semantic competence as a vector:

1. **Accessible** — untouched raw source reaches the instrument.
2. **Detectable** — the instrument recognizes that a semantic structure exists.
3. **Reconstructable** — entities, predicates, polarity, quantities, relations, and arguments are recovered correctly.
4. **Scoped** — the observation is placed under the correct assertion/embedding operator.
5. **Composable** — multiple semantic structures combine without laundering one into another.
6. **Stable** — meaning-preserving transformations preserve the representation and meaning-changing transformations alter it.
7. **Authorizable** — the source warrants exposing the proposition downstream.
8. **Residual-aware** — unresolved structure remains explicit instead of being silently coerced.

RC7E shows that stages 2 and 7 must not be collapsed.

## Safety preference

For CAL, false authorization is more damaging than bounded abstention. A successor should therefore optimize lexicographically:

1. zero or near-zero unsafe authorization and false authorized dimensions;
2. explicit unresolved status for unsupported scope;
3. only then recover additional recall.

A candidate that increases recall while increasing unsafe authority does not qualify for promotion.

## Smallest successor experiments

1. **RC7F-A — Assertion Status and Semantic Scope Jurisdiction**
   - Hold local predicate/argument content approximately constant.
   - Vary narrator assertion, negation, attribution, epistemic modality, deontic modality, quantification, conditional antecedent/consequent, exception, and temporal embedding.
   - Test whether a bounded scope layer can preserve the observation while blocking unauthorized narrator-level assertion.

2. **RC7F-B — Comparative / Quantitative Relation Measurement**
   - Add a bounded specialist for `greater_than`, `less_than`, `equal_to`, threshold, ratio, and comparative constructions.
   - Keep quantity detection separate from relation direction and attachment.

3. **RC7F-C — Event-Event Temporal Ordering**
   - Distinguish event-event order from SUTime-style temporal-expression recognition.

4. **RC7F-D — Deontic Composition**
   - Test permission/obligation with exception, membership, temporal validity, and nested scope.

## Contract-E relationship

RC7E raises a structural analogy with Contract E's authority-basis work: authority should be bound to the exact domain, operation, scope, target, and basis rather than inferred transitively from a nearby artifact.

That analogy is **not** evidence that semantic warrant and operational authorization are one contract.

For CAL semantic interpretation, the relevant question is whether a source warrants proposition `P` under a particular assertion/scope context. For Contract E, the current research question is whether actor/request `A/O/T` is operationally authorized under an authority basis.

A future shared abstraction may exist, but the next discriminating work should first test the semantic scope/warrant primitive independently and only then evaluate whether it composes cleanly with Contract E.
