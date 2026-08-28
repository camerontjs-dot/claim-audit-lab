# RC2-C Deviation 002 — Irrelevant-state fixture was not output-invariant

## Preserved scientific run

RC2-C head: `769fe5602c6ca8206dead2bd62f7cd6f73c9381d`.

Dedicated workflow run `33183144828`, job `98889222521`: **FAILED**.

Frozen receipt artifact:

- artifact `9690557500`;
- digest `sha256:02297c5a05824490efafcc095c57f7098fe733dd3b400e7364ac66edf119f8c7`.

The run executed the experiment after all frozen identity/no-production-mutation checks passed.

Observed control results:

- original production vector: PASS;
- causal-removal mutation: PASS;
- missing-dependency fail-closed: PASS;
- missing-trigger fail-closed: PASS;
- policy-identity control: PASS;
- causal-attribution distinction: PASS;
- irrelevant-state negative control: **FAIL**.

The frozen receipt also records `falsely_recorded_causal: false` for the unrelated evidence item. The failed subcondition was `production_output_unchanged: false`.

## Diagnosis

The negative fixture added an unrelated evidence item **and nominated it as a support candidate**. `ClaimAssessment.candidate_evidence` legitimately retained that candidate, so the complete production result object could not remain byte/content invariant even though the candidate did not alter the verdict, rule trigger, or dependency graph.

This means the fixture did not satisfy the stronger preregistered negative-control condition that the added state be output-invariant. It does not justify calling the failed control green merely because causal attribution remained correct.

## Allowed correction

Preserve the original acceptance criterion: the complete production result must remain unchanged and the unrelated state must not become a causal dependency.

Change only the negative fixture so the unrelated source/excerpt is present in the supplied `EvidenceBundle` but is **not nominated as a candidate**. This keeps it as real evidence-world state while making it irrelevant to the frozen production execution.

Do not change:

- the original seam;
- the causal-removal mutation;
- receipt fields or dependency semantics;
- the independent validator;
- policy values/hash;
- expected original/removal outputs;
- fail-closed criteria;
- the causal-attribution necessity criterion;
- any file under `src/`.

The failed run and artifact remain part of the research record.
