# EDR — Observation, Semantic Warrant, and Successful Abstention

Status: **DECIDED FOR RESEARCH AND FUTURE PROMOTION GATES**

Date: 2026-08-31

## Decision

Adopt the following explicit CAL design principle:

> **CAL may know that it observed something without claiming that it knows the thing is true. When warrant is incomplete, abstention is a successful outcome.**

CAL architecture, research apparatus, and future promotion proposals must keep these states distinct:

1. **observation / measurement** — a parser, instrument, rule, or other reader detected a semantic structure in source material;
2. **semantic warrant** — the source and its scope actually warrant promoting that observation to a proposition CAL may assert at the relevant level;
3. **downstream decision use** — a warranted proposition may participate in a decision under the decision system's own rules;
4. **operational authorization** — any permission to act remains a separately typed authority question.

An observation MUST NOT acquire semantic authority merely because it was detected confidently, detected by multiple instruments, or is locally well-formed. Missing, ambiguous, conflicting, or out-of-jurisdiction warrant is a valid reason to abstain.

This principle is intentionally fail-closed. For safety-sensitive evaluation, a safe miss or explicit unresolved result is preferable to an unwarranted factual assertion.

## Effective artifact

This EDR is a governance/design constraint only. It does not change production `src/` behavior by itself.

Any later production implementation must be separately justified by bounded research and a promotion decision.

## Observed evidence

### RC7E heterogeneous semantic measurement portfolio

Frozen RC7E evidence commit:

`34e9bcafad2c63c9b0761ffc456532344bc75b88`

Accepted RC7E scientific run:

`33448511982`

RC7E showed that heterogeneous non-LLM instruments could observe substantially more semantic structure than the deterministic baseline, but authority remained unsafe in important dimensions. In particular, role/event observations were frequently real observations whose surrounding scope did not warrant narrator-level assertion.

The post-hoc capability-envelope analysis was committed separately at:

`06836f9bb27add59ad6be283e9628e6bd1014d17`

### RC7F-A assertion-scope jurisdiction

Frozen evidence commit:

`120268d34247f8dd448ba3af22420d3ecbe7c8de`

Draft Research PR:

`#65`

Accepted scientific run:

`33452771124`

Observed results over 92 held-out semantics-first cases:

- allow-all local-event baseline false permits: `68`;
- bounded scope candidate false permits: `2`;
- direct positive/negative assertion recall: `1.0`;
- authority-eligibility precision: `0.923077`;
- scope-status accuracy: `0.956522`.

This strongly discriminated **observation** from **warrant**. The two remaining unsafe permits were preserved and the candidate was not repaired after reveal.

Terminal experiment token:

`MORE_SCOPE_RESEARCH_JUSTIFIED`

### RC7F-B comparative-relation measurement

Frozen evidence commit:

`3009da45e98dac099c4758c1d41ff42cf2a56eae`

Draft Research PR:

`#66`

Accepted scientific run:

`33453256638`

Observed results over 60 held-out cases:

- typed comparison precision: `1.0`;
- typed comparison recall: `0.8`;
- false proposals on negative/domain controls: `0`;
- relation-direction accuracy on resolved gold: `1.0`;
- left/right attachment accuracy on resolved gold: `1.0`.

The instrument safely abstained on unsupported comparative families instead of fabricating a relation. Those misses remain research debt rather than being converted into false authority.

Terminal experiment token:

`MORE_COMPARISON_RESEARCH_JUSTIFIED`

## Inference

The evidence supports a layered architecture in which semantic readers emit **non-authoritative observations/proposals**, while a separate scope/warrant mechanism decides whether a particular observation is eligible to become an asserted proposition.

The evidence does **not** support treating parser confidence, model confidence, instrument agreement, or successful extraction as semantic authority.

The structural form appears analogous to operational authority-basis binding, but semantic warrant and operational authorization remain separate typed domains unless later evidence supports a shared algebra.

## Alternatives considered

### 1. Treat every successful extraction as an assertion

Rejected by RC7F-A. The allow-all baseline produced 68 false permits.

### 2. Require reader/instrument agreement before assertion

Not adopted as authority. RC7E already showed that agreement can preserve shared errors, and agreement alone does not establish scope or source warrant.

### 3. Collapse semantic warrant and operational authorization into one generic authority flag

Rejected for now. A proposition can be semantically warranted while no actor is authorized to act, and an actor may be operationally authorized without that permission making an arbitrary proposition true.

### 4. Maximize recall and repair unsafe outputs downstream

Rejected as the default safety posture. The current evidence favors explicit unresolved/safe misses over unwarranted assertions.

## Decision rationale

The smallest architecture consistent with the evidence is not a larger monolithic language reader. It is a separation of concerns:

```text
raw source
  -> semantic observations / proposals
  -> scope and assertion context
  -> semantic warrant
  -> warranted propositions
  -> downstream decision logic
  -> separately typed operational authorization
```

This preserves useful observations without laundering them into truth claims.

## What is not established

This EDR does not establish:

- a complete semantic-warrant ontology;
- that current RC7F-A scope rules are production-ready;
- that all semantic dimensions can be measured without an LLM;
- that an LLM lane will never be useful;
- that semantic warrant and Contract E operational authority share one production representation;
- universal truth, provenance, source reliability, or evidence legitimacy;
- production promotion of any RC7E/RC7F research code.

## Compatibility / migration consequence

Future semantic instruments should default to proposal/observation receipts that do not self-authorize.

Future evaluators should distinguish at least:

- correctly observed and warranted;
- correctly observed but not warranted;
- unresolved/abstained;
- missed observation;
- false observation;
- false warrant / unsafe assertion.

Metamorphic stability must not count paired abstentions as successful understanding. Record `stable_correct`, `stable_abstention`, and `stable_wrong` separately where relevant.

## Residual uncertainty

Open questions include:

- whether scope should be represented as a flat label or stacked scope graph;
- how semantic warrant composes across attribution, epistemic, conditional, deontic, quantifier, temporal, and contradictory contexts;
- whether semantic warrant and operational authority can share a generic typed jurisdiction algebra without domain laundering;
- which remaining semantic capabilities can be implemented safely with bounded non-LLM machinery.

## Reconsideration trigger

Reopen this decision if future frozen evidence shows that:

- a monolithic reader can safely establish assertion eligibility without an explicit warrant boundary;
- separating observation from warrant materially destroys necessary correctness in a bounded production use case;
- a different representation achieves equal or better false-permit safety while preserving recoverability and traceability; or
- a shared authority algebra causes cross-domain laundering or otherwise collapses distinctions this EDR requires.

## Lineage

- RC7E evidence: `34e9bcafad2c63c9b0761ffc456532344bc75b88`
- RC7E capability analysis: `06836f9bb27add59ad6be283e9628e6bd1014d17`
- RC7F-A evidence: `120268d34247f8dd448ba3af22420d3ecbe7c8de`, Draft PR #65
- RC7F-B evidence: `3009da45e98dac099c4758c1d41ff42cf2a56eae`, Draft PR #66

No production code or release is authorized by this record.
