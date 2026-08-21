"""Run the independent P2 contamination judge for one cell via local Ollama.

Judge model defaults to qwen3:14b (Qwen family — independent of the Gemini
generator, matching the sealed T2 precedent). Substitutes the cell's generated
filler into its p2-prompt.txt, calls the local Ollama API, and preserves
ollama-p2-response.json + p2-response.json + p2-record.json. No CAL inference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

SCREEN = Path(__file__).resolve().parent / "slg_scaled_screen.py"


def run_cell(cell: Path, model: str, num_ctx: int) -> dict:
    tmpl = (cell / "p2-prompt.txt").read_text()
    body = (cell / "raw_response.txt").read_text().strip()
    prompt = tmpl.replace("{PASTE THE EXACT GENERATED TITLE + BODY HERE}", body)
    prompt += "\n\nOutput ONLY the JSON object described above. No analysis, preamble, or thinking."
    opts = {"temperature": 0.0, "top_k": 20, "top_p": 0.95, "repeat_penalty": 1.0,
            "num_ctx": num_ctx, "num_predict": 1500, "seed": 20260723}
    payload = {"model": model, "prompt": prompt, "stream": False, "think": False,
               "options": opts, "keep_alive": "10m"}
    req = urllib.request.Request("http://localhost:11434/api/generate",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=1800) as r:
        resp = json.loads(r.read().decode())
    dt = round(time.time() - t0, 1)
    (cell / "ollama-p2-response.json").write_text(json.dumps(resp, indent=2) + "\n")
    answer = resp.get("response", "")
    (cell / "p2-response.json").write_text(answer)
    rec = {"schema_version": "cal-scaled-corpus-p2-record-v1", "p2_judge_surface": "local-ollama",
           "p2_judge_model": model, "p2_judge_options": opts, "think": False,
           "independent_context": True,
           "independent_of_generator": "generator=Gemini via Antigravity; judge=%s local" % model,
           "wall_seconds": dt, "eval_count": resp.get("eval_count"),
           "p2_response_sha256": "sha256:" + hashlib.sha256(answer.encode()).hexdigest()}
    (cell / "p2-record.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    # Re-run the deterministic+P2 validator so the receipt reflects the P2 result.
    v = subprocess.run([sys.executable, str(SCREEN), "--cell", str(cell)],
                       capture_output=True, text=True)
    final = json.loads(v.stdout).get("final_status") if v.stdout.strip() else "validator_error"
    return {"bytes": len(answer), "wall_seconds": dt, "final_status": final}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cells", nargs="+", type=Path, required=True)
    ap.add_argument("--model", default="qwen3:14b")
    ap.add_argument("--num-ctx", type=int, default=8192)
    args = ap.parse_args()
    for cell in args.cells:
        try:
            info = run_cell(cell, args.model, args.num_ctx)
            print(json.dumps({"cell": cell.parent.name + "/" + cell.name, "status": "p2_done", **info}), flush=True)
        except Exception as e:
            print(json.dumps({"cell": str(cell), "status": "p2_error", "error": repr(e)[:200]}), flush=True)


if __name__ == "__main__":
    main()
