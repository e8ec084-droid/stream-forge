"""Instruments a Kafka producer with counters and latency (Week 1, Wednesday).

``InstrumentedProducer`` wraps a real ``confluent_kafka.Producer`` instead of
subclassing it. Composition beats inheritance here because ``Producer`` is a
C-extension class with a fixed API — subclassing it buys nothing, while
wrapping it lets tests pass in a plain fake object with a ``produce`` method.
"""

from collections.abc import Callable
from time import perf_counter
from typing import Any, Protocol

from confluent_kafka import KafkaError, Message

from stream_forge_r5.metrics import EVENTS_PRODUCED_TOTAL, PRODUCE_LATENCY_SECONDS

DeliveryCallback = Callable[[KafkaError | None, Message], None]


class SupportsProduce(Protocol):
    """The one method we depend on — lets tests double a Producer without confluent-kafka."""

    def produce(self, topic: str, callback: DeliveryCallback, **kwargs: Any) -> None: ...


class InstrumentedProducer:
    """Times every ``produce()`` call and counts successful deliveries."""

    def __init__(
        self, producer: SupportsProduce, on_delivery: DeliveryCallback | None = None
    ) -> None:
        self._producer = producer
        self._on_delivery = on_delivery

    def produce(self, topic: str, **kwargs: Any) -> None:
        started_at = perf_counter()
        self._producer.produce(
            topic=topic, callback=self._make_delivery_callback(topic, started_at), **kwargs
        )

    def _make_delivery_callback(self, topic: str, started_at: float) -> DeliveryCallback:
        def _on_delivery(error: KafkaError | None, message: Message) -> None:
            PRODUCE_LATENCY_SECONDS.labels(topic=topic).observe(perf_counter() - started_at)
            if error is None:
                EVENTS_PRODUCED_TOTAL.labels(topic=topic).inc()
            if self._on_delivery is not None:
                self._on_delivery(error, message)

        return _on_delivery
