"""Research CLI for bounded CAL V1 target authoring and conformance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from claim_audit_lab.contracts.bundle_loader import BundleIntegrityError
from claim_audit_lab.contracts.factual_context import FactualContextIntakeError
from claim_audit_lab.production_v1.bundle_input import BundleTargetValidationError
from claim_audit_lab.production_v1.targeting import (
    TargetAuthoringError,
    TargetConformanceError,
    author_target_from_bundle,
    canonical_target_bytes,
    validate_target_conformance,
    write_target_file,
)

app = typer.Typer(
    help=(
        "Research surface for deterministic CAL V1 target authoring/conformance. "
        "It does not change run-bundle semantics."
    ),
    no_args_is_help=True,
    rich_markup_mode=None,
)


@app.command(name="author")
def author(
    bundle_dir: Annotated[
        Path,
        typer.Argument(help="Released Contract B 1.2 bundle directory.", metavar="BUNDLE_DIR"),
    ],
    claim_id: Annotated[
        str,
        typer.Argument(help="Exact Contract B claim_id to author.", metavar="CLAIM_ID"),
    ],
    out: Annotated[
        Path | None,
        typer.Option(
            "--out",
            help="Write a new target file. Existing paths are refused.",
            metavar="TARGET.json",
        ),
    ] = None,
) -> None:
    """Author one canonical typed target from exact Contract B claim text."""
    try:
        target = author_target_from_bundle(bundle_dir, claim_id)
        if out is None:
            typer.echo(canonical_target_bytes(target).decode("utf-8"), nl=False)
        else:
            digest = write_target_file(out, target)
            typer.echo(json.dumps({"target": str(out), "sha256": digest}, sort_keys=True))
    except (BundleIntegrityError, FactualContextIntakeError, TargetAuthoringError) as exc:
        typer.echo(f"author rejected: {exc}", err=True)
        raise typer.Exit(code=2) from exc


@app.command(name="conform")
def conform(
    bundle_dir: Annotated[
        Path,
        typer.Argument(help="Released Contract B 1.2 bundle directory.", metavar="BUNDLE_DIR"),
    ],
    target: Annotated[
        Path,
        typer.Argument(help="Typed CAL target JSON.", metavar="TARGET.json"),
    ],
) -> None:
    """Validate structural binding and exact supported-family target conformance."""
    try:
        receipt = validate_target_conformance(bundle_dir, target)
    except (
        BundleIntegrityError,
        FactualContextIntakeError,
        BundleTargetValidationError,
        TargetAuthoringError,
        TargetConformanceError,
    ) as exc:
        typer.echo(f"conform rejected: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    typer.echo(json.dumps(receipt, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    app()
