"""Build and validate progressive human-gold Rung 2 and Rung 3 reviewers.

The reviewers are controlled DEV teaching packets. Rung 2 adds explicit polarity;
Rung 3 adds bounded insufficiency and a provenance-bound retrieval-gap cue. Neither
packet is representative accuracy, validation, or fresh-gate evidence.

Usage::

    python scripts/progressive_next_rungs.py build \
        --manifest <manifest.yaml> \
        --bundle-root <pilot-bundles/> \
        --out-dir <local-output/>

    python scripts/progressive_next_rungs.py validate \
        --manifest <manifest.yaml> \
        --bundle-root <pilot-bundles/> \
        --packet <local-output/review-packet.json> \
        --review <browser-export.json> \
        --out <new-sealed-review.yaml>
"""

# ruff: noqa: E501 -- the embedded self-contained HTML/JavaScript is line-oriented.

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Literal, Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

try:
    from scripts.gold_lite_review import (
        ReviewCandidate,
        SelectedPassage,
        _load_source_claims,
        _review_candidates,
        _shuffled_candidate_ids,
        _write_absent_or_identical,
    )
except ModuleNotFoundError:  # Direct `python scripts/progressive_next_rungs.py` execution.
    from gold_lite_review import (  # type: ignore[no-redef]
        ReviewCandidate,
        SelectedPassage,
        _load_source_claims,
        _review_candidates,
        _shuffled_candidate_ids,
        _write_absent_or_identical,
    )

MANIFEST_SCHEMA = "progressive-next-rungs-manifest-v0.1"
PACKET_SCHEMA = "progressive-next-rungs-packet-v0.1"
REVIEW_SCHEMA = "progressive-next-rungs-review-v0.1"
SEALED_SCHEMA = "progressive-next-rungs-sealed-dev-v0.1"
RUNG_2 = "rung-02-atomic-polarity"
RUNG_3 = "rung-03-bounded-sufficiency"
PACKET_FILENAME = "review-packet.json"
HTML_FILENAME = "review.html"
README_FILENAME = "README.md"
_PACKET_PLACEHOLDER = "__PROGRESSIVE_NEXT_PACKET_JSON__"

RungId = Literal["rung-02-atomic-polarity", "rung-03-bounded-sufficiency"]
Availability = Literal["not_applicable", "none_identified", "specific_missing_material"]
Relation = Literal[
    "supports",
    "refutes",
    "neither",
    "insufficient",
    "retrieval_gap",
    "needs_split",
    "unsure",
]
ResultOutcome = Literal[
    "supports",
    "refutes",
    "insufficient",
    "retrieval_gap",
    "escalate_relation",
    "escalate_atomicity",
    "second_review",
]

_PASSAGE_RATIONALE_RELATIONS = {"supports", "refutes", "insufficient"}
_RUNG_RELATIONS: dict[str, set[str]] = {
    RUNG_2: {"supports", "refutes", "neither", "needs_split", "unsure"},
    RUNG_3: {
        "supports",
        "refutes",
        "insufficient",
        "retrieval_gap",
        "needs_split",
        "unsure",
    },
}


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        str_strip_whitespace=True,
    )


class ManifestItem(_StrictModel):
    item_id: str = Field(min_length=1)
    source_claim_id: str = Field(min_length=1)
    claim_text: str = Field(min_length=1)
    availability: Availability
    missing_material_note: str | None = None

    @model_validator(mode="after")
    def validate_availability(self) -> Self:
        if self.availability == "specific_missing_material":
            if not self.missing_material_note:
                raise ValueError("specific missing material requires a note")
        elif self.missing_material_note is not None:
            raise ValueError("missing-material note requires specific_missing_material")
        return self


class ProgressiveManifest(_StrictModel):
    schema_version: Literal["progressive-next-rungs-manifest-v0.1"]
    ladder_id: str = Field(min_length=1)
    rung_id: RungId
    label: str = Field(min_length=1)
    selection_method: Literal["fixed-controlled-teaching-v0.1"]
    source_claim_count: int = Field(ge=1)
    candidate_count: int = Field(ge=1)
    items: list[ManifestItem] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_items(self) -> Self:
        _require_unique([item.item_id for item in self.items], "manifest item_id")
        _require_unique(
            [item.source_claim_id for item in self.items],
            "manifest source_claim_id",
        )
        for item in self.items:
            if self.rung_id == RUNG_2 and item.availability != "not_applicable":
                raise ValueError("Rung 2 items must use not_applicable availability")
            if self.rung_id == RUNG_3 and item.availability == "not_applicable":
                raise ValueError("Rung 3 items require an evidence-availability status")
        return self


class ProgressiveItem(_StrictModel):
    item_id: str = Field(min_length=1)
    claim_text: str = Field(min_length=1)
    availability: Availability
    missing_material_note: str | None = None
    candidates: list[ReviewCandidate] = Field(min_length=1)
    candidate_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_candidates(self) -> Self:
        _require_unique(self.candidate_ids, f"candidate_id in {self.item_id}")
        actual = {candidate.candidate_id for candidate in self.candidates}
        if set(self.candidate_ids) != actual:
            raise ValueError(f"{self.item_id}: candidate_ids do not match candidates")
        if self.availability == "specific_missing_material":
            if not self.missing_material_note:
                raise ValueError("specific missing material requires a note")
        elif self.missing_material_note is not None:
            raise ValueError("missing-material note requires specific_missing_material")
        return self


class ProgressivePacket(_StrictModel):
    schema_version: Literal["progressive-next-rungs-packet-v0.1"]
    ladder_id: str = Field(min_length=1)
    rung_id: RungId
    label: str = Field(min_length=1)
    selection_method: Literal["fixed-controlled-teaching-v0.1"]
    source_claim_count: int = Field(ge=1)
    candidate_count: int = Field(ge=1)
    packet_sha256: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    items: list[ProgressiveItem] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_items(self) -> Self:
        _require_unique([item.item_id for item in self.items], "packet item_id")
        return self


class ProgressiveDecision(_StrictModel):
    item_id: str = Field(min_length=1)
    relation: Relation
    reviewed_candidate_ids: list[str] = Field(default_factory=list)
    selected_passages: list[SelectedPassage] = Field(default_factory=list)
    note: str | None = None

    @model_validator(mode="after")
    def validate_decision_shape(self) -> Self:
        _require_unique(
            self.reviewed_candidate_ids,
            f"reviewed candidate in {self.item_id}",
        )
        _require_unique(
            [passage.candidate_id for passage in self.selected_passages],
            f"selected passage in {self.item_id}",
        )
        if self.relation in _PASSAGE_RATIONALE_RELATIONS:
            if len(self.selected_passages) != 1:
                raise ValueError(f"{self.relation} requires one selected rationale passage")
        elif self.selected_passages:
            raise ValueError(f"{self.relation} cannot select a rationale passage")
        return self


class ProgressiveReview(_StrictModel):
    schema_version: Literal["progressive-next-rungs-review-v0.1"]
    ladder_id: str = Field(min_length=1)
    rung_id: RungId
    packet_sha256: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    reviewer: str = Field(min_length=1)
    exported_at_utc: str = Field(min_length=1)
    decisions: list[ProgressiveDecision] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_decisions(self) -> Self:
        _require_unique([decision.item_id for decision in self.decisions], "decision item_id")
        return self


class ProgressiveResult(_StrictModel):
    item_id: str
    outcome: ResultOutcome
    derived_relation: Literal["supports", "refutes", "insufficient", "retrieval_gap"] | None = None
    reason: str


def load_manifest(path: Path) -> ProgressiveManifest:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"could not load progressive-rung manifest {path}: {exc}") from exc
    return ProgressiveManifest.model_validate(raw)


def load_review_packet(path: Path) -> ProgressivePacket:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load progressive-rung packet {path}: {exc}") from exc
    packet = ProgressivePacket.model_validate(raw)
    expected_hash = _packet_hash(_packet_payload(packet))
    if packet.packet_sha256 != expected_hash:
        raise ValueError(
            f"packet hash drift: recorded={packet.packet_sha256} actual={expected_hash}"
        )
    return packet


def load_review_export(path: Path) -> ProgressiveReview:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load progressive-rung review {path}: {exc}") from exc
    return ProgressiveReview.model_validate(raw)


def build_review_packet(
    manifest: ProgressiveManifest,
    bundle_root: Path,
    *,
    deviations_dir: Path,
) -> ProgressivePacket:
    """Build one controlled rung through CAL's fail-closed C-B loader."""
    bundles, claims = _load_source_claims(bundle_root, deviations_dir=deviations_dir)
    if len(claims) != manifest.source_claim_count:
        raise ValueError(
            f"source claim count drift: manifest={manifest.source_claim_count} actual={len(claims)}"
        )

    seed = f"{manifest.ladder_id}:{manifest.rung_id}"
    items: list[ProgressiveItem] = []
    for spec in manifest.items:
        source = claims.get(spec.source_claim_id)
        if source is None:
            raise ValueError(f"manifest contains unknown source claim ID: {spec.source_claim_id}")
        bundle_name, claim = source
        candidates = _review_candidates(claim, bundles[bundle_name])
        if len(candidates) != manifest.candidate_count:
            raise ValueError(
                f"{spec.source_claim_id}: expected {manifest.candidate_count} "
                f"canonical candidates, got {len(candidates)}"
            )
        items.append(
            ProgressiveItem(
                item_id=spec.item_id,
                claim_text=spec.claim_text,
                availability=spec.availability,
                missing_material_note=spec.missing_material_note,
                candidates=sorted(candidates, key=lambda item: item.candidate_id),
                candidate_ids=_shuffled_candidate_ids(
                    candidates,
                    seed=seed,
                    atom_id=spec.item_id,
                ),
            )
        )

    payload: dict[str, Any] = {
        "schema_version": PACKET_SCHEMA,
        "ladder_id": manifest.ladder_id,
        "rung_id": manifest.rung_id,
        "label": manifest.label,
        "selection_method": manifest.selection_method,
        "source_claim_count": manifest.source_claim_count,
        "candidate_count": manifest.candidate_count,
        "items": [item.model_dump(mode="json") for item in items],
    }
    return ProgressivePacket(packet_sha256=_packet_hash(payload), **payload)


def validate_packet_against_sources(
    packet: ProgressivePacket,
    manifest: ProgressiveManifest,
    bundle_root: Path,
    *,
    deviations_dir: Path,
) -> None:
    canonical = build_review_packet(
        manifest,
        bundle_root,
        deviations_dir=deviations_dir,
    )
    if packet != canonical:
        raise ValueError("packet does not match a fresh build from the manifest and source bundles")


def render_review_html(packet: ProgressivePacket) -> str:
    packet_json = json.dumps(
        packet.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).replace("<", "\\u003c")
    if _PACKET_PLACEHOLDER not in _HTML_TEMPLATE:
        raise RuntimeError("progressive-rung HTML packet placeholder is missing")
    return _HTML_TEMPLATE.replace(_PACKET_PLACEHOLDER, packet_json)


def validate_review_export(
    packet: ProgressivePacket,
    review: ProgressiveReview,
    *,
    require_complete: bool,
) -> list[ProgressiveResult]:
    if review.ladder_id != packet.ladder_id or review.rung_id != packet.rung_id:
        raise ValueError("review ladder/rung does not match packet")
    if review.packet_sha256 != packet.packet_sha256:
        raise ValueError("review packet_sha256 does not match packet")

    items = {item.item_id: item for item in packet.items}
    decisions = {decision.item_id: decision for decision in review.decisions}
    unknown = sorted(set(decisions) - set(items))
    if unknown:
        raise ValueError(f"review contains unknown item IDs: {unknown}")

    allowed_relations = _RUNG_RELATIONS[packet.rung_id]
    for item_id, decision in decisions.items():
        item = items[item_id]
        if decision.relation not in allowed_relations:
            raise ValueError(
                f"{item_id}: relation {decision.relation!r} is not allowed for {packet.rung_id}"
            )
        candidates = {candidate.candidate_id: candidate for candidate in item.candidates}
        allowed = set(candidates)
        reviewed = set(decision.reviewed_candidate_ids)
        unknown_reviewed = sorted(reviewed - allowed)
        if unknown_reviewed:
            raise ValueError(
                f"{item_id}: reviewed candidates are not available: {unknown_reviewed}"
            )

        for selected in decision.selected_passages:
            if selected.candidate_id not in candidates:
                raise ValueError(
                    f"{item_id}: selected candidate is not available: {selected.candidate_id}"
                )
            if selected.candidate_id not in reviewed:
                raise ValueError(f"{item_id}: selected passage was not recorded as reviewed")
            expected = candidates[selected.candidate_id]
            if selected.model_dump(mode="json") != {
                "candidate_id": expected.candidate_id,
                "source_id": expected.source_id,
                "passage_id": expected.passage_id,
                "passage_hash": expected.passage_hash,
            }:
                raise ValueError(f"{item_id}: selected passage provenance/hash drift")

        if decision.relation == "neither" and reviewed != allowed:
            raise ValueError(f"{item_id}: neither requires reviewing every candidate")
        if decision.relation == "insufficient":
            if item.availability != "none_identified":
                raise ValueError(
                    f"{item_id}: insufficient requires no specific missing material identified"
                )
            if reviewed != allowed:
                raise ValueError(f"{item_id}: insufficient requires reviewing every candidate")
        if decision.relation == "retrieval_gap":
            if item.availability != "specific_missing_material":
                raise ValueError(
                    f"{item_id}: retrieval_gap requires specifically identified missing material"
                )
            if reviewed != allowed:
                raise ValueError(f"{item_id}: retrieval_gap requires reviewing every candidate")

    if require_complete:
        missing = sorted(set(items) - set(decisions))
        if missing:
            raise ValueError(f"missing progressive-rung decisions: {missing}")

    return [
        _result_for(item.item_id, decisions[item.item_id])
        for item in packet.items
        if item.item_id in decisions
    ]


def build_sealed_review(
    packet: ProgressivePacket,
    review: ProgressiveReview,
    results: list[ProgressiveResult],
    *,
    review_sha256: str,
    complete: bool,
) -> dict[str, Any]:
    def count(outcome: str) -> int:
        return sum(result.outcome == outcome for result in results)

    return {
        "schema_version": SEALED_SCHEMA,
        "label": packet.label,
        "ladder_id": packet.ladder_id,
        "rung_id": packet.rung_id,
        "packet_sha256": packet.packet_sha256,
        "source_review_sha256": f"sha256:{review_sha256}",
        "reviewer": review.reviewer,
        "exported_at_utc": review.exported_at_utc,
        "complete": complete,
        "counts": {
            "items": len(packet.items),
            "decisions_recorded": len(review.decisions),
            "supports": count("supports"),
            "refutes": count("refutes"),
            "insufficient": count("insufficient"),
            "retrieval_gap": count("retrieval_gap"),
            "escalations": sum(
                result.outcome in {"escalate_relation", "escalate_atomicity", "second_review"}
                for result in results
            ),
        },
        "decisions": [decision.model_dump(mode="json") for decision in review.decisions],
        "results": [result.model_dump(mode="json") for result in results],
    }


def write_reviewer_artifacts(
    packet: ProgressivePacket,
    out_dir: Path,
    *,
    manifest_path: Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    packet_text = (
        json.dumps(packet.model_dump(mode="json"), indent=2, sort_keys=True, ensure_ascii=False)
        + "\n"
    )
    _write_absent_or_identical(out_dir / PACKET_FILENAME, packet_text)
    _write_absent_or_identical(out_dir / HTML_FILENAME, render_review_html(packet))
    _write_absent_or_identical(
        out_dir / README_FILENAME,
        _render_output_readme(packet, manifest_name=manifest_path.name),
    )


def _result_for(item_id: str, decision: ProgressiveDecision) -> ProgressiveResult:
    if decision.relation in {"supports", "refutes", "insufficient", "retrieval_gap"}:
        relation = decision.relation
        reason = (
            "human relation is bound to the packet's named missing material"
            if relation == "retrieval_gap"
            else "human relation is bound to an exact reviewed source passage"
        )
        return ProgressiveResult(
            item_id=item_id,
            outcome=relation,
            derived_relation=relation,
            reason=reason,
        )
    if decision.relation == "neither":
        return ProgressiveResult(
            item_id=item_id,
            outcome="escalate_relation",
            reason="no direct support or refutation found in the bounded candidates",
        )
    if decision.relation == "needs_split":
        return ProgressiveResult(
            item_id=item_id,
            outcome="escalate_atomicity",
            reason="claim needs decomposition before relation coding",
        )
    return ProgressiveResult(
        item_id=item_id,
        outcome="second_review",
        reason="reviewer preserved uncertainty",
    )


def _packet_payload(packet: ProgressivePacket) -> dict[str, Any]:
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
    return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_unique(values: list[str], label: str) -> None:
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        raise ValueError(f"duplicate {label}: {duplicates}")


def _render_output_readme(packet: ProgressivePacket, *, manifest_name: str) -> str:
    title = (
        "Rung 2 — atomic polarity" if packet.rung_id == RUNG_2 else "Rung 3 — bounded sufficiency"
    )
    if packet.rung_id == RUNG_2:
        task = "Classify explicit support versus explicit refutation. Missing support is not refutation."
        rationale = "Select the exact rationale passage for every support or refutation."
    else:
        task = (
            "Classify support, refutation, bounded insufficiency, or a specifically identified "
            "retrieval gap."
        )
        rationale = (
            "Select the exact rationale passage for support, refutation, or insufficiency. "
            "The named missing-source statement binds a retrieval gap."
        )
    return f"""# Progressive human-gold ladder — {title}

**Controlled DEV teaching review — not representative CAL accuracy and not gate evidence.**

## Packet

- ladder: `{packet.ladder_id}`
- rung: `{packet.rung_id}`
- packet hash: `{packet.packet_sha256}`
- fixed items: {len(packet.items)}
- canonical candidates per item: {packet.candidate_count}
- source claim inventory: {packet.source_claim_count}
- selection: `{packet.selection_method}`
- manifest: `{manifest_name}`

The reviewer contains controlled atomic statements and read-only Evidence Bundler candidates.
It contains no CAL verdict, old human gold, model answer, or hidden target relation.

## Review

1. Open `review.html` locally and enter a reviewer label.
2. Read one passage at a time; outside knowledge does not count.
3. {task}
4. {rationale}
5. Download the JSON checkpoint after all items are resolved or escalated.

Validate a completed export from the CAL workbench with:

```bash
.venv/bin/python scripts/progressive_next_rungs.py validate \\
  --manifest <path-to>/{manifest_name} \\
  --bundle-root <path-to-pilot-bundles> \\
  --packet <this-directory>/review-packet.json \\
  --review <browser-export.json> \\
  --out <new-sealed-review.yaml>
```

Use `--allow-incomplete` only to inspect a checkpoint. It does not create a completed reference.
"""


def _build_command(args: argparse.Namespace) -> None:
    manifest = load_manifest(args.manifest)
    packet = build_review_packet(
        manifest,
        args.bundle_root,
        deviations_dir=args.deviations_dir or args.out_dir / "deviations",
    )
    write_reviewer_artifacts(packet, args.out_dir, manifest_path=args.manifest)
    print(f"rung: {packet.rung_id}")
    print(f"items: {len(packet.items)}")
    print(f"packet_sha256: {packet.packet_sha256}")
    print(f"review: {args.out_dir / HTML_FILENAME}")


def _validate_command(args: argparse.Namespace) -> None:
    manifest = load_manifest(args.manifest)
    packet = load_review_packet(args.packet)
    validate_packet_against_sources(
        packet,
        manifest,
        args.bundle_root,
        deviations_dir=args.deviations_dir or args.packet.parent / "deviations",
    )
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
    _write_absent_or_identical(
        args.out,
        yaml.safe_dump(sealed, sort_keys=False, allow_unicode=True),
    )
    print(f"complete: {require_complete}")
    print(f"decisions: {len(review.decisions)}")
    print(f"wrote: {args.out}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Build a Rung 2 or Rung 3 local reviewer.")
    build.add_argument("--manifest", type=Path, required=True)
    build.add_argument("--bundle-root", type=Path, required=True)
    build.add_argument("--out-dir", type=Path, required=True)
    build.add_argument("--deviations-dir", type=Path)
    build.set_defaults(func=_build_command)

    validate = subparsers.add_parser("validate", help="Validate and seal a browser export.")
    validate.add_argument("--manifest", type=Path, required=True)
    validate.add_argument("--bundle-root", type=Path, required=True)
    validate.add_argument("--deviations-dir", type=Path)
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
  <title>Progressive Human Gold — Next Rung</title>
  <style>
    :root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    body { margin: 0; background: #f4f1eb; color: #17211b; }
    main { max-width: 900px; margin: 0 auto; padding: 24px 16px 56px; }
    .card { background: #fffdf8; border: 1px solid #d8d2c5; border-radius: 14px; padding: 18px; margin: 14px 0; box-shadow: 0 2px 10px rgba(30, 35, 31, 0.05); }
    .warning { border-left: 6px solid #b15f22; background: #fff6ea; }
    .availability { border-left: 6px solid #4d6b5a; background: #f0f7f2; }
    h1 { line-height: 1.25; }
    .claim { font-size: 1.42rem; }
    .question { font-weight: 700; margin-top: 18px; }
    .small { color: #59645d; font-size: 0.92rem; }
    .status { font-weight: 700; }
    .passage { white-space: pre-wrap; background: #f6f7f4; border: 1px solid #d5dcd6; border-radius: 10px; padding: 14px; margin-top: 8px; line-height: 1.5; }
    .selected-passage { border: 3px solid #2f6f4e; }
    .buttons { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
    button { border: 1px solid #758078; border-radius: 9px; background: #fff; color: #17211b; padding: 9px 12px; cursor: pointer; font-weight: 650; }
    button:hover:not(:disabled) { background: #edf3ee; }
    button.selected { background: #2f6f4e; color: white; border-color: #2f6f4e; }
    button.primary { background: #244f3a; color: white; border-color: #244f3a; }
    button:disabled { cursor: not-allowed; opacity: 0.42; }
    input, textarea { width: 100%; box-sizing: border-box; border: 1px solid #aeb7b0; border-radius: 8px; padding: 10px; font: inherit; }
    textarea { min-height: 76px; }
    .nav { display: flex; justify-content: space-between; gap: 10px; margin-top: 18px; }
    .hidden { display: none; }
    code { overflow-wrap: anywhere; }
    ul { line-height: 1.55; }
  </style>
</head>
<body>
<main>
  <section class="card warning">
    <strong id="rung-title"></strong>
    <p id="rung-summary"></p>
    <p><strong>Missing support is not refutation.</strong> Choose refutes only when a passage positively establishes an incompatible fact.</p>
    <p class="small">DEV teaching review only. This is not representative CAL accuracy, validation, or gate evidence.</p>
  </section>

  <section class="card">
    <label for="reviewer"><strong>Reviewer label</strong></label>
    <input id="reviewer" placeholder="Example: Cameron-rung2-dev">
    <p class="small">Packet: <code id="packet-hash"></code></p>
    <p id="progress" class="status"></p>
  </section>

  <section class="card">
    <p class="question">Quick definitions</p>
    <ul id="definitions"></ul>
  </section>

  <section id="review-card" class="card">
    <p id="item-number" class="small"></p>
    <h1 id="claim" class="claim"></h1>

    <div id="availability" class="card availability hidden"></div>

    <p class="question">Read the bounded passages</p>
    <p class="small">Use only what is shown. Read one passage at a time.</p>
    <div id="passage-meta" class="small"></div>
    <div id="passage" class="passage"></div>
    <div class="buttons">
      <button id="select-passage" type="button">Use this passage as rationale</button>
      <button id="next-passage" type="button">Show another passage</button>
    </div>

    <p class="question">Choose the relation</p>
    <div id="relation" class="buttons"></div>
    <p id="unlock-note" class="small"></p>

    <p class="question">Optional note</p>
    <textarea id="note" placeholder="Only if something was confusing."></textarea>

    <div class="nav">
      <button id="previous" type="button">Previous</button>
      <button id="next" type="button">Next</button>
    </div>
  </section>

  <section class="card">
    <p class="small">The browser autosaves locally. Downloads are additive; preserve earlier files.</p>
    <div class="buttons">
      <button id="download" class="primary" type="button">Download checkpoint JSON</button>
      <button id="clear" type="button">Clear local progress</button>
    </div>
  </section>
</main>

<script>
  const packet = __PROGRESSIVE_NEXT_PACKET_JSON__;
  const isRung2 = packet.rung_id === "rung-02-atomic-polarity";
  const storageKey = `progressive-next:${packet.packet_sha256}`;
  let index = 0;
  let state = loadState();

  const passageRationaleRelations = new Set(["supports", "refutes", "insufficient"]);

  function blankDecision() {
    return {relation: null, reviewedCandidateIds: [], selectedCandidateId: null, candidateIndex: 0, note: ""};
  }

  function loadState() {
    const fallback = {reviewer: "", decisions: {}};
    try {
      const parsed = JSON.parse(localStorage.getItem(storageKey));
      return parsed && typeof parsed === "object" ? {...fallback, ...parsed} : fallback;
    } catch (_) { return fallback; }
  }

  function saveState() {
    state.reviewer = document.getElementById("reviewer").value;
    localStorage.setItem(storageKey, JSON.stringify(state));
    renderProgress();
  }

  function current() {
    const item = packet.items[index];
    if (!state.decisions[item.item_id]) state.decisions[item.item_id] = blankDecision();
    return [item, state.decisions[item.item_id]];
  }

  function candidate(item, decision) {
    const id = item.candidate_ids[decision.candidateIndex % item.candidate_ids.length];
    return item.candidates.find(value => value.candidate_id === id);
  }

  function relationOptions() {
    if (isRung2) {
      return [["Supports", "supports"], ["Refutes", "refutes"], ["Neither", "neither"], ["Needs split", "needs_split"], ["Not sure", "unsure"]];
    }
    return [["Supports", "supports"], ["Refutes", "refutes"], ["Insufficient", "insufficient"], ["Retrieval gap", "retrieval_gap"], ["Needs split", "needs_split"], ["Not sure", "unsure"]];
  }

  function disabledRelations(item, decision) {
    const allViewed = new Set(decision.reviewedCandidateIds || []).size === item.candidate_ids.length;
    if (isRung2) return allViewed ? [] : ["neither"];
    const disabled = [];
    if (!allViewed || item.availability !== "none_identified") disabled.push("insufficient");
    if (!allViewed || item.availability !== "specific_missing_material") disabled.push("retrieval_gap");
    return disabled;
  }

  function renderButtons(containerId, options, selected, handler, disabledValues = []) {
    const container = document.getElementById(containerId);
    container.replaceChildren();
    for (const [label, value] of options) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = label;
      button.className = selected === value ? "selected" : "";
      button.disabled = disabledValues.includes(value);
      button.addEventListener("click", () => handler(value));
      container.appendChild(button);
    }
  }

  function render() {
    const [item, decision] = current();
    const shown = candidate(item, decision);
    if (!Array.isArray(decision.reviewedCandidateIds)) decision.reviewedCandidateIds = [];
    if (!decision.reviewedCandidateIds.includes(shown.candidate_id)) {
      decision.reviewedCandidateIds.push(shown.candidate_id);
      saveState();
    }
    const reviewedCount = new Set(decision.reviewedCandidateIds).size;
    const allViewed = reviewedCount === item.candidate_ids.length;

    document.getElementById("item-number").textContent = `Item ${index + 1} of ${packet.items.length} · ${item.item_id}`;
    document.getElementById("claim").textContent = item.claim_text;
    document.getElementById("note").value = decision.note || "";

    const availability = document.getElementById("availability");
    if (isRung2) {
      availability.className = "hidden";
    } else {
      availability.className = "card availability";
      if (item.availability === "specific_missing_material") {
        availability.innerHTML = `<strong>Specific missing material identified</strong><p>${escapeHtml(item.missing_material_note)}</p>`;
      } else {
        availability.innerHTML = "<strong>No specific missing material identified</strong><p>Judge only the five bounded passages. If relevant evidence still does not establish the full claim, use Insufficient after viewing all five.</p>";
      }
    }

    document.getElementById("passage-meta").textContent = `${shown.source_title}${shown.section ? " · " + shown.section : ""} · viewed ${reviewedCount} of ${item.candidate_ids.length}`;
    const passage = document.getElementById("passage");
    passage.textContent = shown.text;
    passage.className = decision.selectedCandidateId === shown.candidate_id ? "passage selected-passage" : "passage";

    const select = document.getElementById("select-passage");
    select.textContent = decision.selectedCandidateId === shown.candidate_id ? "Rationale selected" : "Use this passage as rationale";
    select.className = decision.selectedCandidateId === shown.candidate_id ? "selected" : "";
    select.onclick = () => {
      decision.selectedCandidateId = decision.selectedCandidateId === shown.candidate_id ? null : shown.candidate_id;
      if (!decision.selectedCandidateId && passageRationaleRelations.has(decision.relation)) decision.relation = null;
      saveState(); render();
    };

    const nextPassage = document.getElementById("next-passage");
    nextPassage.disabled = item.candidate_ids.length === 1;
    nextPassage.onclick = () => {
      decision.candidateIndex = (decision.candidateIndex + 1) % item.candidate_ids.length;
      saveState(); render();
    };

    renderButtons("relation", relationOptions(), decision.relation, value => {
      decision.relation = value;
      if (passageRationaleRelations.has(value)) {
        decision.selectedCandidateId = decision.selectedCandidateId || shown.candidate_id;
      } else {
        decision.selectedCandidateId = null;
      }
      saveState(); render();
    }, disabledRelations(item, decision));

    if (isRung2) {
      document.getElementById("unlock-note").textContent = allViewed ? "All passages viewed." : "Neither unlocks after all five passages are viewed.";
    } else if (item.availability === "specific_missing_material") {
      document.getElementById("unlock-note").textContent = allViewed ? "Retrieval gap is available; the named missing-source statement is the rationale." : "Retrieval gap unlocks after all five passages are viewed.";
    } else {
      document.getElementById("unlock-note").textContent = allViewed ? "Insufficient is available; select the closest partial passage." : "Insufficient unlocks after all five passages are viewed.";
    }

    document.getElementById("previous").disabled = index === 0;
    document.getElementById("next").disabled = index === packet.items.length - 1;
    renderProgress();
  }

  function isComplete(item, decision) {
    if (!decision || !decision.relation) return false;
    const reviewedCount = new Set(decision.reviewedCandidateIds || []).size;
    if (passageRationaleRelations.has(decision.relation) && !decision.selectedCandidateId) return false;
    if (["neither", "insufficient", "retrieval_gap"].includes(decision.relation)) {
      return reviewedCount === item.candidate_ids.length;
    }
    return true;
  }

  function renderProgress() {
    const complete = packet.items.filter(item => isComplete(item, state.decisions[item.item_id])).length;
    document.getElementById("progress").textContent = `${complete}/${packet.items.length} items resolved or escalated`;
  }

  function selectedPassage(item, id) {
    if (!id) return [];
    const value = item.candidates.find(candidateValue => candidateValue.candidate_id === id);
    return [{candidate_id: value.candidate_id, source_id: value.source_id, passage_id: value.passage_id, passage_hash: value.passage_hash}];
  }

  function exportReview() {
    const decisions = [];
    for (const item of packet.items) {
      const value = state.decisions[item.item_id];
      if (!isComplete(item, value)) continue;
      decisions.push({
        item_id: item.item_id,
        relation: value.relation,
        reviewed_candidate_ids: item.candidate_ids.filter(id => (value.reviewedCandidateIds || []).includes(id)),
        selected_passages: passageRationaleRelations.has(value.relation) ? selectedPassage(item, value.selectedCandidateId) : [],
        note: value.note.trim() || null
      });
    }
    return {
      schema_version: "progressive-next-rungs-review-v0.1",
      ladder_id: packet.ladder_id,
      rung_id: packet.rung_id,
      packet_sha256: packet.packet_sha256,
      reviewer: document.getElementById("reviewer").value.trim(),
      exported_at_utc: new Date().toISOString(),
      decisions
    };
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, character => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", "'":"&#39;", '"':"&quot;"})[character]);
  }

  function configureRung() {
    document.getElementById("rung-title").textContent = isRung2 ? "Rung 2 — atomic polarity" : "Rung 3 — bounded sufficiency";
    document.getElementById("rung-summary").textContent = isRung2 ? "Find a passage that supports or positively refutes each exact claim." : "Separate direct relations from evidence that is too weak and from specifically identified missing material.";
    const definitions = isRung2 ? [
      "Supports: a passage says the same thing as the claim.",
      "Refutes: a passage positively establishes an incompatible fact.",
      "Neither: after all five passages, none directly supports or refutes; this escalates rather than becoming a guessed label.",
      "Needs split / Not sure: preserve the problem for another review."
    ] : [
      "Supports: a passage establishes the exact claim.",
      "Refutes: a passage establishes an incompatible fact.",
      "Insufficient: relevant evidence is present, but a key scope, strength, causal, or attribution element remains unproved.",
      "Retrieval gap: specific material needed to decide is known to be absent.",
      "Needs split / Not sure: preserve the problem for another review."
    ];
    const list = document.getElementById("definitions");
    list.replaceChildren(...definitions.map(text => { const li = document.createElement("li"); li.textContent = text; return li; }));
  }

  document.getElementById("reviewer").value = state.reviewer || "";
  document.getElementById("packet-hash").textContent = packet.packet_sha256;
  document.getElementById("reviewer").addEventListener("input", saveState);
  document.getElementById("note").addEventListener("input", event => { current()[1].note = event.target.value; saveState(); });
  document.getElementById("previous").addEventListener("click", () => { if (index > 0) { index -= 1; render(); } });
  document.getElementById("next").addEventListener("click", () => { if (index < packet.items.length - 1) { index += 1; render(); } });
  document.getElementById("download").addEventListener("click", () => {
    const review = exportReview();
    if (!review.reviewer) { alert("Enter a reviewer label before downloading."); return; }
    const blob = new Blob([JSON.stringify(review, null, 2) + "\n"], {type: "application/json"});
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    const shortRung = isRung2 ? "rung2" : "rung3";
    link.download = `progressive-gold-${shortRung}-${new Date().toISOString().replace(/[:.]/g, "-")}.json`;
    link.click();
    URL.revokeObjectURL(link.href);
  });
  document.getElementById("clear").addEventListener("click", () => {
    if (!confirm("Clear this packet's browser-local progress? Download a checkpoint first if needed.")) return;
    localStorage.removeItem(storageKey); state = {reviewer: "", decisions: {}}; index = 0; document.getElementById("reviewer").value = ""; render();
  });

  configureRung();
  render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
