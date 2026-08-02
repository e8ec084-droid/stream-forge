import json
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from stream_forge_r2.schemas import TelemetryEventV1, ValidatedTelemetryEventV1

T = TypeVar("T", bound=BaseModel)


class SerializationError(ValueError):
    """Raised when Kafka payload decoding fails."""


class SchemaValidationError(ValueError):
    """Raised when payload shape does not match the expected schema."""


def decode_json_payload(payload: bytes | str) -> dict[str, Any]:
    try:
        raw = payload.decode("utf-8") if isinstance(payload, bytes) else payload
        decoded = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SerializationError(f"Invalid JSON payload: {exc}") from exc

    if not isinstance(decoded, dict):
        raise SerializationError("Kafka message must decode into a JSON object")
    return decoded


def deserialize_telemetry(payload: bytes | str) -> TelemetryEventV1:
    try:
        return TelemetryEventV1.model_validate(decode_json_payload(payload))
    except ValidationError as exc:
        raise SchemaValidationError(str(exc)) from exc


def serialize_model(model: BaseModel) -> bytes:
    return model.model_dump_json(exclude_none=True).encode("utf-8")


def serialize_validated_event(event: ValidatedTelemetryEventV1) -> bytes:
    return serialize_model(event)
