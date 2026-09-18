# CAL Attribute State Gate-1B Authority RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / independent source-completion and warrant qualification.

## Frozen lineage

- terminal Gate-1A RC1 parent: `08c198ee009f389b6386383c289494f2a44c2a9a`
- pre-candidate apparatus head: `997e2d7f22c97a5a580657aa2eba125869dc3bb5`
- exact qualified candidate head: `9f74ac0a2d0054cec1683cea96691b744bbb2067`
- dedicated qualification run: `35297311335`

## Disposition

**SUPPORTED_GATE1B_ATTRIBUTE_STATE_RC0.**

The independent source completer reconstructs the bounded declared state atom and warrants only exact agreement with the Gate-1A measurement.

## Qualified state

Authority preserves:
- entity;
- attribute;
- domain;
- value;
- functional vs non-functional declaration.

The candidate correctly preserves alternate bindings that previously exposed the invalid RC0 measurement evaluator, including `other_batch / batch_status` and `document / document_status`.

## Falsifiers

The frozen evaluator mutates entity, attribute, domain, value, and functional state. Every mutation is refused. A weak trust-measurement authority is rejected.

## Machinery consequence

```
conservative declared-state measurement
  -> StateAtom
  -> independent declared-state source reconstruction
  -> exact atom equality
  -> state warrant
  -> Gate-0 functional/closed attribute-state algebra
```

This remains a narrow declared-state family, not a generic subject-predicate-value catch-all.

## Boundary

No ontology acquisition, temporal-state reasoning, event-to-state inference, production wiring, merge, or release. Broad pressure testing remains deferred until every family is finalized.
