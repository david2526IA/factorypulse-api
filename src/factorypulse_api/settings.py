from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    lakehouse_db: Path
    anomalies_jsonl: Path
    quality_event_json: Path

    @classmethod
    def from_directory(cls, directory: str | Path) -> "Settings":
        root = Path(directory)
        return cls(root / "warehouse.duckdb", root / "anomalies.jsonl", root / "data_quality_event.json")
