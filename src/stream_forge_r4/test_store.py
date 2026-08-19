from collections.abc import Iterator

import pytest

from stream_forge_r4.models import TruckState
from stream_forge_r4.store import RocksDBStore


@pytest.fixture
def store() -> Iterator[RocksDBStore]:
    store = RocksDBStore()
    yield store
    store.delete("test-truck-001")
    store.close()


def test_put_and_get(store: RocksDBStore) -> None:
    state = TruckState(
        truck_id="test-truck-001",
        avg_temperature=25.0,
        event_count=1,
        window_start=1723120000,
        window_end=1723120060,
        status="healthy",
    )

    store.put(state)

    result = store.get("test-truck-001")

    assert result == state


def test_get_missing_returns_none(store: RocksDBStore) -> None:
    result = store.get("does-not-exist")

    assert result is None


def test_delete(store: RocksDBStore) -> None:
    state = TruckState(
        truck_id="test-truck-001",
        avg_temperature=25.0,
        event_count=1,
        window_start=1723120000,
        window_end=1723120060,
        status="healthy",
    )

    store.put(state)
    store.delete("test-truck-001")

    result = store.get("test-truck-001")

    assert result is None


def test_put_window_result(store: RocksDBStore) -> None:
    store.put_window_result(
        truck_id="test-truck-window",
        avg_temperature=27.5,
        event_count=10,
        window_start=1723120000,
        window_end=1723120060,
        status="healthy",
    )

    result = store.get("test-truck-window")

    assert result is not None
    assert result.truck_id == "test-truck-window"
    assert result.avg_temperature == 27.5
    assert result.event_count == 10
    assert result.window_start == 1723120000
    assert result.window_end == 1723120060
    assert result.status == "healthy"

    store.delete("test-truck-window")


def test_write_and_get_changelog(store: RocksDBStore) -> None:
    state = TruckState(
        truck_id="test-truck-changelog",
        avg_temperature=28.5,
        event_count=5,
        window_start=1723120000,
        window_end=1723120060,
        status="healthy",
    )

    key = store.write_changelog(state)

    entry = store.get_changelog(key)

    assert entry is not None
    assert entry["operation"] == "upsert"
    assert entry["truck_id"] == "test-truck-changelog"
    assert entry["state"]["avg_temperature"] == 28.5
    assert entry["state"]["event_count"] == 5


def test_state_read_latency(store: RocksDBStore) -> None:
    state = TruckState(
        truck_id="latency-truck-001",
        avg_temperature=26.5,
        event_count=10,
        window_start=1723120000,
        window_end=1723120060,
        status="healthy",
    )

    store.put(state)

    import time

    start = time.perf_counter()

    for _ in range(100):
        result = store.get("latency-truck-001")
        assert result is not None

    elapsed = time.perf_counter() - start

    assert elapsed < 1.0

    store.delete("latency-truck-001")


def test_sustained_updates_consistency(store: RocksDBStore) -> None:
    truck_id = "sustained-truck-001"

    for i in range(500):
        state = TruckState(
            truck_id=truck_id,
            avg_temperature=20.0 + i,
            event_count=i,
            window_start=1723120000 + i,
            window_end=1723120060 + i,
            status="healthy",
        )

        store.put(state)

        result = store.get(truck_id)

        assert result is not None
        assert result.truck_id == truck_id
        assert result.avg_temperature == 20.0 + i
        assert result.event_count == i
        assert result.window_start == 1723120000 + i
        assert result.window_end == 1723120060 + i
        assert result.status == "healthy"

    store.delete(truck_id)

    assert store.get(truck_id) is None


def test_changelog_integrity(store: RocksDBStore) -> None:
    entries = []

    for i in range(10):
        state = TruckState(
            truck_id=f"changelog-truck-{i}",
            avg_temperature=20.0 + i,
            event_count=i,
            window_start=1723120000 + i,
            window_end=1723120060 + i,
            status="healthy",
        )

        key = store.write_changelog(state)
        entry = store.get_changelog(key)

        assert entry is not None
        assert entry["operation"] == "upsert"
        assert entry["truck_id"] == state.truck_id

        entries.append(entry)

    sequences = [entry["sequence"] for entry in entries]

    assert len(set(sequences)) == len(sequences)
    assert sequences == sorted(sequences)

def test_get_size_bytes(store: RocksDBStore) -> None:
    state = TruckState(
        truck_id="size-test-truck",
        avg_temperature=25.0,
        event_count=1,
        window_start=1723120000,
        window_end=1723120060,
        status="healthy",
    )

    store.put(state)

    size = store.get_size_bytes()

    assert isinstance(size, int)
    assert size >= 0
def test_state_store_stress_at_scale(store: RocksDBStore) -> None:
    records = 5000

    states = [
        TruckState(
            truck_id=f"stress-truck-{i}",
            avg_temperature=20.0 + (i % 50),
            event_count=i,
            window_start=1723120000 + i,
            window_end=1723120060 + i,
            status="healthy",
        )
        for i in range(records)
    ]

    # Write a large number of state records
    for state in states:
        store.put(state)

    # Verify all records can be read back correctly
    for state in states:
        result = store.get(state.truck_id)

        assert result is not None
        assert result.truck_id == state.truck_id
        assert result.avg_temperature == state.avg_temperature
        assert result.event_count == state.event_count

    # Verify the state store contains data
    size = store.get_size_bytes()
    assert isinstance(size, int)
    assert size > 0

    # Clean up stress-test records
    for state in states:
    store.delete(state.truck_id)