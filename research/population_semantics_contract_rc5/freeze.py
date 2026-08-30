from __future__ import annotations

import argparse
import json
from pathlib import Path

from .build_corpus import build, canonical_bytes, sha256

EXPECTED_SHA256 = "9b5ce098f92061b310e812e2681ff4a7b710f05c8f3d777395a75c87ef8fa92a"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    actual = sha256()
    if actual != EXPECTED_SHA256:
        raise RuntimeError(f"RC5 corpus mismatch: {actual}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    corpus = build()
    (args.output_dir / "CORPUS.json").write_bytes(canonical_bytes(corpus))
    receipt = {"schema_version": corpus["schema_version"], "cohort_sha256": actual,
               "n_cases": len(corpus["cases"]), "n_ablation_witnesses": len(corpus["ablation_witnesses"]),
               "n_metamorphic_pairs": len(corpus["metamorphic_pairs"]), "mechanisms_executed": False}
    (args.output_dir / "FREEZE_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
