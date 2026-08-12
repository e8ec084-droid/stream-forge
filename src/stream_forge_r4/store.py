import json
import time
from typing import Any, cast

from rocksdict import Rdict

from stream_forge_r4.config import get_settings
from stream_forge_r4.models import TruckState


class RocksDBStore:
    """Simple wrapper around RocksDict."""

    CHANGELOG_PREFIX = "__changelog__:"

    def __init__(self) -> None:
        settings = get_settings()
        self.db = Rdict(settings.db_path)

    def put(self, state: TruckState) -> None:
        self.db[state.truck_id] = json.dumps(state.__dict__)

    def put_window_result(
        self,
        truck_id: str,
        avg_temperature: float,
        event_count: int,
        window_start: int,
        window_end: int,
        status: str = "healthy",
    ) -> None:
        """Persist the latest aggregated window result for a truck."""
        state = TruckState(
            truck_id=truck_id,
            avg_temperature=avg_temperature,
            event_count=event_count,
            window_start=window_start,
            window_end=window_end,
            status=status,
        )

        self.put(state)

    def write_changelog(
        self,
        state: TruckState,
        operation: str = "upsert",
    ) -> str:
        """Persist a changelog entry for a state change.

        The entry is stored locally so a later recovery layer can publish
        the same serialized record to Kafka.
        """
        sequence = time.time_ns()
        key = f"{self.CHANGELOG_PREFIX}{sequence}"

        entry: dict[str, Any] = {
            "sequence": sequence,
            "operation": operation,
            "truck_id": state.truck_id,
            "state": state.__dict__,
        }

        self.db[key] = json.dumps(entry)
        return key

    def get_changelog(self, key: str) -> dict[str, Any] | None:
        """Read a previously persisted changelog entry."""
        data = self.db.get(key)

        if data is None:
            return None

        return cast(dict[str, Any], json.loads(data))
    def get(self, truck_id: str) -> TruckState | None:
        data = self.db.get(truck_id)

        if data is None:
            return None

        return TruckState(**json.loads(data))

    def delete(self, truck_id: str) -> None:
        self.db.delete(truck_id)

    def close(self) -> None:
        self.db.close()