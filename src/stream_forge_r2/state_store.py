import json
from pathlib import Path


class StateStore:
    def __init__(self, snapshot_path: str = "state_snapshot.json"):
        self._store: dict[str, dict] = {}
        self._snapshot_path = Path(snapshot_path)
        self._load_from_disk()

    def get(self, truck_id: str) -> dict | None:
        return self._store.get(truck_id)

    def put(self, truck_id: str, event: dict) -> None:
        self._store[truck_id] = event
        self._save_to_disk()

    def _save_to_disk(self) -> None:
        self._snapshot_path.write_text(json.dumps(self._store))

    def _load_from_disk(self) -> None:
        if self._snapshot_path.exists():
            self._store = json.loads(self._snapshot_path.read_text())