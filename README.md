# FactoryPulse API

> Read-only FastAPI service that composes FactoryPulse telemetry, anomaly and data-quality outputs.

[![API CI](https://github.com/david2526IA/factorypulse-api/actions/workflows/ci.yml/badge.svg)](https://github.com/david2526IA/factorypulse-api/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Contracts](https://img.shields.io/badge/validated-FactoryPulse%20Contracts-2563EB)](https://github.com/david2526IA/factorypulse-contracts)

FactoryPulse API is the read-only integration boundary for the FactoryPulse reference platform. It reads the validated lakehouse database, anomaly JSONL and pipeline-quality event, then exposes a concise operational view for a dashboard or external client.

## Endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Component availability without exposing internal files. |
| `GET /v1/summary` | Asset health, anomaly count and last pipeline-quality event. |
| `GET /v1/telemetry?limit=50` | Recent silver telemetry, bounded to 500 records. |
| `GET /v1/anomalies` | Valid anomaly events and count of malformed records. |
| `GET /v1/data-quality` | Last validated `data_quality.v1` event. |

## Data boundary

```text
FactoryPulse Lakehouse ── warehouse.duckdb + data_quality_event.json ─┐
FactoryPulse Intelligence ── anomalies.jsonl ─────────────────────────┼──► FactoryPulse API
                                                                        │          │
                                                                        └──► dashboard / client
```

The API is intentionally **read-only**. It cannot issue a command to equipment, modify the lakehouse or acknowledge alarms. This separation is deliberate: an operational display must not become an unreviewed control channel.

## Quick start

Prepare a directory containing these three artifacts:

```text
data/
├── warehouse.duckdb          # FactoryPulse Lakehouse
├── data_quality_event.json   # FactoryPulse Lakehouse
└── anomalies.jsonl           # FactoryPulse Intelligence
```

```bash
git clone https://github.com/david2526IA/factorypulse-api.git
cd factorypulse-api
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -e ".[dev]"
factorypulse-api --data-dir data
pytest -q
```

Browse interactive documentation at `http://127.0.0.1:8000/docs`.

## Container run

```bash
docker build -t factorypulse-api .
docker run --rm -p 8000:8000 -v "${PWD}/data:/data:ro" factorypulse-api
```

## Production considerations

This repository is a portfolio/reference API. A production implementation needs authentication/authorisation, network policy, audit trails, rate limiting, secret management, observability and an explicit safety review before it is connected to any real operational environment.

## License

MIT © 2026 David
