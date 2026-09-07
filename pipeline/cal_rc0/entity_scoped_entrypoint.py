"""Entity-scoped entrypoint for the CAL Pipeline RC0 integration build.

RC0A established a replacement rule for ambiguous entity anchoring. The frozen
RC0 atom completer also uses its legacy span helper for measure, quantity, and
unit surfaces. This adapter applies the RC0A resolver only to the first two
lookups performed by the frozen completer (lhs and rhs entities), then delegates
all remaining lookups to the frozen RC0 helper.

This is an integration boundary, not a new scientific result. It deliberately
avoids treating the unpublished RC0B apparatus attempt as evidence.
"""
from __future__ import annotations

from types import ModuleType
from typing import Any, Callable

import run_pipeline as base


SpanResolver = Callable[[str, str], tuple[int, int] | None]


class _EntityScopedRuntime:
    """Proxy the frozen RC0 module while narrowing the RC0A replacement seam."""

    def __init__(self, module: ModuleType) -> None:
        object.__setattr__(self, "_module", module)
        object.__setattr__(self, "_entity_resolver", None)

    def __getattr__(self, name: str) -> Any:
        if name == "_unique_casefold_span":
            resolver = object.__getattribute__(self, "_entity_resolver")
            if resolver is not None:
                return resolver
        if name == "execute_rc0_case":
            return self._execute_rc0_case
        return getattr(object.__getattribute__(self, "_module"), name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_unique_casefold_span":
            object.__setattr__(self, "_entity_resolver", value)
            return
        setattr(object.__getattribute__(self, "_module"), name, value)

    def _execute_rc0_case(self, **kwargs: Any) -> dict[str, Any]:
        module = object.__getattribute__(self, "_module")
        resolver = object.__getattribute__(self, "_entity_resolver")
        if resolver is None:
            raise RuntimeError("RC0A entity resolver was not installed")

        frozen_complete = module.complete_strict_comparison_atom
        frozen_span = module._unique_casefold_span

        def adapted_complete(
            *, claim_id: str, evidence: Any, measurement: dict[str, Any]
        ) -> tuple[Any, str]:
            calls = 0

            def entity_then_frozen(text: str, surface: str) -> tuple[int, int] | None:
                nonlocal calls
                calls += 1
                if calls <= 2:
                    return resolver(text, surface)
                return frozen_span(text, surface)

            module._unique_casefold_span = entity_then_frozen
            try:
                return frozen_complete(
                    claim_id=claim_id,
                    evidence=evidence,
                    measurement=measurement,
                )
            finally:
                module._unique_casefold_span = frozen_span

        module.complete_strict_comparison_atom = adapted_complete
        try:
            return module.execute_rc0_case(**kwargs)
        finally:
            module.complete_strict_comparison_atom = frozen_complete
            module._unique_casefold_span = frozen_span


def _scoped_load_module(name: str, path: Any) -> Any:
    module = _ORIGINAL_LOAD_MODULE(name, path)
    if name == "cal_pipeline_rc0_runtime":
        return _EntityScopedRuntime(module)
    return module


_ORIGINAL_LOAD_MODULE = base.load_module
_ORIGINAL_EXECUTE = base.execute
base.load_module = _scoped_load_module


def _execute_with_boundary_receipt(args: Any) -> dict[str, Any]:
    receipt = _ORIGINAL_EXECUTE(args)
    cal = receipt["cal"]
    cal["span_resolver"] = "rc0a_entity_only_unique_exact_lexical_boundary"
    cal["entity_span_resolver"] = "rc0a_unique_exact_lexical_boundary"
    cal["non_entity_span_resolver"] = "frozen_rc0_unique_casefold_span"
    cal["entity_span_scope"] = ["lhs_entity", "rhs_entity"]
    return receipt


base.execute = _execute_with_boundary_receipt


if __name__ == "__main__":
    raise SystemExit(base.main())
