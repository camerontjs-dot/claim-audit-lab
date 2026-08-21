"""Build a T4 cell (~6,000 words / 120 paras) by chunked assembly.

Single-call generation caps out near T3 scale (~1,500 words); longer generations
under-deliver word count and accumulate banned verbs. So a T4 is assembled from
N screened T3-sized chunks (default 4 x 30 paras / 1,400-1,600 words), which sum
to the T4 contract (120 paras / 5,600-6,400 words). Each chunk must pass the
chunk-level screen before it is accepted; the assembly of clean chunks is clean
by construction. No CAL inference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from slg_scaled_antigravity_packet import domain_generator_prompt, plain_generator_prompt  # noqa: E402
from slg_scaled_gen_cell import avoidance_block  # noqa: E402
from slg_scaled_screen import LANE_SETS, screen  # noqa: E402

NO_TOOLS = ("\n\nIMPORTANT: You have no tools and no file access in this session. Do not run "
            "commands, call tools, or read/write files. Reply with only the requested document text.")
CHUNK_PARAS, CHUNK_MIN, CHUNK_MAX = 30, 1400, 1600


def blocks(text: str) -> list[str]:
    return [b.strip() for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]


def gen_chunk(lane: str, model: str, timeout: int, attempts: int) -> tuple[str | None, str]:
    subjects, props = LANE_SETS[lane]
    genfn = domain_generator_prompt if lane == "domain" else plain_generator_prompt
    prompt = genfn(CHUNK_PARAS, CHUNK_MIN, CHUNK_MAX) + avoidance_block(lane) + NO_TOOLS
    for _ in range(attempts):
        try:
            p = subprocess.run(["agy", "-p", prompt, "--model", model], capture_output=True,
                               text=True, stdin=subprocess.DEVNULL, timeout=timeout)
        except subprocess.TimeoutExpired:
            continue
        out, err = p.stdout.strip(), p.stderr.strip()
        if "quota" in err.lower():
            return None, "quota"
        if not out:
            continue
        if screen(out, subjects, props, CHUNK_PARAS, CHUNK_MIN, CHUNK_MAX)["decision"] == "continue_to_p2":
            return out, "ok"
    return None, "exhausted"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cell", type=Path, required=True)
    ap.add_argument("--chunks", type=int, default=4)
    ap.add_argument("--model", default="Gemini 3.5 Flash (High)")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--attempts", type=int, default=4)
    args = ap.parse_args()
    case = json.loads((args.cell / "case.json").read_text())
    lane = case["lane"]

    chunk_dir = args.cell / "chunks"
    chunk_dir.mkdir(exist_ok=True)
    texts: list[str] = []
    for i in range(1, args.chunks + 1):
        text, status = gen_chunk(lane, args.model, args.timeout, args.attempts)
        if status == "quota":
            print(json.dumps({"cell": case["cell_id"], "status": "quota_blocked", "chunk": i})); sys.exit(3)
        if text is None:
            print(json.dumps({"cell": case["cell_id"], "status": "chunk_failed", "chunk": i})); sys.exit(2)
        (chunk_dir / f"chunk-{i:02d}.txt").write_text(text + "\n")
        texts.append(text)

    b0 = blocks(texts[0])
    title, paras = b0[0], b0[1:]
    for t in texts[1:]:
        paras += blocks(t)[1:]  # drop each later chunk's title line
    assembled = title + "\n\n" + "\n\n".join(paras) + "\n"
    (args.cell / "raw_response.txt").write_text(assembled)

    rec = {
        "schema_version": "cal-scaled-corpus-antigravity-generation-record-v1",
        "cell_id": case["cell_id"], "lane": lane, "world_id": case["world_id"], "tier": case["tier"],
        "generator_surface": "antigravity", "generator_cli": "agy 1.1.4", "generator_model": args.model,
        "generation_mode": "exclusion-aware-lexical, chunked-assembly",
        "chunks": args.chunks, "chunk_paragraphs": CHUNK_PARAS, "chunk_word_band": [CHUNK_MIN, CHUNK_MAX],
        "chunk_sha256": ["sha256:" + hashlib.sha256((t + "\n").encode()).hexdigest() for t in texts],
        "preregistration": case.get("preregistration"), "preregistration_admitted": False,
        "operator": "claude-code-on-behalf-of-cameron",
        "raw_response_sha256": "sha256:" + hashlib.sha256(assembled.encode()).hexdigest(),
        "note": "DEV pre-admission candidate; T4 assembled from screened T3-sized chunks; not admitted, not CAL evidence.",
    }
    (args.cell / "generation-record.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    words = sum(len(re.findall(r"[A-Za-z0-9]+", p)) for p in paras)
    print(json.dumps({"cell": case["cell_id"], "status": "assembled", "paras": len(paras), "words": words}))


if __name__ == "__main__":
    main()
