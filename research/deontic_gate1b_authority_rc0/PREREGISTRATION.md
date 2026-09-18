# CAL Deontic Gate-1B Authority RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / independent source-completion and warrant qualification.

Parent: terminal Deontic Gate-1A branch head `786a77eedd872ca22fea75106cf224d8e19fe02a`.
Selected measurement path: `direct_grammar`.

## Question

Can a deontic authority layer independently reconstruct the exact bounded norm from source text and refuse a measurement whose material semantic fields do not match that independent reconstruction?

## Frozen clean jurisdiction

The source completer must warrant the already-qualified direct-grammar forms for:
- permission;
- prohibition;
- obligation;
- restricted permission;
- explicit permitted/prohibited/required wording;
- alternate actor/action bindings;
- simple condition;
- simple temporal relation/reference;
- simple exception.

## Frozen mismatch falsifiers

Starting from a legitimately CLAIMED measurement, the evaluator mutates exactly one material field and requires refusal:
- mode;
- subject;
- action;
- condition;
- temporal relation/reference;
- exception set;
- restricted-permission mode.

A source completer that merely trusts the measurement is therefore invalid.

## Warrant contract

A warrant candidate receives source text plus a CLAIMED measured `Norm`. It may warrant only if:
1. it independently parses the source without calling the Gate-1A measurement function;
2. the independently reconstructed `Norm` equals the measured `Norm` exactly;
3. every material modifier field is retained.

The candidate must fail closed outside this bounded source grammar.

## Acceptance

`SUPPORTED_GATE1B_DEONTIC_RC0` requires all clean cases warrant, every frozen mutated measurement is refused, replay is deterministic, the weak trust-measurement strategy is detected, and Gate-1A files remain unchanged.

No broad pressure-testing corpus is introduced here. That is deferred until all families are finalized.
