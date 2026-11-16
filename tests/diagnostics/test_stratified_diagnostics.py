from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from public_service_sla.telemetry.service_event import DomainRecord, records_from_fixture
from public_service_sla.diagnostics.stratified_diagnostics import (
    DIMENSIONS,
    TRUSTED,
    INSUFFICIENT_EVIDENCE,
    Thresholds,
    diagnose_records,
    safe_float,
    stratify_records,
    strata_for_record,
    trusted_strata_for_record,
)
from public_service_sla.remediation.routing_flow import decide, diagnostic_guard
from public_service_sla.reports.sla_report import export_bundle, verify_bundle, build_summary
from public_service_sla.service_monitor import Application

FIELDS = ['service_id', 'region_code', 'access_tier', 'user_group', 'response_ms',
          'request_queue', 'resource_load', 'error_rate', 'support_status',
          'capacity_units', 'priority', 'event_sequence']


def make_payload(seq, region, group, *, response_ms=120.0, request_queue=20.0,
                 resource_load=0.5, error_rate=0.05, capacity_units=100.0,
                 missing=None, bad_numeric=None):
    payload = {
        'service_id': f'service-{seq}',
        'region_code': region,
        'access_tier': 'standard',
        'user_group': group,
        'response_ms': response_ms,
        'request_queue': request_queue,
        'resource_load': resource_load,
        'error_rate': error_rate,
        'support_status': 'clear',
        'capacity_units': capacity_units,
        'priority': 2,
        'event_sequence': seq,
    }
    for name in missing or ():
        payload[name] = ""
    for name in bad_numeric or ():
        payload[name] = "not-a-number"
    return payload


def make_record(seq, region, group, **kwargs):
    return DomainRecord(f'window-{seq:03d}', make_payload(seq, region, group, **kwargs))


def make_region_dataset():
    # region-healthy: fast, low error, comfortable capacity (4 trusted windows)
    healthy = [make_record(i, 'region-healthy', 'group-a',
                           response_ms=100.0, request_queue=10.0, error_rate=0.02,
                           capacity_units=200.0) for i in range(1, 5)]
    # region-queue: queue surge + saturated capacity -> targeted capacity
    queued = [make_record(10 + i, 'region-queue', 'group-b',
                          response_ms=900.0, request_queue=280.0, error_rate=0.03,
                          capacity_units=300.0) for i in range(1, 5)]
    # region-anomaly: record defects / high error but ample capacity -> fix records
    anomaly = [make_record(20 + i, 'region-anomaly', 'group-c',
                           response_ms=150.0, request_queue=15.0, error_rate=0.6,
                           capacity_units=300.0) for i in range(1, 5)]
    # region-breach: persistent misses with slack capacity -> protect group
    breach = [make_record(30 + i, 'region-breach', 'group-d',
                          response_ms=1500.0, request_queue=20.0, error_rate=0.04,
                          capacity_units=400.0) for i in range(1, 5)]
    return healthy + queued + anomaly + breach


class SafeFloatTests(unittest.TestCase):
    def test_invalid_values_return_none(self):
        for value in (None, "", "not-a-number", float('inf'), float('-inf'), float('nan')):
            self.assertIsNone(safe_float(value))
        self.assertEqual(safe_float("12.5"), 12.5)
        self.assertEqual(safe_float(3), 3.0)
        self.assertIsNone(safe_float(True))


class StratificationTests(unittest.TestCase):
    def test_slices_along_both_dimensions(self):
        records = make_region_dataset()
        strata = stratify_records(records)
        self.assertEqual(set(strata), set(DIMENSIONS))
        self.assertEqual(set(strata['region_code']),
                         {'region-healthy', 'region-queue', 'region-anomaly', 'region-breach'})
        for stats in strata['region_code'].values():
            self.assertEqual(stats.samples, 4)
            self.assertTrue(stats.is_trusted())

    def test_small_stratum_is_marked_insufficient_evidence(self):
        records = [make_record(1, 'region-sparse', 'group-a'),
                   make_record(2, 'region-sparse', 'group-a')]
        diagnosis = diagnose_records(records)
        stats = diagnosis.strata['region_code']['region-sparse']
        self.assertEqual(stats['evidence_status'], INSUFFICIENT_EVIDENCE)
        self.assertEqual(stats['recommendation'], 'insufficient_evidence')
        self.assertTrue(any('sample_size' in reason for reason in stats['evidence_reasons']))

    def test_missing_and_bad_fields_reduce_coverage_and_block_trust(self):
        records = [
            make_record(1, 'region-gap', 'group-a', missing=('response_ms',)),
            make_record(2, 'region-gap', 'group-a', bad_numeric=('error_rate',)),
            make_record(3, 'region-gap', 'group-a'),
        ]
        diagnosis = diagnose_records(records)
        stats = diagnosis.strata['region_code']['region-gap']
        self.assertEqual(stats['evidence_status'], INSUFFICIENT_EVIDENCE)
        self.assertLess(stats['field_coverage']['response_ms'], 1.0)
        self.assertLess(stats['field_coverage']['error_rate'], 1.0)
        self.assertTrue(stats['evidence_reasons'])


class DriverDiagnosisTests(unittest.TestCase):
    def setUp(self):
        self.diagnosis = diagnose_records(make_region_dataset())

    def _region(self, key):
        return self.diagnosis.strata['region_code'][key]

    def test_queue_surge_with_saturated_capacity_recommends_targeted_capacity(self):
        stats = self._region('region-queue')
        self.assertIn('queue_surge', stats['drivers'])
        self.assertIn('capacity_constrained', stats['drivers'])
        self.assertEqual(stats['recommendation'], 'add_capacity_targeted')

    def test_record_anomaly_does_not_recommend_capacity(self):
        stats = self._region('region-anomaly')
        self.assertIn('record_anomaly', stats['drivers'])
        self.assertEqual(stats['recommendation'], 'fix_records_and_instrumentation')
        self.assertNotEqual(stats['recommendation'], 'add_capacity_targeted')

    def test_persistent_breach_with_capacity_slack_protects_group(self):
        stats = self._region('region-breach')
        self.assertIn('persistent_window_breach', stats['drivers'])
        self.assertNotIn('capacity_constrained', stats['drivers'])
        self.assertEqual(stats['recommendation'], 'protect_user_group')

    def test_healthy_stratum_is_monitored_only(self):
        stats = self._region('region-healthy')
        self.assertEqual(stats['evidence_status'], TRUSTED)
        self.assertEqual(stats['recommendation'], 'monitor_only')

    def test_effective_response_and_anomaly_separate_failure_modes(self):
        healthy = self._region('region-healthy')
        breach = self._region('region-breach')
        self.assertGreater(healthy['effective_response_rate'], breach['effective_response_rate'])
        anomaly = self._region('region-anomaly')
        self.assertGreater(anomaly['anomaly_rate'], healthy['anomaly_rate'])

    def test_vulnerable_strata_are_flagged_beneath_the_portfolio(self):
        vulnerable = {(item['dimension'], item['key'])
                      for item in self.diagnosis.vulnerable_strata}
        self.assertIn(('region_code', 'region-breach'), vulnerable)
        self.assertNotIn(('region_code', 'region-healthy'), vulnerable)

    def test_diagnosis_is_deterministic_and_fingerprinted(self):
        again = diagnose_records(make_region_dataset())
        self.assertEqual(again.fingerprint, self.diagnosis.fingerprint)
        self.assertTrue(self.diagnosis.fingerprint)

    def test_thresholds_are_overridable(self):
        strict = diagnose_records(make_region_dataset(),
                                  {'diagnostics_min_samples': 5})
        self.assertTrue(
            all(stats['evidence_status'] == INSUFFICIENT_EVIDENCE
                for stats in strict.strata['region_code'].values())
        )


class RemediationSharingTests(unittest.TestCase):
    def setUp(self):
        self.records = make_region_dataset()
        self.diagnosis = diagnose_records(self.records)

    def test_diagnostic_guard_is_off_without_diagnosis(self):
        record = self.records[0]
        override, reasons = diagnostic_guard(record, {})
        self.assertEqual(override, '')
        self.assertEqual(reasons, ())
        # Standalone decision engine remains unchanged.
        self.assertEqual(decide(record).reasons[:3], decide(record, {}).reasons[:3])

    def test_untrusted_stratum_cannot_be_approved_or_rejected(self):
        sparse = [make_record(1, 'region-sparse', 'group-z'),
                  make_record(2, 'region-sparse', 'group-z')]
        diagnosis = diagnose_records(sparse)
        record = sparse[0]
        trust = trusted_strata_for_record(record, diagnosis)
        context = {'_stratified_diagnosis': diagnosis,
                   '_record_strata': strata_for_record(record),
                   '_record_stratum_trust': trust}
        override, reasons = diagnostic_guard(record, context)
        self.assertEqual(override, 'review')
        self.assertTrue(any('insufficient_evidence' in item for item in reasons))
        decision = decide(record, context)
        # Evidence-insufficient strata never produce an approve/reject verdict;
        # a critical-rule 'hold' (already fail-closed) is allowed to stand.
        self.assertIn(decision.outcome, ('review', 'hold'))
        self.assertNotIn(decision.outcome, ('approve', 'reject'))
        self.assertTrue(any('diagnostic_guard=insufficient_evidence' in reason
                            for reason in decision.reasons))

    def test_vulnerable_stratum_record_is_held_for_review(self):
        record = next(item for item in self.records
                      if item.payload['region_code'] == 'region-breach')
        trust = trusted_strata_for_record(record, self.diagnosis)
        context = {'_stratified_diagnosis': self.diagnosis,
                   '_record_strata': strata_for_record(record),
                   '_record_stratum_trust': trust}
        override, reasons = diagnostic_guard(record, context)
        self.assertEqual(override, 'review')
        self.assertTrue(any('vulnerable_stratum' in item for item in reasons))

    def test_healthy_record_keeps_original_outcome(self):
        record = next(item for item in self.records
                      if item.payload['region_code'] == 'region-healthy')
        baseline = decide(record).outcome
        trust = trusted_strata_for_record(record, self.diagnosis)
        context = {'_stratified_diagnosis': self.diagnosis,
                   '_record_strata': strata_for_record(record),
                   '_record_stratum_trust': trust}
        self.assertEqual(decide(record, context).outcome, baseline)


class ReportWiringTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_summary_carries_diagnosis_and_csv_lists_every_stratum(self):
        records = make_region_dataset()
        diagnosis = diagnose_records(records)
        output = self.root / "output"
        decisions = {record.record_id: decide(record) for record in records}
        snapshot = {'counts': {}, 'ledgers': {}, 'chain_errors': []}
        export_bundle(output, records, decisions, snapshot, [], diagnosis)
        self.assertEqual(verify_bundle(output), [])
        summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
        self.assertIn('stratified_diagnostics', summary)
        with (output / "stratified-diagnostics.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), len(DIMENSIONS) * 4)
        self.assertIn('evidence_status', rows[0])
        self.assertTrue(any(row['recommendation'] == 'add_capacity_targeted' for row in rows))

    def test_bundle_without_diagnosis_still_verifies(self):
        records = make_region_dataset()[:4]
        output = self.root / "plain"
        decisions = {record.record_id: decide(record) for record in records}
        snapshot = {'counts': {}, 'ledgers': {}, 'chain_errors': []}
        manifest = export_bundle(output, records, decisions, snapshot, [])
        self.assertEqual(verify_bundle(output), [])
        self.assertEqual(manifest['stratum_rows'], 0)
        summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
        self.assertNotIn('stratified_diagnostics', summary)


class ApplicationWiringTests(unittest.TestCase):
    FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "acceptance.json"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.database = self.root / "run.sqlite3"
        self.output = self.root / "output"

    def test_application_run_embeds_shared_diagnosis(self):
        fixture = json.loads(self.FIXTURE.read_text(encoding="utf-8"))
        application = Application(self.database)
        result = application.run_fixture(fixture, self.output)
        self.assertEqual(result["manifest"]["stratum_rows"], 10)
        summary = json.loads((self.output / "summary.json").read_text(encoding="utf-8"))
        diagnosis = summary["stratified_diagnostics"]
        # Every sparse acceptance stratum must be explicitly untrusted, never "normal".
        self.assertTrue(diagnosis["insufficient_evidence_strata"])
        for dimension in DIMENSIONS:
            for stats in diagnosis["strata"][dimension].values():
                self.assertEqual(stats["evidence_status"], INSUFFICIENT_EVIDENCE)
        # Decisions persisted in the same run carry the shared diagnostic reason.
        decisions = application.inspect()["decisions"]
        self.assertTrue(any(
            any("diagnostic_guard=insufficient_evidence" in reason
                for reason in decision["reasons"])
            for decision in decisions
        ))

    def test_repeated_run_is_idempotent_with_diagnosis(self):
        fixture = json.loads(self.FIXTURE.read_text(encoding="utf-8"))
        first = Application(self.database).run_fixture(fixture, self.output)
        second = Application(self.database).run_fixture(fixture, self.output)
        self.assertEqual(first["run_id"], second["run_id"])
        self.assertEqual(first["manifest"]["manifest_hash"], second["manifest"]["manifest_hash"])


if __name__ == '__main__':
    unittest.main()
