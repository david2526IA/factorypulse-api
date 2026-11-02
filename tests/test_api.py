import json
import uuid

import duckdb
from fastapi.testclient import TestClient

from factorypulse_api.app import create_app
from factorypulse_api.settings import Settings


def _settings(tmp_path) -> Settings:
    database = tmp_path / "warehouse.duckdb"
    connection = duckdb.connect(str(database))
    connection.execute("CREATE TABLE silver_telemetry(event_id UUID, occurred_at TIMESTAMPTZ, asset_id VARCHAR, temperature_c DOUBLE, vibration_mm_s DOUBLE, pressure_bar DOUBLE, power_kw DOUBLE, source VARCHAR)")
    connection.execute("INSERT INTO silver_telemetry VALUES (?, '2026-01-01T00:00:00Z', 'PUMP-01', 63, 2.7, 7.4, 18.0, 'test')", [str(uuid.uuid4())])
    connection.execute("CREATE TABLE gold_asset_health(hour TIMESTAMPTZ, asset_id VARCHAR, readings INTEGER, avg_temperature_c DOUBLE, avg_vibration_mm_s DOUBLE, avg_pressure_bar DOUBLE, avg_power_kw DOUBLE, critical_signal_count INTEGER)")
    connection.execute("INSERT INTO gold_asset_health VALUES ('2026-01-01T00:00:00Z', 'PUMP-01', 1, 63, 2.7, 7.4, 18.0, 0)")
    connection.close()
    anomaly = {"event_id": str(uuid.uuid4()), "event_type": "factorypulse.anomaly", "schema_version": "1.0", "occurred_at": "2026-01-01T00:00:00Z", "asset_id": "PUMP-01", "severity": "warning", "score": 4.2, "reasons": ["vibration robust-z=4.20"]}
    anomalies = tmp_path / "anomalies.jsonl"
    anomalies.write_text(json.dumps(anomaly) + "\ninvalid-json", encoding="utf-8")
    quality = tmp_path / "data_quality_event.json"
    quality.write_text(json.dumps({"event_id": str(uuid.uuid4()), "event_type": "factorypulse.data_quality", "schema_version": "1.0", "occurred_at": "2026-01-01T00:00:00Z", "pipeline": "test", "accepted_rows": 1, "rejected_rows": 0}), encoding="utf-8")
    return Settings(database, anomalies, quality)


def test_summary_composes_validated_upstream_outputs(tmp_path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    response = client.get("/v1/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["anomaly_count"] == 1
    assert body["invalid_anomaly_records"] == 1
    assert body["asset_health"][0]["asset_id"] == "PUMP-01"


def test_telemetry_limit_is_bounded(tmp_path) -> None:
    client = TestClient(create_app(_settings(tmp_path)))
    assert len(client.get("/v1/telemetry?limit=1").json()) == 1
    assert client.get("/v1/telemetry?limit=501").status_code == 422
