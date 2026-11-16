from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from public_service_sla.telemetry.service_event import DomainRecord, bounded, finite_number, normalized_text


@dataclass(frozen=True)
class RouteOption:
    route: tuple[str, ...]
    minutes: float
    cost: float
    capacity_left: float
    cold_chain_risk: float


def route_graph(records: Iterable[DomainRecord]) -> dict[str, list[tuple[str, float, float]]]:
    graph: dict[str, list[tuple[str, float, float]]] = {"service": []}
    for record in records:
        region = normalized_text(record.payload.get("region_code", "unknown"))
        response = max(0.0, finite_number(record.payload.get("response_ms", 0.0)))
        capacity = max(0.0, finite_number(record.payload.get("capacity_units", 0.0)))
        graph["service"].append((region, response, capacity))
    return graph


def shortest_capacity_path(graph: Mapping[str, list[tuple[str, float, float]]], start: str, end: str,
                           demand: float) -> RouteOption | None:
    if start != "service":
        return None
    candidates = [(response, capacity) for region, response, capacity in graph.get(start, [])
                  if region == end and capacity >= demand]
    if not candidates:
        return None
    response, capacity = min(candidates)
    return RouteOption((start, end), response, response, capacity - demand, 0.0)


def journey_pressure(record: DomainRecord) -> dict[str, float]:
    queue = bounded(finite_number(record.payload.get("request_queue", 0.0)) / 300.0)
    load = bounded(finite_number(record.payload.get("resource_load", 0.0)))
    status = normalized_text(record.payload.get("support_status", "clear"))
    support = 0.8 if status not in {"clear", "released", "approved"} else 0.1
    error = finite_number(record.payload.get("error_rate", 0.0))
    error = bounded(error / 100.0 if error > 1.0 else error)
    response = bounded(finite_number(record.payload.get("response_ms", 0.0)) / 5000.0)
    return {"border": queue, "warehouse": load, "customs": support, "cold": error,
            "total": bounded(queue * .25 + load * .25 + support * .15 + error * .20 + response * .15)}


def capacity_balance(records: Iterable[DomainRecord]) -> dict[str, float]:
    rows = list(records)
    capacities = [max(0.0, finite_number(row.payload.get("capacity_units", 0.0))) for row in rows]
    demands = [1.0 + max(0.0, finite_number(row.payload.get("priority", 0.0))) for row in rows]
    capacity = sum(capacities)
    demand = sum(demands)
    return {"capacity": capacity, "demand": demand, "utilization": bounded(demand / max(1.0, capacity)),
            "slack": max(0.0, capacity - demand)}


def derive_context(record: DomainRecord, repository: Any) -> dict[str, float]:
    rows = repository.list_records() or [record]
    pressure = journey_pressure(record)
    balance = capacity_balance(rows)
    return {"route_pressure_weight": 0.7 + pressure["total"] * 0.7,
            "eta_reliability_weight": 1.1 - pressure["border"] * 0.4,
            "capacity_balance_weight": 1.1 - balance["utilization"] * 0.3,
            "cold_chain_risk_weight": 0.7 + pressure["cold"] * 0.7,
            "capacity_resilience_weight": 0.6 + bounded(balance["slack"] / max(1.0, balance["capacity"])) * 0.6}
