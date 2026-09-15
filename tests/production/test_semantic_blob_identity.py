from __future__ import annotations

import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEMANTIC_ROOT = PROJECT_ROOT / "src" / "claim_audit_lab" / "production_v1" / "semantic"

# The successor preserves the qualified RC1 authority/measurement machinery and
# changes only the bounded semantic surfaces required by the convergence record:
# failure localization, negative-event relation behavior, and unresolved
# composition precedence.
EXPECTED_BLOBS = {
    "authority.py": "3cfcfb8cc3b3a8860e119edfbe22a4d684650a86",
    "authority_validation.py": "73ee2cc8e26cc3945558f76fa8c0992441177a97",
    "engine.py": "296e59ccf855db9e15064c78b1ebeec01b28873d",
    "measurements.py": "aa26d34a94488901d8a838824e0d7a23c6655f4c",
    "models.py": "4a8ee5ddc66ad5512d675b45215a858eb8fdd7ee",
    "relations.py": "2330f7acb64ac77ed0d26aebe7f4536062503400",
}


def _git_blob_sha(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content, usedforsecurity=False).hexdigest()


def test_production_semantic_core_matches_exact_successor_freeze() -> None:
    observed = {name: _git_blob_sha(SEMANTIC_ROOT / name) for name in EXPECTED_BLOBS}

    assert observed == EXPECTED_BLOBS
