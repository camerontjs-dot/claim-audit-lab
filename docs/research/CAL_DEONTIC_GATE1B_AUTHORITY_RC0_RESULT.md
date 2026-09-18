# CAL Deontic Gate-1B Authority RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / independent source-completion and warrant qualification.

## Frozen lineage

- terminal Gate-1A parent: `786a77eedd872ca22fea75106cf224d8e19fe02a`
- pre-candidate apparatus head: `5581e5423ae738c4728b67f1abb1994972d0f0bd`
- first exposed candidate head: `6f2d816d05ba5285b3395ed1be6272fcf7c5e139`
- semantic-green/static-red run: `35295204182`
- exact terminal head: `60298c99e8eb16cdad01f3c652cead83cad02992`
- dedicated terminal run: `35295516172`

## Disposition

**SUPPORTED_GATE1B_DEONTIC_RC0.**

The independently written source completer reconstructs the bounded deontic norm and warrants only when every measured semantic field equals the source reconstruction exactly.

## Qualified fields

Exact agreement is required for:
- mode: PERMITTED / PROHIBITED / OBLIGATORY / PERMISSION_RESTRICTED_TO;
- subject;
- action;
- exception set;
- condition;
- temporal relation;
- temporal reference.

## Falsifiers

The frozen evaluator mutates one field at a time and requires refusal. The candidate refused all mutations, including:
- mode flip;
- actor swap;
- action swap;
- erased condition;
- erased temporal state;
- erased exception;
- restricted permission collapsed to ordinary permission.

The weak strategy that simply trusts the measured `Norm` is rejected by the same evaluator.

## Machinery consequence

The bounded family now has a qualified research path:

```
bounded direct deontic measurement
  -> typed Norm proposal
  -> independent source reconstruction
  -> exact full-field equality
  -> deontic warrant
  -> Gate-0 deontic relation algebra
```

The authority parser is independent from the Gate-1A measurement function. Broader dependency parsing remains a shadow/diagnostic instrument, not authority.

## Preserved deviations

The first exposed candidate was semantically green but Ruff rejected frozen-evaluator import layout. A later import-order edit remained semantically green but Ruff still rejected the frozen layout. The terminal branch therefore adds a file-scoped `I001` suppression rather than altering evaluator semantics.

## Boundary

Research qualification only. No production plugin, Contract C/Decision behavior, merge, or release is authorized. End-stage pressure testing remains deferred until every family is finalized.
