import logging
import signal
from collections.abc import Callable
from dataclasses import dataclass

from confluent_kafka import Consumer, KafkaError, KafkaException, Message, Producer

from stream_forge_r2.config import KafkaSettings, get_settings
from stream_forge_r2.serializers import (
    SchemaValidationError,
    SerializationError,
    deserialize_telemetry,
    serialize_validated_event,
)
from stream_forge_r2.topology import TemperatureBounds, process_event

logger = logging.getLogger(__name__)


@dataclass
class ConsumerStats:
    consumed: int = 0
    produced: int = 0
    invalid: int = 0
    filtered: int = 0


class GracefulShutdown:
    def __init__(self) -> None:
        self.stop_requested = False
        signal.signal(signal.SIGINT, self._request_stop)
        signal.signal(signal.SIGTERM, self._request_stop)

    def _request_stop(self, _signum: int, _frame: object) -> None:
        self.stop_requested = True


def delivery_report(error: KafkaError | None, message: Message) -> None:
    if error is not None:
        logger.error("delivery_failed topic=%s error=%s", message.topic(), error)
    else:
        logger.debug("delivery_ok topic=%s "
        "partition=%s offset=%s", 
        message.topic(),
         message.partition(), 
         message.offset())


def handle_message(
    message_value: bytes,
    producer: Producer,
    output_topic: str,
    bounds: TemperatureBounds,
    stats: ConsumerStats,
) -> None:
    stats.consumed += 1
    try:
        raw_event = deserialize_telemetry(message_value)
        validated_event = process_event(raw_event, bounds)
    except (SerializationError, SchemaValidationError) as exc:
        stats.invalid += 1
        logger.warning("invalid_message error=%s", exc)
        return

    if validated_event is None:
        stats.filtered += 1
        return

    producer.produce(
        topic=output_topic,
        key=validated_event.truck_id.encode("utf-8"),
        value=serialize_validated_event(validated_event),
        callback=delivery_report,
    )
    producer.poll(0)
    stats.produced += 1


def run_consumer(
    settings: KafkaSettings | None = None,
    shutdown_factory: Callable[[], GracefulShutdown] = GracefulShutdown,
) -> ConsumerStats:
    settings = settings or get_settings()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    consumer = Consumer(settings.consumer_config())
    producer = Producer(settings.producer_config())
    shutdown = shutdown_factory()
    stats = ConsumerStats()
    bounds = TemperatureBounds(settings.stream_filter_min_temp_c, settings.stream_filter_max_temp_c)

    consumer.subscribe([settings.input_topic])
    logger.info("consumer_started input=%s output=%s", settings.input_topic, settings.output_topic)

    try:
        while not shutdown.stop_requested:
            message = consumer.poll(1.0)
            if message is None:
                continue
            error=message.error()
            if error is not None:
                if error.code() == KafkaError._PARTITION_EOF:
                    continue
                raise KafkaException(message.error())

            value=message.value()
            if value is None:
                continue
            handle_message(value, producer, settings.output_topic, bounds, stats)
            consumer.commit(message=message, asynchronous=False)
    finally:
        producer.flush(10)
        consumer.close()
        logger.info("consumer_stopped stats=%s", stats)

    return stats


if __name__ == "__main__":
    run_consumer()
