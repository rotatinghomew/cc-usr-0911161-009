from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

@dataclass(frozen=True)
class DomainSignal:
    code: str
    score: float
    severity: str
    evidence: dict[str, Any]

def number(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    try:
        value = float(payload.get(key, default))
    except (TypeError, ValueError):
        return default
    return default if value != value or value in (float('inf'), float('-inf')) else value

def ratio(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    value = number(payload, key, default)
    if value > 1.0:
        value /= 100.0
    return max(0.0, min(1.0, value))

def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

def sla_pressure(payload: Mapping[str, Any]) -> DomainSignal:
    response = min(1.0, number(payload, 'response_ms') / 5000.0)
    queue = min(1.0, number(payload, 'request_queue') / 1000.0)
    load = ratio(payload, 'resource_load')
    errors = ratio(payload, 'error_rate')
    capacity = max(1.0, number(payload, 'capacity_units', 1.0))
    priority = min(1.0, number(payload, 'priority') / 100.0)
    sequence = max(0.0, number(payload, 'event_sequence'))
    saturation = min(1.0, queue/capacity)
    pressure = clamp(response*0.2 + saturation*0.24 + load*0.22 + errors*0.2 + priority*0.08 + min(1.0,sequence/1000.0)*0.06)
    severity = 'critical' if pressure >= 0.75 or errors >= 0.5 else 'warning' if pressure >= 0.45 else 'info'
    return DomainSignal('sla_pressure', pressure, severity, {'response_pressure': response, 'saturation': saturation, 'load': load, 'error_rate': errors})

def peer_distribution(records: Iterable[Any], group_field: str = 'region_code') -> dict[str, Any]:
    regions = {}
    for record in records:
        payload = getattr(record,'payload',record); regions.setdefault(str(payload.get(group_field,'unknown')),[]).append(sla_pressure(payload).score)
    peaks = {k:max(v) for k,v in regions.items()}
    return {'region_peaks': peaks, 'critical_regions': sum(v>=0.75 for v in peaks.values()), 'count': sum(len(v) for v in regions.values())}

def augment_context(record: Any, repository: Any) -> dict[str, Any]:
    signal=sla_pressure(record.payload); peers=peer_distribution(repository.list_records())
    return {'domain_signal':signal.score,'domain_severity':signal.severity,'critical_regions':peers['critical_regions'],'peer_count':peers['count']}
