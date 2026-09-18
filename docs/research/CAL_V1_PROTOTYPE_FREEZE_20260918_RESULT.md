# CAL V1 Prototype Freeze — Terminal Result

Date: 2026-09-18

Classification: Research prototype freeze. Not an official release, production promotion, tag, or authorization.

## Disposition

**CAL_V1_PROTOTYPE_FROZEN.**

The exact accepted freeze subject is:

`e24e405f5336ee024674f39dba97255bb58a2dd9`

Freeze ID:

`cal-v1-prototype-20260918`

Decisive workflow:

`35372362109` — **PASS**

## Exact acceptance evidence

On the exact freeze subject:

- frozen CAL source identity: PASS;
- exact external authority pins: PASS;
- Contract A 2.0 → EB #79 → Contract B 1.2 → CAL children → parent recomposition: **13 passed**;
- final semantic closure: **3 passed**;
- frozen architecture gates: **80 passed**;
- full-history repository regression: **1129 passed, 5 skipped, 48 deselected**;
- qualified-surface Ruff checks: PASS;
- strict mypy: PASS.

The workflow verified the exact Evidence Bundler #79 checkout and the exact historical typed-binary and attribute-state authority subjects.

## Separate Public-suite result

Public-suite run `35372362091` remains red with exactly one inherited repository-history defect.

Observed:

- **1112 passed, 9 skipped, 48 deselected, 1 failed**;
- sole failure: `test_historical_goldens_only_change_the_distribution_version`;
- cause: `git show 32275a239b68af383a56bca843e28cbc1e343976:tests/v1/fixtures/traces/01-supported-verbatim.json` exits 128 because the historical object is unavailable.

This defect predates the frozen V1 prototype and is preserved rather than counted as semantic evidence.

## Frozen architecture

The prototype freezes three distinct authority layers:

1. `SemanticFamilyRegistry` for atomic measure → warrant → proposition-relative relation;
2. `CompositionRegistry` for bounded derivation over already-warranted authority;
3. `DecompositionComposer` for exact Contract A root/single and declared `all_of` recomposition.

The native CAL result boundary remains the authoritative V1 prototype output boundary.

## Active runtime versus research-qualified extension

The active default atomic runtime remains deliberately narrow:

- `strict_comparison`;
- `direct_event_order`.

The registered composition runtime contains:

- `quantitative_change_exact_v1`.

However, ordinary A/B execution does not yet produce active scalar-value atomic authority, so quantitative change is **not** claimed as ordinary end-to-end runtime behavior.

The wider research-qualified family/extension envelope remains evidence for promotion design, not proof that every family is wired into the current default runtime.

## Upstream boundary

The frozen integrated path pins:

- Contract A `2.0.0`;
- Evidence Bundler PR #79 head `4e1f6fe00e7c350b28f52bfea14f1f8988847884`;
- EB profile `eb-v1-integration-10x3-rc0`;
- Contract B `1.2.0` production lock `c314e53bd91c0736aa4370a364673b069aceb43e`.

## Downstream boundary

Canonical Contract C remains `1.0.0`.

Apparatus Contracts PR #107 established:

`C1_CANNOT_AUTHORITATIVELY_BIND_CAL_V1_DECOMPOSITION_RC0`.

This is preserved as a downstream boundary limitation, not repaired by overloading opaque C1 fields.

Decision Engine has not been requalified against the new native parent-decomposition surface.

## Final semantic closure

No additional atomic family is justified by the final two discriminators:

- explicit definition/equivalence collapses to closed typed-binary relation semantics;
- explicitly warranted entity existence collapses to closed functional attribute-state semantics.

These conclusions do not authorize arbitrary language parsing, synonym/ontology reasoning, equivalence substitution, mention→existence, or absence→nonexistence shortcuts.

## Preserved unsupported regions

The freeze does not establish, among other things:

- universal retrieval completeness;
- EB obligation-selector PR #119 as baseline authority;
- all research-qualified families as active runtime plugins;
- scalar-value end-to-end A/B wiring;
- percentage/rate/compound/uncertain quantitative change;
- rich spatial geometry/topology/routing;
- inferred causality;
- deep coreference;
- subset-derived deontic applicability/conflict resolution;
- Contract C 1.0 losslessness;
- Decision Engine compatibility with the new parent surface;
- official release or operational authorization.

## Authorized successor

The research question is closed for this prototype.

The smallest justified successor is:

> design a minimal promotion candidate against the real production base that makes only already-qualified V1 machinery reachable/packageable, without reopening semantic research.

Any new semantic capability must return to a separate research lane.
