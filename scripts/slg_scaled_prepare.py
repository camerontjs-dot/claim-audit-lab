"""Construct one admitted Lane A scaled-corpus cell into a CAL fixture packet.

Generalizes the proven single-cell preparer (slg_scaled_first_cell_prepare.py) to
the admitted Antigravity corpus: reads an admitted cell (case.json +
candidate-receipt.json + admission.json + the frozen world), inserts the one
frozen load-bearing fact at the tier's fixed insertion point, recomputes exact
source offsets, authors one C-A fixture scaffold, and invokes Evidence Bundler's
read-only verify-intake + build-fixture-bundle. Fail-closed on every boundary,
hash, screen, P2, and admission gate. DEV preparation only: no retrieval,
entailment, verdict, or measured CAL inference.

Provenance is represented HONESTLY for cloud generation: surface=antigravity,
model as reported by Antigravity, bound by the candidate's raw/receipt SHAs and
Cameron's admission record — no fabricated local model-blob hash or endpoint.

Scope: family-agnostic. Reuses the proven E4 mapping (slg_cb_author_and_bundle.py) —
one extracted_claim per atom (all support_status "sourced"; the frozen relation lives
only in scaffold_notes so CAL derives the verdict), every fact a passage. Handles all
12 SLG logic families uniformly; validated against the proven single-atom reference.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any

# Reuse the proven, security-reviewed helpers verbatim (path-safe manifest
# verification, EB subprocess wrapper, boundary checks, YAML dump, manifests).
try:
    from scripts import slg_scaled_first_cell_prepare as ref
    from scripts.slg_scaled_first_cell_prepare import (
        _dump_yaml,
        _run,
        sha256_file,
        sha256_text,
        tree_hashes,
        verify_eb_boundary,
        verify_sha256_manifest,
        write_recursive_manifest,
    )
    from scripts.slg_scaled_screen import parse_p2, validate_p2
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    import slg_scaled_first_cell_prepare as ref  # type: ignore[no-redef]
    from slg_scaled_first_cell_prepare import (  # type: ignore[no-redef]
        _dump_yaml,
        _run,
        sha256_file,
        sha256_text,
        tree_hashes,
        verify_eb_boundary,
        verify_sha256_manifest,
        write_recursive_manifest,
    )
    from slg_scaled_screen import parse_p2, validate_p2  # type: ignore[no-redef]

GREEN = "screened_candidate_pending_cameron"
GENERATED_AT_UTC = "2026-07-21T00:00:00Z"


def split_candidate(raw: str, paragraphs: int) -> tuple[str, list[str]]:
    """Return the exact title and the contracted number of non-empty paragraphs."""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", raw.strip()) if b.strip()]
    if len(blocks) != paragraphs + 1:
        raise ValueError(f"candidate must be title + {paragraphs} paragraphs; got {len(blocks)}")
    title, *paras = blocks
    if not title:
        raise ValueError("candidate title is empty")
    if any(not p for p in paras):
        raise ValueError("candidate contains an empty paragraph")
    return title, paras


def load_admitted_cell(cell: Path) -> dict[str, Any]:
    """Fail-closed load of an admitted cell across all its screening + admission gates."""
    manifest = cell / "SHA256SUMS"
    verified = verify_sha256_manifest(cell, manifest)
    required = {
        "raw_response.txt",
        "candidate-receipt.json",
        "deterministic-screen.json",
        "p2-response.json",
        "case.json",
        "admission.json",
        "generation-record.json",
    }
    if not required.issubset(verified):
        raise ValueError(
            f"cell manifest missing required files: {sorted(required - set(verified))}"
        )

    case = json.loads((cell / "case.json").read_text())
    receipt = json.loads((cell / "candidate-receipt.json").read_text())
    admission = json.loads((cell / "admission.json").read_text())
    screen = json.loads((cell / "deterministic-screen.json").read_text())

    raw_hash = "sha256:" + sha256_file(cell / "raw_response.txt")

    # Admission gate (Cameron's decision, bound to the exact raw hash — prereg §7).
    if admission.get("admitted") is not True:
        raise ValueError("cell is not admitted")
    if admission.get("raw_response_sha256") != raw_hash:
        raise ValueError("admission raw hash does not match the current filler")

    # Screening gates.
    if receipt.get("final_status") != GREEN:
        raise ValueError(
            f"candidate final_status={receipt.get('final_status')} (not admitted-green)"
        )
    if receipt.get("raw_response_sha256") != raw_hash:
        raise ValueError("candidate-receipt raw hash drift")
    if screen.get("raw_response_sha256") != raw_hash:
        raise ValueError("deterministic-screen raw hash drift")
    if screen.get("decision") != "continue_to_p2":
        raise ValueError("deterministic screen is not continue_to_p2")
    if screen.get("reasons"):
        raise ValueError(f"deterministic screen carries reasons: {screen['reasons']}")
    if screen.get("paragraph_count") != case["paragraphs"]:
        raise ValueError("screen paragraph count disagrees with case contract")
    if not (case["body_word_min"] <= screen.get("body_word_count", -1) <= case["body_word_max"]):
        raise ValueError("screen body word count outside contract band")

    # Fence-tolerant P2 parse (same parser the screen used; some judges wrap JSON in ```).
    p2_ok, p2_reason = validate_p2(parse_p2((cell / "p2-response.json").read_text()), 25)
    if not p2_ok:
        raise ValueError(f"P2 gate failed: {p2_reason}")

    # Cloud filler provenance (for honest recording; not a controlled local model).
    gr = json.loads((cell / "generation-record.json").read_text())
    if gr.get("raw_response_sha256") != raw_hash:
        raise ValueError("generation-record raw hash drift")
    for field in ("generator_surface", "generator_model", "generator_cli", "generation_mode"):
        if not gr.get(field):
            raise ValueError(f"generation-record missing {field}")
    filler_surface = gr["generator_surface"]
    filler_model = gr["generator_model"]
    filler_cli = gr["generator_cli"]
    filler_mode = gr["generation_mode"]

    title, paras = split_candidate((cell / "raw_response.txt").read_text(), case["paragraphs"])
    return {
        "case": case,
        "receipt": receipt,
        "admission": admission,
        "screen": screen,
        "title": title,
        "paragraphs": paras,
        "raw_hash": raw_hash,
        "receipt_hash": "sha256:" + sha256_file(cell / "candidate-receipt.json"),
        "manifest_hash": "sha256:" + sha256_file(manifest),
        "filler_surface": filler_surface,
        "filler_model": filler_model,
        "filler_cli": filler_cli,
        "filler_mode": filler_mode,
    }


def verify_current_workbench_boundary(workbench: Path) -> dict[str, str]:
    """Record the current commit while failing on branch or package drift."""
    head = _run(["git", "rev-parse", "HEAD"], cwd=workbench)
    branch = _run(["git", "branch", "--show-current"], cwd=workbench)
    if branch != "cal-v1-skeleton":
        raise ValueError(f"unexpected CAL workbench branch: {branch}")
    package_status = _run(
        ["git", "status", "--porcelain", "--", "src/claim_audit_lab", "pyproject.toml"],
        cwd=workbench,
    )
    if package_status:
        raise ValueError(f"CAL package/config is dirty:\n{package_status}")
    return {"branch": branch, "head": head, "package_status": "clean"}


def load_world(frozen_gold: Path, world_id: str) -> dict[str, Any]:
    """Load one frozen world and validate it is a supported logic family."""
    payload = json.loads(frozen_gold.read_text())
    matches = [c for c in payload["frozen_cases"] if c["base_case_id"] == world_id]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {world_id} case, got {len(matches)}")
    case = matches[0]
    # Family-agnostic structural validation (the E4 mapping is uniform: atoms->claims,
    # facts->passages, gold relation kept only in scaffold_notes so CAL derives the verdict).
    if not case.get("atoms"):
        raise ValueError(f"{world_id} has no atoms")
    if not case.get("facts"):
        raise ValueError(f"{world_id} has no facts")
    for a in case["atoms"]:
        if not (a.get("atom_id") and a.get("claim") and a.get("relation")):
            raise ValueError(f"{world_id} atom missing atom_id/claim/relation")
    for f in case["facts"]:
        if not (f.get("fact_id") and f.get("text")):
            raise ValueError(f"{world_id} fact missing fact_id/text")
    return case


def build_content_and_passages(
    title: str,
    paragraphs: list[str],
    facts: list[dict[str, Any]],
    atom_ids: list[str],
    insert_after: int,
    filler_prefix: str,
) -> tuple[str, list[dict[str, Any]]]:
    """Insert all frozen facts (clustered) at the fixed point; return content + char offsets.

    Every fact of the world becomes a passage (the bounded/exhaustive evidence packet stays
    contiguous); each passage is cited by all atoms, matching the proven E4 mapping + the
    first-cell dilution design (fact needle amid filler distractors)."""
    fact_texts = [f["text"] for f in facts]
    fact_ids = [f["fact_id"] for f in facts]
    ordered = [*paragraphs[:insert_after], *fact_texts, *paragraphs[insert_after:]]
    passage_ids = (
        [f"{filler_prefix}-p{i:02d}" for i in range(1, insert_after + 1)]
        + fact_ids
        + [f"{filler_prefix}-p{i:02d}" for i in range(insert_after + 1, len(paragraphs) + 1)]
    )
    header = f"# {title}" if not title.startswith("#") else title
    parts, cursor, passages = [header, ""], len(header) + 2, []
    for idx, (pid, text) in enumerate(zip(passage_ids, ordered, strict=True), 1):
        start = cursor
        end = start + len(text)
        passages.append(
            {
                "passage_id": pid,
                "section": title.lstrip("# "),
                "paragraph_index": idx,
                "char_start": start,
                "char_end": end,
                "text_preview": text[:60],
                "used_for_claims": list(atom_ids),
                "extraction_method": "scaffold_cited",
                "text": text,
            }
        )
        parts.extend([text, ""])
        cursor = end + 2
    content = "\n".join(parts).rstrip() + "\n"
    for p in passages:
        if content[p["char_start"] : p["char_end"]] != p["text"]:
            raise ValueError(f"offset mismatch for {p['passage_id']}")
    return content, passages


def author_scaffold(
    out: Path,
    loaded: dict,
    world: dict,
    eb_python: Path,
    cal_boundary: dict[str, str],
) -> tuple[str, list[dict], str]:
    """Author one family-agnostic C-A scaffold (loop atoms->claims, facts->passages).

    The gold relation of each atom is recorded only in scaffold_notes ("gold, unseen by
    CAL") — never in a machine-readable support field — so CAL must derive the verdict."""
    case = loaded["case"]
    lane, world_id, tier = case["lane"], case["world_id"], case["tier"]
    facts, atoms = world["facts"], world["atoms"]
    atom_ids = [a["atom_id"] for a in atoms]
    source_id = f"src-{world_id.lower()}-{tier.lower()}"
    filler_prefix = "filler"

    out.mkdir(parents=True)
    (out / "CONTRACT_VERSION").write_text("1.1.0\n")
    source_dir = out / "corpus" / source_id
    source_dir.mkdir(parents=True)
    content, passages = build_content_and_passages(
        loaded["title"],
        loaded["paragraphs"],
        facts,
        atom_ids,
        case["insert_after_paragraph"],
        filler_prefix,
    )
    content_path = source_dir / "content.md"
    content_path.write_text(content)

    source_type = (
        "regulatory_guidance" if lane == "domain" else "other"
    )  # EB SourceType enum; fiction => other
    _dump_yaml(
        {
            "source_id": source_id,
            "schema_version": "1.0.0",
            "bibliographic": {
                "source_type": source_type,
                "title": loaded["title"].lstrip("# "),
                "authors": ["CAL DEV synthetic fixture"],
                "publication_date": "2026-07-21",
                "pmid": None,
                "doi": None,
                "url": f"https://example.test/cal/scaled-corpus/{world_id.lower()}/{tier.lower()}",
                "access_date_utc": GENERATED_AT_UTC,
            },
            "trust_level": "primary",
            "content_hash": "sha256:" + sha256_file(content_path),
            "retrieval": {
                "retrieved_for": atom_ids,
                "retrieval_query": world["plain_claim"],
                "retrieval_rank": 1,
            },
            "notes": (
                f"Lane A {tier} DEV fixture ({lane}): {len(facts)} frozen fact(s) plus "
                f"{len(loaded['paragraphs'])} admitted relation-neutral filler passages; "
                f"logic_family={world['logic_family']}, parent_verdict={world['parent_verdict']} "
                "(gold, CAL-derived not scaffold-declared)."
            ),
        },
        source_dir / "metadata.yaml",
    )
    _dump_yaml(
        {
            "source_id": source_id,
            "schema_version": "1.0.0",
            "passages": [{k: v for k, v in p.items() if k != "text"} for p in passages],
        },
        source_dir / "passages.yaml",
    )

    source_refs = [{"source_id": source_id, "passage_id": p["passage_id"]} for p in passages]
    run_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"cal:lane-a:scaled:{world_id}:{tier}:admitted"))
    claims = [
        {
            "claim_id": f"seed-{world_id.lower()}-{tier.lower()}",
            "claim_type": "retrieval_seed",
            "claim_text": f"Which frozen {world_id} claims does this {tier} evidence bear on?",
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
    ]
    for atom in atoms:  # one extracted_claim per atom; gold relation only in notes
        claims.append(
            {
                "claim_id": atom["atom_id"],
                "claim_type": "extracted_claim",
                "claim_text": atom["claim"],
                "support_status": "sourced",
                "claim_strength": 0.9,
                "extraction_fidelity": 0.9,
                "source_refs": source_refs,
                "counterevidence_checked": True,
                "counterevidence_found": False,
                "downgraded": False,
                "downgrade_reason": None,
                "scaffold_notes": (
                    f"Frozen relation {atom['relation']} (gold, unseen by CAL); "
                    "all filler passages separately screened relation-neutral + "
                    "independently P2-cleared."
                ),
            }
        )
    _dump_yaml(
        {
            "schema_version": "1.0.0",
            "run_id": run_id,
            "generated_at_utc": GENERATED_AT_UTC,
            "claims": claims,
        },
        out / "claims.yaml",
    )

    corpus_hash = _run(
        [
            str(eb_python),
            "-c",
            (
                "from pathlib import Path; "
                "from evidence_bundler.contracts.hashing import compute_corpus_hash; "
                f"print(compute_corpus_hash(Path({str(out / 'corpus')!r})))"
            ),
        ]
    )
    # HONEST cloud provenance: no local model-blob / endpoint; SHA + admission bound.
    _dump_yaml(
        {
            "run_id": run_id,
            "task_id": f"cal-lane-a-scaled-{world_id.lower()}-{tier.lower()}",
            "workflow_condition": "full_scaffold",
            "timestamp_utc": GENERATED_AT_UTC,
            "scaffold": {
                "version": "scaled-corpus-v0.1",
                "prompt_template_id": f"slg-{tier.lower()}-exclusion-aware-freeprose",
                "prompt_template_hash": case["prompt_sha256"],
                "config_hash": loaded["receipt_hash"],
            },
            # Deterministic-authoring semantics (Cameron 2026-07-21): the model block describes
            # what actually built this scaffold — the deterministic preparer, no LLM, no sampling.
            # temperature 0.0 is literally true; max_tokens 1 is a schema-required placeholder.
            # The cloud filler LLM's real provenance is recorded in run_metadata.notes + the
            # preparation-receipt (SHA + admission bound).
            "model": {
                "model_id": "cal-deterministic-scaffold-preparer",
                "model_version": cal_boundary["head"],
                "api_endpoint": "local:deterministic-authoring",
                "temperature": 0.0,
                "max_tokens": 1,
            },
            "task": {
                "research_question": (
                    f"Does admitted {tier} {lane} filler preserve the {world_id} "
                    "fact and CAL verdict versus frozen T1?"
                ),
                "domain": "pharma_regulatory" if lane == "domain" else "everyday_narrative",
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
                "notes": (
                    "The model block describes DETERMINISTIC scaffold authoring by "
                    "slg_scaled_prepare.py (no LLM, no sampling); temperature 0.0 and "
                    "max_tokens 1 are schema-required placeholders, not a real sampling "
                    "config. FILLER PROVENANCE: prose generated by "
                    f"{loaded['filler_model']} via {loaded['filler_surface']} / "
                    f"{loaded['filler_cli']}, "
                    f"{loaded['filler_mode']} mode; exact filler bound by "
                    f"candidate_raw_sha256 {loaded['raw_hash']} + candidate_receipt_sha256 "
                    f"{loaded['receipt_hash']} + Cameron admission "
                    f"{loaded['admission']['admitted_at']}. Frozen fact inserted after "
                    f"filler paragraph {case['insert_after_paragraph']}."
                ),
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
    return content, passages, run_id


def prepare(cell: Path, frozen_gold: Path, eb_cli: Path, eb_python: Path, out: Path) -> dict:
    if out.exists():
        raise FileExistsError(f"refusing to replace existing preparation: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)

    cal_boundary = verify_current_workbench_boundary(Path(ref.__file__).resolve().parents[1])
    eb_boundary = verify_eb_boundary(eb_cli)
    loaded = load_admitted_cell(cell)
    case = loaded["case"]
    world = load_world(frozen_gold, case["world_id"])

    temp = Path(tempfile.mkdtemp(prefix=f".{out.name}-", dir=out.parent))
    try:
        scaffold = temp / f"scaffold-run-{case['tier'].lower()}"
        bundle = (
            temp / "packet" / f"evidence-bundle-{case['world_id'].lower()}-{case['tier'].lower()}"
        )
        content, passages, run_id = author_scaffold(
            scaffold, loaded, world, eb_python, cal_boundary
        )
        verify_output = _run([str(eb_cli), "verify-intake", str(scaffold)])
        build_output = _run(
            [str(eb_cli), "build-fixture-bundle", str(scaffold), "--output", str(bundle)]
        )

        fact_ids = [f["fact_id"] for f in world["facts"]]
        receipt = {
            "schema_version": "cal-lane-a-scaled-preparation-v1",
            "label": "DEV-only preparation; no CAL inference or dilution result",
            "lane": "A",
            "corpus_lane": case["lane"],
            "world_id": case["world_id"],
            "atom_ids": [a["atom_id"] for a in world["atoms"]],
            "atom_relations": {a["atom_id"]: a["relation"] for a in world["atoms"]},
            "parent_verdict_gold": world["parent_verdict"],
            "tier": case["tier"],
            "logic_family": world["logic_family"],
            "genre": case["genre"],
            "inputs": {
                "frozen_gold_sha256": "sha256:" + sha256_file(frozen_gold),
                "candidate_raw_sha256": loaded["raw_hash"],
                "candidate_receipt_sha256": loaded["receipt_hash"],
                "candidate_manifest_sha256": loaded["manifest_hash"],
            },
            "admission": {
                "authority": loaded["admission"]["admitted_by"],
                "admitted_at": loaded["admission"]["admitted_at"],
                "admitted_raw_sha256": loaded["admission"]["raw_response_sha256"],
                "governing_preregistration": loaded["admission"]["governing_preregistration"],
            },
            "construction": {
                "title": loaded["title"].lstrip("# "),
                "filler_paragraphs": len(loaded["paragraphs"]),
                "filler_body_word_count": loaded["screen"]["body_word_count"],
                "fact_insert_after_filler_paragraph": case["insert_after_paragraph"],
                "fact_ids": fact_ids,
                "passage_order": [p["passage_id"] for p in passages],
                "passage_count": len(passages),
                "content_sha256": sha256_text(content),
                "passage_text_sha256": {p["passage_id"]: sha256_text(p["text"]) for p in passages},
                "offsets": [
                    {
                        "passage_id": p["passage_id"],
                        "char_start": p["char_start"],
                        "char_end": p["char_end"],
                    }
                    for p in passages
                ],
            },
            "provenance_representation": (
                "cloud (antigravity/gemini); no local model-blob; SHA+admission bound"
            ),
            "boundaries": {"cal": cal_boundary, "evidence_bundler": eb_boundary},
            "evidence_bundler": {
                "verify_intake_stdout": verify_output,
                "build_fixture_bundle_stdout": build_output,
            },
            "outputs": {
                "scaffold_tree": tree_hashes(scaffold),
                "packet_tree": tree_hashes(temp / "packet"),
            },
            "measured_inference_run": False,
            "next_gate": "Cameron approval of the exact measured-run command",
        }
        (temp / "preparation-receipt.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        )
        write_recursive_manifest(temp)
        temp.rename(out)
    except BaseException:
        shutil.rmtree(temp, ignore_errors=True)
        raise
    return receipt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cell", type=Path, required=True)
    ap.add_argument("--frozen-gold", type=Path, required=True)
    ap.add_argument("--eb-cli", type=Path, required=True)
    ap.add_argument("--eb-python", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    receipt = prepare(
        args.cell.resolve(),
        args.frozen_gold.resolve(),
        args.eb_cli.resolve(),
        args.eb_python.absolute(),
        args.out.resolve(),
    )
    print(
        json.dumps(
            {
                "world_id": receipt["world_id"],
                "tier": receipt["tier"],
                "logic_family": receipt["logic_family"],
                "passage_count": receipt["construction"]["passage_count"],
                "measured_inference_run": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
