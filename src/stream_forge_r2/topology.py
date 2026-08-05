"""Stream topology — pure business logic (framework-agnostic).

Week 2 additions
----------------
* ``filter_temp_positive`` — enforces the Week 2 explicit requirement that
  temperature must be strictly > 0 °C (in addition to the physical-bounds gate
  already present from Week 1).  Both checks are composed in ``process_event``
  so callers get a single entry point.
* ``FilterReason`` — typed enum returned by the detailed diagnostic helper
  ``classify_event`` so edge-case tests can assert *why* an event was dropped
  without string-matching log lines.
* ``process_event`` is unchanged in signature for full backward compatibility
  with the Week 1 consumer loop and existing tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from stream_forge_r2.schemas import TelemetryEventV1, ValidatedTelemetryEventV1


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TemperatureBounds:
    """Physical plausibility window for truck sensor readings."""
    min_c: float = -50.0
    max_c: float = 120.0


# ---------------------------------------------------------------------------
# Filter predicates
# ---------------------------------------------------------------------------

def is_business_valid_temperature(
    event: TelemetryEventV1,
    bounds: TemperatureBounds,
) -> bool:
    """Keep physically plausible truck telemetry for downstream aggregation.

    Week 1 gate: temperature within [min_c, max_c].
    """
    return bounds.min_c <= event.temperature_c <= bounds.max_c


def filter_temp_positive(event: TelemetryEventV1) -> bool:
    """Week 2 explicit filter gate: temperature must be strictly > 0 °C.

    Zero and sub-zero readings from a running truck indicate a sensor fault
    or an unstarted vehicle and must not pollute rolling-average aggregations.
    """
    return event.temperature_c > 0.0


# ---------------------------------------------------------------------------
# Map / transform stage
# ---------------------------------------------------------------------------

def transform_to_validated_event(
    event: TelemetryEventV1,
) -> ValidatedTelemetryEventV1:
    """Map raw telemetry to a validated, enriched downstream event.

    Enrichments added here (Week 2):
    * ``temperature_f`` — Fahrenheit conversion for R3 dual-unit aggregations.
    * ``topology_stage`` — literal tag consumed by R6 dashboard to colour nodes.
    """
    return ValidatedTelemetryEventV1.from_raw(event)


# ---------------------------------------------------------------------------
# Edge-case classification (diagnostic helper for tests & observability)
# ---------------------------------------------------------------------------

class FilterReason(Enum):
    PASS           = auto()   # event passes all gates
    OUT_OF_BOUNDS  = auto()   # physical bounds check failed
    NON_POSITIVE   = auto()   # temperature <= 0 (Week 2 gate)


def classify_event(
    event: TelemetryEventV1,
    bounds: TemperatureBounds | None = None,
) -> FilterReason:
    """Return the reason an event would be kept or dropped.

    Useful in unit tests to assert the *specific* filter gate that rejected
    an edge-case reading, and in observability counters to split drop reasons.
    """
    active_bounds = bounds or TemperatureBounds()
    if not is_business_valid_temperature(event, active_bounds):
        return FilterReason.OUT_OF_BOUNDS
    if not filter_temp_positive(event):
        return FilterReason.NON_POSITIVE
    return FilterReason.PASS


# ---------------------------------------------------------------------------
# Main entry point (used by consumer.py and bytewax_flow.py)
# ---------------------------------------------------------------------------

def process_event(
    event: TelemetryEventV1,
    bounds: TemperatureBounds | None = None,
) -> ValidatedTelemetryEventV1 | None:
    """Apply all filter gates then map to a validated event.

    Returns ``None`` when the event is rejected by any gate so callers can
    use a single None-check (idiomatic with Bytewax ``filter_map``).
    """
    active_bounds = bounds or TemperatureBounds()

    # Gate 1 — physical bounds (Week 1)
    if not is_business_valid_temperature(event, active_bounds):
        return None

    # Gate 2 — strictly positive temperature (Week 2)
    if not filter_temp_positive(event):
        return None

    # Map stage
    return transform_to_validated_event(event)
