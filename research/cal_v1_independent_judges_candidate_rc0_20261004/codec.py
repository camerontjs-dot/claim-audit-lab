"""Shared canonical JSON helpers for candidate lanes. Not used by adapter.py."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def parse_envelope(raw: bytes) -> dict[str, Any]:
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("envelope must be an object")
    claim = value.get("claim")
    evidence = value.get("evidence")
    if not isinstance(claim, str) or not isinstance(evidence, list):
        raise ValueError("envelope requires claim text and an evidence list")
    passages: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("evidence item must be an object")
        passage_id = item.get("id")
        text = item.get("text")
        if not isinstance(passage_id, str) or not isinstance(text, str) or not passage_id:
            raise ValueError("evidence item requires id and text")
        if passage_id in seen:
            raise ValueError("duplicate evidence id")
        seen.add(passage_id)
        passages.append({"id": passage_id, "text": text})
    return {"claim": claim, "evidence": passages}
