from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    """Runtime settings for the R2 streaming worker."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bootstrap_servers: str  = Field(default="localhost:9092",            alias="KAFKA_BOOTSTRAP_SERVERS")
    input_topic:       str  = Field(default="truck.telemetry.raw",       alias="KAFKA_INPUT_TOPIC")
    output_topic:      str  = Field(default="truck.telemetry.validated",  alias="KAFKA_OUTPUT_TOPIC")
    consumer_group:    str  = Field(default="stream-forge-r2-week2",     alias="KAFKA_CONSUMER_GROUP")
    auto_offset_reset: str  = Field(default="earliest",                  alias="KAFKA_AUTO_OFFSET_RESET")

    # Filter bounds — configurable so QA/R3 can adjust without code changes
    stream_filter_min_temp_c: float = Field(default=-50.0,  alias="STREAM_FILTER_MIN_TEMP_C")
    stream_filter_max_temp_c: float = Field(default=120.0,  alias="STREAM_FILTER_MAX_TEMP_C")

    def consumer_config(self) -> dict[str, str]:
        return {
            "bootstrap.servers":  self.bootstrap_servers,
            "group.id":           self.consumer_group,
            "auto.offset.reset":  self.auto_offset_reset,
            "enable.auto.commit": "false",
        }

    def producer_config(self) -> dict[str, str]:
        return {
            "bootstrap.servers":    self.bootstrap_servers,
            "enable.idempotence":   "true",
            "acks":                 "all",
            "linger.ms":            "20",
            "batch.num.messages":   "1000",
        }


@lru_cache(maxsize=1)
def get_settings() -> KafkaSettings:
    return KafkaSettings()
