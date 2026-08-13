"""Generates Prometheus alerting rules from settings (Week 4, Thursday).

Rules are built as plain ``dict``/``list`` structures that mirror
Prometheus's own YAML shape 1:1, so ``write_alert_rules`` is a one-line
``yaml.safe_dump`` with no custom serialization logic to maintain.
"""

from pathlib import Path
from typing import Any

import yaml

from stream_forge_r5.config import ObservabilitySettings

# Alert-rule documents are inherently heterogeneous (strings, nested dicts,
# lists) — mirroring Prometheus's own YAML shape — so `Any` is the honest
# value type here rather than a contrived TypedDict that would just repeat
# Prometheus's schema.
AlertRule = dict[str, Any]
AlertRuleDocument = dict[str, Any]


def build_alert_rules(settings: ObservabilitySettings) -> AlertRuleDocument:
    """Builds the alert-rule document that thresholds every metric in ``metrics.py``."""
    rules = [
        _threshold_rule(
            "StreamForgeConsumerLagWarning",
            "warning",
            f"stream_forge_consumer_lag > {settings.consumer_lag_warning_threshold}",
            "Consumer lag exceeded the warning threshold",
        ),
        _threshold_rule(
            "StreamForgeConsumerLagCritical",
            "critical",
            f"stream_forge_consumer_lag > {settings.consumer_lag_critical_threshold}",
            "Consumer lag exceeded the critical threshold",
        ),
        _threshold_rule(
            "StreamForgeBrokerDown",
            "critical",
            "stream_forge_broker_up == 0",
            "Kafka broker is not responding to metadata requests",
        ),
        _threshold_rule(
            "StreamForgeThroughputBelowTarget",
            "warning",
            f"sum(rate(stream_forge_events_consumed_total[5m])) "
            f"< {settings.throughput_target_events_per_second * settings.throughput_alert_ratio}",
            f"Throughput dropped below {int(settings.throughput_alert_ratio * 100)}% of target",
        ),
    ]
    return {"groups": [{"name": "stream-forge-r5", "rules": rules}]}


def _threshold_rule(alert_name: str, severity: str, expression: str, summary: str) -> AlertRule:
    return {
        "alert": alert_name,
        "expr": expression,
        "for": "2m",
        "labels": {"severity": severity},
        "annotations": {"summary": summary},
    }


def write_alert_rules(settings: ObservabilitySettings, path: Path) -> None:
    path.write_text(yaml.safe_dump(build_alert_rules(settings), sort_keys=False))
