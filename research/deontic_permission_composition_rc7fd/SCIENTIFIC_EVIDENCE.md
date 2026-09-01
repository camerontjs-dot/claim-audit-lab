# RC7F-D Deontic / Permission Scope Composition — Terminal Evidence

Status: **TERMINAL RESEARCH EVIDENCE**

Terminal token:

`DEONTIC_COMPOSITION_CANDIDATE_READY_FOR_HARDENING`

## Immutable lineage

- parent RC7E evidence: `34e9bcafad2c63c9b0761ffc456532344bc75b88`
- preregistration: `3219093b348b9ae81af58887489b26404bd0db16`
- apparatus freeze: `01a1d8d80fccdc96f82e85f678e463c32becd55f`
- qualification run: `33464797025`
- qualification artifact: `9784452070`
- qualification digest: `sha256:73b1522730d2bf1d28d9dea85ea006e5e10678c07455d7c402d6a3fe02ab481a`
- held-out cohort freeze: `56a7e091a30bc9a0055421542191f15d5d9cf836`
- accepted scientific run: `33464964947`
- scientific artifact: `9784507428`
- artifact ZIP digest: `sha256:b2f996cd24e62d9faf1a21e3345b00e7645ed1f6125fdc36eed8e9edb9449e4d`

The production `src/` guard passed. Candidate code was not changed after held-out creation.

## Scientific result

Accepted result over 64 cases, including 50 supported semantic permission-composition cases and 14 negative/unsupported controls:

- true positives: `50`
- false proposals: `0`
- misses: `0`
- typed precision: `1.000000`
- typed recall: `1.000000`
- exact composition accuracy: `1.000000`
- exception attachment accuracy: `1.000000`
- temporal relation/reference attachment accuracy: `1.000000`
- false proposals on negative/unsupported controls: `0`
- meaning-changing pair accuracy: `1.000000`

## Supported bounded observation jurisdiction

Permission core:

- `Only <population> may <predicate>`
- `Permission to <predicate> is restricted to <population>`

Explicit exception composition:

- `except`
- `excluding`
- `apart from`
- `save for`
- `with the exception of`

Explicit temporal composition:

- `before`
- `after`
- `until`
- `as of`

The candidate extracts what the source normatively states. It does **not** determine that an actor presently has real-world execution authority.

## Interpretation

RC7E's permission residue included permission combined with exception/temporal scope. RC7F-D shows that this bounded semantic composition can be measured non-generatively with no false proposals on the frozen controls.

This is a measurement candidate for hardening. Operational permission remains a separately typed authority problem.

## Design principle preserved

> **CAL may know that it observed something without claiming that it knows the thing is true. When warrant is incomplete, abstention is a successful outcome.**

A permission statement may be correctly observed as a semantic norm without granting operational authorization to anyone.

## Nonclaims

This record does not establish production Contract E semantics, execution authority, universal deontic logic, arbitrary nested normative composition, production CAL behavior, release, or merge.
