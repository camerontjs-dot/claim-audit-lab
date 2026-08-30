# NLI Measurement Discrimination RC0 — Results

## Terminal disposition

**INCONCLUSIVE**

This experiment does **not** justify replacing the production CAL entailer.

It does establish two narrower findings:

1. **same-family capacity/training breadth is a real short-context signal:** the larger Laurer model corrected two incumbent errors without introducing a new short-case regression on this frozen slice;
2. **512-token aperture is a directly demonstrated failure mechanism:** moving unchanged decisive evidence behind irrelevant material collapsed both 512-position models while the 1280-position model preserved its labels and short-case accuracy.

The result therefore narrows the next question. It does not authorize a production model change.

## Frozen authority

- production main: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- frozen Cohort A science head: `ba1310d73ab63adf7c83de2f1e130f7f00a665af`
- Cohort A accepted Actions run: `33286159031`
- Cohort A frozen RESULTS SHA256: `38cd6f29eab0ea6e0f50e737814b993aaf45a3919cacb5e02296289516e112d7`
- preregistration commit: `c3208161e8a69c5a86adf1849161900e7383bb77`
- accepted RC0 execution head: `8e4267e42e2be0615c20da79b74988e4f1747668`
- accepted RC0 Actions run: `33286762938`
- accepted artifact ID: `9724863795`
- artifact ZIP SHA256: `4a1653aca619921eaa1393b7085a33a031342f969ae0284134a3d1c58cf60a36`
- frozen RC0 INPUTS SHA256: `6c1780a05c5720d0f8c2d20b0109198939846a8f6ea6d47ef6c79afeaa73c5ab`
- frozen RC0 RESULTS SHA256: `07eb1a99927226779e5071959c527f7a7d280afebe23855e1f1ae058cc425caf`

No production semantic surface, threshold, operator, aggregation rule, Contract C object, or decision policy changed.

## Models

| Arm | Frozen model revision | Purpose |
|---|---|---|
| incumbent | `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli@6f5cf0a2b59cabb106aca4c287eed12e357e90eb` | production baseline |
| same-family large | `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli@0de4830e69aa5710af98b05f2c4d001d0edc0e52` | capacity / NLI-training breadth |
| long-context base | `tasksource/deberta-base-long-nli@d6e08f68489c9ac015ba3071f90ac0976cbc1fff` | 1280-position aperture probe |

All three exposed an unambiguous three-way entailment / neutral / contradiction label map. Determinism sentinels passed.

## Target slice

The frozen 33-case construction corpus yielded **14** cases whose stipulated relation had a defensible ordinary three-way NLI target:

- `restates` → entailment;
- `weakens` → entailment;
- `contradicts` → contradiction;
- `overgeneralizes` → neutral.

Source-boundary absence, numeric bound instantiation, conjunction/partial conjunction, and multi-hop chain cases were excluded from model ranking.

### OBSERVED

Primary target composition:

- entailment: 7;
- contradiction: 6;
- neutral: 1.

### LIMIT

The single neutral target is a serious evidentiary limitation. Neutral-versus-contradiction preservation is important to CAL, so one neutral case cannot establish a promotion-quality false-adverse rate.

## Short-context result

| Model | Correct | Exact match | Entailment | Contradiction | Neutral | Neutral→contradiction |
|---|---:|---:|---:|---:|---:|---:|
| incumbent base | 11/14 | 0.786 | 6/7 | 5/6 | 0/1 | 1 |
| same-family large | 13/14 | 0.929 | 7/7 | 6/6 | 0/1 | 1 |
| long-context base | 12/14 | 0.857 | 7/7 | 5/6 | 0/1 | 0 |

### OBSERVED — incumbent errors

The three incumbent short-case errors are:

1. **CG-18, overgeneralization target = neutral**
   - prediction: contradiction
   - `p_contradiction = 0.970703125`
   - `p_neutral = 0.02001953125`
   - `p_entailment = 0.00945281982421875`

2. **CG-19, genuine exception-based contradiction**
   - prediction: neutral
   - `p_neutral = 0.982421875`
   - `p_entailment = 0.01311492919921875`
   - `p_contradiction = 0.0045318603515625`

3. **CG-20, logical weakening target = entailment**
   - prediction: contradiction
   - `p_contradiction = 0.76416015625`
   - `p_entailment = 0.22021484375`
   - `p_neutral = 0.0157318115234375`

These are model measurements against construction-stipulated relations, not posterior probabilities.

### OBSERVED — same-family large

The large model corrected **CG-19** and **CG-20** and introduced no new short-case regression relative to the incumbent.

It did **not** repair CG-18:

- CG-18 target: neutral;
- prediction: contradiction;
- `p_contradiction = 0.98291015625`;
- `p_neutral = 0.01409912109375`.

### INFERENCE

The preregistered capacity/training-breadth hypothesis survives this test. Two of three incumbent errors disappear with the larger same-family checkpoint.

However, the most directly CAL-dangerous error in this slice, neutral → high-confidence adverse, remains and becomes slightly more extreme numerically. This blocks any claim that scale alone fixes CAL's three-way semantic boundary.

## Aperture mutation

Every primary case had three frozen forms:

1. `short`: decisive support-role passage(s) only;
2. `stress_head`: identical decisive evidence first, then irrelevant administrative filler;
3. `stress_tail`: the same irrelevant filler first, then unchanged decisive evidence.

The stress inputs were approximately 705–720 incumbent tokens.

### OBSERVED — context visibility

- incumbent DeBERTa-base native maximum: 512; all 14 stress inputs truncated;
- same-family DeBERTa-large native maximum: 512; all 14 stress inputs truncated;
- long-context DeBERTa-base native maximum: 1280; no stress input truncated.

### Position result

| Model | Short | Stress head | Stress tail | Tail label stability |
|---|---:|---:|---:|---:|
| incumbent base | 11/14 | 11/14 | 3/14 | 3/14 |
| same-family large | 13/14 | 13/14 | 7/14 | 6/14 |
| long-context base | 12/14 | 12/14 | 12/14 | 14/14 |

The long-context model was the only model to recover the correct stress-tail relation where both 512-position models failed on:

- CG-03;
- CG-04;
- CG-12a;
- CG-12b;
- CG-20;
- CG-24.

### INFERENCE

This is strong evidence for a **mechanical aperture effect**.

The same irrelevant material was present in both stress variants. The 512-position models retained their short performance when decisive evidence appeared before the truncation boundary, then collapsed when the same evidence moved behind it. The 1280-position model saw the full input and preserved all 14 labels across short/head/tail forms.

This does not establish that CAL should adopt a long-context entailer. It establishes that **when CAL presents a premise whose decisive material is beyond 512 tokens, model aperture can independently manufacture a semantic-measurement failure**.

A smaller upstream evidence-construction fix may be preferable where a short sufficient passage can be selected without losing needed composition.

## What the long-context model did not solve

### OBSERVED

The long-context model remained wrong on two short cases:

- CG-18: target neutral, predicted entailment (`p_entailment = 0.8493005633354187`);
- CG-19: target contradiction, predicted neutral (`p_neutral = 0.8691510558128357`).

Its perfect 14/14 positional label stability therefore means stable measurement, not perfect semantics.

### INFERENCE

Long context fixes **visibility**, not the underlying quantifier/exception reasoning problem.

That distinction is exactly why aperture and measurement should remain separate CAL failure stages.

## Preregistered falsifiers

### Capacity / training-breadth hypothesis

**NOT FALSIFIED; SUPPORTED AS A RESEARCH SIGNAL.**

The large same-family model reduced short errors from 3 to 1 and introduced no new incumbent-correct → candidate-wrong short cases.

However, it did not reduce the neutral→contradiction false-adverse count, which remained 1/1 neutral cases.

### Aperture hypothesis

**SUPPORTED AS A MECHANISM.**

The 1280-position model preserved short-case correctness and labels under the >512-token tail mutation while both 512-position models materially degraded.

### Production replacement hypothesis

**INCONCLUSIVE / NOT JUSTIFIED.**

Reasons:

1. only 14 primary cases;
2. only one neutral target;
3. the large model retains the high-confidence neutral→adverse failure;
4. the long-context model retains semantic failures despite perfect positional stability;
5. typed numeric, source-boundary, and compositional cases were intentionally excluded rather than used to inflate a model score;
6. this experiment does not establish how frequently production CAL genuinely requires >512-token evidence sets rather than better evidence construction.

## Competing explanations checked

### “The large model only looks better because it sees more context”

Rejected for the **short** comparison. Both incumbent and same-family large use the same 512-position aperture on short premises.

### “The tail result is just distraction sensitivity”

Disfavored. The same irrelevant filler in `stress_head` leaves short accuracy intact for the two 512 models; moving the unchanged decisive evidence behind that filler produces the collapse.

### “A better NLI model fixes Cohort A's operator problems”

Not established and not tested. Operator-owned/source-boundary/compositional relations were deliberately excluded from the ranking surface.

### “High softmax confidence means epistemic certainty”

Rejected by design. The frozen measurements contain highly confident wrong predictions in multiple directions.

## Preserved deviations

### Attempt 1 — run `33286692575`

Stopped before model execution because Ruff found five line-length violations in the new runner.

Repair: formatting only.

No target, model, threshold, corpus, semantic, or scoring change.

### Attempt 2 — run `33286734751`

Stopped before model execution because the research test module was invoked without the repository root on `PYTHONPATH`.

Repair: invocation environment only.

No target, model, threshold, corpus, semantic, or scoring change.

### Pull-request merge-context check — run `33286764482`

The PR-event job failed the protected-surface diff because GitHub tested a synthetic merge with the later Cohort A documentation head, which legitimately contains post-science files under the protected Cohort A research directory.

The accepted scientific execution is the direct head push run `33286762938`, tied to `8e4267e42e2be0615c20da79b74988e4f1747668`. The push-run protected-surface check passed against the exact frozen Cohort A science head before model execution.

This PR-event failure is retained as an apparatus/stacking limitation; it is not repaired by weakening the science guard in this RC.

## Decision

**Do not change the production entailer.**

Preserve three separate candidate follow-ups:

1. **neutral / universal / exception discrimination:** expand independently frozen neutral and quantifier/exception cases around the CG-18/CG-19 failure family before considering the large same-family checkpoint;
2. **aperture incidence:** determine whether real CAL evidence construction materially places necessary evidence beyond 512 tokens, and whether smaller passage/set construction solves it before testing a long-context production candidate;
3. **typed semantic operators:** continue numeric, boundary, scope, and composition work independently of NLI model ranking.

The current entailer remains the production baseline pending those discriminating tests.

## Non-authorization

This evidence record does not authorize:

- production model replacement;
- threshold tuning;
- calibration changes;
- Contract C changes;
- semantic-operator changes;
- aggregation or decision-policy changes;
- reuse of the killed historical SLG entailer bake-off;
- any claim that a model softmax is a posterior probability of truth.
