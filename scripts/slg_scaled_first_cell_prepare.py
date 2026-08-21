"""Prepare the frozen Lane A SLG-01-d T2 first cell without running CAL.

The preparer verifies Cameron's approved generated artifact, inserts the one
frozen load-bearing fact after filler paragraph three, recomputes exact source
offsets, authors one C-A fixture scaffold, and invokes Evidence Bundler's
installed ``verify-intake`` and ``build-fixture-bundle`` commands. Evidence
Bundler is used read-only; every output lands under CAL's caller-supplied path.

DEV preparation only. This module performs no retrieval, entailment, verdict,
or measured CAL inference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any

import yaml

WORLD_ID = "SLG-01-d"
ATOM_ID = "SLG-01-d-a1"
FACT_ID = "d-sample-cabinet-a"
CLAIM_TEXT = "The retained sample is in cabinet A."
FACT_TEXT = CLAIM_TEXT
TITLE = "Suite B environmental and cleaning log — week of 12 May"
PASSAGE_IDS = (
    "filler-p01",
    "filler-p02",
    "filler-p03",
    FACT_ID,
    "filler-p04",
    "filler-p05",
    "filler-p06",
)

DOMAIN_GOLD_SHA256 = "6c82025c9c017bf8e2e78a499cf7f1f6df0fa672d700462f9ffb992bfec4e9a4"
CANDIDATE_RAW_SHA256 = "56d78a3817a827124156ddd0c1d6c3c3a97dbdc43e16320eb232f7d381959e6c"
CANDIDATE_RECEIPT_SHA256 = "3df12d8386de9255165459496bd68a5b1e5ad70edc082d5758a134cae207755a"
CANDIDATE_MANIFEST_SHA256 = "a1356b0430290d74b5ae5fb36b8ebb552822858a1b617c1629344f82b4bd4f9e"
WORKBENCH_HEAD = "adf394d3eb6dd5a8571e77cdf2b49e452210e2f3"
EB_HEAD = "626c494f4dcaf7dcdb732d8ecfbf66a5f9607975"
EB_VERSION = "evidence-bundler, version 0.1.0"
GENERATED_AT_UTC = "2026-07-18T00:00:00Z"


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 hex digest for one file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    """Return a ``sha256:`` digest over UTF-8 text."""
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_sha256_manifest(root: Path, manifest: Path) -> dict[str, str]:
    """Verify a two-column SHA256SUMS file without accepting path traversal."""
    observed: dict[str, str] = {}
    for line_number, raw_line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            continue
        parts = raw_line.split(maxsplit=1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]):
            raise ValueError(f"{manifest}: malformed line {line_number}")
        relative = parts[1].lstrip("*")
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError as exc:
            raise ValueError(f"{manifest}: path escapes root: {relative}") from exc
        if relative in observed:
            raise ValueError(f"{manifest}: duplicate path: {relative}")
        if not candidate.is_file():
            raise ValueError(f"{manifest}: missing file: {relative}")
        actual = sha256_file(candidate)
        if actual != parts[0]:
            raise ValueError(
                f"{manifest}: hash mismatch for {relative}: expected={parts[0]} actual={actual}"
            )
        observed[relative] = actual
    if not observed:
        raise ValueError(f"{manifest}: empty manifest")
    return observed


def split_candidate(raw: str) -> tuple[str, list[str]]:
    """Return the exact title and six non-empty body paragraphs."""
    blocks = [block.strip() for block in re.split(r"\n\s*\n", raw.strip())]
    if len(blocks) != 7:
        raise ValueError(f"candidate must contain title plus six paragraphs; got {len(blocks)}")
    title, *paragraphs = blocks
    if title != TITLE:
        raise ValueError(f"candidate title mismatch: {title!r}")
    if any(not paragraph for paragraph in paragraphs):
        raise ValueError("candidate contains an empty paragraph")
    word_count = len(re.findall(r"\b[\w’–-]+\b", "\n\n".join(paragraphs)))
    if word_count != 255:
        raise ValueError(f"candidate body word count drifted: expected=255 actual={word_count}")
    return title, paragraphs


def build_content_and_passages(
    title: str, paragraphs: list[str], fact_text: str = FACT_TEXT
) -> tuple[str, list[dict[str, Any]]]:
    """Insert the fact centrally and return content plus exact passage offsets."""
    if len(paragraphs) != 6:
        raise ValueError(f"expected six filler paragraphs, got {len(paragraphs)}")
    ordered_texts = [*paragraphs[:3], fact_text, *paragraphs[3:]]
    if len(ordered_texts) != len(PASSAGE_IDS):
        raise AssertionError("internal passage-order drift")

    header = f"# {title}"
    parts = [header, ""]
    cursor = len(header) + 2
    passages: list[dict[str, Any]] = []
    for index, (passage_id, text) in enumerate(zip(PASSAGE_IDS, ordered_texts, strict=True), 1):
        start = cursor
        end = start + len(text)
        passages.append(
            {
                "passage_id": passage_id,
                "section": title,
                "paragraph_index": index,
                "char_start": start,
                "char_end": end,
                "text_preview": text[:60],
                "used_for_claims": [ATOM_ID],
                "extraction_method": "scaffold_cited",
                "text": text,
            }
        )
        parts.extend([text, ""])
        cursor = end + 2

    content = "\n".join(parts).rstrip() + "\n"
    for passage in passages:
        excerpt = content[passage["char_start"] : passage["char_end"]]
        if excerpt != passage["text"]:
            raise ValueError(f"offset mismatch for {passage['passage_id']}")
    return content, passages


def load_and_validate_candidate(candidate_dir: Path) -> tuple[str, list[str], dict[str, Any]]:
    """Fail closed on the approved candidate's hashes and screen receipts."""
    manifest = candidate_dir / "SHA256SUMS"
    if sha256_file(manifest) != CANDIDATE_MANIFEST_SHA256:
        raise ValueError("candidate SHA256SUMS hash mismatch")
    verified = verify_sha256_manifest(candidate_dir, manifest)
    required = {
        "raw_response.txt",
        "candidate-receipt.json",
        "deterministic-screen.json",
        "p2-response.json",
    }
    if not required.issubset(verified):
        missing = sorted(required - verified)
        raise ValueError(f"candidate manifest missing required files: {missing}")

    raw_path = candidate_dir / "raw_response.txt"
    receipt_path = candidate_dir / "candidate-receipt.json"
    if sha256_file(raw_path) != CANDIDATE_RAW_SHA256:
        raise ValueError("candidate raw-response hash mismatch")
    if sha256_file(receipt_path) != CANDIDATE_RECEIPT_SHA256:
        raise ValueError("candidate receipt hash mismatch")

    title, paragraphs = split_candidate(raw_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("final_status") != "admissible_candidate_pending_cameron":
        raise ValueError("candidate receipt is not at the Cameron-approval boundary")
    if receipt.get("generator", {}).get("raw_response_sha256") != (
        "sha256:" + CANDIDATE_RAW_SHA256
    ):
        raise ValueError("candidate receipt does not bind the approved raw response")

    screen = json.loads((candidate_dir / "deterministic-screen.json").read_text(encoding="utf-8"))
    expected_screen = {
        "title_exact": True,
        "paragraph_count": 6,
        "body_word_count": 255,
        "admissible_to_independent_p2": True,
        "decision": "continue_to_p2",
    }
    for key, expected in expected_screen.items():
        if screen.get(key) != expected:
            raise ValueError(f"candidate deterministic screen drifted: {key}")
    if any(
        screen.get(key)
        for key in (
            "choice_marker_residue",
            "forbidden_subject_hits",
            "banned_outcome_or_derivation_hits",
            "exact_or_normalized_proposition_hits",
            "high_overlap_flags",
            "reasons",
        )
    ):
        raise ValueError("candidate deterministic screen contains a rejection signal")

    p2 = json.loads((candidate_dir / "p2-response.json").read_text(encoding="utf-8"))
    reviews = p2.get("reviews", [])
    expected_ids = [f"P{index:02d}" for index in range(1, 26)]
    if [review.get("id") for review in reviews] != expected_ids:
        raise ValueError("candidate P2 review does not cover P01..P25 exactly")
    if p2.get("overall") != "clean" or any(
        review.get("relation") != "unrelated" for review in reviews
    ):
        raise ValueError("candidate P2 review is not 25/25 unrelated")
    return title, paragraphs, receipt


def load_world(domain_frozen: Path) -> dict[str, Any]:
    """Load and validate the one frozen world used by this first cell."""
    if sha256_file(domain_frozen) != DOMAIN_GOLD_SHA256:
        raise ValueError("domain frozen-gold hash mismatch")
    payload = json.loads(domain_frozen.read_text(encoding="utf-8"))
    matches = [case for case in payload["frozen_cases"] if case["base_case_id"] == WORLD_ID]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {WORLD_ID} case, got {len(matches)}")
    case = matches[0]
    expected = {
        "plain_claim": CLAIM_TEXT,
        "operator": "single",
        "parent_verdict": "supported",
        "source_boundary": "bounded",
    }
    for key, value in expected.items():
        if case.get(key) != value:
            raise ValueError(f"{WORLD_ID} frozen field drifted: {key}")
    if case.get("facts") != [{"fact_id": FACT_ID, "text": FACT_TEXT}]:
        raise ValueError(f"{WORLD_ID} frozen fact drifted")
    if len(case.get("atoms", [])) != 1:
        raise ValueError(f"{WORLD_ID} must contain exactly one atom")
    atom = case["atoms"][0]
    if (atom.get("atom_id"), atom.get("claim"), atom.get("relation")) != (
        ATOM_ID,
        CLAIM_TEXT,
        "supports",
    ):
        raise ValueError(f"{WORLD_ID} frozen atom drifted")
    return case


def _dump_yaml(payload: dict[str, Any], path: Path) -> None:
    path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def _run(command: list[str], *, cwd: Path | None = None) -> str:
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or "no subprocess output"
        raise RuntimeError(f"command failed ({exc.returncode}): {command!r}\n{detail}") from exc
    return result.stdout.strip()


def verify_workbench_boundary(workbench: Path) -> dict[str, str]:
    """Bind HEAD while allowing only harness/test changes outside package source."""
    head = _run(["git", "rev-parse", "HEAD"], cwd=workbench)
    branch = _run(["git", "branch", "--show-current"], cwd=workbench)
    if head != WORKBENCH_HEAD or branch != "cal-v1-skeleton":
        raise ValueError(f"CAL workbench drifted: branch={branch} head={head}")
    package_status = _run(
        ["git", "status", "--porcelain", "--", "src/claim_audit_lab", "pyproject.toml"],
        cwd=workbench,
    )
    if package_status:
        raise ValueError(f"CAL package/config is dirty:\n{package_status}")
    return {"branch": branch, "head": head, "package_status": "clean"}


def verify_eb_boundary(eb_cli: Path) -> dict[str, str]:
    """Require the paused Evidence Bundler checkout to remain exact and clean."""
    workbench = eb_cli.resolve().parents[2]
    head = _run(["git", "rev-parse", "HEAD"], cwd=workbench)
    status = _run(["git", "status", "--porcelain"], cwd=workbench)
    version = _run([str(eb_cli), "--version"])
    if head != EB_HEAD or status:
        raise ValueError(f"Evidence Bundler boundary drifted: head={head} status={status!r}")
    if version != EB_VERSION:
        raise ValueError(f"Evidence Bundler version drifted: {version!r}")
    return {"head": head, "status": "clean", "version": version}


def author_scaffold(
    out: Path,
    case: dict[str, Any],
    title: str,
    paragraphs: list[str],
    candidate_receipt: dict[str, Any],
    eb_python: Path,
) -> tuple[str, list[dict[str, Any]]]:
    """Author one C-A fixture scaffold with all seven passages cited."""
    out.mkdir(parents=True)
    (out / "CONTRACT_VERSION").write_text("1.1.0\n", encoding="utf-8")
    source_id = "src-slg-01-d-t2"
    source_dir = out / "corpus" / source_id
    source_dir.mkdir(parents=True)
    content, passages = build_content_and_passages(title, paragraphs)
    content_path = source_dir / "content.md"
    content_path.write_text(content, encoding="utf-8")

    _dump_yaml(
        {
            "source_id": source_id,
            "schema_version": "1.0.0",
            "bibliographic": {
                "source_type": "regulatory_guidance",
                "title": title,
                "authors": ["CAL DEV synthetic fixture"],
                "publication_date": "2026-07-18",
                "pmid": None,
                "doi": None,
                "url": "https://example.test/cal/scaled-corpus/slg-01-d/t2",
                "access_date_utc": GENERATED_AT_UTC,
            },
            "trust_level": "primary",
            "content_hash": "sha256:" + sha256_file(content_path),
            "retrieval": {
                "retrieved_for": [ATOM_ID],
                "retrieval_query": CLAIM_TEXT,
                "retrieval_rank": 1,
            },
            "notes": (
                "Lane A T2 DEV fixture: one frozen fact plus six Cameron-approved "
                "relation-neutral filler passages."
            ),
        },
        source_dir / "metadata.yaml",
    )
    _dump_yaml(
        {
            "source_id": source_id,
            "schema_version": "1.0.0",
            "passages": [
                {key: value for key, value in passage.items() if key != "text"}
                for passage in passages
            ],
        },
        source_dir / "passages.yaml",
    )

    source_refs = [{"source_id": source_id, "passage_id": passage_id} for passage_id in PASSAGE_IDS]
    claims = [
        {
            "claim_id": "seed-slg-01-d-t2",
            "claim_type": "retrieval_seed",
            "claim_text": "Which frozen SLG-01-d claim does this bounded T2 evidence support?",
            "support_status": "uncertain",
            "claim_strength": 0.4,
            "extraction_fidelity": 0.4,
            "source_refs": [],
            "counterevidence_checked": False,
            "counterevidence_found": False,
            "downgraded": False,
            "downgrade_reason": None,
            "scaffold_notes": "Retrieval seed excluded from C-B claim files.",
        },
        {
            "claim_id": ATOM_ID,
            "claim_type": "extracted_claim",
            "claim_text": CLAIM_TEXT,
            "support_status": "sourced",
            "claim_strength": 0.9,
            "extraction_fidelity": 0.9,
            "source_refs": source_refs,
            "counterevidence_checked": True,
            "counterevidence_found": False,
            "downgraded": False,
            "downgrade_reason": None,
            "scaffold_notes": (
                "Frozen relation supports; all six filler passages separately screened "
                "relation-neutral. Gold remains unseen by CAL."
            ),
        },
    ]
    run_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "cal:lane-a:first-cell:slg-01-d:t2:g05"))
    _dump_yaml(
        {
            "schema_version": "1.0.0",
            "run_id": run_id,
            "generated_at_utc": GENERATED_AT_UTC,
            "claims": claims,
        },
        out / "claims.yaml",
    )

    corpus = out / "corpus"
    corpus_hash = _run(
        [
            str(eb_python),
            "-c",
            (
                "from pathlib import Path; "
                "from evidence_bundler.contracts.hashing import compute_corpus_hash; "
                f"print(compute_corpus_hash(Path({str(corpus)!r})))"
            ),
        ]
    )
    generator = candidate_receipt["generator"]
    _dump_yaml(
        {
            "run_id": run_id,
            "task_id": "cal-lane-a-first-cell-slg-01-d-t2",
            "workflow_condition": "full_scaffold",
            "timestamp_utc": GENERATED_AT_UTC,
            "scaffold": {
                "version": "scaled-corpus-v0.1",
                "prompt_template_id": "slg-t2-target-blind-scaffold",
                "prompt_template_hash": generator["prompt_sha256"],
                "config_hash": "sha256:" + CANDIDATE_RECEIPT_SHA256,
            },
            "model": {
                "model_id": generator["model"],
                "model_version": generator["model_blob_sha256"],
                "api_endpoint": "http://127.0.0.1:11434/api/generate",
                "temperature": 0.0,
                "max_tokens": 500,
            },
            "task": {
                "research_question": (
                    "Does approved T2 easy-paperwork filler preserve the SLG-01-d fact "
                    "and CAL verdict versus frozen T1?"
                ),
                "domain": "pharma_regulatory",
                "expert_checkable": True,
                "ground_truth_ref": None,
            },
            "corpus": {
                "total_sources": 1,
                "corpus_hash": corpus_hash,
                "retrieval_strategy": "synthetic_fixture",
                "retrieval_timestamp_utc": GENERATED_AT_UTC,
            },
            "intermediates_present": False,
            "run_metadata": {
                "operator": "cameron",
                "environment": "local-dev",
                "notes": ("DEV-only Lane A first cell; fact inserted after filler paragraph 3."),
            },
        },
        out / "scaffold_run.yaml",
    )
    _run(
        [
            str(eb_python),
            "-c",
            (
                "from pathlib import Path; "
                "from evidence_bundler.contracts.hashing import write_sha256sums; "
                f"write_sha256sums(Path({str(out)!r}))"
            ),
        ]
    )
    return content, passages


def tree_hashes(root: Path, *, exclude: set[Path] | None = None) -> dict[str, str]:
    """Return stable relative-path hashes for all files beneath ``root``."""
    excluded = {path.resolve() for path in (exclude or set())}
    return {
        str(path.relative_to(root)): sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.resolve() not in excluded
    }


def write_recursive_manifest(root: Path) -> None:
    """Write a recursive SHA256SUMS that excludes itself."""
    manifest = root / "SHA256SUMS"
    hashes = tree_hashes(root, exclude={manifest})
    manifest.write_text(
        "".join(f"{digest}  {relative}\n" for relative, digest in hashes.items()),
        encoding="utf-8",
    )


def prepare(
    domain_frozen: Path,
    candidate_dir: Path,
    eb_cli: Path,
    eb_python: Path,
    out: Path,
) -> dict[str, Any]:
    """Prepare one fail-closed T2 fixture bundle atomically."""
    if out.exists():
        raise FileExistsError(f"refusing to replace existing preparation: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)

    workbench = Path(__file__).resolve().parents[1]
    cal_boundary = verify_workbench_boundary(workbench)
    eb_boundary = verify_eb_boundary(eb_cli)
    case = load_world(domain_frozen)
    title, paragraphs, candidate_receipt = load_and_validate_candidate(candidate_dir)

    temp_path = Path(tempfile.mkdtemp(prefix=f".{out.name}-", dir=out.parent))
    try:
        scaffold = temp_path / "scaffold-run-t2"
        packet_root = temp_path / "packet"
        bundle = packet_root / "evidence-bundle-slg-01-d-t2"
        content, passages = author_scaffold(
            scaffold, case, title, paragraphs, candidate_receipt, eb_python
        )
        verify_output = _run([str(eb_cli), "verify-intake", str(scaffold)])
        build_output = _run(
            [str(eb_cli), "build-fixture-bundle", str(scaffold), "--output", str(bundle)]
        )

        passage_text_sha256 = {
            passage["passage_id"]: sha256_text(passage["text"]) for passage in passages
        }
        receipt: dict[str, Any] = {
            "schema_version": "cal-lane-a-first-cell-preparation-v1",
            "label": "DEV-only preparation; no CAL inference or dilution result",
            "lane": "A",
            "world_id": WORLD_ID,
            "atom_id": ATOM_ID,
            "tier": "T2",
            "difficulty": "easy",
            "genre": "pharmaceutical-paperwork",
            "inputs": {
                "domain_frozen_sha256": "sha256:" + DOMAIN_GOLD_SHA256,
                "candidate_raw_sha256": "sha256:" + CANDIDATE_RAW_SHA256,
                "candidate_receipt_sha256": "sha256:" + CANDIDATE_RECEIPT_SHA256,
                "candidate_manifest_sha256": "sha256:" + CANDIDATE_MANIFEST_SHA256,
            },
            "approval": {
                "authority": "Cameron",
                "approved_at": "2026-07-18",
                "approved_raw_sha256": "sha256:" + CANDIDATE_RAW_SHA256,
            },
            "construction": {
                "title": title,
                "filler_body_word_count": 255,
                "fact_insert_after_filler_paragraph": 3,
                "passage_order": list(PASSAGE_IDS),
                "passage_count": len(passages),
                "content_sha256": sha256_text(content),
                "passage_text_sha256": passage_text_sha256,
                "offsets": [
                    {
                        "passage_id": passage["passage_id"],
                        "char_start": passage["char_start"],
                        "char_end": passage["char_end"],
                    }
                    for passage in passages
                ],
            },
            "boundaries": {"cal": cal_boundary, "evidence_bundler": eb_boundary},
            "evidence_bundler": {
                "verify_intake_stdout": verify_output,
                "build_fixture_bundle_stdout": build_output,
            },
            "outputs": {
                "scaffold_tree": tree_hashes(scaffold),
                "packet_tree": tree_hashes(packet_root),
            },
            "measured_inference_run": False,
            "next_gate": "Cameron approval of the exact measured-run command",
        }
        (temp_path / "preparation-receipt.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        write_recursive_manifest(temp_path)
        temp_path.rename(out)
    except BaseException:
        shutil.rmtree(temp_path, ignore_errors=True)
        raise
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain-frozen", type=Path, required=True)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--eb-cli", type=Path, required=True)
    parser.add_argument("--eb-python", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = prepare(
        args.domain_frozen.resolve(),
        args.candidate_dir.resolve(),
        args.eb_cli.resolve(),
        args.eb_python.absolute(),
        args.out.resolve(),
    )
    print(
        json.dumps(
            {
                "world_id": receipt["world_id"],
                "atom_id": receipt["atom_id"],
                "passage_count": receipt["construction"]["passage_count"],
                "measured_inference_run": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
