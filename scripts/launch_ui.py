"""Launcher script for Claim Audit Lab Visual Workbench UI."""

from __future__ import annotations

import sys
from pathlib import Path

# Add workbench/src to sys.path
workbench_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(workbench_dir / "src"))

from claim_audit_lab.ui.server import run_server


def main():
    port = 8765
    print("=" * 75)
    print("🚀 CLAIM AUDIT LAB — VISUAL WORKBENCH UI")
    print(f"URL: http://127.0.0.1:{port}")
    print("=" * 75)
    run_server(port)


if __name__ == "__main__":
    main()
