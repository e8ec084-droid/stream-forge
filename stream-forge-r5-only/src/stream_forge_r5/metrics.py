"""Central metrics taxonomy for Stream Forge (Week 1, Tuesday deliverable).

Every metric emitted anywhere in the pipeline is declared exactly once here,
so the producer, the consumer, and the dashboard API all import the same
name instead of re-declaring counters ad hoc with slightly different labels.
One registry (instead of the global default registry) also means unit tests
can import this module repeatedly without "duplicated metric" errors.
"""

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

registry = CollectorRegistry()

EVENTS_PRODUCED_TOTAL = Counter(
    "stream_forge_events_produced_total",
    "Telemetry events successfully produced to Kafka.",
    labelnames=("topic",),
    registry=registry,
)

EVENTS_CONSUMED_TOTAL = Counter(
    "stream_forge_events_consumed_total",
    "Telemetry events consumed from Kafka by a stream worker.",
    labelnames=("topic",),
    registry=registry,
)

EVENTS_INVALID_TOTAL = Counter(
    "stream_forge_events_invalid_total",
    "Events rejected for failing schema validation or JSON decoding.",
    labelnames=("topic", "reason"),
    registry=registry,
)

EVENTS_FILTERED_TOTAL = Counter(
    "stream_forge_events_filtered_total",
    "Events dropped by business-rule filtering (e.g. temperature out of range).",
    labelnames=("topic",),
    registry=registry,
)

CONSUMER_LAG = Gauge(
    "stream_forge_consumer_lag",
    "High watermark offset minus last committed offset, per partition.",
    labelnames=("topic", "partition"),
    registry=registry,
)

BROKER_UP = Gauge(
    "stream_forge_broker_up",
    "1 when the broker answers a metadata request, 0 otherwise.",
    labelnames=("bootstrap_server",),
    registry=registry,
)

PRODUCE_LATENCY_SECONDS = Histogram(
    "stream_forge_produce_latency_seconds",
    "Time between calling produce() and the delivery callback firing.",
    labelnames=("topic",),
    registry=registry,
)
