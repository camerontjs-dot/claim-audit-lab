---
title: "Live GitHub authority — camerontjs-dot/claim-audit-lab"
status: "observed-2026-08-29"
privacy: "private-local"
---

# LIVE_AUTHORITY

Live GitHub is authoritative for current repository state. Historical local material is evidence about prior work, not authority about current CAL behavior.

Observed via GitHub MCP and local preflight tool on 2026-08-29 / 2026-08-30 UTC. Preflight receipt: `github-preflight.json`.

## Repository

| Field | Value | Class |
|---|---|---|
| Owner/repo | `camerontjs-dot/claim-audit-lab` | OBSERVED |
| Visibility | public | OBSERVED |
| Default branch | `main` | OBSERVED |
| Live `main` HEAD | `53f0885b111676794d1bd20e10b91aa58b07e9d4` | OBSERVED |
| `main` HEAD subject | `Decision: bound RC1A production promotion` | OBSERVED |
| `main` HEAD date | 2026-08-29T20:35:55Z | OBSERVED |

Recent `main` commits (newest first):

| SHA | Subject | Class |
|---|---|---|
| `53f0885b111676794d1bd20e10b91aa58b07e9d4` | Decision: bound RC1A production promotion | OBSERVED |
| `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a` | Release recovery: attach locked CAL 0.5.0 assets (#27) | OBSERVED |
| `5533bbcf27a3ee3a7d901f7dfc44c241bc558e2c` | Release: Claim Audit Lab 0.5.0 with Contract C 1.0.0 exporter (#26) | OBSERVED |
| `a069707e5031cef5b82af02d08b0f1a47ea8752e` | Promotion: add minimal Contract C 1.0.0 exporter (#25) | OBSERVED |
| `885004b455dbb8717b9db99230376452b6f03427` | Maintenance: cancel superseded PR CI (#23) | OBSERVED |

## Open PRs

Three Draft Research Infrastructure PRs, all open. One open issue (#3, Contract-B consumer seam).

### PR #35 — Research Infrastructure: CAL machinery audit baseline

| Field | Value |
|---|---|
| URL | https://github.com/camerontjs-dot/claim-audit-lab/pull/35 |
| State | open, draft |
| Base | `main` `53f0885b111676794d1bd20e10b91aa58b07e9d4` |
| Head | `research/machinery-audit-20260829` `8c7cb29f6251f4f6566ab5fcc501cddc791e3539` |
| Commits | `db387e016e8e366542c64ec1965a9614ccf0e5e5`, `ccc5fae0a691cd5bee8e7a23bf781c5702e36080`, `8c7cb29f6251f4f6566ab5fcc501cddc791e3539` |

Frozen research artifacts: `research/machinery_audit/RESULTS.md`, `research/machinery_audit/real_pipeline_smoke.py`, workflow `research-machinery-audit.yml`. Hosted smoke run `33274013299`; artifact digest `sha256:329e99cb9d8b74f08f87f5d8cb0b5e601343cc5d7e1d38a504a37edf26955392`.

Does not change production semantics, thresholds, Contract C, or pinned models.

### PR #36 — Research Infrastructure: production trace → explicit decision shadow

| Field | Value |
|---|---|
| URL | https://github.com/camerontjs-dot/claim-audit-lab/pull/36 |
| State | open, draft |
| Base | `main` `53f0885b111676794d1bd20e10b91aa58b07e9d4` |
| Head | `research-infra/production-trace-decision-shadow-20260829` `b487d1dce4cc1a076e3705b0a7ef457e7d438814` |
| Preregistration commit | `0db9f18f40117c274df32dba999cba176752281b` |
| Disposition | `SHADOW_COMPATIBLE_WITH_GAPS` |

Frozen objects named in the PR:

| Object | Identity |
|---|---|
| Diagnostic corpus | `tests/v1/test_pipeline_e2e.py::CASES` blob `48a22cfab82ea0a2abd8d1c80d0da32a3dacd260` |
| Replay adapter | `scripts/decision_model_replay.py` blob `cb26ba5a5ba9174dedbd686ea10dffcaae1a80db` |
| Decision model | `src/claim_audit_lab/v1/decision_model.py` blob `f0d9d3bc061d966ed9c8c16b3424b3dd5c3bb339` |
| Evidence state | blob `e873772588e8c6ac27ced79559812afc8f5e9cdc` |
| Semantic operators | blob `ae64056d2cbec4ed7fd615fe3f4fa6f2bebb177f` |

Primary valid run `33275184773`; independent fully-green repeat `33275342888`. Repeat raw `RESULTS.json` `sha256:a2bab28e138fbadc8343d4efce29d8e42823bf8ee97f1a41fa094b9f45da9bdf`. Scientific object reproduces after removing only `execution_head_sha`.

Quantitative descriptor, not an accuracy claim: 25 cases; 23 terminal agreements; 2 preserved disagreements (`e2e-08`, `e2e-09`); 0 support↔adverse transitions; 6/6 metamorphic controls passed.

### PR #37 — Research: reconcile production-trace shadow and falsify semantic-operator authority

| Field | Value |
|---|---|
| URL | https://github.com/camerontjs-dot/claim-audit-lab/pull/37 |
| State | open, draft, stacked on #36 |
| Base | `research-infra/production-trace-decision-shadow-20260829` `b487d1dce4cc1a076e3705b0a7ef457e7d438814` |
| Head | `research-infra/shadow-reconciliation-semantic-operator-rc-20260829` `64d05b731a4f5b4c0a829a8f03b252fa0103d7fe` |
| Successor preregistration | `87304482dfa8792fda3ed035c98538603280c3ab` |
| Accepted science head | `0d8e67a2cf96e1d6eb665dae2cf9dc11629cfcc8` |
| Accepted Actions run | `33281047763` |
| Disposition | `PARALLEL_RESEARCH_ARTIFACT_JUSTIFIED_WITH_OPERATOR_GAPS` |

`e2e-08` disposition `SUPPORTED_WITH_BOUNDS`: `p_contradict=0.9970703125`; A4 probe `{negated_claim: null, abstained: true, result: null}`; no typed numeric/quantity semantic receipt. Does not validate the numeric refutation.

`e2e-09` disposition `SUPPORTED_WITH_BOUNDS`: sub-threshold `p_contradict=0.673828125`; zero semantic-operator judgments for the refutation.

Larger-shadow preregistration (`CROSS_CORPUS_PREREGISTRATION.md`) is **DESIGN ONLY. DO NOT EXECUTE AS PART OF THIS RC.** Cohort A = all 33 Construction Invariant Gold inputs under an input-only freeze. Cohort B = SLG DEV slice, gated on a separately frozen label-sealed input manifest.

## Current GitHub surfaces relevant to this audit

On live `main` `53f0885b111676794d1bd20e10b91aa58b07e9d4`:

| Surface | Status | Class |
|---|---|---|
| `research/` directory | **absent** (exists only on PR #35–#37 heads) | OBSERVED |
| `tests/` | present, including `tests/v1/` | OBSERVED |
| `tests/v1/test_pipeline_e2e.py` | blob `48a22cfab82ea0a2abd8d1c80d0da32a3dacd260` | OBSERVED |
| `tests/v1/fixtures/traces/` | 25 e2e + 5 inference frozen AuditTrace goldens | OBSERVED |
| `scripts/build_construction_gold.py` | blob `2c677ee29fd121cf1c76b1476664474aa09dc982` | OBSERVED |
| `scripts/audit_construction_gold.py` | present | OBSERVED |
| `scripts/simple_logic_gold.py` and SLG test/harness family | present | OBSERVED |
| `scripts/decision_model_replay.py` | blob `cb26ba5a5ba9174dedbd686ea10dffcaae1a80db` | OBSERVED |
| `docs/research/brief-02-construction-gold.md` | present | OBSERVED |
| `DECISIONS.md` | blob `600ba1577ea703bee99be72dedc7f93b5c89f442` (PR #37 cites this as the 33-case construction surface record) | OBSERVED |
| `.gitignore` | ignores `outputs/` deliberately: “Research outputs are sealed with SHA256SUMS manifests, not version-controlled.” | OBSERVED |
| Pinned retriever | `sentence-transformers/all-MiniLM-L6-v2` revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41` | OBSERVED (PR #35) |
| Pinned entailer | `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli` revision `6f5cf0a2b59cabb106aca4c287eed12e357e90eb` | OBSERVED (PR #35) |

## Hygiene rule that controls migration

GitHub CAL already declares that generated research outputs are not repository objects. Migrating local `outputs/` trees into Git would contradict live repository hygiene unless a separately reviewed exception allowlists a bounded, portable, non-generated artifact.

## Verbose Engine migration authority (controlling where more precise)

Live Verbose Engine HEAD `3b893f1c0c8c80814bc037ff54aceee2db9c38fb`.

`project-governance/GITHUB-AND-PR-GOVERNANCE.md` §29 relationship classes:

| Class | Meaning |
|---|---|
| `SYNCED` | intended local and remote objects match |
| `LOCAL-AHEAD` | local line is a clean descendant of the remote line |
| `REMOTE-AHEAD` | remote line contains commits the local line does not |
| `DIVERGED` | both sides contain distinct commits from a common ancestor |
| `DISCONNECTED` | both histories are legitimate but share no usable ancestor |

The github-preflight Skill in Verbose Engine still uses `GITHUB-AHEAD` / `UNKNOWN`. Where the two disagree, §29 is the more precise **migration** classifier; `UNKNOWN` remains the fail-closed label when ancestry cannot be established.

Other Verbo controls applied here: publication-safety Skill; private-repository capture boundary in `SECURITY-AND-PUBLICATION-SAFETY.md`; isolated worktree; exact staging; clean-clone verification; do not weaken scanners; do not copy the workstation.

## What live GitHub is not

Live GitHub `main` is not the dirty local `feat/v2-epistemic-pipeline` worktree. It is not the frozen candidate `cal-v1-eval-candidate-20260825-01`. It is not the unpublished historical `cal-v1-skeleton` line. Those are local or feature-branch objects.
