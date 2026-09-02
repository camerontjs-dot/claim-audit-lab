# RC8 Authority Architecture Candidate

## Supported distinction graph

The current evidence supports keeping these authority questions separate:

`evidence binding -> source assertion -> interpretation -> operator jurisdiction -> atom warrant -> composition warrant -> epistemic conclusion`

They are not a confidence ladder. A later stage cannot repair missing authority in an earlier stage merely by agreement or additional measurement.

## 1. Evidence authority

Evidence authority answers only whether the source/passage is legitimately present in CAL's validated Contract B input and admitted semantic-measurement context.

Contract B factual context, history, anchors, and aperture observations remain evidence-world state. They do not become proposition-specific semantic authority merely because they are integrity-bound.

## 2. Source/assertion authority

A local semantic event can be observed without being a narrator-level factual assertion.

The authority layer therefore requires an assertion state plus structural scope path. For the proposed narrator-level atom:

- `asserted` may proceed;
- `not_asserted` rejects narrator-level authority while preserving the local observation;
- `unknown` remains unresolved.

Attribution, quotation, conditional scope, hypotheticals, deontic embedding, epistemic/evidential qualification, quantifier scope, parenthetical wrappers, exceptions/exclusions, and other embeddings are scope structures, not automatically factual assertions.

## 3. Interpretation authority

Each material atom field has one of:

- `established`: the source establishes the typed value;
- `semantic_unknown`: the source establishes that the semantic value is unknown;
- `extraction_unresolved`: CAL failed to recover a unique value;
- `insufficient_authority`: CAL recovered a candidate but lacks source/warrant authority to establish it;
- `absent_not_applicable`: the field is absent because it is not part of the relevant source construction.

Only `established` and a matching source-established `semantic_unknown` can satisfy a required field. Extraction failure and insufficient authority never become ordinary semantic unknown.

## 4. Operator jurisdiction

Each operator receipt binds:

- operator identity;
- semantic domain/family;
- applicability: `applicable`, `inapplicable`, or `unknown`;
- governed source span;
- material fields within jurisdiction.

`inapplicable` rejects authority for the proposed atom. `unknown` leaves authority unresolved. Correct family recognition is insufficient if the span or material field lies outside jurisdiction.

## 5. Atom-level warrant

An atom is warranted only when every material field matches a source-supported field receipt and all earlier gates are satisfied.

A partially correct atom does not inherit full authority. Unsupported extra modifiers reject the atom rather than being silently dropped. Role direction, subclass direction, polarity, quantity, unit, comparison direction, necessary/sufficient direction, quantifier, exception and temporal attachments are material whenever the atom schema declares them material.

## 6. Composition authority

Warranted components do not automatically warrant their composition.

When a proposition depends on composition, the receipt must separately establish the composition state and basis. The candidate distinguishes at least:

- warranted composition;
- rejected composition;
- unresolved composition.

Composition type remains a typed basis detail, e.g. conjunction, alternatives, all-members-required, existential support, conflict/coexistence, or incomplete multi-passage composition. This RC does not claim that every such composition rule is implemented.

## 7. Epistemic authority

Only warranted atoms under warranted required composition may strengthen CAL's epistemic conclusion. This authority remains CAL epistemic state, not Decision Engine policy and not operational authorization.

## State transition

```text
OBSERVED / PROPOSED
  -> execution check
  -> evidence binding
  -> assertion/scope
  -> operator jurisdiction/applicability
  -> per-field interpretation warrant
  -> required composition/aperture checks
  -> WARRANTED | REJECTED | UNRESOLVED
```

Execution failure exits this transition as `NO_ASSESSMENT`; it is not an epistemic unresolved state.

## Why no scalar confidence

Existing falsifiers show that agreement, parser success, and additional instruments can coexist with shared error and authority growth. A scalar could rank observations for diagnostic use, but it has no demonstrated authority transition in this architecture and therefore carries no normative role.

## Minimal receipt surface under test

Authority-bearing inputs:

- exact evidence/source identity and admitted state;
- exact proposed atom and its source span;
- assertion state and scope path;
- operator domain, applicability, governed span, and jurisdiction fields;
- per-material-field status and value;
- composition basis/state only when composition is required;
- aperture state only when the proposition requires aperture/completeness authority;
- separate execution state.

Diagnostic-only/non-authority metadata may include implementation identity or interpretation-rule provenance. Reader count, instrument count, confidence, and agreement do not strengthen authority.

## Receipt-field failure modes

- source/evidence identity: prevents receipt substitution across evidence;
- source span: prevents a correct local reading from being transplanted to an unsupported span;
- assertion/scope: prevents local observations under wrappers/embedding from becoming narrator facts;
- operator domain/applicability: prevents cross-domain and inapplicable-operator laundering;
- per-field status/value: prevents extraction failure, semantic-unknown laundering, role/direction/value mutations, and partially correct atoms from becoming fully authoritative;
- composition basis/state: prevents valid components from automatically authorizing a whole;
- aperture state: prevents bounded/unknown search scope from becoming an absence/completeness conclusion;
- execution state: prevents failed assessment from becoming epistemic abstention or authority.

No generic confidence field is justified.
