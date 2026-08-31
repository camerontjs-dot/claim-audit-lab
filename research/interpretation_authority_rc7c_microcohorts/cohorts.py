from __future__ import annotations

JURISDICTION_CASES = []


def _j(case_id, text, expected, category, family=None):
    JURISDICTION_CASES.append({
        "case_id": case_id,
        "text": text,
        "expected": expected,
        "category": category,
        "family": family,
    })


for i, text in enumerate([
    "If the technicians inspect the vessel, release stewards may approve the packet.",
    "Provided that the auditors sign the log, the archive may be unlocked.",
    "Assuming that the reviewers concur, Nia may sign the release.",
    "On condition that the lab analysts inspect the sample, the batch may proceed.",
    "Approval is contingent on the inspectors completing the review.",
    "Should the auditors finish the review, the release stewards may sign the certificate.",
], 1):
    _j(f"RC7C-J-COND-{i:02}", text, "out_of_jurisdiction", "conditional")

for i, text in enumerate([
    "Every technician except Nia inspected the vessel.",
    "With the exception of Hugo, all reviewers approved the packet.",
    "Inspectors other than Ada signed the release.",
    "The release stewards, excluding Rowan, approved the dossier.",
    "Unless Nia is absent, every auditor signs the certificate.",
    "Save for Hugo, all lab analysts reviewed the record.",
], 1):
    _j(f"RC7C-J-EXC-{i:02}", text, "out_of_jurisdiction", "exception")

for i, text in enumerate([
    "Nia was a release steward before the deadline.",
    "Hugo became a reviewer after the cutoff.",
    "Ada held inspector status prior to the deadline.",
    "Rowan was authorized following the cutoff.",
    "Nia remained an auditor until the deadline.",
    "As of 2026-08-31, Hugo was a release steward.",
], 1):
    _j(f"RC7C-J-TEMP-{i:02}", text, "out_of_jurisdiction", "temporal")

for i, text in enumerate([
    "Release stewards are a subclass of quality reviewers.",
    "Lab auditors are a subset of inspectors.",
    "Quality reviewers are a proper subset of release officers.",
    "A release steward is a kind of reviewer.",
    "Lab auditors are a type of inspector.",
    "The inspector class sits within the reviewer class.",
], 1):
    _j(f"RC7C-J-SUB-{i:02}", text, "out_of_jurisdiction", "subclass")

for i, text in enumerate([
    "70% of the technicians inspected the vessel.",
    "Seventy percent of the reviewers approved the packet.",
    "Exactly four auditors signed the release.",
    "Most release stewards reviewed the dossier.",
    "At least 3 inspectors approved the record.",
    "A majority of lab analysts inspected the sample.",
], 1):
    _j(f"RC7C-J-NUM-{i:02}", text, "out_of_jurisdiction", "quantitative")

for i, text in enumerate([
    "The technicians probably inspected the vessel.",
    "The reviewers are likely to approve the packet.",
    "There is a chance that Ada signed the release.",
    "The probability that the auditors reviewed the dossier is high.",
    "The inspectors are unlikely to approve the record.",
    "The odds favor the lab analysts inspecting the sample.",
], 1):
    _j(f"RC7C-J-PROB-{i:02}", text, "out_of_jurisdiction", "probabilistic")

for i, text in enumerate([
    "Only release stewards may sign the certificate. Every technician inspected the vessel.",
    "Permission to approve the packet is limited to quality reviewers. Some auditors signed the log.",
    "Only lab auditors may unlock the archive. Nia was reviewed by Hugo.",
    "Every release steward approved the dossier. Ada is authorized to sign the certificate.",
    "No inspectors approved the record. Rowan is permitted to unlock the archive.",
    "Some reviewers signed the release. The packet was approved by Nia.",
], 1):
    _j(f"RC7C-J-XFAM-{i:02}", text, "out_of_jurisdiction", "cross_family")

only_controls = [
    "Only release stewards may sign certificate. Nia belongs to the release stewards. Nia is authorized to sign certificate.",
    "Permission to approve packet is restricted to quality reviewers. Hugo is not a member of the quality reviewers. Hugo is not permitted to approve packet.",
    "Anyone permitted to unlock archive must belong to lab auditors. Ada belongs to the lab auditors. Whether Ada is permitted to unlock archive is unknown.",
    "To be permitted to sign release, someone must belong to release officers. Rowan's non-membership in the release officers is confirmed. Permission for Rowan to sign release is denied.",
    "Permission to approve dossier requires membership in certified reviewers. Nia's membership in certified reviewers is confirmed. Permission for Nia to approve dossier is granted.",
    "Only quality approvers may release batch b. It is unknown whether Hugo is a member of the quality approvers. Hugo has permission to release batch b.",
    "Permission to unlock vault is limited to archive custodians. Ada works beside archive custodians.",
    "Only release officers may sign certificate. Rowan belongs to the release officers.",
    "Permission to approve packet requires membership in quality reviewers. The record leaves Nia's permission to approve packet unknown.",
    "Only lab auditors may inspect sample. The record leaves Hugo's membership in lab auditors unknown.",
    "Anyone permitted to sign release must belong to certified reviewers. Ada is allowed to sign release.",
    "Permission to approve dossier is restricted to release stewards. Rowan does not belong to the release stewards.",
    "Only archive custodians may unlock vault. Nia is a member of archive custodians. Nia is not authorized to unlock vault.",
    "Permission to sign certificate is limited to quality approvers. Hugo belongs to quality approvers. Hugo is permitted to sign certificate.",
]
for i, text in enumerate(only_controls, 1):
    _j(f"RC7C-J-ID-OP-{i:02}", text, "supported", "supported_only_permission", "only_permission")

role_controls = [
    "Dana reviewed Lee submission.",
    "Lee submission was reviewed by Dana.",
    "Nia did not approve Hugo packet.",
    "Hugo packet was not approved by Nia.",
    "Ada signed Rowan certificate.",
    "Rowan certificate was signed by Ada.",
    "Nia inspected Hugo sample.",
    "Hugo sample was inspected by Nia.",
    "Ada did not audit Rowan record.",
    "Rowan record was not audited by Ada.",
    "Hugo reviewed Nia dossier.",
    "Nia dossier was reviewed by Hugo.",
    "Rowan approved Ada packet.",
    "Ada packet was approved by Rowan.",
]
for i, text in enumerate(role_controls, 1):
    _j(f"RC7C-J-ID-RL-{i:02}", text, "supported", "supported_role_binding", "role_binding")

quant_controls = [
    "Every technician inspected vessel.",
    "Each reviewer approved packet.",
    "All auditors signed release.",
    "No release steward reviewed dossier.",
    "None of the inspectors approved record.",
    "Not one lab analyst inspected sample.",
    "Some technicians inspected vessel.",
    "At least one reviewer approved packet.",
    "Not every auditor signed release.",
    "Not all release stewards reviewed dossier.",
    "Every aftercare reviewer approved packet.",
    "Some conditional auditors signed release.",
    "No probability reviewers inspected sample.",
    "Each subclass documentation reviewer approved record.",
]
for i, text in enumerate(quant_controls, 1):
    _j(f"RC7C-J-ID-QU-{i:02}", text, "supported", "supported_quantifier", "quantifier")


FIELD_INDEPENDENCE_PAIRS = []


def _pair(pair_id, family, kind, before_text, before_query, after_text, after_query, expected_changed_fields):
    FIELD_INDEPENDENCE_PAIRS.append({
        "pair_id": pair_id,
        "family": family,
        "kind": kind,
        "before_text": before_text,
        "before_query": before_query,
        "after_text": after_text,
        "after_query": after_query,
        "expected_changed_fields": list(expected_changed_fields),
    })


def _past(pred):
    if pred == "review":
        return "reviewed"
    if pred == "approve":
        return "approved"
    if pred == "sign":
        return "signed"
    if pred == "inspect":
        return "inspected"
    return pred + "ed"


role_specs = [
    ("Dana", "Lee submission", "review"),
    ("Nia", "Hugo packet", "approve"),
    ("Ada", "Rowan certificate", "sign"),
    ("Hugo", "Nia sample", "inspect"),
]
for idx, (subj, obj, pred) in enumerate(role_specs, 1):
    other_subj = obj.split()[0]
    other_obj = f"{subj} {' '.join(obj.split()[1:])}" if len(obj.split()) > 1 else subj
    bq = {"kind": "event", "predicate": pred, "roles": {"subject": subj.lower(), "object": obj.lower()}, "polarity": "positive"}
    aq = {"kind": "event", "predicate": pred, "roles": {"subject": other_subj.lower(), "object": other_obj.lower()}, "polarity": "positive"}
    _pair(
        f"RC7C-M-RL-SWAP-A-{idx:02}", "role_binding", "role_swap",
        f"{subj} {_past(pred)} {obj}.", bq,
        f"{other_subj} {_past(pred)} {other_obj}.", aq,
        ["subject", "object"],
    )
    _pair(
        f"RC7C-M-RL-SWAP-N-{idx:02}", "role_binding", "role_swap",
        f"{subj} did not {pred} {obj}.", {**bq, "polarity": "negative"},
        f"{other_subj} did not {pred} {other_obj}.", {**aq, "polarity": "negative"},
        ["subject", "object"],
    )

for idx, (subj, obj, pred) in enumerate(role_specs, 1):
    posq = {"kind": "event", "predicate": pred, "roles": {"subject": subj.lower(), "object": obj.lower()}, "polarity": "positive"}
    negq = {**posq, "polarity": "negative"}
    _pair(
        f"RC7C-M-RL-POL-{idx:02}", "role_binding", "polarity_flip",
        f"{subj} {_past(pred)} {obj}.", posq,
        f"{subj} did not {pred} {obj}.", negq,
        ["polarity"],
    )
    _pair(
        f"RC7C-M-RL-PARA-{idx:02}", "role_binding", "paraphrase_invariant",
        f"{subj} {_past(pred)} {obj}.", posq,
        f"{obj} was {_past(pred)} by {subj}.", posq,
        [],
    )

quant_specs = [
    ("technicians", "inspect vessel"),
    ("reviewers", "approve packet"),
    ("auditors", "sign release"),
    ("release stewards", "review dossier"),
    ("inspectors", "approve record"),
    ("lab analysts", "inspect sample"),
]
for idx, (pop, pred) in enumerate(quant_specs, 1):
    bq = {"kind": "quantified", "population": pop, "predicate": pred, "quantifier": "every"}
    aq = {"kind": "quantified", "population": pop, "predicate": pred, "quantifier": "some"}
    verb = pred.split()[0]
    rest = " ".join(pred.split()[1:])
    past = _past(verb)
    _pair(
        f"RC7C-M-QU-CHG-{idx:02}", "quantifier", "quantifier_change",
        f"Every {pop} {past} {rest}.", bq,
        f"Some {pop} {past} {rest}.", aq,
        ["quantifier"],
    )
    _pair(
        f"RC7C-M-QU-PARA-{idx:02}", "quantifier", "paraphrase_invariant",
        f"Every {pop} {past} {rest}.", bq,
        f"Each {pop} {past} {rest}.", bq,
        [],
    )


ONLY_PERMISSION_CASES = []
ONLY_PERMISSION_MUTATIONS = []


def _receipt_gold(entity, population, predicate, membership_status, membership_value, permission_status, permission_value):
    return {
        "entity": ("established", entity),
        "population": ("established", population),
        "membership": (membership_status, membership_value),
        "predicate": ("established", predicate),
        "only_population_may": ("established", True),
        "explicit_permission": (permission_status, permission_value),
    }


contexts = [
    ("nia", "release stewards", "sign certificate"),
    ("hugo", "quality reviewers", "approve packet"),
    ("ada", "lab auditors", "unlock archive"),
    ("rowan", "release officers", "sign release"),
]
condition_templates = [
    "Only {population} may {predicate}.",
    "Permission to {predicate} is restricted to {population}.",
    "Anyone permitted to {predicate} must belong to the {population}.",
    "To be permitted to {predicate}, someone must belong to the {population}.",
    "The {population} are a necessary class for permission to {predicate}.",
    "Permission to {predicate} requires membership in the {population}.",
]
member_templates = {
    "member": [
        "{Entity} is a member of the {population}.",
        "{Entity} belongs to the {population}.",
        "{Entity}'s membership in the {population} is confirmed.",
        "The record places {Entity} in the {population}.",
    ],
    "non_member": [
        "{Entity} is not a member of the {population}.",
        "{Entity} does not belong to the {population}.",
        "{Entity}'s non-membership in the {population} is confirmed.",
        "The record excludes {Entity} from the {population}.",
    ],
    "unknown": [
        "It is unknown whether {Entity} is a member of the {population}.",
        "Whether {Entity} belongs to the {population} is unknown.",
        "The record leaves {Entity}'s membership in the {population} unknown.",
    ],
}
permission_templates = {
    "permitted": [
        "{Entity} is authorized to {predicate}.",
        "{Entity} has permission to {predicate}.",
        "Permission for {Entity} to {predicate} is granted.",
        "The record explicitly allows {Entity} to {predicate}.",
    ],
    "not_permitted": [
        "{Entity} is not authorized to {predicate}.",
        "{Entity} does not have permission to {predicate}.",
        "Permission for {Entity} to {predicate} is denied.",
        "The record explicitly forbids {Entity} from {predicate}.",
    ],
    "unknown": [
        "Whether {Entity} is permitted to {predicate} is unknown.",
        "Permission for {Entity} to {predicate} is unknown.",
        "The record leaves {Entity}'s permission to {predicate} unknown.",
    ],
}
state_pairs = [
    ("member", "permitted"),
    ("member", "not_permitted"),
    ("member", "unknown"),
    ("non_member", "permitted"),
    ("non_member", "not_permitted"),
    ("non_member", "unknown"),
    ("unknown", "permitted"),
    ("unknown", "not_permitted"),
    ("unknown", "unknown"),
]
case_index = 0
for cidx, (entity, population, predicate) in enumerate(contexts):
    Entity = entity.capitalize()
    for sidx, (mstate, pstate) in enumerate(state_pairs):
        case_index += 1
        cond = condition_templates[(case_index - 1) % len(condition_templates)].format(population=population, predicate=predicate)
        mtempl = member_templates[mstate][(case_index + cidx) % len(member_templates[mstate])]
        ptempl = permission_templates[pstate][(case_index + sidx) % len(permission_templates[pstate])]
        mtext = mtempl.format(Entity=Entity, population=population, predicate=predicate)
        ptext = ptempl.format(Entity=Entity, population=population, predicate=predicate)
        text = f"{cond} {mtext} {ptext}"
        ms = "semantic_unknown" if mstate == "unknown" else "established"
        mv = "unknown" if mstate == "unknown" else mstate
        ps = "semantic_unknown" if pstate == "unknown" else "established"
        pv = "unknown" if pstate == "unknown" else pstate
        ONLY_PERMISSION_CASES.append({
            "case_id": f"RC7C-OP-{case_index:03}",
            "text": text,
            "query": {"kind": "permission", "entity": entity, "population": population, "predicate": predicate},
            "gold": _receipt_gold(entity, population, predicate, ms, mv, ps, pv),
            "kind": "fully_specified",
        })

for cidx, (entity, population, predicate) in enumerate(contexts):
    Entity = entity.capitalize()
    cond = condition_templates[cidx].format(population=population, predicate=predicate)
    membership = member_templates["member"][cidx % len(member_templates["member"])].format(Entity=Entity, population=population, predicate=predicate)
    permission = permission_templates["permitted"][cidx % len(permission_templates["permitted"])].format(Entity=Entity, population=population, predicate=predicate)
    base = {"kind": "permission", "entity": entity, "population": population, "predicate": predicate}
    for suffix, text, missing in [
        ("M", f"{cond} {permission}", "membership"),
        ("P", f"{cond} {membership}", "explicit_permission"),
        ("MP", cond + f" {Entity} works beside the {population}.", "both"),
    ]:
        gold = _receipt_gold(entity, population, predicate, "established", "member", "established", "permitted")
        if missing in {"membership", "both"}:
            gold["membership"] = ("insufficient_authority", None)
        if missing in {"explicit_permission", "both"}:
            gold["explicit_permission"] = ("insufficient_authority", None)
        ONLY_PERMISSION_CASES.append({
            "case_id": f"RC7C-OP-I-{cidx+1:02}-{suffix}",
            "text": text,
            "query": base,
            "gold": gold,
            "kind": "insufficient_control",
        })

for idx, (entity, population, predicate) in enumerate(contexts, 1):
    Entity = entity.capitalize()
    cond = condition_templates[(idx + 1) % len(condition_templates)].format(population=population, predicate=predicate)
    member = member_templates["member"][idx % len(member_templates["member"])].format(Entity=Entity, population=population, predicate=predicate)
    nonmember = member_templates["non_member"][idx % len(member_templates["non_member"])].format(Entity=Entity, population=population, predicate=predicate)
    grant = permission_templates["permitted"][idx % len(permission_templates["permitted"])].format(Entity=Entity, population=population, predicate=predicate)
    denial = permission_templates["not_permitted"][idx % len(permission_templates["not_permitted"])].format(Entity=Entity, population=population, predicate=predicate)
    query = {"kind": "permission", "entity": entity, "population": population, "predicate": predicate}
    ONLY_PERMISSION_MUTATIONS.append({
        "mutation_id": f"RC7C-OP-MEM-{idx:02}",
        "before_text": f"{cond} {member} {grant}",
        "after_text": f"{cond} {nonmember} {grant}",
        "query": query,
        "expected_changed_fields": ["membership"],
    })
    ONLY_PERMISSION_MUTATIONS.append({
        "mutation_id": f"RC7C-OP-PERM-{idx:02}",
        "before_text": f"{cond} {member} {grant}",
        "after_text": f"{cond} {member} {denial}",
        "query": query,
        "expected_changed_fields": ["explicit_permission"],
    })
