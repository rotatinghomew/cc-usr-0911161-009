from __future__ import annotations

import unittest
from public_service_sla.telemetry.service_event import DomainRecord
from public_service_sla.capacity.load_replay import journey_pressure, capacity_balance, route_graph, shortest_capacity_path


class CapacityReplayTests(unittest.TestCase):
    def record(self, key, region="region-a"):
        return DomainRecord(key, {"service_id": key, "region_code": region, "access_tier": "standard", "user_group": "residents",
            "response_ms": 120, "request_queue": 20, "resource_load": .6, "error_rate": 7,
            "support_status": "clear", "capacity_units": 10, "priority": 2, "event_sequence": 1})

    def test_region_response_respects_capacity(self):
        graph = route_graph([self.record("s1")])
        self.assertIsNotNone(shortest_capacity_path(graph, "service", "region-a", 5))
        self.assertIsNone(shortest_capacity_path(graph, "service", "region-a", 50))

    def test_pressure_and_balance(self):
        rows = [self.record("a"), self.record("b")]
        self.assertGreater(journey_pressure(rows[0])["total"], 0.0)
        self.assertGreater(capacity_balance(rows)["capacity"], capacity_balance(rows)["demand"])
