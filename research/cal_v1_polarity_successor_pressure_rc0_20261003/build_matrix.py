"""Emit the frozen synthetic and authority matrix. Does not import or call CAL."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

HIGHER = "Alpha had a higher rate than Beta."
LOWER = "Alpha had a lower rate than Beta."
BEFORE = "Ada reviewed Batch before Bea signed Record."
EVIDENCE_HIGHER = "Alpha had a higher rate than Beta."
EVIDENCE_LOWER = "Alpha had a lower rate than Beta."
EVIDENCE_NEG = "Alpha did not have a higher rate than Beta."
EVIDENCE_BEFORE = "Ada reviewed Batch before Bea signed Record."


def semantic(case_id, family, claim, evidence, conclusion, match_class, critical, note, **extra):
    row = {
        "case_id": case_id,
        "domain": "semantic",
        "family": family,
        "claim": claim,
        "evidence": evidence,
        "expected_kind": "conclusion",
        "expected_conclusion": conclusion,
        "match_class": match_class,
        "critical_conclusions": critical,
        "note": note,
    }
    row.update(extra)
    return row


def refusal(case_id, family, claim, note):
    return {
        "case_id": case_id,
        "domain": "semantic",
        "family": family,
        "claim": claim,
        "evidence": [],
        "expected_kind": "authoring_refusal",
        "expected_conclusion": None,
        "match_class": "PASS",
        "critical_conclusions": ["supported", "contradicted"],
        "note": note,
    }


CASES = [
    semantic("SC-SUPPORT", "strict_comparison", HIGHER, [EVIDENCE_HIGHER], "supported", "PASS", ["contradicted", "not_checkable"], "Same-direction positive comparison."),
    semantic("SC-REFUTE", "strict_comparison", HIGHER, [EVIDENCE_LOWER], "contradicted", "PASS", ["supported"], "Opposite positive direction refutes."),
    semantic("SC-ENTITY-SWAP", "strict_comparison", HIGHER, ["Beta had a lower rate than Alpha."], "supported", "PASS", ["contradicted", "not_checkable"], "Entity swap plus direction inversion preserves the comparison."),
    semantic("SC-DID-NOT", "strict_comparison", HIGHER, [EVIDENCE_NEG], "contradicted", "PASS", ["supported"], "One adjacent did-not refutes the same orientation. This is the #188 sentence."),
    semantic("SC-NOT-HIGHER-VS-LOWER", "strict_comparison", LOWER, [EVIDENCE_NEG], "not_checkable", "PASS", ["supported", "contradicted"], "not higher is not lower. Equality remains possible."),
    semantic("SC-MIXED", "strict_comparison", HIGHER, [EVIDENCE_HIGHER, EVIDENCE_LOWER], "not_checkable", "PASS", ["supported", "contradicted"], "Support and refute together do not yield a direction."),
    semantic("SC-IRRELEVANT", "strict_comparison", HIGHER, ["Gamma had a higher rate than Delta."], "not_checkable", "PASS", ["supported", "contradicted"], "Unrelated entities are not a decision."),
    refusal("SC-EQUALITY", "strict_comparison", "Alpha had the same rate as Beta.", "Equality is outside the supported comparison grammar and must fail closed."),
    semantic("SC-MULTI-CUE", "strict_comparison", HIGHER, ["Alpha had a higher rate than Beta and a lower rate than Gamma."], "not_checkable", "PASS", ["supported", "contradicted"], "Multiple comparison cues must not collapse to one direction."),
    semantic("SC-QUALIFIER", "strict_comparison", HIGHER, ["Alpha had a higher rate than Beta among adults in 2024."], "not_checkable", "PASS", ["supported", "contradicted"], "A population and time scope must not confirm the bare comparison."),
    semantic("SC-ORDER-A", "strict_comparison", HIGHER, [EVIDENCE_HIGHER, "Alpha exceeded Beta."], "supported", "PASS", ["contradicted"], "First evidence order. Paired with SC-ORDER-B. A shared not_checkable result is a robustness limit. A difference is nondeterminism.", not_checkable_class="ROBUSTNESS_LIMIT"),
    semantic("SC-ORDER-B", "strict_comparison", HIGHER, ["Alpha exceeded Beta.", EVIDENCE_HIGHER], "supported", "PASS", ["contradicted"], "Permuted evidence order. A conclusion difference from SC-ORDER-A is nondeterminism.", not_checkable_class="ROBUSTNESS_LIMIT"),
    semantic("SC-DUPLICATE", "strict_comparison", HIGHER, [EVIDENCE_HIGHER, EVIDENCE_HIGHER], "supported", "PASS", ["contradicted", "not_checkable"], "Duplicate admitted support stays support."),
    semantic("SC-NEAR-DUP", "strict_comparison", HIGHER, [EVIDENCE_HIGHER, "Alpha had a higher rate than Beta"], "supported", "PASS", ["contradicted"], "Near-duplicate punctuation. not_checkable is a robustness limit, not a wrong direction.", not_checkable_class="ROBUSTNESS_LIMIT"),
    semantic("SC-SOURCE-SUBST", "strict_comparison", HIGHER, [EVIDENCE_HIGHER], "supported", "PASS", ["contradicted", "not_checkable"], "Same passage text under a different caller-supplied source hash.", source_sha256="sha256:" + "ab" * 32),
    semantic("SC-CASE", "strict_comparison", HIGHER, ["alpha had a higher rate than beta."], "not_checkable", "ROBUSTNESS_LIMIT", ["supported", "contradicted"], "Lowercase entities lose coverage and must not invent a direction."),
    semantic("SC-PUNCT", "strict_comparison", HIGHER, ["Alpha had a higher rate than Beta!"], "not_checkable", "ROBUSTNESS_LIMIT", ["supported", "contradicted"], "Exclamation is outside the measurement terminator and must stay safe."),
    semantic("SC-WS", "strict_comparison", HIGHER, ["Alpha  had a higher rate than Beta."], "supported", "PASS", ["contradicted", "not_checkable"], "Internal whitespace collapses and the comparison is unchanged."),
    semantic("SC-NEVER", "strict_comparison", HIGHER, ["Alpha never had a higher rate than Beta."], "not_checkable", "PASS", ["supported", "contradicted"], "never is an unsupported negation and must fail closed."),
    semantic("SC-DOUBLE-NEG", "strict_comparison", HIGHER, ["Alpha did not not have a higher rate than Beta."], "not_checkable", "PASS", ["supported", "contradicted"], "Double negation is not a supported positive."),
    semantic("SC-NOT-BARE", "strict_comparison", HIGHER, ["Alpha had a not higher rate than Beta."], "not_checkable", "PASS", ["supported", "contradicted"], "not outside one adjacent did-not frame fails closed."),
    semantic("SC-CANNOT", "strict_comparison", HIGHER, ["Alpha cannot have a higher rate than Beta."], "not_checkable", "PASS", ["supported", "contradicted"], "cannot is an unsupported negation."),
    semantic("EV-BEFORE", "direct_event_order", BEFORE, [EVIDENCE_BEFORE], "supported", "PASS", ["contradicted", "not_checkable"], "Same before-order."),
    semantic("EV-AFTER-INVERSION", "direct_event_order", BEFORE, ["Ada reviewed Batch after Bea signed Record."], "contradicted", "PASS", ["supported"], "BEFORE claim against AFTER evidence."),
    semantic("EV-SIDE-SWAP-PRESERVE", "direct_event_order", BEFORE, ["Bea signed Record after Ada reviewed Batch."], "supported", "PASS", ["contradicted", "not_checkable"], "Swapped sides with the temporal cue that preserves order."),
    semantic("EV-SIDE-SWAP-INVERT", "direct_event_order", BEFORE, ["Bea signed Record before Ada reviewed Batch."], "contradicted", "PASS", ["supported"], "Swapped sides that invert order."),
    semantic("EV-NEGATIVE", "direct_event_order", BEFORE, ["Ada did not review Batch before Bea signed Record."], "not_checkable", "PASS", ["supported", "contradicted"], "Negative-event form has no deciding semantics."),
    semantic("EV-MULTI-CUE", "direct_event_order", BEFORE, ["Ada reviewed Batch before Bea signed Record after Cara approved File."], "not_checkable", "PASS", ["supported", "contradicted"], "Two temporal cues must not yield a direction."),
    semantic("EV-UNRELATED", "direct_event_order", BEFORE, ["Cara approved File before Dan archived Log."], "not_checkable", "PASS", ["supported", "contradicted"], "Unrelated events are not a decision."),
    semantic("EV-MIXED", "direct_event_order", BEFORE, [EVIDENCE_BEFORE, "Ada reviewed Batch after Bea signed Record."], "not_checkable", "PASS", ["supported", "contradicted"], "Mixed before and after evidence."),
    semantic("EV-SOURCE-SUBST", "direct_event_order", BEFORE, [EVIDENCE_BEFORE], "supported", "PASS", ["contradicted", "not_checkable"], "Same event text under a substituted source hash.", source_sha256="sha256:" + "cd" * 32),
    semantic("EV-PUNCT", "direct_event_order", BEFORE, ["Ada reviewed Batch, before Bea signed Record."], "not_checkable", "ROBUSTNESS_LIMIT", ["supported", "contradicted"], "Comma punctuation is outside the direct event grammar."),
    semantic("EV-CASE", "direct_event_order", BEFORE, ["ada reviewed batch before bea signed record."], "not_checkable", "ROBUSTNESS_LIMIT", ["supported", "contradicted"], "Lowercase event prose loses coverage."),
    semantic("EV-COMPLEX", "direct_event_order", BEFORE, ["On Monday, after the inspection window closed, Ada reviewed Batch before Bea signed Record in the archive room."], "not_checkable", "ROBUSTNESS_LIMIT", ["supported", "contradicted"], "Naturally more complex prose with an extra temporal cue and a scene."),
    refusal("SC-SCOPED-CLAIM", "strict_comparison", "Alpha had a higher rate than Beta among adults in 2024.", "A qualifier-bearing comparison is not representable by lhs, rhs, and direction. Refusal is an authoring limit of the real surface. The weak collapse must still extract a bare comparison."),
]

AUTHORITY = [
    {"case_id": "AUTH-PASSAGE-HASH", "expected": "explicit_rejection", "match_class": "PASS", "note": "A mutated passage hash must be rejected before a decision."},
    {"case_id": "AUTH-SOURCE-HASH-UNBOUND", "expected": "decision_without_rejection", "match_class": "INTERFACE_GAP", "note": "A well-formed substituted source hash is not bound to passage bytes. A decision here is a gap, not support."},
    {"case_id": "AUTH-CROSS-WORLD", "expected": "explicit_rejection", "match_class": "PASS", "note": "A relation from one evidence world must not compose in another."},
    {"case_id": "AUTH-STALE-CHILD", "expected": "explicit_rejection", "match_class": "PASS", "note": "A child text hash that does not match the declaration is stale."},
    {"case_id": "AUTH-MISSING-CHILD", "expected": "explicit_rejection", "match_class": "PASS", "note": "A missing declared child must fail."},
    {"case_id": "AUTH-EXTRA-CHILD", "expected": "explicit_rejection", "match_class": "PASS", "note": "An undeclared child result must fail."},
    {"case_id": "AUTH-REPLAY-RESULT-ID", "expected": "explicit_rejection", "match_class": "PASS", "note": "A copied child result id must fail verification."},
    {"case_id": "AUTH-CHILD-SEQUENCE", "expected": "explicit_rejection", "match_class": "PASS", "note": "A declaration whose child sequence is not 1..n must fail."},
    {"case_id": "AUTH-CHILD-SUPPLY-ORDER", "expected": "same_conclusion", "match_class": "PASS", "note": "Supply order of a commutative all_of does not change the conclusion. The declared sequence still binds."},
    {"case_id": "AUTH-MISSING-VERSION", "expected": "explicit_rejection", "match_class": "PASS", "note": "An empty Contract B version must fail."},
    {"case_id": "AUTH-EXTRA-APERTURE", "expected": "accepted_extra_state", "match_class": "INTERFACE_GAP", "note": "Unknown aperture keys are not a closed schema on the audit seam. Acceptance is a gap."},
    {"case_id": "AUTH-WRONG-CONTRACT-C", "expected": "explicit_rejection", "match_class": "PASS", "note": "A checkout that is not the pinned Contract C candidate must fail."},
    {"case_id": "AUTH-WRONG-RESOLVER", "expected": "explicit_rejection", "match_class": "PASS", "note": "A checkout that is not the pinned resolver must fail."},
    {"case_id": "AUTH-EXACT-AUTHORITY", "expected": "accepted", "match_class": "PASS", "note": "The pinned Contract C, RC2, and resolver checkouts must verify. Unavailable checkouts block only this control."},
    {"case_id": "AUTH-SEMANTIC-MISMATCH", "expected": "explicit_rejection", "match_class": "PASS", "note": "A candidate module whose semantic identity is not caa0048f must fail before emission."},
]

OPERATIONAL = [
    {"case_id": "OPS-DET-ROOTS", "expected": "byte_identical_distinct_roots", "match_class": "PASS"},
    {"case_id": "OPS-OVERWRITE", "expected": "explicit_rejection", "match_class": "PASS"},
    {"case_id": "OPS-NONDIR", "expected": "explicit_rejection", "match_class": "PASS"},
    {"case_id": "OPS-SYMLINK", "expected": "explicit_rejection", "match_class": "PASS"},
    {"case_id": "OPS-CONCURRENT", "expected": "distinct_outputs_succeed", "match_class": "PASS"},
    {"case_id": "OPS-COLLISION", "expected": "both_callers_reject_nonempty", "match_class": "PASS", "note": "Two callers on one pre-filled output directory must both be refused. Acceptance is a critical overwrite."},
    {"case_id": "OPS-EMPTY-RACE", "expected": "both_accept_is_interface_gap", "match_class": "INTERFACE_GAP", "note": "Two callers on one empty directory. The destination helper does not take a lock. Both accepting is an interface gap. Both rejecting is a stronger PASS."},
    {"case_id": "OPS-LOCALE", "expected": "identical_across_locale_tz_hashseed", "match_class": "PASS"},
    {"case_id": "OPS-WHEEL", "expected": "same_polarity_conclusion_as_source", "match_class": "PASS"},
    {"case_id": "OPS-SDIST", "expected": "same_polarity_conclusion_as_source", "match_class": "PASS"},
]

WEAK = [
    {"case_id": "WEAK-IGNORE-POLARITY", "gate": "SC-DID-NOT is contradicted", "weak_expected": "supported", "real_expected": "contradicted"},
    {"case_id": "WEAK-COLLAPSE-SCOPE", "gate": "scoped comparison is not authored as bare lhs/rhs/direction", "weak_expected": "bare_fields", "real_expected": "authoring_refusal"},
    {"case_id": "WEAK-STRUCTURAL-ONLY", "gate": "direction-mutated target fails exact conformance", "weak_expected": "accepted", "real_expected": "rejected"},
    {"case_id": "WEAK-RESOLVER-WILDCARD", "gate": "wrong semantic identity is rejected", "weak_expected": "accepted", "real_expected": "rejected"},
]

payload = {
    "schema": "cal-v1-polarity-successor-pressure-matrix-rc0",
    "frozen_before_cal_execution": True,
    "subject_commit": "64b6c7702696c851057c1cf0b2c105b1c81db543",
    "cases": CASES,
    "authority": AUTHORITY,
    "operational": OPERATIONAL,
    "weak": WEAK,
    "counts": {
        "semantic": len(CASES),
        "authority": len(AUTHORITY),
        "operational": len(OPERATIONAL),
        "weak": len(WEAK),
    },
}
(ROOT / "MATRIX.json").write_text(json.dumps(payload, indent=2) + "\n")
print(payload["counts"])
