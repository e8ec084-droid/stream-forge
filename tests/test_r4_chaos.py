from collections.abc import Generator
from typing import cast

import pytest

from chaos_helpers import inject_failure
from stream_forge_r4.models import TruckState
from stream_forge_r4.store import RocksDBStore


@pytest.fixture
def store() -> Generator[RocksDBStore, None, None]:
    db = RocksDBStore()
    yield db
    db.close()


def test_prepare_write_failure_injection(store: RocksDBStore) -> None:
    with inject_failure(store, "put"), pytest.raises(RuntimeError, match="injected chaos failure"):
        store.put(cast(TruckState, None))


def test_prepare_read_failure_injection(store: RocksDBStore) -> None:
    with inject_failure(store, "get"), pytest.raises(RuntimeError, match="injected chaos failure"):
        store.get("chaos-test")
