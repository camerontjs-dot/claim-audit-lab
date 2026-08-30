from __future__ import annotations

import argparse
import json
from pathlib import Path

from .build_corpus import build, canonical_bytes, sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    corpus = build()
    if len(corpus["cases"]) != 460:
        raise RuntimeError(f"unexpected corrected case count: {len(corpus['cases'])}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "CORPUS.json").write_bytes(canonical_bytes(corpus))
    receipt = {
        "schema_version": corpus["schema_version"],
        "cohort_sha256": sha256(),
        "n_cases": len(corpus["cases"]),
        "n_ablation_witnesses": len(corpus["ablation_witnesses"]),
        "n_metamorphic_pairs": len(corpus["metamorphic_pairs"]),
        "semantic_mechanisms_executed": False,
        "semantic_mechanisms": "immutable imports from RC5",
    }
    (args.output_dir / "FREEZE_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
