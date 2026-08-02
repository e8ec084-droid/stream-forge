import argparse
import time
from random import Random

from confluent_kafka import Producer

from stream_forge_r2.config import get_settings
from stream_forge_r2.schemas import TelemetryEventV1
from stream_forge_r2.serializers import serialize_model


def build_event(index: int, rng: Random) -> TelemetryEventV1:
    return TelemetryEventV1(
        truck_id=f"truck-{index % 10:04d}",
        temperature_c=round(rng.uniform(2, 95), 2),
        timestamp_ms=int(time.time() * 1000),
        source="r2-sample-producer",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()

    settings = get_settings()
    producer = Producer(settings.producer_config())
    rng = Random(42)

    for index in range(args.count):
        event = build_event(index, rng)
        producer.produce(
            settings.input_topic,
            key=event.truck_id.encode("utf-8"),
            value=serialize_model(event),
        )
    producer.flush(10)
    print(f"Produced {args.count} sample events to {settings.input_topic}")


if __name__ == "__main__":
    main()
