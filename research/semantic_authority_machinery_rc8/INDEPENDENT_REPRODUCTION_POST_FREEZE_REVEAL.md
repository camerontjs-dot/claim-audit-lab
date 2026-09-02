# POST-FREEZE REVEAL: Frozen Authority Gate v1 Independent Reproduction

**Do not provide this packet to the independent implementer before their implementation and prereveal tests are externally verified as frozen.**

This packet continues an existing fresh independent reproduction. It does not authorize restarting or repairing the independent implementation.

## 1. Preconditions

Proceed only if the operator has verified a prereveal freeze receipt containing immutable implementation and test identities.

The independent implementation and prereveal tests must remain unchanged after this reveal. If they are edited after observing evaluator/reference behavior, the edited result cannot be counted as the original independent reproduction.

## 2. Post-freeze authorization

After the freeze is verified, the implementer may consume the frozen comparison package identified by `INDEPENDENT_REPRODUCTION_REVEAL_FREEZE.json`.

The reveal authorizes access to:

- the post-freeze comparator `independent_reproduction_compare.py`;
- its frozen cohort/evaluator dependencies in `research/semantic_authority_machinery_rc8/`;
- the frozen RC8J reference implementation used only for post-freeze differential comparison;
- frozen expected outputs embedded in the evaluator cohorts;
- aggregate/reference behavior needed to classify disagreements.

This authorization begins **after** implementation freeze only.

## 3. Frozen comparator interface

The independent implementation must still expose:

```python
def assess_authority(case: dict) -> dict:
    ...
```

The comparator accepts the frozen implementation file path without modifying it.

From a checkout of the frozen reveal package, run:

```bash
python -m research.semantic_authority_machinery_rc8.independent_reproduction_compare \
  --implementation /absolute/path/to/frozen/authority_gate_independent.py \
  --output INDEPENDENT_REPRODUCTION_COMPARISON.json
```

Do not patch the independent implementation in response to this output.

## 4. Comparison corpus

The frozen comparator combines:

- the 268-case exposed RC8J qualification corpus; and
- the 28-case fresh RC8J prospective heldout corpus.

Total comparison cases: **296**.

The corpus spans the accumulated typed reason surface, including the preserved source, atom, Contract B segment and Contract B claim falsifiers.

This is a reference-conformance evaluator. It is not claimed to be an independently designed evaluator.

## 5. Required result preservation

Preserve `INDEPENDENT_REPRODUCTION_COMPARISON.json` exactly as emitted.

Record at least:

- independent status-exact count;
- independent reason-exact count;
- independent/reference exact count;
- reference status/reason exact counts against frozen expected outputs;
- unsafe warranted atom count;
- expected, independent and reference state distributions;
- every disagreement row;
- prereveal uncertainties and whether each was exercised by the evaluator;
- any runtime or apparatus deviation.

## 6. Scoring order

Interpret the comparison in this order.

### 6.1 Reference/evaluator self-consistency

First check the reference implementation against the frozen expected labels.

If the reference itself disagrees with an expected label on a case, classify that case as evaluator/reference inconsistency before judging the independent implementation on it.

Do not force independent agreement to a defective reference row.

### 6.2 Unsafe independent warrants

Any case whose expected authority is not `WARRANTED` but whose independent result is `WARRANTED` is an unsafe disagreement and must be reported prominently.

Do not hide it inside aggregate accuracy.

### 6.3 Typed status and reason agreement

Report status and typed-reason agreement separately.

A correct coarse status with a different typed reason is still a disagreement because the frozen specification defines deterministic precedence.

### 6.4 Independent/reference differential

Report exact output equality between independent and frozen reference behavior, but do not treat differential agreement alone as proof of correctness. The expected-label comparison remains separate.

## 7. Terminal classifications

Use evidence-led classifications rather than a binary pass/fail slogan.

Possible terminal interpretations include:

- `INDEPENDENT_RECOVERY_SUPPORTED_WITHIN_EVALUATOR_ENVELOPE`: reference is self-consistent and the frozen independent implementation matches all scored expected statuses/reasons with zero unsafe warrants;
- `INDEPENDENT_RECOVERY_PARTIAL`: no unsafe warrants but one or more scored status/reason disagreements remain;
- `INDEPENDENT_RECOVERY_DISAGREEMENT`: substantive independent disagreement remains, especially if an unsafe warrant occurs;
- `EVALUATOR_REFERENCE_DEFECT`: one or more expected rows are not reproduced by the frozen reference and affected rows require separate treatment;
- `CONTAMINATED`: pre-freeze independence was materially compromised;
- `INCONCLUSIVE`: apparatus/runtime failure prevents valid comparison.

These labels are descriptive evidence summaries, not production promotion decisions.

## 8. No post-reveal repair

Do not modify the frozen implementation after seeing the comparison and then report the modified result as independent agreement.

If a repair is scientifically useful, preserve the original terminal result first. Any repaired implementation is a new, non-independent follow-up unless a new clean-room reproduction is started from scratch under a new freeze.

## 9. Terminal record

Create a terminal reproduction record containing:

- original prereveal freeze receipt;
- frozen specification identity;
- frozen reveal-package identity;
- comparison artifact identity;
- exact metrics;
- all disagreements;
- uncertainty resolution;
- contamination status;
- terminal classification;
- explicit statement that no production/release/promotion is authorized by the reproduction alone.

Then stop for operator governance review.
