# ruff: noqa: E501 -- self-contained HTML/JavaScript is intentionally line-oriented.

"""Derive Simple Logic Gold DEV targets from explicit draft-world facts.

This construction tool deliberately has no CAL, model, or Evidence Bundler inputs.
It turns an approved-world candidate manifest into a deterministic, reviewable
gold derivative.  Until Cameron approves a versioned manifest, every output is
only a draft construction receipt.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

MANIFEST_SCHEMA = "simple-logic-gold-worlds-v0.1"
DERIVATION_SCHEMA = "simple-logic-gold-derived-v0.1"
FREEZE_SCHEMA = "simple-logic-gold-frozen-dev-v0.1"
ALLOWED_BOUNDARIES = {"bounded", "exhaustive", "named_missing_material"}
ALLOWED_OPERATORS = {"single", "all_of"}
ATOM_RELATIONS = {"supports", "refutes", "insufficient", "retrieval_gap"}
PARENT_VERDICTS = {
    "supported",
    "contradicted",
    "not_checkable",
    "partially_supported",
    "pending",
}


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_text(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _sha256_bytes(value: bytes) -> str:
    """Hash preserved bytes without text decoding or newline translation."""
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"could not load Simple Logic Gold manifest {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("Simple Logic Gold manifest must be a mapping")
    base_manifest = raw.pop("base_manifest", None)
    overrides = raw.pop("world_overrides", None)
    if base_manifest is None:
        if overrides is not None:
            raise ValueError("world_overrides requires base_manifest")
        manifest = raw
    else:
        if not isinstance(base_manifest, str) or not base_manifest:
            raise ValueError("base_manifest must be a non-empty relative path")
        base_path = Path(base_manifest)
        if base_path.is_absolute():
            raise ValueError("base_manifest must be relative")
        base_path = path.parent / base_path
        base = load_manifest(base_path)
        manifest = copy.deepcopy(base)
        manifest.update(raw)
        if not isinstance(overrides, dict):
            raise ValueError("world_overrides must be a mapping when base_manifest is used")
        by_id = {world["base_case_id"]: world for world in manifest["worlds"]}
        for case_id, override in overrides.items():
            if (
                not isinstance(case_id, str)
                or case_id not in by_id
                or not isinstance(override, dict)
            ):
                raise ValueError("world_overrides must target known case IDs with mappings")
            by_id[case_id] = _deep_merge(by_id[case_id], override)
        manifest["worlds"] = [by_id[world["base_case_id"]] for world in manifest["worlds"]]
    validate_manifest(manifest)
    return manifest


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        raise ValueError(f"schema_version must be {MANIFEST_SCHEMA}")
    if manifest.get("approval_status") != "draft_pending_cameron_approval":
        raise ValueError("manifest must remain draft_pending_cameron_approval before freeze")
    if not isinstance(manifest.get("version"), str) or not manifest["version"].strip():
        raise ValueError("manifest version must be a non-empty string")
    worlds = manifest.get("worlds")
    if not isinstance(worlds, list) or len(worlds) != 12:
        raise ValueError("manifest must contain exactly 12 draft worlds")
    world_ids = [world.get("base_case_id") for world in worlds if isinstance(world, dict)]
    if (
        len(world_ids) != 12
        or len(set(world_ids)) != 12
        or not all(isinstance(item, str) and item for item in world_ids)
    ):
        raise ValueError("base_case_id values must be unique non-empty strings")

    for world in worlds:
        if not isinstance(world, dict):
            raise ValueError("each world must be a mapping")
        _validate_world(world)


def _validate_world(world: dict[str, Any]) -> None:
    case_id = world["base_case_id"]
    if not isinstance(world.get("logic_family"), str) or not world["logic_family"]:
        raise ValueError(f"{case_id}: logic_family is required")
    if world.get("source_boundary") not in ALLOWED_BOUNDARIES:
        raise ValueError(f"{case_id}: source_boundary is invalid")
    if not isinstance(world.get("source_boundary_note"), str) or not world["source_boundary_note"]:
        raise ValueError(f"{case_id}: source_boundary_note is required")
    if not isinstance(world.get("plain_claim"), str) or not world["plain_claim"].strip():
        raise ValueError(f"{case_id}: plain_claim is required")
    facts = world.get("facts")
    if not isinstance(facts, list) or not facts:
        raise ValueError(f"{case_id}: facts are required")
    if any(not isinstance(fact, dict) for fact in facts):
        raise ValueError(f"{case_id}: facts must be mappings")
    fact_ids = [fact.get("fact_id") for fact in facts]
    if len(set(fact_ids)) != len(fact_ids) or not all(
        isinstance(item, str) and item for item in fact_ids
    ):
        raise ValueError(f"{case_id}: fact_id values must be unique non-empty strings")
    if any(not isinstance(fact.get("text"), str) or not fact["text"] for fact in facts):
        raise ValueError(f"{case_id}: each fact needs explicit text")
    if world.get("operator") not in ALLOWED_OPERATORS:
        raise ValueError(f"{case_id}: operator must be single or all_of")
    parent_rule_ids = world.get("parent_rule_fact_ids", [])
    if not isinstance(parent_rule_ids, list) or not all(
        isinstance(item, str) and item for item in parent_rule_ids
    ):
        raise ValueError(f"{case_id}: parent_rule_fact_ids must be non-empty strings")
    unknown_parent_rules = set(parent_rule_ids) - set(fact_ids)
    if unknown_parent_rules:
        raise ValueError(
            f"{case_id}: parent rule references unknown facts: {sorted(unknown_parent_rules)}"
        )
    atoms = world.get("atoms")
    if not isinstance(atoms, list) or not atoms:
        raise ValueError(f"{case_id}: atoms are required")
    if any(not isinstance(atom, dict) for atom in atoms):
        raise ValueError(f"{case_id}: atoms must be mappings")
    if world["operator"] == "single" and len(atoms) != 1:
        raise ValueError(f"{case_id}: single worlds require exactly one atom")
    if world["operator"] == "all_of" and len(atoms) < 2:
        raise ValueError(f"{case_id}: all_of worlds require at least two atoms")
    atom_ids = [atom.get("atom_id") for atom in atoms]
    if len(set(atom_ids)) != len(atom_ids) or not all(
        isinstance(item, str) and item for item in atom_ids
    ):
        raise ValueError(f"{case_id}: atom_id values must be unique non-empty strings")
    for atom in atoms:
        if not isinstance(atom.get("claim"), str) or not atom["claim"]:
            raise ValueError(f"{case_id}: every atom needs plain-language claim text")
        support_ids = atom.get("support_fact_ids", [])
        contradict_ids = atom.get("contradicting_fact_ids", [])
        scope_ids = atom.get("scope_fact_ids", [])
        missing_id = atom.get("missing_material_id")
        if (
            not isinstance(support_ids, list)
            or not isinstance(contradict_ids, list)
            or not isinstance(scope_ids, list)
        ):
            raise ValueError(f"{case_id}: fact references must be lists")
        if not all(
            isinstance(item, str) and item for item in support_ids + contradict_ids + scope_ids
        ):
            raise ValueError(f"{case_id}: fact references must be non-empty strings")
        if set(support_ids) & set(contradict_ids):
            raise ValueError(f"{case_id}: support and contradiction facts must be disjoint")
        if support_ids and contradict_ids:
            raise ValueError(
                f"{case_id}: an atom cannot declare both support and contradiction routes"
            )
        unknown = (set(support_ids) | set(contradict_ids) | set(scope_ids)) - set(fact_ids)
        if unknown:
            raise ValueError(f"{case_id}: atom references unknown facts: {sorted(unknown)}")
        if missing_id is not None:
            if world["source_boundary"] != "named_missing_material":
                raise ValueError(f"{case_id}: missing material requires named_missing_material")
            if not isinstance(missing_id, str) or not missing_id:
                raise ValueError(f"{case_id}: missing_material_id must be a non-empty string")
            if support_ids or contradict_ids or scope_ids:
                raise ValueError(f"{case_id}: missing material cannot share a fact route")
            description = atom.get("missing_material_description")
            if not isinstance(description, str) or not description.strip():
                raise ValueError(
                    f"{case_id}: missing material requires a human-readable description"
                )


def derive_gold(manifest: dict[str, Any], *, manifest_sha256: str) -> dict[str, Any]:
    """Mechanically derive all atom relations and parent verdicts from declared facts."""
    validate_manifest(manifest)
    cases: list[dict[str, Any]] = []
    atom_counts: Counter[str] = Counter()
    parent_counts: Counter[str] = Counter()
    for world in manifest["worlds"]:
        fact_ids = {fact["fact_id"] for fact in world["facts"]}
        atoms: list[dict[str, Any]] = []
        for atom in world["atoms"]:
            relation = _derive_relation(atom, fact_ids)
            atom_counts[relation] += 1
            atoms.append(
                {
                    "atom_id": atom["atom_id"],
                    "claim": atom["claim"],
                    "relation": relation,
                    "derivation": _atom_derivation(atom, relation),
                }
            )
        verdict = _derive_parent_verdict(world["operator"], [atom["relation"] for atom in atoms])
        parent_counts[verdict] += 1
        cases.append(
            {
                "base_case_id": world["base_case_id"],
                "logic_family": world["logic_family"],
                "source_boundary": world["source_boundary"],
                "source_boundary_note": world["source_boundary_note"],
                "operator": world["operator"],
                "plain_claim": world["plain_claim"],
                "facts": world["facts"],
                "parent_rule_fact_ids": world.get("parent_rule_fact_ids", []),
                "atoms": atoms,
                "parent_verdict": verdict,
                "parent_derivation": _parent_derivation(
                    world["operator"],
                    atoms,
                    verdict,
                    world.get("parent_rule_fact_ids", []),
                ),
            }
        )
    _validate_coverage(atom_counts, parent_counts)
    output: dict[str, Any] = {
        "schema_version": DERIVATION_SCHEMA,
        "status": "draft_not_frozen_pending_cameron_approval",
        "label": "By-construction DEV logic contract; not validation, representative accuracy, or gate evidence",
        "manifest_version": manifest["version"],
        "manifest_sha256": manifest_sha256,
        "world_count": len(cases),
        "atom_relation_counts": dict(sorted(atom_counts.items())),
        "parent_verdict_counts": dict(sorted(parent_counts.items())),
        "cases": cases,
    }
    output["derived_gold_sha256"] = _sha256_text(_canonical_json(output))
    return output


def _derive_relation(atom: dict[str, Any], fact_ids: set[str]) -> str:
    if atom.get("missing_material_id") is not None:
        return "retrieval_gap"
    support_ids = set(atom.get("support_fact_ids", []))
    scope_ids = set(atom.get("scope_fact_ids", []))
    if support_ids and support_ids | scope_ids <= fact_ids:
        return "supports"
    if set(atom.get("contradicting_fact_ids", [])) & fact_ids and scope_ids <= fact_ids:
        return "refutes"
    return "insufficient"


def _atom_derivation(atom: dict[str, Any], relation: str) -> str:
    if relation == "retrieval_gap":
        return (
            f"named missing material {atom['missing_material_id']}: "
            f"{atom['missing_material_description']}"
        )
    if relation == "supports":
        if atom.get("scope_fact_ids"):
            return "all declared support and explicit scope facts are present"
        return "all declared support facts are present"
    if relation == "refutes":
        if atom.get("scope_fact_ids"):
            return "a declared incompatible fact is present within the explicit scope"
        return "a declared incompatible fact is present"
    return "no declared support or incompatible fact is present in the bounded evidence"


def _derive_parent_verdict(operator: str, relations: list[str]) -> str:
    if operator == "single":
        return {
            "supports": "supported",
            "refutes": "contradicted",
            "insufficient": "not_checkable",
            "retrieval_gap": "pending",
        }[relations[0]]
    if "refutes" in relations:
        return "contradicted"
    if "retrieval_gap" in relations:
        return "pending"
    if all(relation == "supports" for relation in relations):
        return "supported"
    if all(relation == "insufficient" for relation in relations):
        return "not_checkable"
    return "partially_supported"


def _parent_derivation(
    operator: str,
    atoms: list[dict[str, Any]],
    verdict: str,
    parent_rule_fact_ids: list[str] | None = None,
) -> str:
    relations = ", ".join(atom["relation"] for atom in atoms)
    rule = ""
    if parent_rule_fact_ids:
        rule = f" using declared parent rule facts {', '.join(parent_rule_fact_ids)}"
    return f"{operator} aggregation over [{relations}]{rule} derives {verdict}"


def _validate_coverage(atom_counts: Counter[str], parent_counts: Counter[str]) -> None:
    missing_relations = sorted(ATOM_RELATIONS - set(atom_counts))
    if missing_relations or any(atom_counts[relation] < 2 for relation in ATOM_RELATIONS):
        raise ValueError(
            f"every atom relation must appear at least twice; missing={missing_relations}"
        )
    missing_verdicts = sorted(PARENT_VERDICTS - set(parent_counts))
    if missing_verdicts or any(parent_counts[verdict] < 2 for verdict in PARENT_VERDICTS):
        raise ValueError(
            f"every parent verdict must appear at least twice; missing={missing_verdicts}"
        )


def render_review_cards(derived: dict[str, Any]) -> str:
    lines = [
        f"# Simple Logic Gold {derived['manifest_version']} — Cameron construction review",
        "",
        "This is a **DEV construction review**, not a CAL run, validation, or fresh-gate evidence.",
        "Approve or revise each explicit world and derivation. The relation targets are visible",
        "because you are approving the construction contract, not performing a blinded annotation.",
        "No world is frozen until you approve it; a revision creates a new version.",
        "",
        f"- Manifest SHA-256: `{derived['manifest_sha256']}`",
        f"- Draft derivative SHA-256: `{derived['derived_gold_sha256']}`",
        f"- Atom coverage: `{derived['atom_relation_counts']}`",
        f"- Parent coverage: `{derived['parent_verdict_counts']}`",
        "",
        "## Decision needed",
        "",
        "For each card: approve the facts, boundary, claim wording, and mechanical derivation; or",
        "write the exact revision. Do not approve based on what CAL or a model would likely say.",
    ]
    for case in derived["cases"]:
        lines.extend(
            [
                "",
                f"## {case['base_case_id']} — {case['logic_family']}",
                "",
                f"**Plain claim:** {case['plain_claim']}",
                "",
                f"**Evidence boundary:** `{case['source_boundary']}` — {case['source_boundary_note']}",
                "",
                "**Declared facts:**",
            ]
        )
        lines.extend(f"- `{fact['fact_id']}` — {fact['text']}" for fact in case["facts"])
        lines.append("")
        lines.append("**Mechanical atom derivation:**")
        lines.extend(
            f"- `{atom['atom_id']}` — `{atom['relation']}`: {atom['derivation']}"
            for atom in case["atoms"]
        )
        lines.extend(
            [
                "",
                f"**Parent:** `{case['parent_verdict']}` — {case['parent_derivation']}",
                "",
                "- [ ] Approve this world and derivation",
                "- [ ] Revise (write exact change):",
            ]
        )
    lines.extend(
        [
            "",
            "## Approval boundary",
            "",
            "After all 12 cards are approved, create a new frozen manifest version with the approval",
            "record and content hashes. Only then may CAL run on the direct-evidence lane. Evidence",
            "Bundler remains out of scope until the later read-only round-trip unit.",
            "",
        ]
    )
    return "\n".join(lines)


def render_review_html(derived: dict[str, Any]) -> str:
    """Render a local, checkpoint-only construction-review surface."""
    cards = []
    for case in derived["cases"]:
        case_id = html.escape(case["base_case_id"], quote=True)
        facts = "".join(f"<li>{html.escape(fact['text'])}</li>" for fact in case["facts"])
        atoms = "".join(
            "<li><strong>"
            f"{html.escape(atom['relation'])}</strong> — {html.escape(atom['claim'])} "
            f"({html.escape(atom['derivation'])})</li>"
            for atom in case["atoms"]
        )
        cards.append(
            f"""<section class=\"card\"><h2>{case_id} — {html.escape(case["logic_family"])}</h2>
<p><strong>Claim:</strong> {html.escape(case["plain_claim"])}</p>
<p><strong>Boundary:</strong> {html.escape(case["source_boundary"])} — {html.escape(case["source_boundary_note"])}</p>
<p><strong>Facts/evidence:</strong></p><ul>{facts}</ul>
<details><summary>Mechanical derivation and parent result</summary><ul>{atoms}</ul>
<p><strong>Parent:</strong> {html.escape(case["parent_verdict"])} — {html.escape(case["parent_derivation"])}</p></details>
<fieldset><legend>Your decision</legend><label><input type=\"radio\" name=\"{case_id}\" value=\"approve\"> Approve</label>
<label><input type=\"radio\" name=\"{case_id}\" value=\"revise\"> Revise</label></fieldset>
<label>Exact revision (required when revising)<textarea id=\"note-{case_id}\"></textarea></label></section>"""
        )
    payload = json.dumps(
        {
            "schema_version": "simple-logic-gold-construction-review-v0.1",
            "manifest_version": derived["manifest_version"],
            "manifest_sha256": derived["manifest_sha256"],
            "derived_gold_sha256": derived["derived_gold_sha256"],
            "case_ids": [case["base_case_id"] for case in derived["cases"]],
        },
        ensure_ascii=False,
        sort_keys=True,
    ).replace("<", "\\u003c")
    return f"""<!doctype html><html lang=\"en\"><meta charset=\"utf-8\"><title>Simple Logic Gold construction review</title>
<style>body{{font:16px system-ui;max-width:900px;margin:2rem auto;padding:0 1rem}}.card{{border:1px solid #bbb;border-radius:8px;padding:1rem;margin:1rem 0}}textarea{{display:block;width:100%;min-height:4rem}}button{{font:inherit;padding:.6rem 1rem}}.warning{{background:#fff4cc;padding:1rem}}</style>
<h1>Simple Logic Gold {html.escape(derived["manifest_version"])}</h1><p class=\"warning\">Approve or revise this explicit DEV construction contract. This export is a checkpoint only: it does not freeze worlds, run CAL, or create validation/gate evidence.</p>
<p>Decide each card quickly; open details only when needed. A revise decision needs an exact change.</p>{"".join(cards)}
<label>Your name <input id=\"reviewer\"></label><p><button id=\"download\">Download checkpoint</button> <span id=\"status\"></span></p>
<script>const base={payload}, key='simple-logic-gold:'+base.manifest_sha256;
function save(){{const s={{reviewer:document.querySelector('#reviewer').value}};base.case_ids.forEach(id=>{{s[id]=[...document.getElementsByName(id)].find(x=>x.checked)?.value||null;s['note-'+id]=document.getElementById('note-'+id).value||null}});localStorage.setItem(key,JSON.stringify(s));}}
function restore(){{const s=JSON.parse(localStorage.getItem(key)||'{{}}');document.querySelector('#reviewer').value=s.reviewer||'';base.case_ids.forEach(id=>{{[...document.getElementsByName(id)].forEach(x=>x.checked=x.value===s[id]);document.getElementById('note-'+id).value=s['note-'+id]||''}})}}
document.querySelectorAll('input,textarea').forEach(x=>x.addEventListener('input',save));restore();document.querySelector('#download').onclick=()=>{{const reviewer=document.querySelector('#reviewer').value.trim();const decisions=base.case_ids.map(id=>({{base_case_id:id,decision:[...document.getElementsByName(id)].find(x=>x.checked)?.value||null,note:document.getElementById('note-'+id).value.trim()||null}}));const bad=decisions.filter(d=>!d.decision||(d.decision==='revise'&&!d.note));if(!reviewer||bad.length){{document.querySelector('#status').textContent='Enter your name, complete every decision, and give every revision an exact change.';return}}const record={{...base,status:'draft_checkpoint_not_freeze',label:'DEV construction checkpoint; not validation or gate evidence',reviewer,exported_at_utc:new Date().toISOString(),decisions}};const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(record,null,2)+'\\n'],{{type:'application/json'}}));a.download='simple-logic-gold-'+base.manifest_version+'-construction-review-checkpoint.json';a.click();document.querySelector('#status').textContent='Checkpoint downloaded. Approval still requires an explicit versioned freeze.'}};</script>"""


def _write_absent_or_identical(path: Path, text: str) -> None:
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise FileExistsError(f"refusing to overwrite non-identical draft artifact: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_draft_artifacts(manifest_path: Path, out_dir: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    manifest_sha256 = _sha256_text(_canonical_json(manifest))
    derived = derive_gold(manifest, manifest_sha256=manifest_sha256)
    _write_absent_or_identical(
        out_dir / "derived-gold.json",
        json.dumps(derived, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )
    _write_absent_or_identical(out_dir / "CAMERON_REVIEW.md", render_review_cards(derived))
    _write_absent_or_identical(out_dir / "review.html", render_review_html(derived))
    return derived


def freeze_approved_draft(
    manifest_path: Path,
    derived_path: Path,
    checkpoint_path: Path,
    *,
    freeze_version: str,
    freeze_identifier: str,
) -> dict[str, Any]:
    """Fail closed while turning one approved construction checkpoint into a DEV freeze."""
    if not isinstance(freeze_version, str) or not freeze_version.strip():
        raise ValueError("freeze_version must be a non-empty string")
    if not isinstance(freeze_identifier, str) or not freeze_identifier.strip():
        raise ValueError("freeze_identifier must be a non-empty string")
    manifest = load_manifest(manifest_path)
    manifest_sha256 = _sha256_text(_canonical_json(manifest))
    rebuilt = derive_gold(manifest, manifest_sha256=manifest_sha256)
    try:
        stored = json.loads(derived_path.read_text(encoding="utf-8"))
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load freeze input: {exc}") from exc
    if stored != rebuilt:
        raise ValueError("derived gold does not match a fresh deterministic manifest rebuild")
    if not isinstance(checkpoint, dict):
        raise ValueError("construction checkpoint must be a mapping")
    _validate_approval_checkpoint(checkpoint, rebuilt)
    return {
        "schema_version": FREEZE_SCHEMA,
        "freeze_version": freeze_version,
        "freeze_identifier": freeze_identifier,
        "status": "frozen_approved_dev_not_validation_or_gate_evidence",
        "label": (
            "Frozen by-construction DEV logic contract; not validation, representative accuracy, "
            "fresh-blind gate evidence, production evidence, or a CAL-derived label source"
        ),
        "manifest_version": rebuilt["manifest_version"],
        "manifest_sha256": rebuilt["manifest_sha256"],
        "derived_gold_sha256": rebuilt["derived_gold_sha256"],
        "source_checkpoint_sha256": _sha256_bytes(checkpoint_path.read_bytes()),
        "reviewer": checkpoint["reviewer"],
        "checkpoint_exported_at_utc": checkpoint["exported_at_utc"],
        "approval": {
            "expected_case_count": len(rebuilt["cases"]),
            "approved": len(rebuilt["cases"]),
        },
        "world_count": rebuilt["world_count"],
        "atom_relation_counts": rebuilt["atom_relation_counts"],
        "parent_verdict_counts": rebuilt["parent_verdict_counts"],
        "frozen_cases": rebuilt["cases"],
    }


def _validate_approval_checkpoint(checkpoint: dict[str, Any], rebuilt: dict[str, Any]) -> None:
    if checkpoint.get("schema_version") != "simple-logic-gold-construction-review-v0.1":
        raise ValueError("checkpoint schema_version is invalid")
    if checkpoint.get("status") != "draft_checkpoint_not_freeze":
        raise ValueError("checkpoint status is not the expected pre-freeze approval record")
    if checkpoint.get("reviewer") != "Cameron":
        raise ValueError("checkpoint reviewer must be Cameron")
    exported_at_utc = checkpoint.get("exported_at_utc")
    if not isinstance(exported_at_utc, str) or not exported_at_utc.strip():
        raise ValueError("checkpoint exported_at_utc must be a non-empty string")
    for key in ("manifest_version", "manifest_sha256", "derived_gold_sha256"):
        if checkpoint.get(key) != rebuilt[key]:
            raise ValueError(f"checkpoint {key} does not match the deterministic draft rebuild")
    decisions = checkpoint.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError("checkpoint decisions must be a list")
    expected_ids = [case["base_case_id"] for case in rebuilt["cases"]]
    received_ids = [item.get("base_case_id") for item in decisions if isinstance(item, dict)]
    if len(decisions) != len(expected_ids) or set(received_ids) != set(expected_ids):
        raise ValueError("checkpoint must contain exactly the expected case IDs")
    if any(item.get("decision") != "approve" for item in decisions if isinstance(item, dict)):
        raise ValueError("every checkpoint decision must be approve before freeze")


def write_frozen_artifact(
    manifest_path: Path,
    derived_path: Path,
    checkpoint_path: Path,
    out_path: Path,
    *,
    freeze_version: str,
    freeze_identifier: str,
) -> dict[str, Any]:
    frozen = freeze_approved_draft(
        manifest_path,
        derived_path,
        checkpoint_path,
        freeze_version=freeze_version,
        freeze_identifier=freeze_identifier,
    )
    _write_absent_or_identical(
        out_path,
        json.dumps(frozen, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )
    return frozen


def _build_command(args: argparse.Namespace) -> None:
    derived = write_draft_artifacts(args.manifest, args.out_dir)
    print(f"worlds: {derived['world_count']}")
    print(f"manifest_sha256: {derived['manifest_sha256']}")
    print(f"derived_gold_sha256: {derived['derived_gold_sha256']}")
    print(f"review_cards: {args.out_dir / 'CAMERON_REVIEW.md'}")


def _freeze_command(args: argparse.Namespace) -> None:
    frozen = write_frozen_artifact(
        args.manifest,
        args.derived,
        args.checkpoint,
        args.out,
        freeze_version=args.freeze_version,
        freeze_identifier=args.freeze_identifier,
    )
    print(f"freeze_version: {frozen['freeze_version']}")
    print(f"freeze_identifier: {frozen['freeze_identifier']}")
    print(f"manifest_version: {frozen['manifest_version']}")
    print(f"manifest_sha256: {frozen['manifest_sha256']}")
    print(f"derived_gold_sha256: {frozen['derived_gold_sha256']}")
    print(f"source_checkpoint_sha256: {frozen['source_checkpoint_sha256']}")
    print(f"wrote: {args.out}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build-draft", help="Build draft review cards and derived gold.")
    build.add_argument("--manifest", type=Path, required=True)
    build.add_argument("--out-dir", type=Path, required=True)
    build.set_defaults(func=_build_command)
    freeze = subparsers.add_parser("freeze", help="Seal an approved draft without changing it.")
    freeze.add_argument("--manifest", type=Path, required=True)
    freeze.add_argument("--derived", type=Path, required=True)
    freeze.add_argument("--checkpoint", type=Path, required=True)
    freeze.add_argument("--out", type=Path, required=True)
    freeze.add_argument("--freeze-version", required=True)
    freeze.add_argument("--freeze-identifier", required=True)
    freeze.set_defaults(func=_freeze_command)
    return parser


def main() -> None:
    args = _parser().parse_args()
    try:
        args.func(args)
    except (FileExistsError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
