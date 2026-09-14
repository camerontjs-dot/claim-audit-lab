# CAL V1 Frozen Prototype RC0 — 10-Claim Smoke Protocol

Classification: preregistered integration/operational-learning smoke. It is not a benchmark, production qualification, semantic-family promotion, Contract C test, or automatic MainFrame action.

## Decision sentence

Run exactly 10 frozen real typed-claim packets through one exact frozen prototype head with no mid-run CAL semantic changes. The smoke passes as apparatus if all 10 inputs produce a terminal receipt or an explicitly localized input/harness failure, identities are recoverable, deterministic replay holds, and no downstream authority is manufactured.

Scientific/product outcomes such as `supported`, `contradicted`, `not_checkable`, `MIXED_RELATIONS`, measurement misses and `UNSUPPORTED_SEMANTIC_FAMILY` are observations, not apparatus failures.

## Before claim 1

Freeze and record:

- exact prototype commit;
- exact semantic implementation SHA;
- exact packet-schema blob;
- a manifest listing 10 packet filenames and SHA-256 digests;
- operator/evaluator identity or review method;
- output directory convention.

Do not alter any of those between claim 1 and claim 10.

## Cohort selection

Use real claims representative of intended MainFrame use, not claims selected because CAL is already known to handle them.

Prefer shape diversity. Include unsupported or awkward claims if they naturally occur. Do not force a balanced benchmark distribution.

Record the source/context used to choose each claim separately from CAL's result.

## Per-claim execution

For each frozen packet:

1. compute and preserve the input packet SHA-256;
2. execute the frozen prototype once;
3. preserve JSON receipt and Markdown report;
4. replay the exact same input at least once for deterministic comparison;
5. record human review without editing the original machine result;
6. record irregularities even when the result appears correct.

## Human review fields

At minimum capture:

- `claim_id`;
- `semantic_family_expected_by_operator`;
- `packet_typing_acceptable`: yes / no / uncertain;
- `evidence_world_acceptable`: yes / no / uncertain;
- `cal_conclusion_acceptable`: yes / no / uncertain;
- `failure_localization_useful`: yes / no / not_applicable;
- `important_evidence_missed_by_cal`: yes / no / uncertain;
- `important_evidence_not_in_packet`: yes / no / uncertain;
- `notes`;
- `operator_intervention`.

Keep packet-construction quality, evidence-world quality and CAL semantic quality separate. A bad packet is not automatically a CAL failure.

## Smoke apparatus PASS

PASS requires all of the following:

- 10 frozen packet hashes exist;
- every packet has exactly one primary result receipt or a localized input/harness failure record;
- semantic implementation identity is `a902621e8baea3063dddd7f92ba975aade305464` for every successful execution;
- Contract C remains `not_emitted` for every receipt;
- automatic action remains false;
- exact-input replays reproduce deterministic CAL result receipts;
- no semantic tuning, packet replacement, evidence replacement or claim replacement occurs after execution begins;
- human review records remain separate from raw machine receipts.

## FAIL / INCONCLUSIVE

FAIL apparatus if identities cannot be recovered, output changes on exact deterministic replay without a recorded environmental cause, a packet is silently replaced, CAL emits unqualified downstream authority, or the runner mutates CAL semantic behavior.

Use INCONCLUSIVE when external infrastructure or evaluator failure prevents determining whether the apparatus passed. Do not relabel infrastructure failure as a CAL semantic failure.

## After claim 10

Do not tune immediately. First summarize:

- outcome counts by conclusion and failure code;
- counts by semantic family;
- unsupported-family shapes;
- packet-construction disagreements;
- evidence-world disagreements;
- CAL-result disagreements;
- recurring measurement/relation failure patterns;
- deterministic replay status;
- operator intervention burden;
- surprising counterexamples and irregularities.

Then make one explicit decision whether the frozen prototype is suitable for a larger cohort unchanged, needs only apparatus/input fixes, or has exposed a CAL semantic defect requiring a successor rather than mid-cohort mutation.
