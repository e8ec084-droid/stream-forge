import time
from typing import Any

from stream_forge_r2.consumer import ConsumerStats, handle_message
from stream_forge_r2.schemas import TelemetryEventV1
from stream_forge_r2.serializers import serialize_model
from stream_forge_r2.topology import TemperatureBounds


class FakeProducer:
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def produce(self, **kwargs: Any) -> None:
        self.records.append(kwargs)

    def poll(self, _timeout: float) -> None:
        return None


def test_handle_message_produces_validated_output() -> None:
    producer = FakeProducer()
    stats = ConsumerStats()
    raw = TelemetryEventV1(
        truck_id="truck-0001",
        temperature_c=10.0,
        timestamp_ms=int(time.time() * 1000),
        source="unit-test",
    )

    handle_message(
        serialize_model(raw),
        producer,  # type: ignore[arg-type]
        "truck.telemetry.validated",
        TemperatureBounds(),
        stats,
    )

    assert stats.consumed == 1
    assert stats.produced == 1
    assert len(producer.records) == 1
    assert producer.records[0]["topic"] == "truck.telemetry.validated"


def test_handle_message_counts_invalid_messages() -> None:
    producer = FakeProducer()
    stats = ConsumerStats()
    handle_message(
        b"not-json",
        producer,  # type: ignore[arg-type]
        "truck.telemetry.validated",
        TemperatureBounds(),
        stats,
    )
    assert stats.invalid == 1
    assert len(producer.records) == 0
