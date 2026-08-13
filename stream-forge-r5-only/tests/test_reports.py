from stream_forge_r5.chaos import ChaosResult
from stream_forge_r5.reports import (
    build_chaos_test_report,
    build_final_observability_report,
    build_mid_project_audit_report,
)
from stream_forge_r5.throughput_audit import AuditResult, PartitionSample


def sample_audit() -> AuditResult:
    return AuditResult(
        target_events_per_second=100_000,
        partitions=(PartitionSample(0, 60_000), PartitionSample(1, 45_000)),
    )


def sample_chaos_result() -> ChaosResult:
    return ChaosResult(
        target_worker="worker-4",
        failover_worker="worker-5",
        partition=3,
        rebalanced=True,
        state_recovered=True,
        rebalance_seconds=4.2,
    )


def test_mid_project_audit_report_mentions_pass_status() -> None:
    report = build_mid_project_audit_report(sample_audit(), bottleneck_partitions=[1])

    assert "PASSED" in report
    assert "Partition 1" in report


def test_chaos_test_report_mentions_rebalance_outcome() -> None:
    report = build_chaos_test_report(sample_chaos_result())

    assert "worker-4" in report
    assert "Succeeded" in report


def test_final_observability_report_combines_both() -> None:
    report = build_final_observability_report(sample_audit(), sample_chaos_result())

    assert "Throughput" in report
    assert "Resilience" in report
    assert "monitoring/alerts.yml" in report
