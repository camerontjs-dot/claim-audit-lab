"""CLI for the production-shaped CAL V1 parent-bound Contract C candidate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from claim_audit_lab.contracts.bundle_loader import BundleIntegrityError
from claim_audit_lab.contracts.factual_context import FactualContextIntakeError
from claim_audit_lab.production_v1.bundle_input import BundleTargetValidationError
from claim_audit_lab.production_v1.execution import OutputSafetyError
from claim_audit_lab.production_v1.parent_bound import (
    ParentBoundPipelineError,
    inspect_parent_bound_authority,
    run_parent_bound_pipeline,
)

app = typer.Typer(
    help=(
        "Run trusted Contract B 1.2 child targets through frozen CAL V1 parent "
        "recomposition and the exact frozen parent-bound Contract C authority."
    ),
    no_args_is_help=True,
    rich_markup_mode=None,
)


def _target_map(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ParentBoundPipelineError("--target must be PROPOSITION_ID=TARGET.json")
        proposition_id, raw_path = value.split("=", 1)
        proposition_id = proposition_id.strip()
        if not proposition_id or not raw_path.strip():
            raise ParentBoundPipelineError("--target must be PROPOSITION_ID=TARGET.json")
        if proposition_id in result:
            raise ParentBoundPipelineError(f"duplicate --target proposition id: {proposition_id}")
        result[proposition_id] = Path(raw_path)
    return result


@app.command(name="run")
def run_parent(
    contract_a: Annotated[
        Path,
        typer.Argument(
            help="Exact prevalidated Contract A object with declared all_of decomposition.",
            metavar="CONTRACT_A.json",
        ),
    ],
    bundle_dir: Annotated[
        Path,
        typer.Argument(
            help="Released Contract B 1.2 bundle directory shared by the child targets.",
            metavar="BUNDLE_DIR",
        ),
    ],
    targets: Annotated[
        list[str],
        typer.Option(
            "--target",
            help="Trusted child target binding as PROPOSITION_ID=TARGET.json. Repeat per child.",
            metavar="ID=TARGET.json",
        ),
    ],
    out_dir: Annotated[
        Path,
        typer.Option(
            "--out-dir",
            help="New or empty output directory.",
            metavar="RUN_DIR",
        ),
    ],
    contract_c_root: Annotated[
        Path,
        typer.Option(
            "--contract-c-root",
            help="Clean checkout at the exact frozen parent-bound Contract C commit.",
            metavar="DIR",
        ),
    ],
    rc2_root: Annotated[
        Path,
        typer.Option(
            "--rc2-root",
            help="Clean checkout at the exact Candidate A RC2 authority commit.",
            metavar="DIR",
        ),
    ],
    resolver_root: Annotated[
        Path,
        typer.Option(
            "--resolver-root",
            help="Clean checkout at the exact current-CAL resolver authority commit.",
            metavar="DIR",
        ),
    ],
) -> None:
    """Run the bounded B1.2 -> CAL children -> parent -> frozen Contract C path."""
    try:
        run_parent_bound_pipeline(
            contract_a_path=contract_a,
            bundle_dir=bundle_dir,
            child_targets=_target_map(targets),
            out_dir=out_dir,
            contract_c_root=contract_c_root,
            rc2_root=rc2_root,
            resolver_root=resolver_root,
        )
    except (
        BundleIntegrityError,
        FactualContextIntakeError,
        BundleTargetValidationError,
        OutputSafetyError,
        ParentBoundPipelineError,
        OSError,
        ValueError,
    ) as exc:
        typer.echo(f"parent-bound run rejected: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    except Exception as exc:
        typer.echo(f"parent-bound run failed: {exc}", err=True)
        raise typer.Exit(code=70) from exc
    typer.echo(f"Wrote CAL V1 parent-bound run: {out_dir}")


@app.command(name="inspect")
def inspect_parent(
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Emit deterministic JSON authority information."),
    ] = False,
) -> None:
    """Show exact frozen authorities required by this candidate."""
    if not json_output:
        typer.echo("inspect requires --json", err=True)
        raise typer.Exit(code=2)
    typer.echo(
        json.dumps(
            inspect_parent_bound_authority(),
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    app()
