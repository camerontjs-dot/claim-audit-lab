"""Input loading for drafts and evidence bundles."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from pydantic import ValidationError

from claim_audit_lab.models import DraftDocument, EvidenceBundle

_DRAFT_SUFFIXES = {".md", ".markdown", ".txt"}
_YAML_SUFFIXES = {".yml", ".yaml"}
_JSON_SUFFIXES = {".json"}


class LoaderError(ValueError):
    """Path-aware error for file loading and validation failures."""

    def __init__(self, path: str | Path, message: str) -> None:
        self.path = Path(path)
        self.message = message
        super().__init__(f"{self.path}: {self.message}")


def load_draft(
    path: str | Path,
    *,
    document_id: str | None = None,
    title: str | None = None,
) -> DraftDocument:
    """Load a Markdown or plain text draft into a typed document."""
    draft_path = Path(path)
    suffix = draft_path.suffix.lower()

    if suffix not in _DRAFT_SUFFIXES:
        raise LoaderError(
            draft_path,
            "Unsupported draft file type. Expected Markdown or plain text.",
        )

    content = _read_text(draft_path)
    inferred_title = title
    if inferred_title is None and suffix in {".md", ".markdown"}:
        inferred_title = _infer_markdown_title(content)

    try:
        return DraftDocument(
            id=document_id or draft_path.stem,
            title=inferred_title,
            content=content,
            path=str(draft_path),
        )
    except ValidationError as exc:
        raise LoaderError(
            draft_path,
            f"Validation failed for draft: {_format_validation_error(exc)}",
        ) from exc


def load_evidence_bundle(path: str | Path) -> EvidenceBundle:
    """Load a YAML or JSON evidence bundle into typed models."""
    bundle_path = Path(path)
    suffix = bundle_path.suffix.lower()

    if suffix in _YAML_SUFFIXES:
        content = _read_text(bundle_path)
        data = _parse_yaml(content, bundle_path)
    elif suffix in _JSON_SUFFIXES:
        content = _read_text(bundle_path)
        data = _parse_json(content, bundle_path)
    else:
        raise LoaderError(
            bundle_path,
            "Unsupported evidence file type. Expected YAML or JSON.",
        )

    try:
        return EvidenceBundle.model_validate(data)
    except ValidationError as exc:
        raise LoaderError(
            bundle_path,
            f"Validation failed for evidence bundle: {_format_validation_error(exc)}",
        ) from exc


def _read_text(path: Path) -> str:
    if not path.exists():
        raise LoaderError(path, "File does not exist.")
    if not path.is_file():
        raise LoaderError(path, "Path is not a file.")

    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise LoaderError(path, "Could not read UTF-8 text.") from exc
    except OSError as exc:
        raise LoaderError(path, f"Could not read file: {exc}") from exc


def _parse_yaml(content: str, path: Path) -> object:
    try:
        data: object = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise LoaderError(path, f"Could not parse YAML: {exc}") from exc
    return data


def _parse_json(content: str, path: Path) -> object:
    try:
        data: object = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LoaderError(path, f"Could not parse JSON: {exc}") from exc
    return data


def _infer_markdown_title(content: str) -> str | None:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            return title or None
    return None


def _format_validation_error(exc: ValidationError) -> str:
    messages: list[str] = []
    for error in exc.errors():
        loc = _format_error_location(error["loc"])
        message = str(error["msg"])
        messages.append(f"{loc}: {message}" if loc else message)
    return "; ".join(messages)


def _format_error_location(loc: tuple[int | str, ...]) -> str:
    return ".".join(str(part) for part in loc)


__all__ = ["LoaderError", "load_draft", "load_evidence_bundle"]
