# RC7F Capability Envelope Update

Status: **POST-HOC SYNTHESIS OF SEPARATELY FROZEN SUCCESSOR EVIDENCE**

This document does not modify RC7E, RC7F-A/B/A1/B1/C/D apparatus, cohorts, accepted runs, or terminal dispositions. It updates the capability map using terminal evidence from separate experiments.

## Governing design principle

CAL now records the following design decision separately in `docs/decisions/edr-2026-08-31-semantic-warrant-and-abstention.md` on commit `f52e3d873f7e7c9265921163c895f809465d01a6` / PR #67:

> **CAL may know that it observed something without claiming that it knows the thing is true. When warrant is incomplete, abstention is a successful outcome.**

This update therefore distinguishes measurement capability from semantic-warrant capability.

## Evidence incorporated

### RC7F-A1 stacked scope / semantic warrant

- terminal evidence: `ead5a6b068c17aefea0c2fc6b0b54b78ced26729`
- Draft Research PR: #68
- apparatus freeze: `e50e9fda7ad67b90b8b2ce4b0b84e4bc98f6d33d`
- held-out freeze: `a964ba8817d964bbc5156daa60d69eb1119d0936`
- scientific run: `33464507877`
- artifact: `9784357201`
- digest: `sha256:59086e23fa91e180f2f54fc4475305ae6ea533293a1f537e816b5d36f7a12041`
- terminal: `SCOPE_ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE`

Result: 4 unsafe false permits out of 92; direct assertion recall 1.0; exact scope-path accuracy 0.956522. All four unsafe cases were parenthetical evidential wrappers. The zero-false-permit warrant gate failed.

### RC7F-B1 comparison measurement

- terminal evidence: `0ecdedc5cea970485a635508255f3670ab231c33`
- Draft Research PR: #69
- apparatus freeze: `e3463a7c92747fa9583d5abde230b89373756693`
- accepted R1 held-out/deviation freeze: `f386da3d80eabfae836ab37c59a4ecf77f172634`
- scientific run: `33465045942`
- artifact: `9784534254`
- digest: `sha256:2c65ddfc0f2bc7a91a34ee6ea4c09d8a696a5cc7538b2e4e86e64e8788e89e67`
- terminal: `COMPARISON_INSTRUMENT_CANDIDATE_READY_FOR_HARDENING`

Result: 56/56 supported comparison observations recovered, zero false proposals, precision/recall/direction/attachment 1.0. The first held-out run failed only in a pre-execution count guard and is preserved separately.

### RC7F-C explicit event ordering

- terminal evidence: `e8d33913db66ad21027dffdf731d50f7a0977c8f`
- Draft Research PR: #70
- apparatus freeze: `9e172ebd221301b6a4513ead2c15cc4095e55ea4`
- held-out freeze: `4ced5d9b2e5a784529431e2bd440549be41e0b18`
- scientific run: `33464936862`
- artifact: `9784497429`
- digest: `sha256:e1707378d0b815d6773951b18744aee8b2fb3246175d4f4ff7f127f5c993bcbd`
- terminal: `EVENT_ORDERING_INSTRUMENT_CANDIDATE_READY_FOR_HARDENING`

Result: 44/44 supported explicit `before/after` event-order observations recovered, zero false proposals on 16 negative/unsupported controls, with direction/attachment/polarity 1.0.

### RC7F-D permission composition

- terminal evidence: `9e1f28c3e4f217561e4364e1560539bdf4870298`
- Draft Research PR: #71
- apparatus freeze: `01a1d8d80fccdc96f82e85f678e463c32becd55f`
- held-out freeze: `56a7e091a30bc9a0055421542191f15d5d9cf836`
- scientific run: `33464964947`
- artifact: `9784507428`
- digest: `sha256:b2f996cd24e62d9faf1a21e3345b00e7645ed1f6125fdc36eed8e9edb9449e4d`
- terminal: `DEONTIC_COMPOSITION_CANDIDATE_READY_FOR_HARDENING`

Result: 50/50 supported semantic permission-composition observations recovered, zero false proposals on 14 negative/unsupported controls, with exact composition, exception attachment, and temporal attachment 1.0.

## Updated capability states

These states are deliberately not a single scalar score.

| Capability | RC7E state | Successor evidence | Updated state | Meaning |
|---|---|---|---|---|
| comparison | `UNOBSERVED` | RC7F-B partial safe; RC7F-B1 56/56, 0 false proposals | `BOUNDED_SAFE_MEASUREMENT_CANDIDATE` | The preregistered bounded comparison grammar is measurable; semantic warrant remains separate. |
| event-event ordering | `UNOBSERVED` | RC7F-C 44/44, 0 false proposals | `BOUNDED_SAFE_MEASUREMENT_CANDIDATE` | Explicit two-event `before/after` ordering is measurable; implicit chronology remains outside jurisdiction. |
| permission + exception/temporal composition | `PARTIAL` | RC7F-D 50/50, 0 false proposals | `BOUNDED_SAFE_MEASUREMENT_CANDIDATE` | The tested semantic norm composition is measurable; this is not operational execution permission. |
| assertion/scope semantic warrant | `SCOPE_UNSAFE` | RC7F-A reduced false permits 68→2; RC7F-A1 still produced 4 parenthetical false permits | `WARRANT_ARCHITECTURE_INCOMPLETE_UNSAFE` | Observation/scope is strongly discriminable, but current surface-matching warrant machinery still violates the zero-false-permit safety requirement. |

All original RC7E dimensions not directly tested by these successors retain their frozen RC7E state. No successor result silently broadens jurisdiction beyond its own cohort.

## Main inference

The successor results separate two questions that RC7E had entangled:

1. **Can CAL observe the semantic structure?**
2. **Does the source warrant CAL asserting the resulting proposition?**

For three formerly missing/partial families, the answer to (1) is now strongly positive within narrow frozen jurisdictions using non-LLM machinery.

For semantic warrant/scope, the answer to (2) remains **not yet safely solved**. RC7F-A1 is particularly informative because high scope-path accuracy coexisted with four unsafe permits. This reinforces the design rule that aggregate semantic accuracy is not an acceptable substitute for a false-permit safety gate.

## What the A1 falsifier changes

The next scope/warrant successor should **not** simply add `(` and `)` to the evidential-adverb regex and call the result independent evidence.

The smallest useful next hypothesis is structural:

- identify a wrapper/operator and its governed span independently of incidental punctuation;
- preserve multiple nested scopes as structure rather than a single winning label;
- derive assertion eligibility from the typed scope/warrant object;
- keep unsupported wrapper resolution fail-closed.

A small parser or deterministic tokenizer/constituency mechanism may still satisfy this without an LLM. The evidence does not currently justify an LLM lane merely because A1's surface matcher failed.

## Authority architecture implication

The evidence now favors a pipeline of the form:

```text
raw source
  -> non-authoritative semantic observations
  -> typed scope / embedding representation
  -> semantic-warrant evaluation
  -> warranted propositions
  -> downstream decision machinery
  -> separately typed operational authorization
```

Measurement confidence, reader agreement, or parser success does not grant semantic warrant.

A semantic permission observation also does not grant operational permission. The latter remains the Contract E authority domain unless future cross-domain experiments justify a common typed jurisdiction algebra.

## Current non-LLM posture

There is still no evidence-based reason to promote a generative LLM proposal lane.

Observed non-LLM progress since RC7E:

- comparison blind spot: bounded candidate recovered;
- explicit event-ordering blind spot: bounded candidate recovered;
- permission exception/temporal composition residue: bounded candidate recovered;
- semantic warrant: falsifier narrowed from broad role-binding overclaim to a specific structural wrapper/embedding problem.

This does not prove that all remaining language capability is achievable without an LLM. It shows that the currently isolated residues still admit smaller discriminating non-LLM tests.

## Remaining highest-priority uncertainty

**Semantic-warrant representation, not raw observation recall.**

The strongest next falsifier is whether a structural scope/warrant representation can achieve zero false permits on fresh wrapper, nesting, attribution, epistemic, deontic, conditional, quantifier, and contradiction cases without destroying direct-assertion recall.

Contract E should not be changed to absorb this conclusion while its independent semantic-recoverability reader cohort remains frozen and incomplete. After Contract E's current gate terminates, a separate successor can test whether semantic warrant and operational authority share a domain-typed jurisdiction algebra without allowing cross-domain laundering.

## Nonclaims

This synthesis does not promote any research candidate to production, change RC7E's terminal result, authorize a release or merge, establish universal semantic competence, establish source truth/reliability, or establish Contract E semantics.
