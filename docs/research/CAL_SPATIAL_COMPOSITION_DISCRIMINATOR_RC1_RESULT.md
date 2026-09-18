# CAL Spatial Composition Discriminator RC1 — Result

Date: 2026-09-17

Classification: Draft Research / terminal post-authority composition discrimination.

## Disposition

**SUPPORTED FOR PROMOTION, bounded to metadata-driven typed-binary spatial composition.**

The tested result supports keeping the qualified spatial subset as predicate-specific composition over the closed `typed_binary_relation` family. It does not justify a separate atomic `spatial_relation` family under the tested bounds.

## Exact evidence

- parent typed-binary Gate-1B candidate: `1641d349e4740bf439e90e12953fffa7439ee986`
- exact qualified candidate head before this result record: `e4e1e629be2ea1a58d394cc43f838104202d0523`
- dedicated qualification run: `35300652381`
- frozen evaluator controls: PASS
- candidate qualification: PASS
- parent `src/` and typed-binary Gate-1B isolation guards: PASS
- focused static checks: PASS

All frozen cases matched the oracle. Weak strategies were discriminated for universal transitivity, frame erasure, warrant erasure, and failure to normalize `IN`/`CONTAINS` and `NORTH_OF`/`SOUTH_OF` inverses.

## Supported boundary

Within this RC, composition may derive only:

- nested `IN` / `CONTAINS` relations;
- `NORTH_OF` / `SOUTH_OF` transitivity when both warranted premises share one established frame.

The composition refuses:

- adjacency and ownership transitivity;
- mixed-predicate chains;
- unknown or mismatched directional frames;
- unwarranted or negative premises;
- reused authority identity;
- self-relations produced by cycles.

Frame identity remains a composition modifier in this result, not a new atomic semantic family field.

## Preserved CI deviation

The ordinary Public suite on this branch is red only at the repository-level historical-golden migration check, where `git show 32275a239b68af383a56bca843e28cbc1e343976:tests/v1/fixtures/traces/01-supported-verbatim.json` exits 128.

The same exact failure is independently visible on the scalar parent lineage before either composition candidate existed, including Public-suite run `35297087826`. Both #166 and #167 therefore preserve the shared CI defect rather than treating it as semantic evidence.

## What is not established

This does not qualify:

- metric geometry or distance;
- topology beyond the tested containment chain;
- routes or coordinate systems;
- natural-language frame extraction;
- arbitrary spatial transitivity;
- production registration or runtime wiring;
- Contract C or Decision Engine behavior.

No merge, release, or production mutation is authorized by this result alone.
