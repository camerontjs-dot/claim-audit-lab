#!/usr/bin/env python3
"""Produce one frozen Evidence Bundler V1 package for independent CAL consumption.

This file is producer-side apparatus. The independent consumer must not import it
or Evidence Bundler implementation code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from evidence_bundler.v1 import V1Config, build_package


def sha_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def contract_a_fixture() -> dict[str, object]:
    root_text = "Alpha exceeded Beta by 4 units and Gamma exceeded Delta by 2 units."
    child_1 = "Alpha exceeded Beta by 4 units."
    child_2 = "Gamma exceeded Delta by 2 units."
    sources = [
        {
            "source_id": "CAL-EB-V1-S1",
            "media_type": "text/plain; charset=utf-8",
            "content": "Alpha exceeded Beta by 4 units. Independent context follows.",
        },
        {
            "source_id": "CAL-EB-V1-S2",
            "media_type": "text/plain; charset=utf-8",
            "content": "Gamma exceeded Delta by 2 units. Independent context follows.",
        },
        {
            "source_id": "CAL-EB-V1-S3",
            "media_type": "text/plain; charset=utf-8",
            "content": "Alpha and Beta appear in a calibration note with units but no deciding comparison.",
        },
        {
            "source_id": "CAL-EB-V1-S4",
            "media_type": "text/plain; charset=utf-8",
            "content": "Gamma and Delta appear in a calibration note with units but no deciding comparison.",
        },
        {
            "source_id": "CAL-EB-V1-S5",
            "media_type": "text/plain; charset=utf-8",
            "content": "Alpha Beta Gamma Delta units context is recorded for retrieval pressure only.",
        },
        {
            "source_id": "CAL-EB-V1-S6",
            "media_type": "text/plain; charset=utf-8",
            "content": "Beta and Alpha units are listed in an unrelated reference table description.",
        },
        {
            "source_id": "CAL-EB-V1-S7",
            "media_type": "text/plain; charset=utf-8",
            "content": "Delta and Gamma units are listed in an unrelated reference table description.",
        },
    ]
    for source in sources:
        source["content_sha256"] = sha_text(str(source["content"]))
    value: dict[str, object] = {
        "schema": "contract-a-wire-candidate-rc2",
        "handoff_id": "cal-eb-v1-structural-handoff",
        "producer": {
            "producer_id": "cal-eb-v1-structural-fixture",
            "producer_version": "1",
        },
        "work": {"work_id": "cal-eb-v1-structural-work"},
        "root_proposition": {
            "proposition_id": "cal-eb-v1:root",
            "text": root_text,
            "text_sha256": sha_text(root_text),
        },
        "decomposition": {
            "state": "declared",
            "decomposition_id": "cal-eb-v1:decomposition:1",
            "operator": "all_of",
            "children": [
                {
                    "proposition_id": "cal-eb-v1:child:1",
                    "text": child_1,
                    "text_sha256": sha_text(child_1),
                    "sequence": 1,
                },
                {
                    "proposition_id": "cal-eb-v1:child:2",
                    "text": child_2,
                    "text_sha256": sha_text(child_2),
                    "sequence": 2,
                },
            ],
        },
        "sources": sources,
        "handoff_sha256": "sha256:" + "0" * 64,
    }
    payload = dict(value)
    payload.pop("handoff_sha256")
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    value["handoff_sha256"] = "sha256:" + hashlib.sha256(encoded).hexdigest()
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    contract_a = contract_a_fixture()
    config = V1Config()
    first = build_package(contract_a=contract_a, config=config)

    decisions: dict[tuple[str, str], str] = {}
    expected_sources = {
        "cal-eb-v1:child:1": "CAL-EB-V1-S1",
        "cal-eb-v1:child:2": "CAL-EB-V1-S2",
    }
    for proposition_id, source_id in expected_sources.items():
        matches = [
            row
            for row in first["candidates"]
            if row["proposition_id"] == proposition_id
            and row["source_id"] == source_id
            and row["selection_state"] == "retained"
        ]
        if len(matches) != 1:
            raise RuntimeError(
                f"fixture must yield one retained candidate for {proposition_id}/{source_id}; "
                f"observed={len(matches)}"
            )
        decisions[(proposition_id, str(matches[0]["passage_id"]))] = "accepted"

    package = build_package(contract_a=contract_a, config=config, admission=decisions)
    if not any(row["selection_state"] == "not_retained" for row in package["candidates"]):
        raise RuntimeError("fixture must expose at least one non-retained candidate")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(package, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    receipt = {
        "schema": "cal-eb-v1-producer-receipt-v1",
        "eb_head": "c4e3f97ec8f0bd36180954c3aa382418925bf947",
        "package_sha256": package["package_sha256"],
        "accepted_count": sum(
            row["admission_state"] == "accepted" for row in package["candidates"]
        ),
        "support_refutation_or_verdict_authored": False,
    }
    args.out.with_name("producer-receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
