from __future__ import annotations

import argparse

import uvicorn

from .app import create_app
from .settings import Settings


def main() -> None:
    parser = argparse.ArgumentParser(prog="factorypulse-api")
    parser.add_argument("--data-dir", default="data", help="directory containing warehouse.duckdb, anomalies.jsonl and data_quality_event.json")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(create_app(Settings.from_directory(args.data_dir)), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
