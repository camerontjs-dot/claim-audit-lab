"""Access package-owned runtime resources."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from importlib.resources import as_file, files
from pathlib import Path

_PACKAGE = "claim_audit_lab"


class PackageResourceError(RuntimeError):
    """Raised when a required packaged resource is unavailable."""


def read_package_text(relative_path: str) -> str:
    """Read one UTF-8 package resource."""
    resource = files(_PACKAGE).joinpath(relative_path)
    if not resource.is_file():
        raise PackageResourceError(f"Required package resource is missing: {relative_path}")
    return resource.read_text(encoding="utf-8")


def read_package_bytes(relative_path: str) -> bytes:
    """Read one package resource as bytes."""
    resource = files(_PACKAGE).joinpath(relative_path)
    if not resource.is_file():
        raise PackageResourceError(f"Required package resource is missing: {relative_path}")
    return resource.read_bytes()


@contextmanager
def package_file(relative_path: str) -> Iterator[Path]:
    """Expose one package resource as a filesystem path for a bounded operation."""
    resource = files(_PACKAGE).joinpath(relative_path)
    if not resource.is_file():
        raise PackageResourceError(f"Required package resource is missing: {relative_path}")
    with as_file(resource) as path:
        yield path


__all__ = [
    "PackageResourceError",
    "package_file",
    "read_package_bytes",
    "read_package_text",
]
