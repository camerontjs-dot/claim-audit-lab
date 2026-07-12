"""Calibration engine for the ``calibrate`` command (Phase 4 Unit 1 / B17).

Runs the v1 pipeline over a packet of C-B bundles, scores every claim against a
blind human gold, and renders a deterministic Markdown calibration report plus
one :class:`~claim_audit_lab.v1.models.AuditTrace` per claim.

Two design choices keep this module honest and testable:

* **Build against the shipped two-axis verdict.** The report measures CAL's
  *emitted* ``support_verdict`` (5 ordinal degrees) against gold; ``overstated`` /
  ``inferred`` are flags on a degree, not degrees, so the confusion matrix is 5×5
  and the flags are a second axis. The gold is crosswalked into the same two-axis
  space (Decision A / the 3 explicit mappings in ``v1-pre-coding-decisions.md``).
* **Torch-free by construction.** The pipeline is injected as an ``auditor``
  callable, so the metric/crosswalk/render logic imports no inference stack and is
  covered by fast unit tests; the CLI passes the real
  :func:`claim_audit_lab.v1.runner.run_default_audit`.

Metrics are pure functions over integer counts (stdlib only). Cohen's κ is kept
for continuity with the v0.2 −0.006 baseline; Gwet AC2 + quadratic weighted-κ are
the prevalence-robust metrics flagged by Decision D (PROPOSED — the *gate
threshold* under AC2 is re-derived at Unit 3, not here). The κ confidence interval
is a simplified asymptotic Wald interval; confirming the exact Bonett & Bergsma
(2008) variance is a gate-time (Unit 3) sign-off item.

The report additionally carries ``## 7. Rule fire rates`` (added 2026-07-02 —
additive under the ACCEPTED §1–7 schema): per-rule claims-fired counts over the
packet, the instrument for the Decision G dev-iteration loop and the "no Phase C
rule dominates" sanity criterion.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from claim_audit_lab.contracts.bundle_loader import load_bundle
from claim_audit_lab.v1.config import RULES_FILE_RESOURCE, hash_audit_config
from claim_audit_lab.v1.intake import bundle_to_requests
from claim_audit_lab.v1.models import (
    AuditConfig,
    AuditFlag,
    AuditRequest,
    AuditTrace,
    CitationStatus,
    SupportVerdict,
    Verdict,
    VerdictReason,
)

Auditor = Callable[[AuditRequest], AuditTrace]
"""A claim-auditing callable. The CLI injects ``run_default_audit`` (real models);
tests inject a stub returning canned traces."""

# --- Vocabularies ----------------------------------------------------------------

RawGoldVerdict = Literal[
    "supported",
    "partially_supported",
    "reasonable_inference",
    "unsupported",
    "contradicted",
    "not_checkable",
]
"""The single-coder PILOT-001 gold verdict vocabulary (score_calibration.py)."""

RawGoldFlag = Literal[
    "source_scope_error",
    "overconfident",
    "missing_needed",
    "false_caution",
]
"""Gold flag vocabulary (separate axis from the verdict)."""

SUPPORT_VERDICTS: tuple[SupportVerdict, ...] = (
    "supported",
    "partially_supported",
    "unsupported",
    "contradicted",
    "not_checkable",
)

ALL_FLAGS: tuple[AuditFlag, ...] = (
    "overstated",
    "inferred",
    "source_scope_error",
    "false_caution",
    "missed_counterevidence",
    "coverage_loss",
)

# Ordinal positions for the weighted metrics (Decision 1 scale). ``not_checkable``
# is off-scale and excluded from weighted-κ / AC2; it still appears in exact
# agreement, Cohen's κ, and the 5×5 confusion matrix.
ON_SCALE: tuple[SupportVerdict, ...] = (
    "supported",
    "partially_supported",
    "unsupported",
    "contradicted",
)
_ORDINAL: dict[SupportVerdict, float] = {
    "supported": 4.0,
    "partially_supported": 3.0,
    "unsupported": 1.0,
    "contradicted": 0.0,
}
_SCALE_RANGE = 4.0
_ADVERSE: frozenset[SupportVerdict] = frozenset({"unsupported", "contradicted"})
_Z_95 = 1.959963984540054  # standard-normal 0.975 quantile

VerdictPair = tuple[SupportVerdict, SupportVerdict]  # (gold, cal)


# --- Gold contract ---------------------------------------------------------------


class _StrictModel(BaseModel):
    """Base for calibration contract types: frozen, strict, no extras."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class GoldClaim(_StrictModel):
    """One blind-gold record for a single claim."""

    claim_id: str
    condition: str
    model: str
    gold_verdict: RawGoldVerdict
    gold_flags: list[RawGoldFlag] = Field(default_factory=list)


class CalibrationGold(_StrictModel):
    """The sealed human gold for a calibration packet."""

    gold_version: str
    starved_claim_ids: list[str] = Field(default_factory=list)
    claims: list[GoldClaim]


# --- Result models ---------------------------------------------------------------


class AgreementStats(_StrictModel):
    """Exact agreement plus the reliability coefficients."""

    n_total: int
    n_agree: int
    exact_agreement: float
    cohens_kappa: float
    kappa_ci_low: float
    kappa_ci_high: float
    on_scale_n: int
    weighted_kappa: float
    gwet_ac2: float


class RecallFloor(_StrictModel):
    """How the v0.2-starved claims land under v1 (gate condition 1)."""

    starved_total: int
    supported: int
    partially_supported: int
    adverse: int
    not_checkable: int


class FlagTally(_StrictModel):
    """Per-flag occurrence counts on each axis."""

    flag: AuditFlag
    gold_count: int
    cal_count: int


class AdverseRate(_StrictModel):
    """Adverse = unsupported + contradicted; checkable = total − not_checkable."""

    group: str
    cal_adverse: int
    cal_checkable: int
    gold_adverse: int
    gold_checkable: int


class RuleFireTally(_StrictModel):
    """How many claims a rule fired on across the packet (§7 of the report)."""

    rule_id: str
    fired: int


class CalibrationResult(_StrictModel):
    """Everything the report renders — a pure function of (traces, gold, config)."""

    n_claims: int
    agreement: AgreementStats
    recall_floor: RecallFloor
    confusion: dict[SupportVerdict, dict[SupportVerdict, int]]
    flags: list[FlagTally]
    overall_adverse: AdverseRate
    per_condition: list[AdverseRate]
    per_model: list[AdverseRate]
    rule_fires: list[RuleFireTally]
    rules_version: str
    rules_file_sha: str
    audit_config_hash: str
    library_version: str
    retriever: str
    entailer: str


# --- Crosswalk -------------------------------------------------------------------


def crosswalk_gold(verdict: RawGoldVerdict, flags: list[RawGoldFlag]) -> Verdict:
    """Map a raw gold (verdict, flags) record into CAL's two-axis :class:`Verdict`.

    The three explicit mappings (Decision A): ``reasonable_inference`` →
    ``supported`` + ``inferred``; ``overconfident`` → flag ``overstated``;
    ``missing_needed`` → ``citation_status='missing_needed'``. ``source_scope_error``
    and ``false_caution`` pass through to the like-named CAL flag.
    """
    support: SupportVerdict
    audit_flags: list[AuditFlag] = []
    reason: VerdictReason | None = None
    if verdict == "reasonable_inference":
        support = "supported"
        audit_flags.append("inferred")
    else:
        support = verdict

    citation: CitationStatus = "not_applicable"
    for flag in flags:
        if flag == "overconfident":
            audit_flags.append("overstated")
        elif flag == "source_scope_error":
            audit_flags.append("source_scope_error")
        elif flag == "false_caution":
            audit_flags.append("false_caution")
        elif flag == "missing_needed":
            citation = "missing_needed"

    return Verdict(
        support_verdict=support,
        support_verdict_reason=reason,
        audit_flags=_dedupe(audit_flags),
        citation_status=citation,
    )


def _dedupe(flags: list[AuditFlag]) -> list[AuditFlag]:
    seen: set[AuditFlag] = set()
    out: list[AuditFlag] = []
    for flag in flags:
        if flag not in seen:
            seen.add(flag)
            out.append(flag)
    return out


# --- Metrics (pure) --------------------------------------------------------------


def exact_agreement(pairs: list[VerdictPair]) -> tuple[int, int]:
    """Return (n_agree, n_total) on the support_verdict axis."""
    return sum(1 for gold, cal in pairs if gold == cal), len(pairs)


def _kappa_components(pairs: list[VerdictPair]) -> tuple[float, float, int]:
    """Return (observed agreement, expected agreement, n) for Cohen's κ."""
    n = len(pairs)
    if n == 0:
        return 0.0, 0.0, 0
    labels = SUPPORT_VERDICTS
    counts: dict[SupportVerdict, dict[SupportVerdict, int]] = {
        gold: dict.fromkeys(labels, 0) for gold in labels
    }
    for gold, cal in pairs:
        counts[gold][cal] += 1
    po = sum(counts[k][k] for k in labels) / n
    row = {k: sum(counts[k][c] for c in labels) / n for k in labels}
    col = {k: sum(counts[g][k] for g in labels) / n for k in labels}
    pe = sum(row[k] * col[k] for k in labels)
    return po, pe, n


def cohens_kappa(pairs: list[VerdictPair]) -> float:
    """Unweighted Cohen's κ over all five support degrees."""
    po, pe, n = _kappa_components(pairs)
    return _chance_corrected(po, pe, n)


def cohens_kappa_ci(pairs: list[VerdictPair]) -> tuple[float, float]:
    """Simplified asymptotic Wald 95% CI for Cohen's κ.

    SE = sqrt(po(1−po) / (n(1−pe)²)). Informational at Unit 1; the exact
    Bonett & Bergsma (2008) variance is a gate-time sign-off item.
    """
    po, pe, n = _kappa_components(pairs)
    kappa = _chance_corrected(po, pe, n)
    denom = 1.0 - pe
    if n == 0 or abs(denom) < 1e-12:
        return kappa, kappa
    se = math.sqrt(max(po * (1.0 - po), 0.0) / (n * denom * denom))
    return max(-1.0, kappa - _Z_95 * se), min(1.0, kappa + _Z_95 * se)


def weighted_kappa(pairs: list[VerdictPair]) -> tuple[float, int]:
    """Quadratic weighted Cohen's κ over the on-scale subset; returns (κ_w, n)."""
    sub = _on_scale(pairs)
    n = len(sub)
    if n == 0:
        return 0.0, 0
    prop, row, col = _weighted_proportions(sub)
    pa = sum(_weight(g, c) * prop[g][c] for g in ON_SCALE for c in ON_SCALE)
    pe = sum(_weight(g, c) * row[g] * col[c] for g in ON_SCALE for c in ON_SCALE)
    return _chance_corrected(pa, pe, n), n


def gwet_ac2(pairs: list[VerdictPair]) -> tuple[float, int]:
    """Gwet's AC2 with quadratic weights over the on-scale subset; returns (AC2, n).

    Prevalence-robust: chance agreement uses the averaged marginals π_k. Reduces
    to AC1 under identity weights (asserted in the unit tests).
    """
    sub = _on_scale(pairs)
    n = len(sub)
    if n == 0:
        return 0.0, 0
    prop, row, col = _weighted_proportions(sub)
    pi = {k: (row[k] + col[k]) / 2.0 for k in ON_SCALE}
    q = len(ON_SCALE)
    tw = sum(_weight(a, b) for a in ON_SCALE for b in ON_SCALE)
    pa = sum(_weight(g, c) * prop[g][c] for g in ON_SCALE for c in ON_SCALE)
    pe = (tw / (q * (q - 1))) * sum(pi[k] * (1.0 - pi[k]) for k in ON_SCALE)
    return _chance_corrected(pa, pe, n), n


def confusion_matrix(pairs: list[VerdictPair]) -> dict[SupportVerdict, dict[SupportVerdict, int]]:
    """Return the 5×5 confusion counts, gold rows × CAL columns."""
    matrix: dict[SupportVerdict, dict[SupportVerdict, int]] = {
        gold: dict.fromkeys(SUPPORT_VERDICTS, 0) for gold in SUPPORT_VERDICTS
    }
    for gold, cal in pairs:
        matrix[gold][cal] += 1
    return matrix


def adverse_rate(labels: list[SupportVerdict]) -> tuple[int, int]:
    """Return (adverse, checkable): adverse = unsupported+contradicted."""
    adverse = sum(1 for label in labels if label in _ADVERSE)
    checkable = sum(1 for label in labels if label != "not_checkable")
    return adverse, checkable


def _weight(a: SupportVerdict, b: SupportVerdict) -> float:
    """Quadratic agreement weight between two on-scale degrees (1.0 on the diagonal)."""
    delta = (_ORDINAL[a] - _ORDINAL[b]) / _SCALE_RANGE
    return 1.0 - delta * delta


def _on_scale(pairs: list[VerdictPair]) -> list[VerdictPair]:
    return [(g, c) for g, c in pairs if g in _ORDINAL and c in _ORDINAL]


def _weighted_proportions(
    sub: list[VerdictPair],
) -> tuple[
    dict[SupportVerdict, dict[SupportVerdict, float]],
    dict[SupportVerdict, float],
    dict[SupportVerdict, float],
]:
    n = len(sub)
    prop: dict[SupportVerdict, dict[SupportVerdict, float]] = {
        g: dict.fromkeys(ON_SCALE, 0.0) for g in ON_SCALE
    }
    for gold, cal in sub:
        prop[gold][cal] += 1.0 / n
    row = {k: sum(prop[k][c] for c in ON_SCALE) for k in ON_SCALE}
    col = {k: sum(prop[g][k] for g in ON_SCALE) for k in ON_SCALE}
    return prop, row, col


def _chance_corrected(observed: float, expected: float, n: int) -> float:
    if n == 0:
        return 0.0
    denom = 1.0 - expected
    if abs(denom) < 1e-12:
        return 1.0 if abs(1.0 - observed) < 1e-12 else 0.0
    return (observed - expected) / denom


# --- Assembly --------------------------------------------------------------------


def compute_calibration(
    traces: dict[str, AuditTrace],
    gold: CalibrationGold,
    config: AuditConfig,
) -> CalibrationResult:
    """Score ``traces`` against ``gold`` into a :class:`CalibrationResult`.

    Requires the gold claim set to exactly match the audited claim set — a
    calibration instrument never silently drops or invents claims.
    """
    gold_by_id = {claim.claim_id: claim for claim in gold.claims}
    _check_alignment(set(gold_by_id), set(traces), set(gold.starved_claim_ids))

    claim_ids = sorted(gold_by_id)
    gold_verdicts = {
        cid: crosswalk_gold(gold_by_id[cid].gold_verdict, gold_by_id[cid].gold_flags)
        for cid in claim_ids
    }
    cal_verdicts = {cid: traces[cid].verdict for cid in claim_ids}
    pairs: list[VerdictPair] = [
        (gold_verdicts[cid].support_verdict, cal_verdicts[cid].support_verdict) for cid in claim_ids
    ]

    n_agree, n_total = exact_agreement(pairs)
    kappa = cohens_kappa(pairs)
    ci_low, ci_high = cohens_kappa_ci(pairs)
    wk, on_scale_n = weighted_kappa(pairs)
    ac2, _ = gwet_ac2(pairs)

    return CalibrationResult(
        n_claims=n_total,
        agreement=AgreementStats(
            n_total=n_total,
            n_agree=n_agree,
            exact_agreement=(n_agree / n_total) if n_total else 0.0,
            cohens_kappa=kappa,
            kappa_ci_low=ci_low,
            kappa_ci_high=ci_high,
            on_scale_n=on_scale_n,
            weighted_kappa=wk,
            gwet_ac2=ac2,
        ),
        recall_floor=_recall_floor(gold.starved_claim_ids, cal_verdicts),
        confusion=confusion_matrix(pairs),
        flags=_flag_tallies(gold_verdicts, cal_verdicts),
        overall_adverse=_adverse_for(
            "__overall__",
            [cal_verdicts[c].support_verdict for c in claim_ids],
            [gold_verdicts[c].support_verdict for c in claim_ids],
        ),
        per_condition=_grouped_adverse(
            claim_ids, gold_verdicts, cal_verdicts, lambda cid: gold_by_id[cid].condition
        ),
        per_model=_grouped_adverse(
            claim_ids, gold_verdicts, cal_verdicts, lambda cid: gold_by_id[cid].model
        ),
        rule_fires=_rule_fire_tallies(traces),
        rules_version=RULES_FILE_RESOURCE.removesuffix(".yaml"),
        rules_file_sha=config.rules_file_sha,
        audit_config_hash=hash_audit_config(config),
        library_version=_library_version(traces),
        retriever=f"{config.retriever.model_id}@{config.retriever.hf_revision_sha}",
        entailer=f"{config.entailer.model_id}@{config.entailer.hf_revision_sha}",
    )


def run_calibration(
    packet_dir: Path,
    gold: CalibrationGold,
    config: AuditConfig,
    *,
    auditor: Auditor,
    deviations_dir: Path,
) -> tuple[CalibrationResult, dict[str, AuditTrace]]:
    """Audit every claim in ``packet_dir`` and score it against ``gold``.

    ``packet_dir``'s immediate subdirectories that contain a ``bundle_manifest.yaml``
    are each loaded via the fail-closed :func:`load_bundle`, normalized to requests,
    and audited with ``auditor``. Claims are keyed by ``claim_id``, which must be
    unique across the packet.
    """
    traces: dict[str, AuditTrace] = {}
    for bundle_dir in sorted(
        path
        for path in packet_dir.iterdir()
        if path.is_dir() and (path / "bundle_manifest.yaml").is_file()
    ):
        contents = load_bundle(bundle_dir, deviations_dir=deviations_dir)
        for request in bundle_to_requests(contents, config):
            if request.claim_id in traces:
                raise ValueError(f"duplicate claim_id across packet: {request.claim_id}")
            traces[request.claim_id] = auditor(request)
    return compute_calibration(traces, gold, config), traces


def load_gold(path: Path) -> CalibrationGold:
    """Load and strictly validate a calibration gold YAML."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"malformed gold YAML at {path}: {exc}") from exc
    return CalibrationGold.model_validate(raw)


def _check_alignment(gold_ids: set[str], trace_ids: set[str], starved: set[str]) -> None:
    missing = sorted(gold_ids - trace_ids)
    if missing:
        raise ValueError(f"gold claims absent from packet traces: {', '.join(missing)}")
    extra = sorted(trace_ids - gold_ids)
    if extra:
        raise ValueError(f"audited claims absent from gold: {', '.join(extra)}")
    unknown_starved = sorted(starved - gold_ids)
    if unknown_starved:
        raise ValueError(f"starved_claim_ids not in gold: {', '.join(unknown_starved)}")


def _recall_floor(starved: list[str], cal_verdicts: dict[str, Verdict]) -> RecallFloor:
    counts = {"supported": 0, "partially_supported": 0, "adverse": 0, "not_checkable": 0}
    for cid in starved:
        verdict = cal_verdicts[cid].support_verdict
        if verdict == "supported":
            counts["supported"] += 1
        elif verdict == "partially_supported":
            counts["partially_supported"] += 1
        elif verdict in _ADVERSE:
            counts["adverse"] += 1
        else:
            counts["not_checkable"] += 1
    return RecallFloor(starved_total=len(starved), **counts)


def _flag_tallies(
    gold_verdicts: dict[str, Verdict],
    cal_verdicts: dict[str, Verdict],
) -> list[FlagTally]:
    return [
        FlagTally(
            flag=flag,
            gold_count=sum(1 for v in gold_verdicts.values() if flag in v.audit_flags),
            cal_count=sum(1 for v in cal_verdicts.values() if flag in v.audit_flags),
        )
        for flag in ALL_FLAGS
    ]


def _rule_fire_tallies(traces: dict[str, AuditTrace]) -> list[RuleFireTally]:
    """Count, per rule_id, how many claims that rule fired on (once per claim)."""
    counts: dict[str, int] = {}
    for trace in traces.values():
        for rule_id in {fired.rule_id for fired in trace.rules_fired}:
            counts[rule_id] = counts.get(rule_id, 0) + 1
    return [RuleFireTally(rule_id=rule_id, fired=counts[rule_id]) for rule_id in sorted(counts)]


def _grouped_adverse(
    claim_ids: list[str],
    gold_verdicts: dict[str, Verdict],
    cal_verdicts: dict[str, Verdict],
    key_fn: Callable[[str], str],
) -> list[AdverseRate]:
    groups: dict[str, list[str]] = {}
    for cid in claim_ids:
        groups.setdefault(key_fn(cid), []).append(cid)
    return [
        _adverse_for(
            name,
            [cal_verdicts[cid].support_verdict for cid in groups[name]],
            [gold_verdicts[cid].support_verdict for cid in groups[name]],
        )
        for name in sorted(groups)
    ]


def _adverse_for(
    group: str,
    cal_labels: list[SupportVerdict],
    gold_labels: list[SupportVerdict],
) -> AdverseRate:
    cal_adverse, cal_checkable = adverse_rate(cal_labels)
    gold_adverse, gold_checkable = adverse_rate(gold_labels)
    return AdverseRate(
        group=group,
        cal_adverse=cal_adverse,
        cal_checkable=cal_checkable,
        gold_adverse=gold_adverse,
        gold_checkable=gold_checkable,
    )


def _library_version(traces: dict[str, AuditTrace]) -> str:
    versions = {trace.library_version for trace in traces.values()}
    if len(versions) == 1:
        return versions.pop()
    if not versions:
        from importlib.metadata import PackageNotFoundError, version

        try:
            return version("claim-audit-lab")
        except PackageNotFoundError:  # pragma: no cover - clean-wheel always resolves
            return "unknown"
    raise ValueError("inconsistent library_version across traces")


# --- Report rendering ------------------------------------------------------------


def render_report(result: CalibrationResult, *, pinned_at: str) -> str:
    """Render the deterministic Markdown calibration report.

    Section headers are fixed strings in a fixed order so a ``diff`` catches any
    drift. ``pinned_at`` is the only timestamp — never the wall clock — so two
    runs over the same inputs are byte-identical.
    """
    overall = result.overall_adverse
    cal_overall = _ratio(overall.cal_adverse, overall.cal_checkable)
    gold_overall = _ratio(overall.gold_adverse, overall.gold_checkable)
    lines: list[str] = [
        "# CAL v1 Calibration Report",
        f"Generated: {pinned_at}",
        f"Library: claim_audit_lab {result.library_version}",
        f"Rules: {result.rules_version} (sha: {result.rules_file_sha})",
        f"audit_config_hash: {result.audit_config_hash}",
        f"Claims scored: {result.n_claims}",
        "",
        "## 1. Recall floor on starved claims",
        *_recall_lines(result.recall_floor),
        "",
        "## 2. Agreement and reliability",
        *_agreement_lines(result.agreement),
        "",
        "## 3. Support-verdict confusion (gold rows x CAL columns)",
        *_confusion_lines(result.confusion),
        "",
        "## 4. Flags axis (gold vs CAL counts)",
        *_flag_lines(result.flags),
        "",
        "## 5. Per-condition adverse rate",
        *_adverse_table(result.per_condition, "condition"),
        "",
        "## 6. Per-model adverse rate",
        *_adverse_table(result.per_model, "model"),
        "",
        "## 7. Rule fire rates",
        *_rule_fire_lines(result.rule_fires, result.n_claims),
        "",
        "## Trace metadata",
        f"- Retriever: {result.retriever}",
        f"- Entailer: {result.entailer}",
        "- Determinism: CPU-only, fixed seed; report timestamp pinned via --pinned-at",
        f"- Overall adverse (CAL): {cal_overall}; (gold): {gold_overall}",
    ]
    return "\n".join(lines) + "\n"


def _recall_lines(floor: RecallFloor) -> list[str]:
    total = floor.starved_total
    return [
        f"- supported: {floor.supported}/{total}",
        f"- partially_supported: {floor.partially_supported}/{total}",
        f"- adverse (unsupported + contradicted): {floor.adverse}/{total}",
        f"- not_checkable: {floor.not_checkable}/{total}",
    ]


def _agreement_lines(stats: AgreementStats) -> list[str]:
    pct = (100.0 * stats.n_agree / stats.n_total) if stats.n_total else 0.0
    return [
        f"- Exact agreement: {stats.n_agree}/{stats.n_total} ({pct:.1f}%)",
        f"- Cohen's kappa: {stats.cohens_kappa:.4f}",
        f"- 95% CI (asymptotic Wald): [{stats.kappa_ci_low:.4f}, {stats.kappa_ci_high:.4f}]",
        f"- Gwet AC2 (quadratic, on-scale n={stats.on_scale_n}): {stats.gwet_ac2:.4f}",
        f"- Weighted kappa (quadratic, on-scale): {stats.weighted_kappa:.4f}",
    ]


def _confusion_lines(matrix: dict[SupportVerdict, dict[SupportVerdict, int]]) -> list[str]:
    header = "| gold \\ CAL | " + " | ".join(SUPPORT_VERDICTS) + " |"
    divider = "|" + "---|" * (len(SUPPORT_VERDICTS) + 1)
    rows = [
        "| " + gold + " | " + " | ".join(str(matrix[gold][cal]) for cal in SUPPORT_VERDICTS) + " |"
        for gold in SUPPORT_VERDICTS
    ]
    return [header, divider, *rows]


def _rule_fire_lines(tallies: list[RuleFireTally], n_claims: int) -> list[str]:
    rows = [
        f"| {tally.rule_id} | {tally.fired}/{n_claims} "
        f"({(100.0 * tally.fired / n_claims) if n_claims else 0.0:.1f}%) |"
        for tally in tallies
    ]
    return ["| rule_id | claims fired |", "|---|---|", *rows]


def _flag_lines(flags: list[FlagTally]) -> list[str]:
    return [
        "| flag | gold | CAL |",
        "|---|---|---|",
        *(f"| {tally.flag} | {tally.gold_count} | {tally.cal_count} |" for tally in flags),
    ]


def _adverse_table(rows: list[AdverseRate], key: str) -> list[str]:
    return [
        f"| {key} | CAL adverse/checkable | gold adverse/checkable |",
        "|---|---|---|",
        *(
            f"| {row.group} | {_ratio(row.cal_adverse, row.cal_checkable)} "
            f"| {_ratio(row.gold_adverse, row.gold_checkable)} |"
            for row in rows
        ),
    ]


def _ratio(numerator: int, denominator: int) -> str:
    return f"{numerator}/{denominator}"


__all__ = [
    "AdverseRate",
    "AgreementStats",
    "Auditor",
    "CalibrationGold",
    "CalibrationResult",
    "FlagTally",
    "GoldClaim",
    "RawGoldFlag",
    "RawGoldVerdict",
    "RecallFloor",
    "adverse_rate",
    "cohens_kappa",
    "cohens_kappa_ci",
    "compute_calibration",
    "confusion_matrix",
    "crosswalk_gold",
    "exact_agreement",
    "gwet_ac2",
    "load_gold",
    "render_report",
    "run_calibration",
    "weighted_kappa",
]
