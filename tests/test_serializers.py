import json
import time

import pytest

from stream_forge_r2.schemas import TelemetryEventV1
from stream_forge_r2.serializers import (
    SchemaValidationError,
    SerializationError,
    deserialize_telemetry,
    serialize_model,
)


def valid_payload() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "truck_id": "truck-0001",
        "temperature_c": 21.5,
        "timestamp_ms": int(time.time() * 1000),
        "source": "mock-generator",
    }


def test_deserialize_valid_payload() -> None:
    event = deserialize_telemetry(json.dumps(valid_payload()).encode())
    assert event.truck_id == "truck-0001"
    assert event.temperature_c == 21.5


def test_rejects_invalid_json() -> None:
    with pytest.raises(SerializationError):
        deserialize_telemetry(b"not-json")


def test_rejects_bad_schema() -> None:
    payload = valid_payload()
    payload["truck_id"] = "bad truck id with spaces"
    with pytest.raises(SchemaValidationError):
        deserialize_telemetry(json.dumps(payload))


def test_serialize_model_returns_bytes() -> None:
    event = TelemetryEventV1.model_validate(valid_payload())
    result = serialize_model(event)
    assert isinstance(result, bytes)
    assert b"truck-0001" in result
