"""Join the PILOT-001 human gold with its blinding key into a CalibrationGold YAML.

Decision G dev tooling (``plans/adr-v1-pilot-001-dev-set.md``; the Unit-3 brief's
"gold-join shim"). The human gold (``audit_gold_template.yaml``, filled) is keyed
by blind ``ref: clm-XXX`` and carries no condition/model/claim_id; the blinding
key maps each ref to its bundle ``claim_id`` + condition (+ blinded ``model``).
This script emits the strict :class:`claim_audit_lab.v1.calibrate.CalibrationGold`
shape that ``claim-audit calibrate --gold`` consumes, keyed by ``claim_id`` so
``_check_alignment`` matches the packet traces exactly.

Vocabulary handling (fail-closed — an unmapped value is an error, never a drop):

* ``human_support_verdict`` values pass through (the codebook vocabulary equals
  ``RawGoldVerdict``).
* ``flags`` must be RawGoldFlag members (``overconfident`` / ``false_caution`` /
  ``source_scope_error`` / ``missing_needed``). Any other codebook flag
  (``citation_mismatch`` / ``missed_counterevidence`` / ``coverage_loss``) aborts
  with a message — extend ``RawGoldFlag`` + the crosswalk consciously, not here.
* ``citation_status: missing_needed`` is bridged into ``gold_flags`` (the
  crosswalk expects it as a flag; DECISIONS.md § 2026-07-01 finding). Other
  citation values are recorded in the summary but not emitted — no gate/dev
  acceptance condition scores citation (§1–7 schema note, 2026-06-30).

Starved derivation (operational, per the Unit-3 brief): ``cal_confidence == 0.0``
in the blinding key ∩ gold supported-slot (supported / partially_supported /
reasonable_inference). NOTE: this is *broader* than the falsification's
"41 starved-but-supported" — that number additionally required an identifiable
supporting passage found by the offline probe's ideal-span analysis, which is
not a machine-readable artifact. The derived set contains it; the run README
should report both framings. The count is printed and must be reviewed, not
assumed.

Usage:
    python scripts/pilot001_gold_shim.py \
        --gold <audit_gold_template.yaml> \
        --blinding-key <blinding_key.yaml> \
        --out <gold.dev.yaml>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import get_args

import yaml

from claim_audit_lab.v1.calibrate import CalibrationGold, RawGoldFlag, RawGoldVerdict

SUPPORTED_SLOT = frozenset({"supported", "partially_supported", "reasonable_inference"})
_GOLD_VERDICTS = frozenset(get_args(RawGoldVerdict))
_GOLD_FLAGS = frozenset(get_args(RawGoldFlag))


def build_gold(gold_path: Path, key_path: Path) -> tuple[dict[str, object], dict[str, int]]:
    """Return (CalibrationGold-shaped mapping, summary counts). Fail-closed."""
    gold_doc = yaml.safe_load(gold_path.read_text(encoding="utf-8"))
    key = yaml.safe_load(key_path.read_text(encoding="utf-8"))["key"]
    records = {claim["ref"]: claim for claim in gold_doc["claims"]}

    if set(records) != set(key):
        missing = sorted(set(records) ^ set(key))
        raise SystemExit(f"gold refs and blinding-key refs disagree: {', '.join(missing)}")

    claims: list[dict[str, object]] = []
    starved: list[str] = []
    bridged_citation = 0
    dropped_citation: dict[str, int] = {}
    for ref in sorted(records):
        record, join = records[ref], key[ref]
        verdict = record["human_support_verdict"]
        if verdict not in _GOLD_VERDICTS:
            raise SystemExit(f"{ref}: unmapped human_support_verdict {verdict!r}")

        flags = list(record.get("flags") or [])
        unknown = [flag for flag in flags if flag not in _GOLD_FLAGS]
        if unknown:
            raise SystemExit(
                f"{ref}: flags {unknown} are outside RawGoldFlag — extend the "
                "vocabulary + crosswalk deliberately before rerunning"
            )
        citation = (record.get("citation_status") or "").strip()
        if citation == "missing_needed":
            if "missing_needed" not in flags:
                flags.append("missing_needed")
            bridged_citation += 1
        elif citation:
            dropped_citation[citation] = dropped_citation.get(citation, 0) + 1

        claims.append(
            {
                "claim_id": join["claim_id"],
                "condition": join["condition"],
                "model": join["model"],
                "gold_verdict": verdict,
                "gold_flags": flags,
            }
        )
        if join.get("cal_confidence") == 0.0 and verdict in SUPPORTED_SLOT:
            starved.append(join["claim_id"])

    payload: dict[str, object] = {
        "gold_version": f"pilot-001-v2-audit+{key_path.name}+shim-v1",
        "starved_claim_ids": sorted(starved),
        "claims": claims,
    }
    summary = {
        "claims": len(claims),
        "starved": len(starved),
        "bridged_missing_needed": bridged_citation,
        **{f"dropped_citation[{k}]": v for k, v in sorted(dropped_citation.items())},
    }
    return payload, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--blinding-key", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    payload, summary = build_gold(args.gold, args.blinding_key)
    CalibrationGold.model_validate(payload)  # strict validation before writing

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    for name, value in summary.items():
        print(f"{name}: {value}", file=sys.stderr)
    print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
