# RC8B — Bound Authority-Receipt Successor Preregistration

## Parent result

RC8A falsified the frozen RC8 receipt on all six preregistered provenance substitutions while preserving the fully bound positive control. The frozen RC8 implementation remains unchanged and is terminally falsified for receipt sufficiency.

RC8A is now exposed qualification evidence only.

## Decision question

Does adding one explicit authority-subject binding invariant, plus required-field support-span governance, eliminate the observed substitution failure without weakening RC8's previously supported authority-state behavior?

## Smallest justified architectural change

RC8B may add only these authority checks before consuming an authority-bearing receipt:

1. the assessment carries one `authority_subject_id`;
2. the proposal is explicitly bound to that same subject;
3. the assertion receipt is explicitly bound to that same subject;
4. the operator receipt is explicitly bound to that same subject;
5. every required field warrant is explicitly bound to that same subject;
6. every required field warrant has a support span contained by the operator's governed source span;
7. a required composition receipt is explicitly bound to that same subject;
8. a required aperture receipt is explicitly bound to that same subject.

No reader-count, instrument-count, confidence, voting, or agreement rule may affect authority.

## Typed binding outcomes

- explicit authority-subject mismatch: `REJECTED`;
- missing authority-subject binding needed to assess a receipt: `UNRESOLVED`;
- explicit required-field support span outside operator governance: `REJECTED`;
- malformed or missing required-field support span: `UNRESOLVED`;
- otherwise preserve RC8's existing typed state/reason behavior.

The binding check must occur before the semantic content of that receipt is used as authority.

## Threat-model boundary

RC8B tests consistency of frozen receipt provenance, not cryptographic authenticity or adversarial forgery. A transplanted receipt is treated as the unchanged authority fragment it was when produced. Whether an upstream producer may dishonestly relabel a receipt is a separate trust/authenticity problem and is not claimed solved here.

## Qualification before freeze

The candidate may be tuned only against exposed evidence:

- RC8's open qualification cohort;
- RC8's now-exposed 68-case held-out cohort, converted to the RC8B bound-receipt schema without changing its semantic mutations or expected authority outcomes;
- RC8A's seven exposed source-binding cases.

Qualification must verify:

- all exposed expected authority statuses remain exact under valid binding augmentation;
- all six RC8A substitutions are rejected;
- the RC8A fully bound control is warranted;
- weak reader/instrument-count perturbations remain authority-inert;
- production `src/` and `schema/` remain unchanged.

No qualification result counts as prospective scientific evidence for RC8B.

## Candidate freeze

After exposed qualification passes, freeze the RC8B candidate bytes before authoring any fresh RC8B held-out source-binding cohort.

The frozen candidate must not be repaired after prospective reveal.

## Prospective held-out requirements

A fresh post-freeze cohort must include unseen combinations of:

- missing top-level/proposal/assertion/operator/field/composition/aperture subject binding;
- explicit subject mismatch at each authority-bearing layer;
- multiple simultaneous mismatches with deterministic reason precedence;
- required-field support span wholly outside operator governance;
- required-field support span touching a governance boundary;
- unresolved field authority combined with correct subject binding;
- source semantic unknown combined with correct subject binding;
- composition/aperture not required, proving no gratuitous binding requirement is introduced there;
- irrelevant reader/instrument bank growth on warranted and unresolved cases;
- previously supported domain/applicability/assertion/value/composition/aperture failure states under valid binding.

## Hard falsifiers

RC8B is falsified if any of the following occurs in the frozen prospective cohort:

1. `unsafe_warranted_atoms > 0`;
2. any explicit subject mismatch is warranted or unresolved rather than rejected;
3. any missing required binding is warranted;
4. any required field whose support span lies outside operator governance is warranted;
5. any previously supported semantic rejection/unresolved state becomes warranted merely because subject binding is present;
6. reader/instrument-count growth changes authority;
7. the fully bound positive controls cease to be warranted.

## Non-authorization

RC8B remains research machinery. Passing this programme would not authorize production CAL changes, Contract B/C changes, a release, downstream policy, or a clean-room independence claim.
