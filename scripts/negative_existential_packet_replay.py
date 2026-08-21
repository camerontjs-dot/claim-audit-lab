#!/usr/bin/env python3
"""Replay the frozen D5 DEV packet through pipeline and evidence-state shadows."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.impl.aggregator import MaxEntailmentAggregator
from claim_audit_lab.v1.impl.features import DefaultFeatureExtractor
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.models import AuditRequest, EntailResult, Passage
from claim_audit_lab.v1.pipeline import run_audit
from scripts.evidence_state_eligibility_shadow import build_eligibility_report
from scripts.evidence_state_operator_shadow import build_operator_report
from scripts.evidence_state_shadow import build_report
from scripts.negative_existential_operator_shadow import judgment_from_probe


@dataclass(frozen=True)
class FrozenRetriever:
    passage_id: str
    score: float

    def retrieve(self, claim: str, passages: list[Passage], top_k: int) -> list[Any]:
        from claim_audit_lab.v1.models import RetrievalResult

        return [RetrievalResult(passage_id=self.passage_id, score=self.score)]


@dataclass(frozen=True)
class FrozenEntailer:
    passage_id: str
    direct: dict[str, Any]
    probes: dict[str, dict[str, Any]]

    def entail(self, claim: str, premise: str, passage_id: str) -> EntailResult:
        receipt = self.probes.get(claim, self.direct)
        return EntailResult(
            passage_id=passage_id,
            label=receipt["label"],
            score=float(receipt["score"]),
            raw_logits=tuple(receipt["raw_logits"]),
            p_entail=self.direct.get("p_entail") if receipt is self.direct else None,
            p_contradict=self.direct.get("p_contradict") if receipt is self.direct else None,
        )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay(packet_path: Path, receipts_path: Path, output_dir: Path) -> dict[str, Any]:
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    receipts = json.loads(receipts_path.read_text(encoding="utf-8"))
    if receipts["receipt_kind"] != "deterministic_stub" or receipts["model_inference"]:
        raise ValueError("D5 replay accepts only explicit non-model deterministic receipts")
    output_dir.mkdir(parents=True, exist_ok=True)
    trace_dir = output_dir / "traces"
    trace_dir.mkdir(exist_ok=True)
    config = load_default_audit_config()
    judgments = []
    for case in packet["cases"]:
        receipt = receipts["cases"][case["claim_id"]]
        probes = {}
        if (production := receipt.get("production_probe")) is not None:
            probes[production["hypothesis"]] = production
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
            retriever=FrozenRetriever(case["passage_id"], receipt["retrieval_score"]),
            entailer=FrozenEntailer(case["passage_id"], receipt["direct"], probes),
            aggregator=MaxEntailmentAggregator(),
            rules=VerdictRules(rules_file_sha=config.rules_file_sha),
        )
        (trace_dir / f"{case['claim_id']}.json").write_text(
            trace.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        canonical = receipt["canonical_probe"]
        if trace.entailment and case["claim_id"] != "d5-insufficient":
            judgments.append(
                judgment_from_probe(
                    claim_id=case["claim_id"],
                    passage_id=case["passage_id"],
                    claim=case["claim"],
                    probed_hypothesis=canonical["hypothesis"],
                    probe_label=canonical["label"],
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
    summary = {
        "schema_version": "cal-d5-packet-replay-v0.1",
        "production_behavior_changed": False,
        "receipt_kind": receipts["receipt_kind"],
        "model_inference": False,
        "packet_sha256": sha256(packet_path),
        "receipts_sha256": sha256(receipts_path),
        "rows": [
            {
                "claim_id": row["claim_id"],
                "production": row["current_verdict"],
                "raw_state": row["raw_state"],
                "eligible_state": row["eligible_state"],
                "operator_state": row["operator_state"],
                "operator_shadow_verdict": row["operator_shadow_verdict"],
            }
            for row in operator["rows"]
        ],
    }
    (output_dir / "result.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--receipts", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(replay(args.packet, args.receipts, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
