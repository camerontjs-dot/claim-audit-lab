# RC8 Authority Architecture: Terminal Research Candidate

Status: **supported with bounds after RC8J prospective evaluation**.

This document describes the strongest architecture supported by the RC8 research programme. It is a research result, not production authorization.

## Supported distinction graph

The evidence supports keeping these questions separate:

`execution -> evidence admission -> source identity -> Contract B bundle -> admitted passage + extent -> Contract B claim -> atom identity -> source assertion -> operator jurisdiction -> field warrant -> composition/aperture -> epistemic conclusion`

This is not a confidence ladder. A later stage cannot repair missing authority in an earlier stage through agreement, reader count, instrument count, or scalar confidence.

## 1. Execution is orthogonal to epistemic state

Execution is evaluated before semantic authority.

- `completed`: proceed to authority assessment;
- `failed`: return `NO_ASSESSMENT / EXECUTION_FAILED`.

A failed assessment is not epistemic unresolved and must not be reported as an abstention caused by evidence or semantics.

## 2. Evidence admission

Evidence authority begins with whether evidence is legitimately admitted from the validated Contract B input.

- admitted evidence may proceed;
- non-admitted evidence rejects the proposed authority;
- Contract B factual context, history, anchors, and aperture observations remain evidence-world state and do not become proposition-specific semantic authority by integrity binding alone.

## 3. Contract B identity and coordinate chain

The supported research candidate binds the authority receipt to the already-validated Contract B chain rather than inventing a second integrity system.

The tested chain is:

1. admitted source identity;
2. validated Contract B bundle identity;
3. admitted Contract B passage identity;
4. admitted passage extent;
5. referenced Contract B claim identity;
6. target atom identity.

Each identity has an authority-subject counterpart. Missing bindings remain unresolved; mismatches reject.

### 3.1 Source identity

The authority receipt must refer to the same admitted source as the evidence context.

RC8C showed that an internally consistent receipt without this anchor can be attached to a different or missing source and still look valid.

### 3.2 Bundle and passage identity

The authority receipt must remain attached to the validated Contract B bundle and admitted passage.

Contract B remains the integrity authority for bundle and passage hashes. RC8 does not duplicate those hashes as a new semantic-authority mechanism.

RC8G showed that source + atom identity alone allowed bundle and passage substitution.

### 3.3 Admitted passage extent

The admitted passage extent must be present and typed. The proposal source span and every valid required-field support span must remain inside it.

Exact boundary equality is permitted. A proposal or field support crossing the admitted passage boundary rejects even when it remains inside the broader operator-governance span.

Malformed or missing admitted extent remains unresolved.

### 3.4 Contract B claim identity

The authority receipt must bind to the referenced Contract B `claim_id` before atom authority is considered.

RC8I showed that a receipt with the same source, bundle, passage, passage extent, atom and semantic material could be transplanted between distinct Contract B claims. Missing claim binding remained unsafe until made explicit.

### 3.5 Atom identity

Within the same source, passage and claim context, the authority receipt must also bind to the target atom.

RC8E showed that source binding alone does not prevent whole-atom transplantation between semantically identical same-source atoms.

The research does not establish how canonical atom IDs must be generated or prove that opaque IDs were generated honestly. That remains evidence debt.

## 4. Source/assertion authority

A local semantic event can be observed without being a narrator-level factual assertion.

The authority layer therefore keeps assertion state and structural scope separate from local semantic recognition:

- `asserted`: may proceed;
- `not_asserted`: rejects narrator-level authority while preserving the local observation;
- `unknown`: remains unresolved.

Attribution, quotation, conditional scope, hypotheticals, deontic embedding, epistemic/evidential qualification, quantifier scope, parenthetical wrappers, exceptions and exclusions are structural scope conditions. Local recognition under one of these structures is not automatically a narrator-level assertion.

## 5. Interpretation authority

Each material atom field has one of:

- `established`: the source establishes the typed value;
- `semantic_unknown`: the source establishes that the semantic value is unknown;
- `extraction_unresolved`: CAL failed to recover a unique value;
- `insufficient_authority`: CAL recovered a candidate but lacks warrant to establish it;
- `absent_not_applicable`: the field is absent because it does not apply to the source construction.

Only `established` and a matching source-established `semantic_unknown` can satisfy a required field.

Extraction failure and insufficient authority never become ordinary semantic unknown. This distinction is part of the fail-closed epistemic surface.

## 6. Operator jurisdiction

Each operator receipt binds:

- operator identity;
- semantic domain/family;
- applicability: `applicable`, `inapplicable`, or `unknown`;
- governed source span;
- material fields within jurisdiction;
- the same authority subject as the proposal being assessed.

`inapplicable` rejects authority for the proposed atom. `unknown` leaves authority unresolved. Correct family recognition is insufficient when the source span or material field lies outside the operator's jurisdiction.

The admitted Contract B passage extent and operator-governance span are independent boundaries. Both must be satisfied.

## 7. Atom-level warrant

An atom is warranted only when every material field matches its field receipt and all earlier identity, evidence, assertion and operator gates have passed.

A partially correct atom does not inherit full authority. Unsupported extra modifiers reject rather than being silently dropped.

Material fields include whichever fields the atom schema declares material, including role direction, subclass direction, polarity, quantity, unit, comparison direction, necessary/sufficient direction, quantifier, exception and temporal attachments.

Each required field must have:

- a receipt bound to the same authority subject;
- a typed interpretation status;
- a matching value when the status requires a value;
- a valid support span;
- support inside both admitted-passage extent and operator governance;
- operator jurisdiction over that field.

## 8. Composition authority

Warranted components do not automatically warrant their composition.

When a proposition depends on composition, a separately bound composition receipt must establish the composition state and basis.

The research candidate distinguishes:

- warranted composition;
- rejected composition;
- unresolved composition;
- not applicable when composition is not required.

The programme does not claim that every possible composition rule is implemented or scientifically established.

## 9. Aperture authority

Aperture/completeness authority is separate from local support.

When aperture is required, the receipt must separately establish a sufficient, rejected or unresolved aperture state and remain bound to the same authority subject.

Contract B aperture observations do not by themselves establish proposition-specific completeness.

## 10. Epistemic authority

Only warranted atoms under any required warranted composition and aperture may strengthen CAL's epistemic conclusion.

This is CAL epistemic authority only. It is not Decision Engine policy, operational authorization, a truth guarantee, or a Contract C projection rule.

## Supported state transition

```text
OBSERVED / PROPOSED
  -> execution
  -> evidence admitted
  -> source identity
  -> Contract B bundle identity
  -> Contract B passage identity
  -> admitted passage extent and containment
  -> Contract B claim identity
  -> atom identity
  -> proposal/assertion same-subject binding
  -> assertion/scope
  -> operator same-subject binding + jurisdiction/applicability
  -> required field same-subject binding + status/value/support
  -> required composition/aperture binding + state
  -> WARRANTED | REJECTED | UNRESOLVED
```

Execution failure exits as `NO_ASSESSMENT`.

## Why no scalar confidence, reader vote or instrument vote

Across the research history, agreement and additional instruments could coexist with shared structural errors. The prospective bank-growth controls remained invariant after the authority architecture was strengthened.

Reader count, instrument count and scalar confidence may remain diagnostic metadata. They have no demonstrated normative transition in this architecture.

## Falsification path that produced the current architecture

The current chain is not an a priori design claim. Each added binding followed a preserved failure:

- **RC8A:** unbound receipt fragments were substitutable;
- **RC8C:** internally consistent receipts were not anchored to admitted evidence source;
- **RC8E:** source binding did not prevent same-source atom transplantation;
- **RC8G:** source + atom binding did not prevent Contract B bundle/passage/span substitution;
- **RC8I:** source/bundle/passage/span/atom binding did not prevent cross-claim transplantation.

RC8B, RC8D, RC8F, RC8H and RC8J are the corresponding bounded successors. Failures remain part of the evidence record rather than being erased by the successful terminal candidate.

## Strongest supported candidate

RC8J:

- candidate blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`;
- exposed qualification: 268/268 exact status, 268/268 exact reason, 0 unsafe warrants;
- prospective heldout: 28/28 exact status, 28/28 exact reason, 0 unsafe warrants;
- prospective artifact: `9862475745`;
- artifact digest: `sha256:0f377934b1e4adb8e813fd6d5a7c7d2e679cf37ca882d21979ca5889b98141d0`.

## Remaining evidence debt

The programme has not established:

- canonical or collision-resistant atom-ID generation;
- honest derivation of opaque IDs;
- correctness of source-text interpretation;
- proposition truth;
- full composition semantics outside tested families;
- cryptographic authenticity beyond Contract B's existing integrity regime;
- Contract C projection sufficiency;
- production integration or release readiness;
- independent recoverability by a fresh implementation.

The next costly-to-fake evidence is independent implementation/reproduction from a frozen behavioral specification under a clean information aperture.
