# ruff: noqa: E501 -- long provenance/error text is clearer as one contract statement.

"""Seal an assisted Gold Lite DEV export without weakening legacy complete mode.

The original Gold Lite validator intentionally treats ``needs_revision`` as
incomplete.  That remains correct for an unassisted completed review.  This
separate, versioned contract preserves an assisted export in which Cameron
completed every decomposition decision, documented two decomposition
escalations, and decided every atom under the approved parents.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.gold_lite_review import (
        GoldLiteManifest,
        ReviewExport,
        ReviewPacket,
        build_review_packet,
        load_manifest,
        load_review_export,
        load_review_packet,
        validate_review_export,
    )
except ModuleNotFoundError:  # Direct script execution.
    from gold_lite_review import (  # type: ignore[no-redef]
        GoldLiteManifest,
        ReviewExport,
        ReviewPacket,
        build_review_packet,
        load_manifest,
        load_review_export,
        load_review_packet,
        validate_review_export,
    )


SEALED_SCHEMA = "gold-lite-assisted-adjudication-sealed-dev-v0.1"
ASSISTED_LABEL = (
    "Cameron + Codex-assisted DEV reference; not independent human gold, "
    "validation, representative accuracy, or fresh-gate evidence"
)


def validate_packet_against_sources(
    packet: ReviewPacket,
    manifest: GoldLiteManifest,
    bundle_root: Path,
    *,
    deviations_dir: Path,
) -> None:
    """Require byte-for-byte equality with a fresh canonical C-B rebuild."""
    canonical = build_review_packet(
        manifest,
        bundle_root,
        deviations_dir=deviations_dir,
    )
    if packet != canonical:
        raise ValueError("packet does not match a fresh build from the manifest and source bundles")


def validate_assisted_review(
    packet: ReviewPacket,
    review: ReviewExport,
) -> dict[str, Any]:
    """Validate a completed assisted state while retaining all escalation semantics."""
    parent_results = validate_review_export(packet, review, require_complete=False)
    parents = {parent.parent_id: parent for parent in packet.parents}
    decompositions = {decision.parent_id: decision for decision in review.decompositions}
    decisions = {decision.atom_id: decision for decision in review.decisions}

    missing_decompositions = sorted(set(parents) - set(decompositions))
    if missing_decompositions:
        raise ValueError(f"missing decomposition decisions: {missing_decompositions}")

    escalations = [
        decision for decision in review.decompositions if decision.status == "needs_revision"
    ]
    if not escalations:
        raise ValueError(
            "assisted-adjudication seal requires documented needs_revision escalations"
        )
    undocumented = sorted(
        decision.parent_id
        for decision in escalations
        if decision.note is None or not decision.note.strip()
    )
    if undocumented:
        raise ValueError(f"needs_revision decompositions require notes: {undocumented}")

    approved_parent_ids = {
        decision.parent_id for decision in review.decompositions if decision.status == "approved"
    }
    expected_atom_ids = {
        atom.atom_id
        for parent in packet.parents
        if parent.parent_id in approved_parent_ids
        for atom in parent.atoms
    }
    missing_atoms = sorted(expected_atom_ids - set(decisions))
    if missing_atoms:
        raise ValueError(f"missing atom decisions under approved decompositions: {missing_atoms}")
    nonapproved_atoms = sorted(set(decisions) - expected_atom_ids)
    if nonapproved_atoms:
        raise ValueError(
            f"atom decisions are only allowed under approved decompositions: {nonapproved_atoms}"
        )

    try:
        validate_review_export(packet, review, require_complete=True)
    except ValueError as exc:
        legacy_complete_error = str(exc)
    else:  # pragma: no cover - guard against accidentally weakening legacy mode.
        raise ValueError("legacy complete mode unexpectedly accepted an assisted escalation export")

    results_by_parent = {result.parent_id: result for result in parent_results}
    second_review_atoms = sorted(
        decision.atom_id for decision in review.decisions if decision.confidence == "unsure"
    )
    return {
        "approved_parent_ids": sorted(approved_parent_ids),
        "escalations": [decision.model_dump(mode="json") for decision in escalations],
        "parent_results": [
            results_by_parent[parent_id].model_dump(mode="json")
            for parent_id in sorted(approved_parent_ids)
        ],
        "second_review_atom_ids": second_review_atoms,
        "legacy_complete_error": legacy_complete_error,
    }


def build_assisted_sealed_review(
    packet: ReviewPacket,
    review: ReviewExport,
    assisted: dict[str, Any],
    *,
    review_sha256: str,
) -> dict[str, Any]:
    """Render a provenance-bound derivative; the raw export remains unchanged."""
    return {
        "schema_version": SEALED_SCHEMA,
        "label": ASSISTED_LABEL,
        "rehearsal_id": packet.rehearsal_id,
        "packet_sha256": packet.packet_sha256,
        "source_review_sha256": f"sha256:{review_sha256}",
        "reviewer": review.reviewer,
        "exported_at_utc": review.exported_at_utc,
        "adjudication_status": "completed_with_documented_escalations",
        "legacy_complete_mode_green": False,
        "legacy_complete_mode_error": assisted["legacy_complete_error"],
        "counts": {
            "parents": len(packet.parents),
            "approved_decompositions": len(assisted["approved_parent_ids"]),
            "documented_needs_revision_escalations": len(assisted["escalations"]),
            "atom_decisions_under_approved_parents": len(review.decisions),
            "supports": sum(decision.label == "supports" for decision in review.decisions),
            "refutes": sum(decision.label == "refutes" for decision in review.decisions),
            "insufficient": sum(decision.label == "insufficient" for decision in review.decisions),
            "retrieval_gap": sum(
                decision.label == "retrieval_gap" for decision in review.decisions
            ),
            "second_review_queue": len(assisted["second_review_atom_ids"]),
        },
        "documented_escalations": assisted["escalations"],
        "second_review_atom_ids": assisted["second_review_atom_ids"],
        "approved_parent_results": assisted["parent_results"],
    }


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_absent_or_identical(path: Path, text: str) -> None:
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise FileExistsError(f"refusing to overwrite non-identical output: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seal_command(args: argparse.Namespace) -> None:
    manifest = load_manifest(args.manifest)
    packet = load_review_packet(args.packet)
    validate_packet_against_sources(
        packet,
        manifest,
        args.bundle_root,
        deviations_dir=args.deviations_dir or args.out.parent / "canonical-deviations",
    )
    review = load_review_export(args.review)
    assisted = validate_assisted_review(packet, review)
    sealed = build_assisted_sealed_review(
        packet,
        review,
        assisted,
        review_sha256=_sha256_file(args.review),
    )
    _write_absent_or_identical(
        args.out, yaml.safe_dump(sealed, sort_keys=False, allow_unicode=True)
    )
    print(f"adjudication_status: {sealed['adjudication_status']}")
    print(f"approved_decompositions: {sealed['counts']['approved_decompositions']}")
    print(f"documented_escalations: {sealed['counts']['documented_needs_revision_escalations']}")
    print(f"second_review_queue: {sealed['counts']['second_review_queue']}")
    print("legacy_complete_mode_green: False")
    print(f"wrote: {args.out}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    seal = subparsers.add_parser("seal", help="Seal a completed assisted Rung 4 export.")
    seal.add_argument("--manifest", type=Path, required=True)
    seal.add_argument("--bundle-root", type=Path, required=True)
    seal.add_argument("--packet", type=Path, required=True)
    seal.add_argument("--review", type=Path, required=True)
    seal.add_argument("--out", type=Path, required=True)
    seal.add_argument("--deviations-dir", type=Path)
    seal.set_defaults(func=_seal_command)
    return parser


def main() -> None:
    args = _parser().parse_args()
    try:
        args.func(args)
    except (FileExistsError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
