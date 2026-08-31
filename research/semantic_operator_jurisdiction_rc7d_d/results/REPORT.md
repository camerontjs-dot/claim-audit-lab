# RC7D-D Deterministic Multi-Reader Results

Scientific state: **`MULTI_READER_OVERCLAIM`**

No LLM or learned model was used.

## Single reader
- proposal dimension recall: 0.314
- authorized dimension recall: 0.271
- authorized atom precision: 0.789
- unsafe authorized atoms: 8

## Multi reader
- proposal dimension recall: 0.629
- proposal dimension precision: 0.957
- authorized dimension recall: 0.621
- authorized atom precision: 0.804
- unsafe authorized atoms: 19
- false authorized dimensions: 1
- proposal recall gain: 0.314
- authorized recall gain: 0.350
- mixed-semantic authorized retention: 0.633

## Agreement audit
- agreement case-dimensions: 9
- disagreement case-dimensions: 17
- error when agree: 0.556
- error when disagree: 0.941
- agreement-only unsafe authorized atoms: 3

## Composition
- oracle component composition accuracy: 1.000 (68/68)

## Boundary
Post-reveal deterministic hardening only. No independent-consumability or production claim.
