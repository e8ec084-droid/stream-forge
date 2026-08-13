from dataclasses import dataclass

from stream_forge_r5.throughput_audit import (
    AuditResult,
    PartitionSample,
    benchmark_baseline,
    sample_partition_throughput,
)


@dataclass(frozen=True)
class FakeTopicPartition:
    topic: str
    partition: int


class FakeConsumer:
    """Returns a fixed watermark regardless of when it's called, isolating the diff math."""

    def __init__(self, watermark_sequence: dict[int, list[int]]) -> None:
        self._watermark_sequence = watermark_sequence
        self._call_count: dict[int, int] = dict.fromkeys(watermark_sequence, 0)

    def get_watermark_offsets(
        self, partition: FakeTopicPartition, cached: bool = False
    ) -> tuple[int, int]:
        call_index = self._call_count[partition.partition]
        self._call_count[partition.partition] += 1
        return 0, self._watermark_sequence[partition.partition][call_index]


def test_sample_partition_throughput_computes_rate(monkeypatch) -> None:
    monkeypatch.setattr("stream_forge_r5.throughput_audit.sleep", lambda seconds: None)
    consumer = FakeConsumer({0: [1000, 1500], 1: [2000, 2200]})

    samples = sample_partition_throughput(
        consumer, "t", [0, 1], FakeTopicPartition, sample_seconds=5.0
    )

    assert samples == (PartitionSample(0, 100.0), PartitionSample(1, 40.0))


def test_audit_result_aggregates_and_flags_pass() -> None:
    result = AuditResult(
        target_events_per_second=100,
        partitions=(PartitionSample(0, 60.0), PartitionSample(1, 50.0)),
    )

    assert result.total_events_per_second == 110.0
    assert result.passed is True


def test_audit_result_flags_failure_below_target() -> None:
    result = AuditResult(target_events_per_second=100, partitions=(PartitionSample(0, 30.0),))

    assert result.passed is False


def test_benchmark_baseline_aggregates_samples() -> None:
    summary = benchmark_baseline([90.0, 100.0, 110.0])

    assert summary == {"min": 90.0, "max": 110.0, "mean": 100.0, "samples_count": 3}
