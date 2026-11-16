from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any, Callable, Iterable, Mapping

from public_service_sla.telemetry.service_event import DomainRecord, bounded, finite_number, normalized_text, stable_hash
from public_service_sla.capacity.routing_rules import evaluate, summarize

MetricFunction = Callable[[DomainRecord, Mapping[str, Any]], float]

def _value(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    return float(sum((index + 1) * ord(ch) for index, ch in enumerate(text)) % 997) / 10.0

def _signal(record: DomainRecord, fields: tuple[str, ...], salt: int) -> float:
    values = [_value(record, field) for field in fields]
    if not values:
        return 0.0
    center = statistics.fmean(values)
    spread = statistics.pstdev(values) if len(values) > 1 else 0.0
    harmonic = sum(math.sin(value / (salt + 1)) + math.cos(value * (salt + 1) / 17.0) for value in values)
    return bounded(0.5 + math.tanh((center - spread + harmonic) / (30.0 + salt)) / 2.0)

def metric_route_pressure_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('service_id', 'user_group', 'resource_load', 'capacity_units'), 1)
    weight = finite_number(context.get('route_pressure_weight', 0.7))
    offset = finite_number(context.get('metric_route_pressure_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_route_pressure_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('region_code', 'response_ms', 'error_rate', 'priority'), 2)
    weight = finite_number(context.get('route_pressure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_route_pressure_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_route_pressure_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('access_tier', 'request_queue', 'support_status', 'event_sequence'), 3)
    weight = finite_number(context.get('route_pressure_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_route_pressure_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_route_pressure_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('user_group', 'resource_load', 'capacity_units', 'service_id'), 4)
    weight = finite_number(context.get('route_pressure_weight', 1.0))
    offset = finite_number(context.get('metric_route_pressure_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_route_pressure_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('response_ms', 'error_rate', 'priority', 'region_code'), 5)
    weight = finite_number(context.get('route_pressure_weight', 0.7))
    offset = finite_number(context.get('metric_route_pressure_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_route_pressure_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('request_queue', 'support_status', 'event_sequence', 'access_tier'), 6)
    weight = finite_number(context.get('route_pressure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_route_pressure_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_route_pressure_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_load', 'capacity_units', 'service_id', 'user_group'), 7)
    weight = finite_number(context.get('route_pressure_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_route_pressure_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_route_pressure_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('error_rate', 'priority', 'region_code', 'response_ms'), 8)
    weight = finite_number(context.get('route_pressure_weight', 1.0))
    offset = finite_number(context.get('metric_route_pressure_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_route_pressure_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('support_status', 'event_sequence', 'access_tier', 'request_queue'), 9)
    weight = finite_number(context.get('route_pressure_weight', 0.7))
    offset = finite_number(context.get('metric_route_pressure_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_route_pressure_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capacity_units', 'service_id', 'user_group', 'resource_load'), 10)
    weight = finite_number(context.get('route_pressure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_route_pressure_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_eta_reliability_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('region_code', 'response_ms', 'error_rate', 'priority'), 2)
    weight = finite_number(context.get('eta_reliability_weight', 0.7))
    offset = finite_number(context.get('metric_eta_reliability_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_eta_reliability_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('access_tier', 'request_queue', 'support_status', 'event_sequence'), 3)
    weight = finite_number(context.get('eta_reliability_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_eta_reliability_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_eta_reliability_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('user_group', 'resource_load', 'capacity_units', 'service_id'), 4)
    weight = finite_number(context.get('eta_reliability_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_eta_reliability_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_eta_reliability_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('response_ms', 'error_rate', 'priority', 'region_code'), 5)
    weight = finite_number(context.get('eta_reliability_weight', 1.0))
    offset = finite_number(context.get('metric_eta_reliability_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_eta_reliability_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('request_queue', 'support_status', 'event_sequence', 'access_tier'), 6)
    weight = finite_number(context.get('eta_reliability_weight', 0.7))
    offset = finite_number(context.get('metric_eta_reliability_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_eta_reliability_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_load', 'capacity_units', 'service_id', 'user_group'), 7)
    weight = finite_number(context.get('eta_reliability_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_eta_reliability_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_eta_reliability_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('error_rate', 'priority', 'region_code', 'response_ms'), 8)
    weight = finite_number(context.get('eta_reliability_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_eta_reliability_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_eta_reliability_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('support_status', 'event_sequence', 'access_tier', 'request_queue'), 9)
    weight = finite_number(context.get('eta_reliability_weight', 1.0))
    offset = finite_number(context.get('metric_eta_reliability_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_eta_reliability_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capacity_units', 'service_id', 'user_group', 'resource_load'), 10)
    weight = finite_number(context.get('eta_reliability_weight', 0.7))
    offset = finite_number(context.get('metric_eta_reliability_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_eta_reliability_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('priority', 'region_code', 'response_ms', 'error_rate'), 11)
    weight = finite_number(context.get('eta_reliability_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_eta_reliability_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_capacity_balance_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('access_tier', 'request_queue', 'support_status', 'event_sequence'), 3)
    weight = finite_number(context.get('capacity_balance_weight', 0.7))
    offset = finite_number(context.get('metric_capacity_balance_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_capacity_balance_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('user_group', 'resource_load', 'capacity_units', 'service_id'), 4)
    weight = finite_number(context.get('capacity_balance_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_capacity_balance_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_capacity_balance_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('response_ms', 'error_rate', 'priority', 'region_code'), 5)
    weight = finite_number(context.get('capacity_balance_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_capacity_balance_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_capacity_balance_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('request_queue', 'support_status', 'event_sequence', 'access_tier'), 6)
    weight = finite_number(context.get('capacity_balance_weight', 1.0))
    offset = finite_number(context.get('metric_capacity_balance_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_capacity_balance_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_load', 'capacity_units', 'service_id', 'user_group'), 7)
    weight = finite_number(context.get('capacity_balance_weight', 0.7))
    offset = finite_number(context.get('metric_capacity_balance_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_capacity_balance_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('error_rate', 'priority', 'region_code', 'response_ms'), 8)
    weight = finite_number(context.get('capacity_balance_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_capacity_balance_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_capacity_balance_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('support_status', 'event_sequence', 'access_tier', 'request_queue'), 9)
    weight = finite_number(context.get('capacity_balance_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_capacity_balance_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_capacity_balance_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capacity_units', 'service_id', 'user_group', 'resource_load'), 10)
    weight = finite_number(context.get('capacity_balance_weight', 1.0))
    offset = finite_number(context.get('metric_capacity_balance_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_capacity_balance_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('priority', 'region_code', 'response_ms', 'error_rate'), 11)
    weight = finite_number(context.get('capacity_balance_weight', 0.7))
    offset = finite_number(context.get('metric_capacity_balance_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_capacity_balance_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('event_sequence', 'access_tier', 'request_queue', 'support_status'), 12)
    weight = finite_number(context.get('capacity_balance_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_capacity_balance_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_cold_chain_risk_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('user_group', 'resource_load', 'capacity_units', 'service_id'), 4)
    weight = finite_number(context.get('cold_chain_risk_weight', 0.7))
    offset = finite_number(context.get('metric_cold_chain_risk_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_cold_chain_risk_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('response_ms', 'error_rate', 'priority', 'region_code'), 5)
    weight = finite_number(context.get('cold_chain_risk_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_cold_chain_risk_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_cold_chain_risk_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('request_queue', 'support_status', 'event_sequence', 'access_tier'), 6)
    weight = finite_number(context.get('cold_chain_risk_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_cold_chain_risk_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_cold_chain_risk_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_load', 'capacity_units', 'service_id', 'user_group'), 7)
    weight = finite_number(context.get('cold_chain_risk_weight', 1.0))
    offset = finite_number(context.get('metric_cold_chain_risk_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_cold_chain_risk_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('error_rate', 'priority', 'region_code', 'response_ms'), 8)
    weight = finite_number(context.get('cold_chain_risk_weight', 0.7))
    offset = finite_number(context.get('metric_cold_chain_risk_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_cold_chain_risk_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('support_status', 'event_sequence', 'access_tier', 'request_queue'), 9)
    weight = finite_number(context.get('cold_chain_risk_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_cold_chain_risk_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_cold_chain_risk_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capacity_units', 'service_id', 'user_group', 'resource_load'), 10)
    weight = finite_number(context.get('cold_chain_risk_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_cold_chain_risk_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_cold_chain_risk_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('priority', 'region_code', 'response_ms', 'error_rate'), 11)
    weight = finite_number(context.get('cold_chain_risk_weight', 1.0))
    offset = finite_number(context.get('metric_cold_chain_risk_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_cold_chain_risk_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('event_sequence', 'access_tier', 'request_queue', 'support_status'), 12)
    weight = finite_number(context.get('cold_chain_risk_weight', 0.7))
    offset = finite_number(context.get('metric_cold_chain_risk_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_cold_chain_risk_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('service_id', 'user_group', 'resource_load', 'capacity_units'), 13)
    weight = finite_number(context.get('cold_chain_risk_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_cold_chain_risk_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_customs_delay_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('response_ms', 'error_rate', 'priority', 'region_code'), 5)
    weight = finite_number(context.get('customs_delay_weight', 0.7))
    offset = finite_number(context.get('metric_customs_delay_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_customs_delay_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('request_queue', 'support_status', 'event_sequence', 'access_tier'), 6)
    weight = finite_number(context.get('customs_delay_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_customs_delay_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_customs_delay_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_load', 'capacity_units', 'service_id', 'user_group'), 7)
    weight = finite_number(context.get('customs_delay_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_customs_delay_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_customs_delay_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('error_rate', 'priority', 'region_code', 'response_ms'), 8)
    weight = finite_number(context.get('customs_delay_weight', 1.0))
    offset = finite_number(context.get('metric_customs_delay_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_customs_delay_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('support_status', 'event_sequence', 'access_tier', 'request_queue'), 9)
    weight = finite_number(context.get('customs_delay_weight', 0.7))
    offset = finite_number(context.get('metric_customs_delay_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_customs_delay_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capacity_units', 'service_id', 'user_group', 'resource_load'), 10)
    weight = finite_number(context.get('customs_delay_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_customs_delay_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_customs_delay_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('priority', 'region_code', 'response_ms', 'error_rate'), 11)
    weight = finite_number(context.get('customs_delay_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_customs_delay_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_customs_delay_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('event_sequence', 'access_tier', 'request_queue', 'support_status'), 12)
    weight = finite_number(context.get('customs_delay_weight', 1.0))
    offset = finite_number(context.get('metric_customs_delay_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_customs_delay_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('service_id', 'user_group', 'resource_load', 'capacity_units'), 13)
    weight = finite_number(context.get('customs_delay_weight', 0.7))
    offset = finite_number(context.get('metric_customs_delay_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_customs_delay_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('region_code', 'response_ms', 'error_rate', 'priority'), 14)
    weight = finite_number(context.get('customs_delay_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_customs_delay_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_reroute_cost_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('request_queue', 'support_status', 'event_sequence', 'access_tier'), 6)
    weight = finite_number(context.get('reroute_cost_weight', 0.7))
    offset = finite_number(context.get('metric_reroute_cost_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_reroute_cost_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_load', 'capacity_units', 'service_id', 'user_group'), 7)
    weight = finite_number(context.get('reroute_cost_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_reroute_cost_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_reroute_cost_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('error_rate', 'priority', 'region_code', 'response_ms'), 8)
    weight = finite_number(context.get('reroute_cost_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_reroute_cost_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_reroute_cost_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('support_status', 'event_sequence', 'access_tier', 'request_queue'), 9)
    weight = finite_number(context.get('reroute_cost_weight', 1.0))
    offset = finite_number(context.get('metric_reroute_cost_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_reroute_cost_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capacity_units', 'service_id', 'user_group', 'resource_load'), 10)
    weight = finite_number(context.get('reroute_cost_weight', 0.7))
    offset = finite_number(context.get('metric_reroute_cost_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_reroute_cost_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('priority', 'region_code', 'response_ms', 'error_rate'), 11)
    weight = finite_number(context.get('reroute_cost_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_reroute_cost_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_reroute_cost_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('event_sequence', 'access_tier', 'request_queue', 'support_status'), 12)
    weight = finite_number(context.get('reroute_cost_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_reroute_cost_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_reroute_cost_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('service_id', 'user_group', 'resource_load', 'capacity_units'), 13)
    weight = finite_number(context.get('reroute_cost_weight', 1.0))
    offset = finite_number(context.get('metric_reroute_cost_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_reroute_cost_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('region_code', 'response_ms', 'error_rate', 'priority'), 14)
    weight = finite_number(context.get('reroute_cost_weight', 0.7))
    offset = finite_number(context.get('metric_reroute_cost_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_reroute_cost_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('access_tier', 'request_queue', 'support_status', 'event_sequence'), 15)
    weight = finite_number(context.get('reroute_cost_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_reroute_cost_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_sla_exposure_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_load', 'capacity_units', 'service_id', 'user_group'), 7)
    weight = finite_number(context.get('sla_exposure_weight', 0.7))
    offset = finite_number(context.get('metric_sla_exposure_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_sla_exposure_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('error_rate', 'priority', 'region_code', 'response_ms'), 8)
    weight = finite_number(context.get('sla_exposure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_sla_exposure_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_sla_exposure_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('support_status', 'event_sequence', 'access_tier', 'request_queue'), 9)
    weight = finite_number(context.get('sla_exposure_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_sla_exposure_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_sla_exposure_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capacity_units', 'service_id', 'user_group', 'resource_load'), 10)
    weight = finite_number(context.get('sla_exposure_weight', 1.0))
    offset = finite_number(context.get('metric_sla_exposure_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_sla_exposure_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('priority', 'region_code', 'response_ms', 'error_rate'), 11)
    weight = finite_number(context.get('sla_exposure_weight', 0.7))
    offset = finite_number(context.get('metric_sla_exposure_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_sla_exposure_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('event_sequence', 'access_tier', 'request_queue', 'support_status'), 12)
    weight = finite_number(context.get('sla_exposure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_sla_exposure_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_sla_exposure_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('service_id', 'user_group', 'resource_load', 'capacity_units'), 13)
    weight = finite_number(context.get('sla_exposure_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_sla_exposure_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_sla_exposure_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('region_code', 'response_ms', 'error_rate', 'priority'), 14)
    weight = finite_number(context.get('sla_exposure_weight', 1.0))
    offset = finite_number(context.get('metric_sla_exposure_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_sla_exposure_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('access_tier', 'request_queue', 'support_status', 'event_sequence'), 15)
    weight = finite_number(context.get('sla_exposure_weight', 0.7))
    offset = finite_number(context.get('metric_sla_exposure_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_sla_exposure_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('user_group', 'resource_load', 'capacity_units', 'service_id'), 16)
    weight = finite_number(context.get('sla_exposure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_sla_exposure_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_capacity_resilience_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('error_rate', 'priority', 'region_code', 'response_ms'), 8)
    weight = finite_number(context.get('capacity_resilience_weight', 0.7))
    offset = finite_number(context.get('metric_capacity_resilience_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_capacity_resilience_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('support_status', 'event_sequence', 'access_tier', 'request_queue'), 9)
    weight = finite_number(context.get('capacity_resilience_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_capacity_resilience_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_capacity_resilience_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('capacity_units', 'service_id', 'user_group', 'resource_load'), 10)
    weight = finite_number(context.get('capacity_resilience_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_capacity_resilience_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_capacity_resilience_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('priority', 'region_code', 'response_ms', 'error_rate'), 11)
    weight = finite_number(context.get('capacity_resilience_weight', 1.0))
    offset = finite_number(context.get('metric_capacity_resilience_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_capacity_resilience_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('event_sequence', 'access_tier', 'request_queue', 'support_status'), 12)
    weight = finite_number(context.get('capacity_resilience_weight', 0.7))
    offset = finite_number(context.get('metric_capacity_resilience_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_capacity_resilience_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('service_id', 'user_group', 'resource_load', 'capacity_units'), 13)
    weight = finite_number(context.get('capacity_resilience_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_capacity_resilience_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_capacity_resilience_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('region_code', 'response_ms', 'error_rate', 'priority'), 14)
    weight = finite_number(context.get('capacity_resilience_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_capacity_resilience_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_capacity_resilience_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('access_tier', 'request_queue', 'support_status', 'event_sequence'), 15)
    weight = finite_number(context.get('capacity_resilience_weight', 1.0))
    offset = finite_number(context.get('metric_capacity_resilience_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_capacity_resilience_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('user_group', 'resource_load', 'capacity_units', 'service_id'), 16)
    weight = finite_number(context.get('capacity_resilience_weight', 0.7))
    offset = finite_number(context.get('metric_capacity_resilience_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_capacity_resilience_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('response_ms', 'error_rate', 'priority', 'region_code'), 17)
    weight = finite_number(context.get('capacity_resilience_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_capacity_resilience_10_offset', 0.1))
    return bounded(base * weight + offset)

METRICS: dict[str, MetricFunction] = {
    'metric_route_pressure_01': metric_route_pressure_01,
    'metric_route_pressure_02': metric_route_pressure_02,
    'metric_route_pressure_03': metric_route_pressure_03,
    'metric_route_pressure_04': metric_route_pressure_04,
    'metric_route_pressure_05': metric_route_pressure_05,
    'metric_route_pressure_06': metric_route_pressure_06,
    'metric_route_pressure_07': metric_route_pressure_07,
    'metric_route_pressure_08': metric_route_pressure_08,
    'metric_route_pressure_09': metric_route_pressure_09,
    'metric_route_pressure_10': metric_route_pressure_10,
    'metric_eta_reliability_01': metric_eta_reliability_01,
    'metric_eta_reliability_02': metric_eta_reliability_02,
    'metric_eta_reliability_03': metric_eta_reliability_03,
    'metric_eta_reliability_04': metric_eta_reliability_04,
    'metric_eta_reliability_05': metric_eta_reliability_05,
    'metric_eta_reliability_06': metric_eta_reliability_06,
    'metric_eta_reliability_07': metric_eta_reliability_07,
    'metric_eta_reliability_08': metric_eta_reliability_08,
    'metric_eta_reliability_09': metric_eta_reliability_09,
    'metric_eta_reliability_10': metric_eta_reliability_10,
    'metric_capacity_balance_01': metric_capacity_balance_01,
    'metric_capacity_balance_02': metric_capacity_balance_02,
    'metric_capacity_balance_03': metric_capacity_balance_03,
    'metric_capacity_balance_04': metric_capacity_balance_04,
    'metric_capacity_balance_05': metric_capacity_balance_05,
    'metric_capacity_balance_06': metric_capacity_balance_06,
    'metric_capacity_balance_07': metric_capacity_balance_07,
    'metric_capacity_balance_08': metric_capacity_balance_08,
    'metric_capacity_balance_09': metric_capacity_balance_09,
    'metric_capacity_balance_10': metric_capacity_balance_10,
    'metric_cold_chain_risk_01': metric_cold_chain_risk_01,
    'metric_cold_chain_risk_02': metric_cold_chain_risk_02,
    'metric_cold_chain_risk_03': metric_cold_chain_risk_03,
    'metric_cold_chain_risk_04': metric_cold_chain_risk_04,
    'metric_cold_chain_risk_05': metric_cold_chain_risk_05,
    'metric_cold_chain_risk_06': metric_cold_chain_risk_06,
    'metric_cold_chain_risk_07': metric_cold_chain_risk_07,
    'metric_cold_chain_risk_08': metric_cold_chain_risk_08,
    'metric_cold_chain_risk_09': metric_cold_chain_risk_09,
    'metric_cold_chain_risk_10': metric_cold_chain_risk_10,
    'metric_customs_delay_01': metric_customs_delay_01,
    'metric_customs_delay_02': metric_customs_delay_02,
    'metric_customs_delay_03': metric_customs_delay_03,
    'metric_customs_delay_04': metric_customs_delay_04,
    'metric_customs_delay_05': metric_customs_delay_05,
    'metric_customs_delay_06': metric_customs_delay_06,
    'metric_customs_delay_07': metric_customs_delay_07,
    'metric_customs_delay_08': metric_customs_delay_08,
    'metric_customs_delay_09': metric_customs_delay_09,
    'metric_customs_delay_10': metric_customs_delay_10,
    'metric_reroute_cost_01': metric_reroute_cost_01,
    'metric_reroute_cost_02': metric_reroute_cost_02,
    'metric_reroute_cost_03': metric_reroute_cost_03,
    'metric_reroute_cost_04': metric_reroute_cost_04,
    'metric_reroute_cost_05': metric_reroute_cost_05,
    'metric_reroute_cost_06': metric_reroute_cost_06,
    'metric_reroute_cost_07': metric_reroute_cost_07,
    'metric_reroute_cost_08': metric_reroute_cost_08,
    'metric_reroute_cost_09': metric_reroute_cost_09,
    'metric_reroute_cost_10': metric_reroute_cost_10,
    'metric_sla_exposure_01': metric_sla_exposure_01,
    'metric_sla_exposure_02': metric_sla_exposure_02,
    'metric_sla_exposure_03': metric_sla_exposure_03,
    'metric_sla_exposure_04': metric_sla_exposure_04,
    'metric_sla_exposure_05': metric_sla_exposure_05,
    'metric_sla_exposure_06': metric_sla_exposure_06,
    'metric_sla_exposure_07': metric_sla_exposure_07,
    'metric_sla_exposure_08': metric_sla_exposure_08,
    'metric_sla_exposure_09': metric_sla_exposure_09,
    'metric_sla_exposure_10': metric_sla_exposure_10,
    'metric_capacity_resilience_01': metric_capacity_resilience_01,
    'metric_capacity_resilience_02': metric_capacity_resilience_02,
    'metric_capacity_resilience_03': metric_capacity_resilience_03,
    'metric_capacity_resilience_04': metric_capacity_resilience_04,
    'metric_capacity_resilience_05': metric_capacity_resilience_05,
    'metric_capacity_resilience_06': metric_capacity_resilience_06,
    'metric_capacity_resilience_07': metric_capacity_resilience_07,
    'metric_capacity_resilience_08': metric_capacity_resilience_08,
    'metric_capacity_resilience_09': metric_capacity_resilience_09,
    'metric_capacity_resilience_10': metric_capacity_resilience_10,
}

def metric_vector(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, float]:
    context = context or {}
    return {name: function(record, context) for name, function in METRICS.items()}

def grouped_metrics(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, float]:
    vector = metric_vector(record, context)
    groups: dict[str, list[float]] = defaultdict(list)
    for name, value in vector.items():
        key = name.rsplit('_', 1)[0].removeprefix('metric_')
        groups[key].append(value)
    return {key: statistics.fmean(values) for key, values in groups.items()}

def record_score(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    rules = evaluate(record, context)
    rule_summary = summarize(rules)
    metrics = grouped_metrics(record, context)
    metric_score = statistics.fmean(metrics.values()) if metrics else 0.0
    combined = bounded(rule_summary['score'] * 0.55 + metric_score * 0.45)
    return {'score': combined, 'rule_summary': rule_summary, 'metrics': metrics,
            'fingerprint': stable_hash({'record': record.fingerprint, 'metrics': metrics, 'rules': rule_summary})}

def portfolio(records: Iterable[DomainRecord], context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    rows = [record_score(record, context) | {'record_id': record.record_id} for record in records]
    if not rows:
        return {'count': 0, 'average': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'rows': []}
    scores = [row['score'] for row in rows]
    return {'count': len(rows), 'average': statistics.fmean(scores),
            'minimum': min(scores), 'maximum': max(scores), 'rows': sorted(rows, key=lambda row: (-row['score'], row['record_id']))}

def compare(left: DomainRecord, right: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    left_metrics = grouped_metrics(left, context)
    right_metrics = grouped_metrics(right, context)
    delta = {key: right_metrics.get(key, 0.0) - left_metrics.get(key, 0.0) for key in sorted(set(left_metrics) | set(right_metrics))}
    return {'left': left.record_id, 'right': right.record_id, 'delta': delta,
            'winner': right.record_id if sum(delta.values()) >= 0 else left.record_id}
