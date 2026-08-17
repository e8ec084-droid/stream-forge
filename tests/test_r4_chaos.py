import pytest

from chaos_helpers import inject_failure
from stream_forge_r4.store import RocksDBStore


@pytest.fixture
def store():
    db = RocksDBStore()
    yield db
    db.close()


def test_prepare_write_failure_injection(store):
    with inject_failure(store, "put"), pytest.raises(
        RuntimeError, match="injected chaos failure"
    ):
        store.put(None)


def test_prepare_read_failure_injection(store):
    with inject_failure(store, "get"), pytest.raises(
        RuntimeError, match="injected chaos failure"
    ):
        store.get("chaos-test")
