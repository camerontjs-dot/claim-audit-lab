# CAL V1 Target Authoring / Conformance RC0 — 2026-10-01

## Classification

Draft research experiment against the exact qualified CAL V1 Slice 2 parent-bound candidate.

This branch does not promote, version, merge, or release a target authoring capability. It does not change the frozen CAL semantic implementation, DecompositionComposer, `run-bundle`, parent-bound runtime, or Contract C authority.

## Exact subject

CAL base:

- PR #183 qualified head: `ddaf94551e38663920593cab89f9c60d43c1555f`
- tree: `1677a1de987a594f4ee8d2670d56943c5f189fbd`
- semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`
- frozen DecompositionComposer blob: `268d0dc4dd22ddde3848141d62b7d719e48d374d`

Pre-existing trusted-target oracle:

- frozen CAL fixture source: `e24e405f5336ee024674f39dba97255bb58a2dd9`
- exact Evidence Bundler: `4e1f6fe00e7c350b28f52bfea14f1f8988847884`
- Contract B: `1.2.0`

Contract C remains external and is not consumed by this experiment.

## Prior observation

PR #182 established a specific seam:

- existing `validate-bundle` binds target identity and exact claim-text hash;
- it does not establish semantic correspondence between the claim text and family-specific target fields;
- structurally valid targets can carry missing family fields, unsupported directions, extra ignored semantic fields, reversed comparison direction, swapped entity orientation, or an inactive family;
- frozen CAL then either fails closed at execution or, for some semantically drifted targets, can issue a terminal verdict over the typed proposition it was given.

That evidence supports keeping the frozen runtime unchanged and moving the next question to target authoring/conformance.

## Research question

Can a deterministic bounded authoring/conformance path produce trusted targets for the two active CAL V1 semantic families while rejecting the PR #182 semantic-drift cases before frozen CAL execution?

## Claim under review

A conservative target seam can be qualified without changing CAL V1 semantics if:

1. target authoring derives only the fields already consumed by the two active families;
2. out-of-aperture or ambiguous claim forms are rejected rather than guessed;
3. conformance independently re-authors the expected target from the exact Contract B claim text and requires an exact family/field-map match;
4. the pre-existing structural validator remains a deliberately weak control and is not silently redefined;
5. authored targets reproduce the pre-existing trusted targets and frozen CAL behavior exactly.

## Boundaries

### In scope

- `strict_comparison`;
- `direct_event_order`;
- deterministic claim-text → typed-target authoring for a deliberately narrow grammar;
- exact Contract B claim binding;
- target conformance before CAL execution;
- frozen-oracle equivalence;
- mutation and weak-control discrimination.

### Protected / prohibited

The experiment may not change:

- `src/claim_audit_lab/production_v1/semantic/**`;
- frozen DecompositionComposer bytes;
- `bundle_input.py`;
- `bundle_cli.py`;
- `execution.py`;
- parent-bound runtime/CLI;
- `pyproject.toml`;
- Contract C or any Apparatus contract;
- CAL conclusion semantics or failure precedence;
- existing `run-bundle` behavior.

No version number or promotion decision is part of this question.

## Candidate mechanism

The research candidate adds a separate authoring/conformance module.

Authoring:

- reads the exact claim text from released Contract B 1.2;
- maps only an unambiguous supported claim form to one active family;
- emits the existing target shape;
- rejects unsupported, ambiguous, qualified, or currently unsupported negative-event forms.

Conformance:

- first runs the existing Contract B / target structural-binding path unchanged;
- independently authors the expected target from the exact claim text;
- requires the target's active semantic family and complete field map to match exactly;
- treats JSON formatting as non-semantic.

The candidate is intentionally narrower than the runtime grammar. Failure to author is an explicit stop, not a fallback to guessed fields.

## Competing explanations / alternatives

### A. Target authoring is the missing seam

If the new path exactly reproduces pre-existing trusted targets and rejects the known semantic-drift mutations while frozen CAL remains unchanged, the PR #182 gap is primarily an authoring/conformance boundary problem.

### B. Frozen CAL semantics must change

This would gain support only if correctly authored/conformant targets still reproduce the unsafe direction or identity behavior at the runtime seam. This experiment does not authorize that change.

### C. The target representation is insufficient for safe unattended authoring

This remains live if common canonical claims cannot be mapped without ambiguity, if the weak controls also pass the new conformance gate, or if target equivalence does not preserve frozen runtime behavior.

## Preregistered acceptance

All of the following are required:

1. exact base ancestry at `ddaf94551e38663920593cab89f9c60d43c1555f`;
2. protected CAL runtime files are byte-identical to that base;
3. DecompositionComposer blob remains `268d0dc4dd22ddde3848141d62b7d719e48d374d`;
4. authored C1 `strict_comparison` target is byte-identical to the pre-existing frozen trusted target;
5. authored C2 `direct_event_order` target is byte-identical to the pre-existing frozen trusted target;
6. frozen CAL native runs from authored versus frozen trusted targets are byte-identical for both families;
7. the existing structural validator accepts the preregistered PR #182-style semantic-drift mutation set, preserving it as a meaningful weak control;
8. the new conformance path rejects every one of those same mutations;
9. semantically identical pretty-formatted JSON remains conformant while raw target identity changes;
10. out-of-aperture claim forms fail authoring explicitly;
11. clean-installed distribution can execute the research author/conform module;
12. ordinary CAL regression, Ruff, formatting, and strict mypy all pass.

## Preregistered falsifiers / negative outcomes

`FALSIFIED` if any of these occur:

- authored target differs semantically from the frozen trusted target for either active family;
- authored versus frozen-target execution changes native CAL output;
- a semantic-drift mutation passes the new conformance gate;
- target authoring silently guesses for an out-of-aperture claim;
- any protected runtime or semantic file changes are required.

`INCONCLUSIVE` if:

- the frozen trusted-target oracle or exact EB fixture cannot be reconstructed;
- the weak structural validator unexpectedly rejects enough mutations that the new gate's discrimination cannot be established;
- the evaluator/harness is changed after observing the decisive result in a way that could alter the conclusion.

`BLOCKED` if required exact GitHub authority or CI environment is unavailable.

## Weak-system discriminator

The existing `validate-bundle` path is the intentionally weak control.

For the known PR #182 target-drift cases, it should continue to accept structural/binding validity. The new conformer must reject those same cases for semantic mismatch. If both paths accept the mutations, this research question remains unsupported.

## Evidence outputs

The decisive workflow must preserve:

- machine-readable qualification result;
- exact candidate commit/tree receipt;
- built wheel/sdist hashes;
- frozen trusted and authored target bytes for both active families;
- CI run/job/artifact identities;
- any failure/deviation without rewriting it away.

## Stop rule

Do not change frozen CAL semantics to make this experiment pass.

Stop on a protected-boundary change, target/runtime divergence, conformance false negative, evaluator deviation that could alter the result, or inability to reconstruct the exact frozen oracle.

A passing research result may justify a later minimal promotion review of the authoring/conformance seam. It does not itself assign a CAL version, change `run-bundle`, or move Contract C into CAL.
