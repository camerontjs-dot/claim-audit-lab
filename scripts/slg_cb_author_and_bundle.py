"""E4 Unit 4 step 1: author C-A scaffold runs from the frozen SLG artifacts and bundle them.

Authors one contract-conformant C-A scaffold-run directory per lane (plain /
domain) — one corpus source per world, one scaffold-cited passage per frozen
fact, one extracted claim per frozen atom citing all of its world's facts —
then drives the PAUSED Evidence Bundler strictly read-only through its own
installed venv CLI: ``verify-intake`` then ``build-fixture-bundle`` (the
no-retrieval fixture writer). EB's workbench is never edited; its hashing
helpers are imported inside its venv only to compute the corpus hash and
SHA256SUMS for the authored input. DEV evidence only, never a gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import uuid
from pathlib import Path
from typing import Any

import yaml

_EB_VENV = Path(__file__).resolve().parents[3] / "evidence-bundler" / "workbench" / ".venv" / "bin"
_TS = "2026-07-16T00:00:00Z"


def _dump(payload: dict[str, Any], path: Path) -> None:
    path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def author_scaffold_run(case: dict[str, Any], lane: str, out: Path) -> None:
    """Write one C-A run per frozen world so its bounded source_boundary holds:
    a single lane-wide bundle would let CAL retrieve across worlds (e.g. the
    SLG-02 contradiction against the SLG-01 claim), which the frozen contract
    forbids. One world -> one run -> one sealed bundle, PILOT-style."""
    out.mkdir(parents=True, exist_ok=True)
    (out / "CONTRACT_VERSION").write_text("1.1.0\n", encoding="utf-8")
    case_id = case["base_case_id"]
    run_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"slg-cb-replay:{lane}:{case_id}"))

    claims: list[dict[str, Any]] = [
        {
            "claim_id": f"seed-{case_id.lower()}",
            "claim_type": "retrieval_seed",
            "claim_text": "Which Simple Logic Gold claims does the bounded evidence support?",
            "support_status": "uncertain",
            "claim_strength": 0.4,
            "extraction_fidelity": 0.4,
            "source_refs": [],
            "counterevidence_checked": False,
            "counterevidence_found": False,
            "downgraded": False,
            "downgrade_reason": None,
            "scaffold_notes": "Retrieval seed excluded from C-B claim files.",
        }
    ]
    corpus = out / "corpus"
    if True:
        source_id = "src-" + case["base_case_id"].lower()
        src_dir = corpus / source_id
        src_dir.mkdir(parents=True, exist_ok=True)
        title = f"Simple Logic Gold {case['base_case_id']} bounded facts"
        paragraphs = [f"# {title}", ""]
        spans: list[tuple[str, int, int, str]] = []
        cursor = len(paragraphs[0]) + 2
        for fact in case["facts"]:
            text = fact["text"]
            spans.append((fact["fact_id"], cursor, cursor + len(text), text))
            paragraphs.append(text)
            paragraphs.append("")
            cursor += len(text) + 2
        content = "\n".join(paragraphs).rstrip() + "\n"
        (src_dir / "content.md").write_text(content, encoding="utf-8")
        for fact_id, start, end, text in spans:
            if content[start:end] != text:
                raise ValueError(f"{source_id}/{fact_id}: char offsets do not match content")
        atom_ids = [atom["atom_id"] for atom in case["atoms"]]
        _dump(
            {
                "source_id": source_id,
                "schema_version": "1.0.0",
                "bibliographic": {
                    "source_type": "regulatory_guidance",
                    "title": title,
                    "authors": ["Simple Logic Gold frozen fixture"],
                    "publication_date": "2026-07-15",
                    "pmid": None,
                    "doi": None,
                    "url": f"https://example.test/slg/{lane}/{source_id}",
                    "access_date_utc": _TS,
                },
                "trust_level": "primary",
                "content_hash": _sha256_file(src_dir / "content.md"),
                "retrieval": {
                    "retrieved_for": atom_ids,
                    "retrieval_query": case["plain_claim"],
                    "retrieval_rank": 1,
                },
                "notes": f"By-construction {lane}-lane world; boundary: {case['source_boundary']}.",
            },
            src_dir / "metadata.yaml",
        )
        _dump(
            {
                "source_id": source_id,
                "schema_version": "1.0.0",
                "passages": [
                    {
                        "passage_id": fact_id,
                        "section": title,
                        "paragraph_index": index + 1,
                        "char_start": start,
                        "char_end": end,
                        "text_preview": text[:60],
                        "used_for_claims": atom_ids,
                        "extraction_method": "scaffold_cited",
                    }
                    for index, (fact_id, start, end, text) in enumerate(spans)
                ],
            },
            src_dir / "passages.yaml",
        )
        for atom in case["atoms"]:
            claims.append(
                {
                    "claim_id": atom["atom_id"],
                    "claim_type": "extracted_claim",
                    "claim_text": atom["claim"],
                    "support_status": "sourced",
                    "claim_strength": 0.9,
                    "extraction_fidelity": 0.9,
                    "source_refs": [
                        {"source_id": source_id, "passage_id": fact["fact_id"]}
                        for fact in case["facts"]
                    ],
                    "counterevidence_checked": True,
                    "counterevidence_found": False,
                    "downgraded": False,
                    "downgrade_reason": None,
                    "scaffold_notes": f"Frozen relation {atom['relation']} (gold, unseen by CAL).",
                }
            )

    _dump(
        {"schema_version": "1.0.0", "run_id": run_id, "generated_at_utc": _TS, "claims": claims},
        out / "claims.yaml",
    )
    corpus_hash = _eb_python(
        "from pathlib import Path; from evidence_bundler.contracts.hashing import "
        f"compute_corpus_hash; print(compute_corpus_hash(Path({str(corpus)!r})))"
    )
    _dump(
        {
            "run_id": run_id,
            "task_id": f"slg-cb-replay-{lane}-{case_id.lower()}",
            "workflow_condition": "full_scaffold",
            "timestamp_utc": _TS,
            "scaffold": {
                "version": "0.0.0",
                "prompt_template_id": "simple-logic-gold-by-construction",
                "prompt_template_hash": "sha256:" + "0" * 63 + "1",
                "config_hash": "sha256:" + "0" * 63 + "2",
            },
            "model": {
                "model_id": "none",
                "model_version": "by-construction",
                "api_endpoint": "https://example.test/none",
                "temperature": 0.0,
                "max_tokens": 1,
            },
            "task": {
                "research_question": (
                    "Do the bounded Simple Logic Gold facts support the frozen claims?"
                ),
                "domain": "pharma_regulatory",
                "expert_checkable": True,
                "ground_truth_ref": None,
            },
            "corpus": {
                "total_sources": 1,
                "corpus_hash": corpus_hash,
                "retrieval_strategy": "synthetic_fixture",
                "retrieval_timestamp_utc": _TS,
            },
            "intermediates_present": False,
            "run_metadata": {
                "operator": "cameron",
                "environment": "local-dev",
                "notes": f"E4 Unit 4 {lane}/{case_id} authored per frozen source boundary.",
            },
        },
        out / "scaffold_run.yaml",
    )
    _eb_python(
        "from pathlib import Path; from evidence_bundler.contracts.hashing import "
        f"write_sha256sums; write_sha256sums(Path({str(out)!r}))"
    )


def _eb_python(code: str) -> str:
    result = subprocess.run(
        [str(_EB_VENV / "python"), "-c", code], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def _eb_cli(*args: str) -> str:
    result = subprocess.run(
        [str(_EB_VENV / "evidence-bundler"), *args], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plain-frozen", type=Path, required=True)
    parser.add_argument("--domain-frozen", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    receipts: dict[str, Any] = {}
    for lane, frozen_path in (("plain", args.plain_frozen), ("domain", args.domain_frozen)):
        frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
        packet_dir = args.out / "packets" / lane
        packet_dir.mkdir(parents=True, exist_ok=True)
        lane_receipts = []
        for case in frozen["frozen_cases"]:
            case_slug = case["base_case_id"].lower()
            run_dir = args.out / "scaffold-runs" / lane / case_slug
            bundle_dir = packet_dir / f"evidence-bundle-{case_slug}"
            author_scaffold_run(case, lane, run_dir)
            intake = _eb_cli("verify-intake", str(run_dir))
            build = _eb_cli("build-fixture-bundle", str(run_dir), "--output", str(bundle_dir))
            lane_receipts.append(
                {"case": case["base_case_id"], "verify_intake": intake, "build": build}
            )
        receipts[lane] = {
            "bundles": sorted(p.name for p in packet_dir.iterdir() if p.is_dir()),
            "cases": lane_receipts,
            "frozen_source": str(frozen_path),
            "frozen_sha256": _sha256_file(frozen_path),
        }
    (args.out / "authoring-receipt.json").write_text(
        json.dumps(receipts, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({lane: r["bundles"] for lane, r in receipts.items()}, sort_keys=True))


if __name__ == "__main__":
    main()
