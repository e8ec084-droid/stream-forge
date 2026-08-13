import time

from stream_forge_r2.schemas import TelemetryEventV1
from stream_forge_r2.topology import TemperatureBounds, process_event


def event(temp: float) -> TelemetryEventV1:
    return TelemetryEventV1(
        truck_id="truck-0001",
        temperature_c=temp,
        timestamp_ms=int(time.time() * 1000),
        source="unit-test",
    )


def test_process_event_maps_celsius_to_fahrenheit() -> None:
    output = process_event(event(10.0))
    assert output is not None
    assert output.temperature_f == 50.0
    assert output.topology_stage == "validated"


def test_process_event_filters_business_invalid_temperature() -> None:
    output = process_event(event(121.0), TemperatureBounds(min_c=-50, max_c=120))
    assert output is None
