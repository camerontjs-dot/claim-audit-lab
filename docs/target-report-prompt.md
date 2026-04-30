# Target report drafting prompt

status: ready
last_updated: 2026-04-30
output_target: examples/reports/ai-research-note.target.md

Use this prompt to hand-write the first target report for Claim Audit Lab. The point is to settle the UX of an audit report before any renderer exists, so the renderer has a concrete golden file to converge on later. The output is a paper design, not a claim about what the current code can produce.

```text
We are in `/Users/gammaquantum/My Drive/projects/job-hunt/portfolio/live-asset/claim-audit-lab`.

Task: hand-write `examples/reports/ai-research-note.target.md` as the aspirational target output for the existing AI research memo fixture.

Read these files first:

1. `README.md`
2. `docs/master-plan.md`
3. `docs/validation-matrix-reference.md`
4. `examples/drafts/ai-research-note.md`
5. `examples/evidence/ai-research-evidence.yml`
6. `src/claim_audit_lab/models.py`

Project boundary:

Claim Audit Lab audits whether claims are supported by supplied evidence. It does not verify external truth. The target report is hand-authored, not generated output.

Rules for the draft:

- Mark the file clearly as `hand-authored target output`.
- Do not use `true`, `false`, `fact checked`, `verified`, or `proven` as capability claims.
- Do not invent evidence beyond what the supplied bundle contains.
- Preserve uncertainty, partial support, and source limitations visibly.

Report goal:

Write the report we wish the tool would generate once the renderer exists. Treat it as a UX spec and a future golden file, not as a claim that the current code can produce it.

Required report sections:

1. Title and metadata
   - draft ID or path
   - evidence bundle ID or path
   - report type: hand-authored target output
   - intended future generated report status

2. Executive summary
   - count-style summary of supported, partially supported, unsupported, overstated, and needs-source claims
   - clear statement that findings cover supplied-evidence support, nothing else

3. Limitations
   - supplied evidence only
   - fictional fixture data
   - no external source lookup
   - target output may include behavior the current code does not yet produce

4. Claim register
   - table with claim ID placeholder, claim text, claim type, support label, risk label, strongest evidence, and main issue
   - use stable-looking claim IDs, and note the renderer should replace them with generated IDs once it exists

5. Claim details
   For each important claim, include:
   - claim text
   - support assessment
   - candidate evidence links by source ID and excerpt ID
   - rule flags or limitations
   - explanation
   - suggested rewrite where useful

6. Evidence register
   - source IDs
   - excerpt IDs
   - reliability labels
   - short description of what each source can and cannot support

7. Suggested rewrites
   - rewrite overstrong claims into evidence-supported language
   - preserve meaning where possible, but reduce certainty, causality, or scope when evidence is weaker

8. Design questions surfaced
   - list any report-rendering, rule, scoring, ID, or fixture questions the hand-written report exposes

Style:

- Plain, professional, reviewer-friendly Markdown.
- Short explanations over long essays.
- Make uncertainty visible without sounding apologetic.
- Use `supported`, `partially_supported`, `unsupported`, `overstated`, `needs_source`, and `not_audit_ready` only as the current model vocabulary defines them.

After writing the file:

- Update `docs/master-plan.md` if the target report surfaces new design decisions.
- Update `docs/verification.md` with a documentation-only note.
- Do not mark validation matrix rows as verified unless current code or checked-in generated artifacts actually meet the acceptance criteria.
```
