# RC8E Results: Same-Source Whole-Atom Identity Falsifier

## Disposition

**FALSIFIED.** Frozen RC8D is not a sufficient end-to-end authority receipt because it does not bind an internally consistent authority bundle to the target atom being assessed.

## Frozen parent and apparatus

- parent: RC8D
- RC8D candidate blob: `f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1`
- RC8B dependency blob: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`
- RC8E preregistration commit: `f4abc96e197a5a04185e573296852b4dadc48f62`
- RC8E apparatus freeze head: `53f2fe8233c33e52609a258d5bd6883678e24881`

Pre-reveal run `33659920378`, job `100347660622`, verified the frozen parent, apparatus identities, unchanged production surface, and candidate-blind structural tests before any RC8E candidate execution.

## Reveal

GitHub Actions run `33660009114`, job `100347951972`:

- production surface verification: success;
- frozen parent/apparatus reverification: success;
- evaluator execution: success;
- artifact upload: success;
- hard safety criterion: **failure**.

Artifact:

- ID: `9858276262`
- name: `rc8e-atom-identity-33660009114`
- digest: `sha256:9f617f12aa83c40ae3c79be87156fda07616812fcfa5890443fe725efe592d30`

## Exact result

- cases: **10**
- status exact: **7 / 10**
- typed reason exact: **6 / 10**
- unsafe warranted atoms: **3**
- atom-binding cases non-warranted: **1 / 4**
- bank invariance: **pass**
- scientific state: `RC8D_WHOLE_ATOM_BINDING_FALSIFIED_OR_REGRESSED`

Unsafe rows:

1. `E-TRANSPLANT`: complete internally consistent atom-B receipt bundle attached to target atom A in the same admitted source was observed as `WARRANTED`.
2. `E-TARGET-MISSING`: missing target atom identity was observed as `WARRANTED`.
3. `E-SUBJECT-ATOM-MISSING`: missing authority-bundle atom identity was observed as `WARRANTED`.

The atom-mismatch-plus-subreceipt-mismatch case was rejected, but for the later subordinate-subject mismatch rather than the atom mismatch. This shows that RC8D has no atom-binding precedence layer.

## What this localizes

### Observed

RC8D correctly preserved source mismatch precedence, execution failure precedence, evidence rejection precedence, and reader/instrument-count non-authority.

### Inference

The defect is not source anchoring. The defect is the missing binding between:

- the atom/consumer slot whose authority is being assessed; and
- the atom identity to which the otherwise-valid authority bundle belongs.

Because the transplantation control held admitted source, source span, semantic values, operator domain, governed span, and field-warrant values constant, value or source checks could not detect the substitution.

## Successor constraint

Preserve RC8D unchanged. The smallest successor should add exactly one atom-identity layer after execution/evidence/source anchoring but before RC8B subordinate receipt checks:

- missing target or authority atom identity -> `UNRESOLVED`;
- explicit mismatch -> `REJECTED`;
- exact match -> continue through frozen RC8D.

Reader count, instrument count, confidence, voting, or agreement must not gain authority.

## Not established

RC8E does not determine how atom identities should be canonically generated, authenticated, or projected across contracts. It does not establish source-byte/content binding, natural-language semantic recovery, production readiness, or independent recoverability.
