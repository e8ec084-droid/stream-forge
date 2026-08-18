import json
import os
from collections.abc import Iterable, Iterator
from typing import Any, cast

from confluent_kafka import Producer

from stream_forge_r4.store import RocksDBStore

CHANGELOG_PREFIX = "__changelog__:"


class ChangelogBackup:
    """Publish persisted RocksDB changelog entries to Kafka."""

    def __init__(
        self,
        store: RocksDBStore,
        producer: Producer,
        topic: str,
    ) -> None:
        self.store = store
        self.producer = producer
        self.topic = topic

    def iter_changelog(self) -> Iterator[tuple[str, Any]]:
        """Yield persisted changelog entries from RocksDB."""
        db = cast(Iterable[bytes | str], self.store.db)

        for raw_key in db:
            key = (
                raw_key.decode()
                if isinstance(raw_key, bytes)
                else str(raw_key)
            )

            if not key.startswith(CHANGELOG_PREFIX):
                continue

            raw_value = self.store.db.get(raw_key)

            if raw_value is None:
                continue

            value = (
                raw_value.decode()
                if isinstance(raw_value, bytes)
                else str(raw_value)
            )

            yield key, json.loads(value)

    def backup(self) -> int:
        """Publish all persisted changelog entries to Kafka."""
        count = 0

        for changelog_key, entry in self.iter_changelog():
            truck_id = entry.get("truck_id")

            self.producer.produce(
                topic=self.topic,
                key=str(truck_id) if truck_id is not None else changelog_key,
                value=json.dumps(entry),
            )

            self.producer.poll(0)
            count += 1

        self.producer.flush()

        return count


def create_backup(store: RocksDBStore) -> ChangelogBackup:
    """Create a Kafka-backed changelog backup using environment settings."""
    bootstrap_servers = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092",
    )

    topic = os.getenv(
        "KAFKA_CHANGELOG_TOPIC",
        "stream-forge.r4.changelog",
    )

    producer = Producer(
        {
            "bootstrap.servers": bootstrap_servers,
        }
    )

    return ChangelogBackup(
        store=store,
        producer=producer,
        topic=topic,
    )