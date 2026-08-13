from datetime import  UTC,datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TelemetryEventV1(BaseModel):
    """Raw IoT telemetry event consumed from Kafka."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    truck_id: str = Field(min_length=3, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    temperature_c: float = Field(ge=-100.0, le=200.0)
    timestamp_ms: int = Field(gt=0)
    source: str = Field(default="mock-generator", min_length=1, max_length=64)

    @field_validator("timestamp_ms")
    @classmethod
    def timestamp_must_be_reasonable(cls, value: int) -> int:
        # Reject values before 2020 to catch seconds accidentally sent as milliseconds.
        min_ms = int(datetime(2020, 1, 1, tzinfo=UTC).timestamp() * 1000)
        if value < min_ms:
            raise ValueError("timestamp_ms must be epoch milliseconds, not seconds")
        return value


class ValidatedTelemetryEventV1(BaseModel):
    """Cleaned event produced by the R2 topology for downstream roles."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    truck_id: str
    temperature_c: float
    temperature_f: float
    timestamp_ms: int
    source: str
    topology_stage: Literal["validated"] = "validated"

    @classmethod
    def from_raw(cls, event: TelemetryEventV1) -> "ValidatedTelemetryEventV1":
        return cls(
            truck_id=event.truck_id,
            temperature_c=round(event.temperature_c, 2),
            temperature_f=round((event.temperature_c * 9 / 5) + 32, 2),
            timestamp_ms=event.timestamp_ms,
            source=event.source,
        )