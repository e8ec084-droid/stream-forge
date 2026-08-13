from unittest.mock import MagicMock, patch

from stream_forge_r5.broker_health import check_broker_health


def test_healthy_cluster_reports_broker_count() -> None:
    fake_metadata = MagicMock(brokers={0: "broker-0", 1: "broker-1"})
    with patch("stream_forge_r5.broker_health.AdminClient") as admin_client_cls:
        admin_client_cls.return_value.list_topics.return_value = fake_metadata
        result = check_broker_health("localhost:9092")

    assert result.is_healthy is True
    assert result.broker_count == 2
    assert result.error is None


def test_unreachable_broker_reports_unhealthy() -> None:
    with patch("stream_forge_r5.broker_health.AdminClient") as admin_client_cls:
        admin_client_cls.return_value.list_topics.side_effect = Exception("timed out")
        result = check_broker_health("localhost:9092")

    assert result.is_healthy is False
    assert result.broker_count == 0
    assert result.error == "timed out"
