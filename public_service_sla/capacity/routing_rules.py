from __future__ import annotations

import math
from typing import Any, Callable, Mapping

from public_service_sla.telemetry.service_event import DomainRecord, RuleResult, bounded, finite_number, normalized_text

RuleFunction = Callable[[DomainRecord, Mapping[str, Any]], RuleResult]

def _number(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    if not text:
        return 0.0
    try:
        return finite_number(text)
    except ValueError:
        return float(sum(ord(ch) for ch in text) % 101)

def _context_number(context: Mapping[str, Any], key: str, default: float) -> float:
    try:
        return finite_number(context.get(key, default))
    except ValueError:
        return default

def _result(code: str, value: float, threshold: float, higher_is_better: bool, message: str, evidence: dict[str, Any]) -> RuleResult:
    distance = (value - threshold) if higher_is_better else (threshold - value)
    passed = distance >= 0
    scale = max(1.0, abs(threshold))
    score = bounded(0.5 + distance / (2.0 * scale))
    severity = 'info' if passed else ('critical' if score < 0.2 else 'error')
    return RuleResult(code, passed, score, severity, message, evidence)

def check_service_id_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'service_id')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_service_id_presence_threshold', 10.333)
    return _result('check_service_id_presence', adjusted, threshold, True, 'validates service_id presence',
                   {'field': 'service_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_service_id_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'service_id')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_service_id_range_threshold', 12.667)
    return _result('check_service_id_range', adjusted, threshold, True, 'validates service_id range',
                   {'field': 'service_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_service_id_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'service_id')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_service_id_stability_threshold', 15.0)
    return _result('check_service_id_stability', adjusted, threshold, False, 'validates service_id stability',
                   {'field': 'service_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_service_id_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'service_id')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_service_id_freshness_threshold', 17.333)
    return _result('check_service_id_freshness', adjusted, threshold, True, 'validates service_id freshness',
                   {'field': 'service_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_service_id_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'service_id')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_service_id_coverage_threshold', 19.667)
    return _result('check_service_id_coverage', adjusted, threshold, True, 'validates service_id coverage',
                   {'field': 'service_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_service_id_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'service_id')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_service_id_consistency_threshold', 22.0)
    return _result('check_service_id_consistency', adjusted, threshold, False, 'validates service_id consistency',
                   {'field': 'service_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_service_id_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'service_id')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_service_id_risk_threshold', 24.333)
    return _result('check_service_id_risk', adjusted, threshold, True, 'validates service_id risk',
                   {'field': 'service_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_service_id_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'service_id')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_service_id_confidence_threshold', 26.667)
    return _result('check_service_id_confidence', adjusted, threshold, True, 'validates service_id confidence',
                   {'field': 'service_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_service_id_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'service_id')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_service_id_dependency_threshold', 29.0)
    return _result('check_service_id_dependency', adjusted, threshold, False, 'validates service_id dependency',
                   {'field': 'service_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_service_id_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'service_id')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_service_id_readiness_threshold', 31.333)
    return _result('check_service_id_readiness', adjusted, threshold, True, 'validates service_id readiness',
                   {'field': 'service_id', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_region_code_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'region_code')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_region_code_presence_threshold', 9.333)
    return _result('check_region_code_presence', adjusted, threshold, True, 'validates region_code presence',
                   {'field': 'region_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_region_code_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'region_code')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_region_code_range_threshold', 11.667)
    return _result('check_region_code_range', adjusted, threshold, False, 'validates region_code range',
                   {'field': 'region_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_region_code_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'region_code')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_region_code_stability_threshold', 14.0)
    return _result('check_region_code_stability', adjusted, threshold, True, 'validates region_code stability',
                   {'field': 'region_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_region_code_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'region_code')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_region_code_freshness_threshold', 16.333)
    return _result('check_region_code_freshness', adjusted, threshold, True, 'validates region_code freshness',
                   {'field': 'region_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_region_code_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'region_code')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_region_code_coverage_threshold', 18.667)
    return _result('check_region_code_coverage', adjusted, threshold, False, 'validates region_code coverage',
                   {'field': 'region_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_region_code_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'region_code')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_region_code_consistency_threshold', 21.0)
    return _result('check_region_code_consistency', adjusted, threshold, True, 'validates region_code consistency',
                   {'field': 'region_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_region_code_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'region_code')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_region_code_risk_threshold', 23.333)
    return _result('check_region_code_risk', adjusted, threshold, True, 'validates region_code risk',
                   {'field': 'region_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_region_code_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'region_code')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_region_code_confidence_threshold', 25.667)
    return _result('check_region_code_confidence', adjusted, threshold, False, 'validates region_code confidence',
                   {'field': 'region_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_region_code_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'region_code')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_region_code_dependency_threshold', 28.0)
    return _result('check_region_code_dependency', adjusted, threshold, True, 'validates region_code dependency',
                   {'field': 'region_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_region_code_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'region_code')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_region_code_readiness_threshold', 30.333)
    return _result('check_region_code_readiness', adjusted, threshold, True, 'validates region_code readiness',
                   {'field': 'region_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_access_tier_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'access_tier')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_access_tier_presence_threshold', 8.333)
    return _result('check_access_tier_presence', adjusted, threshold, False, 'validates access_tier presence',
                   {'field': 'access_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_access_tier_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'access_tier')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_access_tier_range_threshold', 10.667)
    return _result('check_access_tier_range', adjusted, threshold, True, 'validates access_tier range',
                   {'field': 'access_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_access_tier_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'access_tier')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_access_tier_stability_threshold', 13.0)
    return _result('check_access_tier_stability', adjusted, threshold, True, 'validates access_tier stability',
                   {'field': 'access_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_access_tier_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'access_tier')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_access_tier_freshness_threshold', 15.333)
    return _result('check_access_tier_freshness', adjusted, threshold, False, 'validates access_tier freshness',
                   {'field': 'access_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_access_tier_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'access_tier')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_access_tier_coverage_threshold', 17.667)
    return _result('check_access_tier_coverage', adjusted, threshold, True, 'validates access_tier coverage',
                   {'field': 'access_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_access_tier_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'access_tier')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_access_tier_consistency_threshold', 20.0)
    return _result('check_access_tier_consistency', adjusted, threshold, True, 'validates access_tier consistency',
                   {'field': 'access_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_access_tier_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'access_tier')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_access_tier_risk_threshold', 22.333)
    return _result('check_access_tier_risk', adjusted, threshold, False, 'validates access_tier risk',
                   {'field': 'access_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_access_tier_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'access_tier')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_access_tier_confidence_threshold', 24.667)
    return _result('check_access_tier_confidence', adjusted, threshold, True, 'validates access_tier confidence',
                   {'field': 'access_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_access_tier_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'access_tier')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_access_tier_dependency_threshold', 27.0)
    return _result('check_access_tier_dependency', adjusted, threshold, True, 'validates access_tier dependency',
                   {'field': 'access_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_access_tier_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'access_tier')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_access_tier_readiness_threshold', 29.333)
    return _result('check_access_tier_readiness', adjusted, threshold, False, 'validates access_tier readiness',
                   {'field': 'access_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_user_group_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'user_group')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_user_group_presence_threshold', 31.667)
    return _result('check_user_group_presence', adjusted, threshold, True, 'validates user_group presence',
                   {'field': 'user_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_user_group_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'user_group')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_user_group_range_threshold', 9.667)
    return _result('check_user_group_range', adjusted, threshold, True, 'validates user_group range',
                   {'field': 'user_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_user_group_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'user_group')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_user_group_stability_threshold', 12.0)
    return _result('check_user_group_stability', adjusted, threshold, False, 'validates user_group stability',
                   {'field': 'user_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_user_group_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'user_group')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_user_group_freshness_threshold', 14.333)
    return _result('check_user_group_freshness', adjusted, threshold, True, 'validates user_group freshness',
                   {'field': 'user_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_user_group_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'user_group')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_user_group_coverage_threshold', 16.667)
    return _result('check_user_group_coverage', adjusted, threshold, True, 'validates user_group coverage',
                   {'field': 'user_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_user_group_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'user_group')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_user_group_consistency_threshold', 19.0)
    return _result('check_user_group_consistency', adjusted, threshold, False, 'validates user_group consistency',
                   {'field': 'user_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_user_group_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'user_group')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_user_group_risk_threshold', 21.333)
    return _result('check_user_group_risk', adjusted, threshold, True, 'validates user_group risk',
                   {'field': 'user_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_user_group_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'user_group')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_user_group_confidence_threshold', 23.667)
    return _result('check_user_group_confidence', adjusted, threshold, True, 'validates user_group confidence',
                   {'field': 'user_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_user_group_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'user_group')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_user_group_dependency_threshold', 26.0)
    return _result('check_user_group_dependency', adjusted, threshold, False, 'validates user_group dependency',
                   {'field': 'user_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_user_group_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'user_group')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_user_group_readiness_threshold', 28.333)
    return _result('check_user_group_readiness', adjusted, threshold, True, 'validates user_group readiness',
                   {'field': 'user_group', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_response_ms_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'response_ms')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_response_ms_presence_threshold', 30.667)
    return _result('check_response_ms_presence', adjusted, threshold, True, 'validates response_ms presence',
                   {'field': 'response_ms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_response_ms_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'response_ms')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_response_ms_range_threshold', 8.667)
    return _result('check_response_ms_range', adjusted, threshold, False, 'validates response_ms range',
                   {'field': 'response_ms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_response_ms_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'response_ms')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_response_ms_stability_threshold', 11.0)
    return _result('check_response_ms_stability', adjusted, threshold, True, 'validates response_ms stability',
                   {'field': 'response_ms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_response_ms_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'response_ms')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_response_ms_freshness_threshold', 13.333)
    return _result('check_response_ms_freshness', adjusted, threshold, True, 'validates response_ms freshness',
                   {'field': 'response_ms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_response_ms_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'response_ms')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_response_ms_coverage_threshold', 15.667)
    return _result('check_response_ms_coverage', adjusted, threshold, False, 'validates response_ms coverage',
                   {'field': 'response_ms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_response_ms_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'response_ms')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_response_ms_consistency_threshold', 18.0)
    return _result('check_response_ms_consistency', adjusted, threshold, True, 'validates response_ms consistency',
                   {'field': 'response_ms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_response_ms_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'response_ms')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_response_ms_risk_threshold', 20.333)
    return _result('check_response_ms_risk', adjusted, threshold, True, 'validates response_ms risk',
                   {'field': 'response_ms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_response_ms_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'response_ms')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_response_ms_confidence_threshold', 22.667)
    return _result('check_response_ms_confidence', adjusted, threshold, False, 'validates response_ms confidence',
                   {'field': 'response_ms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_response_ms_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'response_ms')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_response_ms_dependency_threshold', 25.0)
    return _result('check_response_ms_dependency', adjusted, threshold, True, 'validates response_ms dependency',
                   {'field': 'response_ms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_response_ms_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'response_ms')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_response_ms_readiness_threshold', 27.333)
    return _result('check_response_ms_readiness', adjusted, threshold, True, 'validates response_ms readiness',
                   {'field': 'response_ms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_request_queue_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'request_queue')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_request_queue_presence_threshold', 29.667)
    return _result('check_request_queue_presence', adjusted, threshold, False, 'validates request_queue presence',
                   {'field': 'request_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_request_queue_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'request_queue')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_request_queue_range_threshold', 32.0)
    return _result('check_request_queue_range', adjusted, threshold, True, 'validates request_queue range',
                   {'field': 'request_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_request_queue_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'request_queue')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_request_queue_stability_threshold', 10.0)
    return _result('check_request_queue_stability', adjusted, threshold, True, 'validates request_queue stability',
                   {'field': 'request_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_request_queue_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'request_queue')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_request_queue_freshness_threshold', 12.333)
    return _result('check_request_queue_freshness', adjusted, threshold, False, 'validates request_queue freshness',
                   {'field': 'request_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_request_queue_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'request_queue')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_request_queue_coverage_threshold', 14.667)
    return _result('check_request_queue_coverage', adjusted, threshold, True, 'validates request_queue coverage',
                   {'field': 'request_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_request_queue_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'request_queue')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_request_queue_consistency_threshold', 17.0)
    return _result('check_request_queue_consistency', adjusted, threshold, True, 'validates request_queue consistency',
                   {'field': 'request_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_request_queue_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'request_queue')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_request_queue_risk_threshold', 19.333)
    return _result('check_request_queue_risk', adjusted, threshold, False, 'validates request_queue risk',
                   {'field': 'request_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_request_queue_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'request_queue')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_request_queue_confidence_threshold', 21.667)
    return _result('check_request_queue_confidence', adjusted, threshold, True, 'validates request_queue confidence',
                   {'field': 'request_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_request_queue_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'request_queue')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_request_queue_dependency_threshold', 24.0)
    return _result('check_request_queue_dependency', adjusted, threshold, True, 'validates request_queue dependency',
                   {'field': 'request_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_request_queue_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'request_queue')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_request_queue_readiness_threshold', 26.333)
    return _result('check_request_queue_readiness', adjusted, threshold, False, 'validates request_queue readiness',
                   {'field': 'request_queue', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_load_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_load')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_resource_load_presence_threshold', 28.667)
    return _result('check_resource_load_presence', adjusted, threshold, True, 'validates resource_load presence',
                   {'field': 'resource_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_load_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_load')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_resource_load_range_threshold', 31.0)
    return _result('check_resource_load_range', adjusted, threshold, True, 'validates resource_load range',
                   {'field': 'resource_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_load_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_load')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_resource_load_stability_threshold', 9.0)
    return _result('check_resource_load_stability', adjusted, threshold, False, 'validates resource_load stability',
                   {'field': 'resource_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_load_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_load')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_resource_load_freshness_threshold', 11.333)
    return _result('check_resource_load_freshness', adjusted, threshold, True, 'validates resource_load freshness',
                   {'field': 'resource_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_load_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_load')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_resource_load_coverage_threshold', 13.667)
    return _result('check_resource_load_coverage', adjusted, threshold, True, 'validates resource_load coverage',
                   {'field': 'resource_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_load_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_load')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_resource_load_consistency_threshold', 16.0)
    return _result('check_resource_load_consistency', adjusted, threshold, False, 'validates resource_load consistency',
                   {'field': 'resource_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_load_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_load')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_resource_load_risk_threshold', 18.333)
    return _result('check_resource_load_risk', adjusted, threshold, True, 'validates resource_load risk',
                   {'field': 'resource_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_load_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_load')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_resource_load_confidence_threshold', 20.667)
    return _result('check_resource_load_confidence', adjusted, threshold, True, 'validates resource_load confidence',
                   {'field': 'resource_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_load_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_load')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_resource_load_dependency_threshold', 23.0)
    return _result('check_resource_load_dependency', adjusted, threshold, False, 'validates resource_load dependency',
                   {'field': 'resource_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_load_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_load')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_resource_load_readiness_threshold', 25.333)
    return _result('check_resource_load_readiness', adjusted, threshold, True, 'validates resource_load readiness',
                   {'field': 'resource_load', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_error_rate_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'error_rate')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_error_rate_presence_threshold', 27.667)
    return _result('check_error_rate_presence', adjusted, threshold, True, 'validates error_rate presence',
                   {'field': 'error_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_error_rate_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'error_rate')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_error_rate_range_threshold', 30.0)
    return _result('check_error_rate_range', adjusted, threshold, False, 'validates error_rate range',
                   {'field': 'error_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_error_rate_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'error_rate')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_error_rate_stability_threshold', 8.0)
    return _result('check_error_rate_stability', adjusted, threshold, True, 'validates error_rate stability',
                   {'field': 'error_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_error_rate_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'error_rate')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_error_rate_freshness_threshold', 10.333)
    return _result('check_error_rate_freshness', adjusted, threshold, True, 'validates error_rate freshness',
                   {'field': 'error_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_error_rate_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'error_rate')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_error_rate_coverage_threshold', 12.667)
    return _result('check_error_rate_coverage', adjusted, threshold, False, 'validates error_rate coverage',
                   {'field': 'error_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_error_rate_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'error_rate')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_error_rate_consistency_threshold', 15.0)
    return _result('check_error_rate_consistency', adjusted, threshold, True, 'validates error_rate consistency',
                   {'field': 'error_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_error_rate_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'error_rate')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_error_rate_risk_threshold', 17.333)
    return _result('check_error_rate_risk', adjusted, threshold, True, 'validates error_rate risk',
                   {'field': 'error_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_error_rate_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'error_rate')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_error_rate_confidence_threshold', 19.667)
    return _result('check_error_rate_confidence', adjusted, threshold, False, 'validates error_rate confidence',
                   {'field': 'error_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_error_rate_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'error_rate')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_error_rate_dependency_threshold', 22.0)
    return _result('check_error_rate_dependency', adjusted, threshold, True, 'validates error_rate dependency',
                   {'field': 'error_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_error_rate_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'error_rate')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_error_rate_readiness_threshold', 24.333)
    return _result('check_error_rate_readiness', adjusted, threshold, True, 'validates error_rate readiness',
                   {'field': 'error_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_status_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_status')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_support_status_presence_threshold', 26.667)
    return _result('check_support_status_presence', adjusted, threshold, False, 'validates support_status presence',
                   {'field': 'support_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_status_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_status')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_support_status_range_threshold', 29.0)
    return _result('check_support_status_range', adjusted, threshold, True, 'validates support_status range',
                   {'field': 'support_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_status_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_status')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_support_status_stability_threshold', 31.333)
    return _result('check_support_status_stability', adjusted, threshold, True, 'validates support_status stability',
                   {'field': 'support_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_status_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_status')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_support_status_freshness_threshold', 9.333)
    return _result('check_support_status_freshness', adjusted, threshold, False, 'validates support_status freshness',
                   {'field': 'support_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_status_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_status')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_support_status_coverage_threshold', 11.667)
    return _result('check_support_status_coverage', adjusted, threshold, True, 'validates support_status coverage',
                   {'field': 'support_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_status_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_status')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_support_status_consistency_threshold', 14.0)
    return _result('check_support_status_consistency', adjusted, threshold, True, 'validates support_status consistency',
                   {'field': 'support_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_status_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_status')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_support_status_risk_threshold', 16.333)
    return _result('check_support_status_risk', adjusted, threshold, False, 'validates support_status risk',
                   {'field': 'support_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_status_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_status')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_support_status_confidence_threshold', 18.667)
    return _result('check_support_status_confidence', adjusted, threshold, True, 'validates support_status confidence',
                   {'field': 'support_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_status_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_status')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_support_status_dependency_threshold', 21.0)
    return _result('check_support_status_dependency', adjusted, threshold, True, 'validates support_status dependency',
                   {'field': 'support_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_support_status_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'support_status')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_support_status_readiness_threshold', 23.333)
    return _result('check_support_status_readiness', adjusted, threshold, False, 'validates support_status readiness',
                   {'field': 'support_status', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_capacity_units_presence_threshold', 25.667)
    return _result('check_capacity_units_presence', adjusted, threshold, True, 'validates capacity_units presence',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_capacity_units_range_threshold', 28.0)
    return _result('check_capacity_units_range', adjusted, threshold, True, 'validates capacity_units range',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_capacity_units_stability_threshold', 30.333)
    return _result('check_capacity_units_stability', adjusted, threshold, False, 'validates capacity_units stability',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_capacity_units_freshness_threshold', 8.333)
    return _result('check_capacity_units_freshness', adjusted, threshold, True, 'validates capacity_units freshness',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_capacity_units_coverage_threshold', 10.667)
    return _result('check_capacity_units_coverage', adjusted, threshold, True, 'validates capacity_units coverage',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_capacity_units_consistency_threshold', 13.0)
    return _result('check_capacity_units_consistency', adjusted, threshold, False, 'validates capacity_units consistency',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_capacity_units_risk_threshold', 15.333)
    return _result('check_capacity_units_risk', adjusted, threshold, True, 'validates capacity_units risk',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_capacity_units_confidence_threshold', 17.667)
    return _result('check_capacity_units_confidence', adjusted, threshold, True, 'validates capacity_units confidence',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_capacity_units_dependency_threshold', 20.0)
    return _result('check_capacity_units_dependency', adjusted, threshold, False, 'validates capacity_units dependency',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_capacity_units_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'capacity_units')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_capacity_units_readiness_threshold', 22.333)
    return _result('check_capacity_units_readiness', adjusted, threshold, True, 'validates capacity_units readiness',
                   {'field': 'capacity_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_priority_presence_threshold', 24.667)
    return _result('check_priority_presence', adjusted, threshold, True, 'validates priority presence',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_priority_range_threshold', 27.0)
    return _result('check_priority_range', adjusted, threshold, False, 'validates priority range',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_priority_stability_threshold', 29.333)
    return _result('check_priority_stability', adjusted, threshold, True, 'validates priority stability',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_priority_freshness_threshold', 31.667)
    return _result('check_priority_freshness', adjusted, threshold, True, 'validates priority freshness',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_priority_coverage_threshold', 9.667)
    return _result('check_priority_coverage', adjusted, threshold, False, 'validates priority coverage',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_priority_consistency_threshold', 12.0)
    return _result('check_priority_consistency', adjusted, threshold, True, 'validates priority consistency',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_priority_risk_threshold', 14.333)
    return _result('check_priority_risk', adjusted, threshold, True, 'validates priority risk',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_priority_confidence_threshold', 16.667)
    return _result('check_priority_confidence', adjusted, threshold, False, 'validates priority confidence',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_priority_dependency_threshold', 19.0)
    return _result('check_priority_dependency', adjusted, threshold, True, 'validates priority dependency',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_priority_readiness_threshold', 21.333)
    return _result('check_priority_readiness', adjusted, threshold, True, 'validates priority readiness',
                   {'field': 'priority', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_event_sequence_presence_threshold', 23.667)
    return _result('check_event_sequence_presence', adjusted, threshold, False, 'validates event_sequence presence',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_event_sequence_range_threshold', 26.0)
    return _result('check_event_sequence_range', adjusted, threshold, True, 'validates event_sequence range',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_event_sequence_stability_threshold', 28.333)
    return _result('check_event_sequence_stability', adjusted, threshold, True, 'validates event_sequence stability',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_event_sequence_freshness_threshold', 30.667)
    return _result('check_event_sequence_freshness', adjusted, threshold, False, 'validates event_sequence freshness',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_event_sequence_coverage_threshold', 8.667)
    return _result('check_event_sequence_coverage', adjusted, threshold, True, 'validates event_sequence coverage',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_event_sequence_consistency_threshold', 11.0)
    return _result('check_event_sequence_consistency', adjusted, threshold, True, 'validates event_sequence consistency',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_event_sequence_risk_threshold', 13.333)
    return _result('check_event_sequence_risk', adjusted, threshold, False, 'validates event_sequence risk',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_event_sequence_confidence_threshold', 15.667)
    return _result('check_event_sequence_confidence', adjusted, threshold, True, 'validates event_sequence confidence',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_event_sequence_dependency_threshold', 18.0)
    return _result('check_event_sequence_dependency', adjusted, threshold, True, 'validates event_sequence dependency',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_event_sequence_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'event_sequence')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_event_sequence_readiness_threshold', 20.333)
    return _result('check_event_sequence_readiness', adjusted, threshold, False, 'validates event_sequence readiness',
                   {'field': 'event_sequence', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

RULES: tuple[RuleFunction, ...] = (
    check_service_id_presence,
    check_service_id_range,
    check_service_id_stability,
    check_service_id_freshness,
    check_service_id_coverage,
    check_service_id_consistency,
    check_service_id_risk,
    check_service_id_confidence,
    check_service_id_dependency,
    check_service_id_readiness,
    check_region_code_presence,
    check_region_code_range,
    check_region_code_stability,
    check_region_code_freshness,
    check_region_code_coverage,
    check_region_code_consistency,
    check_region_code_risk,
    check_region_code_confidence,
    check_region_code_dependency,
    check_region_code_readiness,
    check_access_tier_presence,
    check_access_tier_range,
    check_access_tier_stability,
    check_access_tier_freshness,
    check_access_tier_coverage,
    check_access_tier_consistency,
    check_access_tier_risk,
    check_access_tier_confidence,
    check_access_tier_dependency,
    check_access_tier_readiness,
    check_user_group_presence,
    check_user_group_range,
    check_user_group_stability,
    check_user_group_freshness,
    check_user_group_coverage,
    check_user_group_consistency,
    check_user_group_risk,
    check_user_group_confidence,
    check_user_group_dependency,
    check_user_group_readiness,
    check_response_ms_presence,
    check_response_ms_range,
    check_response_ms_stability,
    check_response_ms_freshness,
    check_response_ms_coverage,
    check_response_ms_consistency,
    check_response_ms_risk,
    check_response_ms_confidence,
    check_response_ms_dependency,
    check_response_ms_readiness,
    check_request_queue_presence,
    check_request_queue_range,
    check_request_queue_stability,
    check_request_queue_freshness,
    check_request_queue_coverage,
    check_request_queue_consistency,
    check_request_queue_risk,
    check_request_queue_confidence,
    check_request_queue_dependency,
    check_request_queue_readiness,
    check_resource_load_presence,
    check_resource_load_range,
    check_resource_load_stability,
    check_resource_load_freshness,
    check_resource_load_coverage,
    check_resource_load_consistency,
    check_resource_load_risk,
    check_resource_load_confidence,
    check_resource_load_dependency,
    check_resource_load_readiness,
    check_error_rate_presence,
    check_error_rate_range,
    check_error_rate_stability,
    check_error_rate_freshness,
    check_error_rate_coverage,
    check_error_rate_consistency,
    check_error_rate_risk,
    check_error_rate_confidence,
    check_error_rate_dependency,
    check_error_rate_readiness,
    check_support_status_presence,
    check_support_status_range,
    check_support_status_stability,
    check_support_status_freshness,
    check_support_status_coverage,
    check_support_status_consistency,
    check_support_status_risk,
    check_support_status_confidence,
    check_support_status_dependency,
    check_support_status_readiness,
    check_capacity_units_presence,
    check_capacity_units_range,
    check_capacity_units_stability,
    check_capacity_units_freshness,
    check_capacity_units_coverage,
    check_capacity_units_consistency,
    check_capacity_units_risk,
    check_capacity_units_confidence,
    check_capacity_units_dependency,
    check_capacity_units_readiness,
    check_priority_presence,
    check_priority_range,
    check_priority_stability,
    check_priority_freshness,
    check_priority_coverage,
    check_priority_consistency,
    check_priority_risk,
    check_priority_confidence,
    check_priority_dependency,
    check_priority_readiness,
    check_event_sequence_presence,
    check_event_sequence_range,
    check_event_sequence_stability,
    check_event_sequence_freshness,
    check_event_sequence_coverage,
    check_event_sequence_consistency,
    check_event_sequence_risk,
    check_event_sequence_confidence,
    check_event_sequence_dependency,
    check_event_sequence_readiness,
)

RULE_INDEX = {rule.__name__: rule for rule in RULES}

def evaluate(record: DomainRecord, context: Mapping[str, Any] | None = None) -> tuple[RuleResult, ...]:
    context = context or {}
    return tuple(rule(record, context) for rule in RULES)

def summarize(results: tuple[RuleResult, ...]) -> dict[str, Any]:
    if not results:
        return {'score': 0.0, 'passed': 0, 'failed': 0, 'critical': 0}
    return {'score': sum(item.score for item in results) / len(results),
            'passed': sum(item.passed for item in results),
            'failed': sum(not item.passed for item in results),
            'critical': sum(item.severity == 'critical' for item in results)}
