from stream_forge_r5.bottleneck_analysis import find_bottleneck_partitions, rank_worker_lag
from stream_forge_r5.throughput_audit import PartitionSample


def test_finds_partition_lagging_behind_average() -> None:
    samples = (PartitionSample(0, 100.0), PartitionSample(1, 100.0), PartitionSample(2, 50.0))

    bottlenecks = find_bottleneck_partitions(samples, deviation_threshold=0.2)

    assert len(bottlenecks) == 1
    assert bottlenecks[0].partition == 2


def test_no_bottleneck_when_partitions_are_balanced() -> None:
    samples = (PartitionSample(0, 100.0), PartitionSample(1, 98.0), PartitionSample(2, 102.0))

    assert find_bottleneck_partitions(samples, deviation_threshold=0.2) == ()


def test_empty_samples_returns_empty_tuple() -> None:
    assert find_bottleneck_partitions((), deviation_threshold=0.2) == ()


def test_rank_worker_lag_orders_worst_first() -> None:
    ranked = rank_worker_lag({"worker-1": 10, "worker-2": 500, "worker-3": 50})

    assert ranked == [("worker-2", 500), ("worker-3", 50), ("worker-1", 10)]
