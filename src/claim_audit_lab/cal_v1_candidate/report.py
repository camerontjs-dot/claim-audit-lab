from __future__ import annotations

from .engine import AuditResult
from .models import AuditContext, CategoricalRelation


PROFILE = "cal-v1-candidate-2026-09"


def render_markdown(context: AuditContext, result: AuditResult) -> str:
    lines = [
        "# Claim Audit Lab V1 candidate report",
        "",
        f"- Profile: `{PROFILE}`",
        f"- Proposition: {context.original_claim}",
        f"- Semantic family: `{result.semantic_family.value}`",
        f"- Conclusion: `{result.conclusion.value}`",
        (
            f"- Contract B: `{context.evidence_world.contract_b_version}` / "
            f"`{context.evidence_world.bundle_id}`"
        ),
        f"- Evidence-world SHA-256: `{result.evidence_world_sha256}`",
        "- Limitation: supported only by the admitted evidence under this CAL profile.",
        "",
        "## Evidence",
        "",
    ]
    for trace in result.traces:
        passage = context.evidence_world.passage(trace.passage_id)
        role = "non_deciding"
        if trace.relation is not None:
            if trace.relation.categorical_relation is CategoricalRelation.SUPPORTS:
                role = "support"
            elif trace.relation.categorical_relation is CategoricalRelation.REFUTES:
                role = "counterevidence"
        lines.extend(
            [
                f"### `{trace.passage_id}` — {role}",
                "",
                passage.text,
                "",
                f"Source: `{passage.source_id}`; SHA-256: `{passage.text_sha256}`.",
                "",
            ]
        )
        if trace.failure_code is not None:
            lines.append(f"Failure localization: `{trace.failure_code.value}`.\n")
    return "\n".join(lines).rstrip() + "\n"
