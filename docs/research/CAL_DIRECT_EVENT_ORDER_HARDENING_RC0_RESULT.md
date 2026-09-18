# CAL Direct Event Order Measurement Hardening RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / adversarial hardening.

## Frozen subject

- RC7F-C evidence head: `e8d33913db66ad21027dffdf731d50f7a0977c8f`
- event-order implementation blob: `3e29b0e2ec5d9ba2d873d1584e76635147e421aa`
- prior terminal: `EVENT_ORDERING_INSTRUMENT_CANDIDATE_READY_FOR_HARDENING`
- hardening apparatus head: `02b1e44392b3ff477c3407bcf25d939e3377db17`
- hardening run: `35292276872`

The exact event-order instrument and production `src/` were verified unchanged before execution.

## Disposition

**FALSIFIED FOR MODIFIER/COMPOSITION-SAFE STANDALONE MEASUREMENT.**

The original RC7F-C result remains valid inside its frozen explicit two-event before/after jurisdiction. This hardening result falsifies the stronger interpretation that the raw RC7F-C proposal is complete enough to stand alone when material scope, temporal modifiers, or additional-event structure surrounds the ordering cue.

## Preserved positives

All five MUST_RETAIN controls remained exact:

- positive BEFORE;
- positive AFTER;
- negative left-event polarity;
- negative right-event polarity;
- irrelevant preceding sentence.

Fresh diagnostics produced no wrong typed claims, including:

- hyphenated actor identity;
- longer object phrases;
- alternate frozen event verbs.

## Hardening counterexamples

The frozen instrument emitted a plain two-event order proposal for nine FAIL_CLOSED surfaces:

- `EOF01`: report-attributed ordering;
- `EOF02`: epistemic `Perhaps ... before ...`;
- `EOF03`: conditional `If ... before ...`;
- `EOF04`: negated temporal relation `not before`;
- `EOF05`: `immediately before`;
- `EOF06`: `shortly before`;
- `EOF07`: second-event causal tail;
- `EOF08`: third event joined by conjunction;
- `EOF09`: third event joined by disjunction.

The multiple-ordering-cue control and non-event calendar/narrative controls failed closed.

The defect is therefore not merely the presence of the word `before`. It is that the event parsers search/bind a supported event around a single cue while allowing surrounding material to be absorbed into event objects or discarded, and the proposal type has no field for these modifiers/composition relations.

## Architectural consequence

RC7F-C remains evidence for bounded **surface order observation**. It is not a modifier-complete temporal proposition representation.

The smallest successor question is:

> Can an independent source-completion/warrant layer reconstruct and validate the full two-event proposition, including attribution, condition, temporal-relation negation/modification, and composition boundaries, before the raw order measurement may decide?

If not, measurement itself needs a modifier-aware envelope or a pre-measurement gate.

A later authority layer cannot safely assume the raw order receipt contains all material semantics merely because left event, right event, polarity, and BEFORE/AFTER were measured correctly.

## Preserved failure

Run `35292276872` verified the immutable subject, printed all observations, then failed exactly at the preregistered scope/modifier/composition acceptance test. Static checks were skipped after semantic failure. No candidate code was changed and no counterexample was removed.

## Non-claims

This result does not invalidate RC7F-C within its original 60-case frozen cohort, does not alter the qualified direct-event-order relation algebra, does not establish a successor measurement representation, and does not authorize production changes, merge, or release.
