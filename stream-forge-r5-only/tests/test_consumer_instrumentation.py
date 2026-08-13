from dataclasses import dataclass

from stream_forge_r5.consumer_instrumentation import (
    record_consumed,
    record_filtered,
    record_invalid,
    refresh_consumer_lag,
)
from stream_forge_r5.metrics import (
    CONSUMER_LAG,
    EVENTS_CONSUMED_TOTAL,
    EVENTS_FILTERED_TOTAL,
    EVENTS_INVALID_TOTAL,
)


@dataclass(frozen=True)
class FakeTopicPartition:
    topic: str
    partition: int


@dataclass(frozen=True)
class FakeCommit:
    offset: int


class FakeConsumer:
    def __init__(self, watermarks: dict[int, int], committed_offsets: dict[int, int]) -> None:
        self._watermarks = watermarks
        self._committed_offsets = committed_offsets

    def get_watermark_offsets(
        self, partition: FakeTopicPartition, cached: bool = False
    ) -> tuple[int, int]:
        return 0, self._watermarks[partition.partition]

    def committed(
        self, partitions: list[FakeTopicPartition], timeout: float = -1
    ) -> list[FakeCommit]:
        return [
            FakeCommit(self._committed_offsets[partition.partition]) for partition in partitions
        ]


def test_record_functions_increment_expected_counters() -> None:
    before = EVENTS_CONSUMED_TOTAL.labels(topic="t")._value.get()
    record_consumed("t")
    assert EVENTS_CONSUMED_TOTAL.labels(topic="t")._value.get() == before + 1

    before = EVENTS_INVALID_TOTAL.labels(topic="t", reason="bad_schema")._value.get()
    record_invalid("t", "bad_schema")
    assert EVENTS_INVALID_TOTAL.labels(topic="t", reason="bad_schema")._value.get() == before + 1

    before = EVENTS_FILTERED_TOTAL.labels(topic="t")._value.get()
    record_filtered("t")
    assert EVENTS_FILTERED_TOTAL.labels(topic="t")._value.get() == before + 1


def test_refresh_consumer_lag_computes_and_publishes_gauge() -> None:
    consumer = FakeConsumer(watermarks={0: 1000, 1: 500}, committed_offsets={0: 900, 1: 500})

    lag_by_partition = refresh_consumer_lag(consumer, "t", [0, 1], FakeTopicPartition)

    assert lag_by_partition == {0: 100, 1: 0}
    assert CONSUMER_LAG.labels(topic="t", partition="0")._value.get() == 100
    assert CONSUMER_LAG.labels(topic="t", partition="1")._value.get() == 0
