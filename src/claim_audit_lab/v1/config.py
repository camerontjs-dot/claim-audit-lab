"""Default-config loading + rules-file materialization for CAL v1.

The operational defaults (pinned model revisions, ``top_k``, aggregation) ship
as package data at ``claim_audit_lab/v1/configs/v1-default.yaml``. The *verdict
thresholds* ship separately in the versioned rules file
``claim_audit_lab/v1/configs/cal-rules-v1.5.0.yaml`` — the single authored
source of truth for any number that decides a verdict.

:func:`load_default_audit_config` composes the two: it reads the operational
defaults, materializes the thresholds from the rules file, and pins the rules
file's SHA-256 as ``AuditConfig.rules_file_sha``. Because the thresholds are
never authored in two places they cannot drift; :func:`verify_rules_consistency`
re-checks an ``AuditConfig`` against the shipped rules file and fails loudly if
they ever diverge.

See DECISIONS.md § 2026-06-21 § 6 and § 9, and ``plans/adr-v1-rule-order.md``.
"""

from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from pathlib import Path

import yaml

from claim_audit_lab.contracts.serialization import hash_text
from claim_audit_lab.v1.models import AuditConfig

DEFAULT_CONFIG_RESOURCE = "v1-default.yaml"
RULES_FILE_RESOURCE = "cal-rules-v1.5.0.yaml"

_CONFIGS_PACKAGE = "claim_audit_lab.v1.configs"

# Verdict-deciding thresholds materialized from the rules file into AuditConfig.
# v1-default.yaml deliberately does NOT author these.
_MATERIALIZED_THRESHOLDS = (
    "retrieval_floor",
    "supported_threshold",
    "contradicted_threshold",
    "numeric_tolerance",
    "approx_numeric_tolerance",
)


class RulesConsistencyError(ValueError):
    """An ``AuditConfig`` disagrees with the rules file it pins via ``rules_file_sha``."""


def _read_resource_bytes(resource_name: str) -> bytes:
    return files(_CONFIGS_PACKAGE).joinpath(resource_name).read_bytes()


def load_rules_file() -> tuple[dict[str, object], str]:
    """Return the parsed rules file and its SHA-256 (hex, over the raw bytes)."""
    raw = _read_resource_bytes(RULES_FILE_RESOURCE)
    payload: dict[str, object] = yaml.safe_load(raw.decode("utf-8"))
    return payload, hashlib.sha256(raw).hexdigest()


def load_default_audit_config() -> AuditConfig:
    """Return the pinned v1 default :class:`AuditConfig`.

    Composes the operational defaults (``v1-default.yaml``) with the verdict
    thresholds materialized from ``cal-rules-v1.5.0.yaml``, pinning the rules
    file's SHA as ``rules_file_sha``. Works identically from an editable
    checkout and an installed wheel via :mod:`importlib.resources`.
    """
    operational: dict[str, object] = yaml.safe_load(
        _read_resource_bytes(DEFAULT_CONFIG_RESOURCE).decode("utf-8")
    )
    return _materialize_audit_config(operational)


def load_audit_config(path: Path) -> AuditConfig:
    """Return an :class:`AuditConfig` from an operational-defaults YAML at ``path``.

    Mirrors :func:`load_default_audit_config` but reads the operational knobs
    (``top_k``, ``aggregation``, model revisions) from ``path`` instead of the
    packaged default. The verdict thresholds and ``rules_file_sha`` are still
    materialized from the shipped ``cal-rules-v1.5.0.yaml`` — the rules file is
    the single source of truth for any verdict-deciding number, never the per-run
    config — and :func:`verify_rules_consistency` then guards the result. This is
    the loader the ``calibrate`` command uses for its ``--config`` file.
    """
    try:
        operational = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"malformed audit_config YAML at {path}: {exc}") from exc
    if not isinstance(operational, dict):
        raise ValueError(f"audit_config YAML must be a mapping, got {type(operational).__name__}")
    config = _materialize_audit_config(operational)
    verify_rules_consistency(config)
    return config


def _materialize_audit_config(operational: dict[str, object]) -> AuditConfig:
    """Compose operational defaults with rules-file thresholds into an ``AuditConfig``."""
    rules, rules_sha = load_rules_file()
    thresholds = {key: rules[key] for key in _MATERIALIZED_THRESHOLDS}
    return AuditConfig.model_validate({**operational, **thresholds, "rules_file_sha": rules_sha})


def verify_rules_consistency(config: AuditConfig) -> None:
    """Raise :class:`RulesConsistencyError` if ``config`` has drifted from the rules file.

    Checks that the config pins the current rules-file SHA *and* that every
    materialized threshold matches the rules file. This is the integrity guard
    that makes "thresholds live in the rules file, materialized into the config"
    safe: a hand-edited threshold or a stale SHA pin fails loudly instead of
    silently auditing with the wrong numbers.
    """
    rules, current_sha = load_rules_file()
    if config.rules_file_sha != current_sha:
        raise RulesConsistencyError(
            f"AuditConfig pins rules_file_sha {config.rules_file_sha!r} but the "
            f"shipped rules file hashes to {current_sha!r}"
        )
    for key in _MATERIALIZED_THRESHOLDS:
        materialized = getattr(config, key)
        if materialized != rules[key]:
            raise RulesConsistencyError(
                f"AuditConfig.{key}={materialized!r} disagrees with the rules "
                f"file value {rules[key]!r}"
            )


def hash_audit_config(config: AuditConfig) -> str:
    """Return a deterministic ``sha256:`` digest over an :class:`AuditConfig`.

    The hash is taken over the config's canonical JSON — ``model_dump(mode="json")``
    serialized with sorted keys and no incidental whitespace — so it is stable
    across runs and independent of field declaration order. This is the value
    stamped into :attr:`claim_audit_lab.v1.models.AuditTrace.audit_config_hash`,
    which (given deterministic layers) makes the whole trace byte-reproducible.
    Reuses the contract layer's
    :func:`claim_audit_lab.contracts.serialization.hash_text` so the ``sha256:``
    convention matches the bundle-tree and audit-config-file hashes.
    """
    canonical = json.dumps(
        config.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hash_text(canonical)


__all__ = [
    "DEFAULT_CONFIG_RESOURCE",
    "RULES_FILE_RESOURCE",
    "RulesConsistencyError",
    "hash_audit_config",
    "load_audit_config",
    "load_default_audit_config",
    "load_rules_file",
    "verify_rules_consistency",
]
