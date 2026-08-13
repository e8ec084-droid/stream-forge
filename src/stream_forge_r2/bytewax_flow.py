import contextlib

import bytewax.operators as op
from bytewax.connectors.kafka import (
    KafkaError,
    KafkaSink,
    KafkaSinkMessage,
    KafkaSource,
    KafkaSourceMessage,
)
from bytewax.dataflow import Dataflow

from stream_forge_r2.config import get_settings
from stream_forge_r2.schemas import TelemetryEventV1, ValidatedTelemetryEventV1
from stream_forge_r2.serializers import (
    SchemaValidationError,
    SerializationError,
    deserialize_telemetry,
    serialize_validated_event,
)
from stream_forge_r2.state_store import StateStore
from stream_forge_r2.topology import (
    TemperatureBounds,
    is_business_valid_temperature,
    transform_to_validated_event,
)

settings = get_settings()

flow = Dataflow("stream-forge-r2-topology")

kafka_input = KafkaSource(
    brokers=[settings.bootstrap_servers],
    topics=[settings.input_topic],
)

stream = op.input("kafka-consume", flow, kafka_input)

bounds = TemperatureBounds(settings.stream_filter_min_temp_c, settings.stream_filter_max_temp_c)

state_store = StateStore()


def deserialize_step(
    msg: KafkaSourceMessage[bytes | None, bytes | None] | KafkaError[bytes | None, bytes | None],
) -> TelemetryEventV1 | None:
    """Decode a raw Kafka message into a TelemetryEventV1.

    Returns None for Kafka-level errors, empty payloads, malformed JSON, or
    schema-invalid payloads, so downstream steps can simply filter out None.
    """
    if isinstance(msg, KafkaError):
        return None
    if msg.value is None:
        return None
    try:
        return deserialize_telemetry(msg.value)
    except (SerializationError, SchemaValidationError):
        return None


def filter_step(event: TelemetryEventV1 | None) -> bool:
    """Keep only events that deserialized successfully and pass business validation."""
    if event is None:
        return False
    return is_business_valid_temperature(event, bounds)


def map_step(event: TelemetryEventV1 | None) -> ValidatedTelemetryEventV1:
    """Transform a valid raw event into its validated, topology-tagged form."""
    assert event is not None
    return transform_to_validated_event(event)


def dedup_step(event: ValidatedTelemetryEventV1) -> bool:
    """Exactly-once guard: drop events already processed for this truck.

    Uses the state store's last-seen timestamp per truck to detect Kafka
    redeliveries (at-least-once) and prevent double-processing the same event.
    """
    last_seen = state_store.get(event.truck_id)
    if last_seen is not None and event.timestamp_ms <= last_seen.get("timestamp_ms", -1):
        return False
    return True


def save_state_step(event: ValidatedTelemetryEventV1) -> ValidatedTelemetryEventV1:
    """Persist the latest event per truck_id for recovery.

    A failed disk write is swallowed (OSError) so a state-store issue never
    blocks the event from reaching the validated Kafka topic.
    """
    with contextlib.suppress(OSError):
        state_store.put(event.truck_id, event.model_dump())
    return event


deserialized_stream = op.map("deserialize", stream, deserialize_step)
filtered_stream = op.filter("filter-valid-temp", deserialized_stream, filter_step)
mapped_stream = op.map("transform-to-validated", filtered_stream, map_step)
mapped_stream = op.filter("dedup-exactly-once", mapped_stream, dedup_step)
mapped_stream = op.map("save-state", mapped_stream, save_state_step)


def to_kafka_message(event: ValidatedTelemetryEventV1) -> KafkaSinkMessage[bytes, bytes]:
    """Serialize a validated event into a keyed Kafka Sink message."""
    return KafkaSinkMessage(
        key=event.truck_id.encode("utf-8"),
        value=serialize_validated_event(event),
    )


kafka_output = KafkaSink(
    brokers=[settings.bootstrap_servers],
    topic=settings.output_topic,
)

output_stream = op.map("prepare-kafka-message", mapped_stream, to_kafka_message)
op.output("kafka-produce", output_stream, kafka_output)