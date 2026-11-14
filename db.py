import json
from pathlib import Path
from typing import Any, Iterable

from npc import Npc


DATABASE_PATH = Path(__file__).with_name("db.json")


def load_npcs(database_path: str | Path = DATABASE_PATH) -> list[dict[str, Any]]:
    path = Path(database_path)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as database_file:
        records = json.load(database_file)

    if not isinstance(records, list):
        raise ValueError(f"Expected a JSON array in {path}")
    return records


def add_npcs(npcs: Iterable[Npc], database_path: str | Path = DATABASE_PATH) -> None:
    path = Path(database_path)
    records = load_npcs(path)
    records.extend(
        {
            "name": npc.name,
            "race": npc.race,
            "nationality": npc.nationality,
            "stats": npc.stats,
            "tendencies": npc.tendencies,
        }
        for npc in npcs
    )

    with path.open("w", encoding="utf-8") as database_file:
        json.dump(records, database_file, indent=2)
