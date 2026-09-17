"""Frozen evaluator for CAL Deontic Measurement Machinery RC0."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .cohort import Bucket, CASES, CASES_BY_ID, METAMORPHIC_PAIRS, Observation, Status

Strategy = Callable[[str], Observation]


@dataclass(frozen=True, slots=True)
class Report:
    must_handle_failures: tuple[str, ...]
    fail_closed_unsafe: tuple[str, ...]
    diagnostic_wrong_claims: tuple[str, ...]
    diagnostic_exact: tuple[str, ...]
    diagnostic_unresolved: tuple[str, ...]
    diagnostic_not_applicable: tuple[str, ...]

    @property
    def qualifiable(self) -> bool:
        return (
            not self.must_handle_failures
            and not self.fail_closed_unsafe
            and not self.diagnostic_wrong_claims
        )


def evaluate(strategy: Strategy) -> Report:
    must_handle_failures: list[str] = []
    fail_closed_unsafe: list[str] = []
    diagnostic_wrong_claims: list[str] = []
    diagnostic_exact: list[str] = []
    diagnostic_unresolved: list[str] = []
    diagnostic_not_applicable: list[str] = []

    for case in CASES:
        observed = strategy(case.text)
        if case.bucket is Bucket.MUST_HANDLE:
            if observed.status is not Status.CLAIMED or observed.norm != case.expected:
                must_handle_failures.append(case.case_id)
        elif case.bucket is Bucket.FAIL_CLOSED:
            if observed.status is Status.CLAIMED:
                fail_closed_unsafe.append(case.case_id)
        else:
            if observed.status is Status.CLAIMED:
                if observed.norm == case.expected:
                    diagnostic_exact.append(case.case_id)
                else:
                    diagnostic_wrong_claims.append(case.case_id)
            elif observed.status is Status.UNRESOLVED:
                diagnostic_unresolved.append(case.case_id)
            else:
                diagnostic_not_applicable.append(case.case_id)

    return Report(
        must_handle_failures=tuple(must_handle_failures),
        fail_closed_unsafe=tuple(fail_closed_unsafe),
        diagnostic_wrong_claims=tuple(diagnostic_wrong_claims),
        diagnostic_exact=tuple(diagnostic_exact),
        diagnostic_unresolved=tuple(diagnostic_unresolved),
        diagnostic_not_applicable=tuple(diagnostic_not_applicable),
    )


def metamorphic_failures(strategy: Strategy) -> tuple[str, ...]:
    failures: list[str] = []
    for left_id, right_id in METAMORPHIC_PAIRS:
        left = CASES_BY_ID[left_id]
        right = CASES_BY_ID[right_id]
        left_obs = strategy(left.text)
        right_obs = strategy(right.text)
        if left.bucket is Bucket.MUST_HANDLE and (
            left_obs.status is not Status.CLAIMED or left_obs.norm != left.expected
        ):
            failures.append(f"{left_id}->{right_id}:left")
            continue
        if right.bucket is Bucket.MUST_HANDLE:
            if right_obs.status is not Status.CLAIMED or right_obs.norm != right.expected:
                failures.append(f"{left_id}->{right_id}:right")
        elif right.bucket is Bucket.FAIL_CLOSED and right_obs.status is Status.CLAIMED:
            failures.append(f"{left_id}->{right_id}:unsafe-right")
    return tuple(failures)


# Frozen weak strategies prove that the evaluator discriminates the intended hazards.
def weak_modal_cue(text: str) -> Observation:
    from .cohort import Mode, Norm

    if " may " in f" {text.casefold()} ":
        return Observation.claimed(Norm(Mode.PERMITTED, "qualified_technicians", "release_batch"))
    return Observation.unresolved("weak")


def weak_modifier_erasure(text: str) -> Observation:
    from .cohort import Mode, Norm

    low = text.casefold()
    if "must not" in low or "prohibited" in low:
        mode = Mode.PROHIBITED
    elif "must " in low or "required" in low:
        mode = Mode.OBLIGATORY
    elif "only " in low:
        mode = Mode.PERMISSION_RESTRICTED_TO
    else:
        mode = Mode.PERMITTED
    return Observation.claimed(Norm(mode, "qualified_technicians", "release_batch"))


def weak_may_not_prohibition(text: str) -> Observation:
    from .cohort import Mode, Norm

    low = text.casefold()
    if "may not" in low:
        return Observation.claimed(Norm(Mode.PROHIBITED, "qualified_technicians", "release_batch"))
    return Observation.unresolved("weak")


def weak_reporting_erasure(text: str) -> Observation:
    from .cohort import Mode, Norm

    low = text.casefold()
    if "may release the batch" in low:
        return Observation.claimed(Norm(Mode.PERMITTED, "qualified_technicians", "release_batch"))
    return Observation.unresolved("weak")


def weak_exact_modal_only(text: str) -> Observation:
    from .cohort import Mode, Norm

    low = text.casefold()
    if "must not" in low:
        return Observation.claimed(Norm(Mode.PROHIBITED, "qualified_technicians", "release_batch"))
    if "must " in low:
        return Observation.claimed(Norm(Mode.OBLIGATORY, "qualified_technicians", "release_batch"))
    if " may " in f" {low} ":
        return Observation.claimed(Norm(Mode.PERMITTED, "qualified_technicians", "release_batch"))
    return Observation.not_applicable("weak")
