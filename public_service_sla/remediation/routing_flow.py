from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from public_service_sla.telemetry.service_event import ContractError, Decision, DomainRecord, RuleResult, bounded
from public_service_sla.scenarios.outage_simulator import grouped_metrics, record_score
from public_service_sla.capacity.routing_rules import evaluate

STATES = ['onboarded', 'serving', 'degraded', 'remediating', 'certified', 'retired']
TRANSITIONS = {ledger: tuple(STATES[i + 1:i + 3]) for i, ledger in enumerate(STATES)}

@dataclass(frozen=True)
class TransitionPlan:
    from_ledger: str
    to_ledger: str
    allowed: bool
    reasons: tuple[str, ...]
    score: float

def allowed_targets(ledger: str) -> tuple[str, ...]:
    if ledger not in TRANSITIONS:
        raise ContractError('unknown workflow ledger')
    return TRANSITIONS[ledger]

def plan_transition(record: DomainRecord, target: str, context: Mapping[str, Any] | None = None) -> TransitionPlan:
    context = context or {}
    if target not in STATES:
        raise ContractError('unknown target ledger')
    scorecard = record_score(record, context)
    reasons: list[str] = []
    structurally_allowed = target in allowed_targets(record.ledger)
    if not structurally_allowed:
        reasons.append('transition is not adjacent in the lifecycle')
    threshold = float(context.get('transition_threshold', 0.42))
    if scorecard['score'] < threshold:
        reasons.append('record score is below the transition threshold')
    return TransitionPlan(record.ledger, target, structurally_allowed and not reasons, tuple(reasons or ['eligible']), scorecard['score'])

def apply_transition(record: DomainRecord, target: str, context: Mapping[str, Any] | None = None) -> DomainRecord:
    plan = plan_transition(record, target, context)
    if not plan.allowed:
        raise ContractError('; '.join(plan.reasons))
    return record.with_ledger(target)

def guard_service_id_route_pressure_01(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_service_id_route_pressure_01_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_service_id_route_pressure_01' + (':passed' if allowed else ':blocked')

def guard_region_code_eta_reliability_02(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_region_code_eta_reliability_02_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_region_code_eta_reliability_02' + (':passed' if allowed else ':blocked')

def guard_access_tier_capacity_balance_03(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_access_tier_capacity_balance_03_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_access_tier_capacity_balance_03' + (':passed' if allowed else ':blocked')

def guard_user_group_cold_chain_risk_04(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_user_group_cold_chain_risk_04_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_user_group_cold_chain_risk_04' + (':passed' if allowed else ':blocked')

def guard_response_ms_customs_delay_05(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_response_ms_customs_delay_05_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_response_ms_customs_delay_05' + (':passed' if allowed else ':blocked')

def guard_request_queue_reroute_cost_06(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_request_queue_reroute_cost_06_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_request_queue_reroute_cost_06' + (':passed' if allowed else ':blocked')

def guard_resource_load_sla_exposure_07(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_resource_load_sla_exposure_07_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_load_sla_exposure_07' + (':passed' if allowed else ':blocked')

def guard_error_rate_capacity_resilience_08(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_error_rate_capacity_resilience_08_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_error_rate_capacity_resilience_08' + (':passed' if allowed else ':blocked')

def guard_support_status_route_pressure_09(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_support_status_route_pressure_09_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_support_status_route_pressure_09' + (':passed' if allowed else ':blocked')

def guard_capacity_units_eta_reliability_10(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_capacity_units_eta_reliability_10_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_capacity_units_eta_reliability_10' + (':passed' if allowed else ':blocked')

def guard_priority_capacity_balance_11(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_priority_capacity_balance_11_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_priority_capacity_balance_11' + (':passed' if allowed else ':blocked')

def guard_event_sequence_cold_chain_risk_12(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_event_sequence_cold_chain_risk_12_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_event_sequence_cold_chain_risk_12' + (':passed' if allowed else ':blocked')

def guard_service_id_customs_delay_13(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_service_id_customs_delay_13_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_service_id_customs_delay_13' + (':passed' if allowed else ':blocked')

def guard_region_code_reroute_cost_14(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_region_code_reroute_cost_14_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_region_code_reroute_cost_14' + (':passed' if allowed else ':blocked')

def guard_access_tier_sla_exposure_15(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_access_tier_sla_exposure_15_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_access_tier_sla_exposure_15' + (':passed' if allowed else ':blocked')

def guard_user_group_capacity_resilience_16(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_user_group_capacity_resilience_16_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_user_group_capacity_resilience_16' + (':passed' if allowed else ':blocked')

def guard_response_ms_route_pressure_17(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_response_ms_route_pressure_17_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_response_ms_route_pressure_17' + (':passed' if allowed else ':blocked')

def guard_request_queue_eta_reliability_18(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_request_queue_eta_reliability_18_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_request_queue_eta_reliability_18' + (':passed' if allowed else ':blocked')

def guard_resource_load_capacity_balance_19(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_resource_load_capacity_balance_19_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_load_capacity_balance_19' + (':passed' if allowed else ':blocked')

def guard_error_rate_cold_chain_risk_20(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_error_rate_cold_chain_risk_20_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_error_rate_cold_chain_risk_20' + (':passed' if allowed else ':blocked')

def guard_support_status_customs_delay_21(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_support_status_customs_delay_21_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_support_status_customs_delay_21' + (':passed' if allowed else ':blocked')

def guard_capacity_units_reroute_cost_22(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_capacity_units_reroute_cost_22_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_capacity_units_reroute_cost_22' + (':passed' if allowed else ':blocked')

def guard_priority_sla_exposure_23(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_priority_sla_exposure_23_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_priority_sla_exposure_23' + (':passed' if allowed else ':blocked')

def guard_event_sequence_capacity_resilience_24(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_event_sequence_capacity_resilience_24_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_event_sequence_capacity_resilience_24' + (':passed' if allowed else ':blocked')

def guard_service_id_route_pressure_25(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_service_id_route_pressure_25_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_service_id_route_pressure_25' + (':passed' if allowed else ':blocked')

def guard_region_code_eta_reliability_26(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_region_code_eta_reliability_26_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_region_code_eta_reliability_26' + (':passed' if allowed else ':blocked')

def guard_access_tier_capacity_balance_27(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_access_tier_capacity_balance_27_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_access_tier_capacity_balance_27' + (':passed' if allowed else ':blocked')

def guard_user_group_cold_chain_risk_28(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_user_group_cold_chain_risk_28_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_user_group_cold_chain_risk_28' + (':passed' if allowed else ':blocked')

def guard_response_ms_customs_delay_29(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_response_ms_customs_delay_29_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_response_ms_customs_delay_29' + (':passed' if allowed else ':blocked')

def guard_request_queue_reroute_cost_30(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_request_queue_reroute_cost_30_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_request_queue_reroute_cost_30' + (':passed' if allowed else ':blocked')

def guard_resource_load_sla_exposure_31(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_resource_load_sla_exposure_31_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_load_sla_exposure_31' + (':passed' if allowed else ':blocked')

def guard_error_rate_capacity_resilience_32(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_error_rate_capacity_resilience_32_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_error_rate_capacity_resilience_32' + (':passed' if allowed else ':blocked')

def guard_support_status_route_pressure_33(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_support_status_route_pressure_33_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_support_status_route_pressure_33' + (':passed' if allowed else ':blocked')

def guard_capacity_units_eta_reliability_34(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_capacity_units_eta_reliability_34_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_capacity_units_eta_reliability_34' + (':passed' if allowed else ':blocked')

def guard_priority_capacity_balance_35(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_priority_capacity_balance_35_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_priority_capacity_balance_35' + (':passed' if allowed else ':blocked')

def guard_event_sequence_cold_chain_risk_36(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_event_sequence_cold_chain_risk_36_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_event_sequence_cold_chain_risk_36' + (':passed' if allowed else ':blocked')

def guard_service_id_customs_delay_37(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_service_id_customs_delay_37_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_service_id_customs_delay_37' + (':passed' if allowed else ':blocked')

def guard_region_code_reroute_cost_38(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_region_code_reroute_cost_38_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_region_code_reroute_cost_38' + (':passed' if allowed else ':blocked')

def guard_access_tier_sla_exposure_39(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_access_tier_sla_exposure_39_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_access_tier_sla_exposure_39' + (':passed' if allowed else ':blocked')

def guard_user_group_capacity_resilience_40(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_user_group_capacity_resilience_40_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_user_group_capacity_resilience_40' + (':passed' if allowed else ':blocked')

def guard_response_ms_route_pressure_41(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_response_ms_route_pressure_41_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_response_ms_route_pressure_41' + (':passed' if allowed else ':blocked')

def guard_request_queue_eta_reliability_42(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_request_queue_eta_reliability_42_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_request_queue_eta_reliability_42' + (':passed' if allowed else ':blocked')

def guard_resource_load_capacity_balance_43(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_resource_load_capacity_balance_43_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_load_capacity_balance_43' + (':passed' if allowed else ':blocked')

def guard_error_rate_cold_chain_risk_44(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_error_rate_cold_chain_risk_44_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_error_rate_cold_chain_risk_44' + (':passed' if allowed else ':blocked')

def guard_support_status_customs_delay_45(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_support_status_customs_delay_45_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_support_status_customs_delay_45' + (':passed' if allowed else ':blocked')

def guard_capacity_units_reroute_cost_46(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_capacity_units_reroute_cost_46_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_capacity_units_reroute_cost_46' + (':passed' if allowed else ':blocked')

def guard_priority_sla_exposure_47(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_priority_sla_exposure_47_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_priority_sla_exposure_47' + (':passed' if allowed else ':blocked')

def guard_event_sequence_capacity_resilience_48(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_event_sequence_capacity_resilience_48_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_event_sequence_capacity_resilience_48' + (':passed' if allowed else ':blocked')

def guard_service_id_route_pressure_49(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_service_id_route_pressure_49_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_service_id_route_pressure_49' + (':passed' if allowed else ':blocked')

def guard_region_code_eta_reliability_50(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_region_code_eta_reliability_50_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_region_code_eta_reliability_50' + (':passed' if allowed else ':blocked')

def guard_access_tier_capacity_balance_51(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_access_tier_capacity_balance_51_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_access_tier_capacity_balance_51' + (':passed' if allowed else ':blocked')

def guard_user_group_cold_chain_risk_52(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_user_group_cold_chain_risk_52_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_user_group_cold_chain_risk_52' + (':passed' if allowed else ':blocked')

def guard_response_ms_customs_delay_53(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_response_ms_customs_delay_53_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_response_ms_customs_delay_53' + (':passed' if allowed else ':blocked')

def guard_request_queue_reroute_cost_54(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_request_queue_reroute_cost_54_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_request_queue_reroute_cost_54' + (':passed' if allowed else ':blocked')

def guard_resource_load_sla_exposure_55(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_resource_load_sla_exposure_55_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_load_sla_exposure_55' + (':passed' if allowed else ':blocked')

def guard_error_rate_capacity_resilience_56(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_error_rate_capacity_resilience_56_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_error_rate_capacity_resilience_56' + (':passed' if allowed else ':blocked')

def guard_support_status_route_pressure_57(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_support_status_route_pressure_57_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_support_status_route_pressure_57' + (':passed' if allowed else ':blocked')

def guard_capacity_units_eta_reliability_58(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_capacity_units_eta_reliability_58_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_capacity_units_eta_reliability_58' + (':passed' if allowed else ':blocked')

def guard_priority_capacity_balance_59(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_priority_capacity_balance_59_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_priority_capacity_balance_59' + (':passed' if allowed else ':blocked')

def guard_event_sequence_cold_chain_risk_60(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_event_sequence_cold_chain_risk_60_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_event_sequence_cold_chain_risk_60' + (':passed' if allowed else ':blocked')

def guard_service_id_customs_delay_61(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_service_id_customs_delay_61_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_service_id_customs_delay_61' + (':passed' if allowed else ':blocked')

def guard_region_code_reroute_cost_62(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_region_code_reroute_cost_62_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_region_code_reroute_cost_62' + (':passed' if allowed else ':blocked')

def guard_access_tier_sla_exposure_63(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_access_tier_sla_exposure_63_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_access_tier_sla_exposure_63' + (':passed' if allowed else ':blocked')

def guard_user_group_capacity_resilience_64(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_user_group_capacity_resilience_64_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_user_group_capacity_resilience_64' + (':passed' if allowed else ':blocked')

def guard_response_ms_route_pressure_65(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_response_ms_route_pressure_65_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_response_ms_route_pressure_65' + (':passed' if allowed else ':blocked')

def guard_request_queue_eta_reliability_66(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_request_queue_eta_reliability_66_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_request_queue_eta_reliability_66' + (':passed' if allowed else ':blocked')

def guard_resource_load_capacity_balance_67(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_resource_load_capacity_balance_67_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_load_capacity_balance_67' + (':passed' if allowed else ':blocked')

def guard_error_rate_cold_chain_risk_68(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_error_rate_cold_chain_risk_68_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_error_rate_cold_chain_risk_68' + (':passed' if allowed else ':blocked')

def guard_support_status_customs_delay_69(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_support_status_customs_delay_69_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_support_status_customs_delay_69' + (':passed' if allowed else ':blocked')

def guard_capacity_units_reroute_cost_70(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_capacity_units_reroute_cost_70_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_capacity_units_reroute_cost_70' + (':passed' if allowed else ':blocked')

def guard_priority_sla_exposure_71(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_priority_sla_exposure_71_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_priority_sla_exposure_71' + (':passed' if allowed else ':blocked')

def guard_event_sequence_capacity_resilience_72(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_event_sequence_capacity_resilience_72_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_event_sequence_capacity_resilience_72' + (':passed' if allowed else ':blocked')

def guard_service_id_route_pressure_73(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_service_id_route_pressure_73_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_service_id_route_pressure_73' + (':passed' if allowed else ':blocked')

def guard_region_code_eta_reliability_74(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_region_code_eta_reliability_74_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_region_code_eta_reliability_74' + (':passed' if allowed else ':blocked')

def guard_access_tier_capacity_balance_75(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_access_tier_capacity_balance_75_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_access_tier_capacity_balance_75' + (':passed' if allowed else ':blocked')

def guard_user_group_cold_chain_risk_76(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_user_group_cold_chain_risk_76_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_user_group_cold_chain_risk_76' + (':passed' if allowed else ':blocked')

def guard_response_ms_customs_delay_77(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_response_ms_customs_delay_77_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_response_ms_customs_delay_77' + (':passed' if allowed else ':blocked')

def guard_request_queue_reroute_cost_78(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_request_queue_reroute_cost_78_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_request_queue_reroute_cost_78' + (':passed' if allowed else ':blocked')

def guard_resource_load_sla_exposure_79(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_resource_load_sla_exposure_79_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_load_sla_exposure_79' + (':passed' if allowed else ':blocked')

def guard_error_rate_capacity_resilience_80(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_error_rate_capacity_resilience_80_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_error_rate_capacity_resilience_80' + (':passed' if allowed else ':blocked')

def guard_support_status_route_pressure_81(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_support_status_route_pressure_81_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_support_status_route_pressure_81' + (':passed' if allowed else ':blocked')

def guard_capacity_units_eta_reliability_82(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_capacity_units_eta_reliability_82_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_capacity_units_eta_reliability_82' + (':passed' if allowed else ':blocked')

def guard_priority_capacity_balance_83(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_priority_capacity_balance_83_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_priority_capacity_balance_83' + (':passed' if allowed else ':blocked')

def guard_event_sequence_cold_chain_risk_84(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_event_sequence_cold_chain_risk_84_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_event_sequence_cold_chain_risk_84' + (':passed' if allowed else ':blocked')

def guard_service_id_customs_delay_85(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_service_id_customs_delay_85_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_service_id_customs_delay_85' + (':passed' if allowed else ':blocked')

def guard_region_code_reroute_cost_86(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_region_code_reroute_cost_86_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_region_code_reroute_cost_86' + (':passed' if allowed else ':blocked')

def guard_access_tier_sla_exposure_87(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_access_tier_sla_exposure_87_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_access_tier_sla_exposure_87' + (':passed' if allowed else ':blocked')

def guard_user_group_capacity_resilience_88(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_user_group_capacity_resilience_88_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_user_group_capacity_resilience_88' + (':passed' if allowed else ':blocked')

def guard_response_ms_route_pressure_89(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_response_ms_route_pressure_89_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_response_ms_route_pressure_89' + (':passed' if allowed else ':blocked')

def guard_request_queue_eta_reliability_90(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_request_queue_eta_reliability_90_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_request_queue_eta_reliability_90' + (':passed' if allowed else ':blocked')

def guard_resource_load_capacity_balance_91(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_resource_load_capacity_balance_91_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_load_capacity_balance_91' + (':passed' if allowed else ':blocked')

def guard_error_rate_cold_chain_risk_92(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_error_rate_cold_chain_risk_92_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_error_rate_cold_chain_risk_92' + (':passed' if allowed else ':blocked')

def guard_support_status_customs_delay_93(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_support_status_customs_delay_93_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_support_status_customs_delay_93' + (':passed' if allowed else ':blocked')

def guard_capacity_units_reroute_cost_94(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_capacity_units_reroute_cost_94_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_capacity_units_reroute_cost_94' + (':passed' if allowed else ':blocked')

def guard_priority_sla_exposure_95(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_priority_sla_exposure_95_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_priority_sla_exposure_95' + (':passed' if allowed else ':blocked')

def guard_event_sequence_capacity_resilience_96(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_event_sequence_capacity_resilience_96_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_event_sequence_capacity_resilience_96' + (':passed' if allowed else ':blocked')

def guard_service_id_route_pressure_97(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_service_id_route_pressure_97_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_service_id_route_pressure_97' + (':passed' if allowed else ':blocked')

def guard_region_code_eta_reliability_98(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_region_code_eta_reliability_98_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_region_code_eta_reliability_98' + (':passed' if allowed else ':blocked')

def guard_access_tier_capacity_balance_99(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_access_tier_capacity_balance_99_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_access_tier_capacity_balance_99' + (':passed' if allowed else ':blocked')

def guard_user_group_cold_chain_risk_100(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_user_group_cold_chain_risk_100_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_user_group_cold_chain_risk_100' + (':passed' if allowed else ':blocked')

def guard_response_ms_customs_delay_101(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_response_ms_customs_delay_101_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_response_ms_customs_delay_101' + (':passed' if allowed else ':blocked')

def guard_request_queue_reroute_cost_102(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_request_queue_reroute_cost_102_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_request_queue_reroute_cost_102' + (':passed' if allowed else ':blocked')

def guard_resource_load_sla_exposure_103(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_resource_load_sla_exposure_103_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_load_sla_exposure_103' + (':passed' if allowed else ':blocked')

def guard_error_rate_capacity_resilience_104(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_error_rate_capacity_resilience_104_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_error_rate_capacity_resilience_104' + (':passed' if allowed else ':blocked')

def guard_support_status_route_pressure_105(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_support_status_route_pressure_105_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_support_status_route_pressure_105' + (':passed' if allowed else ':blocked')

def guard_capacity_units_eta_reliability_106(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_capacity_units_eta_reliability_106_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_capacity_units_eta_reliability_106' + (':passed' if allowed else ':blocked')

def guard_priority_capacity_balance_107(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_priority_capacity_balance_107_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_priority_capacity_balance_107' + (':passed' if allowed else ':blocked')

def guard_event_sequence_cold_chain_risk_108(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_event_sequence_cold_chain_risk_108_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_event_sequence_cold_chain_risk_108' + (':passed' if allowed else ':blocked')

def guard_service_id_customs_delay_109(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_service_id_customs_delay_109_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_service_id_customs_delay_109' + (':passed' if allowed else ':blocked')

def guard_region_code_reroute_cost_110(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_region_code_reroute_cost_110_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_region_code_reroute_cost_110' + (':passed' if allowed else ':blocked')

def guard_access_tier_sla_exposure_111(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_access_tier_sla_exposure_111_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_access_tier_sla_exposure_111' + (':passed' if allowed else ':blocked')

def guard_user_group_capacity_resilience_112(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_user_group_capacity_resilience_112_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_user_group_capacity_resilience_112' + (':passed' if allowed else ':blocked')

def guard_response_ms_route_pressure_113(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('route_pressure', 0.0)
    floor = float(context.get('guard_response_ms_route_pressure_113_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_response_ms_route_pressure_113' + (':passed' if allowed else ':blocked')

def guard_request_queue_eta_reliability_114(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('eta_reliability', 0.0)
    floor = float(context.get('guard_request_queue_eta_reliability_114_floor', 0.32))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_request_queue_eta_reliability_114' + (':passed' if allowed else ':blocked')

def guard_resource_load_capacity_balance_115(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_balance', 0.0)
    floor = float(context.get('guard_resource_load_capacity_balance_115_floor', 0.39))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_load_capacity_balance_115' + (':passed' if allowed else ':blocked')

def guard_error_rate_cold_chain_risk_116(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('cold_chain_risk', 0.0)
    floor = float(context.get('guard_error_rate_cold_chain_risk_116_floor', 0.46))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('serving')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_error_rate_cold_chain_risk_116' + (':passed' if allowed else ':blocked')

def guard_support_status_customs_delay_117(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('customs_delay', 0.0)
    floor = float(context.get('guard_support_status_customs_delay_117_floor', 0.53))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('degraded')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_support_status_customs_delay_117' + (':passed' if allowed else ':blocked')

def guard_capacity_units_reroute_cost_118(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('reroute_cost', 0.0)
    floor = float(context.get('guard_capacity_units_reroute_cost_118_floor', 0.6000000000000001))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('remediating')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_capacity_units_reroute_cost_118' + (':passed' if allowed else ':blocked')

def guard_priority_sla_exposure_119(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('sla_exposure', 0.0)
    floor = float(context.get('guard_priority_sla_exposure_119_floor', 0.67))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('certified')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_priority_sla_exposure_119' + (':passed' if allowed else ':blocked')

def guard_event_sequence_capacity_resilience_120(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_resilience', 0.0)
    floor = float(context.get('guard_event_sequence_capacity_resilience_120_floor', 0.25))
    ledger_ok = STATES.index(record.ledger) <= STATES.index('retired')
    allowed = ledger_ok and value >= min(1.0, floor)
    return allowed, 'guard_event_sequence_capacity_resilience_120' + (':passed' if allowed else ':blocked')

GUARDS: tuple[Callable[[DomainRecord, Mapping[str, Any]], tuple[bool, str]], ...] = (
    guard_service_id_route_pressure_01,
    guard_region_code_eta_reliability_02,
    guard_access_tier_capacity_balance_03,
    guard_user_group_cold_chain_risk_04,
    guard_response_ms_customs_delay_05,
    guard_request_queue_reroute_cost_06,
    guard_resource_load_sla_exposure_07,
    guard_error_rate_capacity_resilience_08,
    guard_support_status_route_pressure_09,
    guard_capacity_units_eta_reliability_10,
    guard_priority_capacity_balance_11,
    guard_event_sequence_cold_chain_risk_12,
    guard_service_id_customs_delay_13,
    guard_region_code_reroute_cost_14,
    guard_access_tier_sla_exposure_15,
    guard_user_group_capacity_resilience_16,
    guard_response_ms_route_pressure_17,
    guard_request_queue_eta_reliability_18,
    guard_resource_load_capacity_balance_19,
    guard_error_rate_cold_chain_risk_20,
    guard_support_status_customs_delay_21,
    guard_capacity_units_reroute_cost_22,
    guard_priority_sla_exposure_23,
    guard_event_sequence_capacity_resilience_24,
    guard_service_id_route_pressure_25,
    guard_region_code_eta_reliability_26,
    guard_access_tier_capacity_balance_27,
    guard_user_group_cold_chain_risk_28,
    guard_response_ms_customs_delay_29,
    guard_request_queue_reroute_cost_30,
    guard_resource_load_sla_exposure_31,
    guard_error_rate_capacity_resilience_32,
    guard_support_status_route_pressure_33,
    guard_capacity_units_eta_reliability_34,
    guard_priority_capacity_balance_35,
    guard_event_sequence_cold_chain_risk_36,
    guard_service_id_customs_delay_37,
    guard_region_code_reroute_cost_38,
    guard_access_tier_sla_exposure_39,
    guard_user_group_capacity_resilience_40,
    guard_response_ms_route_pressure_41,
    guard_request_queue_eta_reliability_42,
    guard_resource_load_capacity_balance_43,
    guard_error_rate_cold_chain_risk_44,
    guard_support_status_customs_delay_45,
    guard_capacity_units_reroute_cost_46,
    guard_priority_sla_exposure_47,
    guard_event_sequence_capacity_resilience_48,
    guard_service_id_route_pressure_49,
    guard_region_code_eta_reliability_50,
    guard_access_tier_capacity_balance_51,
    guard_user_group_cold_chain_risk_52,
    guard_response_ms_customs_delay_53,
    guard_request_queue_reroute_cost_54,
    guard_resource_load_sla_exposure_55,
    guard_error_rate_capacity_resilience_56,
    guard_support_status_route_pressure_57,
    guard_capacity_units_eta_reliability_58,
    guard_priority_capacity_balance_59,
    guard_event_sequence_cold_chain_risk_60,
    guard_service_id_customs_delay_61,
    guard_region_code_reroute_cost_62,
    guard_access_tier_sla_exposure_63,
    guard_user_group_capacity_resilience_64,
    guard_response_ms_route_pressure_65,
    guard_request_queue_eta_reliability_66,
    guard_resource_load_capacity_balance_67,
    guard_error_rate_cold_chain_risk_68,
    guard_support_status_customs_delay_69,
    guard_capacity_units_reroute_cost_70,
    guard_priority_sla_exposure_71,
    guard_event_sequence_capacity_resilience_72,
    guard_service_id_route_pressure_73,
    guard_region_code_eta_reliability_74,
    guard_access_tier_capacity_balance_75,
    guard_user_group_cold_chain_risk_76,
    guard_response_ms_customs_delay_77,
    guard_request_queue_reroute_cost_78,
    guard_resource_load_sla_exposure_79,
    guard_error_rate_capacity_resilience_80,
    guard_support_status_route_pressure_81,
    guard_capacity_units_eta_reliability_82,
    guard_priority_capacity_balance_83,
    guard_event_sequence_cold_chain_risk_84,
    guard_service_id_customs_delay_85,
    guard_region_code_reroute_cost_86,
    guard_access_tier_sla_exposure_87,
    guard_user_group_capacity_resilience_88,
    guard_response_ms_route_pressure_89,
    guard_request_queue_eta_reliability_90,
    guard_resource_load_capacity_balance_91,
    guard_error_rate_cold_chain_risk_92,
    guard_support_status_customs_delay_93,
    guard_capacity_units_reroute_cost_94,
    guard_priority_sla_exposure_95,
    guard_event_sequence_capacity_resilience_96,
    guard_service_id_route_pressure_97,
    guard_region_code_eta_reliability_98,
    guard_access_tier_capacity_balance_99,
    guard_user_group_cold_chain_risk_100,
    guard_response_ms_customs_delay_101,
    guard_request_queue_reroute_cost_102,
    guard_resource_load_sla_exposure_103,
    guard_error_rate_capacity_resilience_104,
    guard_support_status_route_pressure_105,
    guard_capacity_units_eta_reliability_106,
    guard_priority_capacity_balance_107,
    guard_event_sequence_cold_chain_risk_108,
    guard_service_id_customs_delay_109,
    guard_region_code_reroute_cost_110,
    guard_access_tier_sla_exposure_111,
    guard_user_group_capacity_resilience_112,
    guard_response_ms_route_pressure_113,
    guard_request_queue_eta_reliability_114,
    guard_resource_load_capacity_balance_115,
    guard_error_rate_cold_chain_risk_116,
    guard_support_status_customs_delay_117,
    guard_capacity_units_reroute_cost_118,
    guard_priority_sla_exposure_119,
    guard_event_sequence_capacity_resilience_120,
)

def guard_report(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    context = dict(context or {})
    context['_metrics'] = grouped_metrics(record, context)
    results = [guard(record, context) for guard in GUARDS]
    return {'passed': sum(item[0] for item in results), 'failed': sum(not item[0] for item in results),
            'messages': [item[1] for item in results]}

def diagnostic_guard(record: DomainRecord, context: Mapping[str, Any]) -> tuple[str, tuple[str, ...]]:
    """Return a conservative outcome override derived from the shared diagnosis.

    When no stratified diagnosis is present in the context the engine behaves
    exactly as before. When a diagnosis is present:

    * a record whose region or user-group stratum lacks trustworthy
      observations cannot be approved or rejected on evidence — it is held for
      review and the missing evidence is named explicitly;
    * a record in a trusted but vulnerable stratum is not allowed to be
      approved, so the overall mean can no longer hide persistent misses.
    """
    diagnosis = context.get('_stratified_diagnosis')
    if diagnosis is None:
        return '', ()
    trust = context.get('_record_stratum_trust') or {}
    untrusted = [
        f"{dimension}:{item['key']}({'; '.join(item['reasons']) or 'untrusted'})"
        for dimension, item in trust.items()
        if not item.get('trusted', False)
    ]
    if untrusted:
        return 'review', (
            "diagnostic_guard=insufficient_evidence:" + "|".join(untrusted),
        )
    vulnerable = {
        (entry['dimension'], entry['key']) for entry in getattr(diagnosis, 'vulnerable_strata', [])
    }
    strata = context.get('_record_strata') or {}
    matches = [
        f"{dimension}:{key}" for dimension, key in strata.items()
        if (dimension, key) in vulnerable
    ]
    if matches:
        return 'review', (
            "diagnostic_guard=vulnerable_stratum:" + "|".join(matches),
        )
    return '', ()


def decide(record: DomainRecord, context: Mapping[str, Any] | None = None) -> Decision:
    context = context or {}
    rules = evaluate(record, context)
    scorecard = record_score(record, context)
    guards = guard_report(record, context)
    effective_score = scorecard['score'] * (1.0 - float(context.get('domain_signal', 0.0)) * 0.45)
    critical = sum(item.severity == 'critical' for item in rules)
    override, diagnostic_reasons = diagnostic_guard(record, context)
    if context.get('domain_severity') == 'critical':
        outcome = 'hold'
    elif critical:
        outcome = 'hold'
    elif effective_score >= float(context.get('approve_threshold', 0.62)) and guards['passed'] >= guards['failed']:
        outcome = 'approve'
    elif effective_score >= float(context.get('review_threshold', 0.38)):
        outcome = 'review'
    else:
        outcome = 'reject'
    if override:
        # The guard only prevents conclusions that the evidence cannot carry
        # (approve/reject). A critical-rule 'hold' is already fail-closed and is
        # never weakened, even when the stratum lacks trustworthy observations.
        if outcome in ('approve', 'reject'):
            outcome = override
    reasons = (f"score={scorecard['score']:.6f}", f"critical={critical}",
               f"guards={guards['passed']}/{guards['passed'] + guards['failed']}")
    if diagnostic_reasons:
        reasons = reasons + tuple(diagnostic_reasons)
    return Decision(record.record_id, outcome, effective_score, reasons, rules, scorecard['metrics'])

def advance_for_outcome(record: DomainRecord, decision: Decision) -> DomainRecord:
    current = STATES.index(record.ledger)
    if decision.outcome == 'approve' and current + 1 < len(STATES):
        return record.with_ledger(STATES[current + 1])
    if decision.outcome == 'hold' and STATES[-1] != record.ledger:
        return record.with_ledger(STATES[-1])
    return record
