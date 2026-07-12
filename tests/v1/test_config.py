"""Tests for the v1 ``AuditConfig`` loader + rules-file materialization.

The verdict thresholds are the single source of truth in ``cal-rules-v1.5.0.yaml``
and are materialized into ``AuditConfig`` at load; ``v1-default.yaml`` carries
only operational settings. These tests pin that wiring and the consistency guard
so any drift between the rules file, the operational config, and the model is
caught immediately.
"""

from __future__ import annotations

import hashlib
from importlib.resources import files

import pytest
import yaml

from claim_audit_lab.v1 import config, load_default_audit_config
from claim_audit_lab.v1.config import (
    RulesConsistencyError,
    hash_audit_config,
    load_rules_file,
    verify_rules_consistency,
)
from claim_audit_lab.v1.models import AuditConfig

_EXPECTED_RETRIEVER_SHA = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
_EXPECTED_ENTAILER_SHA = "6f5cf0a2b59cabb106aca4c287eed12e357e90eb"


def test_load_default_audit_config_returns_audit_config() -> None:
    assert isinstance(load_default_audit_config(), AuditConfig)


def test_default_config_pins_resolved_hf_revisions() -> None:
    cfg = load_default_audit_config()
    assert cfg.retriever.model_id == "sentence-transformers/all-MiniLM-L6-v2"
    assert cfg.retriever.hf_revision_sha == _EXPECTED_RETRIEVER_SHA
    assert cfg.entailer.model_id == "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
    assert cfg.entailer.hf_revision_sha == _EXPECTED_ENTAILER_SHA


def test_operational_defaults_load() -> None:
    cfg = load_default_audit_config()
    assert cfg.top_k == 5
    assert cfg.aggregation == "max_entailment"


def test_thresholds_are_materialized_from_rules_file() -> None:
    rules, _ = load_rules_file()
    cfg = load_default_audit_config()
    assert rules["retrieval_floor"] == 0.40
    assert rules["supported_threshold"] == 0.70
    assert rules["contradicted_threshold"] == 0.70
    assert rules["numeric_tolerance"] == 0.0
    assert cfg.retrieval_floor == 0.40
    assert cfg.supported_threshold == 0.70
    assert cfg.contradicted_threshold == 0.70
    assert cfg.numeric_tolerance == 0.0


def test_operational_yaml_does_not_author_thresholds() -> None:
    """Single-source-of-truth invariant: thresholds live only in the rules file."""
    payload = yaml.safe_load(
        files("claim_audit_lab.v1.configs")
        .joinpath(config.DEFAULT_CONFIG_RESOURCE)
        .read_text(encoding="utf-8")
    )
    for key in (
        "retrieval_floor",
        "supported_threshold",
        "contradicted_threshold",
        "numeric_tolerance",
    ):
        assert key not in payload


def test_rules_file_sha_is_pinned_and_stable() -> None:
    _, sha = load_rules_file()
    raw = files("claim_audit_lab.v1.configs").joinpath(config.RULES_FILE_RESOURCE).read_bytes()
    assert sha == hashlib.sha256(raw).hexdigest()
    assert load_default_audit_config().rules_file_sha == sha
    assert load_default_audit_config().rules_file_sha == load_default_audit_config().rules_file_sha


def test_default_config_round_trips_through_json() -> None:
    """The loaded config must serialize and re-validate byte-equivalently."""
    cfg = load_default_audit_config()
    rehydrated = AuditConfig.model_validate_json(cfg.model_dump_json())
    assert rehydrated == cfg


def test_verify_rules_consistency_passes_for_default() -> None:
    verify_rules_consistency(load_default_audit_config())  # must not raise


def test_verify_rules_consistency_rejects_tampered_threshold() -> None:
    tampered = load_default_audit_config().model_copy(update={"supported_threshold": 0.99})
    with pytest.raises(RulesConsistencyError):
        verify_rules_consistency(tampered)


def test_verify_rules_consistency_rejects_stale_sha() -> None:
    stale = load_default_audit_config().model_copy(update={"rules_file_sha": "0" * 64})
    with pytest.raises(RulesConsistencyError):
        verify_rules_consistency(stale)


def test_hash_audit_config_is_prefixed_and_deterministic() -> None:
    cfg = load_default_audit_config()
    digest = hash_audit_config(cfg)
    assert digest.startswith("sha256:")
    assert digest == hash_audit_config(cfg)
    # Stable across independent loads of the same pinned defaults — the property
    # AuditTrace.audit_config_hash relies on for byte-reproducible traces.
    assert digest == hash_audit_config(load_default_audit_config())


def test_hash_audit_config_changes_with_content() -> None:
    cfg = load_default_audit_config()
    bumped = cfg.model_copy(update={"supported_threshold": 0.99})
    assert hash_audit_config(bumped) != hash_audit_config(cfg)


def test_hash_audit_config_is_yaml_field_order_and_whitespace_invariant() -> None:
    """Phase-2 § Unit 3 doc parity: two configs that differ only in source YAML
    field order or whitespace must hash identically.

    The canonicalization sorts keys, so order in the source representation cannot
    leak into the digest; this test asserts that property at the YAML boundary
    (the form an apparatus consumer actually authors), not just via ``model_copy``.
    """
    cfg = load_default_audit_config()
    payload = cfg.model_dump(mode="json")

    # Alphabetical top-level field order, no extra whitespace.
    ordered_yaml = yaml.safe_dump(payload, sort_keys=True, default_flow_style=False)
    # Same fields, declaration (non-alphabetical) order, plus a leading comment
    # and trailing blank lines — YAML the canonicalization must treat identically.
    scrambled_yaml = (
        "# operator-authored config\n\n"
        + yaml.safe_dump(payload, sort_keys=False, default_flow_style=False)
        + "\n\n   \n"
    )
    assert ordered_yaml != scrambled_yaml  # the inputs really do differ on the wire

    from_ordered = AuditConfig.model_validate(yaml.safe_load(ordered_yaml))
    from_scrambled = AuditConfig.model_validate(yaml.safe_load(scrambled_yaml))

    assert hash_audit_config(from_ordered) == hash_audit_config(from_scrambled)
    assert hash_audit_config(from_ordered) == hash_audit_config(cfg)
