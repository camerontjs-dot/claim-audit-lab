"""No tracked file may carry a path from the machine it was authored on.

This has been a recurring defect rather than a one-off. Absolute paths reached the
tracked tree three separate times, and the existing guard in ``test_report.py`` did
not catch any of them because it only scans ``examples/``. The leak that survived
longest was in ``scripts/`` and did not even contain ``/Users/`` — it carried the
same information in a temp-directory name of the form ``-Users-<user>-Desktop-``,
which a naive search misses.

So this scans **every tracked file**, and matches the shapes rather than one literal.

Nothing here is exempt, including this file. The patterns end in a character class or
escape rather than a bare username, so the regex source is not an instance of the regex,
and the sample leaks below are assembled from fragments at run time. A guard that needs
an exemption for itself invites the next exemption.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Each pattern describes a path shape that identifies an authoring machine.
AUTHORING_PATH_PATTERNS = (
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
    # Session scratch directories encode the same thing with dashes for slashes.
    re.compile(r"-Users-[A-Za-z0-9._]+-"),
    # Per-uid temp roots, e.g. a CLI session directory suffixed with the user id.
    re.compile(r"claude-\d{3,}"),
    re.compile(r"admins?-MacBook"),
)

# Binary and vendored files are skipped by extension rather than by content sniffing,
# so the skip list is visible and reviewable instead of implicit.
SKIP_SUFFIXES = frozenset(
    {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".woff", ".woff2", ".whl", ".lock"}
)


def _tracked_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):  # pragma: no cover - no git / no checkout
        pytest.skip("not a git checkout; nothing to enumerate")
    names = [n for n in result.stdout.decode("utf-8").split("\0") if n]
    return [REPO_ROOT / n for n in names]


def test_repository_is_enumerable() -> None:
    """The scan below is only meaningful if it has files to scan."""
    assert len(_tracked_files()) > 50


def test_no_tracked_file_contains_an_authoring_path() -> None:
    """Every tracked file is free of paths identifying the machine it was written on."""
    offenders: list[str] = []
    for path in _tracked_files():
        if path.suffix.lower() in SKIP_SUFFIXES or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern in AUTHORING_PATH_PATTERNS:
                match = pattern.search(line)
                if match:
                    rel = path.relative_to(REPO_ROOT)
                    offenders.append(f"{rel}:{lineno}: {match.group(0)!r}")
    assert not offenders, "authoring-machine paths in tracked files:\n" + "\n".join(offenders)


def test_guard_detects_each_shape_it_claims_to() -> None:
    """The patterns actually match the forms that reached the tree in the past.

    The samples are assembled from fragments at run time. Writing them as literals
    would put matchable strings in a tracked file and make this module fail its own
    scan — which it did, on the first version of this test.
    """
    sep, dash, user, uid = "/", "-", "someone", "000"
    known_leaks = (
        f"{sep}Users{sep}{user}{sep}Desktop{sep}project{sep}.venv{sep}bin",
        f"{sep}home{sep}{user}{sep}project",
        f"{sep}private{sep}tmp{sep}claude{dash}{uid}{sep}"
        f"{dash}Users{dash}{user}{dash}Desktop{dash}Project{sep}scratchpad",
        f"admins{dash}MacBook{dash}Air.local",
    )
    for leak in known_leaks:
        assert any(p.search(leak) for p in AUTHORING_PATH_PATTERNS), leak


def test_guard_scans_itself() -> None:
    """This module is tracked, so the scan above must cover it and it must pass.

    Guarding this explicitly because the failure mode is quiet: while the file was
    still untracked it was not enumerated, so the scan passed for the wrong reason.
    """
    tracked = {p.resolve() for p in _tracked_files()}
    assert Path(__file__).resolve() in tracked, "guard is not tracked; the scan skips it"


def test_guard_does_not_flag_ordinary_paths() -> None:
    """Relative and derived paths must not trip the guard."""
    benign = (
        'ROOT = Path(__file__).resolve().parents[2] / "outputs"',
        "src/claim_audit_lab/v1/configs/cal-rules-v1.13.0.yaml",
        "python -m pip install -e '.[dev,v1]'",
        "https://github.com/camerontjs-dot/claim-audit-lab",
        "tempfile.gettempdir()",
    )
    for line in benign:
        assert not any(p.search(line) for p in AUTHORING_PATH_PATTERNS), line
