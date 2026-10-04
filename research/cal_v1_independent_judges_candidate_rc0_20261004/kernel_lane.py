"""Bounded legacy lane. Authoring refusal stays local to this process.

The lane calls the unchanged production semantic engine. It does not strip
scope from a claim to force that grammar to match.
"""

from __future__ import annotations

import hashlib
from typing import Any

from claim_audit_lab.production_v1 import CONTRACT_B_VERSION, SEMANTIC_IMPLEMENTATION_SHA
from claim_audit_lab.production_v1.semantic.engine import audit
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)
from claim_audit_lab.production_v1.targeting import TargetAuthoringError, author_target

from codec import digest, parse_envelope


def _not_applicable(raw: bytes, cause: str, detail: str) -> dict[str, Any]:
    return {
        "process_id": "kernel_legacy",
        "input_sha256": digest(raw),
        "execution": "completed",
        "applicability": "not_applicable",
        "role": "relation",
        "conclusion": "not_applicable",
        "warrant": "qualified",
        "material_loss": False,
        "abstention_cause": cause,
        "authoring_status": "refused",
        "authoring_detail": detail,
        "instrument_id": "frozen-kernel",
        "instrument_version": SEMANTIC_IMPLEMENTATION_SHA,
        "model": None,
        "dependence_group": "frozen-kernel",
        "local_material_conflict": False,
        "semantic_implementation": SEMANTIC_IMPLEMENTATION_SHA,
    }


def judge(raw: bytes) -> dict[str, Any]:
    envelope = parse_envelope(raw)
    try:
        target = author_target("rc0-claim", envelope["claim"])
    except TargetAuthoringError as exc:
        return _not_applicable(raw, "authoring_refusal", str(exc).split(":", 1)[0])
    proposition = target["proposition"]
    typed = TypedProposition.create(
        "rc0-claim",
        SemanticFamily(proposition["semantic_family"]),
        proposition["fields"],
        text_sha256=proposition["text_sha256"],
    )
    passages = tuple(
        AdmittedPassage.create(item["id"], item["id"], item["text"]) for item in envelope["evidence"]
    )
    world = EvidenceWorld.create(
        CONTRACT_B_VERSION,
        "rc0-synthetic-envelope",
        "sha256:" + hashlib.sha256(raw).hexdigest(),
        passages,
        {
            "available_world": "supplied_passages_only",
            "raw_source_archive": "unavailable",
        },
    )
    result = audit(AuditContext(envelope["claim"], typed, world))
    mapped = {
        "supported": "supports",
        "contradicted": "refutes",
        "not_checkable": "unresolved",
        "not_composed": "unresolved",
    }[result.conclusion.value]
    cause = None if mapped in {"supports", "refutes"} else (
        "missing_evidence" if not envelope["evidence"] else (result.failure_code.value if result.failure_code else "kernel_non_deciding")
    )
    if result.failure_code is not None and result.failure_code.value == "MIXED_RELATIONS":
        cause = "material_conflict"
    return {
        "process_id": "kernel_legacy",
        "input_sha256": digest(raw),
        "execution": "completed",
        "applicability": "applicable",
        "role": "relation",
        "conclusion": mapped,
        "warrant": "qualified",
        "material_loss": False,
        "abstention_cause": cause,
        "authoring_status": "accepted",
        "kernel_conclusion": result.conclusion.value,
        "kernel_failure": None if result.failure_code is None else result.failure_code.value,
        "semantic_family": proposition["semantic_family"],
        "authored_fields": proposition["fields"],
        "instrument_id": "frozen-kernel",
        "instrument_version": SEMANTIC_IMPLEMENTATION_SHA,
        "model": None,
        "dependence_group": "frozen-kernel",
        "local_material_conflict": cause == "material_conflict",
        "semantic_implementation": SEMANTIC_IMPLEMENTATION_SHA,
        "consumed_passage_ids": [item["id"] for item in envelope["evidence"]],
        "available_passage_ids": [item["id"] for item in envelope["evidence"]],
        "consumed_claim": envelope["claim"],
    }
