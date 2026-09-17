from __future__ import annotations

import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEMANTIC_ROOT = PROJECT_ROOT / "src" / "claim_audit_lab" / "production_v1" / "semantic"

# Preserve the qualified predecessor identities explicitly across architecture
# successors. M3 changed authority.py and added measurement_ledger.py. M4 changes
# exactly engine.py to add the isolated shadow-observation runtime path.
KERNEL_RC0_AUTHORITY_BLOB = "3cfcfb8cc3b3a8860e119edfbe22a4d684650a86"
M3_AUTHORITY_SUCCESSOR_BLOB = "09761aab9e04deca724fd213a9295fc93cc3be52"
M3_MEASUREMENT_LEDGER_BLOB = "5e01c0a3246a90fcc42219da78b7d8a1ed5d5f74"
M3_ENGINE_BLOB = "67a519958bcf06b289b8a13cb0246d22ccf53c5c"
M4_ENGINE_SUCCESSOR_BLOB = "4111545663f97b4be53cc7523071bbed394d6769"

M4_SUCCESSOR_BLOBS = {
    "authority.py": M3_AUTHORITY_SUCCESSOR_BLOB,
    "authority_validation.py": "73ee2cc8e26cc3945558f76fa8c0992441177a97",
    "engine.py": M4_ENGINE_SUCCESSOR_BLOB,
    "measurement_ledger.py": M3_MEASUREMENT_LEDGER_BLOB,
    "measurements.py": "aa26d34a94488901d8a838824e0d7a23c6655f4c",
    "models.py": "4a8ee5ddc66ad5512d675b45215a858eb8fdd7ee",
    "plugins.py": "a2b96f192a4acafb2471785f0b51d2c656e03afc",
    "relations.py": "2330f7acb64ac77ed0d26aebe7f4536062503400",
}

M4_UNCHANGED_M3_BLOBS = {
    "authority.py": M3_AUTHORITY_SUCCESSOR_BLOB,
    "authority_validation.py": "73ee2cc8e26cc3945558f76fa8c0992441177a97",
    "measurement_ledger.py": M3_MEASUREMENT_LEDGER_BLOB,
    "measurements.py": "aa26d34a94488901d8a838824e0d7a23c6655f4c",
    "models.py": "4a8ee5ddc66ad5512d675b45215a858eb8fdd7ee",
    "plugins.py": "a2b96f192a4acafb2471785f0b51d2c656e03afc",
    "relations.py": "2330f7acb64ac77ed0d26aebe7f4536062503400",
}


def _git_blob_sha(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content, usedforsecurity=False).hexdigest()


def test_production_semantic_core_matches_exact_m4_successor_freeze() -> None:
    observed = {name: _git_blob_sha(SEMANTIC_ROOT / name) for name in M4_SUCCESSOR_BLOBS}

    assert observed == M4_SUCCESSOR_BLOBS


def test_m4_successor_preserves_unmodified_m3_semantic_implementations() -> None:
    observed = {
        name: _git_blob_sha(SEMANTIC_ROOT / name)
        for name in M4_UNCHANGED_M3_BLOBS
    }

    assert observed == M4_UNCHANGED_M3_BLOBS


def test_m4_engine_change_is_an_explicit_successor() -> None:
    observed = _git_blob_sha(SEMANTIC_ROOT / "engine.py")

    assert observed == M4_ENGINE_SUCCESSOR_BLOB
    assert observed != M3_ENGINE_BLOB


def test_m3_authority_successor_identity_remains_preserved() -> None:
    observed = _git_blob_sha(SEMANTIC_ROOT / "authority.py")

    assert observed == M3_AUTHORITY_SUCCESSOR_BLOB
    assert observed != KERNEL_RC0_AUTHORITY_BLOB
