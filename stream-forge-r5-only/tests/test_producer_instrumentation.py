from stream_forge_r5.metrics import EVENTS_PRODUCED_TOTAL
from stream_forge_r5.producer_instrumentation import InstrumentedProducer


class FakeProducer:
    """Doubles confluent_kafka.Producer using SupportsProduce's shape only."""

    def produce(self, topic: str, callback, **kwargs) -> None:
        callback(None, MockMessage(topic))


class MockMessage:
    def __init__(self, topic: str) -> None:
        self._topic = topic

    def topic(self) -> str:
        return self._topic


def test_successful_produce_increments_counter() -> None:
    before = EVENTS_PRODUCED_TOTAL.labels(topic="test.topic")._value.get()
    InstrumentedProducer(FakeProducer()).produce(topic="test.topic", value=b"payload")
    after = EVENTS_PRODUCED_TOTAL.labels(topic="test.topic")._value.get()

    assert after == before + 1


def test_on_delivery_callback_is_forwarded() -> None:
    received = []
    producer = InstrumentedProducer(
        FakeProducer(), on_delivery=lambda error, msg: received.append(msg.topic())
    )
    producer.produce(topic="test.topic", value=b"payload")

    assert received == ["test.topic"]
