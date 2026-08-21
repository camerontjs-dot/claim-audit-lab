"""Freeze the accepted Simple Logic Gold domain renderings as a paired artifact.

Builds a frozen-gold-schema domain payload from the accepted renderings draft by
copying the plain frozen artifact and substituting only case ids, claims, fact
ids/texts, atom ids/claims, and entity-mapped boundary notes. Every structural
field (operator, relations, parent verdicts, counts, boundaries) is inherited,
so the pair shares one derivation by construction. Relations declared in the
renderings must equal the base relations or the freeze fails.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

# Boundary-note entity substitutions (accepted option: re-render notes with the
# entity map; everything not listed is inherited verbatim).
_NOTE_SUBSTITUTIONS: dict[str, list[tuple[str, str]]] = {
    "SLG-12": [("complete trip temperature log", "complete trip data-logger temperature record")],
}


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def build_domain_frozen(plain: dict[str, Any], renderings: dict[str, Any]) -> dict[str, Any]:
    """Return the domain frozen payload; raise on any drift from the base structure."""
    by_base = {entry["base_case_id"]: entry for entry in renderings["renderings"]}
    if set(by_base) != {case["base_case_id"] for case in plain["frozen_cases"]}:
        raise ValueError("renderings do not cover exactly the frozen base worlds")

    domain_cases: list[dict[str, Any]] = []
    for case in plain["frozen_cases"]:
        entry = by_base[case["base_case_id"]]
        fact_map = {fact["maps_to"]: fact for fact in entry["facts"]}
        atom_map = {atom["maps_to"]: atom for atom in entry["atoms"]}
        if set(fact_map) != {fact["fact_id"] for fact in case["facts"]}:
            raise ValueError(f"{case['base_case_id']}: fact maps_to set mismatch")
        if set(atom_map) != {atom["atom_id"] for atom in case["atoms"]}:
            raise ValueError(f"{case['base_case_id']}: atom maps_to set mismatch")
        new_case = json.loads(json.dumps(case))
        new_case["base_case_id"] = entry["domain_case_id"]
        new_case["paired_base_case_id"] = case["base_case_id"]
        new_case["plain_claim"] = entry["domain_claim"].strip()
        new_case["facts"] = [
            {"fact_id": fact_map[f["fact_id"]]["fact_id"], "text": fact_map[f["fact_id"]]["text"]}
            for f in case["facts"]
        ]
        new_atoms = []
        for atom in case["atoms"]:
            rendered = atom_map[atom["atom_id"]]
            if rendered["relation"] != atom["relation"]:
                raise ValueError(f"{atom['atom_id']}: rendering changed the frozen relation")
            new_atoms.append(
                {
                    "atom_id": rendered["atom_id"],
                    "claim": rendered["claim"],
                    "relation": atom["relation"],
                    "derivation": atom["derivation"],
                }
            )
        new_case["atoms"] = new_atoms
        note = new_case.get("source_boundary_note", "")
        for old, new in _NOTE_SUBSTITUTIONS.get(case["base_case_id"], []):
            note = note.replace(old, new)
        new_case["source_boundary_note"] = note
        domain_cases.append(new_case)

    payload = json.loads(json.dumps(plain))
    payload["frozen_cases"] = domain_cases
    payload["freeze_identifier"] = "slg-domain-renderings-v0.1-rev02-2026-07-16"
    payload["freeze_version"] = "v0.1-rev02-domain"
    payload["paired_plain_freeze_identifier"] = plain["freeze_identifier"]
    payload["reviewer"] = "Cameron (in-session, 2026-07-16) + adversarial 12-checker sweep"
    payload["approval"] = (
        "Accepted 2026-07-16 per plans/simple-logic-gold-dev.md Unit 3; boundary notes "
        "re-rendered with the entity map; DEV contract evidence only."
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plain", type=Path, required=True)
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    plain = json.loads(args.plain.read_text(encoding="utf-8"))
    renderings = yaml.safe_load(args.draft.read_text(encoding="utf-8"))
    payload = build_domain_frozen(plain, renderings)
    payload["manifest_version"] = "slg-domain-renderings-v0.1-rev02"
    payload["manifest_sha256"] = _sha256_bytes(args.draft.read_bytes())
    canonical = json.dumps(payload["frozen_cases"], sort_keys=True, separators=(",", ":"))
    payload["derived_gold_sha256"] = _sha256_bytes(canonical.encode())

    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / "domain-frozen-gold.json"
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if target.exists() and target.read_text(encoding="utf-8") != text:
        raise FileExistsError(f"refusing to replace non-identical freeze: {target}")
    target.write_text(text, encoding="utf-8")
    print(
        json.dumps({"frozen": str(target), "sha256": _sha256_bytes(text.encode())}, sort_keys=True)
    )


if __name__ == "__main__":
    main()
