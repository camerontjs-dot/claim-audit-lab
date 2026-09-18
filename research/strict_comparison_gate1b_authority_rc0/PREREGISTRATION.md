# CAL Strict Comparison Gate-1B Authority RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / source-completion and warrant discrimination.

## Frozen subject

This study tests the pre-existing M4 authority firewall, not a newly written candidate.

- M4 terminal parent: `607ec560fd53bd56279193a8d39a48b6f80e1012`
- frozen authority implementation is the M3/M4 `complete_and_warrant()` path
- strict measurement instrument identity: `rc7fb1-strict-comparison / rc7fb1-comparator-1`
- hardening evidence: PR #139, exact hardening head `94a4cdabde9fe03253b8409e25c98b1b0698dfdc`, run `35292180149`

PR #139 established that the frozen strict measurement can emit a plain positive comparison atom while dropping material negation, modality, or attribution.

## Question

Can the already-independent source-completion/warrant layer reject those lossy measurement receipts by re-reading the admitted source, while still warranting clean comparison sources?

This is the discriminating architecture question. If yes, measurement may remain a proposal instrument because the firewall independently reconstructs the material semantics. If no, the authority path is not sufficient to protect the current representation.

## Cohorts

### WARRANT

Clean positive sources from the supported strict-comparison jurisdiction. Each must:
1. produce a CLAIMED strict measurement;
2. complete independently from source;
3. return a Warranted SemanticAtom whose fields equal the measured relation.

### REFUSE_AFTER_LOSSY_MEASUREMENT

Exact hardening counterexamples for which the strict measurement is known to CLAIM an unqualified positive comparison:
- negated comparison;
- `no higher than`;
- probabilistic comparison;
- alleged comparison;
- epistemic `may` / `could`;
- report-attributed comparison;
- negated equality / same-as;
- negated multiplier.

Each must:
1. still reproduce the lossy CLAIMED measurement;
2. be refused by `complete_and_warrant()`;
3. never produce an AuthorityReceipt.

## Acceptance

`SUPPORTED_GATE1B_STRICT_COMPARISON` only if every clean source warrants and every lossy hardening source is refused.

No changes to `src/` are permitted. A failure is preserved; do not patch the authority implementation inside RC0.

## Non-claims

A pass is not a general modifier solution, does not qualify new comparison measurement surfaces, and does not promote or merge production code. It establishes only that the frozen source-completion firewall catches this exact class of known measurement loss.
