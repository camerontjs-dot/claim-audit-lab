"""Build and validate the five-item progressive Gold Rung 1 reviewer.

Rung 1 is a DEV positive-control workflow check. It asks whether a claim is atomic,
whether the bounded packet directly supports it, and which exact passage provides the
rationale. Negative or uncertain answers escalate; they never become guessed labels.

Usage::

    python scripts/progressive_gold_review.py build \
        --manifest <manifest.yaml> \
        --bundle-root <pilot-bundles/> \
        --out-dir <local-output/>

    python scripts/progressive_gold_review.py validate \
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
except ModuleNotFoundError:  # Direct `python scripts/progressive_gold_review.py` execution.
    from gold_lite_review import (  # type: ignore[no-redef]
        ReviewCandidate,
        SelectedPassage,
        _load_source_claims,
        _review_candidates,
        _shuffled_candidate_ids,
        _write_absent_or_identical,
    )

MANIFEST_SCHEMA = "progressive-gold-manifest-v0.1"
PACKET_SCHEMA = "progressive-gold-review-packet-v0.1"
REVIEW_SCHEMA = "progressive-gold-review-v0.1"
SEALED_SCHEMA = "progressive-gold-sealed-dev-v0.1"
RUNG_ID = "rung-01-direct-support"
PACKET_FILENAME = "review-packet.json"
HTML_FILENAME = "review.html"
README_FILENAME = "README.md"
_PACKET_PLACEHOLDER = "__PROGRESSIVE_GOLD_PACKET_JSON__"

Atomicity = Literal["yes", "needs_split", "unsure"]
DirectSupport = Literal["yes", "no", "unsure"]
RungOutcome = Literal["supports", "escalate_atomicity", "escalate_relation", "second_review"]


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        str_strip_whitespace=True,
    )


class FixedSelection(_StrictModel):
    method: Literal["fixed-positive-control-v0.1"]
    source_claim_count: int = Field(ge=1)
    claim_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_ids(self) -> Self:
        _require_unique(self.claim_ids, "selection claim_id")
        return self


class ProgressiveManifest(_StrictModel):
    schema_version: Literal["progressive-gold-manifest-v0.1"]
    ladder_id: str = Field(min_length=1)
    rung_id: Literal["rung-01-direct-support"]
    label: str = Field(min_length=1)
    selection: FixedSelection


class ProgressiveItem(_StrictModel):
    claim_id: str = Field(min_length=1)
    claim_text: str = Field(min_length=1)
    candidates: list[ReviewCandidate] = Field(min_length=1)
    candidate_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_candidate_ids(self) -> Self:
        _require_unique(self.candidate_ids, f"candidate_id in {self.claim_id}")
        actual = {candidate.candidate_id for candidate in self.candidates}
        if set(self.candidate_ids) != actual:
            raise ValueError(f"{self.claim_id}: candidate_ids do not match candidates")
        return self


class ProgressivePacket(_StrictModel):
    schema_version: Literal["progressive-gold-review-packet-v0.1"]
    ladder_id: str = Field(min_length=1)
    rung_id: Literal["rung-01-direct-support"]
    label: str = Field(min_length=1)
    source_claim_count: int = Field(ge=1)
    selection_method: Literal["fixed-positive-control-v0.1"]
    packet_sha256: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    items: list[ProgressiveItem] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_items(self) -> Self:
        _require_unique([item.claim_id for item in self.items], "packet claim_id")
        return self


class ProgressiveDecision(_StrictModel):
    claim_id: str = Field(min_length=1)
    atomicity: Atomicity
    direct_support: DirectSupport | None = None
    reviewed_candidate_ids: list[str] = Field(default_factory=list)
    selected_passages: list[SelectedPassage] = Field(default_factory=list)
    note: str | None = None

    @model_validator(mode="after")
    def validate_decision_path(self) -> Self:
        _require_unique(
            self.reviewed_candidate_ids,
            f"reviewed candidate in {self.claim_id}",
        )
        _require_unique(
            [passage.candidate_id for passage in self.selected_passages],
            f"selected passage in {self.claim_id}",
        )
        if self.atomicity != "yes":
            if self.direct_support is not None or self.selected_passages:
                raise ValueError(
                    "non-atomic or unsure items cannot record direct support or passages"
                )
            return self
        if self.direct_support is None:
            raise ValueError("atomic items require a direct-support answer")
        if self.direct_support == "yes" and not self.selected_passages:
            raise ValueError("direct support requires at least one selected passage")
        if self.direct_support != "yes" and self.selected_passages:
            raise ValueError("no or unsure direct support cannot select a passage")
        return self


class ProgressiveReview(_StrictModel):
    schema_version: Literal["progressive-gold-review-v0.1"]
    ladder_id: str = Field(min_length=1)
    rung_id: Literal["rung-01-direct-support"]
    packet_sha256: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    reviewer: str = Field(min_length=1)
    exported_at_utc: str = Field(min_length=1)
    decisions: list[ProgressiveDecision] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_decisions(self) -> Self:
        _require_unique([decision.claim_id for decision in self.decisions], "decision claim_id")
        return self


class ProgressiveResult(_StrictModel):
    claim_id: str
    outcome: RungOutcome
    derived_relation: Literal["supports"] | None = None
    reason: str


def load_manifest(path: Path) -> ProgressiveManifest:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"could not load progressive-gold manifest {path}: {exc}") from exc
    return ProgressiveManifest.model_validate(raw)


def load_review_packet(path: Path) -> ProgressivePacket:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load progressive-gold packet {path}: {exc}") from exc
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
        raise ValueError(f"could not load progressive-gold review {path}: {exc}") from exc
    return ProgressiveReview.model_validate(raw)


def build_review_packet(
    manifest: ProgressiveManifest,
    bundle_root: Path,
    *,
    deviations_dir: Path,
) -> ProgressivePacket:
    """Build a fixed positive-control packet through CAL's fail-closed C-B loader."""
    bundles, claims = _load_source_claims(bundle_root, deviations_dir=deviations_dir)
    if len(claims) != manifest.selection.source_claim_count:
        raise ValueError(
            "source claim count drift: "
            f"manifest={manifest.selection.source_claim_count} actual={len(claims)}"
        )

    unknown = sorted(set(manifest.selection.claim_ids) - set(claims))
    if unknown:
        raise ValueError(f"manifest contains unknown source claim IDs: {unknown}")

    seed = f"{manifest.ladder_id}:{manifest.rung_id}"
    items: list[ProgressiveItem] = []
    for claim_id in manifest.selection.claim_ids:
        bundle_name, claim = claims[claim_id]
        candidates = _review_candidates(claim, bundles[bundle_name])
        if not candidates:
            raise ValueError(f"{claim_id}: source claim has no candidate passages")
        items.append(
            ProgressiveItem(
                claim_id=claim_id,
                claim_text=claim.claim_text,
                candidates=sorted(candidates, key=lambda item: item.candidate_id),
                candidate_ids=_shuffled_candidate_ids(
                    candidates,
                    seed=seed,
                    atom_id=claim_id,
                ),
            )
        )

    payload: dict[str, Any] = {
        "schema_version": PACKET_SCHEMA,
        "ladder_id": manifest.ladder_id,
        "rung_id": manifest.rung_id,
        "label": manifest.label,
        "source_claim_count": manifest.selection.source_claim_count,
        "selection_method": manifest.selection.method,
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
    """Require the packet to equal a fresh fail-closed build from canonical inputs."""
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
        raise RuntimeError("progressive-gold HTML packet placeholder is missing")
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

    items = {item.claim_id: item for item in packet.items}
    decisions = {decision.claim_id: decision for decision in review.decisions}
    unknown = sorted(set(decisions) - set(items))
    if unknown:
        raise ValueError(f"review contains unknown claim IDs: {unknown}")

    for claim_id, decision in decisions.items():
        item = items[claim_id]
        candidates = {candidate.candidate_id: candidate for candidate in item.candidates}
        allowed = set(candidates)
        reviewed = set(decision.reviewed_candidate_ids)
        unknown_reviewed = sorted(reviewed - allowed)
        if unknown_reviewed:
            raise ValueError(
                f"{claim_id}: reviewed candidates are not available: {unknown_reviewed}"
            )
        for selected in decision.selected_passages:
            if selected.candidate_id not in candidates:
                raise ValueError(
                    f"{claim_id}: selected candidate is not available: {selected.candidate_id}"
                )
            if selected.candidate_id not in reviewed:
                raise ValueError(f"{claim_id}: selected passage was not recorded as reviewed")
            expected = candidates[selected.candidate_id]
            if selected.model_dump(mode="json") != {
                "candidate_id": expected.candidate_id,
                "source_id": expected.source_id,
                "passage_id": expected.passage_id,
                "passage_hash": expected.passage_hash,
            }:
                raise ValueError(f"{claim_id}: selected passage provenance/hash drift")
        if decision.direct_support == "no" and reviewed != allowed:
            raise ValueError(f"{claim_id}: direct-support no requires reviewing every candidate")

    if require_complete:
        missing = sorted(set(items) - set(decisions))
        if missing:
            raise ValueError(f"missing progressive-gold decisions: {missing}")

    return [
        _result_for(item, decisions.get(item.claim_id))
        for item in packet.items
        if item.claim_id in decisions or not require_complete
    ]


def build_sealed_review(
    packet: ProgressivePacket,
    review: ProgressiveReview,
    results: list[ProgressiveResult],
    *,
    review_sha256: str,
    complete: bool,
) -> dict[str, Any]:
    return {
        "schema_version": SEALED_SCHEMA,
        "label": "DEV positive-control reference; not representative accuracy or gate evidence",
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
            "supports": sum(result.outcome == "supports" for result in results),
            "escalations": sum(result.outcome != "supports" for result in results),
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


def _result_for(
    item: ProgressiveItem,
    decision: ProgressiveDecision | None,
) -> ProgressiveResult:
    if decision is None:
        return ProgressiveResult(
            claim_id=item.claim_id,
            outcome="second_review",
            reason="no complete decision recorded",
        )
    if decision.atomicity == "needs_split":
        return ProgressiveResult(
            claim_id=item.claim_id,
            outcome="escalate_atomicity",
            reason="claim needs decomposition before relation coding",
        )
    if decision.atomicity == "unsure" or decision.direct_support == "unsure":
        return ProgressiveResult(
            claim_id=item.claim_id,
            outcome="second_review",
            reason="reviewer preserved uncertainty",
        )
    if decision.direct_support == "no":
        return ProgressiveResult(
            claim_id=item.claim_id,
            outcome="escalate_relation",
            reason="no direct support found; harder relation coding is required",
        )
    if decision.direct_support == "yes":
        return ProgressiveResult(
            claim_id=item.claim_id,
            outcome="supports",
            derived_relation="supports",
            reason="atomic claim has direct support and an exact rationale passage",
        )
    raise AssertionError("unhandled progressive-gold decision path")


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
    return f"""# Progressive human-gold ladder — Rung 1

**DEV positive-control review — not representative CAL accuracy and not gate evidence.**

## Packet

- ladder: `{packet.ladder_id}`
- rung: `{packet.rung_id}`
- packet hash: `{packet.packet_sha256}`
- fixed items: {len(packet.items)}
- source claim inventory: {packet.source_claim_count}
- selection: `{packet.selection_method}`
- manifest: `{manifest_name}`

These claims were deliberately curated to be simple, affirmative, atomic positive controls.
Their result can test whether the review workflow is understandable; it cannot estimate
performance on the full corpus. Evidence Bundler candidates are reused read-only. CAL output,
old human gold, and model-panel answers are absent.

## Review

1. Open `review.html` locally.
2. Enter a reviewer label.
3. Answer whether the claim contains one checkable idea.
4. If yes, inspect the passages one at a time and answer whether any directly supports it.
5. A yes answer requires selecting the exact rationale passage.
6. A no answer becomes available only after every bounded passage has been viewed.
7. No, needs-split, and unsure answers are escalations, not guessed relation labels.
8. Download a checkpoint. Preserve every export.

Validate a completed export from the CAL workbench with:

```bash
.venv/bin/python scripts/progressive_gold_review.py validate \\
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
    print(f"supports: {sum(result.outcome == 'supports' for result in results)}")
    print(f"escalations: {sum(result.outcome != 'supports' for result in results)}")
    print(f"wrote: {args.out}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Build the Rung 1 local reviewer.")
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
  <title>Progressive Gold — Rung 1</title>
  <style>
    :root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #f4f0e8; color: #20231f; }
    main { max-width: 920px; margin: 0 auto; padding: 24px 18px 60px; }
    .card { background: #fffdf8; border: 1px solid #d8d2c5; border-radius: 14px; padding: 20px; margin: 14px 0; box-shadow: 0 4px 18px rgba(40, 35, 25, .06); }
    .warning { background: #fff4d6; border-color: #e2c36f; }
    .claim { font-size: 1.35rem; line-height: 1.45; margin: 8px 0 16px; }
    .small { color: #64665f; font-size: .9rem; }
    .question { font-weight: 750; margin: 18px 0 10px; }
    .buttons { display: flex; flex-wrap: wrap; gap: 8px; }
    button { border: 1px solid #777d72; border-radius: 9px; background: #fff; padding: 9px 13px; cursor: pointer; font: inherit; }
    button.selected { background: #244f3c; border-color: #244f3c; color: #fff; }
    button.primary { background: #244f3c; border-color: #244f3c; color: #fff; font-weight: 700; }
    button:disabled { cursor: not-allowed; opacity: .45; }
    .passage { white-space: pre-wrap; line-height: 1.45; background: #f5f7f2; border: 1px solid #d5dbd1; border-radius: 10px; padding: 14px; }
    .selected-passage { border: 2px solid #347154; }
    .nav { display: flex; justify-content: space-between; gap: 10px; margin-top: 16px; }
    input, textarea { width: 100%; border: 1px solid #b9b7af; border-radius: 8px; padding: 9px; font: inherit; }
    textarea { min-height: 70px; resize: vertical; }
    .hidden { display: none; }
    .status { font-weight: 700; color: #244f3c; }
    @media (max-width: 600px) { .buttons button { flex: 1 1 42%; } }
  </style>
</head>
<body>
<main>
  <section class="card warning">
    <strong>DEV positive-control review only.</strong>
    This five-item set tests whether the human workflow is simple. It is not representative
    CAL accuracy, validation, or gate evidence.
  </section>

  <section class="card">
    <label for="reviewer"><strong>Reviewer label</strong></label>
    <input id="reviewer" placeholder="Example: Cameron-rung1-dev">
    <p class="small">Packet: <code id="packet-hash"></code></p>
    <p id="progress" class="status"></p>
  </section>

  <section id="review-card" class="card">
    <p id="item-number" class="small"></p>
    <h1 id="claim" class="claim"></h1>

    <p class="question">1. Does this claim contain one checkable idea?</p>
    <div id="atomicity" class="buttons"></div>

    <div id="evidence-step" class="hidden">
      <p class="question">2. Does any passage directly support this exact claim?</p>
      <p class="small">Read one passage at a time. Outside knowledge does not count.</p>
      <div id="passage-meta" class="small"></div>
      <div id="passage" class="passage"></div>
      <div class="buttons" style="margin-top: 10px">
        <button id="select-passage" type="button">Use this passage as rationale</button>
        <button id="next-passage" type="button">Show another passage</button>
      </div>
      <div id="direct-support" class="buttons" style="margin-top: 14px"></div>
    </div>

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
  const packet = __PROGRESSIVE_GOLD_PACKET_JSON__;
  const storageKey = `progressive-gold:${packet.packet_sha256}`;
  const byId = Object.fromEntries(packet.items.map(item => [item.claim_id, item]));
  let index = 0;
  let state = loadState();

  function blankDecision() {
    return {atomicity: null, directSupport: null, reviewedCandidateIds: [], selectedCandidateId: null, candidateIndex: 0, note: ""};
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
    if (!state.decisions[item.claim_id]) state.decisions[item.claim_id] = blankDecision();
    return [item, state.decisions[item.claim_id]];
  }

  function candidate(item, decision) {
    const id = item.candidate_ids[decision.candidateIndex % item.candidate_ids.length];
    return item.candidates.find(value => value.candidate_id === id);
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
    document.getElementById("item-number").textContent = `Item ${index + 1} of ${packet.items.length} · ${item.claim_id}`;
    document.getElementById("claim").textContent = item.claim_text;
    document.getElementById("note").value = decision.note || "";

    renderButtons("atomicity", [
      ["Yes, one idea", "yes"], ["Needs split", "needs_split"], ["Not sure", "unsure"]
    ], decision.atomicity, value => {
      decision.atomicity = value;
      if (value !== "yes") {
        decision.directSupport = null;
        decision.selectedCandidateId = null;
      }
      saveState(); render();
    });

    const evidence = document.getElementById("evidence-step");
    evidence.className = decision.atomicity === "yes" ? "" : "hidden";
    if (decision.atomicity === "yes") {
      const shown = candidate(item, decision);
      if (!Array.isArray(decision.reviewedCandidateIds)) decision.reviewedCandidateIds = [];
      if (!decision.reviewedCandidateIds.includes(shown.candidate_id)) {
        decision.reviewedCandidateIds.push(shown.candidate_id);
        saveState();
      }
      const reviewedCount = new Set(decision.reviewedCandidateIds).size;
      document.getElementById("passage-meta").textContent = `${shown.source_title}${shown.section ? " · " + shown.section : ""} · viewed ${reviewedCount} of ${item.candidate_ids.length}`;
      const passage = document.getElementById("passage");
      passage.textContent = shown.text;
      passage.className = decision.selectedCandidateId === shown.candidate_id ? "passage selected-passage" : "passage";
      const select = document.getElementById("select-passage");
      select.textContent = decision.selectedCandidateId === shown.candidate_id ? "Rationale selected" : "Use this passage as rationale";
      select.className = decision.selectedCandidateId === shown.candidate_id ? "selected" : "";
      select.onclick = () => {
        decision.selectedCandidateId = decision.selectedCandidateId === shown.candidate_id ? null : shown.candidate_id;
        saveState(); render();
      };
      document.getElementById("next-passage").onclick = () => {
        decision.candidateIndex = (decision.candidateIndex + 1) % item.candidate_ids.length;
        saveState(); render();
      };
      renderButtons("direct-support", [
        ["Yes", "yes"], ["No — none match", "no"], ["Not sure", "unsure"]
      ], decision.directSupport, value => {
        decision.directSupport = value;
        if (value !== "yes") decision.selectedCandidateId = null;
        saveState(); render();
      }, reviewedCount === item.candidate_ids.length ? [] : ["no"]);
    }

    document.getElementById("previous").disabled = index === 0;
    document.getElementById("next").disabled = index === packet.items.length - 1;
    renderProgress();
  }

  function isComplete(item, decision) {
    if (!decision || !decision.atomicity) return false;
    if (decision.atomicity !== "yes") return true;
    if (!decision.directSupport) return false;
    if (decision.directSupport === "yes") return Boolean(decision.selectedCandidateId);
    if (decision.directSupport === "no") {
      return new Set(decision.reviewedCandidateIds || []).size === item.candidate_ids.length;
    }
    return true;
  }

  function renderProgress() {
    const complete = packet.items.filter(item => isComplete(item, state.decisions[item.claim_id])).length;
    document.getElementById("progress").textContent = `${complete}/${packet.items.length} items resolved or escalated`;
  }

  function selectedPassage(item, id) {
    if (!id) return [];
    const value = item.candidates.find(candidate => candidate.candidate_id === id);
    return [{candidate_id: value.candidate_id, source_id: value.source_id, passage_id: value.passage_id, passage_hash: value.passage_hash}];
  }

  function exportReview() {
    const decisions = [];
    for (const item of packet.items) {
      const value = state.decisions[item.claim_id];
      if (!isComplete(item, value)) continue;
      decisions.push({
        claim_id: item.claim_id,
        atomicity: value.atomicity,
        direct_support: value.atomicity === "yes" ? value.directSupport : null,
        reviewed_candidate_ids: item.candidate_ids.filter(id => (value.reviewedCandidateIds || []).includes(id)),
        selected_passages: value.atomicity === "yes" && value.directSupport === "yes" ? selectedPassage(item, value.selectedCandidateId) : [],
        note: value.note.trim() || null
      });
    }
    return {
      schema_version: "progressive-gold-review-v0.1",
      ladder_id: packet.ladder_id,
      rung_id: packet.rung_id,
      packet_sha256: packet.packet_sha256,
      reviewer: document.getElementById("reviewer").value.trim(),
      exported_at_utc: new Date().toISOString(),
      decisions
    };
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
    link.download = `progressive-gold-rung1-${new Date().toISOString().replace(/[:.]/g, "-")}.json`;
    link.click();
    URL.revokeObjectURL(link.href);
  });
  document.getElementById("clear").addEventListener("click", () => {
    if (!confirm("Clear this packet's browser-local progress? Download a checkpoint first if needed.")) return;
    localStorage.removeItem(storageKey); state = {reviewer: "", decisions: {}}; index = 0; document.getElementById("reviewer").value = ""; render();
  });
  render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
