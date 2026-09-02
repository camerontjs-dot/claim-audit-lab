"""Controlled-valid-B coverage successor for the B -> CAL -> C shadow run.

The hardened v3 run established that the unchanged candidate can traverse the
frozen B/C boundary, but its real production-acceptance corpus did not contain a
positive RC7F measurement surface. This successor does not add semantic
warrant. It adds controlled C-A source text, builds exact valid Contract B 1.2.0
objects through the pinned Evidence Bundler production writer, and tests three
B states:

* factual-context extension absent;
* all controlled passages admitted by promoted B review history;
* all controlled passages rejected, yielding no admitted semantic text.

The positive surfaces exercise CLAIMED -> insufficient_authority -> noncausal
Contract-C projection end to end. The rejected variant exercises exclusion/no
admitted semantic evidence without fabricating a semantic truth label.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

import run_integration as base
import run_integration_v2 as predecessor
from shadow_candidate import canonical_bytes

_CONTROLLED_ROWS = (
    (
        "comparison",
        "North Plant exceeded South Plant by 12 units.",
    ),
    (
        "event-ordering",
        "Alice reviewed Batch One before Bob signed Batch Two.",
    ),
    (
        "permission-exception",
        "Only Approved Reviewers may release records, except External Auditors.",
    ),
    (
        "permission-temporal",
        "Only Approved Reviewers may release records after 2026-01-15.",
    ),
    (
        "embedded-comparison",
        "The memo reports that North Plant exceeded South Plant by 12 units.",
    ),
)
_EXPECTED_CLAIMED_FAMILIES = {"comparison", "event_ordering", "permission_composition"}


def _load_registered_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def _write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(value, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _build_controlled_scaffold(root: Path) -> None:
    from evidence_bundler.contracts.hashing import (
        compute_corpus_hash,
        hash_file,
        hash_text,
        write_sha256sums,
    )

    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    (root / "CONTRACT_VERSION").write_text("1.0.0\n", encoding="utf-8")

    run_id = "shadow-controlled-semantic-surfaces-v1"
    claims: list[dict[str, Any]] = []
    for rank, (family, text) in enumerate(_CONTROLLED_ROWS, start=1):
        claim_id = f"clm-{family}"
        source_id = f"src-{family}"
        passage_id = f"pass-{family}"
        source_dir = root / "corpus" / source_id
        source_dir.mkdir(parents=True)
        content_path = source_dir / "content.md"
        content_path.write_text(text + "\n", encoding="utf-8")

        _write_yaml(
            source_dir / "metadata.yaml",
            {
                "source_id": source_id,
                "schema_version": "1.0.0",
                "bibliographic": {
                    "source_type": "other",
                    "title": f"Controlled shadow semantic surface: {family}",
                    "authors": ["CAL shadow integration fixture"],
                    "publication_date": "2026-09-02",
                    "pmid": None,
                    "doi": None,
                    "url": f"https://example.test/cal-shadow/{family}",
                    "access_date_utc": "2026-09-02T13:00:00Z",
                },
                "trust_level": "background",
                "content_hash": hash_file(content_path),
                "retrieval": {
                    "retrieved_for": [claim_id],
                    "retrieval_query": text,
                    "retrieval_rank": rank,
                },
                "notes": (
                    "Controlled lexical surface only. This fixture does not assert "
                    "semantic truth or CAL warrant."
                ),
            },
        )
        _write_yaml(
            source_dir / "passages.yaml",
            {
                "source_id": source_id,
                "schema_version": "1.0.0",
                "passages": [
                    {
                        "passage_id": passage_id,
                        "section": f"Controlled {family}",
                        "paragraph_index": 0,
                        "char_start": 0,
                        "char_end": len(text),
                        "text_preview": text,
                        "used_for_claims": [],
                        "extraction_method": "auto_retrieved",
                    }
                ],
            },
        )
        claims.append(
            {
                "claim_id": claim_id,
                "claim_type": "extracted_claim",
                "claim_text": text,
                "support_status": "uncertain",
                "claim_strength": 0.5,
                "extraction_fidelity": 1.0,
                "source_refs": [],
                "counterevidence_checked": False,
                "counterevidence_found": False,
                "downgraded": False,
                "downgrade_reason": None,
                "scaffold_notes": (
                    "Controlled retrieval target; no upstream semantic support label is asserted."
                ),
            }
        )

    _write_yaml(
        root / "claims.yaml",
        {
            "schema_version": "1.0.0",
            "run_id": run_id,
            "generated_at_utc": "2026-09-02T13:00:00Z",
            "claims": claims,
        },
    )
    corpus_hash = compute_corpus_hash(root / "corpus")
    _write_yaml(
        root / "scaffold_run.yaml",
        {
            "run_id": run_id,
            "task_id": "cal-shadow-controlled-semantic-surfaces-v1",
            "workflow_condition": "full_scaffold",
            "timestamp_utc": "2026-09-02T13:00:00Z",
            "scaffold": {
                "version": "controlled-research-fixture-v1",
                "prompt_template_id": "cal-shadow-controlled-surfaces",
                "prompt_template_hash": hash_text("cal-shadow-controlled-surfaces"),
                "config_hash": hash_text("cal-shadow-controlled-surfaces-config-v1"),
            },
            "model": {
                "model_id": "controlled-fixture",
                "model_version": "2026-09-02",
                "api_endpoint": "local-fixture",
                "temperature": 0.0,
                "max_tokens": 1024,
            },
            "task": {
                "research_question": (
                    "Can bounded semantic measurements remain non-authoritative across valid "
                    "Contract B 1.2.0 intake and Contract C 1.0.0 projection?"
                ),
                "domain": "cal_shadow_integration",
                "expert_checkable": False,
                "ground_truth_ref": None,
            },
            "corpus": {
                "total_sources": len(_CONTROLLED_ROWS),
                "corpus_hash": corpus_hash,
                "retrieval_strategy": "controlled_bm25_fixture",
                "retrieval_timestamp_utc": "2026-09-02T13:00:00Z",
            },
            "intermediates_present": False,
            "run_metadata": {
                "operator": "cal-shadow-integration",
                "environment": "github-actions",
                "notes": (
                    "Controlled lexical surfaces. No semantic truth or authority is encoded."
                ),
            },
        },
    )
    write_sha256sums(root)


def _extension_for_bundle(bundle_dir: Path, *, decision: str) -> dict[str, Any]:
    if decision not in {"accepted", "rejected"}:
        raise ValueError(decision)
    claims: list[dict[str, Any]] = []
    history: list[dict[str, Any]] = []
    counts: list[dict[str, Any]] = []
    aperture: list[dict[str, Any]] = []
    for claim_path in sorted((bundle_dir / "claims").glob("*.yaml")):
        row = yaml.safe_load(claim_path.read_text(encoding="utf-8"))
        claim_id = str(row["claim_id"])
        passage_ids: list[str] = []
        for field in ("evidence_passages", "counterevidence_passages"):
            for passage in row.get(field, []):
                passage_id = passage.get("passage_id")
                if isinstance(passage_id, str) and passage_id not in passage_ids:
                    passage_ids.append(passage_id)
        if not passage_ids:
            raise AssertionError(f"controlled B claim has no nominated passage: {claim_id}")
        claims.append(
            {
                "claim_id": claim_id,
                "origin": {"state": "known", "value": {"surface": "controlled-fixture"}},
                "atomicity": {"state": "unknown", "value": None},
            }
        )
        for index, passage_id in enumerate(passage_ids, start=1):
            history.append(
                {
                    "link_id": f"history-{decision}-{claim_id}-{index}",
                    "claim_id": claim_id,
                    "passage_id": passage_id,
                    "nomination": {
                        "method": "bm25",
                        "rank": index,
                        "variant": "controlled-shadow-v1",
                    },
                    "review": {
                        "decision": decision,
                        "reviewer": "controlled-shadow-fixture",
                    },
                }
            )
        counts.append(
            {
                "claim_id": claim_id,
                "candidate": len(passage_ids),
                "reviewed": len(passage_ids),
                "admitted": len(passage_ids) if decision == "accepted" else 0,
            }
        )
        aperture.append(
            {
                "claim_id": claim_id,
                "search_scope": {"retrieval_method": "bm25", "top_k": 1},
                "outcome": {"state": "unknown", "value": None},
                "limitations": [
                    "Controlled fixture does not assert proposition-specific completeness."
                ],
            }
        )
    return {
        "schema": "contract-b-factual-context-v1",
        "history_complete": True,
        "claims": claims,
        "sources": [],
        "passages": [],
        "history": history,
        "history_count_checks": counts,
        "aperture": aperture,
    }


def _build_extended_corpus(*, eb_root: Path, apparatus_b: Path, out: Path) -> dict[str, Path]:
    from claim_audit_lab.contracts.factual_context import load_contract_b_intake
    from evidence_bundler.contracts.factual_context import (
        ContractBFactualContext,
        attach_factual_context,
    )
    from evidence_bundler.contracts.writer import build_retrieval_bundle, validate_bundle_tree
    from evidence_bundler.models.retrieval import RetrievalConfig

    result = base._build_corpus(eb_root=eb_root, apparatus_b=apparatus_b, out=out)

    scaffold = out.parent / "controlled-ca-semantic-surfaces"
    _build_controlled_scaffold(scaffold)
    controlled = out / "controlled-semantic-absent"
    build_retrieval_bundle(
        scaffold,
        controlled,
        config=RetrievalConfig(retrieval_method="bm25", top_k=1, lexical_score_floor=0.0),
    )
    errors = validate_bundle_tree(controlled)
    if errors:
        raise AssertionError(f"Evidence Bundler rejected controlled B corpus: {errors}")
    base._verify_contract_b(apparatus_b, controlled)
    load_contract_b_intake(controlled)
    result["controlled-semantic-absent"] = controlled

    for decision, suffix in (("accepted", "admitted"), ("rejected", "rejected")):
        variant = out / f"controlled-semantic-{suffix}"
        shutil.copytree(controlled, variant)
        extension = ContractBFactualContext.model_validate(
            _extension_for_bundle(controlled, decision=decision)
        )
        attach_factual_context(variant, extension)
        errors = validate_bundle_tree(variant)
        if errors:
            raise AssertionError(f"Evidence Bundler rejected controlled {suffix} B corpus: {errors}")
        base._verify_contract_b(apparatus_b, variant)
        intake = load_contract_b_intake(variant)
        if intake.extension_state != "present" or intake.semantic_context is None:
            raise AssertionError(f"CAL did not expose controlled {suffix} semantic context")
        result[f"controlled-semantic-{suffix}"] = variant
    return result


def _claimed_families(internal_path: Path) -> set[str]:
    internal = json.loads(internal_path.read_text(encoding="utf-8"))
    families: set[str] = set()
    for record in internal.values():
        for obs in record["semantic_measurements"]:
            measurement = obs.get("measurement") or {}
            if measurement.get("status") != "CLAIMED":
                continue
            if obs["authority"] != {
                "state": "insufficient_authority",
                "reason": "measurement_proposal_has_no_established_warrant_receipt",
                "may_strengthen_conclusion": False,
            }:
                raise AssertionError("CLAIMED measurement did not remain insufficient_authority")
            families.add(obs["family"])
    return families


def _postcheck_and_extend_receipt(out: Path) -> None:
    receipt_path = out / "RUN-RECEIPT.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    cases = {row["case"]: row for row in receipt["cases"]}
    required_cases = {
        "controlled-semantic-absent",
        "controlled-semantic-admitted",
        "controlled-semantic-rejected",
    }
    missing = required_cases - set(cases)
    if missing:
        raise AssertionError(f"controlled B cases missing from receipt: {sorted(missing)}")

    family_evidence: dict[str, list[str]] = {}
    for case_name in ("controlled-semantic-absent", "controlled-semantic-admitted"):
        case = cases[case_name]
        if case["contract_b"]["frozen_validator"] != "PASS":
            raise AssertionError(f"controlled B validator did not pass: {case_name}")
        if case["shadow_contract_c"]["frozen_validator"] != "PASS":
            raise AssertionError(f"controlled shadow C validator did not pass: {case_name}")
        if not case["candidate"]["all_measurements_non_authoritative"]:
            raise AssertionError(f"controlled measurements acquired authority: {case_name}")
        families = _claimed_families(out / "cases" / case_name / "candidate-internal.json")
        if not _EXPECTED_CLAIMED_FAMILIES <= families:
            raise AssertionError(
                f"controlled B did not exercise every bounded positive family in {case_name}: "
                f"{sorted(families)}"
            )
        family_evidence[case_name] = sorted(families)

    rejected = cases["controlled-semantic-rejected"]
    if rejected["candidate"]["selected_passage_count"] != 0:
        raise AssertionError("all-rejected B semantic context still supplied measurement text")
    if rejected["candidate"]["excluded_passage_count"] == 0:
        raise AssertionError("all-rejected B semantic context did not preserve exclusion")
    if rejected["candidate"]["proposal_count"] != 0:
        raise AssertionError("proposal emitted despite zero admitted semantic passages")

    receipt["controlled_valid_contract_b_evidence"] = {
        "fixture_source": "controlled C-A lexical surfaces built through pinned Evidence Bundler",
        "semantic_truth_encoded": False,
        "positive_claimed_families": family_evidence,
        "all_claimed_measurements_remained_insufficient_authority": True,
        "all_rejected_variant_selected_passage_count": 0,
        "all_rejected_variant_excluded_passage_count": rejected["candidate"][
            "excluded_passage_count"
        ],
        "all_rejected_variant_proposal_count": 0,
    }
    receipt["coverage"]["controlled_valid_contract_b_cases"] = sorted(required_cases)
    receipt["coverage"]["represented"].extend(
        [
            "positive comparison measurement proposal on valid Contract B",
            "positive explicit event-ordering measurement proposal on valid Contract B",
            "positive permission/exception/temporal measurement proposal on valid Contract B",
            "promoted factual-context all-admitted measurement selection",
            "promoted factual-context all-rejected/no-admitted measurement selection",
            "adversarial embedded comparative cue retained as non-authoritative measurement state",
        ]
    )
    receipt["terminal_disposition"] = (
        "SHADOW_BOUNDARY_OPERABLE_FAIL_CLOSED_ON_VALID_B_WITH_POSITIVE_PROPOSALS; "
        "AUTHORITY_MACHINERY_BLOCKS_STRONGER_CONCLUSION"
    )
    receipt_path.write_bytes(canonical_bytes(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))


def _arg_path(flag: str) -> Path:
    try:
        index = sys.argv.index(flag)
    except ValueError as exc:
        raise RuntimeError(f"missing required argument {flag}") from exc
    return Path(sys.argv[index + 1]).resolve()


def main() -> int:
    predecessor._load_module = _load_registered_module
    predecessor._build_corpus = _build_extended_corpus
    out = _arg_path("--out")
    code = predecessor.main()
    if code != 0:
        return code
    _postcheck_and_extend_receipt(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
