"""Surgical research adapter for replacing only RC0 entity-span lookup calls."""
from __future__ import annotations

from typing import Any, Callable

SpanResolver = Callable[[str, str], tuple[int, int] | None]


def complete_atom_with_entity_resolver(
    rc0: Any,
    resolver: SpanResolver,
    *,
    claim_id: str,
    evidence: Any,
    measurement: dict[str, Any],
) -> tuple[Any, str]:
    """Call the exact frozen completer with only its first two span lookups replaced.

    The frozen RC0 implementation performs LHS then RHS lookup before any
    measure/quantity/unit lookups. RC0B pins the exact runtime blob, so this
    call-order interception is intentionally version-specific and research-only.
    """
    frozen_complete = rc0.complete_strict_comparison_atom
    frozen_span = rc0._unique_casefold_span
    calls = 0

    def scoped_span(text: str, surface: str) -> tuple[int, int] | None:
        nonlocal calls
        calls += 1
        if calls <= 2:
            return resolver(text, surface)
        return frozen_span(text, surface)

    rc0._unique_casefold_span = scoped_span
    try:
        return frozen_complete(claim_id=claim_id, evidence=evidence, measurement=measurement)
    finally:
        rc0._unique_casefold_span = frozen_span


def execute_with_entity_resolver(rc0: Any, resolver: SpanResolver, **kwargs: Any) -> dict[str, Any]:
    """Execute exact RC0 while substituting only the atom-completion entry seam."""
    frozen_complete = rc0.complete_strict_comparison_atom

    def adapted_complete(*, claim_id: str, evidence: Any, measurement: dict[str, Any]) -> tuple[Any, str]:
        return complete_atom_with_entity_resolver(
            rc0,
            resolver,
            claim_id=claim_id,
            evidence=evidence,
            measurement=measurement,
        )

    rc0.complete_strict_comparison_atom = adapted_complete
    try:
        return rc0.execute_rc0_case(**kwargs)
    finally:
        rc0.complete_strict_comparison_atom = frozen_complete
