# CAL Measurement Envelope RC0 Result

## Disposition

`SUPPORTED_WITH_BOUNDS`

## Exact candidate

- branch: `research/cal-measurement-envelope-rc0-20260909`
- decisive candidate head: `0658caab2edab510302923c0490836425c8a010b`
- frozen parent / base: `7a46d61585f868a2e904f870528f605fb06772ea`
- production `main` remained `32275a239b68af383a56bca843e28cbc1e343976` at experiment start

## Decisive execution

GitHub Actions run `34431468666`: PASS.

Artifact:

- id: `10134635566`
- name: `cal-measurement-envelope-rc0-34431468666`
- digest: `sha256:c146b9c710fc4cf42b9f31f409a40791f87b7a1d24b8e3ad21b6c5de6ad8d374`

Terminal evaluator output:

- research disposition: `SUPPORTED_WITH_BOUNDS`
- audit context: `sha256:e23682b9485b9bee585a381be96188a454be6fcab2570abb665d837ab2385737`
- measurement ledger: `sha256:70ad6a7fba6cb1b21531df37c2c0f16ce8ebd8c6ea248e455c67ca2a62b1ed34`
- preregistered falsifiers passed: 10/10

## Observed result

The common envelope carried two exact frozen measurement instruments under the same audit-context binding:

1. RC7F-B1 strict comparison, `0ecdedc5cea970485a635508255f3670ab231c33` / blob `33820f55e2a87c4de6336fca6b5e5b93a2bccde3`;
2. RC7F-C explicit event ordering, `e8d33913db66ad21027dffdf731d50f7a0977c8f` / blob `3e29b0e2ec5d9ba2d873d1584e76635147e421aa`.

Both receipts:

- bound to the exact same full `AuditContext` hash;
- exposed the full admitted passage-ID set as available context;
- separately declared the exact passage each instrument consumed;
- preserved the raw frozen instrument output exactly;
- remained deterministic on repeat execution;
- carried `authority_state=NOT_EVALUATED`.

The ledger retained a third admitted passage that neither positive-control measurement consumed. It remained reconstructable after both receipts were appended.

Receipt insertion order `[strict,event]` versus `[event,strict]` produced the same canonical ledger payload and ledger hash.

## Mutation / falsifier results

All preregistered controls failed closed as intended:

- original claim mutation -> context binding mismatch;
- typed proposition mutation -> context binding mismatch;
- Contract B bundle-hash mutation -> context binding mismatch;
- admitted passage-set mutation -> context binding mismatch;
- passage-text mutation while retaining stale declared passage hash -> context binding mismatch;
- foreign consumed passage -> refused outside admission;
- consumed span outside passage -> refused;
- available-context omission -> refused;
- raw proposal mutation with stale receipt identity -> refused;
- attempt to set a measurement receipt to `WARRANTED` -> `AUTHORITY_LAUNDERING` refusal.

## Bounded conclusion

The experiment supports a common information-preserving CAL measurement envelope for at least the two exercised bounded measurement families. A narrow measurement can consume a subset of the admitted evidence without shrinking the audit record seen by later stages, and multiple measurement families can coexist under one family-neutral receipt surface.

The result does **not** establish:

- semantic authority from a measurement receipt;
- event-ordering warrant or proposition-relative temporal relation;
- generic semantic competence;
- learned-entailer validity;
- root composition;
- production CAL architecture;
- release, merge or promotion.

The content hashes used here establish deterministic content identity/integrity inside the research apparatus. They are not issuer authentication.

## Smallest justified successor

Preregister a separate event-ordering authority/warrant experiment. Determine which exact event identities, event polarity, temporal relation, cue/source spans, admitted evidence binding, operator jurisdiction/applicability, and proposition identity must be established before an explicit event-order measurement may participate in a proposition-relative categorical relation.

Do not modify this candidate to widen its conclusion and do not reuse the comparison authority family merely because its shape is convenient.
