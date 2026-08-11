import pytest

from stream_forge_r4.store import RocksDBStore
from stream_forge_r4.models import TruckState


@pytest.fixture
def store():
    store = RocksDBStore()
    yield store
    store.delete("test-truck-001")
    store.close()


def test_put_and_get(store):
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


def test_get_missing_returns_none(store):
    result = store.get("does-not-exist")

    assert result is None


def test_delete(store):
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
def test_put_window_result(store):
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