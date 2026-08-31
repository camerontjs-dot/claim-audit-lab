# RC7E Pre-Held-Out Apparatus Deviations

These deviations were discovered and corrected before any RC7E held-out corpus existed. They do not alter the research question or success direction. The original preregistration remains immutable.

## RC7E-D01 — shallow-checkout integrity-guard failure

**Observed:** qualification run `33442319152` failed before any instrument qualification executed. The job log records `fetch-depth: 1`, followed by `git diff --exit-code 253af5313e93932875bdd5956ac46246f3796271 -- src/`, followed by `fatal: bad object 253af5313e93932875bdd5956ac46246f3796271`.

**Disposition:** apparatus failure only. Preserve run `33442319152` and artifact `9776795228` (`sha256:e92d77b83dc08741d9db3a3bb14b54090e7d2a924166fb268a3b8c2749fa8cbc`). The corrected workflow uses full history so the immutable production-source comparison can execute.

## RC7E-D02 — SuPar pretrained model alias correction

**Preregistered alias:** `sdp-biaffine-en`.

**Documented SuPar 1.1.4 alias:** `biaffine-sdp-en` for the English DM semantic-dependency parser.

**Disposition:** the alias was corrected before held-out construction so runtime qualification could exercise the intended model. The original alias remains preserved in instrument identity.

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

## RC7E-D06 — semantic-dependency graph lane unavailable on safe modern runtime

**Observed:** corrected qualification run `33444767215` successfully verified production `src/` against exact base `253af5313e93932875bdd5956ac46246f3796271`, preserved raw source, passed every evaluator control, and loaded the selected portfolio except `supar_sdp`. After downloading the documented `biaffine-sdp-en` checkpoint, SuPar failed with PyTorch's `weights_only=True` safe-deserialization error on `supar.utils.config.Config`.

**Preserved evidence:** artifact `9777713249`, digest `sha256:c403a5e47af93fcaf00a6150fa61bd0bc77facc11705c95fc3a19a814a6479cc`.

**Maintenance/compatibility check:** the upstream `yzhangcs/parser` repository's latest observed code commit is `bebdd350e034c517cd5b71185e056503290164fa` dated 2023-09-03. Upstream issues #147 and #149 independently reproduce PyTorch 2.6+ / 2.7 safe-loading incompatibility; reported workarounds include older PyTorch or unofficial forks.

**Disposition:** prune SuPar from the RC7E scientific portfolio before held-out construction. Do not set `weights_only=False`, accumulate pickle allowlists, pin an obsolete PyTorch solely for category coverage, or substitute an unofficial fork after qualification. Preserve a `supar_sdp_unavailable` receipt with no semantic proposal jurisdiction. Semantic-graph coverage therefore remains an explicit apparatus gap.

## Non-authoritative intermediate tree

A Git-data tree object `9a619745eec6e015ef1176ebeb1dcf39704783df` was constructed during pre-held-out repair but never committed or moved onto the RC7E branch. It is not an apparatus freeze and must not be cited as scientific authority.
