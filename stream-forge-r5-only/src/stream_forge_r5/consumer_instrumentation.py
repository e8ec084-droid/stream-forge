"""Instruments a stream worker with consumption counters and lag (Week 2, Mon+Tue).

These are plain functions, not a class, because instrumentation here is just
"increment a counter" / "set a gauge" — there's no state to hold between
calls, so a class would only add ceremony. ``refresh_consumer_lag`` is kept
separate and pure-ish (it returns what it measured) so it's testable without
asserting against global Prometheus state.
"""

from typing import Protocol

from stream_forge_r5.metrics import (
    CONSUMER_LAG,
    EVENTS_CONSUMED_TOTAL,
    EVENTS_FILTERED_TOTAL,
    EVENTS_INVALID_TOTAL,
)


class HasOffset(Protocol):
    """Confluent Kafka's TopicPartition exposes ``.offset`` — that's all we read from it."""

    offset: int


class SupportsWatermarksAndCommits(Protocol):
    """The subset of confluent_kafka.Consumer that lag calculation needs."""

    def get_watermark_offsets(self, partition: object, cached: bool = False) -> tuple[int, int]: ...
    def committed(self, partitions: list[object], timeout: float = -1) -> list[HasOffset]: ...


def record_consumed(topic: str) -> None:
    EVENTS_CONSUMED_TOTAL.labels(topic=topic).inc()


def record_invalid(topic: str, reason: str) -> None:
    EVENTS_INVALID_TOTAL.labels(topic=topic, reason=reason).inc()


def record_filtered(topic: str) -> None:
    EVENTS_FILTERED_TOTAL.labels(topic=topic).inc()


def refresh_consumer_lag(
    consumer: SupportsWatermarksAndCommits,
    topic: str,
    partitions: list[int],
    topic_partition_factory: type,
) -> dict[int, int]:
    """Computes per-partition lag, publishes it as a gauge, and returns it for callers/tests.

    ``topic_partition_factory`` is injected (rather than importing
    ``confluent_kafka.TopicPartition`` directly) purely so unit tests can
    pass a lightweight stand-in with no Kafka client involved.
    """
    lag_by_partition: dict[int, int] = {}
    for partition in partitions:
        topic_partition = topic_partition_factory(topic, partition)
        _, high_watermark = consumer.get_watermark_offsets(topic_partition, cached=False)
        committed_offset = max(consumer.committed([topic_partition])[0].offset, 0)
        lag = max(high_watermark - committed_offset, 0)
        CONSUMER_LAG.labels(topic=topic, partition=str(partition)).set(lag)
        lag_by_partition[partition] = lag
    return lag_by_partition
