from __future__ import annotations

import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEMANTIC_ROOT = PROJECT_ROOT / "src" / "claim_audit_lab" / "production_v1" / "semantic"

# M1 established the kernel plugin-registry RC0 freeze. M3 deliberately changes
# exactly one previously frozen semantic implementation: authority.py gains an
# independently enforced measurement/proposition family guard after a frozen
# direct-consumption falsifier showed that the plugin wrapper alone was insufficient.
# Preserve the predecessor identity explicitly rather than rewriting its history.
KERNEL_RC0_AUTHORITY_BLOB = "3cfcfb8cc3b3a8860e119edfbe22a4d684650a86"
M3_AUTHORITY_SUCCESSOR_BLOB = "09761aab9e04deca724fd213a9295fc93cc3be52"
M3_MEASUREMENT_LEDGER_BLOB = "5e01c0a3246a90fcc42219da78b7d8a1ed5d5f74"

M3_SUCCESSOR_BLOBS = {
    "authority.py": M3_AUTHORITY_SUCCESSOR_BLOB,
    "authority_validation.py": "73ee2cc8e26cc3945558f76fa8c0992441177a97",
    "engine.py": "67a519958bcf06b289b8a13cb0246d22ccf53c5c",
    "measurement_ledger.py": M3_MEASUREMENT_LEDGER_BLOB,
    "measurements.py": "aa26d34a94488901d8a838824e0d7a23c6655f4c",
    "models.py": "4a8ee5ddc66ad5512d675b45215a858eb8fdd7ee",
    "plugins.py": "a2b96f192a4acafb2471785f0b51d2c656e03afc",
    "relations.py": "2330f7acb64ac77ed0d26aebe7f4536062503400",
}

M3_UNCHANGED_PARENT_BLOBS = {
    "authority_validation.py": "73ee2cc8e26cc3945558f76fa8c0992441177a97",
    "engine.py": "67a519958bcf06b289b8a13cb0246d22ccf53c5c",
    "measurements.py": "aa26d34a94488901d8a838824e0d7a23c6655f4c",
    "models.py": "4a8ee5ddc66ad5512d675b45215a858eb8fdd7ee",
    "plugins.py": "a2b96f192a4acafb2471785f0b51d2c656e03afc",
    "relations.py": "2330f7acb64ac77ed0d26aebe7f4536062503400",
}


def _git_blob_sha(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content, usedforsecurity=False).hexdigest()


def test_production_semantic_core_matches_exact_m3_successor_freeze() -> None:
    observed = {name: _git_blob_sha(SEMANTIC_ROOT / name) for name in M3_SUCCESSOR_BLOBS}

    assert observed == M3_SUCCESSOR_BLOBS


def test_m3_successor_preserves_unmodified_parent_semantic_implementations() -> None:
    observed = {
        name: _git_blob_sha(SEMANTIC_ROOT / name)
        for name in M3_UNCHANGED_PARENT_BLOBS
    }

    assert observed == M3_UNCHANGED_PARENT_BLOBS


def test_m3_authority_change_is_an_explicit_successor() -> None:
    observed = _git_blob_sha(SEMANTIC_ROOT / "authority.py")

    assert observed == M3_AUTHORITY_SUCCESSOR_BLOB
    assert observed != KERNEL_RC0_AUTHORITY_BLOB
