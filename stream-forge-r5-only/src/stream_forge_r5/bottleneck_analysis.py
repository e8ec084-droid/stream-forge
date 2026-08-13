"""Identifies which partition or worker is bottlenecking the pipeline (Mid-Review, Thursday)."""

from dataclasses import dataclass

from stream_forge_r5.throughput_audit import PartitionSample


@dataclass(frozen=True)
class Bottleneck:
    partition: int
    events_per_second: float
    deviation_from_average: float


def find_bottleneck_partitions(
    samples: tuple[PartitionSample, ...],
    deviation_threshold: float = 0.2,
) -> tuple[Bottleneck, ...]:
    """Flags partitions whose throughput trails the group average by more than the threshold."""
    if not samples:
        return ()

    average = mean_events_per_second(samples)
    if average <= 0:
        return ()

    return tuple(
        Bottleneck(
            sample.partition,
            sample.events_per_second,
            (sample.events_per_second - average) / average,
        )
        for sample in samples
        if (average - sample.events_per_second) / average > deviation_threshold
    )


def mean_events_per_second(samples: tuple[PartitionSample, ...]) -> float:
    return sum(sample.events_per_second for sample in samples) / len(samples) if samples else 0.0


def rank_worker_lag(lag_by_worker: dict[str, int]) -> list[tuple[str, int]]:
    """Ranks workers worst-lag-first, so the biggest bottleneck is always index 0."""
    return sorted(lag_by_worker.items(), key=lambda worker_and_lag: worker_and_lag[1], reverse=True)
