"""Run the Claim Audit Lab report demo."""

from __future__ import annotations

import argparse
from pathlib import Path

from claim_audit_lab.auditor import audit_document
from claim_audit_lab.loader import load_draft, load_evidence_bundle
from claim_audit_lab.report import render_json_report, render_markdown_report

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DRAFT = PROJECT_ROOT / "examples" / "drafts" / "ai-research-note.md"
DEFAULT_EVIDENCE = PROJECT_ROOT / "examples" / "evidence" / "ai-research-evidence.yml"
BUILD_REPORT_DIR = PROJECT_ROOT / "build" / "reports"
FIXTURE_REPORT_DIR = PROJECT_ROOT / "examples" / "reports"


def main() -> None:
    """Run the demo entry point."""
    args = _parse_args()
    report_dir = FIXTURE_REPORT_DIR if args.update_fixture else BUILD_REPORT_DIR
    slice_stem = f"{args.draft.stem}.slice"
    markdown_out = args.out or report_dir / f"{slice_stem}.md"
    json_out = args.json_out or report_dir / f"{slice_stem}.json"

    draft = load_draft(args.draft)
    evidence_bundle = load_evidence_bundle(args.evidence)
    report = audit_document(draft, evidence_bundle)

    _write_text(markdown_out, render_markdown_report(report))
    _write_text(json_out, render_json_report(report))

    print(f"Wrote Markdown report: {markdown_out}")
    print(f"Wrote JSON report: {json_out}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Claim Audit Lab deterministic report demo.",
    )
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument(
        "--update-fixture",
        action="store_true",
        help="Write checked-in example reports instead of gitignored build outputs.",
    )
    return parser.parse_args()


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
