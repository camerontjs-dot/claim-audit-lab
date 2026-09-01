# RC7F-C Explicit Event-to-Event Ordering Measurement — Preregistration

Status: **FROZEN BEFORE CANDIDATE AND HELD-OUT COHORT**

## Parent evidence

- RC7E terminal evidence: `34e9bcafad2c63c9b0761ffc456532344bc75b88`
- accepted RC7E scientific run: `33448511982`
- frozen RC7E event-ordering result: `0/4` gold event-order dimensions directly observed by the portfolio.

RC7F-C is a measurement-only successor. It does not repair RC7E.

## Question

Can a small deterministic non-LLM instrument recover **explicit binary ordering between two locally stated events** while preserving direction and event attachment and producing no ordering proposal from temporal/domain traps?

## Supported candidate jurisdiction

Only explicit two-event clauses joined by:

- `before`
- `after`

The candidate may normalize each event into bounded `(subject, predicate, object, polarity)` structure and emit:

- `left_event`
- `relation`: `BEFORE` or `AFTER`
- `right_event`
- exact cue/span

No timestamp normalization, duration inference, causal inference, calendar arithmetic, implicit chronology, or narrative-order inference is authorized.

The output is a **measurement proposal only**. It has no semantic-warrant or operational-authority jurisdiction.

No production `src/` changes. No generative LLM, LLM judge, or model-generated gold.

## Pre-held-out qualification

Must cover:

- active-voice event A `before` event B;
- active-voice event A `after` event B;
- polarity on either side;
- direction-changing minimal pairs;
- differing subjects, predicates, and objects;
- domain traps containing `before`/`after` without two events;
- dates/labels using those words without binary event order;
- unsupported ambiguous forms fail closed.

## Held-out construction

Only after candidate/evaluator freeze. Formal event pairs and ordering relation are created before deterministic rendering. Candidate output never establishes gold.

Required families:

1. positive `before`;
2. positive `after`;
3. negative-left and negative-right events;
4. meaning-changing before/after pairs;
5. meaning-preserving lexical substitutions inside supported event vocabulary;
6. irrelevant prose around a valid ordered pair;
7. domain-word/label traps;
8. deliberately unsupported temporal paraphrases such as implicit chronology or vague temporal adverbs, scored as safe abstention rather than false negative inside supported jurisdiction.

Identical normalized source strings may not carry incompatible gold.

## Metrics

- typed ordering precision/recall in supported jurisdiction;
- relation-direction accuracy;
- left/right event attachment accuracy;
- polarity accuracy;
- false proposals on negative controls;
- meaning-changing direction-pair accuracy;
- unresolved rate.

## Success

`EVENT_ORDERING_INSTRUMENT_CANDIDATE_READY_FOR_HARDENING` requires:

- typed precision `1.0`;
- typed recall >= `0.95` on supported explicit before/after cases;
- direction accuracy `1.0`;
- event attachment accuracy `1.0`;
- polarity accuracy `1.0`;
- negative-control false proposals `0`;
- meaning-changing pair accuracy `1.0`;
- no evaluator/cohort defect;
- no post-held-out repair.

Safe bounded residue yields `MORE_EVENT_ORDERING_RESEARCH_JUSTIFIED`; unsafe proposals or invalid apparatus yield `EVENT_ORDERING_ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE`.

## Design principle

Recognizing chronology is an observation. CAL must not claim chronology it did not observe, and observed chronology must still pass separate semantic warrant before becoming an asserted proposition.
