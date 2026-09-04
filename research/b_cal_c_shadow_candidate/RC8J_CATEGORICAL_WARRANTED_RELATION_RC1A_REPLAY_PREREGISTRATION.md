# RC8J Categorical Warranted-Relation RC1A — Authority Replay Falsifier

## Classification

Draft Research Infrastructure / adversarial successor to RC1. Research-only. No production authorization.

## Frozen parent

- RC1 head: `598968205a5371323989f972442fb9820ba19b35`
- RC1 decisive run: `33868763522`
- RC1 reported bounded disposition: `SUPPORTED_WITH_BOUNDS`
- frozen RC8J candidate commit: `8e75c6782bb95c3763d06230b9c5df2b6af44054`
- frozen RC8J implementation blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`

RC1 is preserved unchanged. This successor does not repair it.

## Adversarial question

Does RC1 actually guarantee that the `WARRANTED` RC8J authority result supplied to `derive_categorical_relation()` belongs to the exact semantic atom payload from which the categorical relation is derived?

The frozen RC1 API accepts `case` and `authority_result` as separate inputs. Static inspection shows that `_require_warranted()` validates only authority status/reason, while `_extract_comparison_atom()` reads semantic identity and fields from the separate case object. RC1 does not encode or verify a cryptographic or structural binding between those two inputs.

## Decisive replay test

1. Construct a valid typed comparison case `A > B` using the same fixture seam as RC1.
2. Evaluate that exact case with the frozen RC8J evaluator and require `WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED`.
3. Mutate only the semantic proposal direction to `A < B` **without** updating the corresponding field warrant receipt. This mutated case must fail the frozen RC8J gate and therefore is not warranted.
4. Feed the mutated case to frozen RC1 `derive_categorical_relation()` together with the original `WARRANTED` authority result from step 2.
5. Compose any returned categorical relation with frozen RC1 scoreless composition.

## Falsifier

RC1 is falsified if the stale/replayed `WARRANTED` authority result allows the mutated non-warranted atom to produce a deciding `SUPPORTS` or `REFUTES` relation and a proposition verdict.

This is an instance of RC1's existing preregistered falsifier: **a non-`WARRANTED` atom can participate as deciding categorical evidence**.

## Passing condition

The replay attempt is refused because authority is bound to the exact atom payload/identity used for relation derivation. A refusal may be implemented by an exact subject identity/digest receipt or another equally strong binding, but this successor does not prescribe or add such a mechanism.

## Stop rule

If replay succeeds, record `FALSIFIED_AUTHORITY_RECEIPT_REPLAY` and stop. Do not patch RC1. Any binding repair is a new candidate revision.

If replay is refused, record the exact observed binding mechanism and bounded pass.

## Boundary

Do not modify RC1, RC8J, production `src/`, Contracts B/C, Decision Engine, release state, or any clean-room aperture. This successor adds only the adversarial test apparatus and receipt.