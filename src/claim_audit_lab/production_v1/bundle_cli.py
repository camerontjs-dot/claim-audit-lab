"""Dedicated operator CLI for the CAL V1 integration candidate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from claim_audit_lab.contracts.bundle_loader import BundleIntegrityError
from claim_audit_lab.contracts.factual_context import FactualContextIntakeError
from claim_audit_lab.production_v1.bundle_input import BundleTargetValidationError
from claim_audit_lab.production_v1.execution import (
    OutputSafetyError,
    inspect_record,
    run_contract_b_bundle,
    validate_contract_b_bundle,
)

app = typer.Typer(
    help="Run the frozen CAL V1 integration candidate against released Contract B 1.2.",
    no_args_is_help=True,
    rich_markup_mode=None,
)


@app.command(name="run-bundle")
def run_bundle(
    bundle_dir: Annotated[
        Path,
        typer.Argument(help="Released Contract B 1.2 bundle directory.", metavar="BUNDLE_DIR"),
    ],
    target: Annotated[
        Path,
        typer.Argument(help="Typed CAL proposition target JSON.", metavar="TARGET.json"),
    ],
    out_dir: Annotated[
        Path,
        typer.Option(
            "--out-dir",
            help="New or empty directory for the immutable native CAL run.",
            metavar="RUN_DIR",
        ),
    ],
) -> None:
    """Run one typed target against one exact Contract B 1.2 evidence world."""
    try:
        run_contract_b_bundle(bundle_dir, target, out_dir)
    except (
        BundleIntegrityError,
        FactualContextIntakeError,
        BundleTargetValidationError,
        OutputSafetyError,
    ) as exc:
        typer.echo(f"run-bundle rejected: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    except Exception as exc:
        typer.echo(f"run-bundle failed: {exc}", err=True)
        raise typer.Exit(code=70) from exc
    typer.echo(f"Wrote CAL V1 native run: {out_dir}")


@app.command(name="validate-bundle")
def validate_bundle(
    bundle_dir: Annotated[
        Path,
        typer.Argument(help="Released Contract B 1.2 bundle directory.", metavar="BUNDLE_DIR"),
    ],
    target: Annotated[
        Path,
        typer.Argument(help="Typed CAL proposition target JSON.", metavar="TARGET.json"),
    ],
) -> None:
    """Validate Contract B intake and target binding without running CAL semantics."""
    try:
        validate_contract_b_bundle(bundle_dir, target)
    except (BundleIntegrityError, FactualContextIntakeError, BundleTargetValidationError) as exc:
        typer.echo(f"validate-bundle rejected: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    typer.echo("VALID")


@app.command(name="inspect")
def inspect_candidate(
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Emit deterministic JSON runtime authority information."),
    ] = False,
) -> None:
    """Show the exact semantic and contract authority pinned by this candidate."""
    if not json_output:
        typer.echo("inspect requires --json", err=True)
        raise typer.Exit(code=2)
    typer.echo(json.dumps(inspect_record(), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    app()
