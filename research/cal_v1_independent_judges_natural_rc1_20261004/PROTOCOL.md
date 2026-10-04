# CAL V1 natural-claim successor RC1

Programme: CAL #205. Predecessor execution gate: CAL #206. This packet does not edit PR #208, the RC0 seeds, the RC0 expectations, or any predecessor byte.

## Predecessor disposition

Primary scientific disposition of the predecessor:

`MECHANICS_SUPPORTED_SEMANTIC_UTILITY_UNESTABLISHED`

Preserved detail: Arm C matched the exposed seed labels. The preregistered Arm A event prediction failed on S09 and S10. The frozen kernel authored `Alpha reviewed Report before Beta approved File.` and returned `SOURCE_COMPLETION_FAILED` because source completion refuses the object token `Report` as a reporting surface. `decisive-01` stays in place. Toy weights were uncalibrated. A versus C was confounded because the instruments differed as well as the routing.

PR #208 records a longer disposition string for that same run. This packet normalizes the primary label. It does not rewrite that pull request.

## Question

On claims drawn from sources that were not used to build the RC0 candidate, does original-input independent analysis improve natural-claim auditing once judge identity, early routing, shared loss, and synthesis weights are separated?

## What is held fixed

- Product version `0.6.0`.
- Frozen kernel `64b6c7702696c851057c1cf0b2c105b1c81db543`.
- Semantic implementation `caa0048f8f511ec3c4aa1ce713766f2219a04bc1`.
- RC0 candidate freeze `83f4afda3328c7ccd9be3fbcd670083fc38f68a6`.
- RC0 evidence head `d3426c5a3113afb4b3ed74618a5512d084a1fd17`.
- Contracts A/B/C/D/E, Decision Engine, release tags, and production consumer pins.

Arm K calls the unchanged production semantic engine through the already frozen RC0 `kernel_lane.py`. That lane is a historical reference. It is not a successor judge and it is not used to attribute topology.

## Source pool

Eight primary public documents, fixed before retrieval. None is an RC0 S01–S14 seed, a #189/#193 source, or a #203 source. The list is in `SOURCE_POOL.json`.

A failed retrieval or an empty extraction stays in the pool. It is not replaced after the download, and it is not replaced after any CAL run.

Extraction, fixed before reading the documents for claims:

- PDF: `pdftotext -layout -enc UTF-8`.
- HTML: drop `script`, `style`, and `noscript`, then drop tags and unescape entities.
- Working window: the full extraction when it is at most 80,000 characters; otherwise the first 80,000 characters. Truncation is recorded. Claim evidence must be an exact substring of that window.

## Split

After raw bytes are hashed, and before any claim is written:

- Sources with a non-empty window are sorted by the SHA-256 of their raw bytes.
- The lower half is the calibration partition. The upper half is the held-out partition.
- An odd count puts the middle source in calibration.
- A source is in only one partition.
- Retrieval failures are unpartitioned.

The qualification lead saw search snippets while confirming that the URLs existed. That lead does not author gold labels. Two adjudicators, working only from the frozen windows, write claims and labels. Held-out labels stay out of the implementer's view until every judge byte, router, loss transform, and synthesis policy is frozen. The pre-reveal seal is the SHA-256 of the held-out label file.

## Claims

For each partitioned source, in document order, at most four claims:

1. One proposition the selected passage states, preserving its numbers, dates, quantifier, measure, and polarity.
2. One proposition that changes exactly one proposition-significant item in that passage, so the passage does not establish it.
3. One proposition the passage explicitly contradicts, and only when the text itself states the contrary.
4. One proposition on which two passages in the same source materially conflict, and only when that conflict is present.

Claims use the source's own wording. They are not rewritten into the RC0 Alpha/Beta grammar. The system under test does not create gold labels.

Each adjudicator records the claim text, the exact evidence substring, the intended proposition, the semantic families, the proposition-significant scope, the expected terminal class when adjudicable, the acceptable `not_checkable` conditions, and the rationale.

Where the two adjudicators disagree, the claim is `adjudication-uncertain`. Those claims stay in the robustness set and leave the accuracy denominators. Agreement is required. There is no convenience label.

## Arms

One successor judge set is frozen and used wherever a process is invoked:

- `quantity_relation` — relation
- `event_order` — relation
- `scope_guard` — guard, weight zero, required
- `attribution_guard` — guard, weight zero, required

| Arm | Role |
|---|---|
| K | Frozen kernel only. Reference. Not a topology contrast. |
| R | Successor judges. An early cue router chooses which processes run. Others are `not_run`. |
| B | All successor judges. One shared reduced text, not the original sentences. |
| C | All successor judges. Each child receives the original claim and authorized evidence. Local parses stay in that process until the receipt is sealed. |

R, B, and C use the same judge modules. Any skipped process or lossy input is an invocation difference and is recorded. Time limit is 30 seconds for every child.

The shared reduction deletes four-digit years, the quantifier words `all`, `some`, `every`, `most`, and `each`, and the hedge words `alleged`, `reportedly`, `projected`, and `according`. It is a control, not a production interpretation.

## Calibration

Only the calibration partition may influence applicability, relevance, dependence groups, weights, and the decision threshold.

A judge's self-confidence, self-declared relevance, and self-awarded weight are not authority. Duplicate process IDs that share a dependence group contribute the maximum weight in that group once, not the sum.

Hard blockers are not outweighed:

- invalid provenance or input binding
- a required guard violation, including material scope or measure mismatch
- demonstrated material loss on a receipt that is allowed to vote
- an unresolved required interpretation
- a qualified material support/refute conflict across dependence groups

`not_applicable` does not vote and does not force abstention.

The threshold is chosen on calibration only. Among thresholds with zero wrong deciding results, choose the one with the most correct deciding results. If every threshold that decides is wrong at least once, the locked threshold abstains. The objective is to avoid wrong deciding results, not to minimize abstention.

After that choice, freeze the judge bytes, router, loss transform, catalogue, applicability, relevance, dependence groups, weights, blockers, threshold, synthesis implementation, and the held-out manifest hash. No later edit uses a held-out result.

## Held-out metrics

One decisive run. Do not overwrite it.

Eligible claims are held-out claims whose adjudicators agreed on `supported`, `contradicted`, or `not_checkable`.

Record eligible claims, correct deciding results, wrong deciding results, false support, false refutation, conditional accuracy among decisions, safe abstentions, abstention causes, family coverage, scope and measure and time and polarity preservation, material-conflict detection, R/B/C differences, and runtime.

`not_applicable` is not semantic correctness. An authoring refusal is not semantic accuracy.

## Error rule

A critical false deciding result is a terminal class of `supported` or `contradicted` on an eligible held-out claim whose agreed class is different. The count must be zero.

## Architecture properties

These are preregistered. Lower abstention is not one of them.

- P1. On at least one eligible held-out claim, the shared reduction changes a proposition-significant year, quantifier, measure, or attribution, C's terminal class matches the agreed class, and B's terminal class is a wrong deciding result.
- P2. On at least one eligible held-out claim, R leaves `not_run` a process that C runs, C's result is a correct deciding result, and R's result is not that same correct class.

An architecture advantage requires P1 or P2. If neither situation occurs, the advantage is unestablished.

## Dependence controls

Separate from the natural-claim denominators. Run once on the frozen policy:

- the same judge under a second process ID
- the same evidence passage duplicated
- the same deterministic judge under two prompt names
- a self-awarded confidence and weight
- a self-declared relevance flag
- extra `not_applicable` processes
- one qualified minority refutation against several correlated support receipts
- one required scope violation against otherwise supportive relation receipts

Clones must not gain authority by multiplicity.

## Acceptance

No result authorizes a V1 release.

- `SUPPORTED_SOURCE_DISJOINT_NATURAL_CLAIM_USEFULNESS_WITH_BOUNDED_INDEPENDENT_JUDGE_ADVANTAGE` requires all six: zero critical false decisions, at least two correct C decisions on eligible held-out claims, safe abstention on agreed unresolved or conflicting or missing cases that were included, P1 or P2, dependence controls passed, and no held-out tuning.
- `SUPPORTED_NATURAL_CLAIM_USEFULNESS_ARCHITECTURE_ADVANTAGE_UNESTABLISHED` when the first, second, third, fifth, and sixth hold and the architecture properties do not.
- `MECHANICS_SUPPORTED_NATURAL_USEFULNESS_UNESTABLISHED` when the run is valid and C does not produce the required correct deciding results, without a critical false decision.
- `FALSIFIED_UNSAFE_FALSE_DECISION_RATE` when the error rule fails.
- `INCONCLUSIVE_EVALUATOR_OR_COHORT_INVALID` when the cohort or the scorer cannot support the question.
- `BLOCKED_REQUIRED_JUDGE_OR_ENVIRONMENT_UNAVAILABLE` when a required judge or the declared regression environment cannot be run.

Fewer than four eligible held-out claims, or fewer than two whose agreed class is a deciding class, blocks either supported disposition. The run can still be `MECHANICS_SUPPORTED_NATURAL_USEFULNESS_UNESTABLISHED` or inconclusive.

## Product regression

Run the maintained suite in an environment that installs the declared `[v1]` extra. The RC0 run without that extra remains incomplete coverage. Do not call the regression complete unless the suite collects and executes.
