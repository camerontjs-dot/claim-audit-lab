"""Research-only integrated smoke for current CAL v1 machinery.

Uses the pinned production retriever + entailer + rules through run_default_audit.
This is operational machinery evidence, not new semantic gold or promotion evidence.
"""

from __future__ import annotations

import json

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.models import AuditRequest, Passage
from claim_audit_lab.v1.runner import run_default_audit


def request(case_id: str, claim: str, passage: str) -> AuditRequest:
    return AuditRequest(
        claim_id=case_id,
        claim_text=claim,
        passages=[Passage(passage_id=f"{case_id}-p1", text=passage, source_meta={})],
        audit_config=load_default_audit_config(),
    )


def main() -> None:
    cases = [
        (
            "support-exact",
            "Administrator actions are logged.",
            "Administrator actions are logged.",
            "supported",
        ),
        (
            "contradiction-exact",
            "The platform logs administrator actions.",
            "The platform does not log any administrator actions.",
            "contradicted",
        ),
        (
            "unrelated-control",
            "The platform encrypts stored customer data.",
            "The local weather forecast predicts rain on Thursday afternoon.",
            None,
        ),
    ]

    rows = []
    for case_id, claim, passage, expected in cases:
        req = request(case_id, claim, passage)
        first = run_default_audit(req)
        second = run_default_audit(req)
        first_json = first.model_dump_json()
        second_json = second.model_dump_json()
        if first_json != second_json:
            raise AssertionError(f"{case_id}: integrated default pipeline is not repeatable")
        verdict = first.verdict.support_verdict
        if expected is not None and verdict != expected:
            raise AssertionError(
                f"{case_id}: expected {expected}, observed {verdict}; "
                f"reason={first.verdict.support_verdict_reason}"
            )
        rows.append(
            {
                "case_id": case_id,
                "claim": claim,
                "passage": passage,
                "verdict": verdict,
                "verdict_reason": first.verdict.support_verdict_reason,
                "retrieval": [item.model_dump(mode="json") for item in first.retrieval],
                "entailment": [item.model_dump(mode="json") for item in first.entailment],
                "support_signal": first.support_signal.model_dump(mode="json"),
                "rules_fired": [item.model_dump(mode="json") for item in first.rules_fired],
            }
        )

    config = load_default_audit_config()
    receipt = {
        "scope": "research-only integrated machinery smoke; not semantic benchmark evidence",
        "retriever": config.retriever.model_dump(mode="json"),
        "entailer": config.entailer.model_dump(mode="json"),
        "rules_file_sha": config.rules_file_sha,
        "cases": rows,
    }
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
