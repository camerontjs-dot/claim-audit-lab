"""Named deterministic scoring boundaries shared across audit modules."""

DIRECT_NUMERIC_SCORE = 0.70
DIRECT_DATE_SCORE = 0.35
DIRECT_TEXT_SCORE = 0.35
DIRECT_TERM_COVERAGE = 0.50

# A numeric mismatch may remain a useful candidate but can never cross the
# direct numeric-support boundary.
MISMATCHED_NUMERIC_SCORE_CAP = DIRECT_NUMERIC_SCORE - 0.01

__all__ = [
    "DIRECT_DATE_SCORE",
    "DIRECT_NUMERIC_SCORE",
    "DIRECT_TERM_COVERAGE",
    "DIRECT_TEXT_SCORE",
    "MISMATCHED_NUMERIC_SCORE_CAP",
]
