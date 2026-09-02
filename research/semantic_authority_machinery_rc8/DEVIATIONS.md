# RC8 Deviations and Procedural Notes

This file records deviations in experiment execution or apparatus handling. Scientific falsifications are preserved in their own result records and in the aggregate `RESULTS.md`; they are not reclassified as procedural deviations.

## 1. Pre-preregistration local prototype execution

Before the durable GitHub preregistration, the research lead executed a local prototype of the original candidate gate against open qualification mutation fixtures while developing the apparatus.

Consequence:

- the original qualification fixture result is not blind evidence;
- it is usable only to establish that the evaluator catches intentionally weak architectures and that the apparatus runs;
- no scientific claim counts the local prototype result as prospective evidence;
- later candidates were frozen before their fresh prospective cohorts were added or executed;
- candidate repair after held-out reveal was prohibited for each frozen experiment.

This deviation does not establish independent implementation. A future independent-recoverability result requires a sanitized aperture and separate context-free implementation.

## 2. RC8F pre-reveal structural cardinality correction

The first RC8F pre-reveal workflow attempt asserted that the frozen cohort contained 20 cases. The cohort actually contained 21.

Preserved failed attempt:

- workflow head: `245c8b04cfc460449ae562be10f3e11f4b74b4e5`;
- run: `33660585742`;
- job: `100349865177`;
- failure: model-free structural assertion `len(cases) == 20` while the frozen cohort returned 21.

Before this failure:

- candidate and predecessor blob checks passed;
- prospective cohort/evaluator identities passed;
- the candidate was **not executed** on the prospective cohort.

Correction:

- only the candidate-blind structural count assertion changed from 20 to 21;
- candidate bytes did not change;
- semantic cohort did not change;
- evaluator did not change;
- expected labels did not change.

The corrected pre-reveal run `33660759984` / job `100350433412` passed, after which the frozen candidate was revealed once. The failed first attempt remains part of the record.

## 3. Duplicate push / pull-request workflow instances

GitHub Actions generated both push-triggered and pull-request-triggered workflow instances for some commits.

Handling rule used throughout the later programme:

- scientific records identify one exact-head **push** run as the accepted pre-reveal or reveal execution;
- duplicate PR-triggered instances are not counted as additional independent evidence;
- run IDs and exact head SHAs are recorded in the corresponding freeze/result files.

This is workflow duplication, not replication.

## 4. Documentation commits after reveal

Once a prospective cohort had been revealed and terminalized, subsequent documentation changes could retrigger the research workflow because the workflow watches the research directory.

Such post-reveal reruns are regression/verification activity only. They do not regain prospective status and must not be counted as additional held-out evidence.

## 5. Independence boundary

This entire RC8 through RC8J programme was conducted in one normal-context research thread with accumulated knowledge of prior failures and successor designs.

Therefore:

- the programme provides sequential falsification and prospective successor evidence;
- it does **not** provide fresh independent implementation evidence for the terminal architecture;
- this context is contaminated for any experiment whose scientific claim depends on independent recovery from specification alone.

A fresh independent reproduction must start in a separate clean context with a frozen information aperture. The current thread may prepare that packet but must not execute the independent implementation and count it as independent evidence.

## 6. Terminal comparator self-check loader deviation

After RC8J and the independent-reproduction package were already frozen, terminal regression workflow run `33671895951` / job `100387261565` failed only at `Self-check post-freeze comparator against frozen reference`.

Observed before that failure:

- production semantic-surface verification passed;
- frozen Contract B and terminal research byte verification passed;
- the 268-case exposed RC8J regression passed;
- the 28-case prospective RC8J regression passed.

The self-check invoked the frozen comparator with `authority_contract_rc8j.py` supplied through the comparator's **external implementation file** loader. That reference module uses package-relative imports and is not itself a valid standalone external implementation file. The intended independent implementation interface is standalone, so the self-check invocation exercised the wrong loading shape.

Handling:

- the failed run remains preserved;
- the frozen comparator `0a3ca098c3aa41ee9a8962969b927ad8e8219890` is not changed;
- the frozen reference `f55156e43e0c1b4a7868bc8339585b8892edda38` is not changed;
- the frozen specification and reveal packets are not changed;
- only the terminal regression workflow may use a temporary standalone adapter that imports the frozen package reference and re-exports `assess_authority` through the comparator's intended external-file interface.

This is a post-terminal harness self-check defect, not evidence against RC8J or against the independent reproduction. It must not be hidden or counted as a scientific disagreement.