"""Fixture-writer successor to the preserved v4 controlled-B failure.

V4 used the pinned retrieval writer on heading-less Markdown. Evidence Bundler's
own model permitted the resulting ``section: null`` while the frozen Apparatus
Contract-B validator requires a string. That cross-repository mismatch is kept
as evidence in the v4 run.

This successor changes only controlled-fixture construction. It uses the pinned
Evidence Bundler fixture writer with explicit scaffold passage sections and
source references, producing exact semantic passage text while remaining a
validator-checked Contract B 1.2.0 object. No CAL semantic or authority rule is
changed.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import yaml

import run_integration as base
import run_integration_v4 as predecessor


def _write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _make_controlled_scaffold_fixture_writer_ready(root: Path) -> None:
    from evidence_bundler.contracts.hashing import compute_corpus_hash, write_sha256sums

    predecessor._build_controlled_scaffold(root)

    claims_path = root / "claims.yaml"
    claims_doc = yaml.safe_load(claims_path.read_text(encoding="utf-8"))
    by_claim = {row["claim_id"]: row for row in claims_doc["claims"]}

    for family, _text in predecessor._CONTROLLED_ROWS:
        claim_id = f"clm-{family}"
        source_id = f"src-{family}"
        passage_id = f"pass-{family}"
        by_claim[claim_id]["source_refs"] = [
            {"source_id": source_id, "passage_id": passage_id}
        ]
        passages_path = root / "corpus" / source_id / "passages.yaml"
        passages_doc = yaml.safe_load(passages_path.read_text(encoding="utf-8"))
        passage = passages_doc["passages"][0]
        passage["section"] = f"Controlled {family}"
        passage["used_for_claims"] = [claim_id]
        _write_yaml(passages_path, passages_doc)

    _write_yaml(claims_path, claims_doc)
    scaffold_path = root / "scaffold_run.yaml"
    scaffold = yaml.safe_load(scaffold_path.read_text(encoding="utf-8"))
    scaffold["corpus"]["corpus_hash"] = compute_corpus_hash(root / "corpus")
    _write_yaml(scaffold_path, scaffold)
    write_sha256sums(root)


def _build_extended_corpus(*, eb_root: Path, apparatus_b: Path, out: Path) -> dict[str, Path]:
    from claim_audit_lab.contracts.factual_context import load_contract_b_intake
    from evidence_bundler.contracts.factual_context import (
        ContractBFactualContext,
        attach_factual_context,
    )
    from evidence_bundler.contracts.writer import build_fixture_bundle, validate_bundle_tree

    result = base._build_corpus(eb_root=eb_root, apparatus_b=apparatus_b, out=out)

    scaffold = out.parent / "controlled-ca-semantic-surfaces-fixture-writer"
    _make_controlled_scaffold_fixture_writer_ready(scaffold)
    controlled = out / "controlled-semantic-absent"
    build_fixture_bundle(scaffold, controlled)
    producer_errors = validate_bundle_tree(controlled)
    if producer_errors:
        raise AssertionError(f"Evidence Bundler rejected controlled fixture B corpus: {producer_errors}")
    if (controlled / "CONTRACT_VERSION").read_text(encoding="utf-8").strip() != "1.2.0":
        raise AssertionError("fixture writer did not generate Contract B 1.2.0")
    base._verify_contract_b(apparatus_b, controlled)
    load_contract_b_intake(controlled)
    result["controlled-semantic-absent"] = controlled

    for decision, suffix in (("accepted", "admitted"), ("rejected", "rejected")):
        variant = out / f"controlled-semantic-{suffix}"
        shutil.copytree(controlled, variant)
        extension = ContractBFactualContext.model_validate(
            predecessor._extension_for_bundle(controlled, decision=decision)
        )
        attach_factual_context(variant, extension)
        producer_errors = validate_bundle_tree(variant)
        if producer_errors:
            raise AssertionError(
                f"Evidence Bundler rejected controlled {suffix} fixture B corpus: {producer_errors}"
            )
        base._verify_contract_b(apparatus_b, variant)
        intake = load_contract_b_intake(variant)
        if intake.extension_state != "present" or intake.semantic_context is None:
            raise AssertionError(f"CAL did not expose controlled {suffix} semantic context")
        result[f"controlled-semantic-{suffix}"] = variant
    return result


def main() -> int:
    predecessor._build_extended_corpus = _build_extended_corpus
    return predecessor.main()


if __name__ == "__main__":
    raise SystemExit(main())
