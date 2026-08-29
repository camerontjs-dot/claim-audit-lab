"""Verify a fresh #36 rerun against the frozen normalized scientific object."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

# Frozen from #36 fully green repeat run 33275342888, artifact 9721337978.
# The predecessor demonstrated that only execution_head_sha changes between
# otherwise identical RESULTS.json objects.  The hash below is canonical JSON
# after removing exactly that one metadata field.
FROZEN_NORMALIZED_RESULTS_SHA256 = (
    "sha256:db6ac4dac26045c0b489cf28a704376b659522979759e33f704706c61472c51d"
)
FROZEN_REPEAT_RESULTS_SHA256 = (
    "sha256:a2bab28e138fbadc8343d4efce29d8e42823bf8ee97f1a41fa094b9f45da9bdf"
)
FROZEN_REPEAT_EXECUTION_HEAD = "e864f3e12942bf3f47306ba895b8b965b638dae0"


def normalized_sha256(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "execution_head_sha" not in payload:
        raise RuntimeError("RESULTS.json lacks the execution-head metadata field")
    del payload["execution_head_sha"]
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    args = parser.parse_args()
    observed = normalized_sha256(args.results)
    receipt = {
        "frozen_repeat_run": 33275342888,
        "frozen_repeat_execution_head": FROZEN_REPEAT_EXECUTION_HEAD,
        "frozen_repeat_results_sha256": FROZEN_REPEAT_RESULTS_SHA256,
        "normalization": "remove exactly execution_head_sha; canonical JSON sort_keys compact",
        "expected_normalized_results_sha256": FROZEN_NORMALIZED_RESULTS_SHA256,
        "observed_normalized_results_sha256": observed,
        "exact_scientific_object_reproduced": observed == FROZEN_NORMALIZED_RESULTS_SHA256,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if observed != FROZEN_NORMALIZED_RESULTS_SHA256:
        raise RuntimeError("fresh predecessor scientific object differs from frozen #36 repeat")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
