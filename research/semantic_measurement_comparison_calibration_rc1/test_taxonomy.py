from research.semantic_measurement_comparison_calibration_rc1.taxonomy import compare_receipts


def rec(status="CLAIMED", atoms=None):
    return {"status": status, "atoms": atoms or []}


def test_exact_agreement_is_not_authority():
    atom = {"kind": "epistemic_probability", "value": "likely"}
    out = compare_receipts(rec(atoms=[atom]), rec(atoms=[dict(atom)]))
    assert out["relation"] == "EXACT_AGREEMENT"
    assert out["winner"] is None


def test_semantic_equivalence_ignores_determiner_only():
    left = {"kind": "quantifier", "quantifier": "every", "population": "reviewers", "predicate": "inspect the vessel"}
    right = {"kind": "quantifier", "quantifier": "every", "population": "the reviewers", "predicate": "inspect vessel"}
    out = compare_receipts(rec(atoms=[left]), rec(atoms=[right]))
    assert out["relation"] == "SEMANTIC_EQUIVALENCE"


def test_scope_material_is_not_treated_as_slot_noise():
    left = {"kind": "quantifier", "quantifier": "every", "population": "reviewers", "predicate": "approve packet"}
    right = {"kind": "quantifier", "quantifier": "every", "population": "reviewers quite likely", "predicate": "approve packet"}
    out = compare_receipts(rec(atoms=[left]), rec(atoms=[right]))
    assert out["relation"] == "SCOPE_ATTACHMENT_DISAGREEMENT"


def test_operator_value_disagreement():
    left = {"kind": "quantifier", "quantifier": "every", "population": "reviewers", "predicate": "approve packet"}
    right = {"kind": "quantifier", "quantifier": "some", "population": "reviewers", "predicate": "approve packet"}
    out = compare_receipts(rec(atoms=[left]), rec(atoms=[right]))
    assert out["relation"] == "OPERATOR_VALUE_DISAGREEMENT"


def test_jurisdiction_disagreement_preserves_both_states():
    atom = {"kind": "exception", "excluded": "nia"}
    out = compare_receipts(rec(atoms=[atom]), rec(status="NOT_APPLICABLE"))
    assert out["relation"] == "JURISDICTION_DISAGREEMENT"
    assert out["left_status"] == "CLAIMED"
    assert out["right_status"] == "NOT_APPLICABLE"
    assert out["winner"] is None


def test_both_inactive_not_compared():
    assert compare_receipts(rec(status="NOT_APPLICABLE"), rec(status="UNRESOLVED")) is None
