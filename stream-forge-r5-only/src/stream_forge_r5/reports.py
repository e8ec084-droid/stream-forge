"""Builds the Markdown reports R5 owns.

Four different Fridays (Week 2 prep, Mid-Review, Week 3, Week 4) each end in
"write a report." Rather than four near-duplicate templating functions, this
module has one generic ``render_report`` and three thin builders that just
supply the sections — the only thing that actually differs between reports.
"""

from stream_forge_r5.chaos import ChaosResult
from stream_forge_r5.throughput_audit import AuditResult


def render_report(title: str, sections: dict[str, str]) -> str:
    """Turns a title + ordered section map into Markdown. Every report builder below calls this."""
    body = "\n\n".join(f"## {heading}\n\n{content}" for heading, content in sections.items())
    return f"# {title}\n\n{body}\n"


def build_mid_project_audit_report(audit: AuditResult, bottleneck_partitions: list[int]) -> str:
    """Mid-Project Review, Friday: throughput result + per-partition breakdown + bottlenecks."""
    status = "PASSED" if audit.passed else "FAILED"
    partition_lines = "\n".join(
        f"- Partition {sample.partition}: {sample.events_per_second:,.0f} events/sec"
        for sample in audit.partitions
    )
    return render_report(
        "Mid-Project Throughput & Windowing Audit Report",
        {
            "Result": f"{status} — {audit.total_events_per_second:,.0f} events/sec against a "
            f"{audit.target_events_per_second:,} target.",
            "Per-partition throughput": partition_lines,
            "Bottleneck partitions": ", ".join(map(str, bottleneck_partitions)) or "none detected",
        },
    )


def build_chaos_test_report(result: ChaosResult) -> str:
    """Week 3, Friday: document what the chaos test proved."""
    return render_report(
        "Chaos Testing Results",
        {
            "Scenario": f"Killed `{result.target_worker}` while it owned partition "
            f"{result.partition}.",
            "Rebalance": f"{'Succeeded' if result.rebalanced else 'Failed'} — moved to "
            f"`{result.failover_worker}` in {result.rebalance_seconds:.1f}s.",
            "State recovery": "Rolling average preserved within tolerance."
            if result.state_recovered
            else "Rolling average diverged after recovery — investigate.",
        },
    )


def build_final_observability_report(audit: AuditResult, chaos: ChaosResult) -> str:
    """Week 4, Friday: the closing summary tying throughput, resilience, and alerting together."""
    resilience_passed = chaos.rebalanced and chaos.state_recovered
    return render_report(
        "Final Observability Report",
        {
            "Throughput": f"Sustained {audit.total_events_per_second:,.0f} events/sec "
            f"({'meets' if audit.passed else 'is below'} the "
            f"{audit.target_events_per_second:,} target).",
            "Resilience": f"Chaos test {'passed' if resilience_passed else 'needs follow-up'} — "
            f"rebalanced in {chaos.rebalance_seconds:.1f}s, "
            f"state recovered={chaos.state_recovered}.",
            "Alerting": "Lag, broker-availability, and throughput alerts "
            "are live in `monitoring/alerts.yml`.",
        },
    )
