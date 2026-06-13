"""Characterization tests for the governed semantic classifier."""

from __future__ import annotations

import pytest

from claim_audit_lab.classifiers import classify_claim_text
from claim_audit_lab.models import ClaimType


@pytest.mark.parametrize(
    "text,expected",
    [
        pytest.param("The checklist will catch 52 cases.", "prediction", id="prediction-first"),
        pytest.param("The tool works across all workflows.", "scope", id="scope"),
        pytest.param("The checklist reduced unsupported claims.", "causal", id="causal"),
        pytest.param("The review is faster than a manual pass.", "comparative", id="comparative"),
        pytest.param(
            "The reviewer has 8 years of experience.",
            "credential",
            id="credential-before-numeric",
        ),
        pytest.param("The tool can generate audit summaries.", "capability", id="capability"),
        pytest.param("The test set included 52 outputs.", "numeric", id="numeric"),
        pytest.param("The report is credible and useful.", "interpretive", id="interpretive"),
        pytest.param("The report describes the pilot.", "unclassified", id="unclassified"),
        pytest.param("The checklist will always work.", "prediction", id="will-always"),
        pytest.param("The method applies to every team.", "scope", id="every"),
        pytest.param("The result occurred because of the review.", "causal", id="because"),
        pytest.param("The score was lower compared with baseline.", "comparative", id="compared"),
        pytest.param("The author published the report.", "credential", id="published"),
        pytest.param("The system is able to extract claims.", "capability", id="able-to"),
        pytest.param("Accuracy reached 92%.", "numeric", id="percent"),
        pytest.param("The outcome is materially significant.", "interpretive", id="significant"),
        pytest.param("A plain factual sentence appears here.", "unclassified", id="plain"),
    ],
)
def test_classify_claim_text_uses_governed_priority(
    text: str,
    expected: ClaimType,
) -> None:
    assert classify_claim_text(text) == expected
