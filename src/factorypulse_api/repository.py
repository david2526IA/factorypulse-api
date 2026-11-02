"""Read-only access adapters for upstream FactoryPulse artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb

from factorypulse_contracts import validate_event

from .settings import Settings


def _query(database: Path, sql: str, params: list[object] | None = None) -> list[dict[str, object]]:
    if not database.exists():
        return []
    connection = duckdb.connect(str(database), read_only=True)
    try:
        cursor = connection.execute(sql, params or [])
        names = [column[0] for column in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]
    finally:
        connection.close()


def telemetry(settings: Settings, limit: int) -> list[dict[str, object]]:
    return _query(settings.lakehouse_db, "SELECT event_id::VARCHAR AS event_id, strftime(occurred_at AT TIME ZONE 'UTC', '%Y-%m-%dT%H:%M:%SZ') AS occurred_at, asset_id, temperature_c, vibration_mm_s, pressure_bar, power_kw, source FROM silver_telemetry ORDER BY occurred_at DESC LIMIT ?", [limit])


def asset_health(settings: Settings) -> list[dict[str, object]]:
    return _query(settings.lakehouse_db, "SELECT strftime(hour AT TIME ZONE 'UTC', '%Y-%m-%dT%H:%M:%SZ') AS hour, asset_id, readings, avg_temperature_c, avg_vibration_mm_s, avg_pressure_bar, avg_power_kw, critical_signal_count FROM gold_asset_health ORDER BY hour DESC, asset_id")


def anomalies(settings: Settings) -> dict[str, object]:
    if not settings.anomalies_jsonl.exists():
        return {"events": [], "invalid_records": 0}
    events, invalid = [], 0
    for raw in settings.anomalies_jsonl.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(raw)
            validate_event("anomaly.v1", event)
            events.append(event)
        except Exception:
            invalid += 1
    return {"events": events, "invalid_records": invalid}


def quality(settings: Settings) -> dict[str, object] | None:
    if not settings.quality_event_json.exists():
        return None
    event = json.loads(settings.quality_event_json.read_text(encoding="utf-8"))
    validate_event("data-quality.v1", event)
    return event
