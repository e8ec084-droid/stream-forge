"""Throughput audit tooling.

Covers three related deliverables with one small module instead of three:
- Week 2 Thursday: benchmark and record a baseline throughput.
- Mid-Project Review Mon-Tue: execute the audit, capture events/sec per partition.
- Mid-Project Review Wednesday: aggregate the captured numbers into one result.

``AuditResult`` and ``PartitionSample`` are frozen dataclasses (not Pydantic)
because they're internal compute results with no external input to
validate — Pydantic's validation overhead buys nothing here, unlike in
R2's ``schemas.py`` where payloads come from Kafka and must be checked.
"""

from dataclasses import dataclass, field
from statistics import mean
from time import sleep
from typing import Protocol


class SupportsWatermarks(Protocol):
    """The one method throughput sampling needs from a Kafka consumer."""

    def get_watermark_offsets(self, partition: object, cached: bool = False) -> tuple[int, int]: ...


@dataclass(frozen=True)
class PartitionSample:
    partition: int
    events_per_second: float


@dataclass(frozen=True)
class AuditResult:
    target_events_per_second: int
    partitions: tuple[PartitionSample, ...]
    total_events_per_second: float = field(init=False)
    passed: bool = field(init=False)

    def __post_init__(self) -> None:
        total = sum(sample.events_per_second for sample in self.partitions)
        object.__setattr__(self, "total_events_per_second", total)
        object.__setattr__(self, "passed", total >= self.target_events_per_second)


def sample_partition_throughput(
    consumer: SupportsWatermarks,
    topic: str,
    partitions: list[int],
    topic_partition_factory: type,
    sample_seconds: float = 5.0,
) -> tuple[PartitionSample, ...]:
    """Captures events/sec per partition by diffing high-watermark offsets over a window."""
    start_offsets = _read_high_watermarks(consumer, topic, partitions, topic_partition_factory)
    sleep(sample_seconds)
    end_offsets = _read_high_watermarks(consumer, topic, partitions, topic_partition_factory)

    return tuple(
        PartitionSample(
            partition=partition,
            events_per_second=(end_offsets[partition] - start_offsets[partition]) / sample_seconds,
        )
        for partition in partitions
    )


def _read_high_watermarks(
    consumer: SupportsWatermarks,
    topic: str,
    partitions: list[int],
    topic_partition_factory: type,
) -> dict[int, int]:
    return {
        partition: consumer.get_watermark_offsets(
            topic_partition_factory(topic, partition), cached=False
        )[1]
        for partition in partitions
    }


def run_throughput_audit(
    consumer: SupportsWatermarks,
    topic: str,
    partitions: list[int],
    target_events_per_second: int,
    topic_partition_factory: type,
    sample_seconds: float = 5.0,
) -> AuditResult:
    """Executes the full audit: sample every partition, then aggregate against the target."""
    samples = sample_partition_throughput(
        consumer, topic, partitions, topic_partition_factory, sample_seconds
    )
    return AuditResult(target_events_per_second=target_events_per_second, partitions=samples)


def benchmark_baseline(samples: list[float]) -> dict[str, float]:
    """Aggregates repeated throughput samples into a baseline summary (Week 2 Thursday)."""
    return {
        "min": min(samples),
        "max": max(samples),
        "mean": mean(samples),
        "samples_count": len(samples),
    }
