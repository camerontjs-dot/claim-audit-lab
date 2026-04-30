"""Tests for draft and evidence loading."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from claim_audit_lab.loader import LoaderError, load_draft, load_evidence_bundle

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = PROJECT_ROOT / "examples"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"


def test_load_markdown_draft_uses_file_stem_and_first_heading() -> None:
    """Markdown drafts load into typed draft documents."""
    draft_path = EXAMPLES_ROOT / "drafts" / "ai-research-note.md"

    draft = load_draft(draft_path)

    assert draft.id == "ai-research-note"
    assert draft.title == "AI research note"
    assert draft.path == str(draft_path)
    assert "The intervention clearly eliminates unsupported claims" in draft.content


def test_load_product_readme_draft() -> None:
    """The second fictional Markdown draft loads for Phase 4 planning."""
    draft_path = EXAMPLES_ROOT / "drafts" / "product-readme-note.md"

    draft = load_draft(draft_path)

    assert draft.id == "product-readme-note"
    assert draft.title == "Meridian Notes README"
    assert "Meridian Notes can generate traceable audit summaries" in draft.content


def test_load_plain_text_draft_allows_explicit_metadata() -> None:
    """Plain text drafts can receive explicit ID and title metadata."""
    draft_path = FIXTURE_ROOT / "drafts" / "plain-note.txt"

    draft = load_draft(draft_path, document_id="plain-demo", title="Plain demo")

    assert draft.id == "plain-demo"
    assert draft.title == "Plain demo"
    assert "Unsupported claims fell from 18 outputs to 11 outputs" in draft.content


def test_load_yaml_evidence_bundle() -> None:
    """YAML evidence bundles load into typed models."""
    bundle_path = EXAMPLES_ROOT / "evidence" / "ai-research-evidence.yml"

    bundle = load_evidence_bundle(bundle_path)

    assert bundle.sources[0].id == "source-001"
    assert bundle.sources[0].excerpts[0].id == "excerpt-001"


def test_load_product_readme_evidence_bundle() -> None:
    """The second fictional evidence bundle loads with dated source metadata."""
    bundle_path = EXAMPLES_ROOT / "evidence" / "product-readme-evidence.yml"

    bundle = load_evidence_bundle(bundle_path)

    assert [source.id for source in bundle.sources] == [
        "source-product-001",
        "source-product-002",
    ]
    assert bundle.sources[0].source_type == "test_output"
    assert bundle.sources[0].reliability == "medium"
    assert bundle.sources[0].date is not None
    assert bundle.sources[0].date.isoformat() == "2024-02-15"
    assert bundle.sources[1].source_type == "documentation"
    assert bundle.sources[1].reliability == "high"
    assert [excerpt.id for excerpt in bundle.sources[1].excerpts] == [
        "excerpt-product-003",
        "excerpt-product-004",
    ]


def test_load_json_evidence_bundle() -> None:
    """JSON evidence bundles load into typed models."""
    bundle_path = FIXTURE_ROOT / "evidence" / "ai-research-evidence.json"

    bundle = load_evidence_bundle(bundle_path)

    assert bundle.sources[0].id == "source-json-001"
    assert bundle.sources[0].excerpts[0].id == "excerpt-json-001"


def test_load_empty_evidence_bundle() -> None:
    """Empty but valid evidence bundles load for later audit warnings."""
    bundle_path = FIXTURE_ROOT / "evidence" / "empty-evidence.yml"

    bundle = load_evidence_bundle(bundle_path)

    assert bundle.sources == []


def test_malformed_yaml_raises_loader_error_with_path() -> None:
    """YAML parse errors are loader errors, not audit findings."""
    bundle_path = FIXTURE_ROOT / "evidence" / "malformed-evidence.yml"

    with pytest.raises(LoaderError) as exc_info:
        load_evidence_bundle(bundle_path)

    message = str(exc_info.value)
    assert "malformed-evidence.yml" in message
    assert "Could not parse YAML" in message


def test_missing_required_evidence_fields_identify_bad_field() -> None:
    """Evidence validation errors identify the file and missing field."""
    bundle_path = FIXTURE_ROOT / "evidence" / "missing-required-field.yml"

    with pytest.raises(LoaderError) as exc_info:
        load_evidence_bundle(bundle_path)

    message = str(exc_info.value)
    assert "missing-required-field.yml" in message
    assert "sources.0.title" in message
    assert "Field required" in message


@pytest.mark.parametrize(
    "file_name,loader",
    [
        pytest.param("draft.docx", load_draft, id="unsupported_draft_type"),
        pytest.param("evidence.toml", load_evidence_bundle, id="unsupported_evidence_type"),
    ],
)
def test_unsupported_file_types_raise_loader_error(
    tmp_path: Path,
    file_name: str,
    loader: Callable[[Path], object],
) -> None:
    """Unsupported file extensions fail before parsing."""
    path = tmp_path / file_name
    path.write_text("placeholder", encoding="utf-8")

    with pytest.raises(LoaderError, match="Unsupported"):
        loader(path)


def test_missing_file_raises_loader_error_with_path(tmp_path: Path) -> None:
    """Missing input files produce a clear loader error."""
    missing_path = tmp_path / "missing.yml"

    with pytest.raises(LoaderError) as exc_info:
        load_evidence_bundle(missing_path)

    assert "missing.yml" in str(exc_info.value)
    assert "File does not exist" in str(exc_info.value)
