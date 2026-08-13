from stream_forge_r2.state_store import StateStore


def test_state_survives_restart(tmp_path):
    snapshot_file = tmp_path / "state_snapshot.json"

    store_before_restart = StateStore(snapshot_path=str(snapshot_file))
    store_before_restart.put("truck-0001", {"temperature_c": 21.5})

    store_after_restart = StateStore(snapshot_path=str(snapshot_file))

    assert store_after_restart.get("truck-0001") == {"temperature_c": 21.5}


def test_missing_truck_returns_none(tmp_path):
    snapshot_file = tmp_path / "state_snapshot.json"
    store = StateStore(snapshot_path=str(snapshot_file))

    assert store.get("truck-9999") is None