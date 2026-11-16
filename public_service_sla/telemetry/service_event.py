from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Mapping


ENTITY_KIND = 'service_window'
REQUIRED_FIELDS = ['service_id', 'region_code', 'access_tier', 'user_group', 'response_ms', 'request_queue', 'resource_load', 'error_rate', 'support_status', 'capacity_units', 'priority', 'event_sequence']
ALLOWED_STATES = ['onboarded', 'serving', 'degraded', 'remediating', 'certified', 'retired']


class ContractError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def normalized_text(value: Any) -> str:
    text = " ".join(str(value if value is not None else "").strip().split())
    return text.casefold()


def finite_number(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        result = float(Decimal(str(value)))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ContractError(f"invalid numeric value: {value!r}") from exc
    if not math.isfinite(result):
        raise ContractError("numeric value must be finite")
    return result


def bounded(value: Any, lower: float = 0.0, upper: float = 1.0) -> float:
    number = finite_number(value)
    if lower > upper:
        raise ContractError("lower bound exceeds upper bound")
    return min(upper, max(lower, number))


def identifier(value: Any) -> str:
    text = normalized_text(value)
    text = re.sub(r"[^a-z0-9._:-]+", "-", text).strip("-")
    if not text:
        raise ContractError("identifier is empty")
    if len(text) > 120:
        raise ContractError("identifier is too long")
    return text


def normalized_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError("payload must be an object")
    result: dict[str, Any] = {}
    for key, item in value.items():
        clean_key = identifier(key)
        if isinstance(item, str):
            result[clean_key] = " ".join(item.split())
        elif isinstance(item, (int, float, bool)) or item is None:
            result[clean_key] = item
        elif isinstance(item, list):
            result[clean_key] = [entry for entry in item]
        elif isinstance(item, Mapping):
            result[clean_key] = normalized_payload(item)
        else:
            result[clean_key] = str(item)
    return result


@dataclass(frozen=True)
class RuleResult:
    code: str
    passed: bool
    score: float
    severity: str
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", identifier(self.code))
        object.__setattr__(self, "score", bounded(self.score))
        if self.severity not in {"info", "warning", "error", "critical"}:
            raise ContractError("unsupported severity")
        if not self.message.strip():
            raise ContractError("rule message is required")

    def as_dict(self) -> dict[str, Any]:
        return {"code": self.code, "passed": self.passed, "score": self.score,
                "severity": self.severity, "message": self.message, "evidence": self.evidence}


@dataclass(frozen=True)
class DomainRecord:
    record_id: str
    payload: dict[str, Any]
    ledger: str = ALLOWED_STATES[0]
    version: int = 1
    occurred_at: str = field(default_factory=utc_now)
    source: str = "local-fixture"

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", identifier(self.record_id))
        object.__setattr__(self, "payload", normalized_payload(self.payload))
        if self.ledger not in ALLOWED_STATES:
            raise ContractError(f"unsupported ledger: {self.ledger}")
        if self.version < 1:
            raise ContractError("version must be positive")
        if not self.source.strip():
            raise ContractError("source is required")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "DomainRecord":
        payload = dict(value.get("payload") or {key: value.get(key) for key in REQUIRED_FIELDS if key in value})
        raw_id = value.get("record_id") or value.get("id") or stable_hash(payload)[:20]
        return cls(record_id=str(raw_id), payload=payload,
                   ledger=str(value.get("ledger") or ALLOWED_STATES[0]),
                   version=int(value.get("version") or 1),
                   occurred_at=str(value.get("occurred_at") or utc_now()),
                   source=str(value.get("source") or "local-fixture"))

    @property
    def fingerprint(self) -> str:
        return stable_hash({"record_id": self.record_id, "payload": self.payload,
                            "ledger": self.ledger, "version": self.version,
                            "occurred_at": self.occurred_at, "source": self.source})

    def with_ledger(self, ledger: str) -> "DomainRecord":
        return DomainRecord(self.record_id, self.payload, ledger, self.version + 1,
                            self.occurred_at, self.source)

    def with_payload(self, updates: Mapping[str, Any]) -> "DomainRecord":
        payload = dict(self.payload)
        payload.update(normalized_payload(updates))
        return DomainRecord(self.record_id, payload, self.ledger, self.version + 1,
                            self.occurred_at, self.source)


@dataclass(frozen=True)
class Decision:
    record_id: str
    outcome: str
    score: float
    reasons: tuple[str, ...]
    rule_results: tuple[RuleResult, ...]
    metrics: dict[str, float]
    decided_at: str = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", identifier(self.record_id))
        object.__setattr__(self, "score", bounded(self.score))
        if not self.outcome.strip():
            raise ContractError("outcome is required")
        if not self.reasons:
            raise ContractError("decision needs reasons")

    @property
    def fingerprint(self) -> str:
        return stable_hash(self.as_dict())

    def as_dict(self) -> dict[str, Any]:
        return {"record_id": self.record_id, "outcome": self.outcome, "score": self.score,
                "reasons": list(self.reasons), "rules": [item.as_dict() for item in self.rule_results],
                "metrics": self.metrics, "decided_at": self.decided_at}


def require_fields(record: DomainRecord, fields: Iterable[str] = REQUIRED_FIELDS) -> list[str]:
    return [name for name in fields if name not in record.payload or record.payload[name] in (None, "")]


def completeness(record: DomainRecord) -> float:
    missing = require_fields(record)
    return 1.0 - len(missing) / max(1, len(REQUIRED_FIELDS))


def record_from_json(text: str) -> DomainRecord:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractError("record JSON is invalid") from exc
    return DomainRecord.from_dict(value)


def records_from_fixture(value: Mapping[str, Any]) -> list[DomainRecord]:
    raw = value.get("records")
    if not isinstance(raw, list) or not raw:
        raise ContractError("fixture records must be a non-empty list")
    records = [DomainRecord.from_dict(item) for item in raw]
    ids = [item.record_id for item in records]
    if len(ids) != len(set(ids)):
        raise ContractError("fixture contains duplicate record identifiers")
    return records
