#!/usr/bin/env python3
"""Build and validate the independent 72-case NLI calibration/evaluation cohort."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

FAMILIES: dict[str, list[tuple[str, str, str, str, str]]] = {
    "quantifier_scope": [
        ("entailment","calibration","All archived batch records are indexed before off-site storage.","Every archived batch record is indexed before it is stored off site.","universal paraphrase"),
        ("entailment","calibration","Some supplier complaints involve damaged packaging.","At least one supplier complaint involves damaged packaging.","existential paraphrase"),
        ("entailment","evaluation","No controlled form may be issued without a document number.","Every controlled form must have a document number before it is issued.","negative universal paraphrase"),
        ("entailment","evaluation","Most quarterly reviews include a trend summary, and all reviews include an approval signature.","Every quarterly review includes an approval signature.","universal conjunct extraction"),
        ("neutral","calibration","Some field inspections include photographic evidence.","Every field inspection includes photographic evidence.","existential does not license universal"),
        ("neutral","calibration","Most training sessions include a practical exercise.","All training sessions include a practical exercise.","most does not license all"),
        ("neutral","evaluation","At least one warehouse audit found labeling errors.","Most warehouse audits found labeling errors.","existential does not license most"),
        ("neutral","evaluation","Every critical alarm is logged. The procedure says nothing about noncritical alarms.","Every alarm is logged.","subset universal does not license superset"),
        ("contradiction","calibration","Every approved vendor has a current quality agreement.","Some approved vendors do not have a current quality agreement.","universal vs existential counterexample"),
        ("contradiction","calibration","No temporary badge permits access to the archive room.","Some temporary badges permit access to the archive room.","negative universal contradiction"),
        ("contradiction","evaluation","All emergency exits remain unlocked while the facility is occupied.","At least one emergency exit is locked while the facility is occupied.","universal vs counterexample"),
        ("contradiction","evaluation","No rejected component may be returned to usable inventory.","Some rejected components may be returned to usable inventory.","negative universal contradiction"),
    ],
    "exceptions": [
        ("entailment","calibration","All external contractors must sign the site safety register, except emergency responders during an active incident.","A routine maintenance contractor must sign the site safety register.","ordinary member covered by universal"),
        ("entailment","calibration","Records are retained for seven years, except duplicate convenience copies, which may be destroyed earlier.","An original investigation record is subject to the seven-year retention rule.","non-exempt member inherits rule"),
        ("entailment","evaluation","All production rooms require line clearance before use, except the dedicated sampling booth.","A packaging room requires line clearance before use.","non-exempt location"),
        ("entailment","evaluation","Every software change requires documented review, except spelling-only corrections to help text.","A database schema change requires documented review.","non-exempt change"),
        ("neutral","calibration","All visitors require an escort, except government inspectors acting under statutory authority; their procedure is not specified here.","Government inspectors are never escorted.","exception does not specify opposite rule"),
        ("neutral","calibration","Every deviation requires investigation, except duplicate reports that are handled under a separate process.","Duplicate reports require no review of any kind.","separate process does not imply no review"),
        ("neutral","evaluation","All refrigerated shipments require temperature logging, except courier hand-carry packages, which follow another procedure.","Courier hand-carry packages are exempt from temperature control.","exception from this logging rule does not imply broader exemption"),
        ("neutral","evaluation","All staff complete annual privacy training, except newly hired staff during their first 30 days; later requirements are described elsewhere.","New hires never complete privacy training.","temporary exception does not imply permanent negation"),
        ("contradiction","calibration","All laboratory doors remain locked after hours, except the staffed security vestibule, which remains unlocked.","Every laboratory door is locked after hours.","explicit exception falsifies universal"),
        ("contradiction","calibration","Every supplier must submit an annual declaration, except suppliers classified as dormant, who are not required to submit one.","Dormant suppliers are required to submit the annual declaration.","explicit exempt class"),
        ("contradiction","evaluation","All final reports require two approvals, except expedited safety alerts, which require only one.","Every final report requires two approvals.","exception falsifies universal"),
        ("contradiction","evaluation","Every portable drive is prohibited in the secure zone, except an encrypted forensic drive issued by security, which is permitted.","No portable drive is permitted in the secure zone.","permitted exception falsifies negative universal"),
    ],
    "modality": [
        ("entailment","calibration","Operators must verify the equipment status before starting the run.","Operators are required to verify equipment status before starting the run.","must paraphrase"),
        ("entailment","calibration","A supervisor may authorize a second review when the first review is inconclusive.","A supervisor is permitted to authorize a second review when the first review is inconclusive.","may paraphrase"),
        ("entailment","evaluation","Teams should document lessons learned after major incidents.","Documenting lessons learned after major incidents is recommended for teams.","should paraphrase"),
        ("entailment","evaluation","Personnel must not share authentication tokens.","Sharing authentication tokens is prohibited for personnel.","must not paraphrase"),
        ("neutral","calibration","Managers may extend the response deadline after consulting compliance.","Managers must extend the response deadline after consulting compliance.","permission does not entail obligation"),
        ("neutral","calibration","Analysts should compare the current result with the historical trend.","Analysts are required to compare the current result with the historical trend.","recommendation does not entail requirement"),
        ("neutral","evaluation","The reviewer can request additional evidence if needed.","The reviewer must request additional evidence whenever evidence is incomplete.","ability does not establish obligation"),
        ("neutral","evaluation","The committee may postpone the vote.","The committee will postpone the vote.","permission does not establish actuality"),
        ("contradiction","calibration","Staff must not disable the audit trail.","Staff may disable the audit trail.","prohibition contradicts permission"),
        ("contradiction","calibration","The operator is required to stop the process when the red alarm appears.","The operator is permitted to continue the process when the red alarm appears.","required stop contradicts permitted continue"),
        ("contradiction","evaluation","Remote access is prohibited during system recovery.","Remote access is allowed during system recovery.","prohibited vs allowed"),
        ("contradiction","evaluation","The inspection team must enter through the controlled entrance.","The inspection team is not required to use the controlled entrance.","obligation vs explicit absence of obligation"),
    ],
    "entity_population_scope": [
        ("entailment","calibration","All pediatric specimens are stored in the locked freezer.","A pediatric specimen is stored in the locked freezer.","class member follows universal"),
        ("entailment","calibration","The North Warehouse is approved for ambient finished goods.","Ambient finished goods may be stored in the North Warehouse.","entity paraphrase"),
        ("entailment","evaluation","Vendor Orion is the approved provider for sterile gloves.","Sterile gloves may be sourced from Vendor Orion.","entity-role paraphrase"),
        ("entailment","evaluation","Every night-shift technician receives the overnight handover report.","A technician working the night shift receives the overnight handover report.","population membership"),
        ("neutral","calibration","All pediatric specimens are stored in the locked freezer. Adult specimens are not discussed.","All specimens are stored in the locked freezer.","subset does not license population generalization"),
        ("neutral","calibration","The East Plant uses electronic logbooks.","The West Plant uses electronic logbooks.","different entity, no relation given"),
        ("neutral","evaluation","Vendor Atlas is approved for glass vials.","Vendor Atlas is approved for rubber stoppers.","same entity, different product scope"),
        ("neutral","evaluation","Night-shift technicians receive the overnight handover report.","Day-shift technicians receive the overnight handover report.","different population"),
        ("contradiction","calibration","Only the Central Laboratory is authorized to release sterility results; the Satellite Laboratory is not authorized to do so.","The Satellite Laboratory is authorized to release sterility results.","explicit entity contradiction"),
        ("contradiction","calibration","Product Helios is licensed for adult patients only and is not licensed for pediatric patients.","Product Helios is licensed for pediatric patients.","explicit population contradiction"),
        ("contradiction","evaluation","The red-tagged containers are designated for destruction and may not be used for production.","The red-tagged containers may be used for production.","entity subset explicit prohibition"),
        ("contradiction","evaluation","Facility C is outside the scope of the certification and is not certified.","Facility C is certified.","explicit entity status contradiction"),
    ],
    "temporal_qualifiers": [
        ("entailment","calibration","The backup generator is tested every Monday morning.","The backup generator is tested on Monday mornings.","recurring time paraphrase"),
        ("entailment","calibration","The revised procedure became effective on 1 March and applies thereafter.","The revised procedure applies after 1 March.","effective date entailment"),
        ("entailment","evaluation","Access badges are disabled while an employee is on leave.","An employee's access badge is disabled during the employee's leave.","interval paraphrase"),
        ("entailment","evaluation","The inspection occurs before the production line restarts.","The production line restarts after the inspection.","before/after inverse relation"),
        ("neutral","calibration","The archive is inspected during the first week of each quarter.","The archive is inspected on the first day of each quarter.","week does not specify day"),
        ("neutral","calibration","The revised procedure applies after 1 March.","The revised procedure applied in February.","future applicability says nothing about prior state"),
        ("neutral","evaluation","The report is reviewed before year end.","The report is reviewed in November.","before year end does not specify month"),
        ("neutral","evaluation","The calibration remains valid until the maintenance event.","The calibration remains valid after the maintenance event.","until event does not state post-event state"),
        ("contradiction","calibration","The shipment arrived before the temperature excursion began.","The shipment arrived after the temperature excursion began.","before vs after"),
        ("contradiction","calibration","The legacy procedure ceased to apply on 30 June.","The legacy procedure remained applicable after 30 June.","cessation contradicts continued applicability"),
        ("contradiction","evaluation","The lockout remains in force until the investigation closes, and it is lifted when the investigation closes.","The lockout remains in force after the investigation closes.","explicit post-event contradiction"),
        ("contradiction","evaluation","The audit started after the system upgrade was completed.","The audit started before the system upgrade was completed.","after vs before"),
    ],
    "conditional_causal": [
        ("entailment","calibration","If the seal is broken, the package is quarantined. The seal on package A is broken.","Package A is quarantined.","modus ponens"),
        ("entailment","calibration","The investigation concluded that a failed cooling fan caused the server shutdown.","The failed cooling fan caused the server shutdown.","explicit causal statement"),
        ("entailment","evaluation","If a complaint alleges patient harm, medical review is required. Complaint Q alleges patient harm.","Complaint Q requires medical review.","modus ponens"),
        ("entailment","evaluation","The report states that water ingress caused the sensor failure.","Water ingress caused the sensor failure.","explicit causal statement"),
        ("neutral","calibration","If the seal is broken, the package is quarantined. The condition of package B's seal is unknown.","Package B is quarantined.","conditional without antecedent"),
        ("neutral","calibration","A pressure drop occurred shortly before the alarm, but the investigation did not determine the cause.","The pressure drop caused the alarm.","temporal association without causal finding"),
        ("neutral","evaluation","If the customer requests expedited handling, the order is prioritized. No information is given about the customer's request.","The order is prioritized.","conditional antecedent unknown"),
        ("neutral","evaluation","Battery depletion and sensor failure occurred during the same shift. The causal relationship was not assessed.","Battery depletion caused the sensor failure.","co-occurrence does not establish cause"),
        ("contradiction","calibration","The investigation ruled out network latency as a cause of the failed transaction.","Network latency caused the failed transaction.","explicit causal exclusion"),
        ("contradiction","calibration","If the emergency stop is active, the motor cannot run. The emergency stop is active.","The motor is running.","conditional plus antecedent contradicts consequent negation"),
        ("contradiction","evaluation","The root-cause report states that operator action did not cause the outage.","Operator action caused the outage.","explicit causal negation"),
        ("contradiction","evaluation","If the access token is expired, login is denied. The token is expired.","Login is permitted.","conditional entails denial, contradicts permission"),
    ],
}

LABELS = {"entailment", "neutral", "contradiction"}
SPLITS = {"calibration", "evaluation"}


def build() -> dict[str, Any]:
    rows: list[dict[str, str]] = []
    for family, cases in FAMILIES.items():
        for target, split, premise, hypothesis, rationale in cases:
            rows.append(
                {
                    "case_id": f"IC2-{len(rows) + 1:03d}",
                    "family": family,
                    "target": target,
                    "split": split,
                    "premise": premise,
                    "hypothesis": hypothesis,
                    "rationale": rationale,
                }
            )
    return {
        "schema_version": "cal-independent-nli-calibration-cohort-v0.1",
        "n_cases": len(rows),
        "cases": rows,
    }


def validate(cohort: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    rows = cohort["cases"]
    if cohort["n_cases"] != 72 or len(rows) != 72:
        problems.append("cohort must contain exactly 72 cases")
    ids = [row["case_id"] for row in rows]
    if len(set(ids)) != 72:
        problems.append("case IDs must be unique")
    pairs = [(row["premise"], row["hypothesis"]) for row in rows]
    if len(set(pairs)) != 72:
        problems.append("premise/hypothesis pairs must be unique")
    if Counter(row["target"] for row in rows) != Counter(
        {"entailment": 24, "neutral": 24, "contradiction": 24}
    ):
        problems.append("overall target balance changed")
    if Counter(row["split"] for row in rows) != Counter(
        {"calibration": 36, "evaluation": 36}
    ):
        problems.append("split balance changed")
    for split in sorted(SPLITS):
        subset = [row for row in rows if row["split"] == split]
        if Counter(row["target"] for row in subset) != Counter(
            {"entailment": 12, "neutral": 12, "contradiction": 12}
        ):
            problems.append(f"{split}: label balance changed")
    if set(FAMILIES) != {row["family"] for row in rows}:
        problems.append("family set changed")
    for family in sorted(FAMILIES):
        subset = [row for row in rows if row["family"] == family]
        if len(subset) != 12:
            problems.append(f"{family}: expected 12 cases")
        if Counter(row["target"] for row in subset) != Counter(
            {"entailment": 4, "neutral": 4, "contradiction": 4}
        ):
            problems.append(f"{family}: target balance changed")
        if Counter(row["split"] for row in subset) != Counter(
            {"calibration": 6, "evaluation": 6}
        ):
            problems.append(f"{family}: split balance changed")
    for row in rows:
        if row["target"] not in LABELS or row["split"] not in SPLITS:
            problems.append(f"{row['case_id']}: invalid label/split")
        if not all(row[key].strip() for key in ("premise", "hypothesis", "rationale")):
            problems.append(f"{row['case_id']}: blank semantic field")
    return problems


def canonical_bytes(cohort: dict[str, Any]) -> bytes:
    return (json.dumps(cohort, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cohort = build()
    problems = validate(cohort)
    if problems:
        raise SystemExit("\n".join(problems))
    raw = canonical_bytes(cohort)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(raw)
    print("cases=72")
    print("sha256=" + hashlib.sha256(raw).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
