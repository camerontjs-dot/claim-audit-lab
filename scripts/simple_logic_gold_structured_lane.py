"""Assemble and later run the preregistered E3 Simple Logic Gold structured lane.

This module intentionally imports no default model wrapper.  It validates the
frozen and preregistered source contracts, constructs explicit requests and
metamorphic variants, and accepts an injected atomic auditor for deterministic
tests or a separately authorized real-model invocation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

from claim_audit_lab.v1.config import hash_audit_config, load_default_audit_config
from claim_audit_lab.v1.explicit_claims import (
    AtomProvenance,
    ExplicitClaimAtom,
    ExplicitClaimRequest,
    ExplicitClaimTrace,
    hash_explicit_claim_request,
    serialize_explicit_claim_trace,
)
from claim_audit_lab.v1.models import Passage

_FREEZE_SCHEMA = "simple-logic-gold-frozen-dev-v0.1"
_FREEZE_STATUS = "frozen_approved_dev_not_validation_or_gate_evidence"
_FREEZE_IDENTIFIER = "simple-logic-gold-v0.1-frozen-rev01-2026-07-15"
_FREEZE_SHA256 = "sha256:cc78b39075d25e331d5905d065870b5382bfdefe1a384f548837a1fd790be1f1"
_STRUCTURE_SCHEMA = "simple-logic-gold-explicit-structure-v0.1"
_VARIANTS_SCHEMA = "simple-logic-gold-wording-variants-v0.1"
_RELATIONS = {"supports", "refutes", "insufficient", "retrieval_gap"}
_PARENT_VERDICTS = {
    "supported",
    "contradicted",
    "partially_supported",
    "not_checkable",
    "pending",
}
_IRRELEVANT_PASSAGE_ID = "metamorphic-irrelevant-01"
_IRRELEVANT_PASSAGE_TEXT = "The blue notebook is on shelf seven."
_FINITE_CONSTRUCTION: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {
    "SLG-04": (
        "Every listed valve passed inspection.",
        (
            "Valve V1 passed inspection.",
            "Valve V2 passed inspection.",
            "Valve V3 passed inspection.",
        ),
        ("supports", "supports", "supports"),
    ),
    "SLG-05": (
        "Every listed valve passed inspection.",
        (
            "Valve V1 passed inspection.",
            "Valve V2 passed inspection.",
            "Valve V3 passed inspection.",
        ),
        ("supports", "refutes", "supports"),
    ),
}
_EXPECTED_WORDING_VARIANTS = (
    ("SLG-01", "SLG-01-a1", "SLG-01-a1", "Drawer A contains the brass key.", "supports"),
    (
        "SLG-02",
        "SLG-02-a1",
        "SLG-02-a1",
        "The brass key is located in drawer A.",
        "refutes",
    ),
    (
        "SLG-03",
        "SLG-03-a1",
        "SLG-03-a1",
        "The brass key was put back before noon.",
        "insufficient",
    ),
)


def _sha256_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _require_mapping(value: object, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a mapping")
    return value


def _require_list(value: object, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{context} must be a list")
    return value


def _require_text(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context} must be a non-empty string")
    return value


def _require_exact_keys(value: dict[str, Any], keys: set[str], context: str) -> None:
    if set(value) != keys:
        raise ValueError(f"{context} has an invalid key set")


def _load_yaml(path: Path, context: str) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
        loaded = yaml.safe_load(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"could not load {context}: {exc}") from exc
    return _require_mapping(loaded, context), _sha256_bytes(raw)


def _load_frozen(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
        loaded = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load frozen Simple Logic Gold: {exc}") from exc
    frozen = _require_mapping(loaded, "frozen artifact")
    raw_sha256 = _sha256_bytes(raw)
    if raw_sha256 != _FREEZE_SHA256:
        raise ValueError("frozen artifact raw SHA-256 does not match the preregistered binding")
    if frozen.get("schema_version") != _FREEZE_SCHEMA:
        raise ValueError("frozen artifact has an invalid schema_version")
    if frozen.get("status") != _FREEZE_STATUS:
        raise ValueError("frozen artifact has an invalid DEV-only status")
    if frozen.get("freeze_identifier") != _FREEZE_IDENTIFIER:
        raise ValueError("frozen artifact has an invalid freeze_identifier")
    cases = _require_list(frozen.get("frozen_cases"), "frozen_cases")
    if frozen.get("world_count") != 12 or len(cases) != 12:
        raise ValueError("frozen artifact must contain exactly 12 cases")
    case_ids: list[str] = []
    frozen_atoms = 0
    for case in cases:
        item = _require_mapping(case, "frozen case")
        case_id = _require_text(item.get("base_case_id"), "frozen base_case_id")
        case_ids.append(case_id)
        if item.get("operator") not in {"single", "all_of"}:
            raise ValueError(f"{case_id}: invalid frozen operator")
        _require_text(item.get("plain_claim"), f"{case_id}: plain_claim")
        _require_list(item.get("facts"), f"{case_id}: facts")
        atoms = _require_list(item.get("atoms"), f"{case_id}: atoms")
        if not atoms:
            raise ValueError(f"{case_id}: atoms must be non-empty")
        frozen_atoms += len(atoms)
        if item.get("parent_verdict") not in _PARENT_VERDICTS:
            raise ValueError(f"{case_id}: invalid frozen parent verdict")
        for atom in atoms:
            atom_value = _require_mapping(atom, f"{case_id}: frozen atom")
            _require_text(atom_value.get("atom_id"), f"{case_id}: frozen atom_id")
            _require_text(atom_value.get("claim"), f"{case_id}: frozen atom claim")
            if atom_value.get("relation") not in _RELATIONS:
                raise ValueError(f"{case_id}: invalid frozen atom relation")
    if case_ids != [f"SLG-{number:02d}" for number in range(1, 13)]:
        raise ValueError("frozen artifact case order is not the preregistered order")
    if frozen_atoms != 17:
        raise ValueError("frozen artifact must contain exactly 17 semantic relation targets")
    return frozen, raw_sha256


@dataclass(frozen=True)
class AssembledCase:
    base_case_id: str
    mode: Literal["inherit_frozen", "explicit_finite_all_of"]
    frozen_case: dict[str, Any]
    request: ExplicitClaimRequest
    runtime_expectations: tuple[dict[str, str], ...]
    frozen_target_routes: tuple[dict[str, str], ...]
    transformation: str = "baseline"
    variant_id: str | None = None
    source_bindings: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class StructuredInputs:
    frozen: dict[str, Any]
    frozen_sha256: str
    structure: dict[str, Any]
    structure_sha256: str
    variants: dict[str, Any]
    variants_sha256: str


def _validate_structure(structure: dict[str, Any], frozen: dict[str, Any]) -> None:
    _require_exact_keys(
        structure, {"schema_version", "status", "freeze_binding", "cases"}, "structure"
    )
    if structure.get("schema_version") != _STRUCTURE_SCHEMA:
        raise ValueError("structure manifest has an invalid schema_version")
    if structure.get("status") != "preregistered_no_inference":
        raise ValueError("structure manifest has an invalid status")
    binding = _require_mapping(structure.get("freeze_binding"), "structure freeze_binding")
    _require_exact_keys(binding, {"freeze_identifier", "frozen_file_sha256"}, "structure binding")
    if binding != {"freeze_identifier": _FREEZE_IDENTIFIER, "frozen_file_sha256": _FREEZE_SHA256}:
        raise ValueError("structure manifest does not bind the accepted frozen artifact")
    entries = _require_list(structure.get("cases"), "structure cases")
    frozen_cases = _require_list(frozen.get("frozen_cases"), "frozen_cases")
    frozen_by_id = {case["base_case_id"]: case for case in frozen_cases}
    if [
        entry.get("base_case_id") if isinstance(entry, dict) else None for entry in entries
    ] != list(frozen_by_id):
        raise ValueError(
            "structure cases must cover frozen case IDs exactly once and in frozen order"
        )
    parent_ids: set[str] = set()
    runtime_ids: set[str] = set()
    finite_case_ids: set[str] = set()
    for entry in entries:
        value = _require_mapping(entry, "structure case")
        case_id = _require_text(value.get("base_case_id"), "structure base_case_id")
        mode = value.get("mode")
        parent_id = _require_text(value.get("parent_claim_id"), f"{case_id}: parent_claim_id")
        if parent_id in parent_ids:
            raise ValueError("structure parent_claim_id values must be unique")
        parent_ids.add(parent_id)
        atoms = _require_list(value.get("runtime_atoms"), f"{case_id}: runtime_atoms")
        if mode == "inherit_frozen":
            _require_exact_keys(
                value,
                {"base_case_id", "mode", "parent_claim_id", "runtime_atoms"},
                f"{case_id}: inherit_frozen entry",
            )
            frozen_atoms = frozen_by_id[case_id]["atoms"]
            if len(atoms) != len(frozen_atoms):
                raise ValueError(
                    f"{case_id}: inherited runtime atom count does not match frozen atoms"
                )
            for runtime, frozen_atom in zip(atoms, frozen_atoms, strict=True):
                runtime_value = _require_mapping(runtime, f"{case_id}: inherited runtime atom")
                _require_exact_keys(
                    runtime_value,
                    {"frozen_atom_id", "runtime_atom_id"},
                    f"{case_id}: inherited atom",
                )
                if runtime_value.get("frozen_atom_id") != frozen_atom["atom_id"]:
                    raise ValueError(f"{case_id}: inherited frozen atom order or identity drift")
                runtime_id = _require_text(
                    runtime_value.get("runtime_atom_id"), f"{case_id}: runtime_atom_id"
                )
                if runtime_id == parent_id or runtime_id in runtime_ids:
                    raise ValueError(
                        "runtime atom IDs must be globally unique and distinct from parents"
                    )
                runtime_ids.add(runtime_id)
        elif mode == "explicit_finite_all_of":
            finite_case_ids.add(case_id)
            _require_exact_keys(
                value,
                {
                    "base_case_id",
                    "mode",
                    "parent_claim_id",
                    "parent_claim_text",
                    "structured_parent_for_frozen_universal_target",
                    "operator",
                    "runtime_atoms",
                },
                f"{case_id}: explicit finite entry",
            )
            expected_parent_text, expected_atom_texts, expected_relations = (
                _FINITE_CONSTRUCTION.get(case_id, ("", (), ()))
            )
            if value.get("operator") != "all_of" or len(atoms) != 3:
                raise ValueError(
                    f"{case_id}: finite expansion must declare exactly three all_of atoms"
                )
            if (
                value.get("parent_claim_text") != expected_parent_text
                or value.get("parent_claim_text") != frozen_by_id[case_id]["plain_claim"]
            ):
                raise ValueError(
                    f"{case_id}: finite parent text must match the frozen parent exactly"
                )
            frozen_target = frozen_by_id[case_id]["atoms"]
            if (
                len(frozen_target) != 1
                or value.get("structured_parent_for_frozen_universal_target")
                != frozen_target[0]["atom_id"]
            ):
                raise ValueError(
                    f"{case_id}: finite route must bind its only frozen universal target"
                )
            declared_atom_texts: list[str] = []
            declared_relations: list[str] = []
            for runtime in atoms:
                runtime_value = _require_mapping(runtime, f"{case_id}: finite runtime atom")
                _require_exact_keys(
                    runtime_value,
                    {"runtime_atom_id", "claim_text", "expected_relation"},
                    f"{case_id}: finite atom",
                )
                runtime_id = _require_text(
                    runtime_value.get("runtime_atom_id"), f"{case_id}: runtime_atom_id"
                )
                declared_atom_texts.append(
                    _require_text(
                        runtime_value.get("claim_text"), f"{case_id}: finite atom claim_text"
                    )
                )
                if runtime_value.get("expected_relation") not in _RELATIONS - {"retrieval_gap"}:
                    raise ValueError(f"{case_id}: finite atom has an invalid expected relation")
                if runtime_id == parent_id or runtime_id in runtime_ids:
                    raise ValueError(
                        "runtime atom IDs must be globally unique and distinct from parents"
                    )
                runtime_ids.add(runtime_id)
                declared_relations.append(runtime_value["expected_relation"])
            if tuple(declared_atom_texts) != expected_atom_texts:
                raise ValueError(f"{case_id}: finite atom text roster differs from preregistration")
            if tuple(declared_relations) != expected_relations:
                raise ValueError(f"{case_id}: finite relation vector differs from preregistration")
        else:
            raise ValueError(f"{case_id}: unknown structure mode")
    if finite_case_ids != set(_FINITE_CONSTRUCTION):
        raise ValueError("explicit finite construction must be exactly the preregistered case set")
    if parent_ids & runtime_ids:
        raise ValueError("parent IDs and runtime atom IDs must be globally disjoint")


def _validate_variants(variants: dict[str, Any], inputs: StructuredInputs) -> None:
    _require_exact_keys(
        variants,
        {"schema_version", "status", "freeze_binding", "structure_manifest_sha256", "variants"},
        "wording variants",
    )
    if (
        variants.get("schema_version") != _VARIANTS_SCHEMA
        or variants.get("status") != "preregistered_no_inference"
    ):
        raise ValueError("wording variants have an invalid schema_version or status")
    binding = _require_mapping(variants.get("freeze_binding"), "wording variants freeze_binding")
    if binding != {"freeze_identifier": _FREEZE_IDENTIFIER, "frozen_file_sha256": _FREEZE_SHA256}:
        raise ValueError("wording variants do not bind the accepted frozen artifact")
    if variants.get("structure_manifest_sha256") != inputs.structure_sha256:
        raise ValueError("wording variants do not bind the loaded structure manifest bytes")
    frozen_cases = {case["base_case_id"]: case for case in inputs.frozen["frozen_cases"]}
    observed_variants: list[tuple[str, str, str, str, str]] = []
    seen_variant_ids: set[str] = set()
    for entry in _require_list(variants.get("variants"), "wording variants entries"):
        value = _require_mapping(entry, "wording variant")
        _require_exact_keys(
            value,
            {
                "base_case_id",
                "frozen_target_id",
                "variant_id",
                "parent_claim_text",
                "atom_claim_text",
                "expected_relation",
            },
            "wording variant entry",
        )
        case_id = _require_text(value.get("base_case_id"), "wording variant base_case_id")
        frozen_target_id = _require_text(
            value.get("frozen_target_id"), "wording variant frozen_target_id"
        )
        variant_id = _require_text(value.get("variant_id"), "wording variant variant_id")
        parent_text = _require_text(value.get("parent_claim_text"), "wording variant parent text")
        atom_text = _require_text(value.get("atom_claim_text"), "wording variant atom text")
        if parent_text != atom_text:
            raise ValueError("wording variants must update parent and atom text together")
        if case_id not in frozen_cases or len(frozen_cases[case_id]["atoms"]) != 1:
            raise ValueError("wording variants are permitted only for declared single frozen cases")
        frozen_atom = frozen_cases[case_id]["atoms"][0]
        if frozen_atom["atom_id"] != frozen_target_id or frozen_atom["relation"] != value.get(
            "expected_relation"
        ):
            raise ValueError("wording variant target binding or expected relation drift")
        if variant_id in seen_variant_ids:
            raise ValueError("wording variants must not duplicate variant_id values")
        seen_variant_ids.add(variant_id)
        observed_variants.append(
            (case_id, frozen_target_id, variant_id, parent_text, value["expected_relation"])
        )
    if tuple(observed_variants) != _EXPECTED_WORDING_VARIANTS:
        raise ValueError("wording variants must be exactly the preregistered ordered set")


def load_structured_inputs(
    frozen_path: Path, structure_path: Path, variants_path: Path
) -> StructuredInputs:
    """Load and fail-closed validate all preregistered E3 source artifacts."""
    frozen, frozen_sha256 = _load_frozen(frozen_path)
    structure, structure_sha256 = _load_yaml(structure_path, "structure manifest")
    _validate_structure(structure, frozen)
    variants, variants_sha256 = _load_yaml(variants_path, "wording variants manifest")
    inputs = StructuredInputs(
        frozen, frozen_sha256, structure, structure_sha256, variants, variants_sha256
    )
    _validate_variants(variants, inputs)
    return inputs


def _passages(frozen_case: dict[str, Any]) -> list[Passage]:
    return [
        Passage(
            passage_id=fact["fact_id"],
            text=fact["text"],
            source_meta={
                "direct_logic_gold": "true",
                "source_boundary": frozen_case["source_boundary"],
            },
        )
        for fact in frozen_case["facts"]
    ]


def assemble_baseline_requests(inputs: StructuredInputs) -> list[AssembledCase]:
    """Build the declared E2 requests without importing or invoking a model wrapper."""
    config = load_default_audit_config()
    frozen_by_id = {case["base_case_id"]: case for case in inputs.frozen["frozen_cases"]}
    assembled: list[AssembledCase] = []
    for declaration in inputs.structure["cases"]:
        case_id = declaration["base_case_id"]
        frozen_case = frozen_by_id[case_id]
        mode = declaration["mode"]
        provenance_sha = (
            inputs.frozen_sha256 if mode == "inherit_frozen" else inputs.structure_sha256
        )
        provenance_ref = (
            "frozen-simple-logic-gold" if mode == "inherit_frozen" else "explicit-structure-v0.1"
        )
        if mode == "inherit_frozen":
            atoms = [
                ExplicitClaimAtom(
                    atom_id=item["runtime_atom_id"],
                    claim_text=frozen_atom["claim"],
                    provenance=AtomProvenance(
                        origin="source_contract",
                        reference_id=provenance_ref,
                        reference_sha256=provenance_sha,
                    ),
                )
                for item, frozen_atom in zip(
                    declaration["runtime_atoms"], frozen_case["atoms"], strict=True
                )
            ]
            expectations = tuple(
                {
                    "runtime_atom_id": item["runtime_atom_id"],
                    "expected_relation": frozen_atom["relation"],
                }
                for item, frozen_atom in zip(
                    declaration["runtime_atoms"], frozen_case["atoms"], strict=True
                )
            )
            routes = tuple(
                {
                    "frozen_target_id": frozen_atom["atom_id"],
                    "route": "runtime_atom",
                    "runtime_atom_id": item["runtime_atom_id"],
                }
                for item, frozen_atom in zip(
                    declaration["runtime_atoms"], frozen_case["atoms"], strict=True
                )
            )
            parent_text = frozen_case["plain_claim"]
            operator = frozen_case["operator"]
        else:
            atoms = [
                ExplicitClaimAtom(
                    atom_id=item["runtime_atom_id"],
                    claim_text=item["claim_text"],
                    provenance=AtomProvenance(
                        origin="source_contract",
                        reference_id=provenance_ref,
                        reference_sha256=provenance_sha,
                    ),
                )
                for item in declaration["runtime_atoms"]
            ]
            expectations = tuple(
                {
                    "runtime_atom_id": item["runtime_atom_id"],
                    "expected_relation": item["expected_relation"],
                }
                for item in declaration["runtime_atoms"]
            )
            routes = (
                {
                    "frozen_target_id": declaration[
                        "structured_parent_for_frozen_universal_target"
                    ],
                    "route": "structured_parent_for_frozen_universal_target",
                    "runtime_atom_id": "",
                },
            )
            parent_text = declaration["parent_claim_text"]
            operator = declaration["operator"]
        assembled.append(
            AssembledCase(
                base_case_id=case_id,
                mode=mode,
                frozen_case=frozen_case,
                request=ExplicitClaimRequest(
                    parent_claim_id=declaration["parent_claim_id"],
                    parent_claim_text=parent_text,
                    operator=operator,
                    atoms=atoms,
                    passages=_passages(frozen_case),
                    audit_config=config,
                ),
                runtime_expectations=expectations,
                frozen_target_routes=routes,
                source_bindings=(
                    ("frozen_file_sha256", inputs.frozen_sha256),
                    ("structure_manifest_sha256", inputs.structure_sha256),
                    ("wording_variants_manifest_sha256", inputs.variants_sha256),
                ),
            )
        )
    _assert_denominators(assembled, inputs.frozen)
    return assembled


def _assert_denominators(cases: list[AssembledCase], frozen: dict[str, Any]) -> None:
    frozen_targets = [atom for case in frozen["frozen_cases"] for atom in case["atoms"]]
    comparable_targets = [atom for atom in frozen_targets if atom["relation"] != "retrieval_gap"]
    comparable_parents = [
        case
        for case in frozen["frozen_cases"]
        if case["source_boundary"] != "named_missing_material"
    ]
    runtime_count = sum(len(case.request.atoms) for case in cases)
    if (
        len(frozen_targets),
        len(comparable_targets),
        len(cases),
        len(comparable_parents),
        runtime_count,
    ) != (17, 15, 12, 10, 21):
        raise ValueError(
            "preregistered E3 denominators do not match 17/15 frozen targets, "
            "21 runtime atoms, and 12/10 parents"
        )


def _validated_atom(atom: ExplicitClaimAtom) -> ExplicitClaimAtom:
    """Revalidate a changed atom because ``model_copy(update=...)`` skips validation."""
    return ExplicitClaimAtom.model_validate(atom.model_dump(mode="python"))


def _validated_request(request: ExplicitClaimRequest) -> ExplicitClaimRequest:
    """Revalidate transformed request data against E2's strict public contract."""
    return ExplicitClaimRequest.model_validate(request.model_dump(mode="python"))


def assemble_stable_id_renaming(
    cases: list[AssembledCase], prefix: str = "metamorphic-renamed-"
) -> list[AssembledCase]:
    """Construct the fixed stable-ID-renaming transform without changing text or evidence."""
    renamed: list[AssembledCase] = []
    for case in cases:
        passage_map = {
            passage.passage_id: f"{prefix}{passage.passage_id}" for passage in case.request.passages
        }
        request = _validated_request(
            case.request.model_copy(
                update={
                    "parent_claim_id": f"{prefix}{case.request.parent_claim_id}",
                    "atoms": [
                        _validated_atom(
                            atom.model_copy(update={"atom_id": f"{prefix}{atom.atom_id}"})
                        )
                        for atom in case.request.atoms
                    ],
                    "passages": [
                        passage.model_copy(update={"passage_id": passage_map[passage.passage_id]})
                        for passage in case.request.passages
                    ],
                }
            )
        )
        expectations = tuple(
            {
                "runtime_atom_id": f"{prefix}{item['runtime_atom_id']}",
                "expected_relation": item["expected_relation"],
            }
            for item in case.runtime_expectations
        )
        routes = tuple(
            {
                **route,
                "runtime_atom_id": f"{prefix}{route['runtime_atom_id']}"
                if route["runtime_atom_id"]
                else "",
            }
            for route in case.frozen_target_routes
        )
        renamed.append(
            AssembledCase(
                case.base_case_id,
                case.mode,
                case.frozen_case,
                request,
                expectations,
                routes,
                "stable_id_renaming",
                None,
                case.source_bindings,
            )
        )
    return renamed


def assemble_reversed_evidence(cases: list[AssembledCase]) -> list[AssembledCase]:
    """Construct the fixed evidence-order transform."""
    return [
        AssembledCase(
            case.base_case_id,
            case.mode,
            case.frozen_case,
            _validated_request(
                case.request.model_copy(update={"passages": list(reversed(case.request.passages))})
            ),
            case.runtime_expectations,
            case.frozen_target_routes,
            "reverse_evidence_order",
            None,
            case.source_bindings,
        )
        for case in cases
    ]


def assemble_irrelevant_evidence(cases: list[AssembledCase]) -> list[AssembledCase]:
    """Construct the fixed one-passage irrelevant-evidence transform."""
    transformed: list[AssembledCase] = []
    for case in cases:
        if any(passage.passage_id == _IRRELEVANT_PASSAGE_ID for passage in case.request.passages):
            raise ValueError("irrelevant passage ID collides with a frozen passage ID")
        extra = Passage(
            passage_id=_IRRELEVANT_PASSAGE_ID,
            text=_IRRELEVANT_PASSAGE_TEXT,
            source_meta={"metamorphic": "irrelevant"},
        )
        transformed.append(
            AssembledCase(
                case.base_case_id,
                case.mode,
                case.frozen_case,
                _validated_request(
                    case.request.model_copy(update={"passages": [*case.request.passages, extra]})
                ),
                case.runtime_expectations,
                case.frozen_target_routes,
                "irrelevant_evidence",
                None,
                case.source_bindings,
            )
        )
    return transformed


def assemble_wording_variants(
    cases: list[AssembledCase], inputs: StructuredInputs
) -> list[AssembledCase]:
    """Construct declared single-request wording variants with parent/atom identity preserved."""
    by_case = {case.base_case_id: case for case in cases}
    transformed: list[AssembledCase] = []
    for variant in inputs.variants["variants"]:
        case = by_case[variant["base_case_id"]]
        if case.request.operator != "single" or len(case.request.atoms) != 1:
            raise ValueError("wording variant did not resolve to one declared single request")
        atom = _validated_atom(
            case.request.atoms[0].model_copy(update={"claim_text": variant["atom_claim_text"]})
        )
        request = _validated_request(
            case.request.model_copy(
                update={"parent_claim_text": variant["parent_claim_text"], "atoms": [atom]}
            )
        )
        if request.parent_claim_text != request.atoms[0].claim_text:
            raise ValueError("wording variant violated the E2 single identity invariant")
        if case.runtime_expectations[0]["expected_relation"] != variant["expected_relation"]:
            raise ValueError("wording variant expected relation drift")
        transformed.append(
            AssembledCase(
                case.base_case_id,
                case.mode,
                case.frozen_case,
                request,
                case.runtime_expectations,
                case.frozen_target_routes,
                "wording_variant",
                variant["variant_id"],
                case.source_bindings,
            )
        )
    return transformed


def _map_support_verdict(verdict: str) -> str | None:
    return {
        "supported": "supports",
        "contradicted": "refutes",
        "not_checkable": "insufficient",
    }.get(verdict)


def run_structured_lane(
    cases: list[AssembledCase],
    explicit_runner: Callable[[ExplicitClaimRequest], ExplicitClaimTrace],
) -> dict[str, Any]:
    """Run assembled requests through the public explicit-request runner shape."""
    runtime_atoms: list[dict[str, Any]] = []
    frozen_targets: list[dict[str, Any]] = []
    parents: list[dict[str, Any]] = []
    for case in cases:
        trace = explicit_runner(case.request)
        if not isinstance(trace, ExplicitClaimTrace):
            raise TypeError("explicit runner must return ExplicitClaimTrace")
        if trace.request_sha256 != hash_explicit_claim_request(case.request):
            raise ValueError("explicit trace request_sha256 does not bind the supplied request")
        if (
            trace.parent_claim_id != case.request.parent_claim_id
            or trace.parent_claim_text != case.request.parent_claim_text
            or trace.operator != case.request.operator
        ):
            raise ValueError("explicit trace parent binding does not match the supplied request")
        if trace.audit_config_hash != hash_audit_config(case.request.audit_config):
            raise ValueError("explicit trace audit config does not match the supplied request")
        if len(trace.atom_audits) != len(case.request.atoms):
            raise ValueError("explicit trace atom count does not match the supplied request")
        for request_atom, trace_atom in zip(case.request.atoms, trace.atom_audits, strict=True):
            if (
                trace_atom.atom_id != request_atom.atom_id
                or trace_atom.claim_text != request_atom.claim_text
                or trace_atom.provenance != request_atom.provenance
            ):
                raise ValueError("explicit trace atom binding does not match the supplied request")
        serialized_trace = json.loads(serialize_explicit_claim_trace(trace))
        atom_by_id = {atom.atom_id: atom for atom in trace.atom_audits}
        for runtime_atom_position, expectation in enumerate(case.runtime_expectations, start=1):
            atom_trace = atom_by_id[expectation["runtime_atom_id"]]
            observed = _map_support_verdict(atom_trace.audit_trace.verdict.support_verdict)
            comparable = expectation["expected_relation"] != "retrieval_gap"
            runtime_atoms.append(
                {
                    "base_case_id": case.base_case_id,
                    "transformation": case.transformation,
                    "variant_id": case.variant_id,
                    "source_bindings": dict(case.source_bindings),
                    "runtime_atom_id": expectation["runtime_atom_id"],
                    "runtime_atom_position": runtime_atom_position,
                    "expected_relation": expectation["expected_relation"],
                    "observed_relation": observed,
                    "comparable": comparable,
                    "match": observed == expectation["expected_relation"] if comparable else None,
                    "provenance": atom_trace.provenance.model_dump(mode="json"),
                    "request_sha256": trace.request_sha256,
                    "trace": atom_trace.audit_trace.model_dump(mode="json"),
                }
            )
        for route in case.frozen_target_routes:
            frozen_atom = next(
                atom
                for atom in case.frozen_case["atoms"]
                if atom["atom_id"] == route["frozen_target_id"]
            )
            if route["route"] == "runtime_atom":
                observed = _map_support_verdict(
                    atom_by_id[route["runtime_atom_id"]].audit_trace.verdict.support_verdict
                )
            else:
                observed = _map_support_verdict(trace.verdict.support_verdict)
            comparable = frozen_atom["relation"] != "retrieval_gap"
            frozen_targets.append(
                {
                    "base_case_id": case.base_case_id,
                    "transformation": case.transformation,
                    "variant_id": case.variant_id,
                    "source_bindings": dict(case.source_bindings),
                    "frozen_target_id": frozen_atom["atom_id"],
                    "route": route["route"],
                    "expected_relation": frozen_atom["relation"],
                    "observed_relation": observed,
                    "comparable": comparable,
                    "match": observed == frozen_atom["relation"] if comparable else None,
                    "request_sha256": trace.request_sha256,
                }
            )
        parent_comparable = case.frozen_case["source_boundary"] != "named_missing_material"
        parents.append(
            {
                "base_case_id": case.base_case_id,
                "transformation": case.transformation,
                "variant_id": case.variant_id,
                "source_bindings": dict(case.source_bindings),
                "expected_parent_verdict": case.frozen_case["parent_verdict"],
                "observed_parent_verdict": trace.verdict.support_verdict,
                "comparable": parent_comparable,
                "match": trace.verdict.support_verdict == case.frozen_case["parent_verdict"]
                if parent_comparable
                else None,
                "request_sha256": trace.request_sha256,
                "explicit_trace": serialized_trace,
            }
        )
    summary = {
        "frozen_semantic_targets": len(frozen_targets),
        "comparable_frozen_semantic_targets": sum(
            record["comparable"] for record in frozen_targets
        ),
        "runtime_atoms": len(runtime_atoms),
        "comparable_runtime_atoms": sum(record["comparable"] for record in runtime_atoms),
        "frozen_parents": len(parents),
        "comparable_frozen_parents": sum(record["comparable"] for record in parents),
    }
    if len(cases) == 12 and summary != {
        "frozen_semantic_targets": 17,
        "comparable_frozen_semantic_targets": 15,
        "runtime_atoms": 21,
        "comparable_runtime_atoms": 19,
        "frozen_parents": 12,
        "comparable_frozen_parents": 10,
    }:
        raise ValueError("structured result did not preserve preregistered reporting denominators")
    return {
        "schema_version": "simple-logic-gold-structured-direct-run-v0.1",
        "label": "DEV diagnostic only; not validation, representative accuracy, or gate evidence",
        "frozen_semantic_targets": frozen_targets,
        "runtime_atoms": runtime_atoms,
        "frozen_parents": parents,
        "summary": summary,
    }


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _score_layer(
    records: list[dict[str, Any]],
    *,
    denominator: int,
    identity_fields: tuple[str, ...],
) -> dict[str, Any]:
    comparable = [record for record in records if record["comparable"]]
    if len(comparable) != denominator:
        raise ValueError("suite layer did not retain its preregistered comparable denominator")
    failures = [
        {
            **{field: record[field] for field in identity_fields},
            "expected": record.get("expected_relation", record.get("expected_parent_verdict")),
            "observed": record.get("observed_relation", record.get("observed_parent_verdict")),
        }
        for record in comparable
        if record["match"] is not True
    ]
    return {
        "denominator": denominator,
        "matching": denominator - len(failures),
        "failures": failures,
    }


def _invariance(
    baseline: dict[str, Any],
    transformed: dict[str, Any],
    *,
    layer: Literal["frozen_semantic_targets", "runtime_atoms", "frozen_parents"],
    denominator: int,
    identity_fields: tuple[str, ...],
    observed_field: str,
) -> dict[str, Any]:
    baseline_records = [record for record in baseline[layer] if record["comparable"]]
    transformed_records = [record for record in transformed[layer] if record["comparable"]]
    if len(baseline_records) != denominator or len(transformed_records) != denominator:
        raise ValueError(
            "metamorphic result did not retain its preregistered comparable denominator"
        )
    failures: list[dict[str, Any]] = []
    for baseline_record, transformed_record in zip(
        baseline_records, transformed_records, strict=True
    ):
        alignment = tuple(baseline_record[field] for field in identity_fields)
        transformed_alignment = tuple(transformed_record[field] for field in identity_fields)
        if alignment != transformed_alignment:
            raise ValueError("metamorphic records do not preserve their stable alignment identity")
        if baseline_record[observed_field] != transformed_record[observed_field]:
            failure = {
                **{field: baseline_record[field] for field in identity_fields},
                "baseline_observed": baseline_record[observed_field],
                "transformed_observed": transformed_record[observed_field],
            }
            if layer == "runtime_atoms":
                failure["baseline_runtime_atom_id"] = baseline_record["runtime_atom_id"]
                failure["transformed_runtime_atom_id"] = transformed_record["runtime_atom_id"]
            failures.append(failure)
    return {"denominator": denominator, "failures": failures}


def _invariance_report(baseline: dict[str, Any], transformed: dict[str, Any]) -> dict[str, Any]:
    return {
        "frozen_semantic_targets": _invariance(
            baseline,
            transformed,
            layer="frozen_semantic_targets",
            denominator=15,
            identity_fields=("base_case_id", "frozen_target_id"),
            observed_field="observed_relation",
        ),
        "runtime_atoms": _invariance(
            baseline,
            transformed,
            layer="runtime_atoms",
            denominator=19,
            identity_fields=("base_case_id", "runtime_atom_position", "expected_relation"),
            observed_field="observed_relation",
        ),
        "frozen_parents": _invariance(
            baseline,
            transformed,
            layer="frozen_parents",
            denominator=10,
            identity_fields=("base_case_id",),
            observed_field="observed_parent_verdict",
        ),
    }


def run_structured_suite(
    inputs: StructuredInputs,
    explicit_runner: Callable[[ExplicitClaimRequest], ExplicitClaimTrace],
) -> dict[str, Any]:
    """Run the complete preregistered E3 suite with an injected explicit runner."""
    baseline_cases = assemble_baseline_requests(inputs)
    baseline = run_structured_lane(baseline_cases, explicit_runner)
    baseline_rerun = run_structured_lane(baseline_cases, explicit_runner)
    baseline_text = _canonical_json(baseline)
    baseline_rerun_text = _canonical_json(baseline_rerun)
    transforms = {
        "stable_id_renaming": assemble_stable_id_renaming(baseline_cases),
        "reverse_evidence_order": assemble_reversed_evidence(baseline_cases),
        "irrelevant_evidence": assemble_irrelevant_evidence(baseline_cases),
    }
    transform_results = {
        name: run_structured_lane(cases, explicit_runner) for name, cases in transforms.items()
    }
    wording_result = run_structured_lane(
        assemble_wording_variants(baseline_cases, inputs), explicit_runner
    )
    return {
        "schema_version": "simple-logic-gold-structured-direct-suite-v0.1",
        "label": "DEV diagnostic only; not validation, representative accuracy, or gate evidence",
        "source_bindings": {
            "frozen_file_sha256": inputs.frozen_sha256,
            "structure_manifest_sha256": inputs.structure_sha256,
            "wording_variants_manifest_sha256": inputs.variants_sha256,
        },
        "baseline": baseline,
        "baseline_scores": {
            "frozen_semantic_targets": _score_layer(
                baseline["frozen_semantic_targets"],
                denominator=15,
                identity_fields=("base_case_id", "frozen_target_id"),
            ),
            "runtime_construction_atoms": _score_layer(
                baseline["runtime_atoms"],
                denominator=19,
                identity_fields=("base_case_id", "runtime_atom_id"),
            ),
            "frozen_parents": _score_layer(
                baseline["frozen_parents"],
                denominator=10,
                identity_fields=("base_case_id",),
            ),
        },
        "exact_baseline_rerun": {
            "serialized_byte_identical": baseline_text == baseline_rerun_text,
            "baseline_sha256": _sha256_bytes(baseline_text.encode("utf-8")),
            "rerun_sha256": _sha256_bytes(baseline_rerun_text.encode("utf-8")),
            "result": baseline_rerun,
        },
        "metamorphic": {
            name: {"result": result, "invariance": _invariance_report(baseline, result)}
            for name, result in transform_results.items()
        },
        "wording_variants": {
            "result": wording_result,
            "frozen_semantic_targets": _score_layer(
                wording_result["frozen_semantic_targets"],
                denominator=3,
                identity_fields=("base_case_id", "frozen_target_id", "variant_id"),
            ),
        },
    }


def suite_is_green(suite: dict[str, Any]) -> bool:
    """Return whether a preserved suite meets every preregistered E3 target."""
    scores = suite["baseline_scores"]
    if any(score["matching"] != score["denominator"] for score in scores.values()):
        return False
    if not suite["exact_baseline_rerun"]["serialized_byte_identical"]:
        return False
    for transform in suite["metamorphic"].values():
        if any(layer["failures"] for layer in transform["invariance"].values()):
            return False
    wording = suite["wording_variants"]["frozen_semantic_targets"]
    return wording["matching"] == wording["denominator"] == 3


def _write_absent_or_identical(path: Path, output: dict[str, Any]) -> None:
    text = json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise FileExistsError(
                f"refusing to overwrite non-identical structured-lane output: {path}"
            )
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen", type=Path, required=True)
    parser.add_argument("--structure", type=Path, required=True)
    parser.add_argument("--wording-variants", type=Path, required=True)
    args = parser.parse_args()
    inputs = load_structured_inputs(args.frozen, args.structure, args.wording_variants)
    cases = assemble_baseline_requests(inputs)
    transformations = {
        "stable_id_renaming": assemble_stable_id_renaming(cases),
        "reverse_evidence_order": assemble_reversed_evidence(cases),
        "irrelevant_evidence": assemble_irrelevant_evidence(cases),
        "wording_variants": assemble_wording_variants(cases, inputs),
    }
    print(
        json.dumps(
            {
                "baseline_cases": len(cases),
                "runtime_atoms": sum(len(case.request.atoms) for case in cases),
                "transformations": {name: len(value) for name, value in transformations.items()},
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    _main()
