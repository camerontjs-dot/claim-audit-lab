"""Shared deterministic C-B hashing and YAML serialization helpers."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

import yaml

PENDING_HASH = "sha256:pending"
SHA256_PREFIX = "sha256:"

_YAML_DUMP_KWARGS: dict[str, Any] = {
    "allow_unicode": True,
    "default_flow_style": False,
    "indent": 2,
    "sort_keys": False,
}


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    """Load one YAML mapping from disk."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("expected YAML mapping")
    return data


def yaml_to_string(data: dict[str, Any]) -> str:
    """Serialize a mapping with the contract's deterministic YAML settings."""
    return cast(str, yaml.safe_dump(data, **_YAML_DUMP_KWARGS))


def hash_file_hex(path: Path) -> str:
    """Return a lowercase SHA-256 hex digest for a file."""
    return sha256(path.read_bytes()).hexdigest()


def hash_text(text: str) -> str:
    """Return a prefixed SHA-256 digest for UTF-8 text."""
    return f"{SHA256_PREFIX}{sha256(text.encode('utf-8')).hexdigest()}"


def iter_handoff_files(
    root: Path,
    *,
    exclude_names: Iterable[str] = ("SHA256SUMS",),
) -> list[Path]:
    """Return sorted bundle files included in handoff integrity calculations."""
    excluded = set(exclude_names)
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.name not in excluded and "deviations" not in path.parts
    )


def hash_audit_config_file(path: Path) -> str:
    """Hash normalized audit config YAML with its self-hash set to pending."""
    return _normalized_yaml_hash(
        path,
        lambda data: data.__setitem__("config_hash", PENDING_HASH),
    )


def hash_bundle_manifest_file(path: Path) -> str:
    """Hash normalized manifest YAML with its bundle hash set to pending."""

    def normalize(data: dict[str, Any]) -> None:
        bundle = data.get("bundle")
        if not isinstance(bundle, dict):
            raise ValueError("bundle_manifest.yaml missing bundle mapping")
        bundle["bundle_hash"] = PENDING_HASH

    return _normalized_yaml_hash(path, normalize)


def compute_bundle_tree_hash(bundle_dir: Path) -> str:
    """Compute the contract bundle-tree hash."""
    hasher = sha256()
    for path in iter_handoff_files(bundle_dir):
        rel_path = path.relative_to(bundle_dir).as_posix()
        if rel_path == "audit_config.yaml":
            digest = _strip_hash_prefix(hash_audit_config_file(path))
        elif rel_path == "bundle_manifest.yaml":
            digest = _strip_hash_prefix(hash_bundle_manifest_file(path))
        else:
            digest = hash_file_hex(path)
        hasher.update(f"{rel_path}\0{digest}\n".encode())
    return f"{SHA256_PREFIX}{hasher.hexdigest()}"


def _normalized_yaml_hash(
    path: Path,
    normalizer: Callable[[dict[str, Any]], None],
) -> str:
    data = load_yaml_mapping(path)
    normalizer(data)
    return hash_text(yaml_to_string(data))


def _strip_hash_prefix(value: str) -> str:
    if not value.startswith(SHA256_PREFIX):
        raise ValueError(f"Expected sha256: hash value, got {value!r}")
    return value.removeprefix(SHA256_PREFIX)


__all__ = [
    "PENDING_HASH",
    "SHA256_PREFIX",
    "compute_bundle_tree_hash",
    "hash_audit_config_file",
    "hash_bundle_manifest_file",
    "hash_file_hex",
    "hash_text",
    "iter_handoff_files",
    "load_yaml_mapping",
    "yaml_to_string",
]
