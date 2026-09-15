#!/usr/bin/env python3
"""Validate then execute one typed target against one Contract B 1.2 bundle.

This wrapper only orchestrates `claim-audit-v1`. It does not choose evidence,
reinterpret evidence, alter semantic family fields, infer a verdict, or
overwrite a non-empty run directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle_dir", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    out_dir = args.out_dir
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"refusing non-empty output directory: {out_dir}", file=sys.stderr)
        return 2

    validate = subprocess.run(
        ["claim-audit-v1", "validate-bundle", str(args.bundle_dir), str(args.target)],
        check=False,
    )
    if validate.returncode != 0:
        return validate.returncode

    run = subprocess.run(
        [
            "claim-audit-v1",
            "run-bundle",
            str(args.bundle_dir),
            str(args.target),
            "--out-dir",
            str(out_dir),
        ],
        check=False,
    )
    if run.returncode != 0:
        return run.returncode

    receipt = {
        "schema": "cal-v1-local-run-receipt-v1",
        "bundle_dir": str(args.bundle_dir),
        "target": str(args.target),
        "target_sha256": _sha256(args.target),
        "out_dir": str(out_dir),
        "files": {path.name: _sha256(path) for path in sorted(out_dir.iterdir()) if path.is_file()},
    }
    (out_dir / "local-run-receipt.json").write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
