"""Reconcile two adjudicators. Disagreement stays disagreement.

The held-out file is written for the later sealed run. This script prints
counts and the held-out hash, not held-out labels.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _load(name: str) -> dict:
    return json.loads((ROOT / "adjudication" / name).read_text(encoding="utf-8"))


def _window(source_id: str) -> str:
    return (ROOT / "sources" / "text" / f"{source_id}.txt").read_text(encoding="utf-8")


def _exact(claim: dict) -> bool:
    window = _window(str(claim["source_id"]))
    return all(str(item["text"]) in window for item in claim["evidence"])


def _reconcile(left: dict, right: dict, partition: str) -> dict:
    by_id = {item["claim_id"]: item for item in right["claims"]}
    claims = []
    for claim in left["claims"]:
        other = by_id.get(claim["claim_id"])
        record = {
            "claim_id": claim["claim_id"],
            "source_id": claim["source_id"],
            "claim": claim["claim"],
            "evidence": claim["evidence"],
            "intended_proposition": claim.get("intended_proposition", ""),
            "families": claim.get("families", []),
            "scope": claim.get("scope", {}),
            "acceptable_not_checkable": claim.get("acceptable_not_checkable", []),
            "rationale_a": claim.get("rationale", ""),
            "expected_a": claim.get("expected"),
            "expected_b": None if other is None else other.get("expected"),
            "evidence_exact": _exact(claim),
        }
        if other is None or not record["evidence_exact"]:
            record["adjudication_status"] = "invalid"
            record["expected"] = None
        elif record["expected_a"] == record["expected_b"] and record["expected_a"] in {
            "supported",
            "contradicted",
            "not_checkable",
        }:
            record["adjudication_status"] = "agreed"
            record["expected"] = record["expected_a"]
        else:
            record["adjudication_status"] = "disagreed"
            record["expected"] = None
        claims.append(record)
    return {
        "partition": partition,
        "adjudicators": ["A", "B"],
        "claims": claims,
    }


def main() -> None:
    calibration = _reconcile(_load("a/calibration.json"), _load("b/calibration.json"), "calibration")
    heldout = _reconcile(_load("a/heldout.json"), _load("b/heldout.json"), "held_out")
    out = ROOT / "adjudication" / "reconciled"
    out.mkdir(parents=True, exist_ok=True)
    (out / "calibration.json").write_text(
        json.dumps(calibration, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    held_bytes = (json.dumps(heldout, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (out / "heldout.json").write_bytes(held_bytes)
    digest = hashlib.sha256(held_bytes).hexdigest()
    seal = {
        "relative_path": "adjudication/reconciled/heldout.json",
        "sha256": digest,
        "claim_count": len(heldout["claims"]),
        "disagreements": sum(1 for item in heldout["claims"] if item["adjudication_status"] == "disagreed"),
        "invalid": sum(1 for item in heldout["claims"] if item["adjudication_status"] == "invalid"),
    }
    (ROOT / "HELD_OUT_SEAL.json").write_text(
        json.dumps(seal, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "calibration_claims": len(calibration["claims"]),
        "calibration_agreed": sum(1 for item in calibration["claims"] if item["adjudication_status"] == "agreed"),
        "calibration_disagreed": sum(1 for item in calibration["claims"] if item["adjudication_status"] == "disagreed"),
        "held_out_claims": seal["claim_count"],
        "held_out_disagreements": seal["disagreements"],
        "held_out_invalid": seal["invalid"],
        "held_out_sha256": digest,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
