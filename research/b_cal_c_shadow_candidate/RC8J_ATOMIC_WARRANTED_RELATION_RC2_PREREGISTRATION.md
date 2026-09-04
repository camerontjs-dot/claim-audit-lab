# RC8J Atomic Warranted-Relation RC2 Preregistration

## Classification

Draft Research Infrastructure. This is a bounded successor to the falsified RC1 authority-binding architecture. It does not authorize production CAL changes, Contract C projection, Decision Engine policy, release, promotion, or merge.

## Frozen parent and dependencies

- frozen RC1A head: `6a01e5be07c0b2ddc11aeeb3974f3221eccc9c0e`
- frozen RC1 head: `598968205a5371323989f972442fb9820ba19b35`
- frozen RC8J commit: `8e75c6782bb95c3763d06230b9c5df2b6af44054`
- frozen RC8J implementation blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`
- production main reference: `32275a239b68af383a56bca843e28cbc1e343976`

RC1 and RC1A remain byte-unchanged. RC8J remains byte-unchanged.

## Parent failure to preserve

RC1 accepted `case` and an independently supplied `authority_result`. RC1A showed that a stale `WARRANTED` result for `A > B` could be replayed against a mutated `A < B` atom with the same atom identity. Frozen RC8J independently rejected the mutated atom as `FIELD_VALUE_MISMATCH:comparison_direction`, yet RC1 derived `REFUTES` and produced a decided `contradicted` conclusion.

The successor must not repair or reinterpret that result. It must make the replay path structurally unavailable or fail the experiment.

## Research question

Can CAL safely derive a proposition-relative categorical relation from an already-constructed semantic atom when the exact same immutable case snapshot is both:

1. evaluated by the exact frozen RC8J authority gate; and
2. consumed by the categorical relation operator,

without accepting a caller-supplied authority result, scalar strength, confidence, threshold, support/refutation channel, or relation hint?

## Candidate architecture

```text
caller semantic case
        |
        v
freeze/deep-copy exact case snapshot
        |
        +--> exact frozen RC8J(snapshot)
        |       |
        |       +-- non-WARRANTED --> refuse relation construction
        |
        +--> WARRANTED
                |
                v
        derive relation from SAME snapshot
                |
                v
  SUPPORTS / REFUTES / IRRELEVANT / UNRESOLVED
                |
                v
       existing scoreless composer
```

The RC2 public operation must not accept an `authority_result` argument.

## Bounded semantic fragment

Exactly the already-constructed typed comparison fragment used by RC1:

- semantic family: `comparison`
- fields: `lhs_entity`, `rhs_entity`, `comparison_direction`
- supported strict-order relation table: `greater_than`, `less_than`
- `at_least` remains semantically unresolved for this bounded operator

No semantic text extraction or generic entailment is claimed.

## Required controls

### C1 baseline support
A fully warranted exact atom `A > B` against proposition `A > B` must derive `SUPPORTS` and compose to `supported`.

### C2 baseline refutation
A fully warranted exact atom `A < B` against proposition `A > B` must derive `REFUTES` and compose to `contradicted`.

### C3 exact RC1A payload-replay killer
Start from a warranted `A > B` atom. Mutate only the semantic proposal direction to `A < B` while preserving the stale `comparison_direction = greater_than` field-warrant receipt and the same atom identity. Frozen RC8J must independently classify the mutated atom as non-WARRANTED. RC2 must refuse relation construction and must not produce a deciding conclusion.

### C4 atom-identity substitution
Change `target_atom_id` while preserving the old `authority_subject_atom_id`. RC2 must preserve RC8J's rejection/unresolved behavior and refuse relation construction.

### C5 claim-binding substitution
Change the case's claim binding while preserving the old authority-subject claim binding. RC2 must preserve RC8J's rejection/unresolved behavior and refuse relation construction.

### C6 unresolved authority
Break an evidence-segment authority binding so RC8J returns `UNRESOLVED`. RC2 must refuse relation construction. It must not reinterpret non-WARRANTED authority as `IRRELEVANT`.

### C7 post-call caller mutation isolation
RC2 must derive its relation from an internal snapshot rather than retaining the caller's mutable dictionary. Mutating the original caller dictionary after relation construction must not change the returned receipt.

### C8 diagnostic metadata invariance
Changing diagnostic-only reader/instrument metadata that leaves RC8J authority unchanged must not change relation or conclusion.

### C9 score/polarity surface exclusion
Caller-supplied `score`, `confidence`, `threshold`, `channel`, and `relation_hint` remain forbidden or unused. No such field may appear as a deciding input in the proposition model, relation receipt, or scoreless conclusion.

### C10 categorical semantic regressions
Rerun the RC1 categorical controls: swapped inverse semantic equivalence, different-pair `IRRELEVANT`, unsupported same-pair relation `UNRESOLVED`, support plus irrelevant, support plus unresolved, mixed support/refutation abstention, and input-order invariance.

## Primary falsifier

RC2 is **FALSIFIED** if any atom that the exact frozen RC8J evaluates as non-`WARRANTED` can nevertheless enter scoreless categorical composition as a deciding `SUPPORTS` or `REFUTES` relation through the RC2 public interface.

## Additional falsifiers

RC2 is also falsified if any of the following occurs:

- the RC2 public interface accepts or requires a caller-supplied authority result;
- changing the semantic payload after the authority decision but before relation derivation can change the relation consumed by composition;
- caller-supplied scalar confidence/decision strength, threshold, channel, or relation hint affects the result;
- a `REJECTED`, `UNRESOLVED`, or `NO_ASSESSMENT` authority state is laundered into a categorical deciding relation;
- passing requires modifying frozen RC8J;
- production `src/` changes are required.

## Success condition

`SUPPORTED_WITH_BOUNDS` requires all preregistered controls to pass against the exact frozen RC8J dependency, including the exact RC1A replay killer, while production `src/` remains byte-unchanged relative to `32275a239b68af383a56bca843e28cbc1e343976`.

A passing result would support only this bounded inference:

> Within the already-constructed typed comparison fragment, authority evaluation and categorical relation derivation can share one exact immutable case snapshot so that a caller cannot replay a stale authority result against a different semantic payload, while retaining scoreless proposition composition.

It would not establish portable authority receipts, generic semantic entailment, semantic-text extraction, proposition truth in the world, Contract C projection, Decision Engine policy, production architecture, release, or promotion.

## Stop rule

Run the preregistered controls once on the frozen candidate revision. Preserve every negative result.

- If any primary/additional falsifier fires: record the exact failure, classify the candidate `FALSIFIED`, do not patch RC2, and stop. Any repair is a new candidate revision.
- If apparatus failure prevents a scientific result: record `INCONCLUSIVE` or `BLOCKED` with exact cause and stop unless the failure is purely execution plumbing that can be corrected without changing the candidate semantics.
- If all controls pass: record `SUPPORTED_WITH_BOUNDS` and stop at the research boundary. Do not promote or merge on the basis of this experiment alone.
