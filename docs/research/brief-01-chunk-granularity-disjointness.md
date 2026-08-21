# Research Brief 01: Why context allocation and semantic entailment fail on disjoint populations

**Claim Audit Lab · DEV probe · 2026-08-02**
**Source directory:** `outputs/2026-08-02-chunk-granularity-probe/` (sealed, `SHA256SUMS`)
**Pipeline version:** `cal-rules-v1.7.0` · retrieval floor `0.40` · `top_k` 5
**Status:** engineering finding. Not validation, not gate evidence, not an accuracy claim.

---

## Summary

A claim-verification pipeline that retrieves evidence and then tests entailment has two
places it can fail: the passage never reaches the reader, or the reader reads it and
declines to draw the conclusion. It is tempting to treat these as the same problem seen from
two angles: improve retrieval and the entailer gets better material; improve the entailer
and marginal retrieval matters less.

This probe tested that directly by changing exactly one variable: the unit of text that
gets embedded, and re-running an identical pipeline over the same claims.

**The two failure modes did not overlap at all.** Finer passage units rescued **2 of 2**
retrieval-floor misses and **0 of 10** entailment misses. The retrieval fix was total on its
own population and worthless on the other.

The headline measurement: a supporting clause that scored **0.392** as part of its section
scores **0.924** as its own unit: the same text, the same claim, the same encoder, a factor
no threshold adjustment can recover.

---

## 1. Background: the misses this probe explains

An earlier run (F8, `outputs/2026-08-02-qms-claim-generation/`) audited 60 claims authored
against a synthetic pharmaceutical QMS corpus. Twelve claims written to be supported came
back abstained, in two mechanically distinct groups:

| group | reason code | n | what happened |
|---|---|---:|---|
| floor misses | `no_evidence` | 2 | nothing cleared the `0.40` retrieval floor, so the entailer never ran |
| entailment misses | `no_entail_signal` | 10 | passages were admitted and read; the NLI head returned `neutral` |

Both floor cases were section-level chunks in which the supporting sentence is one bullet
among several. That suggests a specific, testable mechanism: **the embedding unit is a
section, but the support lives at clause level**, so the section vector is an average over
several propositions and the decisive one is diluted below the floor.

If that is right, finer units should rescue the floor group. The open question, the one
that actually matters for design, is whether they also rescue the entailment group.

## 2. Method

Three arms. Identical claims, identical pipeline, identical config, one variable changed.

| arm | passage unit | passages/doc |
|---|---|---:|
| `section` | shipped `##` section chunks, the F8 baseline | 7 |
| `fine` | bullets and sentences as separate passages | 20 |
| `fine+header` | same units, each prefixed with its section heading | 20 |

The third arm separates two explanations that the second one conflates: if finer units help
because they *isolate* the proposition, `fine` is enough; if they help because the section
heading supplies missing context, `fine+header` should beat `fine`.

Read-only throughout. No rule, config, chunking, floor, or version change was made, and none
was authorized.

## 3. Result

| | floor misses | entailment misses |
|---|---:|---:|
| `fine` | **2 / 2 rescued** | **0 / 10** |
| `fine+header` | **2 / 2 rescued** | **0 / 10** |

### 3.1 The floor half is a unit problem, and finer units solve it outright

| claim | retrieval, section → clause | entailment | verdict |
|---|---|---|---|
| `SOP-MFG-147` | **0.392 → 0.924** | 0.000 → 0.996 | `not_checkable` → **`supported`** |
| `SOP-MFG-102` | **0.385 → 0.677** | 0.000 → 0.961 | `not_checkable` → **`supported`** |

`SOP-MFG-147` §3 reads *"Production Engineer (MFG-SYS-1147): Manages suite utilities in
Cleanroom Suite 107-D and supervises maintenance on MFG-SYS-1147."* The claim restates it
almost verbatim.

The full section-arm retrieval ranking for that claim is worth stating in full, because it is
sharper than a single number suggests:

| rank | passage | score | |
|---:|---|---:|---|
| 1 | `#s01` | 0.397 | does **not** contain the support |
| 2 | `#s03` | **0.392** | **contains the support** |
| 3 | `#s02` | 0.346 | |
| 4 | `#s04` | 0.342 | |
| 5 | `#s06` | 0.262 | |

Nothing cleared `0.40`. `A2_retrieval_empty` fired and the verdict was `not_checkable` with
reason `no_evidence`. Note that the supporting section was not merely below the floor. It
was not even top-ranked, losing to a section that does not support the claim at all.

Split into clauses, the same supporting text becomes `#s03u01` and scores **0.924**, rank 1
by a wide margin, entailment `0.996`, verdict `supported`.

**This is not a threshold marginally missed.** The right text was in the candidate pool the
whole time. The unit was hiding it by a margin no floor value can compensate for: lowering
the floor to admit 0.392 would also admit the three non-supporting sections clustered
immediately beneath it.

Adding section headers changed nothing material (0.924 vs 0.924; 0.677 vs 0.677 band). **The
win is isolation of the proposition, not added context.**

### 3.2 The entailment half does not move at all

| | section | fine |
|---|---:|---:|
| mean `neutral` confidence (n=10) | 0.9963 | **0.9976** |
| still `neutral` | 10 / 10 | **10 / 10** |
| top retrieval, fine arm | n/a | **0.473 – 0.783** |

Every one of the ten retrieved *comfortably above the floor* in the fine arm. The premise
reached the NLI head cleanly, isolated, and stripped of neighbouring material. It returned
`neutral` anyway, and marginally **more** confidently than before.

This kills the obvious rescue hypothesis. "The section contained distractors that confused
the entailer" is false: removing the distractors made the model slightly *more* certain the
passage takes no position.

The clearest instance is `SOP-QC-088`. The passage states that the defrost cap is 6 hours and
that breaches beyond 6 hours require a Quality Hold. The claim asserts that a 7-hour cycle
requires a Quality Hold. Presented with that rule as an isolated sentence, retrieved at
0.573, the entailer scores `neutral` at **0.999**.

It is not being distracted. **It is not performing the comparison.** Applying a threshold
rule to a specific value is a reasoning step, and the entailment head does not take it.

## 4. Conclusion

**Context allocation and semantic claim verification operate on orthogonal layers.**

Formally, for the population measured here: let *F* be the set of claims failing at the
retrieval floor and *E* the set failing at entailment. Changing the passage unit from section
to clause recovered all of *F* and none of *E*. The intervention is total on one set and
inert on the other, and the two sets are disjoint by construction: a claim that never
cleared the floor was never scored by the entailer.

Three consequences follow.

**1. Neither fix substitutes for the other, and neither shrinks the other's problem.**
This is a stronger statement than defense-in-depth. Because the populations do not overlap,
the size of each problem is *unchanged* by fixing the other. Retrieval work cannot recover a
claim whose supporting passage was read and found unconvincing; entailment work cannot
recover a claim whose supporting passage never arrived.

**2. Allocation determines which evidence is in the room; it does not make the judge able
to read.** The ten entailment misses won their seats: decisive clause isolated,
distraction-free, retrieved between 0.473 and 0.783, and the verdict did not move. At the
tightest allocation obtainable on this corpus, **10 of 12 misses survive.** A perfect
retrieval layer does not produce a verdict.

**3. Similarity rank is a poor proxy for relevance *and* a poor proxy for entailment, and
these are separate failures.** `SOP-QC-088` retrieved at 0.573 (a good seat) and entailed at
0.001. Ranking well and being decisive are independent properties.

### 4.1 The asymmetry in danger

The two failure modes are not equally safe when they occur.

An entailment miss reports that evidence was retrieved, read, and found not to settle the
claim. That is a defensible thing to say.

A floor miss reports `no_evidence`, which in a review context is indistinguishable from
*"the document does not say that."* For `SOP-MFG-147`, the document says it almost verbatim,
and CAL reported no evidence. **A retrieval failure is silently mislabelled as an absence of
support.** In a regulated review that is the more dangerous of the two, and it is the one
that finer units fix.

## 5. Boundaries

Stated plainly, because this brief is easy to over-read.

- **DEV probe, read-only.** No chunking, floor, rule, config, or version change was made or
  authorized by this result.
- **n = 12, and the 12 are the F8 misses**, a population *selected for being misses*. The
  rescue rates describe this group. They are not a rate for any corpus and cannot be read as
  an accuracy figure.
- **Intent labels are the generator's.** `relationship` is a generation spec, not
  human-adjudicated gold; 3 of the 12 were verified against source text by hand.
- **Not tested: whether finer units cost anything elsewhere.** Splitting sections into 20
  units per document raises the candidate count, and `top_k` = 5 over finer units admits a
  narrower slice of the document. That could suppress multi-sentence support, or change
  contradiction detection. **This probe shows finer units rescue these 12. It does not show
  finer units are safe to adopt.** A chunking change would require a full-corpus re-run with
  attention to the `conflicts` and `partial` classes first.
- **Single-document bundles.** The corpus places every candidate passage in one document, so
  this probe contains no off-topic-document distractors and says nothing about cross-document
  pollution.

## 6. Relation to prior work

The finding converges with an independent context-allocation argument (Pearmain, 2026-07-27,
captured at `10_knowledge/knowledge-systems/`), which proposes decoupling the retrieval
hierarchy: search at chunk level for precision, expand to section level for readable
context, keep attribution at document level. The stated mechanism is that in regulatory
documentation the decisive material is a small clause, while large documents contain much
internally similar material *by design*, so similarity matching lets one document pollute the
window.

That is precisely the `SOP-MFG-147` failure, and this probe attaches a number to it: §3 is
three structurally similar role bullets, the claim concerns one, and the section embedding
averages three near-neighbours until the right clause disappears. **0.392 as a section, 0.924
as a clause.** Searching at section level cost 0.53 of retrieval score on verbatim support,
and it cost the verdict.

It also **bounds** that argument. Allocation is necessary and not sufficient: at the tightest
allocation this corpus permits, 10 of 12 misses survive untouched. The probe was run without
reference to that argument, which makes the convergence worth something, but it is not
evidence that either design works, and it does not validate CAL.

---

## Receipts

| item | location |
|---|---|
| probe script | `outputs/2026-08-02-chunk-granularity-probe/probe.py` |
| per-claim results | `outputs/2026-08-02-chunk-granularity-probe/results.json` |
| per-claim traces (fine, fine+header) | `outputs/2026-08-02-chunk-granularity-probe/traces/` |
| section-arm baseline traces | `outputs/2026-08-02-qms-claim-generation/scaled-30/cal-audit/traces/` |
| checksum manifest | `outputs/2026-08-02-chunk-granularity-probe/SHA256SUMS` |
| figures used on the docs site | `docs/assets/traces.js`, generated by `scripts/gen_docs_traces.py` |

Every figure quoted in this brief is derived from those files. The docs-site dataset is
regenerated from them rather than transcribed, so the site and this brief cannot drift apart
without the generator failing.
