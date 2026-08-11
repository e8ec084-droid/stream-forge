import json

from rocksdict import Rdict

from stream_forge_r4.config import get_settings
from stream_forge_r4.models import TruckState


class RocksDBStore:
    """Simple wrapper around RocksDict."""

    def __init__(self):
        settings = get_settings()
        self.db = Rdict(settings.db_path)

    def put(self, state: TruckState):
        self.db[state.truck_id] = json.dumps(state.__dict__)  

    def put_window_result(
        self,
        truck_id: str,
        avg_temperature: float,
        event_count: int,
        window_start: int,
        window_end: int,
        status: str = "healthy",
    ):
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

    def get(self, truck_id: str):
        data = self.db.get(truck_id)

        if data is None:
            return None

        return TruckState(**json.loads(data))

    def delete(self, truck_id: str):
        self.db.delete(truck_id)

    def close(self):
        self.db.close()