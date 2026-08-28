"""Mechanically isolated RC1 consumer projector.

Isolation boundary: this module imports no CAL code and no RC1 producer projector.
It accepts only the documented candidate-package mapping. It is intentionally
small so a contamination scan can verify the boundary. Authorship is not claimed
as independently commissioned; see the RC1 failed-attempt record.
"""

from __future__ import annotations

from typing import Any

_REQUIRED = {"identity", "evidence", "assessments", "conclusion", "execution"}


def project_publication_review(package: dict[str, Any]) -> dict[str, Any]:
    missing = sorted(_REQUIRED - package.keys())
    if missing:
        raise ValueError("package missing: " + ", ".join(missing))

    proposition = package["identity"]["proposition"]
    conclusion = package["conclusion"]
    assessments = package["assessments"]
    execution = package["execution"]

    if execution["status"] != "completed":
        posture = "hold_execution_incomplete"
    elif any(item.get("state") == "failed" for item in assessments.values()):
        posture = "hold_assessment_failed"
    elif assessments.get("aperture", {}).get("state") == "performed" and assessments[
        "aperture"
    ].get("value") in {"unknown", "incomplete"}:
        posture = "hold_aperture_unresolved"
    elif conclusion["reported_verdict"] in {"supported", "partially_supported"}:
        posture = "eligible_for_publication_review"
    elif conclusion["reported_verdict"] == "not_checkable":
        posture = "hold_unresolved"
    else:
        posture = "not_supportable_as_written"

    return {
        "result_id": package["result_id"],
        "proposition_id": proposition["proposition_id"],
        "proposition_text_sha256": proposition["text_sha256"],
        "reported_verdict": conclusion["reported_verdict"],
        "reason_code": conclusion.get("reason_code"),
        "counterevidence_ids": list(conclusion["residual"]["counterevidence_ids"]),
        "aperture": dict(assessments["aperture"]),
        "execution_status": execution["status"],
        "review_posture": posture,
    }


def render_compact_report(package: dict[str, Any], *, renderer_policy_id: str) -> str:
    view = project_publication_review(package)
    return (
        f"# CAL audit result {view['proposition_id']}\n\n"
        f"Renderer: `{renderer_policy_id}`\n"
        f"Result: `{view['result_id']}`\n"
        f"Verdict: `{view['reported_verdict']}`\n"
        f"Reason: `{view['reason_code'] or 'none'}`\n"
        f"Execution: `{view['execution_status']}`\n"
        f"Counterevidence: `{','.join(view['counterevidence_ids']) or 'none'}`\n"
        f"Aperture: `{view['aperture'].get('state')}/{view['aperture'].get('value', 'none')}`\n"
        f"Projection posture: `{view['review_posture']}`\n"
    )
