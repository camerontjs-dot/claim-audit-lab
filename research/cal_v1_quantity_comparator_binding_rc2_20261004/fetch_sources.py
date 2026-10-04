"""Download the preselected RC2 sources once. Prints metadata, never page bodies."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SELECTION = ROOT / "SOURCE_POOL_SELECTION.json"
RAW = ROOT / "sources" / "raw"
ORIGINAL = ROOT / "sources" / "original-local"
USER_AGENT = "cal-rc2-source-custody/1.0"

_SECRET_PATTERNS = (
    ("mapbox_public_token", re.compile(r"pk\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_token", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("bearer_jwt", re.compile(r"Bearer\s+eyJ[A-Za-z0-9_\-]{20,}")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)
_MACHINE_PATH = re.compile(r"/Users/[A-Za-z0-9._-]+/")
_HOME_PATH = re.compile(r"/home/[A-Za-z0-9._-]+/")


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _curl_version() -> str:
    completed = subprocess.run(["curl", "--version"], check=True, capture_output=True, text=True)
    return completed.stdout.splitlines()[0]


def _scan(text: str) -> dict[str, object]:
    secrets = []
    for name, pattern in _SECRET_PATTERNS:
        found = list(pattern.finditer(text))
        if found:
            secrets.append(
                {
                    "class": name,
                    "count": len(found),
                    "match_sha256": [
                        hashlib.sha256(item.group(0).encode("utf-8")).hexdigest() for item in found
                    ],
                }
            )
    machine_paths = len(_MACHINE_PATH.findall(text))
    home_paths = sorted(set(_HOME_PATH.findall(text)))
    return {
        "secret_classes": secrets,
        "machine_user_paths": machine_paths,
        "public_home_path_count": len(home_paths),
        "public_home_paths_redacted_from_receipt": bool(home_paths),
    }


def _redact(text: str) -> tuple[str, list[dict[str, object]]]:
    deviations = []
    current = text
    for name, pattern in _SECRET_PATTERNS:
        matches = list(pattern.finditer(current))
        if not matches:
            continue
        current = pattern.sub(f"REDACTED_{name.upper()}", current)
        deviations.append({"class": name, "count": len(matches), "action": "replaced_before_publication"})
    machine_matches = list(_MACHINE_PATH.finditer(current))
    if machine_matches:
        current = _MACHINE_PATH.sub("/REDACTED_MACHINE_PATH/", current)
        deviations.append(
            {"class": "machine_user_path", "count": len(machine_matches), "action": "replaced_before_publication"}
        )
    return current, deviations


def _download(url: str, destination: Path) -> dict[str, object]:
    header_path = destination.with_suffix(".headers")
    started = _utc()
    completed = subprocess.run(
        [
            "curl",
            "--location",
            "--silent",
            "--show-error",
            "--max-time",
            "180",
            "--user-agent",
            USER_AGENT,
            "--dump-header",
            str(header_path),
            "--output",
            str(destination),
            "--write-out",
            "%{http_code}\t%{url_effective}\t%{content_type}",
            url,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    status_text, final_url, media_type = (completed.stdout.strip() + "\t\t").split("\t")[:3]
    raw = destination.read_bytes() if destination.exists() else b""
    return {
        "retrieved_at_utc": started,
        "http_status": int(status_text) if status_text.isdigit() else None,
        "final_url": final_url,
        "media_type": media_type,
        "transport_exit_code": completed.returncode,
        "transport_stderr_present": bool(completed.stderr.strip()),
        "raw_bytes": len(raw),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "header_path_recorded": header_path.name,
    }


def _sources() -> list[tuple[str, dict[str, object]]]:
    document = json.loads(SELECTION.read_text(encoding="utf-8"))
    rows = []
    for partition in ("calibration", "held_out"):
        for item in document[partition]:
            rows.append((partition, item))
    return rows


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    ORIGINAL.mkdir(parents=True, exist_ok=True)
    transport = {
        "tool": "curl",
        "version": _curl_version(),
        "command": [
            "curl",
            "--location",
            "--silent",
            "--show-error",
            "--max-time",
            "180",
            "--user-agent",
            USER_AGENT,
            "--dump-header",
            "<headers>",
            "--output",
            "<raw>",
            "--write-out",
            "%{http_code}\\t%{url_effective}\\t%{content_type}",
            "<requested_url>",
        ],
    }
    records = []
    for partition, item in _sources():
        source_id = str(item["source_id"])
        requested = str(item["url"])
        original_path = ORIGINAL / f"{source_id}.bin"
        published_path = RAW / f"{source_id}.bin"
        download = _download(requested, original_path)
        original_bytes = original_path.read_bytes() if original_path.exists() else b""
        try:
            text = original_bytes.decode("utf-8")
            decoded = True
        except UnicodeDecodeError:
            text = original_bytes.decode("utf-8", errors="replace")
            decoded = False
        scan = _scan(text)
        redacted_text, deviations = _redact(text)
        published = redacted_text.encode("utf-8") if decoded else original_bytes
        if not decoded and deviations:
            published = original_bytes
            deviations.append({"class": "undecoded_bytes", "action": "left_unredacted_fail_closed"})
        published_path.write_bytes(published)
        record = {
            "source_id": source_id,
            "partition": partition,
            "publisher": item["publisher"],
            "title": item["title"],
            "requested_url": requested,
            "final_url": download["final_url"],
            "retrieved_at_utc": download["retrieved_at_utc"],
            "http_status": download["http_status"],
            "media_type": download["media_type"],
            "transport_tool": transport["tool"],
            "transport_version": transport["version"],
            "transport_exit_code": download["transport_exit_code"],
            "transport_stderr_present": download["transport_stderr_present"],
            "decoded_utf8": decoded,
            "original_raw_bytes": download["raw_bytes"],
            "original_raw_sha256": download["raw_sha256"],
            "published_raw_bytes": len(published),
            "published_raw_sha256": hashlib.sha256(published).hexdigest(),
            "raw_bytes": len(published),
            "raw_sha256": hashlib.sha256(published).hexdigest(),
            "leak_scan": scan,
            "redaction_deviations": deviations,
            "status": "frozen" if download["http_status"] == 200 and published else "retrieval_failed",
        }
        records.append(record)
        print(
            json.dumps(
                {
                    "source_id": source_id,
                    "partition": partition,
                    "status": record["status"],
                    "http_status": record["http_status"],
                    "raw_bytes": record["raw_bytes"],
                    "raw_sha256": record["raw_sha256"],
                    "redactions": len(deviations),
                    "secret_classes": [item["class"] for item in scan["secret_classes"]],
                    "machine_user_paths": scan["machine_user_paths"],
                },
                sort_keys=True,
            )
        )
    freeze = {
        "schema": "cal-v1-quantity-comparator-rc2-source-freeze-v1",
        "preparation_head": "990267bf3bf523c0b29ea427dd9610b620c1e3c7",
        "preparation_tree": "2cbbb408caeafef6bdf6518b3d26130d508f73f4",
        "selection_sha256": hashlib.sha256(SELECTION.read_bytes()).hexdigest(),
        "transport": transport,
        "sources": records,
        "failed_source_ids": [item["source_id"] for item in records if item["status"] != "frozen"],
        "replacement_policy": "No source was replaced. A failed retrieval remains a failed retrieval.",
    }
    (ROOT / "SOURCE_FREEZE.json").write_text(
        json.dumps(freeze, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (RAW / ".gitattributes").write_text("* -diff -text\n*.bin binary\n*.headers binary\n", encoding="utf-8")
    (ORIGINAL / ".gitignore").write_text("*\n!.gitignore\n", encoding="utf-8")


if __name__ == "__main__":
    main()
