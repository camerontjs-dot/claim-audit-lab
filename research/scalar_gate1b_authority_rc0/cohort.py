"""Frozen Gate-1B cohort for scalar authority RC0."""

from __future__ import annotations

from dataclasses import dataclass

from research.scalar_measurement_machinery_rc0.cohort import (
    BATCH_COUNT,
    BATCH_TEMP_C,
    BATCH_TEMP_F,
    BATCH_YIELD,
    Target,
)


@dataclass(frozen=True, slots=True)
class CleanCase:
    case_id: str
    text: str
    target: Target


CLEAN: tuple[CleanCase, ...] = (
    CleanCase("SW01", "Batch yield was 92%.", BATCH_YIELD),
    CleanCase("SW02", "Batch yield was 92.5%.", BATCH_YIELD),
    CleanCase("SW03", "Batch yield was between 90% and 94%.", BATCH_YIELD),
    CleanCase("SW04", "Batch count was 17.", BATCH_COUNT),
    CleanCase("SW05", "Batch temperature was 5 °C.", BATCH_TEMP_C),
    CleanCase("SW06", "Batch yield was approximately 92%.", BATCH_YIELD),
    CleanCase("SW07", "Batch yield: 92%.", BATCH_YIELD),
    CleanCase("SW08", "Batch temperature was 41 °F.", BATCH_TEMP_F),
    CleanCase("SW09", "Batch yield was 92 ± 2%.", BATCH_YIELD),
)
