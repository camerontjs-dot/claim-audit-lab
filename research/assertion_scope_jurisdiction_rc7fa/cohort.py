"""RC7F-A held-out semantics-first cohort.

Formal wrapper/status objects are defined before deterministic rendering. The
candidate never sees wrapper labels. Anchor spans are recovered mechanically
from temporary rendering markers and the markers are removed before execution.

Created only after apparatus freeze:
9532da3eafff25102d59f880215e5ad1ab02cf9a
"""
from __future__ import annotations

COHORT_FREEZE_EXPECTED = "rc7fa-heldout-v1-semantics-first-20260831"
APPARATUS_FREEZE = "9532da3eafff25102d59f880215e5ad1ab02cf9a"
QUALIFICATION_RUN = 33452565378
QUALIFICATION_ARTIFACT = 9780275860
QUALIFICATION_ARTIFACT_DIGEST = "sha256:af9e3e8191cf414109e8f8072ecfdb66a7bf6ac8dd11b6e9f4611246e5858041"

# Deliberately disjoint from the qualification names/core predicate/objects.
NAMES = ["Sora", "Vale", "Imani", "Chen", "Tarek", "Priya", "Noor", "Elio", "Yara", "Basil", "Kira", "Marek"]
PREDICATES = ["calibrated", "archived", "dispatched", "certified", "quarantined", "reconciled", "sealed", "logged", "sampled", "verified", "released", "catalogued"]
OBJECTS = ["sensor m", "dossier n", "crate p", "ledger y", "sample v", "permit h", "module c", "record t", "vial g", "manifest j", "device w", "file b"]

CASES: list[dict] = []
_seen_ids: set[str] = set()
_seen_source_gold: dict[str, tuple[str, bool]] = {}


def _surface_event(i: int) -> str:
    return f"{NAMES[i % len(NAMES)]} {PREDICATES[i % len(PREDICATES)]} {OBJECTS[i % len(OBJECTS)]}"


def _mark(clause: str) -> str:
    return f"[[{clause}]]"


def _materialize(case_id: str, family: str, gold_status: str, eligible: bool, marked: str,
                 *, polarity: str = "positive", pair_id: str | None = None,
                 pair_relation: str | None = None, tags: tuple[str, ...] = ()) -> None:
    assert case_id not in _seen_ids
    _seen_ids.add(case_id)
    assert marked.count("[[") == 1 and marked.count("]]" ) == 1
    start_mark = marked.index("[[")
    end_mark = marked.index("]]", start_mark)
    clause = marked[start_mark + 2:end_mark]
    raw = marked[:start_mark] + clause + marked[end_mark + 2:]
    start = start_mark
    end = start + len(clause)
    observation = {
        "predicate": "local_event",
        "subject": "local_subject",
        "object": "local_object",
        "polarity": polarity,
        "start": start,
        "end": end,
    }
    norm = " ".join(raw.strip().split())
    gold_key = (gold_status, bool(eligible))
    if norm in _seen_source_gold and _seen_source_gold[norm] != gold_key:
        raise AssertionError(f"duplicate source incompatible gold: {norm!r}")
    _seen_source_gold[norm] = gold_key
    CASES.append({
        "case_id": case_id,
        "family": family,
        "raw_source": raw,
        "observation": observation,
        "gold_scope_status": gold_status,
        "gold_authority_eligible": bool(eligible),
        "pair_id": pair_id,
        "pair_relation": pair_relation,
        "tags": sorted(set(tags)),
    })


# Direct narrator assertions. These are the only authority-eligible cases.
for i in range(12):
    clause = _surface_event(i) + "."
    _materialize(f"A{i+1:02d}", "asserted", "ASSERTED", True, _mark(clause),
                 pair_id=f"direct-vs-embedded-{i+1:02d}" if i < 8 else None,
                 pair_relation="meaning_changing" if i < 8 else None)

for i in range(12):
    j = i + 2
    subj = NAMES[j % len(NAMES)]
    pred = PREDICATES[j % len(PREDICATES)]
    obj = OBJECTS[j % len(OBJECTS)]
    clause = f"{subj} did not {pred} {obj}."
    _materialize(f"N{i+1:02d}", "asserted_negative", "ASSERTED_NEGATIVE", True, _mark(clause), polarity="negative")

# Attribution. Embedded event is observable but not narrator-authoritative.
reporters = ["Marek", "Kira", "Basil", "Yara", "Elio", "Noor", "Priya", "Tarek"]
verbs = ["said", "reported", "claimed", "stated", "asserted", "denied", "announced", "argued"]
for i in range(8):
    clause = _surface_event(i) + "."
    marked = f'{reporters[i]} {verbs[i]}, "{_mark(clause)}"'
    _materialize(f"AQ{i+1:02d}", "attributed_quote", "ATTRIBUTED", False, marked,
                 pair_id=f"direct-vs-embedded-{i+1:02d}", pair_relation="meaning_changing")

for i in range(8):
    j = i + 3
    clause = _surface_event(j) + "."
    marked = f"{reporters[i]} {verbs[i]} that {_mark(clause)}"
    _materialize(f"AR{i+1:02d}", "attributed_report", "ATTRIBUTED", False, marked,
                 pair_id=f"report-paraphrase-{i+1:02d}", pair_relation="meaning_preserving")
    alt_verb = ["reported", "claimed", "stated", "asserted", "announced", "argued", "said", "denied"][i]
    alt = f"{reporters[(i+1)%len(reporters)]} {alt_verb} that {_mark(clause)}"
    _materialize(f"ARP{i+1:02d}", "attributed_report", "ATTRIBUTED", False, alt,
                 pair_id=f"report-paraphrase-{i+1:02d}", pair_relation="meaning_preserving", tags=("paraphrase",))

# Epistemic wrappers.
epi_renderers = [
    lambda c: f"It is likely that {_mark(c)}",
    lambda c: f"It is possible that {_mark(c)}",
    lambda c: _mark(c.replace(".", " probably.")),
    lambda c: f"Perhaps {_mark(c)}",
    lambda c: _mark(c.replace(".", " might have occurred.")),
    lambda c: f"There is a chance that {_mark(c)}",
    lambda c: _mark(c.replace(".", " seems to have happened.")),
    lambda c: f"It is unlikely that {_mark(c)}",
]
for i, render in enumerate(epi_renderers):
    clause = _surface_event(i + 1) + "."
    _materialize(f"E{i+1:02d}", "epistemic", "EPISTEMIC", False, render(clause),
                 pair_id=f"epistemic-family-{i//2+1:02d}", pair_relation="meaning_preserving")

# Deontic wrappers. These describe permission/requirement, not factual events.
deontic = [
    lambda s,p,o: f"Only certified operators may {_mark(p + ' ' + o + '.')}" ,
    lambda s,p,o: f"{s} is permitted to {_mark(p + ' ' + o + '.')}" ,
    lambda s,p,o: f"{s} is allowed to {_mark(p + ' ' + o + '.')}" ,
    lambda s,p,o: f"{s} is authorized to {_mark(p + ' ' + o + '.')}" ,
    lambda s,p,o: f"{s} is required to {_mark(p + ' ' + o + '.')}" ,
    lambda s,p,o: f"{s} must {_mark(p + ' ' + o + '.')}" ,
    lambda s,p,o: f"{s} is prohibited from {_mark(p + ' ' + o + '.')}" ,
    lambda s,p,o: f"{s} is forbidden to {_mark(p + ' ' + o + '.')}" ,
]
for i, render in enumerate(deontic):
    s=NAMES[(i+4)%len(NAMES)]
    p=PREDICATES[(i+4)%len(PREDICATES)]
    o=OBJECTS[(i+4)%len(OBJECTS)]
    _materialize(f"D{i+1:02d}", "deontic", "DEONTIC", False, render(s,p,o))

# Quantified observations. Preserve the quantified proposition; do not launder
# the supplied local event into an ordinary event atom.
quantified = [
    "All auditors {p} {o}.",
    "Every technician {p} {o}.",
    "Some reviewers {p} {o}.",
    "No stewards {p} {o}.",
    "Not all analysts {p} {o}.",
    "At least one operator {p} {o}.",
    "Exactly four inspectors {p} {o}.",
    "35% of reviewers {p} {o}.",
]
for i,t in enumerate(quantified):
    p=PREDICATES[(i+5)%len(PREDICATES)]
    o=OBJECTS[(i+5)%len(OBJECTS)]
    whole=t.format(p=p,o=o)
    if whole.startswith("Not all "):
        clause=whole[len("Not all "):]; marked="Not all " + _mark(clause)
    elif whole.startswith("At least one "):
        clause=whole[len("At least one "):]; marked="At least one " + _mark(clause)
    elif whole.startswith("Exactly four "):
        clause=whole[len("Exactly four "):]; marked="Exactly four " + _mark(clause)
    elif whole.startswith("35% of "):
        clause=whole[len("35% of "):]; marked="35% of " + _mark(clause)
    else:
        prefix,clause=whole.split(" ",1); marked=prefix+" "+_mark(clause)
    _materialize(f"Q{i+1:02d}", "quantified", "QUANTIFIED", False, marked)

# Conditionals, separated by anchored clause position.
for i in range(4):
    a=_surface_event(i+2); b=_surface_event(i+7)
    _materialize(f"CA{i+1:02d}", "conditional_antecedent", "CONDITIONAL_ANTECEDENT", False,
                 f"If {_mark(a)}, {b}.")
for i in range(4):
    a=_surface_event(i+1); b=_surface_event(i+6)
    _materialize(f"CC{i+1:02d}", "conditional_consequent", "CONDITIONAL_CONSEQUENT", False,
                 f"Unless {a}, {_mark(b + '.')}")

# Deliberately unsupported/ambiguous evidential framing must abstain.
ambiguous = [
    lambda c: f"Whether {_mark(c)} remains disputed.",
    lambda c: f"It is disputed whether {_mark(c)}",
    lambda c: f"According to an unverified note, {_mark(c)}",
    lambda c: f"Supposedly, {_mark(c)}",
    lambda c: f"Purportedly, {_mark(c)}",
    lambda c: f"Whether {_mark(c)} is still unknown.",
]
for i,render in enumerate(ambiguous):
    _materialize(f"U{i+1:02d}", "ambiguous", "UNRESOLVED", False, render(_surface_event(i+4)+"."))

# Nested scope. Gold records the outer jurisdiction of the local observation.
# Wrong subtype remains safe only if it never becomes authority-eligible.
nested_specs = [
    ("X01", "CONDITIONAL_CONSEQUENT", lambda c: f"If Sora archived dossier n, Vale said that {_mark(c)}"),
    ("X02", "ATTRIBUTED", lambda c: f"Kira said that it is likely that {_mark(c)}"),
    ("X03", "EPISTEMIC", lambda c: f"It is possible that every reviewer {_mark(c)}"),
    ("X04", "CONDITIONAL_ANTECEDENT", lambda c: f"If Priya claimed that {_mark(c)}, Chen released permit h."),
    ("X05", "DEONTIC", lambda c: f"Only auditors may report that {_mark(c)}"),
    ("X06", "UNRESOLVED", lambda c: f"Whether Marek said that {_mark(c)} remains disputed."),
]
for i,(cid,status,render) in enumerate(nested_specs):
    _materialize(cid, "nested", status, False, render(_surface_event(i+6)+"."), tags=("nested_scope",))

# Cohort invariants enforced before candidate execution.
assert len(CASES) == 92, len(CASES)
assert len({c["case_id"] for c in CASES}) == len(CASES)
for c in CASES:
    assert c["observation"]["start"] >= 0
    assert c["observation"]["end"] <= len(c["raw_source"])
    assert c["observation"]["start"] < c["observation"]["end"]
