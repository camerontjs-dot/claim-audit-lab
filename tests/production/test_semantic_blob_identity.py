from __future__ import annotations

import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEMANTIC_ROOT = PROJECT_ROOT / "src" / "claim_audit_lab" / "production_v1" / "semantic"

# CAL V1 kernel plugin-registry RC0 is a deliberate architecture successor to
# the frozen integration candidate. The qualified authority, authority-validation,
# measurement, model, and relation implementations remain byte-identical to the
# parent. Engine dispatch changes and plugins.py is new; pin both exactly so this
# research successor cannot drift while still pretending to be the same subject.
EXPECTED_BLOBS = {
    "authority.py": "3cfcfb8cc3b3a8860e119edfbe22a4d684650a86",
    "authority_validation.py": "73ee2cc8e26cc3945558f76fa8c0992441177a97",
    "engine.py": "67a519958bcf06b289b8a13cb0246d22ccf53c5c",
    "measurements.py": "aa26d34a94488901d8a838824e0d7a23c6655f4c",
    "models.py": "4a8ee5ddc66ad5512d675b45215a858eb8fdd7ee",
    "plugins.py": "a2b96f192a4acafb2471785f0b51d2c656e03afc",
    "relations.py": "2330f7acb64ac77ed0d26aebe7f4536062503400",
}

PARENT_STABLE_BLOBS = {
    "authority.py": "3cfcfb8cc3b3a8860e119edfbe22a4d684650a86",
    "authority_validation.py": "73ee2cc8e26cc3945558f76fa8c0992441177a97",
    "measurements.py": "aa26d34a94488901d8a838824e0d7a23c6655f4c",
    "models.py": "4a8ee5ddc66ad5512d675b45215a858eb8fdd7ee",
    "relations.py": "2330f7acb64ac77ed0d26aebe7f4536062503400",
}


def _git_blob_sha(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content, usedforsecurity=False).hexdigest()


def test_production_semantic_core_matches_exact_kernel_successor_freeze() -> None:
    observed = {name: _git_blob_sha(SEMANTIC_ROOT / name) for name in EXPECTED_BLOBS}

    assert observed == EXPECTED_BLOBS


def test_kernel_successor_preserves_parent_semantic_implementations() -> None:
    observed = {name: _git_blob_sha(SEMANTIC_ROOT / name) for name in PARENT_STABLE_BLOBS}

    assert observed == PARENT_STABLE_BLOBS
