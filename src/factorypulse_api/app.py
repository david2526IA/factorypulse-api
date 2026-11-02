from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from .repository import anomalies, asset_health, quality, telemetry
from .settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="FactoryPulse API", version="0.1.0", description="Read-only API over validated FactoryPulse outputs.")

    @app.get("/health")
    def health() -> dict[str, object]:
        components = {"lakehouse": settings.lakehouse_db.exists(), "anomalies": settings.anomalies_jsonl.exists(), "data_quality": settings.quality_event_json.exists()}
        return {"status": "ok" if all(components.values()) else "degraded", "components": components}

    @app.get("/v1/summary")
    def summary() -> dict[str, object]:
        detected = anomalies(settings)
        return {"asset_health": asset_health(settings), "anomaly_count": len(detected["events"]), "invalid_anomaly_records": detected["invalid_records"], "data_quality": quality(settings)}

    @app.get("/v1/telemetry")
    def get_telemetry(limit: int = Query(default=50, ge=1, le=500)) -> list[dict[str, object]]:
        return telemetry(settings, limit)

    @app.get("/v1/anomalies")
    def get_anomalies() -> dict[str, object]:
        return anomalies(settings)

    @app.get("/v1/data-quality")
    def get_quality() -> dict[str, object]:
        event = quality(settings)
        if event is None:
            raise HTTPException(status_code=404, detail="No data quality event is mounted")
        return event

    return app
