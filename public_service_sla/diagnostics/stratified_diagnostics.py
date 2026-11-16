"""Stratified SLA diagnostics.

The portfolio-level mean response time and total capacity cannot distinguish
between three very different failure modes:

1. a request queue surge (a load/capacity problem),
2. abnormal telemetry records (a data quality / instrumentation problem), and
3. a small number of user groups or regions that keep missing their service
   window (an equity/continuity problem hidden by the overall average).

This module recomputes the same service-window telemetry along two business
dimensions (``region_code`` and ``user_group``) and compares, for every
stratum: request load, effective response, anomaly rate and capacity
occupancy. A stratum that does not have enough trustworthy observations is
explicitly marked ``insufficient_evidence`` instead of being reported as
healthy, and remediation advice for such a stratum never recommends adding
capacity.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

from public_service_sla.telemetry.service_event import DomainRecord, stable_hash

#: Dimensions used to slice the service-window telemetry.
DIMENSIONS: tuple[str, ...] = ("region_code", "user_group")

#: Fields that have to be numerically trustworthy before a stratum may drive
#: any of the four headline metrics.
KEY_FIELDS: tuple[str, ...] = (
    "request_queue",
    "response_ms",
    "error_rate",
    "capacity_units",
    "resource_load",
)

#: Fields required by the service-window contract; used to measure how many
#: observations are incomplete records.
CONTRACT_FIELDS: tuple[str, ...] = (
    "service_id",
    "region_code",
    "access_tier",
    "user_group",
    "response_ms",
    "request_queue",
    "resource_load",
    "error_rate",
    "support_status",
    "capacity_units",
    "priority",
    "event_sequence",
)

DEFAULT_MIN_SAMPLES = 3
DEFAULT_RESPONSE_BUDGET_MS = 1000.0
DEFAULT_QUEUE_BUDGET = 300.0
DEFAULT_ERROR_RATE_LIMIT = 0.25
DEFAULT_UTILIZATION_LIMIT = 0.8
DEFAULT_COVERAGE_FLOOR = 0.8
DEFAULT_VULNERABLE_GAP = 0.15
DEFAULT_QUEUE_SURGE = 0.7
DEFAULT_PERSISTENCE_FLOOR = 0.5

TRUSTED = "trusted"
INSUFFICIENT_EVIDENCE = "insufficient_evidence"


def _payload(record: Any) -> Mapping[str, Any]:
    return getattr(record, "payload", record)


def _record_id(record: Any) -> str:
    return str(getattr(record, "record_id", "window"))


def _dimension_value(payload: Mapping[str, Any], name: str) -> str:
    value = payload.get(name)
    if value is None or str(value).strip() == "":
        return "unknown"
    return " ".join(str(value).strip().split())


def safe_float(value: Any) -> float | None:
    """Return a finite float or ``None`` when the observation is not numeric."""
    if value is None or isinstance(value, bool) or value == "":
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    return result


def _error_fraction(value: float) -> float:
    """Normalize an error rate to a 0..1 fraction (inputs may be percent)."""
    fraction = value / 100.0 if value > 1.0 else value
    return max(0.0, min(1.0, fraction))


def _mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, value))


@dataclass(frozen=True)
class Thresholds:
    """Diagnostic thresholds; every value can be overridden via context."""

    min_samples: int = DEFAULT_MIN_SAMPLES
    response_budget_ms: float = DEFAULT_RESPONSE_BUDGET_MS
    queue_budget: float = DEFAULT_QUEUE_BUDGET
    error_rate_limit: float = DEFAULT_ERROR_RATE_LIMIT
    utilization_limit: float = DEFAULT_UTILIZATION_LIMIT
    coverage_floor: float = DEFAULT_COVERAGE_FLOOR
    vulnerable_gap: float = DEFAULT_VULNERABLE_GAP
    queue_surge: float = DEFAULT_QUEUE_SURGE
    persistence_floor: float = DEFAULT_PERSISTENCE_FLOOR

    @classmethod
    def from_context(cls, context: Mapping[str, Any] | None) -> "Thresholds":
        context = context or {}

        def pick(key: str, default: Any) -> Any:
            value = safe_float(context.get(key, default))
            return default if value is None else value

        return cls(
            min_samples=int(pick("diagnostics_min_samples", DEFAULT_MIN_SAMPLES)),
            response_budget_ms=pick("diagnostics_response_budget_ms", DEFAULT_RESPONSE_BUDGET_MS),
            queue_budget=pick("diagnostics_queue_budget", DEFAULT_QUEUE_BUDGET),
            error_rate_limit=pick("diagnostics_error_rate_limit", DEFAULT_ERROR_RATE_LIMIT),
            utilization_limit=pick("diagnostics_utilization_limit", DEFAULT_UTILIZATION_LIMIT),
            coverage_floor=pick("diagnostics_coverage_floor", DEFAULT_COVERAGE_FLOOR),
            vulnerable_gap=pick("diagnostics_vulnerable_gap", DEFAULT_VULNERABLE_GAP),
            queue_surge=pick("diagnostics_queue_surge", DEFAULT_QUEUE_SURGE),
            persistence_floor=pick("diagnostics_persistence_floor", DEFAULT_PERSISTENCE_FLOOR),
        )


@dataclass
class StratumStats:
    """All evidence collected for one region or user-group stratum."""

    dimension: str
    key: str
    record_ids: list[str] = field(default_factory=list)
    samples: int = 0
    trusted_samples: int = 0
    defective_samples: int = 0
    field_coverage: dict[str, float] = field(default_factory=dict)
    coverage: float = 0.0
    # request load
    total_request_queue: float = 0.0
    mean_request_queue: float = 0.0
    mean_resource_load: float = 0.0
    mean_queue_pressure: float = 0.0
    # effective response
    response_observations: int = 0
    mean_response_ms: float = 0.0
    effective_response_rate: float = 0.0
    # anomaly
    error_observations: int = 0
    mean_error_rate: float = 0.0
    anomaly_rate: float = 0.0
    data_defect_rate: float = 0.0
    # capacity occupancy
    total_capacity: float = 0.0
    mean_capacity_occupancy: float = 0.0
    saturated_rate: float = 0.0
    # reliability / interpretation
    persistent_breach_rate: float = 0.0
    evidence_status: str = INSUFFICIENT_EVIDENCE
    evidence_reasons: list[str] = field(default_factory=list)
    drivers: list[str] = field(default_factory=list)
    recommendation: str = "insufficient_evidence"
    recommendation_message: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def is_trusted(self) -> bool:
        return self.evidence_status == TRUSTED

    def as_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "key": self.key,
            "record_ids": list(self.record_ids),
            "samples": self.samples,
            "trusted_samples": self.trusted_samples,
            "defective_samples": self.defective_samples,
            "field_coverage": dict(self.field_coverage),
            "coverage": self.coverage,
            "total_request_queue": self.total_request_queue,
            "mean_request_queue": self.mean_request_queue,
            "mean_resource_load": self.mean_resource_load,
            "mean_queue_pressure": self.mean_queue_pressure,
            "response_observations": self.response_observations,
            "mean_response_ms": self.mean_response_ms,
            "effective_response_rate": self.effective_response_rate,
            "error_observations": self.error_observations,
            "mean_error_rate": self.mean_error_rate,
            "anomaly_rate": self.anomaly_rate,
            "data_defect_rate": self.data_defect_rate,
            "total_capacity": self.total_capacity,
            "mean_capacity_occupancy": self.mean_capacity_occupancy,
            "saturated_rate": self.saturated_rate,
            "persistent_breach_rate": self.persistent_breach_rate,
            "evidence_status": self.evidence_status,
            "evidence_reasons": list(self.evidence_reasons),
            "drivers": list(self.drivers),
            "recommendation": self.recommendation,
            "recommendation_message": self.recommendation_message,
            "evidence": dict(self.evidence),
        }


def _build_stratum(dimension: str, key: str, members: list[Any],
                   thresholds: Thresholds) -> StratumStats:
    stats = StratumStats(dimension=dimension, key=key)
    queues: list[float] = []
    loads: list[float] = []
    queue_pressures: list[float] = []
    responses: list[float] = []
    effective_responses = 0
    errors: list[float] = []
    anomalies = 0
    occupancies: list[float] = []
    saturated = 0
    breaches = 0
    valid_per_field: dict[str, int] = {name: 0 for name in KEY_FIELDS}

    for record in members:
        payload = _payload(record)
        stats.record_ids.append(_record_id(record))
        stats.samples += 1

        defective = any(payload.get(name) in (None, "") for name in CONTRACT_FIELDS)
        if defective:
            stats.defective_samples += 1

        numeric: dict[str, float] = {}
        for name in KEY_FIELDS:
            value = safe_float(payload.get(name))
            if value is not None:
                valid_per_field[name] += 1
                numeric[name] = value
        if len(numeric) == len(KEY_FIELDS):
            stats.trusted_samples += 1

        queue = numeric.get("request_queue")
        if queue is not None:
            queues.append(max(0.0, queue))
            queue_pressures.append(_bounded(max(0.0, queue) / max(1e-9, thresholds.queue_budget)))
        load = numeric.get("resource_load")
        if load is not None:
            loads.append(_bounded(load))
        response = numeric.get("response_ms")
        if response is not None:
            responses.append(max(0.0, response))
            if response <= thresholds.response_budget_ms:
                effective_responses += 1
        error = numeric.get("error_rate")
        if error is not None:
            fraction = _error_fraction(error)
            errors.append(fraction)
            if fraction > thresholds.error_rate_limit:
                anomalies += 1
        capacity = numeric.get("capacity_units")
        if capacity is not None and queue is not None and capacity > 0:
            occupancy = _bounded(max(0.0, queue) / capacity)
            occupancies.append(occupancy)
            if occupancy >= thresholds.utilization_limit:
                saturated += 1
        window_breach = (
            (response is not None and response > thresholds.response_budget_ms)
            or (error is not None and _error_fraction(error) > thresholds.error_rate_limit)
        )
        if window_breach:
            breaches += 1

    stats.field_coverage = {
        name: valid_per_field[name] / stats.samples if stats.samples else 0.0
        for name in KEY_FIELDS
    }
    stats.coverage = _mean(list(stats.field_coverage.values()))
    stats.total_request_queue = sum(queues)
    stats.mean_request_queue = _mean(queues)
    stats.mean_resource_load = _mean(loads)
    stats.mean_queue_pressure = _mean(queue_pressures)
    stats.response_observations = len(responses)
    stats.mean_response_ms = _mean(responses)
    stats.effective_response_rate = effective_responses / len(responses) if responses else 0.0
    stats.error_observations = len(errors)
    stats.mean_error_rate = _mean(errors)
    stats.anomaly_rate = anomalies / len(errors) if errors else 0.0
    stats.data_defect_rate = stats.defective_samples / stats.samples if stats.samples else 0.0
    stats.total_capacity = sum(
        max(0.0, value)
        for record in members
        if (value := safe_float(_payload(record).get("capacity_units"))) is not None
    )
    stats.mean_capacity_occupancy = _mean(occupancies)
    stats.saturated_rate = saturated / len(occupancies) if occupancies else 0.0
    stats.persistent_breach_rate = breaches / stats.samples if stats.samples else 0.0

    _interpret(stats, thresholds)
    return stats


def _interpret(stats: StratumStats, thresholds: Thresholds) -> None:
    reasons: list[str] = []
    if stats.samples < thresholds.min_samples:
        reasons.append(
            f"sample_size {stats.samples} below minimum {thresholds.min_samples}"
        )
    if stats.coverage < thresholds.coverage_floor:
        reasons.append(
            f"field coverage {stats.coverage:.3f} below floor {thresholds.coverage_floor:.3f}"
        )
    weak_fields = sorted(
        name for name, value in stats.field_coverage.items() if value < thresholds.coverage_floor
    )
    if weak_fields:
        reasons.append("low coverage for fields: " + ",".join(weak_fields))
    if stats.response_observations == 0:
        reasons.append("no trustworthy response_ms observations")
    if stats.error_observations == 0:
        reasons.append("no trustworthy error_rate observations")

    if reasons:
        stats.evidence_status = INSUFFICIENT_EVIDENCE
        stats.evidence_reasons = reasons
        stats.recommendation = "insufficient_evidence"
        stats.recommendation_message = (
            "证据不足：补齐该分层的服务窗口遥测后再判断，不得据此增加容量"
        )
        stats.evidence = {
            "samples": stats.samples,
            "coverage": stats.coverage,
            "field_coverage": dict(stats.field_coverage),
        }
        return

    stats.evidence_status = TRUSTED
    drivers: list[str] = []
    if stats.mean_queue_pressure >= thresholds.queue_surge:
        drivers.append("queue_surge")
    if stats.anomaly_rate > thresholds.error_rate_limit or stats.data_defect_rate > 0:
        drivers.append("record_anomaly")
    if stats.persistent_breach_rate >= thresholds.persistence_floor:
        drivers.append("persistent_window_breach")
    if stats.mean_capacity_occupancy >= thresholds.utilization_limit:
        drivers.append("capacity_constrained")
    stats.drivers = drivers
    stats.evidence = {
        "mean_queue_pressure": stats.mean_queue_pressure,
        "anomaly_rate": stats.anomaly_rate,
        "data_defect_rate": stats.data_defect_rate,
        "effective_response_rate": stats.effective_response_rate,
        "mean_capacity_occupancy": stats.mean_capacity_occupancy,
        "persistent_breach_rate": stats.persistent_breach_rate,
        "drivers": list(drivers),
    }

    if "record_anomaly" in drivers:
        stats.recommendation = "fix_records_and_instrumentation"
        stats.recommendation_message = (
            "异常主要来自记录缺陷或错误率，先核查遥测质量与故障源，而非增加容量"
        )
    elif "persistent_window_breach" in drivers and "capacity_constrained" not in drivers:
        stats.recommendation = "protect_user_group"
        stats.recommendation_message = (
            "该分层持续失约但容量未饱和，应保障其服务连续性（分流/优先窗口），而非增加容量"
        )
    elif "queue_surge" in drivers and "capacity_constrained" in drivers:
        stats.recommendation = "add_capacity_targeted"
        stats.recommendation_message = (
            "队列激增且容量占用饱和，仅在该分层定向扩容，并复核扩容后效果"
        )
    elif "queue_surge" in drivers:
        stats.recommendation = "throttle_or_reroute_load"
        stats.recommendation_message = (
            "队列激增但容量未饱和，应限流或改派请求负荷，而非增加容量"
        )
    else:
        stats.recommendation = "monitor_only"
        stats.recommendation_message = "指标在阈值内，保持观测，不触发扩容"


def stratify_records(records: Iterable[Any],
                     context: Mapping[str, Any] | None = None) -> dict[str, dict[str, StratumStats]]:
    """Group records by each diagnostic dimension and build stratum statistics."""
    thresholds = Thresholds.from_context(context)
    grouped: dict[str, dict[str, list[Any]]] = {
        dimension: {} for dimension in DIMENSIONS
    }
    for record in records:
        payload = _payload(record)
        for dimension in DIMENSIONS:
            key = _dimension_value(payload, dimension)
            grouped[dimension].setdefault(key, []).append(record)

    result: dict[str, dict[str, StratumStats]] = {}
    for dimension in DIMENSIONS:
        result[dimension] = {
            key: _build_stratum(dimension, key, members, thresholds)
            for key, members in sorted(grouped[dimension].items())
        }
    return result


def _portfolio_stats(records: list[Any], thresholds: Thresholds) -> StratumStats:
    return _build_stratum("portfolio", "all", records, thresholds)


def _distribution(trusted: list[StratumStats], attribute: str) -> dict[str, float]:
    values = [getattr(item, attribute) for item in trusted]
    if not values:
        return {"minimum": 0.0, "maximum": 0.0, "mean": 0.0, "trusted_strata": 0}
    return {
        "minimum": min(values),
        "maximum": max(values),
        "mean": _mean(values),
        "trusted_strata": len(values),
    }


def diagnose_records(records: Iterable[Any],
                     context: Mapping[str, Any] | None = None) -> "StratifiedDiagnosis":
    """Build the full stratified diagnosis shared by remediation and reports."""
    rows = list(records)
    thresholds = Thresholds.from_context(context)
    strata = stratify_records(rows, context)
    portfolio = _portfolio_stats(rows, thresholds)

    vulnerable: list[dict[str, Any]] = []
    if portfolio.is_trusted():
        for dimension in DIMENSIONS:
            for stats in strata[dimension].values():
                if not stats.is_trusted():
                    continue
                response_gap = portfolio.effective_response_rate - stats.effective_response_rate
                anomaly_gap = stats.anomaly_rate - portfolio.anomaly_rate
                if (response_gap >= thresholds.vulnerable_gap
                        or anomaly_gap >= thresholds.vulnerable_gap):
                    vulnerable.append({
                        "dimension": dimension,
                        "key": stats.key,
                        "effective_response_rate": stats.effective_response_rate,
                        "anomaly_rate": stats.anomaly_rate,
                        "response_gap_vs_portfolio": response_gap,
                        "anomaly_gap_vs_portfolio": anomaly_gap,
                        "drivers": list(stats.drivers),
                        "recommendation": stats.recommendation,
                    })

    findings: list[dict[str, Any]] = []
    for dimension in DIMENSIONS:
        for stats in strata[dimension].values():
            findings.append({
                "dimension": dimension,
                "key": stats.key,
                "evidence_status": stats.evidence_status,
                "drivers": list(stats.drivers),
                "recommendation": stats.recommendation,
            })

    trusted_strata = [
        stats for dimension in DIMENSIONS for stats in strata[dimension].values()
        if stats.is_trusted()
    ]
    insufficient = [
        {"dimension": dimension, "key": stats.key, "reasons": list(stats.evidence_reasons)}
        for dimension in DIMENSIONS for stats in strata[dimension].values()
        if not stats.is_trusted()
    ]

    recommendation_counts: dict[str, int] = {}
    for dimension in DIMENSIONS:
        for stats in strata[dimension].values():
            recommendation_counts[stats.recommendation] = (
                recommendation_counts.get(stats.recommendation, 0) + 1
            )

    diagnosis = StratifiedDiagnosis(
        generated_for=sorted(_record_id(record) for record in rows),
        thresholds=thresholds,
        portfolio=portfolio,
        strata={
            dimension: {key: stats.as_dict() for key, stats in values.items()}
            for dimension, values in strata.items()
        },
        distributions={
            "effective_response_rate": _distribution(trusted_strata, "effective_response_rate"),
            "anomaly_rate": _distribution(trusted_strata, "anomaly_rate"),
            "mean_capacity_occupancy": _distribution(trusted_strata, "mean_capacity_occupancy"),
            "mean_request_queue": _distribution(trusted_strata, "mean_request_queue"),
        },
        vulnerable_strata=vulnerable,
        insufficient_evidence_strata=insufficient,
        findings=findings,
        recommendation_counts=dict(sorted(recommendation_counts.items())),
    )
    diagnosis.fingerprint = stable_hash(diagnosis.as_dict())
    return diagnosis


def strata_for_record(record: Any) -> dict[str, str]:
    """Return the diagnostic stratum keys a record belongs to."""
    payload = _payload(record)
    return {dimension: _dimension_value(payload, dimension) for dimension in DIMENSIONS}


def trusted_strata_for_record(record: Any,
                              diagnosis: "StratifiedDiagnosis") -> dict[str, dict[str, Any]]:
    """Return per-dimension trust information for one record's strata."""
    keys = strata_for_record(record)
    result: dict[str, dict[str, Any]] = {}
    for dimension, key in keys.items():
        stats = diagnosis.strata.get(dimension, {}).get(key)
        if stats is None:
            result[dimension] = {
                "key": key,
                "trusted": False,
                "recommendation": "insufficient_evidence",
                "reasons": ["stratum not present in diagnosis"],
                "drivers": [],
            }
        else:
            result[dimension] = {
                "key": key,
                "trusted": stats["evidence_status"] == TRUSTED,
                "recommendation": stats["recommendation"],
                "reasons": list(stats["evidence_reasons"]),
                "drivers": list(stats["drivers"]),
            }
    return result


@dataclass
class StratifiedDiagnosis:
    generated_for: list[str]
    thresholds: Thresholds
    portfolio: StratumStats
    strata: dict[str, dict[str, dict[str, Any]]]
    distributions: dict[str, dict[str, float]]
    vulnerable_strata: list[dict[str, Any]]
    insufficient_evidence_strata: list[dict[str, Any]]
    findings: list[dict[str, Any]]
    recommendation_counts: dict[str, int]
    fingerprint: str = ""

    def as_dict(self) -> dict[str, Any]:
        thresholds = {
            "min_samples": self.thresholds.min_samples,
            "response_budget_ms": self.thresholds.response_budget_ms,
            "queue_budget": self.thresholds.queue_budget,
            "error_rate_limit": self.thresholds.error_rate_limit,
            "utilization_limit": self.thresholds.utilization_limit,
            "coverage_floor": self.thresholds.coverage_floor,
            "vulnerable_gap": self.thresholds.vulnerable_gap,
            "queue_surge": self.thresholds.queue_surge,
            "persistence_floor": self.thresholds.persistence_floor,
        }
        return {
            "generated_for": list(self.generated_for),
            "thresholds": thresholds,
            "portfolio": self.portfolio.as_dict(),
            "strata": {
                dimension: dict(values) for dimension, values in self.strata.items()
            },
            "distributions": dict(self.distributions),
            "vulnerable_strata": list(self.vulnerable_strata),
            "insufficient_evidence_strata": list(self.insufficient_evidence_strata),
            "findings": list(self.findings),
            "recommendation_counts": dict(self.recommendation_counts),
        }
