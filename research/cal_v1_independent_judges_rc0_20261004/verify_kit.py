"""Verify preparation-kit bytes. No candidate code or source hashes are repaired."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent
    freeze = json.loads((root / "FREEZE.json").read_text(encoding="utf-8"))
    errors = []
    for relative, expected in freeze["files"].items():
        path = root / relative
        if path.is_symlink() or not path.is_file():
            errors.append(f"missing or symlink: {relative}")
            continue
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != expected:
            errors.append(f"hash mismatch: {relative}")
    print(json.dumps({"evidence_class": "PREPARATION_KIT_INTEGRITY_ONLY",
                      "files_checked": len(freeze["files"]), "errors": errors,
                      "passed": not errors, "candidate_executed": False}, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
