from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    subjects_path = Path(sys.argv[1]).resolve()
    root = Path(sys.argv[2]).resolve()
    subjects = json.loads(subjects_path.read_text())
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "worktree", "prune"], check=True)

    for family, spec in subjects.items():
        branch = spec["branch"]
        sha = spec["sha"]
        target = root / family
        if target.exists():
            shutil.rmtree(target)
        subprocess.run(["git", "fetch", "origin", branch], check=True)
        subprocess.run(
            ["git", "worktree", "add", "--detach", str(target), sha],
            check=True,
        )
        observed = subprocess.check_output(
            ["git", "-C", str(target), "rev-parse", "HEAD"],
            text=True,
        ).strip()
        if observed != sha:
            raise SystemExit(f"{family}: expected {sha}, observed {observed}")
        print(f"{family}: {observed}")


if __name__ == "__main__":
    main()
