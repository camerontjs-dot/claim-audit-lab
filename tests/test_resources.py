"""Tests for packaged runtime resources and contract serialization."""

from __future__ import annotations

from pathlib import Path

import pytest

from claim_audit_lab.contracts.serialization import (
    hash_bundle_manifest_file,
    load_yaml_mapping,
)
from claim_audit_lab.resources import (
    PackageResourceError,
    package_file,
    read_package_bytes,
    read_package_text,
)


@pytest.mark.parametrize(
    "reader",
    [read_package_text, read_package_bytes],
    ids=["text", "bytes"],
)
def test_missing_packaged_resource_raises_typed_error(reader) -> None:
    with pytest.raises(PackageResourceError, match="missing.txt"):
        reader("missing.txt")


def test_missing_packaged_file_context_raises_typed_error() -> None:
    with pytest.raises(PackageResourceError, match="missing.txt"):
        with package_file("missing.txt"):
            raise AssertionError("unreachable")


def test_load_yaml_mapping_rejects_non_mapping(tmp_path: Path) -> None:
    path = tmp_path / "list.yaml"
    path.write_text("- item\n", encoding="utf-8")

    with pytest.raises(ValueError, match="expected YAML mapping"):
        load_yaml_mapping(path)


def test_manifest_hash_requires_bundle_mapping(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    path.write_text("bundle: []\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing bundle mapping"):
        hash_bundle_manifest_file(path)
