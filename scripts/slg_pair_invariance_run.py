"""Unit 3b: run CAL over all 24 paired direct-evidence records and report invariance.

Both lanes run through the unchanged ``run_direct_lane`` machinery — 12 plain
worlds from the frozen base artifact and 12 domain worlds from the accepted
paired freeze. The report keeps pair invariance separate from correctness and
classifies every comparable atom pair as both-match, wrong-on-both (invariant
but incorrect), plain-only-miss, or domain-only-miss. DEV diagnostic only;
never validation, representative accuracy, or gate evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from scripts.simple_logic_gold_direct_lane import run_direct_lane
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from simple_logic_gold_direct_lane import run_direct_lane  # type: ignore[no-redef]


def classify(plain_match: bool | None, domain_match: bool | None) -> str:
    """Classify one comparable atom pair per the Unit 3 green boundary."""
    if plain_match is None or domain_match is None:
        return "noncomparable"
    if plain_match and domain_match:
        return "both-match"
    if not plain_match and not domain_match:
        return "wrong-on-both"
    return "plain-only-miss" if not plain_match else "domain-only-miss"


def build_pair_report(
    plain_run: dict[str, Any],
    domain_run: dict[str, Any],
    plain_frozen: dict[str, Any],
    domain_frozen: dict[str, Any],
) -> dict[str, Any]:
    """Join the two lanes over the frozen pair correspondence and classify pairs.

    The domain freeze inherits atom order per case (slg_domain_freeze builds the
    domain atoms by iterating the base atoms), so order-aligned zipping over each
    (paired_base_case_id, domain case) is the pair map.
    """
    plain_cases = {c["base_case_id"]: c for c in plain_frozen["frozen_cases"]}
    atom_pairs: dict[str, str] = {}
    for domain_case in domain_frozen["frozen_cases"]:
        base_case = plain_cases[domain_case["paired_base_case_id"]]
        for atom, rendered in zip(base_case["atoms"], domain_case["atoms"], strict=True):
            atom_pairs[atom["atom_id"]] = rendered["atom_id"]
    plain_atoms = {a["atom_id"]: a for a in plain_run["atoms"]}
    domain_atoms = {a["atom_id"]: a for a in domain_run["atoms"]}
    rows = []
    counts: dict[str, int] = {}
    invariant = 0
    comparable = 0
    for plain_id, domain_id in sorted(atom_pairs.items()):
        p, d = plain_atoms[plain_id], domain_atoms[domain_id]
        outcome = classify(p["match"], d["match"])
        counts[outcome] = counts.get(outcome, 0) + 1
        pair_invariant = p["cal_observed_relation"] == d["cal_observed_relation"]
        if p["comparable"]:
            comparable += 1
            invariant += pair_invariant
        rows.append(
            {
                "plain_atom_id": plain_id,
                "domain_atom_id": domain_id,
                "expected_relation": p["expected_relation"],
                "plain_observed": p["cal_observed_relation"],
                "domain_observed": d["cal_observed_relation"],
                "pair_invariant": pair_invariant,
                "classification": outcome,
            }
        )
    return {
        "schema_version": "slg-pair-invariance-v0.1",
        "label": "DEV diagnostic only; not validation or gate evidence",
        "pairs": rows,
        "summary": {
            "atom_pairs": len(rows),
            "comparable_pairs": comparable,
            "invariant_comparable_pairs": invariant,
            "classification_counts": dict(sorted(counts.items())),
            "plain_matching_comparable": plain_run["summary"]["matching_comparable_atoms"],
            "domain_matching_comparable": domain_run["summary"]["matching_comparable_atoms"],
            "plain_matching_parents": plain_run["summary"]["matching_atom_derived_parents"],
            "domain_matching_parents": domain_run["summary"]["matching_atom_derived_parents"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plain-frozen", type=Path, required=True)
    parser.add_argument("--domain-frozen", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    plain_frozen = json.loads(args.plain_frozen.read_text(encoding="utf-8"))
    domain_frozen = json.loads(args.domain_frozen.read_text(encoding="utf-8"))
    first = _run_once(args.plain_frozen, args.domain_frozen, plain_frozen, domain_frozen)
    second = _run_once(args.plain_frozen, args.domain_frozen, plain_frozen, domain_frozen)
    if json.dumps(first, sort_keys=True) != json.dumps(second, sort_keys=True):
        raise ValueError("pair-invariance run is not repeat-identical")

    args.out.mkdir(parents=True, exist_ok=True)
    for name, payload in first.items():
        target = args.out / f"{name}.json"
        text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if target.exists() and target.read_text(encoding="utf-8") != text:
            raise FileExistsError(f"refusing to replace non-identical output: {target}")
        target.write_text(text, encoding="utf-8")
    print(json.dumps(first["pair-report"]["summary"], sort_keys=True))


def _run_once(
    plain_path: Path,
    domain_path: Path,
    plain_frozen: dict[str, Any],
    domain_frozen: dict[str, Any],
) -> dict[str, Any]:
    plain_run = run_direct_lane(plain_path)
    domain_run = run_direct_lane(domain_path)
    report = build_pair_report(plain_run, domain_run, plain_frozen, domain_frozen)
    return {"plain-run": plain_run, "domain-run": domain_run, "pair-report": report}


if __name__ == "__main__":
    main()
