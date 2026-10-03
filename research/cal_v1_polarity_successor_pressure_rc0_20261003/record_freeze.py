"""Record git blob ids for the campaign files. This file must not import CAL."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def main() -> None:
    names = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative == "HARNESS_FREEZE.json" or relative.startswith("evidence/") or "__pycache__" in relative:
            continue
        names.append(relative)
    payload = {
        "schema": "cal-v1-polarity-successor-pressure-harness-freeze-rc0",
        "blobs": {name: _blob(ROOT / name) for name in names},
    }
    (ROOT / "HARNESS_FREEZE.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(len(payload["blobs"]))


if __name__ == "__main__":
    main()
