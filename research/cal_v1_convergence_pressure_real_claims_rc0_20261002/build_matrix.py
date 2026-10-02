"""CAL #188 apparatus: construct expectations without importing/executing CAL.

Owner: CAL issue #188. This generator is frozen with its emitted matrix.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
CMP = "Alpha had a higher rate than Beta."
EVT = "Alice reviewed dossier before Bob archived dossier."
matrix = []


def add(case_id, domain, operation, invariant, **kwargs):
    matrix.append(dict(case_id=case_id, domain=domain, operation=operation,
                       invariant=invariant, **kwargs))


add("H-182", "H", "historical", "Replay unchanged blob; retain historical labels and outer actual subject identity; no CRITICAL_FAIL.")
cohort = json.loads((ROOT / "COHORT.json").read_text())
for row in cohort["cases"]:
    add(row["case_id"], "REAL", "real", "Correct terminal or documented authoring/refusal/measurement limit; opposite terminal is critical.", cohort_case_id=row["case_id"])

for family, claim in (("strict_comparison", CMP), ("direct_event_order", EVT)):
    for mutation in ("missing", "extra-semantic", "unsupported-direction", "claim-hash",
                     "claim-id", "proposition-id", "orientation", "inversion", "family-substitution",
                     "duplicate-keys", "malformed-json", "invalid-utf8", "unknown-top",
                     "unknown-nested", "whitespace-field", "punctuation-field", "confusable",
                     "long-field", "format-only"):
        add(f"A-{family}-{mutation}", "A", "target", "Conformance rejects semantic/binding/serialization drift; formatting preserves meaning; rejected supported workflow executes zero times.",
            family=family, claim=claim, mutation=mutation, conform_accept=(mutation == "format-only"))
    add(f"A-{family}-raw-bypass", "A", "bypass", "Raw structural acceptance and terminal drift are INTERFACE_GAP; supported author/conform gate rejects and produces no output.", family=family, claim=claim)

for family in ("strict_comparison", "direct_event_order"):
    for mutation in ("passage-hash", "source-hash-invalid", "passage-id", "duplicate-id",
                     "stale-measurement", "source-substitution-stale", "foreign-authority",
                     "forged-authority", "foreign-relation", "aperture-stale",
                     "source-identity-stale", "claim-identity-stale"):
        add(f"D-{family}-{mutation}", "D", "binding", "Hash/identity mutation or stale receipt must refuse before a terminal relation/composition; no silent dropping.", family=family, mutation=mutation)
    add(f"D-{family}-same-world-paths", "D", "same-world", "Different filesystem paths reconstruct byte-identical outputs.", family=family)
    add(f"D-{family}-empty", "D", "semantic", "Empty admitted world must abstain.", family=family, claim=CMP if family == "strict_comparison" else EVT, texts=[], expected="not_checkable")
    add(f"D-{family}-bounded-flood", "D", "semantic", "128 nondeciding distractors cannot flip the deciding relation and cannot disappear from traces.", family=family, claim=CMP if family == "strict_comparison" else EVT,
        texts=[CMP if family == "strict_comparison" else EVT] + [f"Unrelated maintenance note {i}." for i in range(128)], expected="supported")

for op in ("replay", "source-wheel", "wheel-sdist", "overwrite", "file", "symlink",
           "dangling-symlink", "same-output", "distinct-output", "partial-failure",
           "symlink-race", "environment", "manifest-hashes"):
    add("E-" + op, "E", "operational", "Equivalent runs preserve all output bytes; unsafe destinations fail without mutation; two bounded writers yield one complete winner; injected finalization failure cleans temporary output.", control=op)

def semantic(prefix, family, claim, texts, expected, coverage=False, pair=None):
    add(prefix, "B" if family == "strict_comparison" else "C", "semantic",
        "Preserve expressed source relation; mixed/unresolved evidence must not decide; equivalent transformations cannot flip terminal direction.",
        family=family, claim=claim, texts=texts, expected=expected, coverage=coverage, pair=pair)

# Direct-event matrix first; comparison scope/negation falsifiers are last so
# ordinary custody, packaging and the real cohort precede a possible stop.
for suffix, text, expected in (
    ("support", EVT, "supported"),
    ("refute", EVT.replace("before", "after"), "contradicted"),
    ("swap", "Bob archived dossier after Alice reviewed dossier.", "supported"),
    ("event-mismatch", "Clara reviewed dossier before Bob archived dossier.", "not_checkable"),
    ("predicate-mismatch", "Alice signed dossier before Bob archived dossier.", "not_checkable"),
    ("object-mismatch", "Alice reviewed memo before Bob archived dossier.", "not_checkable"),
    ("unrelated", "Clara signed memo before Dan released memo.", "not_checkable"),
    ("negative", "Alice did not review dossier before Bob archived dossier.", "not_checkable"),
    ("multiple-cues", "Alice reviewed dossier before Bob archived dossier after Clara signed memo.", "not_checkable"),
    ("no-cue", "Alice reviewed dossier. Bob archived dossier.", "not_checkable"),
    ("lowercase", EVT.lower(), "supported"),
    ("punctuation", "Alice reviewed dossier, before Bob archived dossier.", "supported"),
    ("complex", "After a second examination, Alice reviewed the dossier before its archival by Bob.", "supported"),
    ("uppercase-cue", EVT.replace("before", "BEFORE"), "supported"),
):
    semantic("C-" + suffix, "direct_event_order", EVT, [text], expected,
              coverage=suffix in {"lowercase", "punctuation", "complex"}, pair="C-support" if suffix == "swap" else None)
semantic("C-after-target", "direct_event_order", EVT.replace("before", "after"), [EVT], "contradicted")
semantic("C-target-swap-invert", "direct_event_order", "Bob archived dossier after Alice reviewed dossier.", [EVT], "supported", pair="C-support")
for suffix, texts, expected in (
    ("duplicate", [EVT, EVT], "supported"),
    ("permutation-a", [EVT, "No relation is expressed here."], "supported"),
    ("permutation-b", ["No relation is expressed here.", EVT], "supported"),
    ("conflict", [EVT, EVT.replace("before", "after")], "not_checkable"),
    ("negative-mixed", [EVT, "Alice did not review dossier before Bob archived dossier."], "not_checkable"),
    ("world-substitution", [EVT.replace("before", "after")], "contradicted"),
): semantic("C-" + suffix, "direct_event_order", EVT, texts, expected, pair="C-permutation-a" if suffix == "permutation-b" else None)

for suffix, text, expected, coverage in (
    ("support", CMP, "supported", False),
    ("refute", CMP.replace("higher", "lower"), "contradicted", False),
    ("swap", "Beta had a lower rate than Alpha.", "supported", False),
    ("unresolved-cue", "The comparison might be higher.", "not_checkable", False),
    ("unrelated-entities", "Gamma had a higher rate than Delta.", "not_checkable", False),
    ("lowercase", CMP.lower(), "supported", True),
    ("punctuation", CMP.replace(".", "!"), "supported", True),
    ("greater", CMP.replace("higher", "greater"), "supported", False),
    ("larger", CMP.replace("higher", "larger"), "supported", False),
    ("exceeded", "Alpha exceeded Beta.", "supported", False),
    ("time-scope", "Alpha had a higher rate than Beta in 2025.", "supported", True),
    ("plural", "Alpha had higher rates than Beta.", "supported", True),
    ("equality", "Alpha had an equal rate to Beta.", "not_checkable", False),
    ("non-order", "Alpha had a different rate from Beta.", "not_checkable", False),
): semantic("B-" + suffix, "strict_comparison", CMP, [text], expected, coverage=coverage, pair="B-support" if suffix == "swap" else None)
semantic("B-target-swap-invert", "strict_comparison", "Beta had a lower rate than Alpha.", [CMP], "supported", pair="B-support")
for suffix, texts, expected in (
    ("irrelevant-insertion", [CMP, "Gamma had a higher rate than Delta."], "supported"),
    ("permutation-a", [CMP, "No deciding comparison here."], "supported"),
    ("permutation-b", ["No deciding comparison here.", CMP], "supported"),
    ("mixed", [CMP, CMP.replace("higher", "lower")], "not_checkable"),
    ("unmeasurable-insertion", [CMP, "The comparison might be higher."], "supported"),
    ("duplicate", [CMP, CMP], "supported"),
    ("near-duplicate", [CMP, "Alpha had a HIGHER rate than Beta."], "supported"),
    ("world-substitution", [CMP.replace("higher", "lower")], "contradicted"),
): semantic("B-" + suffix, "strict_comparison", CMP, texts, expected, pair="B-permutation-a" if suffix == "permutation-b" else None)

# These are source-grounding falsifiers, not promises of general NLP coverage.
# Multiple incompatible cues require abstention. Explicit negation clearly
# refutes higher; contradicted or conservative abstention is acceptable.
semantic("B-explicit-negation", "strict_comparison", CMP,
          ["Alpha did not have a higher rate than Beta."], "refuted_or_abstain")
semantic("B-multiple-cues", "strict_comparison", CMP,
          ["Alpha had a higher rate than Beta, but Alpha had a lower rate than Beta."], "not_checkable")

payload = {"schema": "cal188-matrix-v1", "subject_commit": "6bb0d60f3e2286123f56de5657de4e97d6374c63",
           "stop_rule": "Freeze first meaningful negative immediately. On genuine CRITICAL_FAIL freeze counterexample, block release progression, stop subsequent scientific cases; mark remaining NOT_RUN. Never change expectations or subject.",
           "historical_adapter": "Unchanged harness with external record observer; original CANDIDATE constant retained as historical metadata, outer receipt binds actual subject. OBSERVATION is not a scientific pass/failure.",
           "real_route": "Exact frozen claim -> CAL author_target; refusal is ROBUSTNESS_LIMIT and semantic execution NOT_RUN. If accepted, exact target and verbatim frozen passage go to audit internal seam; no invented target or evidence rewriting.",
           "scope": {"concurrent_writers": 2, "distractors": 128, "long_field_chars": 8192,
                     "general_accuracy": "NOT_ESTABLISHED", "human_gold": False}, "cases": matrix}
(ROOT / "MATRIX.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
print(len(matrix), "preregistered cases; no CAL imports or calls")
