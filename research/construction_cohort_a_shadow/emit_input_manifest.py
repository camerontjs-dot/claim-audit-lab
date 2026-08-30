#!/usr/bin/env python3
"""Emit the blind input-only Construction Gold Cohort A manifest.

This script deliberately does NOT call build() or derive_verdict(). It reads only
input declarations from the canonical construction builder module.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

BUILDER_PATH = Path("scripts/build_construction_gold.py")
EXPECTED_BUILDER_BLOB = "2c677ee29fd121cf1c76b1476664474aa09dc982"
FORBIDDEN_KEYS = {
    "expected_verdict",
    "gold",
    "gold_verdict",
    "derivation",
    "expected_rule",
    "historical_cal",
    "audit_results",
}


def _load_builder(project: Path) -> ModuleType:
    path = project / BUILDER_PATH
    spec = importlib.util.spec_from_file_location("cohort_a_builder_inputs", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load construction builder {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _assert_no_forbidden(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FORBIDDEN_KEYS:
                raise RuntimeError(f"forbidden assessment key in execution manifest: {path}.{key}")
            _assert_no_forbidden(item, f"{path}.{key}")
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            _assert_no_forbidden(item, f"{path}[{idx}]")


def emit(project: Path) -> dict[str, Any]:
    import subprocess

    observed = subprocess.check_output(
        ["git", "hash-object", str(project / BUILDER_PATH)], text=True
    ).strip()
    if observed != EXPECTED_BUILDER_BLOB:
        raise RuntimeError(
            f"construction builder drift: expected {EXPECTED_BUILDER_BLOB}, observed {observed}"
        )

    module = _load_builder(project)
    cases: list[dict[str, Any]] = []
    for declared in module.CASES:
        support_refs = [module._ref(declared, item) for item in declared["uses"]]
        distractor_refs = [
            module._ref(declared, item) for item in declared.get("distractors", [])
        ]
        passages = [
            {
                "passage_id": f"{source_id}#{passage_id}",
                "text": module._passage_text(source_id, passage_id),
                "role": role,
            }
            for role, refs in (("support", support_refs), ("distractor", distractor_refs))
            for source_id, passage_id in refs
        ]
        support_source_ids = sorted({source_id for source_id, _ in support_refs})
        all_source_ids = sorted(
            {source_id for source_id, _ in support_refs + distractor_refs}
        )
        row: dict[str, Any] = {
            "case_id": declared["case_id"],
            "claim_id": f"cg-{declared['case_id'].lower()}",
            "claim_text": declared["claim"],
            "source_id": declared["source_id"],
            "source_ids": all_source_ids,
            "support_source_ids": support_source_ids,
            "source_boundary": declared["boundary"],
            "relation": declared["relation"],
            "passages": passages,
            "n_support_passages": len(support_refs),
            "n_distractor_passages": len(distractor_refs),
            "multi_document": len(support_source_ids) > 1,
        }
        for optional in (
            "variant_group",
            "named_gaps",
            "claimed_material_is_a_named_gap",
            "absent_conjunct_term",
            "distractor_kind",
            "claim_scope_term",
            "distractor_scope_term",
        ):
            if optional in declared:
                row[optional] = declared[optional]
        cases.append(row)

    manifest = {
        "schema_version": "cal-construction-cohort-a-input-v0.1",
        "authority": "input_only_blind_execution",
        "source_builder_blob": EXPECTED_BUILDER_BLOB,
        "corpus_id": "construction-gold-v0.2-input-only",
        "n_cases": len(cases),
        "cases": cases,
    }
    if len(cases) != 33:
        raise RuntimeError(f"expected 33 construction cases, observed {len(cases)}")
    _assert_no_forbidden(manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[2]
    manifest = emit(project)
    raw = (
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    print(json.dumps({"n_cases": 33, "sha256": digest, "path": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
