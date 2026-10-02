# CAL V1 strict-comparison polarity successor RC0

Issue: #190

## Decision

Determine whether the #188 negation falsifier can be removed by preserving assertion polarity in the existing strict-comparison semantic path, without adding a phrase-exception subsystem or a new pipeline stage.

## Scientific base

- CAL #186 commit: `6bb0d60f3e2286123f56de5657de4e97d6374c63`
- CAL #186 tree: `6b09583c86800118862dd5428ce8508e6fc5f2e8`
- #188 counterexample freeze: `9bd10b6fe86e3dd91808df906688d82abe9cb325446c859b26a00015187f747b`

Frozen falsifier:

- claim: `Alpha had a higher rate than Beta.`
- evidence: `Alpha did not have a higher rate than Beta.`
- V1 result: `supported`

## Hypothesis

The critical failure is caused by loss of source polarity in the strict-comparison semantic representation before relation derivation. Preserving the polarity required to interpret the comparison should eliminate the falsifier while retaining the previously qualified positive comparison behavior.

## Protected boundary

This experiment may change only the smallest strict-comparison measurement, source-completion, authority, relation, representation, serialization/schema and test surfaces needed by the hypothesis.

Do not intentionally change:

- `direct_event_order`;
- Contract B or external Contract C;
- parent composition semantics;
- release/version metadata;
- broad target-authoring grammar;
- real-source coverage;
- raw/public interface policy.

Do not add a catalogue of negation phrases, synonym exceptions or case-specific overrides.

Do not map `not higher` to `lower`; equality remains possible.

## Frozen discriminator

The decisive evaluator must be frozen before target implementation and cover these properties:

1. Existing positive higher-direction support remains supported.
2. Existing positive opposite-direction evidence remains contradicted.
3. The exact frozen negation falsifier is contradicted for the positive higher claim.
4. The same `not higher` evidence does not support a lower claim; absent stronger warrant it is unresolved / `not_checkable`.
5. Entity swap plus comparison-direction inversion preserves the qualified relation.
6. Missing or unsafe polarity information fails closed rather than being guessed.

Retain relevant frozen #186 strict-comparison controls as regressions. Do not make authentic-source authoring coverage part of RC0 acceptance.

## Falsification

The hypothesis is falsified or materially weakened if the counterexample can only be removed by:

- phrase-specific exception machinery;
- unrelated broad grammar expansion;
- a compensating new pipeline stage;
- treating negation as the inverse comparison;
- or breaking qualified positive-comparison behavior without a stronger semantic justification.

Preserve the first decisive result. Do not repair a failed frozen evaluator and count the repair as the same experiment.

## Allowed dispositions

- `SUPPORTED_FOR_POLARITY_SUCCESSOR_QUALIFICATION`
- `FALSIFIED_REPRESENTATION_INSUFFICIENT`
- `INCONCLUSIVE_APPARATUS_INVALID`

No disposition authorizes merge, CAL 1.0 release, real-language expansion, or public-interface change.
