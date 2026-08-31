# RC7F-A Scientific Evidence Record

Status: **ACCEPTED HELD-OUT RUN / TERMINAL RESEARCH RECORD**

Terminal disposition: `MORE_SCOPE_RESEARCH_JUSTIFIED`

Research-only. No production authority, Contract E change, CAL `src/` change, merge, or release follows.

## Immutable lineage

- parent RC7E evidence: `34e9bcafad2c63c9b0761ffc456532344bc75b88`
- preregistration: `824152f1ba1183623da637cf4ba1c73ea56a3dbd`
- candidate/apparatus freeze: `9532da3eafff25102d59f880215e5ad1ab02cf9a`
- sealed apparatus ref: `sealed/rc7fa-scope-apparatus-20260831`
- accepted qualification run: `33452565378`
- qualification artifact: `9780275860`
- qualification ZIP digest: `sha256:af9e3e8191cf414109e8f8072ecfdb66a7bf6ac8dd11b6e9f4611246e5858041`
- held-out cohort freeze: `54f16a68eb1f3effe819b82483aa8f69ba7083b7`
- sealed cohort ref: `sealed/rc7fa-heldout-cohort-20260831`
- accepted scientific run: `33452771124`
- scientific artifact: `9780343081`
- scientific artifact ZIP digest: `sha256:b8867f1da09c09da004178d55ee5448cb91ab2d7afcd353965e82fd920c18172`
- `RESULTS.json` digest: `sha256:7cb3fc72966940e78ed2daaff54318e1822e1cc6077f1e7dafa9dfbad6569267`
- `REPORT.md` digest: `sha256:d3468d3f6da5b8cd78a82b53e8377d6ec2806ee81fddd9a7106e4bc6509ae2f8`

## Question

Can a bounded non-LLM scope/assertion layer preserve locally measured event structure while preventing embedded/non-factual event observations from becoming narrator-level factual authority?

## Result

The candidate substantially discriminated scope but did not meet the preregistered zero-false-permit safety condition.

- held-out cases: `92`
- unsafe false permits: `2`
- direct asserted positive/negative recall: `1.000000`
- authority-eligibility precision: `0.923077`
- scope-status accuracy: `0.956522`
- unresolved rate: `0.054348`
- allow-all baseline unsafe false permits: `68`
- meaning-changing pair accuracy: `1.000000`
- meaning-preserving pair stability: `1.000000`

The cohort consistency guard passed before execution; the RC7E duplicate-source/incompatible-gold defect did not recur.

## Exact unsafe cases

Both unsafe false permits occurred in the deliberately ambiguous/evidential family:

1. `U04`: `Supposedly, Elio logged record t.`
2. `U05`: `Purportedly, Yara sampled vial g.`

Gold in both cases was `UNRESOLVED / authority_eligible=false`. The frozen candidate returned `ASSERTED / authority_eligible=true` because its pre-held-out ambiguity markers encoded `supposedly ` and `purportedly ` with a literal following space, while these held-out renderings used a comma.

This is a bounded lexical/punctuation generalization failure. It is not repaired after reveal and the accepted result remains terminal for RC7F-A.

## Safe subtype disagreements

Two nested cases were non-authoritative but assigned the wrong non-authoritative scope subtype:

- one gold `CONDITIONAL_ANTECEDENT` was classified `ATTRIBUTED`;
- one gold `CONDITIONAL_CONSEQUENT` was classified `ATTRIBUTED`.

These did not create false permits, but they show the current flat priority classifier does not fully represent nested scope. A future scope graph should preserve stacked/outer scope rather than force one flat label if downstream semantics require the distinction.

## Ablation evidence

Removing each rule family materially worsened safety while leaving direct-assertion recall at 1.0:

- remove attribution: false permits `26`
- remove conditional: `10`
- remove deontic: `9`
- remove epistemic: `11`
- remove quantifier: `10`
- remove ambiguous/evidential: `6`

This supports the hypothesis that scope/assertion jurisdiction is a real separable layer rather than a cosmetic filter. The rule families contribute distinct safety value.

## Interpretation

Observed evidence supports:

1. locally valid predicate/argument observations can often be separated from narrator-level factual authority with a bounded non-LLM scope layer;
2. doing so reduced the unsafe-permit count from an allow-all baseline of 68 to 2 without losing any direct asserted positive/negative cases;
3. the exact RC7F-A candidate is not safe enough for hardening because the safety criterion required zero false permits;
4. the remaining unsafe error is narrower than the parent RC7E failure and is consistent with an evidential-discourse-marker normalization gap;
5. nested scope still needs a representation that can preserve more than one embedding operator when subtype matters.

## Smallest successor

Do not repair RC7F-A and rerun its held-out cohort as independent evidence.

A successor may test only:

- punctuation/orthography-normalized evidential discourse markers; and
- optionally a stacked scope path rather than a single flat status.

It must freeze before a fresh semantics-first held-out cohort and retain the same zero-false-permit criterion.

Separately, the RC7E `comparison` blind spot remains suitable for the preregistered RC7F-B bounded comparison-relation experiment. That lane need not wait for a successful RC7F-A successor because it tests measurement rather than scope authority.
