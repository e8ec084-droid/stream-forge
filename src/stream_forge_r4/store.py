from rocksdict import Rdict
import json

from stream_forge_r4.config import get_settings
from stream_forge_r4.models import TruckState


class RocksDBStore:
    """Simple wrapper around RocksDict."""

    def __init__(self):
        settings = get_settings()
        self.db = Rdict(settings.db_path)

    def put(self, state: TruckState):
        self.db[state.truck_id] = json.dumps(state.__dict__)

    def get(self, truck_id: str):
        data = self.db.get(truck_id)

        if data is None:
            return None

        return TruckState(**json.loads(data))

    def delete(self, truck_id: str):
        self.db.delete(truck_id)

    def close(self):
        self.db.close()