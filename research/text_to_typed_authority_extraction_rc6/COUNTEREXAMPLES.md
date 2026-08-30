# RC6 Preserved Extraction Counterexamples

This summary preserves the principal RC6 extraction failures. The complete machine-readable counterexample set is in accepted science artifact `9737521527`, `COUNTEREXAMPLES.json` SHA256 `b72697eb4ccf798b7312c6228d6c9bbed76fa5638cecdf7524336cc136524a95`.

No frozen extractor is repaired after reveal.

## Token/clause extractor

Six exact scientific failures were observed.

### SC-05 — benign typed-object mismatch

The extractor resolved the case and the frozen RC5B consumer returned the correct `neutral` relation, but `authority.membership_population` was recovered as `B` instead of `A`.

This is evidence that correct terminal relation does not prove exact authority recovery.

### SC-06 through SC-09 — mirrored subclass surface recovery

Four valid mirrored subclass constructions were rejected as `unparsed`.

The missing behavior is not in the frozen RC5B semantic consumer. RC5B already established the relevant directed subset semantics. These cases therefore remain extraction-coverage failures.

### TM-06 — conservative guard overreach

A valid temporal `never` construction was rejected as `ontology_escape` because the extractor's fail-closed lexical guard treated `either` as an out-of-schema signal even in the supported phrase `not ... either before or after ...`.

This is a jurisdiction-recognition false negative, not authority fabrication.

## Regex/template extractor

The weaker extractor preserved the same general safety pattern, zero authority fabrication on all 30 expected-unknown cases, but undercovered valid in-schema language more heavily.

Its failures included:

- two valid membership/behavior cases rejected by broad lexical guards;
- five subclass cases rejected as unparsed;
- six valid quantifier cases rejected by overbroad fail-closed matching;
- the same temporal `either` over-rejection as the token/clause extractor.

## Cross-extractor disagreement

The extractors disagreed on authority in 17 / 100 frozen cases. Those disagreements were concentrated in membership/behavior, subclass, and quantifier constructions.

For the stronger token/clause extractor, exact scientific failure was 5 / 17 on disagreement cases versus 1 / 83 on agreement cases. This post-hoc relative-risk calculation is approximately 24.4x and is derived from the frozen measurements without modifying or rerunning either extractor.

For the regex/template extractor, exact scientific failure was 13 / 17 on disagreement cases versus 1 / 83 on agreement cases, approximately 63.5x.

Disagreement is therefore a strong bounded risk signal, not semantic authority.

## Safety-relevant negative result

Neither extractor resolved any of the 30 cases preregistered as ambiguous-reference, insufficient-authority, or ontology-escape. No unsafe authority-fabrication counterexample was observed in RC6.

This does not establish arbitrary-language fail-closed behavior because the corpus and extractors were co-designed within the same bounded research execution.
