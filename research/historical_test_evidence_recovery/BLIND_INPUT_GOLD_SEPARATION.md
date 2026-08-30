---
title: "Blind-input / sealed-assessment separation"
privacy: "private-local"
---

# Blind-input / gold-separation assessment

Do not delete assessment surfaces. Seal them from adaptation.

## Rule

**Input-only surface** may contain: claim, supplied evidence, source passage, passage/source identity, allowed execution configuration, input-side source-boundary metadata, frozen phenomenon tags assigned before seeing results.

**Sealed assessment surface** contains: expected verdict, gold label, expected rule, qrels, calibration, previous system result, human adjudication, previous disagreement analysis.

If clean separation cannot be established, classify the corpus as mixed or contaminated rather than calling it blind.

## Family assessments

| Family | Separation | How to mount blindly | What to seal |
|---|---|---|---|
| e2e `CASES` | **MIXED in the Python module**; experiment design in PR #36 was CLEAN | load only claim/passages/source_meta; ignore stub scores, stub NLI, expected verdicts, expected rules, golden traces | `test_pipeline_e2e.py` expectations; `fixtures/traces/` |
| Construction gold `corpus.json` | **MIXED** | generate input-only JSON from `build_construction_gold.py` dropping `expected_verdict`, `derivation` if it encodes the answer, and `gold.json` | `gold.json`, `audit_results.json`, traces, FINDINGS scores |
| Construction gold v1.13.0 run | MIXED | same inputs as above | entire run tree |
| Fresh-blind constructed 50 | MIXED | builder exists on GitHub | gold + audit_results |
| SLG freeze | **CLEAN_SEPARABLE** | CB packets / worlds facts+claims | `frozen-gold.json`, parent_verdict, atom relation if used as answer key |
| SLG scaled-corpus | MIXED | do not use prepared trees as blind without stripping expected worlds | generation contracts, measured cells |
| scaled-30 | **CLEAN_SEPARABLE** if `relationship` is not treated as gold | claims+passages | AUDIT.txt / traces used as labels |
| PILOT-001 | **CLEAN_SEPARABLE** at source (bundles vs analysis gold) | `pilot-001-v2-audit/bundles/` | `gold.dev.yaml`, `blinding_key.yaml`, calibration reports |
| gold-lite | MIXED | do not use for successor adaptation | sealed reviews + API panels |
| operating-point sweeps | MIXED | n/a | selected thresholds |
| EB challenge-corpus-v1 | **CLEAN_SEPARABLE by design** | sources/cases/aperture | `gold/`, decompositions |
| X5 twins | MIXED | twin inputs maybe; expected invariance is assessment | results |

## Construction gold is the critical case

`corpus.json` cases currently include `expected_verdict` beside `claim_text` and `passages`. Copying that file into a successor execution aperture **is gold leakage**.

The GitHub builder can emit the same 33 cases. An input-only freeze should be generated from the builder, hashed, and stored separately from `gold.json`.

`derivation` text often states why the verdict follows. Treat it as assessment unless a review shows it is purely construction metadata.

## e2e-08 leakage risk

The fixture's expected `partially_supported` / `C6a_numeric` is **not** what the real-model path did. Using that expected verdict as adaptation information would teach the successor the stub world, not the real measurement. PR #36 already excluded it. Keep it excluded.

## Do not pretend PILOT-001 is blind for successor machinery

It is Decision-G DEV / adaptation. Inputs may still be reused if gold is sealed. Historical agreement numbers must not enter threshold or operator choice.
