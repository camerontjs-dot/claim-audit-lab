"""RC7E held-out formal semantics-first cohort.

Gold semantic objects are constructed before rendering. Rendered text is never
read back to establish gold. This file was authored after apparatus freeze
05f6570cbfc46aad7941b791aa7345209494da69 and after source-manifest freeze
8e9ae32574b871a3f340090270bdc8843db3e2df.

No model/parser/instrument output is used to establish or revise gold.
"""
from __future__ import annotations

COHORT_FREEZE_EXPECTED = "rc7e-heldout-v1-formal-semantics-first-20260831"
APPARATUS_FREEZE = "05f6570cbfc46aad7941b791aa7345209494da69"
SOURCE_MANIFEST_FREEZE = "8e9ae32574b871a3f340090270bdc8843db3e2df"

CASES = []
_seen = set()

def add(case_id, text, gold, group, *, tags=(), pair_id=None, pair_relation=None, basis=(), composition_oracle=True):
    assert case_id not in _seen
    _seen.add(case_id)
    assert isinstance(text, str) and text
    assert isinstance(gold, dict)
    CASES.append({
        "case_id": case_id,
        "text": text,
        "gold": gold,
        "gold_dimensions": sorted(gold),
        "group": group,
        "tags": sorted(set(tags)),
        "pair_id": pair_id,
        "pair_relation": pair_relation,
        "basis": list(basis),
        "composition_oracle": bool(composition_oracle),
    })

def evt(predicate, subject, object_, polarity="positive"):
    return {"kind": "event", "predicate": predicate, "subject": subject, "object": object_, "polarity": polarity}

def quantifier(value, population, predicate):
    return {"kind": "quantifier", "quantifier": value, "population": population, "predicate": predicate}

def permission(population, predicate):
    return {"kind": "necessary_permission_condition", "population": population, "predicate": predicate}

def explicit_permission(entity, predicate, value):
    return {"kind": "explicit_permission", "entity": entity, "predicate": predicate, "value": value}

def membership(entity, population, value):
    return {"kind": "membership", "entity": entity, "population": population, "value": value}

def exception(entity):
    return {"kind": "exception", "excluded": entity}

def temporal(relation, reference):
    return {"kind": "temporal_scope", "relation": relation, "reference": reference}

def subclass(child, parent):
    return {"kind": "subclass", "child": child, "parent": parent}

def probability(value):
    return {"kind": "epistemic_probability", "value": value}

def quantitative(kind, surface):
    return {"kind": "quantitative_scope", "quantitative_kind": kind, "surface": surface}

def conditional(antecedent, consequent, marker="if"):
    return {"kind": "conditional", "marker": marker, "antecedent": antecedent, "consequent": consequent}

def comparison(left, relation, right):
    return {"kind": "comparison", "left": left, "relation": relation, "right": right}

def coref(*mentions):
    return {"kind": "coreference_chain", "mentions": list(mentions)}

def attribution(speaker, quote):
    return {"kind": "attribution", "speaker": speaker, "quote": quote}

def event_order(first, relation, second):
    return {"kind": "event_ordering", "first": first, "relation": relation, "second": second}

def cap(s):
    return s[:1].upper() + s[1:]

B_RULE = ("ruletaker_method",)
B_SCOPE = ("fracas", "help")
B_DEONTIC = ("lomo", "eu_legislation_disagreement")
B_QUANTITY = ("measeval",)
B_DISCOURSE = ("gum",)
B_TEMPORAL = ("maven_ere_matres",)

# ---------------------------------------------------------------------------
# Atomic controls: formal objects first, deterministic surface realizations.
# ---------------------------------------------------------------------------

role_rows = [
    ("R01", evt("review", "dana", "protocol q"), "Dana reviewed protocol q.", (), "role-active-passive", "meaning_preserving"),
    ("R02", evt("review", "dana", "protocol q"), "Protocol q was reviewed by Dana.", ("unseen_paraphrase",), "role-active-passive", "meaning_preserving"),
    ("R03", evt("sign", "mira", "certificate x", "positive"), "Mira signed certificate x.", (), "role-polarity", "meaning_changing"),
    ("R04", evt("sign", "mira", "certificate x", "negative"), "Mira did not sign certificate x.", (), "role-polarity", "meaning_changing"),
    ("R05", evt("inspect", "hugo", "shipment k", "negative"), "Hugo never inspected shipment k.", ("unseen_paraphrase",), None, None),
    ("R06", evt("approve", "rowan", "control sheet"), "Control sheet was approved by Rowan.", ("unseen_paraphrase",), None, None),
]
for cid, atom, text, tags, pid, prel in role_rows:
    add(cid, text, {"role_binding": [atom]}, "role_binding", tags=tags, pair_id=pid, pair_relation=prel, basis=B_RULE)

quant_rows = [
    ("Q01", quantifier("every", "reviewers", "approve protocol q"), "All reviewers approved protocol q.", (), "quant-all-every", "meaning_preserving"),
    ("Q02", quantifier("every", "reviewers", "approve protocol q"), "Every one of the reviewers approved protocol q.", ("unseen_paraphrase",), "quant-all-every", "meaning_preserving"),
    ("Q03", quantifier("some", "auditors", "sign release note"), "Some auditors signed release note.", (), "quant-some-none", "meaning_changing"),
    ("Q04", quantifier("none", "auditors", "sign release note"), "No auditors signed release note.", (), "quant-some-none", "meaning_changing"),
    ("Q05", quantifier("not_every", "inspectors", "review control sheet"), "Not all inspectors reviewed control sheet.", ("unseen_paraphrase",), None, None),
    ("Q06", quantifier("some", "analysts", "inspect shipment k"), "At least one analyst inspected shipment k.", ("unseen_paraphrase",), None, None),
]
for cid, atom, text, tags, pid, prel in quant_rows:
    add(cid, text, {"quantifier": [atom]}, "quantifier", tags=tags, pair_id=pid, pair_relation=prel, basis=B_SCOPE)

perm_rows = [
    ("P01", permission("release reviewers", "approve protocol q"), "Only release reviewers may approve protocol q.", (), "permission-surface", "meaning_preserving"),
    ("P02", permission("release reviewers", "approve protocol q"), "Permission to approve protocol q is restricted to release reviewers.", ("unseen_paraphrase",), "permission-surface", "meaning_preserving"),
    ("P03", explicit_permission("dana", "release shipment k", "permitted"), "Dana is permitted to release shipment k.", (), "permission-value", "meaning_changing"),
    ("P04", explicit_permission("dana", "release shipment k", "not_permitted"), "Dana is not permitted to release shipment k.", (), "permission-value", "meaning_changing"),
    ("P05", membership("mira", "quality deputies", "member"), "Mira is a member of quality deputies.", (), None, None),
    ("P06", membership("mira", "quality deputies", "non_member"), "Mira is not a member of quality deputies.", ("unseen_paraphrase",), None, None),
]
for cid, atom, text, tags, pid, prel in perm_rows:
    add(cid, text, {"permission": [atom]}, "permission", tags=tags, pair_id=pid, pair_relation=prel, basis=B_DEONTIC)

temp_rows = [
    ("T01", temporal("before", "the deadline"), "The review occurred before the deadline.", (), "temporal-direction", "meaning_changing"),
    ("T02", temporal("after", "the deadline"), "The review occurred after the deadline.", (), "temporal-direction", "meaning_changing"),
    ("T03", temporal("until", "the cutoff"), "The authorization remains active until the cutoff.", ("unseen_paraphrase",), None, None),
    ("T04", temporal("as_of", "2026-09-15"), "The classification applies as of 2026-09-15.", ("unseen_paraphrase",), None, None),
]
for cid, atom, text, tags, pid, prel in temp_rows:
    add(cid, text, {"temporal": [atom]}, "temporal", tags=tags, pair_id=pid, pair_relation=prel, basis=B_TEMPORAL)

sub_rows = [
    ("S01", subclass("quality deputies", "approvers"), "Quality deputies are a subtype of approvers.", (), "subclass-surface", "meaning_preserving"),
    ("S02", subclass("quality deputies", "approvers"), "Quality deputies are a subset of approvers.", ("unseen_paraphrase",), "subclass-surface", "meaning_preserving"),
    ("S03", subclass("release analysts", "reviewers"), "Release analysts fall under reviewers.", (), None, None),
    ("S04", subclass("field inspectors", "auditors"), "Field inspectors are a kind of auditors.", ("unseen_paraphrase",), None, None),
]
for cid, atom, text, tags, pid, prel in sub_rows:
    add(cid, text, {"subclass": [atom]}, "subclass", tags=tags, pair_id=pid, pair_relation=prel, basis=B_RULE)

prob_rows = [
    ("B01", probability("likely"), "It is likely that Dana reviewed protocol q.", (), "probability-direction", "meaning_changing"),
    ("B02", probability("unlikely"), "It is unlikely that Dana reviewed protocol q.", (), "probability-direction", "meaning_changing"),
    ("B03", probability("probable"), "Dana probably reviewed protocol q.", (), None, None),
    ("B04", probability("possible"), "There is a chance Dana reviewed protocol q.", ("unseen_paraphrase",), None, None),
]
for cid, atom, text, tags, pid, prel in prob_rows:
    add(cid, text, {"probability": [atom]}, "probability", tags=tags, pair_id=pid, pair_relation=prel, basis=B_SCOPE)

quantity_rows = [
    ("N01", quantitative("exact_count", "exactly three"), "Exactly three auditors reviewed protocol q.", (), "quantity-bound", "meaning_changing"),
    ("N02", quantitative("minimum_count", "at least three"), "At least three auditors reviewed protocol q.", (), "quantity-bound", "meaning_changing"),
    ("N03", quantitative("percentage", "40%"), "40% of reviewers approved control sheet.", (), None, None),
    ("N04", quantitative("percentage", "forty percent"), "Forty percent of reviewers approved control sheet.", ("unseen_paraphrase",), None, None),
    ("N05", quantitative("majority", "a majority of"), "A majority of inspectors signed release note.", (), None, None),
    ("N06", quantitative("few", "few inspectors"), "Few inspectors approved protocol q.", ("unseen_paraphrase",), None, None),
]
for cid, atom, text, tags, pid, prel in quantity_rows:
    add(cid, text, {"quantitative": [atom]}, "quantitative", tags=tags, pair_id=pid, pair_relation=prel, basis=B_QUANTITY)

# ---------------------------------------------------------------------------
# Mixed-semantic cases. These intentionally stress scope boundaries that caused
# predecessor overclaim. No reader output is used to define the gold.
# ---------------------------------------------------------------------------

qe_rows = [
    ("QE01", quantifier("every", "reviewers", "approve protocol q"), exception("mira"), "All reviewers approved protocol q except Mira.", ()),
    ("QE02", quantifier("some", "auditors", "sign release note"), exception("hugo"), "Some auditors signed release note, excluding Hugo.", ()),
    ("QE03", quantifier("none", "inspectors", "review control sheet"), exception("nia"), "No inspectors reviewed control sheet other than Nia.", ("unseen_paraphrase",)),
    ("QE04", quantifier("not_every", "analysts", "inspect shipment k"), exception("ada"), "Not all analysts inspected shipment k, apart from Ada.", ("unseen_paraphrase",)),
    ("QE05", quantifier("every", "technicians", "release shipment k"), exception("rowan"), "All technicians released shipment k with the exception of Rowan.", ()),
    ("QE06", quantifier("some", "reviewers", "approve protocol q"), exception("mira"), "At least one reviewer approved protocol q save for Mira.", ("unseen_paraphrase",)),
]
for cid, qatom, eatom, text, tags in qe_rows:
    add(cid, text, {"quantifier": [qatom], "exception": [eatom]}, "quantifier_exception", tags=(*tags, "mixed_semantic"), basis=(*B_SCOPE, "eu_legislation_disagreement"))

qp_rows = [
    ("QP01", quantifier("every", "reviewers", "approve protocol q"), probability("probable"), "Probably, all reviewers approved protocol q.", ()),
    ("QP02", quantifier("some", "auditors", "sign release note"), probability("likely"), "Likely, some auditors signed release note.", ()),
    ("QP03", quantifier("none", "inspectors", "review control sheet"), probability("unlikely"), "It is unlikely that no inspectors reviewed control sheet.", ("unseen_paraphrase",)),
    ("QP04", quantifier("not_every", "analysts", "inspect shipment k"), probability("possible"), "There is a chance that not all analysts inspected shipment k.", ("unseen_paraphrase",)),
]
for cid, qatom, patom, text, tags in qp_rows:
    add(cid, text, {"quantifier": [qatom], "probability": [patom]}, "quantifier_probability", tags=(*tags, "mixed_semantic"), basis=B_SCOPE)

pe_rows = [
    ("PE01", permission("release reviewers", "approve protocol q"), exception("mira"), "Only release reviewers may approve protocol q, except Mira.", ()),
    ("PE02", permission("quality deputies", "release shipment k"), exception("hugo"), "Permission to release shipment k is restricted to quality deputies, excluding Hugo.", ()),
    ("PE03", permission("inspectors", "sign release note"), exception("nia"), "Only inspectors may sign release note, apart from Nia.", ("unseen_paraphrase",)),
    ("PE04", permission("auditors", "review control sheet"), exception("ada"), "Permission to review control sheet is restricted to auditors, save for Ada.", ("unseen_paraphrase",)),
]
for cid, patom, eatom, text, tags in pe_rows:
    add(cid, text, {"permission": [patom], "exception": [eatom]}, "permission_exception", tags=(*tags, "mixed_semantic"), basis=B_DEONTIC)

pt_rows = [
    ("PT01", permission("release stewards", "sign certificate x"), temporal("before", "the deadline"), "Only release stewards may sign certificate x before the deadline.", ()),
    ("PT02", permission("inspectors", "release shipment k"), temporal("after", "the cutoff"), "Permission to release shipment k is restricted to inspectors after the cutoff.", ()),
    ("PT03", permission("reviewers", "approve protocol q"), temporal("until", "the deadline"), "Only reviewers may approve protocol q until the deadline.", ("unseen_paraphrase",)),
    ("PT04", permission("quality deputies", "review control sheet"), temporal("as_of", "2026-09-15"), "Permission to review control sheet is restricted to quality deputies as of 2026-09-15.", ("unseen_paraphrase",)),
]
for cid, patom, tatom, text, tags in pt_rows:
    add(cid, text, {"permission": [patom], "temporal": [tatom]}, "permission_temporal", tags=(*tags, "mixed_semantic"), basis=(*B_DEONTIC, *B_TEMPORAL))

sp_rows = [
    ("SP01", subclass("quality deputies", "approvers"), permission("approvers", "release shipment k"), "Quality deputies are a subtype of approvers. Only approvers may release shipment k.", ()),
    ("SP02", subclass("release analysts", "reviewers"), permission("reviewers", "approve protocol q"), "Release analysts are a subset of reviewers. Permission to approve protocol q is restricted to reviewers.", ()),
    ("SP03", subclass("field inspectors", "auditors"), permission("auditors", "sign release note"), "Field inspectors fall under auditors. Only auditors may sign release note.", ("unseen_paraphrase",)),
    ("SP04", subclass("validation aides", "inspectors"), permission("inspectors", "review control sheet"), "Validation aides are a kind of inspectors. Permission to review control sheet is restricted to inspectors.", ("unseen_paraphrase",)),
]
for cid, satom, patom, text, tags in sp_rows:
    add(cid, text, {"subclass": [satom], "permission": [patom]}, "subclass_permission", tags=(*tags, "mixed_semantic"), basis=(*B_RULE, *B_DEONTIC))

qr_rows = [
    ("QR01", quantitative("exact_count", "exactly three"), evt("review", "auditors", "protocol q"), "Exactly three auditors reviewed protocol q.", ()),
    ("QR02", quantitative("minimum_count", "at least four"), evt("inspect", "technicians", "shipment k"), "At least four technicians inspected shipment k.", ()),
    ("QR03", quantitative("percentage", "40%"), evt("approve", "reviewers", "control sheet"), "40% of reviewers approved control sheet.", ("unseen_paraphrase",)),
    ("QR04", quantitative("majority", "a majority of"), evt("sign", "inspectors", "release note"), "A majority of inspectors signed release note.", ("unseen_paraphrase",)),
]
for cid, qatom, eatom, text, tags in qr_rows:
    add(cid, text, {"quantitative": [qatom], "role_binding": [eatom]}, "quantity_event", tags=(*tags, "mixed_semantic"), basis=(*B_QUANTITY, *B_RULE))

# Conditionals: embedded events are not asserted as ordinary narrator-level facts.
cond_rows = [
    ("C01", conditional(evt("review","dana","protocol q"), evt("sign","mira","certificate x")), "If Dana reviews protocol q, Mira signs certificate x.", (), "conditional-polarity", "meaning_changing"),
    ("C02", conditional(evt("review","dana","protocol q","negative"), evt("sign","mira","certificate x")), "If Dana does not review protocol q, Mira signs certificate x.", (), "conditional-polarity", "meaning_changing"),
    ("C03", conditional(evt("inspect","hugo","shipment k"), evt("approve","rowan","control sheet"), marker="provided that"), "Provided that Hugo inspects shipment k, Rowan approves control sheet.", ("unseen_paraphrase",), None, None),
    ("C04", conditional(evt("approve","ada","protocol q"), evt("release","nia","shipment k"), marker="unless"), "Unless Ada approves protocol q, Nia releases shipment k.", ("unseen_paraphrase",), None, None),
]
for cid, catom, text, tags, pid, prel in cond_rows:
    add(cid, text, {"conditional": [catom]}, "conditional_scope", tags=(*tags, "mixed_semantic"), pair_id=pid, pair_relation=prel, basis=(*B_SCOPE, *B_DEONTIC))

comp_rows = [
    ("M01", quantitative("exact_count", "exactly 30"), comparison("team a", "more_than", "team b"), "Team A reviewed exactly 30 files, five more than Team B.", (), "comparison-direction", "meaning_changing"),
    ("M02", quantitative("exact_count", "exactly 30"), comparison("team a", "fewer_than", "team b"), "Team A reviewed exactly 30 files, five fewer than Team B.", (), "comparison-direction", "meaning_changing"),
    ("M03", quantitative("minimum_count", "at least 12"), comparison("group c", "more_than", "group d"), "Group C inspected at least 12 samples, three more than Group D.", ("unseen_paraphrase",), None, None),
    ("M04", quantitative("percentage", "40%"), comparison("site x", "greater_than", "site y"), "Site X approved 40% of packets, a greater share than Site Y.", ("unseen_paraphrase",), None, None),
]
for cid, qatom, matom, text, tags, pid, prel in comp_rows:
    add(cid, text, {"quantitative": [qatom], "comparison": [matom]}, "comparison_quantity", tags=(*tags, "mixed_semantic"), pair_id=pid, pair_relation=prel, basis=("fracas", "measeval"))

# Coreference plus role binding. Gold resolves pronouns to discourse entities.
coref_rows = [
    ("D01", coref("dana","she"), [evt("review","dana","protocol q"), evt("sign","dana","certificate x")], "Dana reviewed protocol q. She signed certificate x.", ()),
    ("D02", coref("dana","dana"), [evt("review","dana","protocol q"), evt("sign","dana","certificate x")], "Dana reviewed protocol q. Dana signed certificate x.", ()),
    ("D03", coref("hugo","he"), [evt("inspect","hugo","shipment k"), evt("approve","hugo","control sheet")], "Hugo inspected shipment k. He approved control sheet.", ("unseen_paraphrase",)),
    ("D04", coref("mira","she"), [evt("approve","mira","protocol q"), evt("release","mira","shipment k")], "Mira approved protocol q. She released shipment k.", ("unseen_paraphrase",)),
]
for cid, catom, events, text, tags in coref_rows:
    add(cid, text, {"coreference": [catom], "role_binding": events}, "coreference_proposition", tags=(*tags, "mixed_semantic"), basis=B_DISCOURSE)

# Attribution is intentionally distinct from narrator-level assertion.
attr_rows = [
    ("A01", attribution("dana","mira approved protocol q"), 'Dana said, "Mira approved protocol q."', (), "attribution-assertion", "meaning_changing"),
    ("A02", None, "Mira approved protocol q.", (), "attribution-assertion", "meaning_changing"),
    ("A03", attribution("hugo","rowan signed certificate x"), 'Hugo said, "Rowan signed certificate x."', ("unseen_paraphrase",), None, None),
    ("A04", attribution("mira","nia released shipment k"), 'Mira said, "Nia released shipment k."', ("unseen_paraphrase",), None, None),
]
for cid, aatom, text, tags, pid, prel in attr_rows:
    gold = {"attribution": [aatom]} if aatom is not None else {"role_binding": [evt("approve","mira","protocol q")]}
    add(cid, text, gold, "attribution_scope", tags=(*tags, "mixed_semantic"), pair_id=pid, pair_relation=prel, basis=B_DISCOURSE)

# Full event ordering is intentionally outside frozen SUTime jurisdiction.
eo_rows = [
    ("E01", event_order(evt("review","dana","protocol q"), "before", evt("sign","mira","certificate x")), [evt("review","dana","protocol q"), evt("sign","mira","certificate x")], "Dana reviewed protocol q before Mira signed certificate x.", (), "event-order-direction", "meaning_changing"),
    ("E02", event_order(evt("review","dana","protocol q"), "after", evt("sign","mira","certificate x")), [evt("review","dana","protocol q"), evt("sign","mira","certificate x")], "Dana reviewed protocol q after Mira signed certificate x.", (), "event-order-direction", "meaning_changing"),
    ("E03", event_order(evt("inspect","hugo","shipment k"), "before", evt("approve","rowan","control sheet")), [evt("inspect","hugo","shipment k"), evt("approve","rowan","control sheet")], "Hugo inspected shipment k before Rowan approved control sheet.", ("unseen_paraphrase",), None, None),
    ("E04", event_order(evt("approve","ada","protocol q"), "after", evt("release","nia","shipment k")), [evt("approve","ada","protocol q"), evt("release","nia","shipment k")], "Ada approved protocol q after Nia released shipment k.", ("unseen_paraphrase",), None, None),
]
for cid, oat, events, text, tags, pid, prel in eo_rows:
    add(cid, text, {"event_ordering": [oat], "role_binding": events}, "event_ordering", tags=(*tags, "mixed_semantic"), pair_id=pid, pair_relation=prel, basis=B_TEMPORAL)

# Irrelevant semantic vocabulary plus a valid proposition.
add("I01", "The permission column is blue. Dana reviewed protocol q.", {"role_binding": [evt("review","dana","protocol q")]}, "irrelevant_plus_valid", tags=("mixed_semantic","domain_trap"), basis=B_RULE)
add("I02", "The temporal dashboard is archived. Mira signed certificate x.", {"role_binding": [evt("sign","mira","certificate x")]}, "irrelevant_plus_valid", tags=("mixed_semantic","domain_trap","unseen_paraphrase"), basis=B_RULE)

# Contradictory same-dimension assertions remain jointly visible.
contradictions = [
    ("X01", "Dana reviewed protocol q. Dana did not review protocol q.", evt("review","dana","protocol q"), evt("review","dana","protocol q","negative")),
    ("X02", "Mira signed certificate x. Mira did not sign certificate x.", evt("sign","mira","certificate x"), evt("sign","mira","certificate x","negative")),
    ("X03", "Hugo inspected shipment k. Hugo never inspected shipment k.", evt("inspect","hugo","shipment k"), evt("inspect","hugo","shipment k","negative")),
    ("X04", "Rowan approved control sheet. Control sheet was not approved by Rowan.", evt("approve","rowan","control sheet"), evt("approve","rowan","control sheet","negative")),
]
for cid, text, a, b in contradictions:
    add(cid, text, {"role_binding": [a,b]}, "contradiction", tags=("mixed_semantic","unseen_paraphrase"), basis=("eu_legislation_disagreement",))

traps = [
    ("Z01", "The permission field was renamed in the schema."),
    ("Z02", "The exception notebook contains six tabs."),
    ("Z03", "The temporal label is printed in bold."),
    ("Z04", "The probability folder was moved yesterday."),
    ("Z05", "The subclass column is empty."),
    ("Z06", "The role binding guide has a new checksum."),
]
for cid, text in traps:
    add(cid, text, {}, "no_semantic_authority", tags=("domain_trap","unseen_paraphrase"), basis=("evaluator_domain_trap",))

# Frozen cohort invariants. These are structural, not result-dependent.
assert len(CASES) == 94, len(CASES)
assert len({c["case_id"] for c in CASES}) == len(CASES)
assert sum("mixed_semantic" in c["tags"] for c in CASES) >= 50
assert sum("unseen_paraphrase" in c["tags"] for c in CASES) >= 30
assert sum(bool(c["pair_id"]) for c in CASES) >= 20
assert all(c["text"] and isinstance(c["gold_dimensions"], list) for c in CASES)
