"""Runtime configuration for the R5 observability toolkit.

Mirrors ``stream_forge_r2.config``: one pydantic-settings class, one
``lru_cache``-wrapped getter. Reusing that pattern (rather than inventing a
new one) means anyone who has already read R2's config can read this file
for free.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ObservabilitySettings(BaseSettings):
    """Environment-driven thresholds and targets shared by every R5 module."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    kafka_bootstrap_servers: str = Field(default="localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")
    metrics_port: int = Field(default=9200, alias="METRICS_PORT")

    throughput_target_events_per_second: int = Field(default=100_000, alias="THROUGHPUT_TARGET_EPS")
    throughput_alert_ratio: float = Field(default=0.8, alias="THROUGHPUT_ALERT_RATIO")

    consumer_lag_warning_threshold: int = Field(
        default=1_000, alias="CONSUMER_LAG_WARNING_THRESHOLD"
    )
    consumer_lag_critical_threshold: int = Field(
        default=5_000, alias="CONSUMER_LAG_CRITICAL_THRESHOLD"
    )

    bottleneck_deviation_threshold: float = Field(
        default=0.2, alias="BOTTLENECK_DEVIATION_THRESHOLD"
    )

    chaos_target_worker_id: str = Field(default="worker-4", alias="CHAOS_TARGET_WORKER_ID")
    chaos_failover_worker_id: str = Field(default="worker-5", alias="CHAOS_FAILOVER_WORKER_ID")
    chaos_rebalance_timeout_seconds: float = Field(
        default=30.0, alias="CHAOS_REBALANCE_TIMEOUT_SECONDS"
    )


@lru_cache(maxsize=1)
def get_observability_settings() -> ObservabilitySettings:
    """Cached accessor so every module shares one settings instance, like R2 does."""
    return ObservabilitySettings()
