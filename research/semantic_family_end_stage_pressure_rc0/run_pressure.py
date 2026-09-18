from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    subjects_path = Path(sys.argv[1]).resolve()
    cases_path = Path(sys.argv[2]).resolve()
    worktree_root = Path(sys.argv[3]).resolve()
    report_path = Path(sys.argv[4]).resolve()

    subjects = json.loads(subjects_path.read_text())
    cases = json.loads(cases_path.read_text())
    probe_script = Path(__file__).with_name("probe_family.py").resolve()

    all_rows: list[dict[str, str]] = []
    for family in subjects:
        target = worktree_root / family
        completed = subprocess.run(
            [
                sys.executable,
                str(probe_script),
                family,
                str(target),
                str(cases_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        rows = json.loads(completed.stdout)
        all_rows.extend(rows)

    by_case: dict[str, list[dict[str, str]]] = {}
    for row in all_rows:
        by_case.setdefault(row["case_id"], []).append(row)

    failures: list[dict[str, object]] = []
    summary: list[dict[str, object]] = []

    for case in cases:
        rows = by_case[case["case_id"]]
        errors = [row for row in rows if row["status"] == "PROBE_ERROR"]
        warrants = sorted(
            row["family"] for row in rows if row["status"] == "WARRANTED"
        )
        allowed = sorted(case["allowed"])
        summary.append(
            {
                "case_id": case["case_id"],
                "class": case["class"],
                "text": case["text"],
                "allowed": allowed,
                "warrants": warrants,
            }
        )
        if errors or warrants != allowed:
            failures.append(
                {
                    "case_id": case["case_id"],
                    "class": case["class"],
                    "text": case["text"],
                    "allowed": allowed,
                    "warrants": warrants,
                    "probe_errors": errors,
                }
            )

    report = {
        "subjects": subjects,
        "case_count": len(cases),
        "family_count": len(subjects),
        "observations": all_rows,
        "summary": summary,
        "failures": failures,
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    print(json.dumps({"summary": summary, "failures": failures}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
