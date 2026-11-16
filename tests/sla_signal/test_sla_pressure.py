from __future__ import annotations
import unittest
from public_service_sla.sla_signal.sla_pressure import sla_pressure, peer_distribution
class Record:
    def __init__(self, payload): self.payload = payload
class SignalTests(unittest.TestCase):
    def setUp(self): self.payload = {'service_id': 'service-a', 'region_code': 'region-a', 'access_tier': 'public', 'user_group': 'researchers', 'response_ms': 900, 'request_queue': 100, 'resource_load': 0.55, 'error_rate': 0.04, 'support_status': 'normal', 'capacity_units': 50, 'priority': 40, 'event_sequence': 10}
    def test_signal_is_bounded_and_explainable(self):
        signal = sla_pressure(self.payload)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)
        self.assertIn(signal.severity, {'info', 'warning', 'critical'})
        self.assertTrue({'error_rate', 'saturation', 'response_pressure'}.issubset(signal.evidence))
    def test_peer_distribution_uses_business_group(self):
        other = dict(self.payload); other['region_code'] = 'group-b'
        result = peer_distribution([Record(self.payload), Record(other)])
        self.assertEqual(result['count'], 2)
        self.assertIn('region_peaks', result)
    def test_material_business_change_is_observable(self):
        changed = dict(self.payload); changed['error_rate'] = 0.9
        self.assertNotEqual(sla_pressure(changed).score, sla_pressure(self.payload).score)
    def test_business_variant_1(self):
        changed = dict(self.payload)
        changed['access_tier'] = self.payload['access_tier']
        signal = sla_pressure(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_2(self):
        changed = dict(self.payload)
        changed['user_group'] = self.payload['user_group']
        signal = sla_pressure(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

    def test_business_variant_3(self):
        changed = dict(self.payload)
        changed['response_ms'] = self.payload['response_ms']
        signal = sla_pressure(changed)
        self.assertGreaterEqual(signal.score, 0.0)
        self.assertLessEqual(signal.score, 1.0)

if __name__ == '__main__': unittest.main()
