from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

TYPED_HEAD = "22bc5c1d97b78cfe6f9e2f57e52f69d528069b9a"
STATE_HEAD = "f117698e6db3b47cc68af2024c7816cc8945b004"


def _exact_repo(env_name: str, expected_head: str) -> Path:
    raw = os.environ.get(env_name)
    if not raw:
        pytest.skip(f"{env_name} is required")
    repo = Path(raw).resolve()
    actual = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    assert actual == expected_head
    return repo


def _run(repo: Path, code: str) -> object:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo)
    raw = subprocess.check_output(
        [sys.executable, "-c", code],
        cwd=repo,
        env=env,
        text=True,
    )
    return json.loads(raw)


def test_explicit_definition_and_equivalence_use_exact_typed_binary_candidate() -> None:
    repo = _exact_repo("CAL_TYPED_BINARY_REPO", TYPED_HEAD)
    code = r"""
import json
from research.typed_spatial_relation_discriminator_rc0.apparatus import (
    Atom,
    SPECS,
    Spec,
)
from research.typed_spatial_relation_discriminator_rc0.candidate import relate

SPECS.update(
    {
        "EQUIVALENT_TO": Spec("EQUIVALENT_TO", symmetric=True),
        "DEFINED_AS": Spec("DEFINED_AS", inverse="DEFINITION_OF"),
        "DEFINITION_OF": Spec("DEFINITION_OF", inverse="DEFINED_AS"),
    }
)

cases = [
    ("EQ01", Atom("A", "EQUIVALENT_TO", "B"), Atom("A", "EQUIVALENT_TO", "B")),
    ("EQ02", Atom("A", "EQUIVALENT_TO", "B"), Atom("B", "EQUIVALENT_TO", "A")),
    (
        "EQ03",
        Atom("A", "EQUIVALENT_TO", "B", True),
        Atom("A", "EQUIVALENT_TO", "B", False),
    ),
    ("EQ04", Atom("A", "EQUIVALENT_TO", "B"), Atom("A", "EQUIVALENT_TO", "C")),
    ("DEF01", Atom("Term", "DEFINED_AS", "Meaning"), Atom("Term", "DEFINED_AS", "Meaning")),
    (
        "DEF02",
        Atom("Term", "DEFINED_AS", "Meaning"),
        Atom("Meaning", "DEFINITION_OF", "Term"),
    ),
    (
        "DEF03",
        Atom("Term", "DEFINED_AS", "Meaning"),
        Atom("Meaning", "DEFINED_AS", "Term"),
    ),
    (
        "DEF04",
        Atom("Term", "DEFINED_AS", "Meaning", True),
        Atom("Term", "DEFINED_AS", "Meaning", False),
    ),
    ("DEF05", Atom("Term", "MEANS", "Meaning"), Atom("Term", "MEANS", "Meaning")),
]
print(json.dumps([(case_id, relate(source, query).value) for case_id, source, query in cases]))
"""
    observed = _run(repo, code)
    assert observed == [
        ["EQ01", "SUPPORTS"],
        ["EQ02", "SUPPORTS"],
        ["EQ03", "REFUTES"],
        ["EQ04", "UNRESOLVED"],
        ["DEF01", "SUPPORTS"],
        ["DEF02", "SUPPORTS"],
        ["DEF03", "UNRESOLVED"],
        ["DEF04", "REFUTES"],
        ["DEF05", "UNRESOLVED"],
    ]


def test_explicit_existence_uses_exact_attribute_state_candidate() -> None:
    repo = _exact_repo("CAL_ATTRIBUTE_STATE_REPO", STATE_HEAD)
    code = r"""
import json
from research.attribute_state_contract_rc0.apparatus import State
from research.attribute_state_contract_rc0.candidate import relate

present = lambda entity, *, functional=True, domain="entity_existence_v1": State(
    entity,
    "existence",
    domain,
    "present",
    functional,
)
absent = lambda entity, *, functional=True, domain="entity_existence_v1": State(
    entity,
    "existence",
    domain,
    "absent",
    functional,
)

cases = [
    ("EX01", present("Entity-A"), present("Entity-A")),
    ("EX02", absent("Entity-A"), present("Entity-A")),
    ("EX03", present("Entity-A"), absent("Entity-A")),
    ("EX04", present("Entity-A"), present("Entity-B")),
    (
        "EX05",
        present("Entity-A", domain="entity_existence_v1"),
        present("Entity-A", domain="document_reference_v1"),
    ),
    (
        "EX06",
        State("Entity-A", "mentioned", "document_reference_v1", "present", True),
        present("Entity-A"),
    ),
    (
        "EX07",
        absent("Entity-A", functional=False),
        present("Entity-A", functional=False),
    ),
]
print(json.dumps([(case_id, relate(source, query).value) for case_id, source, query in cases]))
"""
    observed = _run(repo, code)
    assert observed == [
        ["EX01", "SUPPORTS"],
        ["EX02", "REFUTES"],
        ["EX03", "REFUTES"],
        ["EX04", "UNRESOLVED"],
        ["EX05", "UNRESOLVED"],
        ["EX06", "UNRESOLVED"],
        ["EX07", "UNRESOLVED"],
    ]


def test_closed_registration_not_algorithm_change() -> None:
    typed = _exact_repo("CAL_TYPED_BINARY_REPO", TYPED_HEAD)
    state = _exact_repo("CAL_ATTRIBUTE_STATE_REPO", STATE_HEAD)

    typed_blob = subprocess.check_output(
        [
            "git",
            "-C",
            str(typed),
            "hash-object",
            "research/typed_spatial_relation_discriminator_rc0/candidate.py",
        ],
        text=True,
    ).strip()
    state_blob = subprocess.check_output(
        [
            "git",
            "-C",
            str(state),
            "hash-object",
            "research/attribute_state_contract_rc0/candidate.py",
        ],
        text=True,
    ).strip()

    assert typed_blob == "4dbbc3a94ce561ef71590c8ac900c87259ac361f"
    assert state_blob == "5d33fd1fd5259cd3d3176b9c7e748252a8eac646"
