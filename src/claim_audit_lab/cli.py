"""Command-line interface for Claim Audit Lab."""

from __future__ import annotations

import typer

app = typer.Typer(
    help="Audit whether draft claims are supported by supplied evidence.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Run the Claim Audit Lab command group."""


if __name__ == "__main__":
    app()
