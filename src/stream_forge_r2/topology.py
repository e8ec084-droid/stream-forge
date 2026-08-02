from dataclasses import dataclass

from stream_forge_r2.schemas import TelemetryEventV1, ValidatedTelemetryEventV1


@dataclass(frozen=True)
class TemperatureBounds:
    min_c: float = -50.0
    max_c: float = 120.0


def is_business_valid_temperature(event: TelemetryEventV1, bounds: TemperatureBounds) -> bool:
    """Keep physically plausible truck telemetry for downstream aggregation."""
    return bounds.min_c <= event.temperature_c <= bounds.max_c


def transform_to_validated_event(event: TelemetryEventV1) -> ValidatedTelemetryEventV1:
    return ValidatedTelemetryEventV1.from_raw(event)


def process_event(
    event: TelemetryEventV1,
    bounds: TemperatureBounds | None = None,
) -> ValidatedTelemetryEventV1 | None:
    active_bounds = bounds or TemperatureBounds()
    if not is_business_valid_temperature(event, active_bounds):
        return None
    return transform_to_validated_event(event)
