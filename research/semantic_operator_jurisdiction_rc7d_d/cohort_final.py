"""Accepted RC7D-D held-out cohort loader.

Preserves every case authored in cohort.py, removes only its broken terminal
assertions, and appends two pre-evaluation novel mixed cases required to satisfy
the preregistered cohort counts.
"""
from __future__ import annotations
import ast
from pathlib import Path

SOURCE=Path(__file__).with_name("cohort.py")
tree=ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))
tree.body=[node for node in tree.body if not isinstance(node, ast.Assert)]
ns={"__name__":"rc7d_d_cohort_data"}
exec(compile(tree,str(SOURCE),"exec"),ns)
CASES=list(ns["CASES"])

# Two novel mixed cases authored before evaluator construction.
CASES.append({
    "case_id":"D-SP-09",
    "text":"Release custodians comprise a narrower species within reviewers. Only reviewers may approve the packet.",
    "gold":{
        "subclass":[{"kind":"subclass","child":"release custodians","parent":"reviewers"}],
        "permission":[{"kind":"necessary_permission_condition","population":"reviewers","predicate":"approve the packet"}],
    },
    "gold_dimensions":["permission","subclass"],
    "group":"subclass_permission",
    "novel_surface":True,
    "composition":[("permission","subclass","coexist")],
})
CASES.append({
    "case_id":"D-SP-10",
    "text":"Lab auditors sit beneath the inspector umbrella. Only inspectors may release batch a.",
    "gold":{
        "subclass":[{"kind":"subclass","child":"lab auditors","parent":"inspectors"}],
        "permission":[{"kind":"necessary_permission_condition","population":"inspectors","predicate":"release batch a"}],
    },
    "gold_dimensions":["permission","subclass"],
    "group":"subclass_permission",
    "novel_surface":True,
    "composition":[("permission","subclass","coexist")],
})

assert len(CASES)==84
mixed=[c for c in CASES if len(c["gold_dimensions"])>1]
assert len(mixed)==64
assert sum(1 for c in mixed if c["novel_surface"])==32
