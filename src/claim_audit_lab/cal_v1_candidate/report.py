from __future__ import annotations

import json

from .engine import AuditResult
from .models import AuditContext, CategoricalRelation


PROFILE = "cal-v1-candidate-2026-09"


def render_markdown(context: AuditContext, result: AuditResult) -> str:
    aperture = json.dumps(
        context.evidence_world.aperture_observation(),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )
    lines = [
        "# Claim Audit Lab V1 candidate report",
        "",
        f"- Profile: `{PROFILE}`",
        f"- Proposition: {context.original_claim}",
        f"- Proposition ID: `{context.proposition.proposition_id}`",
        f"- Proposition text SHA-256: `{context.proposition.text_sha256}`",
        f"- Semantic family: `{result.semantic_family.value}`",
        f"- Conclusion: `{result.conclusion.value}`",
        (
            f"- Failure localization: `{result.failure_code.value}`"
            if result.failure_code is not None
            else "- Failure localization: none"
        ),
        (
            f"- Contract B: `{context.evidence_world.contract_b_version}` / "
            f"`{context.evidence_world.bundle_id}`"
        ),
        f"- Contract B bundle hash: `{context.evidence_world.bundle_hash}`",
        f"- Evidence-world SHA-256: `{result.evidence_world_sha256}`",
        "- Limitation: supported only by the admitted evidence under this CAL profile.",
        (
            "- Aperture note: the upstream observation below is audit state, "
            "not a CAL completeness conclusion."
        ),
        "",
        "## Upstream aperture observation",
        "",
        "```json",
        aperture,
        "```",
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
                f"### `{trace.passage_id}`: {role}",
                "",
                passage.text,
                "",
                f"Source: `{passage.source_id}`; passage SHA-256: `{passage.text_sha256}`.",
                (
                    f"Measurement: `{trace.measurement.instrument_id}` / "
                    f"`{trace.measurement.instrument_version}` / "
                    f"receipt `{trace.measurement.receipt_id}`."
                    if trace.measurement is not None
                    else "Measurement: not performed."
                ),
                (
                    f"Available evidence: `{', '.join(trace.measurement.available_passage_ids)}`; "
                    f"consumed: `{', '.join(trace.measurement.consumed_passage_ids)}`."
                    if trace.measurement is not None
                    else "Available/consumed measurement evidence: not applicable."
                ),
                (
                    f"Semantic authority: `{trace.authority.authority_id}`."
                    if trace.authority is not None
                    else "Semantic authority: not established."
                ),
                (
                    "Proposition-relative relation: "
                    f"`{trace.relation.categorical_relation.value}` / "
                    f"`{trace.relation.relation_id}`."
                    if trace.relation is not None
                    else "Proposition-relative relation: unresolved/not derived."
                ),
                (
                    f"Failure localization: `{trace.failure_code.value}`."
                    if trace.failure_code is not None
                    else "Failure localization: none."
                ),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
