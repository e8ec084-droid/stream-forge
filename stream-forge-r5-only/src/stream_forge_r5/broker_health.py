"""Broker health-check tooling (Week 1, Thursday).

Reuses ``confluent_kafka.admin.AdminClient`` — the same Kafka client library
R1/R2 already depend on — instead of adding a second Kafka client just for
health checks.
"""

from dataclasses import dataclass

from confluent_kafka.admin import AdminClient

from stream_forge_r5.metrics import BROKER_UP


@dataclass(frozen=True)
class BrokerHealth:
    """Result of a single metadata-request health probe."""

    bootstrap_servers: str
    is_healthy: bool
    broker_count: int
    error: str | None = None


def check_broker_health(bootstrap_servers: str, timeout_seconds: float = 5.0) -> BrokerHealth:
    """Pings cluster metadata; healthy means at least one broker answered in time."""
    admin_client = AdminClient({"bootstrap.servers": bootstrap_servers})
    try:
        cluster_metadata = admin_client.list_topics(timeout=timeout_seconds)
    except Exception as exc:  # confluent_kafka raises a plain/KafkaException subclass here
        BROKER_UP.labels(bootstrap_server=bootstrap_servers).set(0)
        return BrokerHealth(bootstrap_servers, is_healthy=False, broker_count=0, error=str(exc))

    broker_count = len(cluster_metadata.brokers)
    BROKER_UP.labels(bootstrap_server=bootstrap_servers).set(int(broker_count > 0))
    return BrokerHealth(bootstrap_servers, is_healthy=broker_count > 0, broker_count=broker_count)


if __name__ == "__main__":
    from stream_forge_r5.config import get_observability_settings

    settings = get_observability_settings()
    print(check_broker_health(settings.kafka_bootstrap_servers))
