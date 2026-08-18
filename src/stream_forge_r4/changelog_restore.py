import json
import os
from typing import Any

from confluent_kafka import Consumer, KafkaError

from stream_forge_r4.store import RocksDBStore


class ChangelogRestorer:
    """Restore RocksDB state from a Kafka changelog topic."""

    def __init__(
        self,
        store: RocksDBStore,
        bootstrap_servers: str | None = None,
        topic: str | None = None,
        group_id: str | None = None,
    ) -> None:
        self.store = store

        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
        )

        self.topic = topic or os.getenv(
            "KAFKA_CHANGELOG_TOPIC",
            "stream-forge.r4.changelog",
        )

        self.group_id = group_id or os.getenv(
            "KAFKA_RESTORE_GROUP_ID",
            "stream-forge-r4-restore",
        )

    def _consumer(self) -> Consumer:
        """Create a Kafka consumer configured for changelog recovery."""
        return Consumer(
            {
                "bootstrap.servers": self.bootstrap_servers,
                "group.id": self.group_id,
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
            }
        )

    def restore_record(self, record: dict[str, Any]) -> bool:
        """Apply one changelog record to RocksDB."""
        operation = str(record.get("operation", "upsert")).lower()
        truck_id = record.get("truck_id")
        state = record.get("state")

        if not truck_id:
            return False

        if operation in {"delete", "remove"}:
            self.store.delete(str(truck_id))
            return True

        if not isinstance(state, dict):
            return False

        self.store.db[str(truck_id)] = json.dumps(state)
        return True

    def restore_from_changelog(
        self,
        timeout_seconds: float = 5.0,
        max_messages: int | None = None,
    ) -> int:
        """Restore persisted state from Kafka changelog records."""
        consumer = self._consumer()
        restored = 0

        try:
            assert self.topic is not None
            consumer.subscribe([self.topic])

            while max_messages is None or restored < max_messages:
                message = consumer.poll(timeout_seconds)

                if message is None:
                    break

                error = message.error()

                if error is not None:
                    if error.code() == KafkaError._PARTITION_EOF:
                        break

                    raise RuntimeError(str(error))

                raw_value = message.value()

                if raw_value is None:
                    continue

                try:
                    record = json.loads(raw_value.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue

                if not isinstance(record, dict):
                    continue

                if self.restore_record(record):
                    restored += 1

                consumer.commit(
                    message=message,
                    asynchronous=False,
                )

        finally:
            consumer.close()

        return restored


def create_restorer(store: RocksDBStore) -> ChangelogRestorer:
    """Create a changelog restorer using environment settings."""
    return ChangelogRestorer(store=store)
