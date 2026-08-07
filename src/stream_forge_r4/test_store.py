from stream_forge_r4.store import RocksDBStore
from stream_forge_r4.models import TruckState

store = RocksDBStore()

state = TruckState(
    truck_id="truck-001",
    last_temperature=25.0,
    event_count=1,
    last_timestamp=1723120000,
    status="healthy",
)

store.put(state)

loaded = store.get("truck-001")

print(loaded)

store.delete("truck-001")

print("Deleted successfully!")

store.close()