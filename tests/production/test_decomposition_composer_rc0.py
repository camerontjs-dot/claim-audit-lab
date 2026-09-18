from __future__ import annotations

from dataclasses import replace

import pytest

from claim_audit_lab.production_v1.semantic.decomposition import (
    BoundAuditOutcome,
    DecompositionDeclaration,
    DecompositionRefusal,
    DecompositionState,
    PropositionRef,
    recompose,
    verify_decomposition_receipt,
)
from claim_audit_lab.production_v1.semantic.models import Conclusion

ROOT_HASH = "sha256:" + "1" * 64
A_HASH = "sha256:" + "2" * 64
B_HASH = "sha256:" + "3" * 64
C_HASH = "sha256:" + "4" * 64


def _audit_hash(seed: str) -> str:
    return "sha256:" + seed * 64


def _outcome(
    proposition_id: str,
    text_sha256: str,
    conclusion: Conclusion,
    seed: str,
) -> BoundAuditOutcome:
    return BoundAuditOutcome.create(
        proposition_id=proposition_id,
        text_sha256=text_sha256,
        audit_result_sha256=_audit_hash(seed),
        conclusion=conclusion,
    )


def _root_decl(state: DecompositionState) -> DecompositionDeclaration:
    return DecompositionDeclaration(
        root=PropositionRef("root", ROOT_HASH),
        state=state,
    )


def _allof(
    *,
    decomposition_id: str = "decomp-1",
    children: tuple[PropositionRef, ...] | None = None,
) -> DecompositionDeclaration:
    return DecompositionDeclaration(
        root=PropositionRef("root", ROOT_HASH),
        state=DecompositionState.DECLARED,
        decomposition_id=decomposition_id,
        operator="all_of",
        children=children
        or (
            PropositionRef("child-a", A_HASH, 1),
            PropositionRef("child-b", B_HASH, 2),
        ),
    )


@pytest.mark.parametrize(
    ("state", "conclusion"),
    [
        (DecompositionState.NOT_DECOMPOSED, Conclusion.SUPPORTED),
        (DecompositionState.FAILED, Conclusion.CONTRADICTED),
        (DecompositionState.UNKNOWN, Conclusion.NOT_CHECKABLE),
    ],
)
def test_root_only_preserves_exact_root_outcome(
    state: DecompositionState,
    conclusion: Conclusion,
) -> None:
    declaration = _root_decl(state)
    outcome = _outcome("root", ROOT_HASH, conclusion, "a")
    result = recompose(declaration, root_outcome=outcome)
    assert result.conclusion is conclusion
    assert result.receipt.operator == "single"
    assert result.receipt.decomposition_state is state
    assert result.receipt.root_result_id == outcome.result_id
    assert result.receipt.ordered_child_bindings == ()


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (Conclusion.SUPPORTED, Conclusion.SUPPORTED, Conclusion.SUPPORTED),
        (Conclusion.SUPPORTED, Conclusion.CONTRADICTED, Conclusion.CONTRADICTED),
        (Conclusion.CONTRADICTED, Conclusion.NOT_CHECKABLE, Conclusion.CONTRADICTED),
        (Conclusion.SUPPORTED, Conclusion.NOT_CHECKABLE, Conclusion.NOT_CHECKABLE),
        (Conclusion.NOT_CHECKABLE, Conclusion.NOT_CHECKABLE, Conclusion.NOT_CHECKABLE),
    ],
)
def test_allof_truth_function(
    left: Conclusion,
    right: Conclusion,
    expected: Conclusion,
) -> None:
    result = recompose(
        _allof(),
        child_outcomes=(
            _outcome("child-a", A_HASH, left, "a"),
            _outcome("child-b", B_HASH, right, "b"),
        ),
    )
    assert result.conclusion is expected


def test_three_child_all_supported() -> None:
    declaration = _allof(
        children=(
            PropositionRef("child-a", A_HASH, 1),
            PropositionRef("child-b", B_HASH, 2),
            PropositionRef("child-c", C_HASH, 3),
        )
    )
    result = recompose(
        declaration,
        child_outcomes=(
            _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a"),
            _outcome("child-b", B_HASH, Conclusion.SUPPORTED, "b"),
            _outcome("child-c", C_HASH, Conclusion.SUPPORTED, "c"),
        ),
    )
    assert result.conclusion is Conclusion.SUPPORTED


def test_three_child_contradiction_is_terminal() -> None:
    declaration = _allof(
        children=(
            PropositionRef("child-a", A_HASH, 1),
            PropositionRef("child-b", B_HASH, 2),
            PropositionRef("child-c", C_HASH, 3),
        )
    )
    result = recompose(
        declaration,
        child_outcomes=(
            _outcome("child-a", A_HASH, Conclusion.NOT_CHECKABLE, "a"),
            _outcome("child-b", B_HASH, Conclusion.CONTRADICTED, "b"),
            _outcome("child-c", C_HASH, Conclusion.SUPPORTED, "c"),
        ),
    )
    assert result.conclusion is Conclusion.CONTRADICTED


def test_three_child_unresolved_without_contradiction_is_not_checkable() -> None:
    declaration = _allof(
        children=(
            PropositionRef("child-a", A_HASH, 1),
            PropositionRef("child-b", B_HASH, 2),
            PropositionRef("child-c", C_HASH, 3),
        )
    )
    result = recompose(
        declaration,
        child_outcomes=(
            _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a"),
            _outcome("child-b", B_HASH, Conclusion.NOT_CHECKABLE, "b"),
            _outcome("child-c", C_HASH, Conclusion.SUPPORTED, "c"),
        ),
    )
    assert result.conclusion is Conclusion.NOT_CHECKABLE


def test_supplied_child_call_order_does_not_change_result_or_receipt() -> None:
    declaration = _allof()
    first = _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a")
    second = _outcome("child-b", B_HASH, Conclusion.CONTRADICTED, "b")
    forward = recompose(declaration, child_outcomes=(first, second))
    reversed_result = recompose(declaration, child_outcomes=(second, first))
    assert forward == reversed_result


def test_declaration_sequence_change_changes_receipt_identity_not_logic() -> None:
    first = _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a")
    second = _outcome("child-b", B_HASH, Conclusion.SUPPORTED, "b")
    forward = recompose(_allof(), child_outcomes=(first, second))
    reversed_declaration = _allof(
        children=(
            PropositionRef("child-b", B_HASH, 1),
            PropositionRef("child-a", A_HASH, 2),
        )
    )
    reversed_result = recompose(reversed_declaration, child_outcomes=(first, second))
    assert forward.conclusion is reversed_result.conclusion is Conclusion.SUPPORTED
    assert forward.receipt.receipt_id != reversed_result.receipt.receipt_id


@pytest.mark.parametrize(
    ("declaration", "children", "root", "code"),
    [
        (
            _allof(),
            (_outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a"),),
            None,
            "MISSING_CHILD_RESULT",
        ),
        (
            _allof(),
            (
                _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a"),
                _outcome("child-b", B_HASH, Conclusion.SUPPORTED, "b"),
                _outcome("child-c", C_HASH, Conclusion.SUPPORTED, "c"),
            ),
            None,
            "EXTRA_CHILD_RESULT",
        ),
        (
            _allof(),
            (
                _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a"),
                _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "b"),
            ),
            None,
            "DUPLICATE_CHILD_RESULT",
        ),
        (
            _allof(),
            (
                _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a"),
                _outcome("child-b", C_HASH, Conclusion.SUPPORTED, "b"),
            ),
            None,
            "CHILD_TEXT_BINDING_MISMATCH",
        ),
        (
            _allof(),
            (
                _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a"),
                _outcome("child-b", B_HASH, Conclusion.SUPPORTED, "b"),
            ),
            _outcome("root", ROOT_HASH, Conclusion.SUPPORTED, "c"),
            "DECLARED_ALLOF_HAS_ROOT_RESULT",
        ),
        (
            _root_decl(DecompositionState.NOT_DECOMPOSED),
            (_outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a"),),
            _outcome("root", ROOT_HASH, Conclusion.SUPPORTED, "b"),
            "ROOT_ONLY_HAS_CHILD_RESULTS",
        ),
    ],
)
def test_structural_defects_refuse_instead_of_abstaining(
    declaration: DecompositionDeclaration,
    children: tuple[BoundAuditOutcome, ...],
    root: BoundAuditOutcome | None,
    code: str,
) -> None:
    with pytest.raises(DecompositionRefusal, match=code):
        recompose(declaration, child_outcomes=children, root_outcome=root)


def test_root_binding_mismatch_refuses() -> None:
    with pytest.raises(DecompositionRefusal, match="ROOT_RESULT_BINDING_MISMATCH"):
        recompose(
            _root_decl(DecompositionState.UNKNOWN),
            root_outcome=_outcome("other-root", ROOT_HASH, Conclusion.SUPPORTED, "a"),
        )


def test_wrong_operator_refuses() -> None:
    declaration = replace(_allof(), operator="any_of")
    with pytest.raises(DecompositionRefusal, match="UNSUPPORTED_DECOMPOSITION_OPERATOR"):
        recompose(declaration, child_outcomes=())


def test_noncontiguous_sequence_refuses() -> None:
    declaration = _allof(
        children=(
            PropositionRef("child-a", A_HASH, 1),
            PropositionRef("child-b", B_HASH, 3),
        )
    )
    with pytest.raises(DecompositionRefusal, match="INVALID_CHILD_SEQUENCE"):
        recompose(declaration, child_outcomes=())


def test_mutated_child_result_id_refuses() -> None:
    valid = _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a")
    mutated = replace(valid, result_id="cal-child-result:" + "0" * 64)
    with pytest.raises(DecompositionRefusal, match="CHILD_RESULT_ID_MISMATCH"):
        recompose(
            _allof(),
            child_outcomes=(
                mutated,
                _outcome("child-b", B_HASH, Conclusion.SUPPORTED, "b"),
            ),
        )


def test_reused_result_identity_across_children_refuses() -> None:
    first = _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a")
    second = _outcome("child-b", B_HASH, Conclusion.SUPPORTED, "b")
    forged = replace(second, result_id=first.result_id)
    with pytest.raises(DecompositionRefusal):
        recompose(_allof(), child_outcomes=(first, forged))


def test_receipt_binds_decomposition_identity_and_child_results() -> None:
    declaration = _allof()
    children = (
        _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a"),
        _outcome("child-b", B_HASH, Conclusion.SUPPORTED, "b"),
    )
    result = recompose(declaration, child_outcomes=children)
    assert verify_decomposition_receipt(
        result.receipt,
        declaration,
        child_outcomes=children,
    )

    mutated_receipts = (
        replace(result.receipt, receipt_id="0" * 64),
        replace(result.receipt, decomposition_id="decomp-mutated"),
        replace(result.receipt, parent_conclusion=Conclusion.CONTRADICTED),
        replace(result.receipt, ordered_child_bindings=()),
    )
    for receipt in mutated_receipts:
        assert not verify_decomposition_receipt(
            receipt,
            declaration,
            child_outcomes=children,
        )


def test_decomposition_id_mutation_changes_receipt_identity() -> None:
    children = (
        _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a"),
        _outcome("child-b", B_HASH, Conclusion.SUPPORTED, "b"),
    )
    first = recompose(_allof(decomposition_id="decomp-1"), child_outcomes=children)
    second = recompose(_allof(decomposition_id="decomp-2"), child_outcomes=children)
    assert first.conclusion is second.conclusion
    assert first.receipt.receipt_id != second.receipt.receipt_id


def test_child_conclusion_mutation_changes_semantics_and_result_identity() -> None:
    supported = _outcome("child-b", B_HASH, Conclusion.SUPPORTED, "b")
    contradicted = _outcome("child-b", B_HASH, Conclusion.CONTRADICTED, "b")
    assert supported.result_id != contradicted.result_id
    first = _outcome("child-a", A_HASH, Conclusion.SUPPORTED, "a")
    assert recompose(_allof(), child_outcomes=(first, supported)).conclusion is Conclusion.SUPPORTED
    assert (
        recompose(_allof(), child_outcomes=(first, contradicted)).conclusion
        is Conclusion.CONTRADICTED
    )
