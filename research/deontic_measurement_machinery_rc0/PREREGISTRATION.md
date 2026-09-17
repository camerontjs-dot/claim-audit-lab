# CAL Deontic Measurement Machinery RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / Gate-1A measurement-machinery discrimination.

Parent: terminal Deontic Gate-0 branch head `7f1e63a17b18c14fe23c3fed00c7faf102bc62e7`.
Qualified typed-contract authority remains Gate-0 exact head `791cd59fa47ba8e7a709f289584468aa9e255334`.

## Question

Given the already-qualified bounded `deontic_norm` typed contract, what kind of measurement machinery can safely propose that typed state from ordinary evidence text across materially different claim forms?

This experiment compares three proposal mechanisms under one frozen corpus and evaluator:

1. bounded direct grammar / regex;
2. dependency-aware spaCy parsing;
3. conservative hybrid routing over those instruments.

No instrument is semantic authority. A later Gate-1B experiment must independently reconstruct source semantics before warrant.

## Claim-shape buckets

The corpus freezes three distinct buckets before candidate machinery exists.

### MUST_HANDLE

Canonical forms the first production-intent measurement path would need to parse exactly, including:

- direct permission;
- direct prohibition;
- direct obligation;
- permission restricted to a population;
- explicit lexical forms such as permitted/prohibited/required;
- simple condition, exception, and temporal bindings.

A candidate is not qualifiable if any MUST_HANDLE case is missing or has the wrong typed fields.

### DIAGNOSTIC

Harder but clearly relevant forms used to compare machinery without pretending they are already required production coverage:

- passive voice;
- regulatory `shall`;
- alternate restricted-to wording;
- unfamiliar but structurally similar actions;
- simple attributed policy language.

A diagnostic case may be exact or unresolved. A claimed wrong parse is a failure.

### FAIL_CLOSED

Surfaces where broad lexical matching could manufacture unsafe deontic state:

- epistemic `may`;
- ambiguous `may not`;
- negated obligation;
- reporting/quotation wrappers;
- multi-action or disjunctive scope;
- nested condition/exception structures;
- cross-family uses of modal words.

A candidate claiming a typed deontic norm on these controls is unsafe for this RC0.

## Frozen typed state

The measurement proposal may contain only the Gate-0 fields:

- mode;
- subject;
- action;
- exceptions;
- condition;
- temporal relation;
- temporal reference.

It may also return `UNRESOLVED` or `NOT_APPLICABLE`.

No confidence score participates in acceptance.

## Acceptance rule

A machinery candidate is `QUALIFIABLE_FOR_GATE1B` only if:

- every MUST_HANDLE case is `CLAIMED` with exact frozen semantics;
- zero FAIL_CLOSED case is `CLAIMED`;
- any DIAGNOSTIC `CLAIMED` output is exact;
- deterministic replay is exact;
- frozen metamorphic pairs preserve the expected semantic change;
- no production `src/` file changes.

Diagnostic recall is reported but does not compensate for unsafe claims.

## Weak strategies that the evaluator must kill

Before candidate implementation, the frozen evaluator must detect at least:

1. modal-cue matching that treats any `may` as permission;
2. modifier erasure;
3. `may not` coerced to prohibition;
4. reporting-wrapper erasure;
5. exact-mode-only parsing that ignores lexical permitted/prohibited/required forms.

## Metamorphic pairs

At minimum:

- `may` → `must not` changes PERMITTED → PROHIBITED;
- direct permission → `only` permission changes PERMITTED → PERMISSION_RESTRICTED_TO;
- adding `if QA approves` changes only the condition field;
- adding a reporting wrapper changes a direct claim to fail-closed;
- deontic `may release` → epistemic `may fail` must not preserve a deontic claim.

## Stop rules

Preserve a negative result if no machinery candidate satisfies the safety rule, if broadening recall requires unsafe modal/scope inference, or if candidate success requires mutating the frozen corpus/evaluator after exposure.

## Non-claims

A pass does not establish source-completion warrant, independent reproduction, universal deontic parsing, complete scope resolution, operational authorization, plugin registration, Contract C/Decision behavior, merge, or release.
