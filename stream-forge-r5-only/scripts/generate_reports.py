"""Regenerates every Friday report from live/sample data.

One script instead of three: Week 2 Friday ("prepare the reporting"), Mid-
Review Friday, Week 3 Friday, and Week 4 Friday all just call the relevant
builder in `reports.py` and write the file. Swap the sample data below for
real `AuditResult`/`ChaosResult` objects once R1-R4's services are reachable.
"""

from pathlib import Path

from stream_forge_r5.bottleneck_analysis import find_bottleneck_partitions
from stream_forge_r5.chaos import ChaosResult
from stream_forge_r5.reports import (
    build_chaos_test_report,
    build_final_observability_report,
    build_mid_project_audit_report,
)
from stream_forge_r5.throughput_audit import AuditResult, PartitionSample

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

SAMPLE_AUDIT = AuditResult(
    target_events_per_second=100_000,
    partitions=(
        PartitionSample(0, 25_120),
        PartitionSample(1, 24_880),
        PartitionSample(2, 25_410),
        PartitionSample(3, 25_432),
    ),
)

SAMPLE_CHAOS_RESULT = ChaosResult(
    target_worker="worker-4",
    failover_worker="worker-5",
    partition=3,
    rebalanced=True,
    state_recovered=True,
    rebalance_seconds=4.2,
)


def main() -> None:
    bottlenecks = [b.partition for b in find_bottleneck_partitions(SAMPLE_AUDIT.partitions)]

    _write("mid_project_audit_report.md", build_mid_project_audit_report(SAMPLE_AUDIT, bottlenecks))
    _write("chaos_testing_results.md", build_chaos_test_report(SAMPLE_CHAOS_RESULT))
    _write(
        "final_observability_report.md",
        build_final_observability_report(SAMPLE_AUDIT, SAMPLE_CHAOS_RESULT),
    )


def _write(filename: str, content: str) -> None:
    path = DOCS_DIR / filename
    path.write_text(content)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
