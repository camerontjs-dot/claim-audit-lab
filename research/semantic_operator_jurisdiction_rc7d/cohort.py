"""RC7D held-out mixed-semantic cohort.

Authored after candidate freeze b5b04485cb1e09f025017e25cd6d008e6c5030f6.
Research-only apparatus; not an independent hidden-gold claim.
"""
from __future__ import annotations

CANDIDATE_FREEZE = "b5b04485cb1e09f025017e25cd6d008e6c5030f6"

CASES: list[dict] = []


def add(case_id: str, text: str, gold: dict[str, list[dict]], composition: list[tuple[str, str, str]] | None = None, *, group: str, note: str = "") -> None:
    CASES.append({
        "case_id": case_id,
        "text": text,
        "gold": gold,
        "gold_dimensions": sorted(gold),
        "composition": [
            {"dimensions": sorted([a, b]), "expected": expected}
            for a, b, expected in (composition or [])
        ],
        "group": group,
        "note": note,
    })


# ---------------------------------------------------------------------------
# Quantifier + exception: explicit composition.
# ---------------------------------------------------------------------------

_qe = [
    ("Every technician inspected the vessel except Mira.", "every", "technician", "inspect vessel", "mira"),
    ("All reviewers approved the packet, excluding Hugo.", "every", "reviewers", "approve packet", "hugo"),
    ("Each auditor signed the release other than Ada.", "every", "auditor", "sign release", "ada"),
    ("Some inspectors reviewed the record with the exception of Rowan.", "some", "inspectors", "review record", "rowan"),
    ("No lab analysts approved the sample save for Nia.", "none", "lab analysts", "approve sample", "nia"),
    ("Not every reviewer signed the certificate except Hugo.", "not_every", "reviewer", "sign certificate", "hugo"),
    # Surface variants intentionally not all named in the frozen candidate.
    ("Every technician inspected the vessel bar Mira.", "every", "technician", "inspect vessel", "mira"),
    ("All reviewers aside from Hugo approved the packet.", "every", "reviewers", "approve packet", "hugo"),
    ("Each auditor, Ada excepted, signed the release.", "every", "auditor", "sign release", "ada"),
    ("Some inspectors, Rowan apart, reviewed the record.", "some", "inspectors", "review record", "rowan"),
    ("Every analyst other than Nia approved the sample.", "every", "analyst", "approve sample", "nia"),
    ("Not all reviewers, Hugo being the exception, signed the certificate.", "not_every", "reviewers", "sign certificate", "hugo"),
]
for i, (text, q, pop, pred, excluded) in enumerate(_qe, 1):
    add(
        f"RC7D-QE-{i:02d}", text,
        {
            "quantifier": [{"kind": "quantifier", "quantifier": q, "population": pop, "predicate": pred}],
            "exception": [{"kind": "exception", "excluded": excluded}],
        },
        [("quantifier", "exception", "compose")], group="quantifier_exception",
    )


# ---------------------------------------------------------------------------
# Permission/membership + temporal: preserve both layers.
# ---------------------------------------------------------------------------

_pt = [
    ("Only release stewards may sign the certificate. Nia is a member of the release stewards before the cutoff.",
     [{"kind": "necessary_permission_condition", "population": "release stewards", "predicate": "sign the certificate"}, {"kind": "membership", "entity": "nia", "population": "release stewards", "value": "member"}],
     {"kind": "temporal_scope", "relation": "before", "reference": "the cutoff"}),
    ("Only inspectors may release batch a. Hugo was authorized to release batch a after the deadline.",
     [{"kind": "necessary_permission_condition", "population": "inspectors", "predicate": "release batch a"}, {"kind": "explicit_permission", "entity": "hugo", "predicate": "release batch a", "value": "permitted"}],
     {"kind": "temporal_scope", "relation": "after", "reference": "the deadline"}),
    ("Permission to approve the packet is limited to reviewers. Ada is a member of reviewers prior to the cutoff.",
     [{"kind": "necessary_permission_condition", "population": "reviewers", "predicate": "approve the packet"}, {"kind": "membership", "entity": "ada", "population": "reviewers", "value": "member"}],
     {"kind": "temporal_scope", "relation": "before", "reference": "the cutoff"}),
    ("Only auditors may sign the release. Rowan is not a member of auditors following the deadline.",
     [{"kind": "necessary_permission_condition", "population": "auditors", "predicate": "sign the release"}, {"kind": "membership", "entity": "rowan", "population": "auditors", "value": "non_member"}],
     {"kind": "temporal_scope", "relation": "after", "reference": "the deadline"}),
    ("Only release officers may approve the dossier. Nia was permitted to approve the dossier until the cutoff.",
     [{"kind": "necessary_permission_condition", "population": "release officers", "predicate": "approve the dossier"}, {"kind": "explicit_permission", "entity": "nia", "predicate": "approve the dossier", "value": "permitted"}],
     {"kind": "temporal_scope", "relation": "until", "reference": "the cutoff"}),
    ("Only reviewers may sign the record. As of 2026-08-31, Hugo is a member of reviewers.",
     [{"kind": "necessary_permission_condition", "population": "reviewers", "predicate": "sign the record"}, {"kind": "membership", "entity": "hugo", "population": "reviewers", "value": "member"}],
     {"kind": "temporal_scope", "relation": "as_of", "reference": "2026-08-31"}),
    # Novel temporal paraphrases.
    ("Only release stewards may sign the certificate. Nia belonged to the release stewards ahead of the cutoff.",
     [{"kind": "necessary_permission_condition", "population": "release stewards", "predicate": "sign the certificate"}, {"kind": "membership", "entity": "nia", "population": "release stewards", "value": "member"}],
     {"kind": "temporal_scope", "relation": "before", "reference": "the cutoff"}),
    ("Only inspectors may release batch a. Hugo's authorization to release batch a took effect subsequent to the deadline.",
     [{"kind": "necessary_permission_condition", "population": "inspectors", "predicate": "release batch a"}, {"kind": "explicit_permission", "entity": "hugo", "predicate": "release batch a", "value": "permitted"}],
     {"kind": "temporal_scope", "relation": "after", "reference": "the deadline"}),
]
for i, (text, perm_atoms, temp_atom) in enumerate(_pt, 1):
    add(f"RC7D-PT-{i:02d}", text, {"permission": perm_atoms, "temporal": [temp_atom]}, [("permission", "temporal", "compose")], group="permission_temporal")


# ---------------------------------------------------------------------------
# Permission + exception.
# ---------------------------------------------------------------------------

_pe = [
    ("Only inspectors may release batch a except Mira.", "inspectors", "release batch a", "mira"),
    ("Permission to approve the packet is restricted to reviewers, excluding Hugo.", "reviewers", "approve the packet", "hugo"),
    ("Only release stewards may sign the certificate other than Ada.", "release stewards", "sign the certificate", "ada"),
    ("Only auditors may approve the dossier save for Rowan.", "auditors", "approve the dossier", "rowan"),
    ("Only inspectors may sign the record bar Nia.", "inspectors", "sign the record", "nia"),
    ("Approval permission is restricted to reviewers aside from Hugo.", "reviewers", "approve", "hugo"),
]
for i, (text, pop, pred, excluded) in enumerate(_pe, 1):
    add(
        f"RC7D-PE-{i:02d}", text,
        {
            "permission": [{"kind": "necessary_permission_condition", "population": pop, "predicate": pred}],
            "exception": [{"kind": "exception", "excluded": excluded}],
        },
        [("permission", "exception", "compose")], group="permission_exception",
    )


# ---------------------------------------------------------------------------
# Role binding + polarity. Polarity is internal to the role-binding receipt.
# ---------------------------------------------------------------------------

_role = [
    ("Dana reviewed the dossier.", "review", "dana", "the dossier", "positive"),
    ("Dana did not review the dossier.", "review", "dana", "the dossier", "negative"),
    ("The packet was approved by Mira.", "approve", "mira", "the packet", "positive"),
    ("The packet was not approved by Mira.", "approve", "mira", "the packet", "negative"),
    ("Hugo signed the certificate.", "sign", "hugo", "the certificate", "positive"),
    ("Hugo did not sign the certificate.", "sign", "hugo", "the certificate", "negative"),
    # Novel negative paraphrases expected to challenge bounded rules.
    ("Dana never reviewed the dossier.", "review", "dana", "the dossier", "negative"),
    ("At no point did Hugo sign the certificate.", "sign", "hugo", "the certificate", "negative"),
]
for i, (text, pred, subj, obj, pol) in enumerate(_role, 1):
    add(f"RC7D-RL-{i:02d}", text, {"role_binding": [{"kind": "event", "predicate": pred, "subject": subj, "object": obj, "polarity": pol}]}, group="role_binding")


# ---------------------------------------------------------------------------
# Quantifier + probability: preserve both, do not collapse into one quantifier.
# ---------------------------------------------------------------------------

_qp = [
    ("Probably every technician inspected the vessel.", "every", "technician", "inspect vessel", "probable"),
    ("Every technician probably inspected the vessel.", "every", "technician", "inspect vessel", "probable"),
    ("All reviewers are likely to have approved the packet.", "every", "reviewers", "approve packet", "likely"),
    ("It is likely that all reviewers approved the packet.", "every", "reviewers", "approve packet", "likely"),
    ("Some auditors probably signed the release.", "some", "auditors", "sign release", "probable"),
    ("Not every inspector is likely to have reviewed the record.", "not_every", "inspector", "review record", "likely"),
    ("Every technician conceivably inspected the vessel.", "every", "technician", "inspect vessel", "possible"),
    ("There is a reasonable chance every reviewer approved the packet.", "every", "reviewer", "approve packet", "possible"),
]
for i, (text, q, pop, pred, prob) in enumerate(_qp, 1):
    add(
        f"RC7D-QP-{i:02d}", text,
        {
            "quantifier": [{"kind": "quantifier", "quantifier": q, "population": pop, "predicate": pred}],
            "probability": [{"kind": "epistemic_probability", "value": prob}],
        },
        [("quantifier", "probability", "coexist")], group="quantifier_probability",
    )


# ---------------------------------------------------------------------------
# Subclass + permission: preserve both but no inherited permission conclusion.
# ---------------------------------------------------------------------------

_sp = [
    ("Release stewards are a subset of reviewers. Only reviewers may approve the packet.", "release stewards", "reviewers", "reviewers", "approve the packet"),
    ("Lab auditors are a subclass of inspectors. Only inspectors may release batch a.", "lab auditors", "inspectors", "inspectors", "release batch a"),
    ("Release officers are a type of reviewers. Only reviewers may sign the certificate.", "release officers", "reviewers", "reviewers", "sign the certificate"),
    ("Auditors are a kind of inspectors. Permission to approve the dossier is limited to inspectors.", "auditors", "inspectors", "inspectors", "approve the dossier"),
    ("Release stewards sit within the reviewer class. Only reviewers may approve the packet.", "release stewards", "reviewer class", "reviewers", "approve the packet"),
    ("Lab auditors fall under inspectors. Only inspectors may release batch a.", "lab auditors", "inspectors", "inspectors", "release batch a"),
    # Novel subclass paraphrases.
    ("Release officers are nested beneath reviewers. Only reviewers may sign the certificate.", "release officers", "reviewers", "reviewers", "sign the certificate"),
    ("Auditors belong to a narrower class than inspectors. Only inspectors may approve the dossier.", "auditors", "inspectors", "inspectors", "approve the dossier"),
]
for i, (text, child, parent, pop, pred) in enumerate(_sp, 1):
    add(
        f"RC7D-SP-{i:02d}", text,
        {
            "subclass": [{"kind": "subclass", "child": child, "parent": parent}],
            "permission": [{"kind": "necessary_permission_condition", "population": pop, "predicate": pred}],
        },
        [("subclass", "permission", "coexist")], group="subclass_permission",
    )


# ---------------------------------------------------------------------------
# Quantitative + event content. Both dimensions are informative.
# ---------------------------------------------------------------------------

_qr = [
    ("Exactly four auditors signed the release.", "exact_count", "exactly four", "sign", "auditors", "the release"),
    ("70% of the technicians inspected the vessel.", "percentage", "70%", "inspect", "the technicians", "the vessel"),
    ("Seventy percent of the reviewers approved the packet.", "percentage", "seventy percent", "approve", "the reviewers", "the packet"),
    ("At least 3 inspectors approved the record.", "minimum_count", "at least 3", "approve", "inspectors", "the record"),
    ("A majority of lab analysts inspected the sample.", "majority", "a majority of", "inspect", "lab analysts", "the sample"),
    ("Most release stewards reviewed the dossier.", "most", "most r", "review", "release stewards", "the dossier"),
    ("Roughly three quarters of the auditors signed the release.", "proportion", "roughly three quarters", "sign", "the auditors", "the release"),
    ("A small minority of inspectors approved the record.", "minority", "a small minority", "approve", "inspectors", "the record"),
]
for i, (text, qkind, surface, pred, subj, obj) in enumerate(_qr, 1):
    add(
        f"RC7D-QR-{i:02d}", text,
        {
            "quantitative": [{"kind": "quantitative_scope", "quantitative_kind": qkind, "surface": surface}],
            "role_binding": [{"kind": "event", "predicate": pred, "subject": subj, "object": obj, "polarity": "positive"}],
        },
        [("quantitative", "role_binding", "coexist")], group="quantitative_role",
    )


# ---------------------------------------------------------------------------
# Irrelevant prose controls: semantic facts must survive without deleting prose.
# ---------------------------------------------------------------------------

_irrelevant = [
    ("The room was quiet. Dana reviewed the dossier.", {"role_binding": [{"kind": "event", "predicate": "review", "subject": "dana", "object": "the dossier", "polarity": "positive"}]}),
    ("The dashboard uses a blue header. Only inspectors may release batch a.", {"permission": [{"kind": "necessary_permission_condition", "population": "inspectors", "predicate": "release batch a"}]}),
    ("A note in the margin says draft. Every technician inspected the vessel.", {"quantifier": [{"kind": "quantifier", "quantifier": "every", "population": "technician", "predicate": "inspect vessel"}]}),
    ("The archive folder is labelled old. Mira approved the packet.", {"role_binding": [{"kind": "event", "predicate": "approve", "subject": "mira", "object": "the packet", "polarity": "positive"}]}),
    ("The document contains three headings. Release stewards are a subset of reviewers.", {"subclass": [{"kind": "subclass", "child": "release stewards", "parent": "reviewers"}]}),
    ("The sentence is quoted in an appendix. Nia was authorized to sign the certificate.", {"permission": [{"kind": "explicit_permission", "entity": "nia", "predicate": "sign the certificate", "value": "permitted"}]}),
]
for i, (text, gold) in enumerate(_irrelevant, 1):
    add(f"RC7D-IR-{i:02d}", text, gold, group="irrelevant_prose")


# ---------------------------------------------------------------------------
# No-authority / ambiguity controls. Preserve source and residue; do not invent.
# ---------------------------------------------------------------------------

_none = [
    "The word exception appears in the glossary.",
    "Permission is the name of a database column.",
    "Temporal is a label used in the export format.",
    "The subclass field is currently blank.",
    "The probability notebook is stored on shelf two.",
    "Quantitative is a section heading in the report.",
    "Jordan may review the packet.",  # modal ambiguity; no authoritative reading in this apparatus
    "Mira is associated with the inspectors.",
]
for i, text in enumerate(_none, 1):
    add(f"RC7D-NA-{i:02d}", text, {}, group="no_authority")


# ---------------------------------------------------------------------------
# Conflict / composition controls.
# ---------------------------------------------------------------------------

_conflict = [
    ("Every technician inspected the vessel. No technician inspected the vessel.", {"quantifier": [
        {"kind": "quantifier", "quantifier": "every", "population": "technician", "predicate": "inspect vessel"},
        {"kind": "quantifier", "quantifier": "none", "population": "technician", "predicate": "inspect vessel"},
    ]}),
    ("Mira was authorized to sign the certificate. Mira was not authorized to sign the certificate.", {"permission": [
        {"kind": "explicit_permission", "entity": "mira", "predicate": "sign the certificate", "value": "permitted"},
        {"kind": "explicit_permission", "entity": "mira", "predicate": "sign the certificate", "value": "not_permitted"},
    ]}),
]
for i, (text, gold) in enumerate(_conflict, 1):
    add(f"RC7D-CF-{i:02d}", text, gold, group="internal_conflict", note="Both source assertions must be preserved; the architecture must not silently choose one.")


assert len(CASES) == 86, len(CASES)
