"""Build and validate a local Gold Lite human-review rehearsal.

Gold Lite is DEV tooling, not a public CLI or acceptance-gate input. It consumes
Evidence Bundler C-B directories through CAL's existing fail-closed loader, selects
parent claims without consulting old gold/CAL outputs, and writes a blinded local
review packet. Human decisions stay in a separate browser-exported JSON artifact.

Usage::

    python scripts/gold_lite_review.py build \
        --manifest <manifest.yaml> \
        --bundle-root <pilot-bundles/> \
        --out-dir <local-output/>

    python scripts/gold_lite_review.py validate \
        --packet <local-output/review-packet.json> \
        --review <browser-export.json> \
        --out <new-sealed-review.yaml>
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Literal, Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from claim_audit_lab.contracts.bundle_loader import BundleContents, load_bundle
from claim_audit_lab.contracts.cb_models import CBClaim, CBClaimEvidencePassage

MANIFEST_SCHEMA = "gold-lite-manifest-v0.1"
PACKET_SCHEMA = "gold-lite-review-packet-v0.1"
REVIEW_SCHEMA = "gold-lite-review-v0.1"
SEALED_SCHEMA = "gold-lite-sealed-dev-v0.1"
PACKET_FILENAME = "review-packet.json"
HTML_FILENAME = "review.html"
README_FILENAME = "README.md"
_PACKET_PLACEHOLDER = "__GOLD_LITE_PACKET_JSON__"

Operator = Literal["single", "all_of"]
DecompositionStatus = Literal["approved", "needs_revision"]
AtomLabel = Literal["supports", "refutes", "insufficient", "retrieval_gap"]
Confidence = Literal["sure", "unsure"]
ParentVerdict = Literal[
    "supported", "partially_supported", "contradicted", "not_checkable", "pending"
]


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        str_strip_whitespace=True,
    )


class SelectionSpec(_StrictModel):
    method: Literal["sha256-lowest"]
    seed: str = Field(min_length=1)
    source_claim_count: int = Field(ge=1)
    sample_size: int = Field(ge=1)


class ManifestAtom(_StrictModel):
    atom_id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class ManifestParent(_StrictModel):
    parent_id: str = Field(min_length=1)
    bundle_dir: str = Field(min_length=1)
    source_claim_id: str = Field(min_length=1)
    operator: Operator
    atoms: list[ManifestAtom] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_shape(self) -> Self:
        if self.parent_id != self.source_claim_id:
            raise ValueError("v0.1 parent_id must equal source_claim_id")
        if self.operator == "single" and len(self.atoms) != 1:
            raise ValueError("single parents require exactly one atom")
        if self.operator == "all_of" and len(self.atoms) < 2:
            raise ValueError("all_of parents require at least two atoms")
        return self


class GoldLiteManifest(_StrictModel):
    schema_version: Literal["gold-lite-manifest-v0.1"]
    rehearsal_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    selection: SelectionSpec
    initial_candidate_limit: int = Field(ge=1)
    parents: list[ManifestParent] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_ids(self) -> Self:
        if len(self.parents) != self.selection.sample_size:
            raise ValueError("parents count must equal selection.sample_size")
        _require_unique([parent.parent_id for parent in self.parents], "parent_id")
        _require_unique(
            [atom.atom_id for parent in self.parents for atom in parent.atoms],
            "atom_id",
        )
        return self


class ReviewCandidate(_StrictModel):
    candidate_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    passage_id: str = Field(min_length=1)
    passage_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    source_title: str = Field(min_length=1)
    section: str | None = None
    text: str = Field(min_length=1)


class ReviewAtom(_StrictModel):
    atom_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    candidate_ids: list[str] = Field(min_length=1)


class ReviewParent(_StrictModel):
    parent_id: str = Field(min_length=1)
    parent_text: str = Field(min_length=1)
    operator: Operator
    candidates: list[ReviewCandidate] = Field(min_length=1)
    atoms: list[ReviewAtom] = Field(min_length=1)


class ReviewPacket(_StrictModel):
    schema_version: Literal["gold-lite-review-packet-v0.1"]
    rehearsal_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    packet_sha256: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    selection: SelectionSpec
    initial_candidate_limit: int = Field(ge=1)
    parents: list[ReviewParent] = Field(min_length=1)


class DecompositionDecision(_StrictModel):
    parent_id: str = Field(min_length=1)
    status: DecompositionStatus
    note: str | None = None


class SelectedPassage(_StrictModel):
    candidate_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    passage_id: str = Field(min_length=1)
    passage_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")


class AtomDecision(_StrictModel):
    atom_id: str = Field(min_length=1)
    label: AtomLabel
    confidence: Confidence
    selected_passages: list[SelectedPassage] = Field(default_factory=list)
    note: str | None = None

    @model_validator(mode="after")
    def validate_rationale_shape(self) -> Self:
        _require_unique(
            [passage.candidate_id for passage in self.selected_passages],
            f"selected passage in {self.atom_id}",
        )
        if self.label in {"supports", "refutes"} and not self.selected_passages:
            raise ValueError(f"{self.label} requires at least one selected passage")
        if self.label == "retrieval_gap" and self.selected_passages:
            raise ValueError("retrieval_gap cannot select a passage")
        return self


class ReviewExport(_StrictModel):
    schema_version: Literal["gold-lite-review-v0.1"]
    rehearsal_id: str = Field(min_length=1)
    packet_sha256: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    reviewer: str = Field(min_length=1)
    exported_at_utc: str = Field(min_length=1)
    decompositions: list[DecompositionDecision] = Field(default_factory=list)
    decisions: list[AtomDecision] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_ids(self) -> Self:
        _require_unique(
            [decision.parent_id for decision in self.decompositions],
            "decomposition parent_id",
        )
        _require_unique([decision.atom_id for decision in self.decisions], "decision atom_id")
        return self


class ParentResult(_StrictModel):
    parent_id: str
    support_verdict: ParentVerdict
    atom_labels: list[AtomLabel] = Field(default_factory=list)
    needs_second_review: bool
    reason: str


def load_manifest(path: Path) -> GoldLiteManifest:
    return _load_yaml_model(GoldLiteManifest, path)


def load_review_packet(path: Path) -> ReviewPacket:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load review packet {path}: {exc}") from exc
    packet = ReviewPacket.model_validate(raw)
    expected_hash = _packet_hash(_packet_payload(packet))
    if packet.packet_sha256 != expected_hash:
        raise ValueError(
            f"packet hash drift: recorded={packet.packet_sha256} actual={expected_hash}"
        )
    return packet


def load_review_export(path: Path) -> ReviewExport:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load review export {path}: {exc}") from exc
    return ReviewExport.model_validate(raw)


def build_review_packet(
    manifest: GoldLiteManifest,
    bundle_root: Path,
    *,
    deviations_dir: Path,
) -> ReviewPacket:
    """Load C-B once, verify the deterministic sample, and build a blinded packet."""
    bundles, claims = _load_source_claims(bundle_root, deviations_dir=deviations_dir)
    if len(claims) != manifest.selection.source_claim_count:
        raise ValueError(
            "source claim count drift: "
            f"manifest={manifest.selection.source_claim_count} actual={len(claims)}"
        )

    selected_ids = select_claim_ids(
        claims,
        seed=manifest.selection.seed,
        sample_size=manifest.selection.sample_size,
    )
    manifest_ids = [parent.source_claim_id for parent in manifest.parents]
    if manifest_ids != selected_ids:
        raise ValueError(
            "manifest parents do not match deterministic selection: "
            f"expected={selected_ids!r} actual={manifest_ids!r}"
        )

    parents: list[ReviewParent] = []
    for proposed in manifest.parents:
        source_bundle_name, claim = claims[proposed.source_claim_id]
        if proposed.bundle_dir != source_bundle_name:
            raise ValueError(
                f"{proposed.parent_id}: bundle drift; "
                f"manifest={proposed.bundle_dir!r} actual={source_bundle_name!r}"
            )
        contents = bundles[source_bundle_name]
        candidates = _review_candidates(claim, contents)
        if not candidates:
            raise ValueError(f"{proposed.parent_id}: source claim has no candidate passages")
        atoms = [
            ReviewAtom(
                atom_id=atom.atom_id,
                text=atom.text,
                candidate_ids=_shuffled_candidate_ids(
                    candidates,
                    seed=manifest.selection.seed,
                    atom_id=atom.atom_id,
                ),
            )
            for atom in proposed.atoms
        ]
        parents.append(
            ReviewParent(
                parent_id=proposed.parent_id,
                parent_text=claim.claim_text,
                operator=proposed.operator,
                candidates=sorted(candidates, key=lambda item: item.candidate_id),
                atoms=atoms,
            )
        )

    payload: dict[str, Any] = {
        "schema_version": PACKET_SCHEMA,
        "rehearsal_id": manifest.rehearsal_id,
        "label": manifest.label,
        "selection": manifest.selection.model_dump(mode="json"),
        "initial_candidate_limit": manifest.initial_candidate_limit,
        "parents": [parent.model_dump(mode="json") for parent in parents],
    }
    return ReviewPacket(packet_sha256=_packet_hash(payload), **payload)


def select_claim_ids(
    claims: dict[str, tuple[str, CBClaim]],
    *,
    seed: str,
    sample_size: int,
) -> list[str]:
    if sample_size > len(claims):
        raise ValueError(f"sample_size {sample_size} exceeds claim count {len(claims)}")
    ranked = sorted(
        claims,
        key=lambda claim_id: (_sha256_text(f"{seed}:{claim_id}"), claim_id),
    )
    return ranked[:sample_size]


def render_review_html(packet: ReviewPacket) -> str:
    packet_json = json.dumps(
        packet.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).replace("<", "\\u003c")
    if _PACKET_PLACEHOLDER not in _HTML_TEMPLATE:
        raise RuntimeError("Gold Lite HTML packet placeholder is missing")
    return _HTML_TEMPLATE.replace(_PACKET_PLACEHOLDER, packet_json)


def validate_review_export(
    packet: ReviewPacket,
    review: ReviewExport,
    *,
    require_complete: bool,
) -> list[ParentResult]:
    if review.rehearsal_id != packet.rehearsal_id:
        raise ValueError("review rehearsal_id does not match packet")
    if review.packet_sha256 != packet.packet_sha256:
        raise ValueError("review packet_sha256 does not match packet")

    parents = {parent.parent_id: parent for parent in packet.parents}
    atoms = {atom.atom_id: (parent, atom) for parent in packet.parents for atom in parent.atoms}
    decomposition = {decision.parent_id: decision for decision in review.decompositions}
    decisions = {decision.atom_id: decision for decision in review.decisions}

    extra_parents = sorted(set(decomposition) - set(parents))
    if extra_parents:
        raise ValueError(f"review contains unknown parent IDs: {extra_parents}")
    extra_atoms = sorted(set(decisions) - set(atoms))
    if extra_atoms:
        raise ValueError(f"review contains unknown atom IDs: {extra_atoms}")

    for atom_id, decision in decisions.items():
        parent, atom = atoms[atom_id]
        parent_decision = decomposition.get(parent.parent_id)
        if parent_decision is None or parent_decision.status != "approved":
            raise ValueError(f"{atom_id}: atom decision requires approved decomposition")
        candidates = {candidate.candidate_id: candidate for candidate in parent.candidates}
        allowed = set(atom.candidate_ids)
        for selected in decision.selected_passages:
            if selected.candidate_id not in allowed:
                raise ValueError(
                    f"{atom_id}: selected candidate is not available to this atom: "
                    f"{selected.candidate_id}"
                )
            expected = candidates[selected.candidate_id]
            if selected.model_dump(mode="json") != {
                "candidate_id": expected.candidate_id,
                "source_id": expected.source_id,
                "passage_id": expected.passage_id,
                "passage_hash": expected.passage_hash,
            }:
                raise ValueError(f"{atom_id}: selected passage provenance/hash drift")

    if require_complete:
        missing_decomposition = sorted(set(parents) - set(decomposition))
        if missing_decomposition:
            raise ValueError(f"missing decomposition decisions: {missing_decomposition}")
        needs_revision = sorted(
            parent_id
            for parent_id, decision in decomposition.items()
            if decision.status != "approved"
        )
        if needs_revision:
            raise ValueError(f"decompositions still need revision: {needs_revision}")
        missing_decisions = sorted(set(atoms) - set(decisions))
        if missing_decisions:
            raise ValueError(f"missing atom decisions: {missing_decisions}")

    return [
        aggregate_parent_result(
            parent,
            decomposition.get(parent.parent_id),
            decisions,
        )
        for parent in packet.parents
    ]


def aggregate_parent_result(
    parent: ReviewParent,
    decomposition: DecompositionDecision | None,
    decisions: dict[str, AtomDecision],
) -> ParentResult:
    """Derive a transparent parent verdict from approved atomic decisions."""
    if decomposition is None:
        return _pending_parent(parent, "decomposition not reviewed")
    if decomposition.status != "approved":
        return _pending_parent(parent, "decomposition needs revision")
    atom_decisions = [decisions.get(atom.atom_id) for atom in parent.atoms]
    if any(decision is None for decision in atom_decisions):
        return _pending_parent(parent, "one or more atom decisions are missing")
    complete = [decision for decision in atom_decisions if decision is not None]
    labels = [decision.label for decision in complete]
    needs_second_review = any(decision.confidence == "unsure" for decision in complete)
    if "retrieval_gap" in labels:
        return ParentResult(
            parent_id=parent.parent_id,
            support_verdict="pending",
            atom_labels=labels,
            needs_second_review=True,
            reason="one or more atoms have a retrieval gap; no parent verdict derived",
        )
    if "refutes" in labels:
        verdict: ParentVerdict = "contradicted"
        reason = "at least one material atom is refuted"
    elif all(label == "supports" for label in labels):
        verdict = "supported"
        reason = "all material atoms are supported"
    elif all(label == "insufficient" for label in labels):
        verdict = "not_checkable"
        reason = "all material atoms are insufficient in the bounded packet"
    elif set(labels) <= {"supports", "insufficient"}:
        verdict = "partially_supported"
        reason = "at least one atom is supported and at least one is insufficient"
    else:  # pragma: no cover - Literal exhaustiveness guard
        raise AssertionError(f"unhandled Gold Lite atom labels: {labels}")
    return ParentResult(
        parent_id=parent.parent_id,
        support_verdict=verdict,
        atom_labels=labels,
        needs_second_review=needs_second_review,
        reason=reason,
    )


def build_sealed_review(
    packet: ReviewPacket,
    review: ReviewExport,
    parent_results: list[ParentResult],
    *,
    review_sha256: str,
    complete: bool,
) -> dict[str, Any]:
    return {
        "schema_version": SEALED_SCHEMA,
        "label": "DEV usability rehearsal; not validation and not gate evidence",
        "rehearsal_id": packet.rehearsal_id,
        "packet_sha256": packet.packet_sha256,
        "source_review_sha256": f"sha256:{review_sha256}",
        "reviewer": review.reviewer,
        "exported_at_utc": review.exported_at_utc,
        "complete": complete,
        "counts": {
            "parents": len(packet.parents),
            "atoms": sum(len(parent.atoms) for parent in packet.parents),
            "decompositions_recorded": len(review.decompositions),
            "atom_decisions_recorded": len(review.decisions),
            "pending_parent_results": sum(
                result.support_verdict == "pending" for result in parent_results
            ),
            "needs_second_review": sum(result.needs_second_review for result in parent_results),
        },
        "decompositions": [decision.model_dump(mode="json") for decision in review.decompositions],
        "atom_decisions": [decision.model_dump(mode="json") for decision in review.decisions],
        "parent_results": [result.model_dump(mode="json") for result in parent_results],
    }


def write_rehearsal_artifacts(
    packet: ReviewPacket,
    out_dir: Path,
    *,
    manifest_path: Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_text = (
        json.dumps(packet.model_dump(mode="json"), indent=2, sort_keys=True, ensure_ascii=False)
        + "\n"
    )
    html_text = render_review_html(packet)
    atom_count = sum(len(parent.atoms) for parent in packet.parents)
    candidate_count = sum(len(parent.candidates) for parent in packet.parents)
    readme_text = _render_output_readme(
        packet,
        atom_count=atom_count,
        candidate_count=candidate_count,
        manifest_name=manifest_path.name,
    )
    _write_absent_or_identical(out_dir / PACKET_FILENAME, packet_text)
    _write_absent_or_identical(out_dir / HTML_FILENAME, html_text)
    _write_absent_or_identical(out_dir / README_FILENAME, readme_text)


def _load_source_claims(
    bundle_root: Path,
    *,
    deviations_dir: Path,
) -> tuple[dict[str, BundleContents], dict[str, tuple[str, CBClaim]]]:
    if not bundle_root.is_dir():
        raise ValueError(f"bundle root does not exist: {bundle_root}")
    bundles: dict[str, BundleContents] = {}
    claims: dict[str, tuple[str, CBClaim]] = {}
    for bundle_dir in sorted(path for path in bundle_root.iterdir() if path.is_dir()):
        if not (bundle_dir / "bundle_manifest.yaml").is_file():
            continue
        contents = load_bundle(bundle_dir, deviations_dir=deviations_dir)
        if bundle_dir.name in bundles:
            raise ValueError(f"duplicate bundle directory name: {bundle_dir.name}")
        bundles[bundle_dir.name] = contents
        for claim in contents.claims:
            if claim.claim_type != "extracted_claim":
                continue
            if claim.claim_id in claims:
                raise ValueError(f"duplicate claim_id across source bundles: {claim.claim_id}")
            claims[claim.claim_id] = (bundle_dir.name, claim)
    if not bundles:
        raise ValueError(f"no C-B bundles found under {bundle_root}")
    if not claims:
        raise ValueError(f"no extracted claims found under {bundle_root}")
    return bundles, claims


def _review_candidates(claim: CBClaim, contents: BundleContents) -> list[ReviewCandidate]:
    unique: dict[tuple[str, str], CBClaimEvidencePassage] = {}
    for passage in [*claim.evidence_passages, *claim.counterevidence_passages]:
        key = (passage.source_id, passage.passage_id)
        existing = unique.get(key)
        if existing is not None and existing != passage:
            raise ValueError(f"{claim.claim_id}: duplicate candidate identity with drift: {key}")
        unique[key] = passage
    candidates: list[ReviewCandidate] = []
    for passage in unique.values():
        profile = contents.source_profiles.get(passage.source_id)
        if profile is None:
            raise ValueError(
                f"{claim.claim_id}: candidate source profile missing: {passage.source_id}"
            )
        candidates.append(
            ReviewCandidate(
                candidate_id=f"{passage.source_id}/{passage.passage_id}",
                source_id=passage.source_id,
                passage_id=passage.passage_id,
                passage_hash=passage.passage_hash,
                source_title=profile.bibliographic.title,
                section=passage.section,
                text=passage.passage_text,
            )
        )
    return candidates


def _shuffled_candidate_ids(
    candidates: list[ReviewCandidate],
    *,
    seed: str,
    atom_id: str,
) -> list[str]:
    return [
        candidate.candidate_id
        for candidate in sorted(
            candidates,
            key=lambda candidate: (
                _sha256_text(f"{seed}:{atom_id}:{candidate.candidate_id}"),
                candidate.candidate_id,
            ),
        )
    ]


def _packet_payload(packet: ReviewPacket) -> dict[str, Any]:
    payload = packet.model_dump(mode="json")
    payload.pop("packet_sha256")
    return payload


def _packet_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"sha256:{_sha256_text(canonical)}"


def _pending_parent(parent: ReviewParent, reason: str) -> ParentResult:
    return ParentResult(
        parent_id=parent.parent_id,
        support_verdict="pending",
        needs_second_review=True,
        reason=reason,
    )


def _load_yaml_model(model: type[GoldLiteManifest], path: Path) -> GoldLiteManifest:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"could not load Gold Lite manifest {path}: {exc}") from exc
    return model.model_validate(raw)


def _require_unique(values: list[str], label: str) -> None:
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        raise ValueError(f"duplicate {label}: {duplicates}")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_absent_or_identical(path: Path, text: str) -> None:
    encoded = text.encode("utf-8")
    if path.exists():
        if path.read_bytes() != encoded:
            raise FileExistsError(f"refusing to overwrite non-identical artifact: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)


def _render_output_readme(
    packet: ReviewPacket,
    *,
    atom_count: int,
    candidate_count: int,
    manifest_name: str,
) -> str:
    return f"""# Gold Lite ten-claim DEV rehearsal

**DEV USABILITY REHEARSAL — not validation and not gate evidence.** PILOT-001 is the
adaptation set. No result here can clear Phase 4 or support a release claim.

## Packet

- rehearsal: `{packet.rehearsal_id}`
- packet hash: `{packet.packet_sha256}`
- deterministic parent selection: `{packet.selection.method}` / seed `{packet.selection.seed}`
- parents: {len(packet.parents)}
- proposed atomic steps: {atom_count}
- retained parent-level EB candidates: {candidate_count}
- initial candidates shown per atom: {packet.initial_candidate_limit}; `show more` exposes all
- decomposition source: `{manifest_name}`

The evidence passages were nominated by Evidence Bundler for each **parent claim**. This
first unit reuses those sealed C-B candidates read-only; it does not claim atom-level
retrieval was run. Old gold, CAL output, condition/model, EB role, trust, and retrieval
rank are absent from the review packet.

## Review

1. Open `review.html` locally in a browser.
2. Enter a reviewer label.
3. Approve the proposed decomposition or mark it `needs revision` before labelling atoms.
4. For each enabled atom choose `supports`, `refutes`, `insufficient`, or `retrieval gap`.
5. `supports` and `refutes` require at least one selected rationale passage.
6. Choose `sure` or `unsure`; unsure items remain queued for a second review.
7. Download a checkpoint. Preserve every export; do not overwrite an earlier one.

Validate a completed export from the CAL workbench with:

```bash
.venv/bin/python scripts/gold_lite_review.py validate \\
  --packet <this-directory>/review-packet.json \\
  --review <browser-export.json> \\
  --out <new-sealed-review.yaml>
```

Use `--allow-incomplete` only to inspect a checkpoint. Incomplete or rejected-
decomposition items are never scored.
"""


def _build_command(args: argparse.Namespace) -> None:
    manifest = load_manifest(args.manifest)
    packet = build_review_packet(
        manifest,
        args.bundle_root,
        deviations_dir=args.deviations_dir or args.out_dir / "deviations",
    )
    write_rehearsal_artifacts(packet, args.out_dir, manifest_path=args.manifest)
    print(f"parents: {len(packet.parents)}")
    print(f"atoms: {sum(len(parent.atoms) for parent in packet.parents)}")
    print(f"packet_sha256: {packet.packet_sha256}")
    print(f"review: {args.out_dir / HTML_FILENAME}")


def _validate_command(args: argparse.Namespace) -> None:
    packet = load_review_packet(args.packet)
    review = load_review_export(args.review)
    require_complete = not args.allow_incomplete
    results = validate_review_export(packet, review, require_complete=require_complete)
    sealed = build_sealed_review(
        packet,
        review,
        results,
        review_sha256=_sha256_file(args.review),
        complete=require_complete,
    )
    serialized = yaml.safe_dump(sealed, sort_keys=False, allow_unicode=True)
    _write_absent_or_identical(args.out, serialized)
    print(f"complete: {require_complete}")
    print(f"parents: {len(results)}")
    print(f"pending: {sum(result.support_verdict == 'pending' for result in results)}")
    print(f"needs_second_review: {sum(result.needs_second_review for result in results)}")
    print(f"wrote: {args.out}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Build a blinded local review packet.")
    build.add_argument("--manifest", type=Path, required=True)
    build.add_argument("--bundle-root", type=Path, required=True)
    build.add_argument("--out-dir", type=Path, required=True)
    build.add_argument("--deviations-dir", type=Path)
    build.set_defaults(func=_build_command)

    validate = subparsers.add_parser("validate", help="Validate and seal a browser export.")
    validate.add_argument("--packet", type=Path, required=True)
    validate.add_argument("--review", type=Path, required=True)
    validate.add_argument("--out", type=Path, required=True)
    validate.add_argument("--allow-incomplete", action="store_true")
    validate.set_defaults(func=_validate_command)
    return parser


def main() -> None:
    args = _parser().parse_args()
    try:
        args.func(args)
    except (FileExistsError, ValidationError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc


_HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Gold Lite DEV rehearsal</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #18212a;
      --muted: #607080;
      --line: #d8e0e7;
      --paper: #ffffff;
      --wash: #f3f6f8;
      --accent: #155eef;
      --accent-wash: #eaf0ff;
      --warn: #9a6700;
      --danger: #b42318;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; color: var(--ink); background: var(--wash); }
    button, input, textarea { font: inherit; }
    button { cursor: pointer; }
    .app { max-width: 1080px; margin: 0 auto; padding: 24px 18px 80px; }
    .banner {
      background: #fff4ce; border: 1px solid #e7c766; border-radius: 10px;
      padding: 12px 16px; font-weight: 700;
    }
    .toolbar, .card {
      background: var(--paper); border: 1px solid var(--line); border-radius: 12px;
      box-shadow: 0 1px 2px rgba(16, 24, 40, .04);
    }
    .toolbar {
      display: flex; gap: 14px; align-items: end; justify-content: space-between;
      margin: 16px 0; padding: 14px 16px; flex-wrap: wrap;
    }
    .toolbar label { display: grid; gap: 5px; color: var(--muted); font-size: 14px; }
    input[type="text"], textarea {
      border: 1px solid #aebbc7; border-radius: 8px; padding: 9px 11px; color: var(--ink);
      background: white;
    }
    input[type="text"] { min-width: 240px; }
    textarea { width: 100%; min-height: 72px; resize: vertical; }
    .progress { color: var(--muted); font-size: 14px; }
    .card { padding: 20px; margin-top: 14px; }
    h1 { margin: 18px 0 4px; font-size: 28px; }
    h2 { margin: 0 0 8px; font-size: 20px; }
    h3 { margin: 20px 0 8px; font-size: 16px; }
    p { line-height: 1.5; }
    .eyebrow { color: var(--muted); font-size: 13px; font-weight: 700; text-transform: uppercase; }
    .parent-text, .atom-text {
      font-size: 18px; line-height: 1.55; padding: 13px 15px; border-left: 4px solid var(--accent);
      background: var(--accent-wash); border-radius: 4px 9px 9px 4px;
    }
    .atom-text { font-size: 21px; font-weight: 700; }
    .atom-list { margin: 8px 0 0; padding-left: 22px; }
    .atom-list li { margin: 5px 0; line-height: 1.4; }
    .choice-row { display: flex; gap: 9px; flex-wrap: wrap; }
    .choice {
      border: 1px solid #98a6b5; background: white; border-radius: 9px; padding: 9px 12px;
      color: var(--ink);
    }
    .choice.selected {
      border-color: var(--accent); background: var(--accent-wash); color: #123a8c;
    }
    .choice.danger.selected { border-color: var(--danger); background: #feeceb; color: #8f1d15; }
    .choice.warn.selected { border-color: var(--warn); background: #fff6dc; color: #7a5100; }
    fieldset { border: 0; padding: 0; margin: 0; min-width: 0; }
    fieldset[disabled] { opacity: .48; }
    .warning { color: var(--warn); font-weight: 700; }
    .passage {
      border: 1px solid var(--line); border-radius: 10px; padding: 13px 14px; margin: 10px 0;
      background: #fbfcfd;
    }
    .passage-head { display: flex; align-items: start; gap: 10px; }
    .passage-head input { margin-top: 4px; transform: scale(1.15); }
    .passage-title { font-weight: 700; }
    .passage-section { color: var(--muted); font-size: 13px; margin-top: 3px; }
    .passage-text { white-space: pre-wrap; line-height: 1.5; margin: 10px 0 0 28px; }
    .nav { display: flex; justify-content: space-between; gap: 12px; margin-top: 18px; }
    .primary, .secondary {
      border-radius: 9px; padding: 10px 15px; font-weight: 700;
    }
    .primary { border: 1px solid var(--accent); color: white; background: var(--accent); }
    .secondary { border: 1px solid #98a6b5; color: var(--ink); background: white; }
    .primary:disabled, .secondary:disabled { cursor: default; opacity: .45; }
    .footer-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 16px; }
    .small { color: var(--muted); font-size: 13px; }
    .status { min-height: 22px; margin-top: 8px; color: var(--muted); }
    @media (max-width: 680px) {
      .app { padding: 14px 10px 60px; }
      .card { padding: 15px; }
      .parent-text, .atom-text { font-size: 17px; }
      input[type="text"] { min-width: 0; width: 100%; }
    }
  </style>
</head>
<body>
  <main class="app">
    <div class="banner">DEV usability rehearsal only — not validation and not gate evidence.</div>
    <h1>Gold Lite</h1>
    <p class="small">Approve the decomposition, then review one atomic step at a time.</p>

    <section class="toolbar">
      <label>Reviewer label
        <input id="reviewer" type="text" autocomplete="off" placeholder="e.g. Cameron">
      </label>
      <div id="progress" class="progress"></div>
    </section>

    <section class="card">
      <div id="position" class="eyebrow"></div>
      <h2>Parent claim</h2>
      <div id="parent-text" class="parent-text"></div>
      <p id="operator" class="small"></p>
      <ol id="atom-list" class="atom-list"></ol>

      <h3>Is this decomposition faithful?</h3>
      <div id="decomposition-choices" class="choice-row"></div>
      <label class="small" for="decomposition-note">Decomposition note</label>
      <textarea
        id="decomposition-note"
        placeholder="Required if the split needs revision."
      ></textarea>
    </section>

    <section class="card">
      <div id="atom-position" class="eyebrow"></div>
      <h2>Atomic step</h2>
      <div id="atom-text" class="atom-text"></div>
      <p id="disabled-message" class="warning"></p>
      <fieldset id="decision-fieldset">
        <h3>What does the supplied packet establish?</h3>
        <div id="label-choices" class="choice-row"></div>

        <h3>Rationale passages</h3>
        <p class="small">
          Supports/refutes requires at least one. Passage order is shuffled; EB roles are hidden.
        </p>
        <div id="passages"></div>
        <button id="show-more" class="secondary" type="button"></button>

        <h3>How sure are you?</h3>
        <div id="confidence-choices" class="choice-row"></div>

        <h3>Optional note</h3>
        <textarea
          id="atom-note"
          placeholder="Record ambiguity, missing context, or why you are unsure."
        ></textarea>
      </fieldset>

      <div class="nav">
        <button id="previous" class="secondary" type="button">Previous</button>
        <button id="next" class="primary" type="button">Next</button>
      </div>
      <div id="status" class="status"></div>
    </section>

    <section class="card">
      <h2>Checkpoint</h2>
      <p class="small">
        The browser autosaves locally. Downloads are additive; preserve earlier files.
      </p>
      <div class="footer-actions">
        <button id="download" class="primary" type="button">Download checkpoint JSON</button>
        <button id="clear" class="secondary" type="button">Clear local progress</button>
      </div>
    </section>
  </main>

  <script id="packet-data" type="application/json">__GOLD_LITE_PACKET_JSON__</script>
  <script>
    "use strict";
    const packet = JSON.parse(document.getElementById("packet-data").textContent);
    const storageKey = `gold-lite:${packet.rehearsal_id}:${packet.packet_sha256}`;
    const items = packet.parents.flatMap(parent => parent.atoms.map(atom => ({ parent, atom })));
    const emptyState = { reviewer: "", decomposition: {}, decompositionNotes: {}, decisions: {} };
    let state = loadState();
    let current = 0;
    const showAll = {};

    function loadState() {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return structuredClone(emptyState);
      try { return Object.assign(structuredClone(emptyState), JSON.parse(raw)); }
      catch (_) { return structuredClone(emptyState); }
    }

    function saveState(message = "Saved locally.") {
      localStorage.setItem(storageKey, JSON.stringify(state));
      document.getElementById("status").textContent = message;
      renderProgress();
    }

    function element(tag, className, text) {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (text !== undefined) node.textContent = text;
      return node;
    }

    function decisionFor(atomId) {
      if (!state.decisions[atomId]) {
        state.decisions[atomId] = { label: "", confidence: "", selected: [], note: "" };
      }
      return state.decisions[atomId];
    }

    function choiceButton(text, value, selected, onClick, extraClass = "") {
      const button = element("button", `choice ${extraClass}`.trim(), text);
      button.type = "button";
      if (selected) button.classList.add("selected");
      button.addEventListener("click", onClick);
      button.dataset.value = value;
      return button;
    }

    function render() {
      const { parent, atom } = items[current];
      const parentIndex = packet.parents.findIndex(item => item.parent_id === parent.parent_id);
      document.getElementById("position").textContent =
        `Parent ${parentIndex + 1} of ${packet.parents.length}`;
      document.getElementById("atom-position").textContent =
        `Step ${parent.atoms.findIndex(item => item.atom_id === atom.atom_id) + 1}` +
        ` of ${parent.atoms.length} · Overall ${current + 1} of ${items.length}`;
      document.getElementById("parent-text").textContent = parent.parent_text;
      document.getElementById("operator").textContent = parent.operator === "all_of"
        ? "Compound claim: every material step must hold."
        : "Single-step claim.";
      document.getElementById("atom-text").textContent = atom.text;

      const atomList = document.getElementById("atom-list");
      atomList.replaceChildren(...parent.atoms.map(item => {
        const row = element("li", "", item.text);
        if (item.atom_id === atom.atom_id) row.style.fontWeight = "700";
        return row;
      }));

      renderDecomposition(parent);
      renderDecision(parent, atom);
      document.getElementById("previous").disabled = current === 0;
      document.getElementById("next").disabled = current === items.length - 1;
      document.getElementById("status").textContent = "";
      renderProgress();
    }

    function renderDecomposition(parent) {
      const currentStatus = state.decomposition[parent.parent_id] || "";
      const choices = document.getElementById("decomposition-choices");
      choices.replaceChildren(
        choiceButton("Approve decomposition", "approved", currentStatus === "approved", () => {
          state.decomposition[parent.parent_id] = "approved";
          saveState(); render();
        }),
        choiceButton("Needs revision", "needs_revision", currentStatus === "needs_revision", () => {
          state.decomposition[parent.parent_id] = "needs_revision";
          saveState(); render();
        }, "warn")
      );
      const note = document.getElementById("decomposition-note");
      note.value = state.decompositionNotes[parent.parent_id] || "";
      note.oninput = () => {
        state.decompositionNotes[parent.parent_id] = note.value;
        saveState();
      };
    }

    function renderDecision(parent, atom) {
      const approved = state.decomposition[parent.parent_id] === "approved";
      const fieldset = document.getElementById("decision-fieldset");
      fieldset.disabled = !approved;
      document.getElementById("disabled-message").textContent = approved
        ? ""
        : "Approve this parent decomposition before labelling its steps.";
      const decision = decisionFor(atom.atom_id);

      const labelChoices = document.getElementById("label-choices");
      const labels = [
        ["Supports", "supports", ""],
        ["Refutes", "refutes", "danger"],
        ["Insufficient packet", "insufficient", "warn"],
        ["Retrieval gap", "retrieval_gap", "warn"]
      ];
      labelChoices.replaceChildren(...labels.map(([text, value, className]) =>
        choiceButton(text, value, decision.label === value, () => {
          decision.label = value;
          if (value === "retrieval_gap") decision.selected = [];
          saveState(); renderDecision(parent, atom);
        }, className)
      ));

      const candidateMap = Object.fromEntries(
        parent.candidates.map(item => [item.candidate_id, item])
      );
      const visibleIds = showAll[atom.atom_id]
        ? atom.candidate_ids
        : atom.candidate_ids.slice(0, packet.initial_candidate_limit);
      const passages = document.getElementById("passages");
      passages.replaceChildren(...visibleIds.map((candidateId, index) => {
        const candidate = candidateMap[candidateId];
        const card = element("article", "passage");
        const head = element("div", "passage-head");
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = decision.selected.includes(candidateId);
        checkbox.disabled = decision.label === "retrieval_gap";
        checkbox.addEventListener("change", () => {
          const selected = new Set(decision.selected);
          checkbox.checked ? selected.add(candidateId) : selected.delete(candidateId);
          decision.selected = Array.from(selected);
          saveState();
        });
        const heading = element("div");
        heading.appendChild(element(
          "div",
          "passage-title",
          `Passage ${index + 1} · ${candidate.source_title}`
        ));
        heading.appendChild(element(
          "div",
          "passage-section",
          candidate.section || "Section not supplied"
        ));
        head.append(checkbox, heading);
        card.append(head, element("div", "passage-text", candidate.text));
        return card;
      }));

      const showMore = document.getElementById("show-more");
      const remaining = atom.candidate_ids.length - packet.initial_candidate_limit;
      showMore.hidden = remaining <= 0;
      showMore.textContent = showAll[atom.atom_id]
        ? "Show first passages only"
        : `Show ${remaining} more passage${remaining === 1 ? "" : "s"}`;
      showMore.onclick = () => {
        showAll[atom.atom_id] = !showAll[atom.atom_id];
        renderDecision(parent, atom);
      };

      const confidenceChoices = document.getElementById("confidence-choices");
      confidenceChoices.replaceChildren(
        choiceButton("Sure", "sure", decision.confidence === "sure", () => {
          decision.confidence = "sure"; saveState(); renderDecision(parent, atom);
        }),
        choiceButton("Unsure / second review", "unsure", decision.confidence === "unsure", () => {
          decision.confidence = "unsure"; saveState(); renderDecision(parent, atom);
        }, "warn")
      );
      const note = document.getElementById("atom-note");
      note.value = decision.note || "";
      note.oninput = () => { decision.note = note.value; saveState(); };
    }

    function renderProgress() {
      const approved = packet.parents.filter(
        parent => state.decomposition[parent.parent_id] === "approved"
      ).length;
      const complete = items.filter(({ parent, atom }) => {
        if (state.decomposition[parent.parent_id] !== "approved") return false;
        const decision = state.decisions[atom.atom_id];
        if (!decision || !decision.label || !decision.confidence) return false;
        if (
          ["supports", "refutes"].includes(decision.label) &&
          decision.selected.length === 0
        ) return false;
        return !(decision.label === "retrieval_gap" && decision.selected.length > 0);
      }).length;
      document.getElementById("progress").textContent =
        `${approved}/${packet.parents.length} decompositions approved · ` +
        `${complete}/${items.length} steps complete`;
    }

    function exportCheckpoint() {
      state.reviewer = document.getElementById("reviewer").value.trim();
      saveState("Checkpoint prepared.");
      if (!state.reviewer) {
        alert("Enter a reviewer label before downloading.");
        return;
      }
      const decompositions = packet.parents.flatMap(parent => {
        const status = state.decomposition[parent.parent_id];
        if (!status) return [];
        return [{
          parent_id: parent.parent_id,
          status,
          note: state.decompositionNotes[parent.parent_id]?.trim() || null
        }];
      });
      const decisions = items.flatMap(({ parent, atom }) => {
        if (state.decomposition[parent.parent_id] !== "approved") return [];
        const decision = state.decisions[atom.atom_id];
        if (!decision || !decision.label || !decision.confidence) return [];
        if (
          ["supports", "refutes"].includes(decision.label) &&
          decision.selected.length === 0
        ) return [];
        const candidateMap = Object.fromEntries(
          parent.candidates.map(item => [item.candidate_id, item])
        );
        return [{
          atom_id: atom.atom_id,
          label: decision.label,
          confidence: decision.confidence,
          selected_passages: [...decision.selected].sort().map(candidateId => {
            const candidate = candidateMap[candidateId];
            return {
              candidate_id: candidate.candidate_id,
              source_id: candidate.source_id,
              passage_id: candidate.passage_id,
              passage_hash: candidate.passage_hash
            };
          }),
          note: decision.note?.trim() || null
        }];
      });
      const payload = {
        schema_version: "gold-lite-review-v0.1",
        rehearsal_id: packet.rehearsal_id,
        packet_sha256: packet.packet_sha256,
        reviewer: state.reviewer,
        exported_at_utc: new Date().toISOString(),
        decompositions,
        decisions
      };
      const blob = new Blob(
        [JSON.stringify(payload, null, 2) + "\n"],
        { type: "application/json" }
      );
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      link.download = `${packet.rehearsal_id}-checkpoint-${timestamp}.json`;
      link.click();
      URL.revokeObjectURL(link.href);
    }

    document.getElementById("reviewer").value = state.reviewer || "";
    document.getElementById("reviewer").addEventListener("input", event => {
      state.reviewer = event.target.value; saveState();
    });
    document.getElementById("previous").addEventListener("click", () => {
      if (current > 0) { current -= 1; render(); }
    });
    document.getElementById("next").addEventListener("click", () => {
      if (current < items.length - 1) { current += 1; render(); }
    });
    document.getElementById("download").addEventListener("click", exportCheckpoint);
    document.getElementById("clear").addEventListener("click", () => {
      const message =
        "Clear this rehearsal's browser-local progress? Download a checkpoint first if needed.";
      if (!confirm(message)) return;
      localStorage.removeItem(storageKey);
      state = structuredClone(emptyState);
      document.getElementById("reviewer").value = "";
      current = 0;
      render();
    });
    render();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
