# Natural-claim successor to CAL #206

Disposition: `FALSIFIED_UNSAFE_FALSE_DECISION_RATE`

The original-input arm produced two critical false supports on the sealed held-out cohort. That fails the preregistered error rule. The run does not authorize a V1 release.

Predecessor primary disposition, stated here and left unchanged on Draft PR #208: `MECHANICS_SUPPORTED_SEMANTIC_UTILITY_UNESTABLISHED`. Arm C matched the exposed seeds. The preregistered Arm A event prediction failed on S09 and S10 because the frozen kernel authored `Alpha reviewed Report before Beta approved File.` and source completion refused the object token `Report`.

## What was compared

One successor judge set ran under three topologies. Arm K called the frozen kernel and is reference only.

| Arm | What it changes |
|---|---|
| K | Frozen CAL kernel. Authoring refusal is not semantic accuracy. |
| R | Same judges. An early cue router selects relation lanes. Both guards still run. |
| B | Same judges. One shared reduction deletes four-digit years, the quantifier words all/some/every/most/each, and the hedge words alleged/reportedly/projected/projection/according to. |
| C | Same judges. Each judge receives the original claim and the authorized evidence. |

Calibration used only P02, P06, P07, and P08. Both adjudicators agreed on all 13 calibration claims. The locked policy is minimum `1`, with weight `1` on `quantity_relation` and `event_order`. Guards stay weight `0` and required. Held-out labels were sealed before this policy was frozen at `195821ba8646869a2df7b150a3ea3a32a17a50a9`. No weight or judge byte changed after the held-out run.

## Held-out result

Twelve eligible claims, zero adjudication disagreements, 4.01 seconds, no model calls.

| Claim | Agreed class | K | R | B | C |
|---|---|---|---|---|---|
| P01-1 | supported | not_checkable, authoring refused | supported | supported | supported |
| P01-2 | not_checkable | not_checkable, authoring refused | not_checkable | supported | not_checkable |
| P01-3 | contradicted | not_checkable, authoring refused | supported | supported | supported |
| P03-1 | supported | not_checkable, authoring refused | supported | supported | supported |
| P03-2 | not_checkable | not_checkable, authoring refused | not_checkable | supported | not_checkable |
| P03-3 | contradicted | not_checkable, authoring refused | supported | supported | supported |
| P04-1 | supported | not_checkable, authoring refused | supported | supported | supported |
| P04-2 | not_checkable | not_checkable, authoring refused | not_checkable | supported | not_checkable |
| P04-3 | contradicted | not_checkable, authoring refused | contradicted | contradicted | contradicted |
| P05-1 | supported | not_checkable, authoring refused | not_checkable | not_checkable | not_checkable |
| P05-2 | not_checkable | not_checkable, authoring refused | not_checkable | not_checkable | not_checkable |
| P05-3 | contradicted | not_checkable, authoring refused | not_checkable | not_checkable | not_checkable |

Arm C: 4 correct deciding results, 2 false supports, 0 false refutations, 4 safe abstentions, 2 abstentions where a deciding class was agreed. Conditional accuracy among the 6 decisions is 4/6. Every claim preserved its four-digit years inside C's quantity interpretation.

False supports:

- P01-3. The claim says the yearend 2023 death-sentence count was 73 (3%) more than yearend 2022. The BJS passage says 73 (3%) fewer. C returned `supported`.
- P03-3. The claim says 2024 hospital expenditure growth of 8.9% was faster than 10.6% growth in 2023. The CMS sentence says slower. C returned `supported`.

P01-1 is scored correct because the claim and the passage both say fewer and carry the same quantities. The quantity lane never binds `fewer` or `more` across the parenthetical percent, so that correct score is the same level match that false-supports P01-3.

P04-3 is a real polarity refutation: `32% decrease` against evidence that says `32% increase`.

P05-1 and P05-3 abstained with `no_matching_passage`. The USDA slide extraction does not present the claimed production figure as a passage the quantity lane can match. P05-2 abstained on the changed year.

Safe abstentions P01-2, P03-2, and P04-2 are year mismatches. Scope guard violation blocks them on C and on R. Arm B deletes the years and then supports all three. Those three are preregistered property P1. P2 did not occur: every held-out claim had a quantity cue, R and C reached the same terminal class, and the event-order lane was `not_applicable` wherever C ran it.

## What the arms separate

Judge quality produced the error-rule failure. `more`/`fewer` after a parenthetical rate, and `faster`/`slower` beside a shared `grew`, are proposition-significant, and this judge set does not represent them.

Early routing did not change a held-out terminal class.

The shared reduction did. Removing the year turned three agreed `not_checkable` claims into false supports on B while C abstained.

Original-input analysis preserved those years. It did not catch the two comparator failures, which survive in the original text.

Synthesis weighting did not create the false supports. Calibration had zero wrong deciding results, so the search left both relation weights at 1 and the minimum at 1. One quantity lane was enough to decide. Dependence controls passed on the mechanical fixture: a cloned process, a duplicated passage, two prompt names, a self-awarded score, extra `not_applicable` lanes, a sealed minority refutation, and a sealed scope-guard violation. Clones share a group and contribute the maximum weight once. The minority case is a sealed-receipt check, because copies of one deterministic judge cannot disagree on identical bytes.

## Publication redaction

GitHub push protection refused the first push. The downloaded CMS HTML contained one Mapbox public token. That token was not in the text window and not in any claim or evidence span. I removed it from `sources/raw/P03.bin` before publication. The text-window hash is unchanged. The decisive report still names local execution head `195821ba8646869a2df7b150a3ea3a32a17a50a9`. That commit is not in the published history, because the raw file's parent commit had to be rewritten to drop the token.

## Product regression

The maintained suite was run from this worktree with the declared `[v1]` extra installed and `en_core_web_sm` available. Collection and execution completed: 976 passed, 5 skipped, 48 deselected, 1 failed, in 46.27 seconds.

The failure is `tests/test_no_authoring_paths.py::test_no_tracked_file_contains_an_authoring_path` at `sources/raw/P08.bin` line 739. The frozen EPA page contains a public forms path that matches the scanner's home-directory pattern. Those source bytes stay as frozen. The RC0 run without `[v1]` remains incomplete coverage.

## Smallest next gate

A later candidate has to represent a proposition-significant comparator that is not adjacent to its quantity, including `more`/`fewer` around a parenthetical rate and `faster`/`slower` beside an otherwise matching growth verb. This held-out cohort has been read, so it cannot be the tuning set. The next gate needs a new source-disjoint split, frozen before that change, and it still would not by itself authorize a V1 release.
