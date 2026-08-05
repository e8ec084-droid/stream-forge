"""Bytewax dataflow — Week 2 R2: Consume → Filter(Temp > 0) → Map → Produce.

Week 1 scaffolded the Dataflow object and kept KafkaSource/KafkaSink wiring
intentionally deferred until R1 finalised partition count and producer contract.
Week 2 completes the full pipeline:

    KafkaSource  ──▶  deserialise  ──▶  filter(temp > 0 & bounds)
                                               │
                                               ▼
                                         map / transform
                                               │
                                               ▼
                                         KafkaSink (validated topic)

Design decisions
----------------
* Bytewax ``op.filter_map`` is used for the combined filter + map step so that
  None-returning calls (i.e. rejected events) are automatically dropped without
  a separate ``op.filter`` pass — one fewer operator in the DAG.
* Deserialisation errors are caught inside the mapper and logged; the message is
  dropped (returns None) so the flow never crashes on bad payloads.
* Temperature bounds default to the business rule (> 0 °C) but are overridable
  via environment variables so QA can tighten or loosen the gate without code
  changes.
* The KafkaSink key is set to ``truck_id`` bytes to preserve per-truck ordering
  across partitions — consistent with the R1 producer contract.
"""

from __future__ import annotations

import json
import logging

from bytewax.connectors.kafka import KafkaSinkMessage, KafkaSources, KafkaSink
from bytewax.dataflow import Dataflow
import bytewax.operators as op

from stream_forge_r2.config import get_settings
from stream_forge_r2.schemas import TelemetryEventV1
from stream_forge_r2.serializers import (
    SchemaValidationError,
    SerializationError,
    deserialize_telemetry,
    serialize_validated_event,
)
from stream_forge_r2.topology import TemperatureBounds, process_event

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_and_process(
    kafka_msg: tuple[bytes | None, bytes | None],
    bounds: TemperatureBounds,
) -> KafkaSinkMessage | None:
    """Deserialise, filter, and map a raw Kafka message.

    Returns a KafkaSinkMessage ready for the sink, or None to drop the message.
    Returning None from a ``filter_map`` operator silently discards the record.
    """
    _key, value = kafka_msg
    if value is None:
        return None

    # --- deserialise ---
    try:
        raw_event: TelemetryEventV1 = deserialize_telemetry(value)
    except (SerializationError, SchemaValidationError) as exc:
        logger.warning("drop_invalid_payload error=%s", exc)
        return None

    # --- filter + map (process_event returns None when temp out of bounds) ---
    validated = process_event(raw_event, bounds)
    if validated is None:
        logger.debug(
            "drop_filtered truck_id=%s temperature_c=%s",
            raw_event.truck_id,
            raw_event.temperature_c,
        )
        return None

    # --- serialise output ---
    return KafkaSinkMessage(
        key=validated.truck_id.encode("utf-8"),
        value=serialize_validated_event(validated),
    )


# ---------------------------------------------------------------------------
# Dataflow factory
# ---------------------------------------------------------------------------

def build_flow(
    bootstrap_servers: str | None = None,
    input_topic: str | None = None,
    output_topic: str | None = None,
    consumer_group: str | None = None,
    bounds: TemperatureBounds | None = None,
) -> Dataflow:
    """Construct and return the Bytewax Dataflow.

    All parameters fall back to ``KafkaSettings`` (env / .env file) when not
    supplied explicitly, making the factory easy to call from tests with custom
    values without touching the environment.
    """
    settings = get_settings()

    _bootstrap = bootstrap_servers or settings.bootstrap_servers
    _input     = input_topic      or settings.input_topic
    _output    = output_topic     or settings.output_topic
    _group     = consumer_group   or settings.consumer_group
    _bounds    = bounds or TemperatureBounds(
        min_c=settings.stream_filter_min_temp_c,
        max_c=settings.stream_filter_max_temp_c,
    )

    flow = Dataflow("stream-forge-r2-topology")

    # ── Step 1: Consume from Kafka ──────────────────────────────────────────
    kafka_input = KafkaSources(
        brokers=[_bootstrap],
        topics=[_input],
        add_config={
            "group.id": _group,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": "false",
        },
        # Yield (key_bytes, value_bytes) tuples downstream
        starting_offset="beginning",
    )
    raw_stream = op.input("kafka_source", flow, kafka_input)

    # ── Step 2: Filter(Temp > 0 & within bounds) + Map to validated event ──
    # filter_map: callable returns None → record dropped; returns value → kept.
    validated_stream = op.filter_map(
        "filter_and_map",
        raw_stream,
        lambda msg: _parse_and_process(msg, _bounds),
    )

    # ── Step 3: Wire output to downstream validated topic ───────────────────
    kafka_output = KafkaSink(
        brokers=[_bootstrap],
        topic=_output,
        add_config={
            "enable.idempotence": "true",
            "acks": "all",
            "linger.ms": "20",
            "batch.num.messages": "1000",
        },
    )
    op.output("kafka_sink", validated_stream, kafka_output)

    return flow


# ---------------------------------------------------------------------------
# Entrypoint — ``python -m bytewax.run stream_forge_r2.bytewax_flow:flow``
# ---------------------------------------------------------------------------
flow = build_flow()
