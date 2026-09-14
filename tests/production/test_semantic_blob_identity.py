from __future__ import annotations

import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEMANTIC_ROOT = PROJECT_ROOT / "src" / "claim_audit_lab" / "production_v1" / "semantic"

EXPECTED_BLOBS = {
    "authority.py": "3cfcfb8cc3b3a8860e119edfbe22a4d684650a86",
    "authority_validation.py": "73ee2cc8e26cc3945558f76fa8c0992441177a97",
    "engine.py": "636734fd1341d2ae721ae9697c7ac7652b89eecc",
    "measurements.py": "aa26d34a94488901d8a838824e0d7a23c6655f4c",
    "models.py": "4710923e62ef62b472abb21b9e075b177ebb7413",
    "relations.py": "e9e9401c92ee11d25a50dbc36e80aeb4c4cd220d",
}


def _git_blob_sha(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content, usedforsecurity=False).hexdigest()


def test_production_semantic_core_matches_exact_rc1_git_blobs() -> None:
    observed = {name: _git_blob_sha(SEMANTIC_ROOT / name) for name in EXPECTED_BLOBS}

    assert observed == EXPECTED_BLOBS
