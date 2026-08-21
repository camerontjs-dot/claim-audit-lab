#!/usr/bin/env python3
"""One-shot offline replay of the frozen D5 packet with the pinned entailer."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import torch
import transformers

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.impl.aggregator import MaxEntailmentAggregator
from claim_audit_lab.v1.impl.entailer import DeBERTaEntailer
from claim_audit_lab.v1.impl.features import DefaultFeatureExtractor
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.models import AuditRequest, EntailResult, Passage
from claim_audit_lab.v1.pipeline import run_audit
from scripts.evidence_state_eligibility_shadow import build_eligibility_report
from scripts.evidence_state_operator_shadow import build_operator_report
from scripts.evidence_state_shadow import build_report
from scripts.negative_existential_operator_shadow import judgment_from_probe
from scripts.negative_existential_packet_replay import FrozenRetriever


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_offline() -> dict[str, str]:
    required = {"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
    actual = {name: os.environ.get(name, "") for name in required}
    if actual != required:
        raise ValueError(f"offline environment required: {required}; received {actual}")
    return actual


@dataclass
class RecordingEntailer:
    delegate: DeBERTaEntailer
    calls: list[dict[str, Any]] = field(default_factory=list)

    def entail(self, claim: str, premise: str, passage_id: str) -> EntailResult:
        started = datetime.now(UTC).isoformat()
        result = self.delegate.entail(claim, premise, passage_id)
        finished = datetime.now(UTC).isoformat()
        self.calls.append(
            {
                "premise": premise,
                "hypothesis": claim,
                "passage_id": passage_id,
                "started_at": started,
                "finished_at": finished,
                "result": result.model_dump(mode="json"),
            }
        )
        return result


def replay(
    packet_path: Path, manifest_path: Path, output_dir: Path, invocation: str
) -> dict[str, Any]:
    require_offline()
    if output_dir.exists():
        raise FileExistsError(f"one-shot output already exists: {output_dir}")
    packet_hash = sha256(packet_path)
    manifest_hash = sha256(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_packet_hash = manifest["files"]["packet.json"].removeprefix("sha256:")
    if packet_hash != expected_packet_hash:
        raise ValueError(
            f"packet hash mismatch: expected {expected_packet_hash}; got {packet_hash}"
        )
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    if len(packet["cases"]) != 5:
        raise ValueError("authorized packet must contain exactly five cases")

    output_dir.mkdir(parents=True)
    trace_dir = output_dir / "traces"
    trace_dir.mkdir()
    config = load_default_audit_config()
    entailer = RecordingEntailer(DeBERTaEntailer(revision=config.entailer))
    judgments = []
    run_started = datetime.now(UTC).isoformat()

    for case in packet["cases"]:
        passage = Passage(
            passage_id=case["passage_id"],
            text=case["passage"],
            source_meta={"trust_level": "primary"},
        )
        trace = run_audit(
            AuditRequest(
                claim_id=case["claim_id"],
                claim_text=case["claim"],
                passages=[passage],
                audit_config=config,
            ),
            feature_extractor=DefaultFeatureExtractor(),
            retriever=FrozenRetriever(case["passage_id"], 0.90),
            entailer=entailer,
            aggregator=MaxEntailmentAggregator(),
            rules=VerdictRules(rules_file_sha=config.rules_file_sha),
        )
        (trace_dir / f"{case['claim_id']}.json").write_text(
            trace.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )

        canonical = {
            "d5-supported": "At least one leak was reported during the shift.",
            "d5-refuted": "At least one leak was reported during the shift.",
            "d5-insufficient": "At least one leak was reported during the shift.",
            "ordinary-refuted": "The system did archive records.",
            "d5-ambiguous": None,
        }[case["claim_id"]]
        if canonical is not None:
            probe = entailer.entail(canonical, case["passage"], case["passage_id"])
            judgments.append(
                judgment_from_probe(
                    claim_id=case["claim_id"],
                    passage_id=case["passage_id"],
                    claim=case["claim"],
                    probed_hypothesis=canonical,
                    probe_label=probe.label,
                )
            )
        else:
            judgments.append(
                judgment_from_probe(
                    claim_id=case["claim_id"],
                    passage_id=case["passage_id"],
                    claim=case["claim"],
                    probed_hypothesis=None,
                    probe_label=None,
                )
            )

    raw = build_report(trace_dir, signal_floor=0.20)
    eligible = build_eligibility_report(
        trace_dir, signal_floor=0.20, trust_by_source={"dev-primary": "primary"}
    )
    operator = build_operator_report(eligible, judgments)
    for name, report in (("raw", raw), ("eligibility", eligible), ("operator", operator)):
        (output_dir / f"{name}-shadow.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )

    expected = {
        "d5-supported": ("support_only", "supported"),
        "d5-refuted": ("refutation_only", "contradicted"),
        "d5-insufficient": ("read_silent", "unsupported"),
        "ordinary-refuted": ("refutation_only", "contradicted"),
        "d5-ambiguous": ("read_silent", "unsupported"),
    }
    rows = []
    for row in operator["rows"]:
        want_state, want_verdict = expected[row["claim_id"]]
        rows.append(
            {
                "claim_id": row["claim_id"],
                "production": row["current_verdict"],
                "raw_state": row["raw_state"],
                "eligible_state": row["eligible_state"],
                "operator_state": row["operator_state"],
                "operator_shadow_verdict": row["operator_shadow_verdict"],
                "expected_operator_state": want_state,
                "expected_operator_shadow_verdict": want_verdict,
                "prediction_held": row["operator_state"] == want_state
                and row["operator_shadow_verdict"] == want_verdict,
            }
        )

    receipt = {
        "schema_version": "cal-d5-pinned-entailer-receipt-v0.1",
        "receipt_kind": "pinned_production_entailer",
        "model_inference": True,
        "run_started_at": run_started,
        "run_finished_at": datetime.now(UTC).isoformat(),
        "invocation": invocation,
        "offline_environment": require_offline(),
        "environment_caveats": [
            "Local macOS arm64 CPU execution; no network or downloads were permitted.",
            "Frozen retrieval score 0.90 isolates the pinned production entailer "
            "and existing shadows.",
            "This five-case DEV packet is not validation or an accuracy estimate.",
        ],
        "package_identity": {
            "claim-audit-lab": importlib.metadata.version("claim-audit-lab"),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "torch": torch.__version__,
            "transformers": transformers.__version__,
        },
        "model_identity": config.entailer.model_dump(mode="json"),
        "rules_file_sha": config.rules_file_sha,
        "packet_sha256": packet_hash,
        "manifest_sha256": manifest_hash,
        "inference_calls": entailer.calls,
    }
    receipt_path = output_dir / "model-receipts.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    result = {
        "schema_version": "cal-d5-pinned-entailer-result-v0.1",
        "production_behavior_changed": False,
        "packet_sha256": packet_hash,
        "manifest_sha256": manifest_hash,
        "model_receipts_sha256": sha256(receipt_path),
        "all_predictions_held": all(row["prediction_held"] for row in rows),
        "rows": rows,
    }
    (output_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    invocation = " ".join(sys.argv)
    print(json.dumps(replay(args.packet, args.manifest, args.output_dir, invocation), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
