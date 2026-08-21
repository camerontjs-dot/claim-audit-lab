"""Batch-generate + screen many Lane A cells (background-friendly).

Runs slg_scaled_gen_cell.py then slg_scaled_screen.py for each cell path.
Stops early if Antigravity returns a quota block. Prints one JSON line per cell.
No CAL inference.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GEN = HERE / "slg_scaled_gen_cell.py"
SCREEN = HERE / "slg_scaled_screen.py"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cells", nargs="+", type=Path, required=True)
    ap.add_argument("--model", default="Gemini 3.5 Flash (High)")
    ap.add_argument("--attempts", type=int, default=3, help="regenerate on screen reject")
    ap.add_argument("--gen-timeout", type=int, default=300, help="per-generation timeout (s)")
    args = ap.parse_args()
    for cell in args.cells:
        label = cell.parent.name + "/" + cell.name
        screen, gstatus = "screen_error", "gen_error"
        for attempt in range(1, args.attempts + 1):
            g = subprocess.run([sys.executable, str(GEN), "--cell", str(cell), "--model", args.model,
                                "--timeout", str(args.gen_timeout)],
                               capture_output=True, text=True)
            gstatus = json.loads(g.stdout).get("status") if g.stdout.strip() else "gen_error"
            if gstatus == "quota_blocked":
                print(json.dumps({"cell": label, "status": "quota_blocked_STOP"}), flush=True)
                return
            if gstatus != "generated":
                continue  # empty/timeout — regenerate
            v = subprocess.run([sys.executable, str(SCREEN), "--cell", str(cell)], capture_output=True, text=True)
            screen = json.loads(v.stdout).get("screen") if v.stdout.strip() else "screen_error"
            if screen == "continue_to_p2":
                break  # clean — done
        print(json.dumps({"cell": label, "status": gstatus, "screen": screen, "attempts": attempt}), flush=True)


if __name__ == "__main__":
    main()
