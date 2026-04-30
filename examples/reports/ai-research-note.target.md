# AI research memo audit

*Hand-authored target output. The renderer this file describes does not yet exist; treat this as a UX spec and a future golden file, not as proof the current code can produce it.*

## Metadata

- Draft: `examples/drafts/ai-research-note.md`
- Evidence bundle: `examples/evidence/ai-research-evidence.yml`
- Report type: hand-authored target output
- Generated report status: not implemented; planned in Phase 7
- Audit boundary: Claim Audit Lab audits whether claims are supported by supplied evidence. It does not verify external truth.

## Executive summary

Four claims extracted. Findings: 1 supported, 1 partially supported, 0 unsupported, 2 overstated, 0 needs-source, 0 not-audit-ready. Two claims overstate what the supplied evidence can carry, and one of those two is the headline sentence of the memo.

These findings cover supplied-evidence support only. The audit makes no statement about whether the intervention actually works in the world. The claim is narrower: the supplied evidence does not back the strong wording the draft uses.

## Limitations

- Supplied evidence only. The audit cannot reach beyond the bundle.
- Fictional fixture data. The source, excerpts, and numbers are demo material, not a real study.
- No external source lookup. The tool does not search the web or call an LLM.
- Single-source bundle at medium reliability. Any claim resting on this bundle inherits that ceiling.
- This output may include behavior the current code does not yet produce.

## Claim register

| Claim ID | Claim text | Type | Support | Risk | Strongest evidence | Main issue |
|---|---|---|---|---|---|---|
| `claim-ai001` | The intervention clearly eliminates unsupported claims in multi-step AI research workflows. | scope | overstated | high | `source-001` / `excerpt-001` | Source shows reduction (18 to 11), not elimination, and covers one test set rather than "multi-step AI research workflows" in general. |
| `claim-ai002` | The test set included 52 workflow outputs. | numeric | supported | low | `source-001` / `excerpt-002` | Direct numeric match. |
| `claim-ai003` | Unsupported claims fell from 18 outputs to 11 outputs after the provenance checklist was added. | numeric | partially_supported | medium | `source-001` / `excerpt-001` | Numbers match. Causal sequencing ("after ... was added") is consistent with the excerpt but not directly attested. |
| `claim-ai004` | The checklist will always prevent researchers from relying on weak evidence. | prediction | overstated | high | (none) | "Always" plus future certainty cannot be supported by a single test-set result. |

Stable claim IDs above are placeholders. Once the renderer exists, the engine should generate IDs deterministically from the draft and claim text per the `Claim.id` rule in `models.py`, and this file should be regenerated as the golden reference.

## Claim details

### Claim ai001 (overstated)

> The intervention clearly eliminates unsupported claims in multi-step AI research workflows.

Type: scope. Support: overstated. Risk: high.

**Candidate evidence**

- `source-001` / `excerpt-001`: "The intervention reduced unsupported claims in the test set from 18 to 11."

**Rule flags**

- Overconfident wording. "Clearly eliminates" implies full removal. The excerpt shows partial reduction.
- Scope generalization. The claim covers "multi-step AI research workflows" as a category. The supplied source covers one 52-output test set under a single rubric.

**Explanation**

Two distinct overreaches sit in one sentence. The verb overstates magnitude (the source shows reduction, not elimination). The phrase "multi-step AI research workflows" overstates scope (the source describes one test set). Either flaw alone would push toward `overstated`; together they make this the highest-risk claim in the memo.

**Suggested rewrite**

> In one fictional 52-output test set, the provenance checklist reduced the count of outputs containing unsupported claims from 18 to 11.

---

### Claim ai002 (supported)

> The test set included 52 workflow outputs.

Type: numeric. Support: supported. Risk: low.

**Candidate evidence**

- `source-001` / `excerpt-002`: "The test set included 52 workflow outputs reviewed against the same claim-audit rubric."

**Rule flags:** none.

**Explanation**

Numeric value matches the excerpt directly. No hedging required. The supplied evidence supports this statement at face value within the demo bundle.

---

### Claim ai003 (partially_supported)

> Unsupported claims fell from 18 outputs to 11 outputs after the provenance checklist was added.

Type: numeric, with causal framing. Support: partially_supported. Risk: medium.

**Candidate evidence**

- `source-001` / `excerpt-001`: "The intervention reduced unsupported claims in the test set from 18 to 11."

**Rule flags**

- Causal framing on correlational evidence. "After the provenance checklist was added" frames the checklist as the cause. The excerpt describes a reduction but does not, in this bundle, distinguish correlation from causation.

**Explanation**

The numeric portion is supported. The causal framing leans on "after," weaker than "because of" but still implying the checklist did the work. With only the supplied excerpt and its author note ("supports reduction, not elimination"), the audit cannot fully back the causal reading.

**Suggested rewrite**

> In the same fictional test set, outputs with unsupported claims fell from 18 to 11 alongside the provenance checklist intervention.

---

### Claim ai004 (overstated)

> The checklist will always prevent researchers from relying on weak evidence.

Type: prediction. Support: overstated. Risk: high.

**Candidate evidence:** none in the supplied bundle.

**Rule flags**

- Future certainty. "Will always" makes a universal future claim. No supplied source can back a universal claim from a single demo run.
- Overconfident wording. "Always prevent" leaves no room for failure modes the evaluation did not test.

**Explanation**

No excerpt in the bundle describes future behavior or a universal preventive effect. The claim floats free of the evidence supplied. Marking it `unsupported` would also be defensible. The choice of `overstated` reflects that the underlying intervention has some demo evidence behind it, just not at the strength the wording asserts. The renderer should document which rule decides this split.

**Suggested rewrite**

> In this fictional test set, the checklist appeared to reduce reliance on weak evidence. Whether it does so in other settings is not addressed by the supplied evidence.

## Evidence register

| Source ID | Title | Type | Reliability | Date | Excerpts |
|---|---|---|---|---|---|
| `source-001` | Fictional provenance checklist evaluation | report | medium | 2026-04-01 | `excerpt-001`, `excerpt-002` |

**`excerpt-001`:** "The intervention reduced unsupported claims in the test set from 18 to 11."

Author note: "Fictional demo evidence. Supports reduction, not elimination."

What it can support: the magnitude of reduction in the test set, the before/after counts, and the existence of the intervention.

What it cannot support: elimination, generalization beyond the test set, or a causal inference stronger than the excerpt itself states.

**`excerpt-002`:** "The test set included 52 workflow outputs reviewed against the same claim-audit rubric."

Author note: "Fictional demo evidence for sample size."

What it can support: sample size of 52 and a shared rubric across the set.

What it cannot support: generalization to populations outside this test set.

The bundle has one source at medium reliability. There is no high-reliability corroboration and no second source. Any claim resting on this bundle alone inherits that ceiling.

## Suggested rewrites

The draft can preserve its core finding without overclaiming. One safer version of the full memo:

> In a fictional 52-output test set, adding a provenance checklist coincided with a drop in outputs containing unsupported claims, from 18 to 11. The single test set and medium-reliability source mean this should not be read as proof that the checklist eliminates unsupported claims, or that it would do so in other AI research workflows.

That version keeps the numeric finding, drops "clearly eliminates" and "always," and names the limit on scope and source quality without sounding apologetic.

## Design questions surfaced

Hand-writing this report exposed choices the renderer will need to make.

1. **Multi-flag claims.** `claim-ai001` carries two distinct flags (overconfidence and scope). Should the report emit them as separate `RuleFlag` entries (current schema supports this) or combine them into one merged flag? Separate reads cleaner against the validation matrix; combined reads better in prose.
2. **Mixed numeric-plus-causal claims.** `claim-ai003` is numeric in surface form and causal in framing. Does extraction tag it as one type (`numeric`) and let rules carry the causal flag, or does the model need a multi-type list? The current `ClaimType` is a single literal; a future schema decision is whether to split or extend.
3. **Subclaim ID stability.** If extraction later splits a sentence into atomic subclaims, the SHA-256 ID derived from the full sentence will not match the IDs of its parts. Decide whether subclaim IDs derive from the parent claim ID plus a stable index, or independently from subclaim text.
4. **`overstated` vs `unsupported` for unbacked predictions.** No supplied evidence touches `claim-ai004`, which argues for `unsupported`. The underlying intervention has some demo backing, which argues for `overstated`. The renderer should document the rule that decides between these two labels.
5. **Reliability ceilings.** When a bundle contains only medium-reliability sources, should the report add a top-level limitation, or only flag affected claims? Top-level reads as a clearer caveat for reviewers.
6. **Suggested rewrite location.** Do rewrites belong in the per-claim section, in a dedicated rewrites section, or in both? This file uses both for redundancy. The renderer should pick one home and link to the other.
7. **Risk-label summary.** Two `high` risk claims and one `medium` is a meaningful summary signal. The current `AuditSummary` exposes `high_risk_claims` as a count; consider surfacing it in the executive summary line, not only the schema.
8. **Quoting the claim.** This file blockquotes each claim text below the H3 heading. Decide whether the renderer does the same, or relies on the table-only presentation.
