from stream_forge_r5.alerting import build_alert_rules
from stream_forge_r5.config import ObservabilitySettings


def test_build_alert_rules_includes_all_four_alerts() -> None:
    settings = ObservabilitySettings(_env_file=None)
    rules = build_alert_rules(settings)

    alert_names = {rule["alert"] for rule in rules["groups"][0]["rules"]}
    assert alert_names == {
        "StreamForgeConsumerLagWarning",
        "StreamForgeConsumerLagCritical",
        "StreamForgeBrokerDown",
        "StreamForgeThroughputBelowTarget",
    }


def test_lag_thresholds_come_from_settings() -> None:
    settings = ObservabilitySettings(_env_file=None, consumer_lag_warning_threshold=250)
    rules = build_alert_rules(settings)

    warning_rule = next(
        rule
        for rule in rules["groups"][0]["rules"]
        if rule["alert"] == "StreamForgeConsumerLagWarning"
    )
    assert "250" in warning_rule["expr"]
