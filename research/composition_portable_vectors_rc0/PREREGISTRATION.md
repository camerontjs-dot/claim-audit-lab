# CAL Composition Portable Vectors RC0 — Preregistration

Date: 2026-09-18

Classification: Draft Research / producer-side portable-vector freeze.

## Authority

- composition carrier PR #173;
- exact qualified carrier candidate: `faf2825ee13fe0aea2fa68a520194d847f95f3ab`;
- terminal carrier result: `865bbeb30ae672c290be98f023b3c4711aba22a4`;
- candidate/mutation qualification run: `35353495559`.

## Question

Can the qualified common composition carrier be represented as deterministic bytes that an independent repository can consume without importing CAL code or producer-private Python objects?

## Bounded canonical profile

RC0 freezes `CAL-CANONICAL-JSON-BOUNDED-1`:

- UTF-8 encoding;
- object keys recursively sorted lexicographically;
- no insignificant whitespace;
- arrays preserve order;
- value domain limited to object, array, string, boolean, and integer;
- current vectors are ASCII-only.

RC0 does not claim full RFC 8785/JCS compatibility, floating-point canonicalization, Unicode normalization, or arbitrary JSON portability.

## Frozen vectors

Six vectors cover all representative module shapes used to qualify the common carrier, including SUPPORTS, REFUTES, and UNRESOLVED outcomes.

Expected exact vector-file SHA-256:

`sha256:11818e585780ff70b5bf00fe519463fb487dba9d191abb7810946ad43afebf39`

The producer-side test must prove:
1. exact vector-file byte identity;
2. every request reconstructs the qualified `CompositionRequest`;
3. exact #173 carrier output equals the frozen expected receipt;
4. all nested request digests and final receipt ids recompute under the bounded canonical profile.

## Next gate

After producer validation, copy these exact bytes into `camerontjs-dot/apparatus-contracts` and use an independently written consumer that imports no CAL code.

Do not move expected receipt values or vector bytes to fit the independent consumer.

No production mutation, final wire-schema selection, merge, or release.
