"""Emit the Lane A Antigravity generation packet (paste-ready prompts).

Preparation only: resolves frozen SLG gold + the superseding cloud-generation
preregistration into per-cell, target-blind generator prompts and independent P2
review prompts for Antigravity. Performs NO CAL retrieval, entailment, verdict,
or measured inference. Emitting prompts is template resolution, allowed by the
Lane A packet-preparation ledger.

Self-checks (fail-closed):
  * the frozen domain gold SHA-256 matches the preregistration's recorded hash;
  * no forbidden subject token or frozen proposition substring appears in any
    generator prompt (target-blind guarantee);
  * every domain P2 prompt carries exactly the frozen 25 propositions.

Domain lane emits by default. Appendix A's plain exclusion set was ratified on
2026-07-20; pass ``--plain-ratified`` to emit that separately gated lane.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

# --- Repo-relative anchors -------------------------------------------------
PROJECT = Path(__file__).resolve().parents[2]
FROZEN = PROJECT / "outputs/simple-logic-gold/v0.1-frozen-rev01-2026-07-15"
DOMAIN_GOLD = FROZEN / "domain-renderings-v0.1-rev02-frozen/domain-frozen-gold.json"
PLAIN_GOLD = FROZEN / "frozen-gold.json"
DEFAULT_OUT = FROZEN / "scaled-corpus-v0.1/lane-a-antigravity-pending-v0.1"

PREREG = "plans/2026-07-20-lane-a-antigravity-cloud-generation-superseding-preregistration.md"
DOMAIN_GOLD_SHA256 = "6c82025c9c017bf8e2e78a499cf7f1f6df0fa672d700462f9ffb992bfec4e9a4"

# --- Frozen exclusion sets -------------------------------------------------
# Domain: byte-identical to slg_scaled_t3_candidate.py (Cameron-approved).
DOMAIN_SUBJECTS = (
    "sample",
    "cabinet",
    "autoclave",
    "qualification",
    "logbook",
    "line clearance",
    "deviation",
    "excursion",
    "night shift",
    "analyst chen",
    "assay",
    "batch disposition",
    "disposition form",
    "verification record",
    "cold-chain",
    "shipment",
    "distribution center",
    "temperature range",
)
BANNED_LEMMAS = ("pass", "fail", "seal", "weigh", "store", "return", "ship", "approve", "verify")
DOMAIN_PROPOSITIONS = (
    "The retained sample is in cabinet A.",
    "The retained sample is not in cabinet A; it is in cabinet B.",
    "The retained sample was returned.",
    "The retained sample was returned before noon.",
    "The complete listed autoclave roster contains only A1, A2, and A3.",
    "Autoclave A1 passed the qualification check.",
    "Autoclave A2 passed the qualification check.",
    "Autoclave A2 failed the qualification check.",
    "Autoclave A3 passed the qualification check.",
    "Every listed autoclave passed the qualification check.",
    "The listed logbook entry covers line clearance only; it is not a deviation register.",
    "No temperature excursion was reported during the night shift.",
    "The stability sample was weighed.",
    "The stability sample was sealed.",
    "The stability sample was weighed and sealed.",
    "The stability sample was not sealed.",
    "The signed statement says Analyst Chen reported that the assay passed.",
    "Analyst Chen reported that the assay passed.",
    "The assay passed.",
    "A batch disposition is sufficiently approved only when it has both a signed disposition "
    "form and an independent verification record.",
    "The disposition form has a signature.",
    "The batch disposition has a signed disposition form.",
    "An independent verification record exists.",
    "The cold-chain shipment left the distribution center.",
    "The cold-chain shipment stayed within its temperature range.",
)

# Plain: PROPOSED (Appendix A) — frozen only on Cameron ratification.
PLAIN_SUBJECTS = (
    "brass key",
    "key",
    "drawer",
    "valve",
    "inspection",
    "maintenance record",
    "incident register",
    "leak",
    "shift",
    "parcel",
    "sample",
    "mira",
    "release",
    "signed form",
    "verification record",
    "shipment",
    "warehouse",
    "temperature range",
)
PLAIN_PROPOSITIONS = (
    "The brass key is in drawer A.",
    "The brass key is not in drawer A; it is in drawer B.",
    "The brass key was returned.",
    "The brass key was returned before noon.",
    "The complete listed valve roster contains only V1, V2, and V3.",
    "Valve V1 passed inspection.",
    "Valve V2 passed inspection.",
    "Valve V2 failed inspection.",
    "Valve V3 passed inspection.",
    "Every listed valve passed inspection.",
    "The listed maintenance record covers cleaning only; it is not an incident register.",
    "No leak was reported during the shift.",
    "The parcel was weighed.",
    "The parcel was sealed.",
    "The parcel was weighed and sealed.",
    "The parcel was not sealed.",
    "The signed statement says Mira reported that the sample passed.",
    "Mira reported that the sample passed.",
    "The sample passed.",
    "A release is sufficiently approved only when it has both a signed form and an "
    "independent verification record.",
    "The release form has a signature.",
    "The release has a signed form.",
    "An independent verification record exists.",
    "The shipment left the warehouse.",
    "The shipment stayed within its temperature range.",
)

# --- Tier contracts (50 words/paragraph, +/-~7% band) ----------------------
TIERS = {
    "T2": {
        "target": 300,
        "min_words": 280,
        "max_words": 320,
        "paragraphs": 6,
        "insert_after_para": 3,
    },
    "T3": {
        "target": 1500,
        "min_words": 1400,
        "max_words": 1600,
        "paragraphs": 30,
        "insert_after_para": 15,
    },
    "T4": {
        "target": 6000,
        "min_words": 5600,
        "max_words": 6400,
        "paragraphs": 120,
        "insert_after_para": 60,
    },
}

LANES = {
    "domain": {
        "gold": DOMAIN_GOLD,
        "genre": "pharmaceutical-paperwork",
        "subjects": DOMAIN_SUBJECTS,
        "propositions": DOMAIN_PROPOSITIONS,
        "world_suffix": "-d",
        "ratified": True,
    },
    "plain": {
        "gold": PLAIN_GOLD,
        "genre": "everyday-narrative",
        "subjects": PLAIN_SUBJECTS,
        "propositions": PLAIN_PROPOSITIONS,
        "world_suffix": "",
        "ratified": True,  # Appendix A ratified as-is by Cameron 2026-07-20
    },
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+(?:[’'-][A-Za-z0-9]+)*", text.lower())


def domain_generator_prompt(paragraphs: int, min_w: int, max_w: int) -> str:
    """Target-blind free-prose brief for dry pharmaceutical paperwork."""
    return f"""<role>
You write filler content for a software test fixture.
</role>

<context>
Write one plausible, entirely mundane pharmaceutical-facility paperwork document.
It exists only to pad a retrieval index with realistic but uninformative routine text.
</context>

<constraints>
- Produce exactly ONE title line, then exactly {paragraphs} body paragraphs.
- Body length must be between {min_w} and {max_w} words (title excluded).
- Cover only routine housekeeping: cleaning schedules, training attendance,
  glossary definitions, room-pressure readings, label reconciliation counts,
  and meeting notes. Invent ordinary specifics freely.
- Do NOT state that anything passed, failed, or was sealed, weighed, stored,
  returned, shipped, approved, or verified. Stay entirely off those verbs.
- Do NOT mention any specific equipment identifier, product, material, or named
  person. Keep every subject generic (a room, a page, a schedule, a gauge).
- Plain markdown paragraphs only. No headings after the title, no lists, no
  tables, no commentary, and no mention of these instructions.
</constraints>

<task>
Write the document now. Output only the title and the {paragraphs} paragraphs.
</task>"""


def plain_generator_prompt(paragraphs: int, min_w: int, max_w: int) -> str:
    """Target-blind free-prose brief for everyday slice-of-life fiction."""
    return f"""<role>
You write filler content for a software test fixture.
</role>

<context>
Write one short piece of everyday, slice-of-life fiction about ordinary people
(for example a community-garden dispute, a retiring piano tuner, or a
neighbourhood bakery at dawn). It exists only to pad a retrieval index with
realistic but uninformative narrative text.
</context>

<constraints>
- Produce exactly ONE title line, then exactly {paragraphs} body paragraphs.
- Body length must be between {min_w} and {max_w} words (title excluded).
- Keep the story in ordinary domestic, social, or outdoor life. Do not write
  about laboratories, storage, deliveries, logistics, or equipment checks, and
  do not describe objects being handled, moved, or examined for a record.
- Nothing in the story may be passed, failed, sealed, weighed, stored, returned,
  shipped, approved, or verified. Keep the plot off those actions.
- Invent characters and events freely, but do not name any real product,
  company, or identifier.
- Plain markdown paragraphs only. No headings after the title, no lists, no
  tables, no commentary, and no mention of these instructions.
</constraints>

<task>
Write the story now. Output only the title and the {paragraphs} paragraphs.
</task>"""


def p2_prompt(candidate_id: str, propositions: tuple[str, ...]) -> str:
    """Independent contamination-review prompt over the frozen proposition set."""
    lines = "\n".join(f"P{i:02d}: {p}" for i, p in enumerate(propositions, 1))
    example = '{"id":"P01","relation":"unrelated","reason":"brief reason"}'
    return f"""<role>
You are an independent contamination reviewer for a synthetic retrieval fixture.
</role>

<context>
Decide whether the candidate filler text states, denies, entails, contradicts,
paraphrases, implies, presupposes, or otherwise changes the likelihood of each
frozen proposition. Shared generic words alone do not establish contamination.
Be conservative: if a reasonable reader could learn anything about a proposition
from the filler, mark the specific non-unrelated relation.
</context>

<candidate_filler>
{{PASTE THE EXACT GENERATED TITLE + BODY HERE}}
</candidate_filler>

<frozen_propositions>
{lines}
</frozen_propositions>

<output_format>
Return valid JSON only with this shape:
{{"candidate_id":"{candidate_id}","reviews":[{example}],"overall":"clean_or_contaminated"}}

Include exactly one review for each ID P01 through P{len(propositions):02d} in order.
`relation` must be one of `unrelated`, `entails`, `contradicts`, `paraphrases`,
`implies`, `presupposes`, or `ambiguous`. Set `overall` to `clean` only if all
{len(propositions)} relations are `unrelated`; otherwise set it to `contaminated`.
</output_format>"""


def generation_contract(cell_id: str, world_id: str, tier: str, lane: str, contract: dict) -> str:
    return f"""# Generation contract — {cell_id}

**Preparation artifact.** This is a paste-ready packet for Antigravity, not an
admitted candidate. Governed by `{PREREG}`.

- Lane / genre: {lane} / {LANES[lane]["genre"]}
- World / tier: {world_id} / {tier}
- Body word band: {contract["min_words"]}–{contract["max_words"]} words,
  {contract["paragraphs"]} paragraphs
- Fact insertion (later preparation only): after body paragraph {contract["insert_after_para"]}
- Mode: target-blind free prose (generator is shown no proposition/subject/fact)

## Operator steps on Antigravity
1. Open a **fresh** Antigravity conversation. Disable/ignore tool use.
2. Paste `prompt.txt` verbatim. Save the model's **prose answer only** to
   `raw_response.txt`. If the answer is empty or lives in a thinking/reasoning
   trace, discard it — that is a non-candidate, regenerate.
3. Record the exact model string Antigravity shows + capture time in
   `generation-record.json`.
4. Open a **second, independent** conversation (no shared memory) — or a
   different model. Paste `p2-prompt.txt` with the generated text substituted
   into `{{PASTE ...}}`. Save JSON to `p2-response.json` and the model string to
   `p2-record.json` with `independent_context: true`.
5. Run the deterministic screen + P2 validator locally, then bring the result to
   Cameron for admission. Do not edit the prose to pass; regenerate rejects.
"""


def emit_cell(out_root: Path, lane: str, world_id: str, tier: str) -> dict[str, Any]:
    cfg = LANES[lane]
    contract = TIERS[tier]
    cell_id = f"{world_id.lower()}-{tier.lower()}-{cfg['genre']}"
    cell_dir = out_root / lane / world_id / tier
    cell_dir.mkdir(parents=True, exist_ok=True)

    if lane == "domain":
        gen = domain_generator_prompt(
            contract["paragraphs"], contract["min_words"], contract["max_words"]
        )
    else:
        gen = plain_generator_prompt(
            contract["paragraphs"], contract["min_words"], contract["max_words"]
        )
    p2 = p2_prompt(cell_id, cfg["propositions"])

    # Target-blind self-check: no subject token or proposition text may appear.
    gen_norm = " ".join(words(gen))
    for subj in cfg["subjects"]:
        if re.search(rf"\b{re.escape(subj)}\b", gen_norm):
            raise AssertionError(
                f"target-blind violation: subject '{subj}' leaked into {cell_id} prompt"
            )
    for prop in cfg["propositions"]:
        if " ".join(words(prop)) in gen_norm:
            raise AssertionError(
                f"target-blind violation: proposition leaked into {cell_id} prompt"
            )

    (cell_dir / "prompt.txt").write_text(gen + "\n", encoding="utf-8")
    (cell_dir / "p2-prompt.txt").write_text(p2 + "\n", encoding="utf-8")
    (cell_dir / "GENERATION-CONTRACT.md").write_text(
        generation_contract(cell_id, world_id, tier, lane, contract), encoding="utf-8"
    )
    case = {
        "schema_version": "cal-scaled-corpus-antigravity-cell-v1",
        "cell_id": cell_id,
        "lane": lane,
        "genre": cfg["genre"],
        "world_id": world_id,
        "tier": tier,
        "target_words": contract["target"],
        "body_word_min": contract["min_words"],
        "body_word_max": contract["max_words"],
        "paragraphs": contract["paragraphs"],
        "insert_after_paragraph": contract["insert_after_para"],
        "generation_visibility": (
            "target-blind free prose; exclusions applied only by post-generation screen"
        ),
        "generator_surface": "antigravity",
        "p2_proposition_count": len(cfg["propositions"]),
        "exclusion_set_frozen": cfg["ratified"],
        "preregistration": PREREG,
        "status": "pending_generation",
        "prompt_sha256": sha256_text(gen + "\n"),
        "p2_prompt_sha256": sha256_text(p2 + "\n"),
    }
    (cell_dir / "case.json").write_text(
        json.dumps(case, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return case


def write_manifest(root: Path) -> None:
    manifest = root / "SHA256SUMS"
    entries = sorted(
        (sha256_bytes(p.read_bytes()), p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file() and p.name != "SHA256SUMS"
    )
    manifest.write_text("".join(f"{h}  {rel}\n" for h, rel in entries), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--plain-ratified",
        action="store_true",
        help="Emit the 36 plain cells (only after Appendix A is ratified).",
    )
    args = parser.parse_args()

    # Integrity gate: frozen domain gold must match the preregistration hash.
    observed = sha256_bytes(LANES["domain"]["gold"].read_bytes())
    if observed != DOMAIN_GOLD_SHA256:
        raise SystemExit(f"domain gold hash mismatch: {observed} != {DOMAIN_GOLD_SHA256}")

    if args.out.exists():
        raise SystemExit(f"refusing to overwrite existing packet dir: {args.out}")

    lanes = ["domain"] + (["plain"] if args.plain_ratified else [])
    index: list[dict[str, Any]] = []
    for lane in lanes:
        gold = json.loads(LANES[lane]["gold"].read_text(encoding="utf-8"))
        for case in gold["frozen_cases"]:
            world_id = case["base_case_id"]  # e.g. SLG-01-d or SLG-01
            for tier in ("T2", "T3", "T4"):
                index.append(emit_cell(args.out, lane, world_id, tier))

    summary = {
        "schema_version": "cal-scaled-corpus-antigravity-packet-index-v1",
        "preregistration": PREREG,
        "status": "prepared-pending-admission",
        "lanes_emitted": lanes,
        "plain_gated_reason": None
        if args.plain_ratified
        else "Appendix A plain exclusion set not ratified",
        "cell_count": len(index),
        "cells": index,
    }
    (args.out / "packet-index.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_manifest(args.out)
    try:
        out_label = str(args.out.relative_to(PROJECT))
    except ValueError:
        out_label = str(args.out)
    print(
        json.dumps(
            {
                "cells": len(index),
                "lanes": lanes,
                "out": out_label,
                "cal_inference_performed": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
