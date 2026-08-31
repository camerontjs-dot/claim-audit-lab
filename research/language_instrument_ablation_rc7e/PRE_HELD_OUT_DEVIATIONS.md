# RC7E Pre-Held-Out Apparatus Deviations

These deviations were discovered and corrected before any RC7E held-out corpus existed. They do not alter the research question or success direction. The original preregistration remains immutable.

## RC7E-D01 — shallow-checkout integrity-guard failure

**Observed:** qualification run `33442319152` failed before any instrument qualification executed. The job log records `fetch-depth: 1`, followed by `git diff --exit-code 253af5313e93932875bdd5956ac46246f3796271 -- src/`, followed by `fatal: bad object 253af5313e93932875bdd5956ac46246f3796271`.

**Disposition:** apparatus failure only. Preserve run `33442319152` and artifact `9776795228` (`sha256:e92d77b83dc08741d9db3a3bb14b54090e7d2a924166fb268a3b8c2749fa8cbc`). The corrected workflow uses full history so the immutable production-source comparison can execute.

## RC7E-D02 — SuPar pretrained model alias correction

**Preregistered alias:** `sdp-biaffine-en`.

**Current documented SuPar 1.1.4 alias:** `biaffine-sdp-en` for the English DM semantic-dependency parser.

**External verification:** https://pypi.org/project/supar/1.1.4/ (retrieved 2026-08-31).

**Disposition:** correct the alias before held-out construction. Preserve the original alias in the final instrument identity as a deviation field. This is runtime qualification, not result-driven tuning.

## RC7E-D03 — cross-instrument authority-anchor pooling risk

**Observed from apparatus inspection:** the first `validate_union` candidate flattened all anchors and candidate atoms from every receipt into one synthetic receipt before validation.

**Risk:** an unrelated instrument anchor could become available to another instrument's proposal during authority validation, weakening provenance and creating a costly-to-detect authority leak.

**Disposition:** final pre-held-out authority validates each instrument receipt independently and merges only validation results. Raw source remains common and untouched.

## RC7E-D04 — symbolic-reasoner ablation leakage

**Observed from apparatus inspection:** the first runner generated an OWL-RL receipt from the complete portfolio and stored it as if it were a fixed instrument output. Reusing that receipt in leave-one-in/leave-one-out analysis would allow premises from omitted instruments to leak into an ablation.

**Disposition:** recompute OWL-RL from each subset's own already-authorized premises. Direct raw-source uniqueness for OWL-RL is reported as zero; its value is measured as conditional subset/composition gain.

## RC7E-D05 — NLI proposal-origin provenance

**Observed from apparatus inspection:** the first NLI receipt retained the typed proposal but not which independent instrument(s) nominated it.

**Disposition:** preserve canonical proposal-origin instrument IDs in every NLI measurement. NLI remains non-authoritative and cannot originate atoms.

## Non-authoritative intermediate tree

A local Git-data tree object `9a619745eec6e015ef1176ebeb1dcf39704783df` was constructed during pre-held-out repair but never committed or moved onto the RC7E branch. It is not an apparatus freeze and must not be cited as scientific authority.
