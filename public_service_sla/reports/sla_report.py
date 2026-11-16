from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from public_service_sla.telemetry.service_event import Decision, DomainRecord, canonical_json, stable_hash, utc_now


def ensure_output(path: str | Path) -> Path:
    output = Path(path)
    output.mkdir(parents=True, exist_ok=True)
    return output


def write_json(path: Path, value: Any) -> str:
    body = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)
    path.write_text(body + "\n", encoding="utf-8")
    return stable_hash(value)


def write_records(path: Path, records: Iterable[DomainRecord], decisions: Mapping[str, Decision]) -> int:
    rows = []
    for record in records:
        decision = decisions.get(record.record_id)
        rows.append({"record_id": record.record_id, "ledger": record.ledger, "version": record.version,
                     "source": record.source, "fingerprint": record.fingerprint,
                     "outcome": decision.outcome if decision else "", "score": decision.score if decision else ""})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["record_id", "ledger", "version", "source", "fingerprint", "outcome", "score"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_rules(path: Path, decisions: Mapping[str, Decision]) -> int:
    count = 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["record_id", "code", "passed", "score", "severity", "message"])
        writer.writeheader()
        for record_id, decision in sorted(decisions.items()):
            for result in decision.rule_results:
                writer.writerow({"record_id": record_id, "code": result.code, "passed": result.passed,
                                 "score": result.score, "severity": result.severity, "message": result.message})
                count += 1
    return count


def write_strata(path: Path, diagnosis: Any) -> int:
    """Write one row per region/user-group stratum with its trust and evidence."""
    if diagnosis is None:
        return 0
    body = diagnosis.as_dict() if hasattr(diagnosis, "as_dict") else diagnosis
    fieldnames = [
        "dimension", "key", "evidence_status", "samples", "trusted_samples",
        "defective_samples", "coverage", "total_request_queue", "mean_request_queue",
        "mean_queue_pressure", "mean_response_ms", "effective_response_rate",
        "mean_error_rate", "anomaly_rate", "data_defect_rate", "total_capacity",
        "mean_capacity_occupancy", "saturated_rate", "persistent_breach_rate",
        "drivers", "recommendation", "recommendation_message", "evidence_reasons",
    ]
    count = 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for dimension, strata in sorted(body.get("strata", {}).items()):
            for key, stats in sorted(strata.items()):
                writer.writerow({
                    "dimension": dimension,
                    "key": key,
                    "evidence_status": stats.get("evidence_status", ""),
                    "samples": stats.get("samples", 0),
                    "trusted_samples": stats.get("trusted_samples", 0),
                    "defective_samples": stats.get("defective_samples", 0),
                    "coverage": stats.get("coverage", 0.0),
                    "total_request_queue": stats.get("total_request_queue", 0.0),
                    "mean_request_queue": stats.get("mean_request_queue", 0.0),
                    "mean_queue_pressure": stats.get("mean_queue_pressure", 0.0),
                    "mean_response_ms": stats.get("mean_response_ms", 0.0),
                    "effective_response_rate": stats.get("effective_response_rate", 0.0),
                    "mean_error_rate": stats.get("mean_error_rate", 0.0),
                    "anomaly_rate": stats.get("anomaly_rate", 0.0),
                    "data_defect_rate": stats.get("data_defect_rate", 0.0),
                    "total_capacity": stats.get("total_capacity", 0.0),
                    "mean_capacity_occupancy": stats.get("mean_capacity_occupancy", 0.0),
                    "saturated_rate": stats.get("saturated_rate", 0.0),
                    "persistent_breach_rate": stats.get("persistent_breach_rate", 0.0),
                    "drivers": "|".join(stats.get("drivers", [])),
                    "recommendation": stats.get("recommendation", ""),
                    "recommendation_message": stats.get("recommendation_message", ""),
                    "evidence_reasons": "|".join(stats.get("evidence_reasons", [])),
                })
                count += 1
    return count


def build_summary(records: list[DomainRecord], decisions: Mapping[str, Decision],
                  snapshot: Mapping[str, Any], diagnosis: Any = None) -> dict[str, Any]:
    outcomes: dict[str, int] = {}
    for decision in decisions.values():
        outcomes[decision.outcome] = outcomes.get(decision.outcome, 0) + 1
    scores = [decision.score for decision in decisions.values()]
    summary = {"product": '国际人工智能公共产品服务水平观测台', "entity": 'service_window', "generated_at": utc_now(),
               "record_count": len(records), "decision_count": len(decisions), "outcomes": outcomes,
               "average_score": sum(scores) / len(scores) if scores else 0.0,
               "minimum_score": min(scores) if scores else 0.0, "maximum_score": max(scores) if scores else 0.0,
               "repository": snapshot}
    if diagnosis is not None:
        body = diagnosis.as_dict() if hasattr(diagnosis, "as_dict") else diagnosis
        summary["stratified_diagnostics"] = body
    return summary


def export_bundle(output: str | Path, records: list[DomainRecord], decisions: Mapping[str, Decision],
                  snapshot: Mapping[str, Any], telemetry: list[dict[str, Any]],
                  diagnosis: Any = None) -> dict[str, Any]:
    root = ensure_output(output)
    summary = build_summary(records, decisions, snapshot, diagnosis)
    record_count = write_records(root / "records.csv", records, decisions)
    rule_count = write_rules(root / "rules.csv", decisions)
    stratum_count = write_strata(root / "stratified-diagnostics.csv", diagnosis)
    summary_hash = write_json(root / "summary.json", summary)
    decision_hash = write_json(root / "decisions.json", [value.as_dict() for _, value in sorted(decisions.items())])
    event_hash = write_json(root / "audit-telemetry.json", telemetry)
    manifest = {"files": {"summary.json": summary_hash, "decisions.json": decision_hash,
                           "audit-telemetry.json": event_hash}, "record_rows": record_count,
                "rule_rows": rule_count, "stratum_rows": stratum_count, "created_at": utc_now()}
    manifest["manifest_hash"] = stable_hash(manifest)
    write_json(root / "manifest.json", manifest)
    return manifest


def verify_bundle(output: str | Path) -> list[str]:
    root = Path(output)
    errors: list[str] = []
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        return ["manifest.json is missing"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_manifest_hash = manifest.pop("manifest_hash", "")
    if stable_hash(manifest) != expected_manifest_hash:
        errors.append("manifest hash mismatch")
    for name, expected in manifest.get("files", {}).items():
        path = root / name
        if not path.is_file():
            errors.append(f"{name} is missing")
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        if stable_hash(value) != expected:
            errors.append(f"{name} hash mismatch")
    return errors
