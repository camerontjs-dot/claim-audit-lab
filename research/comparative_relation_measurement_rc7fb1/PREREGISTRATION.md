# RC7F-B1 Comparative Relation Measurement Successor — Preregistration

Status: **FROZEN BEFORE CANDIDATE AND HELD-OUT COHORT**

## Parent

- terminal RC7F-B evidence: `3009da45e98dac099c4758c1d41ff42cf2a56eae`
- parent apparatus freeze: `d331fe6cbd6ce5ec56c446bd3a8a572b33c3457f`
- parent cohort freeze: `827dd907d2f8de2cc550b2e4331cc89872d5f1f6`
- accepted run: `33453256638`
- terminal: `MORE_COMPARISON_RESEARCH_JUSTIFIED`

Parent result: precision `1.0`, recall `0.8`, zero false proposals, perfect direction and attachment on resolved cases. Ten misses were localized to eight adjective+measure-head constructions and two comparative verbs.

## Question

Can the smallest deterministic non-LLM extension recover the observed residue while preserving zero false proposals and perfect typed precision?

## Allowed change

Add only:

1. comparative adjective + measure head + `than` attachment, for bounded adjectives `higher|greater|lower|smaller|larger` and bounded measure heads such as `output|count|volume|score|yield|rate|share|percentage|proportion`;
2. comparative verbs `exceed` / `trail` in explicit entity-to-entity constructions, including optional `by <delta>`;
3. evaluator correction separating `stable_correct`, `stable_abstention`, and `stable_wrong`.

Existing parent-supported families remain regression controls. The instrument remains **measurement-only** and has no semantic-warrant or operational authority.

No production `src/` changes. No generative LLM, LLM judge, or model-generated gold.

## Qualification

Must cover:

- `higher output than`, `greater output than`, `lower count than`, `smaller volume than`;
- `X exceeded Y by 4 units` and `X trailed Y by 4 units`;
- direction-changing pairs;
- old delta/share/equality/multiplier/threshold families;
- negative domain-word traps containing `higher`, `greater`, `exceeded`, `trailed` without a comparative relation;
- unrelated dual quantities;
- ambiguous constructions fail closed.

## Held-out

Only after candidate/evaluator freeze. Gold is formal comparison atoms rendered mechanically, never candidate/model output.

Required families: parent-supported families, new measure-head adjectives, new comparative verbs, direction pairs, paraphrase pairs, negative/domain traps, unrelated quantities, deliberately unsupported ambiguous forms.

Identical normalized source strings may not carry incompatible gold.

## Metrics

- typed precision/recall;
- direction accuracy;
- left/right attachment accuracy;
- false proposals on negative controls;
- unresolved rate;
- pair states `stable_correct`, `stable_abstention`, `stable_wrong`;
- meaning-changing direction-pair accuracy.

## Success

`COMPARISON_INSTRUMENT_CANDIDATE_READY_FOR_HARDENING` requires:

- typed precision `1.0`;
- typed recall >= `0.95`;
- direction accuracy `1.0`;
- attachment accuracy `1.0`;
- negative-control false proposals `0`;
- meaning-changing accuracy `1.0`;
- `stable_wrong = 0`;
- no evaluator/cohort defect;
- no post-held-out repair.

Otherwise a safe bounded residue yields `MORE_COMPARISON_RESEARCH_JUSTIFIED`; unsafe false proposals or invalid apparatus yield `COMPARISON_ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE`.

## Design principle

A comparison proposal is an observation, not an assertion. When measurement or warrant is incomplete, abstention is a successful outcome.
