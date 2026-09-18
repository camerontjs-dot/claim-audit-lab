# CAL Population + Deontic Applicability RC0 — Candidate Exposure Receipt

Date: 2026-09-18

- terminal pressure parent: `b10adbb5f185c093bbe9b7e8e7759f666141cd0e`
- corrected frozen pre-candidate apparatus: `f28b2a8a784271b4e8e880cca55478497b79599e`
- successful freeze run: `35351781535`
- deontic Gate-1B subject: `60298c99e8eb16cdad01f3c652cead83cad02992`
- population Gate-1B subject: `5d72475a65c3b6cf4190a048040fad8ee8b91156`
- candidate implementation commit: `8ee1443201dabf660f3b6c667750595e07074d37`
- candidate test commit: `93e9851f26c4c8bac332a7e93f9757c9eb560a82`
- candidate report commit: `0e589cae7e3900bcf27e7eeac834c85d7999511a`
- candidate qualification workflow commit: `92a17d52de14543e7a9d609e3e35d778943392d8`

Candidate exposure occurred only after parent isolation, frozen evaluator controls, and static checks all passed on exact freeze run `35351781535`.

Frozen preregistration, apparatus, evaluator, apparatus test, and freeze workflow must remain byte-identical to `f28b2a8a784271b4e8e880cca55478497b79599e` during candidate qualification.

Pre-candidate deviations remain preserved:
- `35350034910`: semantic controls passed; static E501/I001 formatting defects.
- `35350150711`: formatting repair accidentally introduced literal escaped newlines; collection failed before evaluation.
- `35351622018`: semantic controls passed; remaining evaluator I001.
- `35351704100`: semantic controls passed; Ruff exposed exact CASES/AppliedNorm ordering requirement.
- `35351781535`: corrected clean freeze.

No candidate was exposed before the successful clean freeze. This receipt is not production authorization.
