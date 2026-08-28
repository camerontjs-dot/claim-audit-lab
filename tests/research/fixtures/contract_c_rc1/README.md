# Contract C RC1 frozen fixtures

## Production-derived C0 fixtures

These files preserve content from CAL production SHA `33a928db97316a3652d57df9cafb8ca240305233`:

| Local fixture | Production source | Git blob SHA |
| --- | --- | --- |
| `c0-no-evidence.json` | `tests/v1/fixtures/traces/15-not-checkable-no-evidence.json` | `5090d01dc35243b0542f4618ce59a08b7bd0e54e` |
| `c0-no-entail.json` | `tests/v1/fixtures/traces/16-not-checkable-no-entail.json` | `bbef26b91d2abcaa5908276d0215f10d3eb5612b` |
| `c0-inf-02-contradicted-logging.json` | `tests/v1/fixtures/traces/inference/inf-02-contradicted-logging.json` | `49b9fc71caebc849ed8bf8a96a12f1ddd24947b1` |
| `c0-inf-03-numeric-uptime.json` | `tests/v1/fixtures/traces/inference/inf-03-numeric-uptime.json` | `0ec4404e7267a3cf82b3774e6acce139d1cfc6d4` |

The JSON formatting is not the object under test. Tests canonicalize JSON before byte-size comparisons.

Production `AuditTrace` does not contain the exact Contract-B bundle identity. Projector tests therefore supply a clearly named fixture-surrogate binding only to exercise projection behavior. The surrogate is not evidence of a real Contract-B lineage.

## Synthetic boundary-state control

`semantic-state-matrix.json` is synthetic. It exercises state distinctions already expressible at CAL's legitimate semantic boundary, including eligibility, semantic validity, aperture, temporal applicability, counterevidence, unresolved evidence, execution failure, and reassessment lineage.

It is not evidence that current production CAL emitted those exact candidate packages from the same execution.
