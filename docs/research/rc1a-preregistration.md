# CAL Epistemic Methodology RC1A — Preregistration and Information Aperture

Status: PRE-FREEZE RESEARCH RECORD

## Scientific question

Can a thin research-only wrapper around unchanged CAL v1 capture the minimum RC0B epistemic state during real execution, including genuine failure paths, while producing exactly the same successful v1 semantic measurements, trace semantics, and verdict as direct `run_audit`?

If the bounded wrapper clears the frozen apparatus, stop. No staged pipeline or historical-v2 comparison is authorized.

## Live production baseline observed before branch creation

- repository: `camerontjs-dot/claim-audit-lab`
- exact live `main`: `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`
- branch source: exact live `main`, not RC0B/RC1
- v1 runner blob: `db53f49745876b6158da0c233fb80916bbeaabaf`
- v1 pipeline blob: `dd67d0d35590d3052826ad697ce9fd11222fff6f`
- v1 intake blob: `d8b304a4259ec128e656f07ca628d8a0a88ddd69`
- v1 models blob: `755e0ef1757055905f3c8b76b7edc5e8ddc1fefd`
- Contract C implementation blob: `d6b32a44ef11109fe0ee91efa212d3904badf58c`
- Contract C implementation constant: `CONTRACT_C_VERSION = "1.0.0"`
- current C-B/schema version file blob: `26aaba0e86632e4d537006e45b0ec918d780b3b4` (`1.2.0`)
- current v1 trace-corpus tree: `7d6735da5f23f78efae479d3c99c1fd2f075f935`

The live base is byte-identical at commit identity to the base recorded by predecessor RC0B and RC1, so no production drift exists between those predecessor experiments and RC1A task start.

## Predecessor evidence admitted before freeze

- RC0B research head: `260e6eaf777675835ae1cf5c97f643f9e516d173`
- RC0B corrected evaluator freeze: `5d880110e39d0450af346fea91074eebaa2c2f96`
- RC0B durable result: `docs/research/results-05-rc0b-final.md`
- RC0B architecture finding: `MINIMAL STATE/POLICY CHANGE SUPPORTED`
- RC0B governance disposition: `SUPPORTED FOR PROMOTION`
- RC1 evaluator freeze: `7accb1d731d1b68cbadd2f62a0835fba8d6e0f1d`
- RC1 terminal head: `ad0dd6a53985e1cd1600818b54bec5138f7d73ea`
- RC1 durable result: `docs/research/results-06-rc1-receipt-replay-final.md`
- RC1 governance disposition: `INCONCLUSIVE`
- RC1 candidate result: NOT RUN because the frozen evaluator accepted post-hoc supplied state rather than requiring real execution-time capture.

## Pre-freeze information aperture

Authorized and inspected:

- durable CAL Pipeline governance records;
- exact live current production CAL v1;
- current Contract-B intake boundary;
- current v1 trace/model definitions;
- current Contract C 1.0.0 exporter surface;
- RC0B durable scientific result;
- RC1 terminal apparatus-failure record;
- current production test fixtures/public regression identities.

Not authorized before evaluator freeze and not inspected or implemented:

- any RC1A candidate wrapper;
- any pre-existing experimental wrapper solving this exact task;
- historical-v2 implementation details beyond predecessor durable result statements;
- any RC1A candidate output/result;
- any solution mechanism capable of leaking a candidate design into evaluator construction.

## Protected production surfaces

RC1A must not modify v1 semantic measurement implementations, `run_audit`, verdict logic, production rules/thresholds/models/config semantics, Contract-B intake semantics, Contract C 1.0.0, Evidence Bundler, Decision Engine, release metadata/assets, or historical v2.

Any candidate must remain research-only. If a required state proves unobservable without altering a protected production surface, stop and record that boundary failure rather than widening scope.

## Frozen-evaluator stopping discipline

Before candidate implementation:

1. freeze the successful real-execution lane and genuine failure lane;
2. freeze all 13 gates and exact invariance surfaces;
3. freeze regression/fixture identities;
4. freeze W1-W6 weak controls;
5. execute weak controls against the frozen evaluator;
6. if any weak control clears its forbidden gate, terminate for apparatus defect;
7. only then implement the smallest research-only candidate.

If an evaluator defect is discovered after freeze, preserve it unchanged and terminate RC1A. A repaired evaluator would require a separately named successor experiment.
