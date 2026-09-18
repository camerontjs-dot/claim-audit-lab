# CAL V1 Two-Registry Architecture RC0 — Terminal Result

Date: 2026-09-18

Classification: Draft Research / terminal candidate evidence. No merge or production promotion.

## Disposition

**SUPPORTED_CAL_V1_TWO_REGISTRY_RC0.**

The exact candidate at `7f093e954c2554c3bf21c8bd72d36550414bf54b` supports the bounded two-registry CAL architecture:

- existing `SemanticFamilyRegistry` remains the atomic semantic-authority path;
- separate `CompositionRegistry` derives bounded relations only from already-warranted authorities plus explicit integration state and query;
- the first and only registered composition module is `quantitative_change_exact_v1`;
- existing atomic engine, family registry, authority, measurement, relation, and model files remain byte-identical to the qualified M4 base.

## Exact lineage

- M4 base/result head: `607ec560fd53bd56279193a8d39a48b6f80e1012`
- M4 qualified implementation: `a18e07ef17e02d83930bea5344624cd9368ae2fc`
- two-registry preregistration: `8fbec89d5787ca7505c16d0d991c991de321e672`
- exact qualified candidate: `7f093e954c2554c3bf21c8bd72d36550414bf54b`
- decisive qualification run: `35365267744`

## Decisive run

Run `35365267744`: PASS.

Observed gates:

- preregistration freeze: PASS;
- inherited semantic-source byte guard: PASS;
- inherited atomic registry / shadow / ledger tests: PASS;
- composition-registry falsifiers: PASS;
- full-history regression: PASS;
- static checks: PASS.

Counts on the exact candidate:

- inherited targeted gates: 28 passed;
- composition-specific gate: 25 passed;
- repository-wide regression: **1086 passed, 5 skipped, 48 deselected**.

## Composition result

The candidate demonstrates:

1. immutable, duplicate-rejecting composition-module registration;
2. explicit module dispatch and fail-closed unknown-module behavior;
3. an authority-only composition input boundary;
4. rejection of unwarranted, foreign-family, cross-context, cross-evidence-world, or duplicate-identity inputs;
5. quantitative-change semantics based on explicit temporal rank rather than call order;
6. unresolved outcomes for unqualified approximation, intervals, identity mismatch, unit mismatch, metric mismatch, missing temporal establishment, or unsupported delta state;
7. exact reproduction of frozen portable vector CPV01 from CAL PR #175;
8. mutation-sensitive provenance-bearing composition receipts.

The candidate does not register scalar-value atomic production semantics. It accepts a normalized warranted-authority carrier at the composition boundary so atomic-family expansion remains a separate authority question.

## Preserved deviations

Pre-terminal failures are preserved:

- initial candidate collection failed because pytest reserves parameter name `request`;
- a first textual repair did not actually change all occurrences;
- a full-history run initially failed because the new research workflow omitted installation of `en_core_web_sm`;
- a later run passed all semantic tests but failed Ruff import hygiene;
- a subsequent run passed all semantic tests but failed only `ruff format --check`.

None of those repairs changed the preregistered architecture or quantitative semantics.

## Separate Public-suite defect

Public-suite run `35365267886` reports:

- **1085 passed, 5 skipped, 48 deselected, 1 failed**.

The sole failure is:

`tests/production/test_historical_golden_version_migration.py::test_historical_goldens_only_change_the_distribution_version`

because:

`git show 32275a239b68af383a56bca843e28cbc1e343976:tests/v1/fixtures/traces/01-supported-verbatim.json`

returns exit 128 because that historical object is unavailable.

This is the same inherited repository defect observed on prior qualified research heads and is not caused by the two-registry candidate.

## Architectural conclusion

The evidence supports freezing the V1 semantic core around two distinct authority mechanisms:

`SemanticFamilyRegistry + CompositionRegistry`

with fail-closed typed joins and provenance-bearing composition receipts.

The next missing V1 capability is not another semantic-family module. It is parent/child recomposition for exact Contract A `single` and declared `all_of` semantics.

## Nonclaims

This result does not authorize:

- production merge;
- release/tag;
- Contract C mutation;
- Decision Engine mutation;
- Evidence Bundler changes;
- new atomic-family production registration;
- decomposition recomposition;
- percentage/rate/uncertainty/unit-conversion semantics.
