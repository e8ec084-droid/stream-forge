import json

from stream_forge_r2 import bytewax_flow
from stream_forge_r2.state_store import StateStore


class FakeKafkaMessage:
    """Stand-in for a real Kafka message — deserialize_step only needs .value."""

    def __init__(self, value: bytes):
        self.value = value


def _raw_event_bytes(truck_id="truck-0001", temp_c=21.5, timestamp_ms=1722297600000):
    return json.dumps(
        {
            "schema_version": "1.0",
            "truck_id": truck_id,
            "temperature_c": temp_c,
            "timestamp_ms": timestamp_ms,
            "source": "mock-generator",
        }
    ).encode("utf-8")


def test_end_to_end_happy_path(tmp_path, monkeypatch):
    monkeypatch.setattr(
        bytewax_flow, "state_store", StateStore(snapshot_path=str(tmp_path / "state.json"))
    )

    msg = FakeKafkaMessage(_raw_event_bytes())

    parsed = bytewax_flow.deserialize_step(msg)
    assert parsed is not None
    assert bytewax_flow.filter_step(parsed) is True

    validated = bytewax_flow.map_step(parsed)
    assert bytewax_flow.dedup_step(validated) is True

    saved = bytewax_flow.save_state_step(validated)
    kafka_msg = bytewax_flow.to_kafka_message(saved)

    assert kafka_msg.key == b"truck-0001"
    payload = json.loads(kafka_msg.value)
    assert payload["temperature_f"] == 70.7
    assert payload["topology_stage"] == "validated"


def test_duplicate_event_is_dropped(tmp_path, monkeypatch):
    monkeypatch.setattr(
        bytewax_flow, "state_store", StateStore(snapshot_path=str(tmp_path / "state.json"))
    )

    first_msg = FakeKafkaMessage(_raw_event_bytes(timestamp_ms=1722297600000))
    parsed = bytewax_flow.deserialize_step(first_msg)
    validated = bytewax_flow.map_step(parsed)
    bytewax_flow.save_state_step(validated)

    duplicate_msg = FakeKafkaMessage(_raw_event_bytes(timestamp_ms=1722297600000))
    parsed_dup = bytewax_flow.deserialize_step(duplicate_msg)
    validated_dup = bytewax_flow.map_step(parsed_dup)

    assert bytewax_flow.dedup_step(validated_dup) is False
    
def test_out_of_order_older_event_is_dropped(tmp_path, monkeypatch):
    monkeypatch.setattr(
        bytewax_flow, "state_store", StateStore(snapshot_path=str(tmp_path / "state.json"))
    )

    newer_msg = FakeKafkaMessage(_raw_event_bytes(timestamp_ms=1722297700000))
    parsed_newer = bytewax_flow.deserialize_step(newer_msg)
    validated_newer = bytewax_flow.map_step(parsed_newer)
    bytewax_flow.save_state_step(validated_newer)

    older_msg = FakeKafkaMessage(_raw_event_bytes(timestamp_ms=1722297600000))
    parsed_older = bytewax_flow.deserialize_step(older_msg)
    validated_older = bytewax_flow.map_step(parsed_older)

    assert bytewax_flow.dedup_step(validated_older) is False