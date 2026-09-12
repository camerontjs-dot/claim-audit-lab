# CAL V1 RC1 fresh qualification terminal record

## Terminal qualification disposition

**SUPPORTED_BOUNDED_RC1_QUALIFICATION**

The exact frozen RC1 authority-integrity successor passed the complete pre-freeze repository gate and then passed the fresh 19-case post-freeze qualification with zero frozen-gold mismatches and zero unsafe results.

The RC1 implementation was not changed after freeze.

## Programme disposition

**BLOCKED ON SPECIFIC CONTRACT OR CONSUMER DECISION**

CAL's bounded V1 RC1 implementation is now qualified within the frozen claim. Pipeline promotion is still blocked because the required downstream representation is not canonical production authority:

1. Apparatus Contracts `main` remains `c3563cff66d2c85dcbf575c693056e2d8e4563d4`; the qualified in-band Contract C `non_deciding` successor remains Draft Research PR #85 and has no official successor version.
2. Contract C compatibility research PR #86 established that an in-band successor is a breaking-change/MAJOR signal and that semantic downgrade to released 1.0 is unsafe.
3. Research PR #87 established that a richer sidecar can technically preserve the missing state while leaving Contract C 1.0 unchanged, but this conflicts with Contract C's published boundary if Contract C itself must remain sufficient for downstream CAL-attributable result reconstruction.
4. Decision Engine research PR #67 independently consumed the in-band `non_deciding` representation safely, but maintained/release-qualified Decision V1 deliberately accepts exact released Contract C 1.0 only.
5. Decision Engine PR #68 and release-readiness PR #70 are merged into protected `main` (`7be709b2141c767c5da89b8b94cf90233c4238fe`), preserving that Contract C 1.0-only maintained boundary. PR #70 explicitly records release authority/tag/publication as withheld.

Therefore the next justified action is not another CAL semantic experiment. It is an operator-governed Contract C architecture/version decision followed, if the in-band successor is chosen, by the smallest maintained Decision Engine consumer port and cross-repository conformance qualification.

No such contract promotion or maintained downstream consumer mutation is performed by this qualification.

## Exact frozen implementation

- repository: `camerontjs-dot/claim-audit-lab`
- successor Draft PR: `#104`
- branch: `converge/cal-v1-candidate-rc1-authority-integrity-20260912`
- frozen RC1 commit: `a902621e8baea3063dddd7f92ba975aade305464`
- frozen RC1 tree: `0ad4434e4a897b39cda062917a3c1eb0968d11aa`
- failed parent candidate: `dca2ec7f2c117cc0b4d6c543ab5049cac7994298`
- failed parent evidence: Draft PR `#103`, `CAL_V1_QUALIFICATION_FAILED`

Freeze receipt:

- commit: `7e7356f8b4746288d1a0254a253adbb77fd30626`
- blob: `d10dbb9b8091c6ea045f4bc20d20cf597307b326`

Frozen authority-integrity implementation blobs:

- `authority_validation.py`: `73ee2cc8e26cc3945558f76fa8c0992441177a97`
- `relations.py`: `e9e9401c92ee11d25a50dbc36e80aeb4c4cd220d`
- RC1 regression test: `aacc755cf8cc4a1a1becb06bfdb5235bca558c5d`

All other CAL V1 candidate semantic source blobs remained identical to the failed parent.

## RC1 repair boundary

Before deriving a proposition-relative categorical relation, RC1 independently revalidates:

- exact warranted authority status/reason;
- authority context/world binding;
- atom-to-authority context/world binding;
- atom/proposition semantic-family agreement;
- atom passage/source membership in the exact admitted evidence world;
- atom semantic fields against independent source completion from the admitted passage;
- content-derived `atom_id`;
- content-derived `authority_id`.

This repairs the demonstrated parent failure where a rebound authority could rewrite supplied binding fields while retaining stale content-derived identities.

RC1 does **not** establish cryptographic origin authenticity for arbitrary external reconstructed receipts. Content hashes remain integrity identifiers, not signatures.

## Pre-freeze repository qualification

Exact RC1 head `a902621e8baea3063dddd7f92ba975aade305464` passed Public suite:

- run: `34674924671`
- job: `103502956632`
- merge-test SHA: `406950ed99f2ece1ed32e5e205c2973a884b26cd`
- pytest: `980 passed, 5 skipped, 48 deselected`;
- Ruff lint: PASS;
- Ruff format: PASS, `62 files already formatted`;
- mypy: PASS, `Success: no issues found in 61 source files`.

The immediately preceding run failed only Ruff formatting on the new verifier. The repair to reach this exact frozen head applied Ruff's canonical formatting and made no semantic change.

## Fresh qualification identities

Qualification branch / Draft evidence PR:

- branch: `research/cal-v1-rc1-qualification-20260912`
- Draft PR: `#105`

Fresh cohort:

- cohort ID: `cal-v1-rc1-fresh-q0-20260912`
- case count: `19`
- cohort commit: `f73ba1d2a15aafa5b9c8b2bc5c5dd73f86687ee7`
- `COHORT.json` blob: `8dbf1c6b6cd83b4fab5f3ee827caad366b8d0e8d`

Frozen gold:

- gold commit: `0e5cbdbc0de13111451c1b48218b7664b1fdd78b`
- `GOLD.json` blob: `c1484518d1e765800681f2d6c2fac38138db00d9`

Frozen evaluator:

- evaluator commit: `3830411fdd88889d61db6a21e6a1ef8998bab68d`
- evaluator blob: `017d21060d60a2c296b3139a9f293fb8a1b7561d`

Order was implementation freeze -> cohort freeze -> gold freeze -> evaluator freeze -> scoring. Gold did not change after scoring began.

## Decisive fresh execution

Public suite:

- run: `34675244077`
- job: `103503854205`
- PR merge-test SHA: `60233672df59a6dea039f8f116d430dba3d9e246`
- pytest: `981 passed, 5 skipped, 48 deselected`;
- fresh qualification mismatches: `0 / 19`;
- unsafe-result count: `0`;
- Ruff lint: PASS, `All checks passed!`;
- Ruff format: PASS, `62 files already formatted`;
- mypy: PASS, `Success: no issues found in 61 source files`;
- Public suite job: PASS.

The workflow uploads no Actions artifact. Durable observation record:

- observation commit: `dc1a3b0d6b66008e81c187d35da1fa12aca0c731`
- `QUALIFICATION_OBSERVATION.json` records the exact run/job, frozen identities, and case-class disposition.

Because the frozen evaluator accumulates every mismatch and asserts the mismatch map is empty, the successful job establishes that all compared fresh observations matched the pre-scoring gold. Passing pytest captured stdout rather than publishing the full observation JSON; the committed observation record therefore records verified comparison outcomes rather than inventing unexposed raw values.

## Authority-integrity pressure result

All authority/binding falsifiers passed:

- same-ID proposition substitution: rejected;
- changed passage under stale hash: rejected;
- ordinary stale-world authority: rejected;
- rebound authority with stale atom and authority identities: rejected on semantic-atom identity mismatch;
- rebound authority with recomputed atom ID but stale authority ID: rejected on semantic-authority identity mismatch;
- fully rehashed source-semantic polarity forgery: rejected because atom fields did not match independent source completion;
- fully rehashed semantic-family mutation: rejected on atom/proposition family mismatch.

The original parent Q12 unsafe acceptance is therefore not reproduced in RC1, and the repair survived three stronger mutation variants rather than only the original exact attack.

## Semantic-family result

### strict comparison

Fresh qualification matched frozen gold for:

- direct support;
- direct refutation;
- inverse/reversal relation;
- insufficient-evidence safe abstention;
- mixed support + refutation -> `not_checkable` / `MIXED_RELATIONS`;
- all authority-integrity/binding mutations above.

### direct event order

Fresh qualification matched frozen gold for:

- direct support;
- direct refutation;
- reporting/scope surface -> safe abstention.

The claim remains narrow direct narrator-level event ordering. No transitivity, coreference resolution, or general temporal QA is inferred.

### unsupported family

Permission/exception remained fail closed with `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY`; no historical v0.5 deciding fallback was observed.

## Contract C research projection result

Fresh projection controls matched frozen gold:

- supported result retained a neutral residual `non_deciding` contribution beside deciding support;
- safe-abstention projection remained `not_checkable` with `non_deciding` attribution;
- mixed support/counterevidence remained `not_checkable`;
- no `score`, `confidence`, `probability`, `winner`, or `rank` selection key was admitted by the no-scalar-winner control;
- no semantic strengthening was observed in the exercised research projection cases.

This qualifies only the research `research-non-deciding-rc0` representation used by CAL. It does not assign canonical Contract C production authority.

## Downstream live-state evidence

### Apparatus Contracts

Protected `main` remains:

`c3563cff66d2c85dcbf575c693056e2d8e4563d4`

Relevant research evidence remains Draft/unmerged:

- PR #85: `SUPPORTED_BOUNDED_TWO_LEAF_SHADOW_DELTA` for in-band `non_deciding`;
- PR #86: `SUPPORTED_PARALLEL_VERSIONING_AND_BREAKING_CHANGE_SIGNAL`; no safe downgrade to 1.0; MAJOR signal if in-band successor is promoted;
- PR #87: `SUPPORTED_RICHER_SIDECAR_TECHNICALLY_SUFFICIENT`; technical necessity of an in-band major revision is falsified, but Contract C-alone sufficiency remains the architectural conflict.

### Decision Engine

Protected `main` is now:

`7be709b2141c767c5da89b8b94cf90233c4238fe`

- PR #68 merged the bounded maintained Decision V1 architecture while deliberately retaining exact released Contract C 1.0 as the maintained raw authority family.
- PR #70 merged the qualified release-readiness tree, but its record explicitly withholds immutable tag/GitHub Release/release authority.
- research PR #67 independently demonstrated safe `non_deciding` consumption, exact provenance/multiplicity recovery, hostile-mutation rejection, and stable HOLD behavior, but remains research-only.

## What is now supported

Within the frozen bounded profile, CAL RC1 supports:

- immutable evidence-world/context binding;
- deterministic measurement for the two adopted semantic families;
- independent source completion before semantic authority;
- relation-consumer revalidation of source grounding and content-derived authority identity;
- proposition-relative categorical support/refutation/irrelevance/unresolved relation;
- scoreless fail-closed composition;
- mixed-evidence abstention;
- unsupported-family fail closure;
- audit-preserving non-deciding evidence projection to the qualified research Contract C shape.

## What remains unresolved

The remaining blocker is no longer a CAL semantic or authority-integrity defect demonstrated by this qualification.

An operator must resolve the Contract C representation boundary:

- promote an in-band exact-version successor, accepting the demonstrated breaking/MAJOR compatibility consequence; or
- explicitly authorize a composed Contract C 1.0 + immutable sidecar handoff despite Contract C's current published sufficiency boundary; or
- define another smaller contract architecture and qualify it.

If the in-band successor is selected, the next smallest engineering step is to port the already-supported PR #67 consumer behavior into a maintained Decision Engine successor surface, preserve exact 1.0 behavior in parallel, and run cross-repository CAL -> Contract C successor -> Decision conformance.

## Exact nonclaims

This record does **not** establish:

- canonical Contract C successor authority;
- a production Contract C version number;
- safe downgrade of `non_deciding` to Contract C 1.0;
- maintained Decision Engine support for `non_deciding`;
- cryptographic authenticity of arbitrary external semantic-authority receipts;
- generic NLU/NLI;
- general temporal reasoning;
- permission/exception deciding semantics;
- root/all-of composition;
- source truthworthiness or retrieval completeness;
- operational Authorization or execution permission;
- merge/release/tag/promotion authority for CAL RC1.

## Stop state

**SUPPORTED_BOUNDED_RC1_QUALIFICATION**

**Programme recommendation: BLOCKED ON SPECIFIC CONTRACT OR CONSUMER DECISION**

No merge, promotion, tag, release, Contract B/C mutation, Decision Engine maintained mutation, or further CAL semantic experiment is performed by this thread.
