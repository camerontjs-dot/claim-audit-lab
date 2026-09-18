# CAL Population/Membership Gate-1B Authority RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / independent source-completion and warrant qualification.

## Frozen lineage

- terminal Gate-1A parent: `6002cb73f8dfe50dc17a40caca2a0bc412d13b3b`
- pre-candidate apparatus head: `c713fab128eb8b55b8f0d3eaf0660d47f121076d`
- first exposed candidate head: `60d94d0ca54b7f07f51c9c6c8e8c3bc83dd21537`
- semantic-green/static-red run: `35295445770`
- exact terminal head: `5d72475a65c3b6cf4190a048040fad8ee8b91156`
- dedicated terminal run: `35295601528`

## Disposition

**SUPPORTED_GATE1B_POPULATION_RC0.**

The independent source completer reconstructs one bounded `MembershipAtom` or `SubsetAtom` and warrants only exact agreement with the measured atom.

## Qualified identity

For membership atoms, authority preserves:
- entity;
- population;
- MEMBER vs NON_MEMBER polarity.

For subset atoms, authority preserves:
- child population;
- parent population;
- direction.

## Falsifiers

The frozen evaluator mutates:
- membership polarity;
- entity identity;
- population identity;
- subset direction;
- subset parent.

Every mutation is refused. A weak trust-measurement authority is rejected.

## Machinery consequence

The bounded family now has:

```
gated membership/subset measurement
  -> MembershipAtom | SubsetAtom proposal
  -> independent source reconstruction
  -> exact atom equality
  -> population warrant
  -> later, separately tested cross-passage composition
  -> Gate-0 population relation algebra
```

The authority step does not invent cross-passage inheritance. A membership passage and a subset passage remain separate warranted atoms.

## Preserved deviation

The first candidate run was semantically green but Ruff rejected the frozen evaluator import layout. The terminal branch uses a file-scoped `I001` suppression without changing evaluator semantics.

## Boundary

No general quantifier logic, temporal membership, class disjointness, role ontology, cross-passage inheritance qualification, production wiring, merge, or release is established. End-stage pressure testing remains deferred.
