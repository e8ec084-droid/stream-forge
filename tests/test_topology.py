"""Topology tests — Week 2 R2.

Covers:
* Week 1 regression — celsius→fahrenheit map, topology_stage tag.
* Week 2 filter gates — physical bounds, strictly-positive gate, edge values.
* FilterReason classification — verifies the *specific* reason for rejection.
* Map/transform correctness — rounding, field propagation, source passthrough.
* process_event composition — both gates applied in correct order.
"""

from __future__ import annotations

import time

import pytest

from stream_forge_r2.schemas import TelemetryEventV1
from stream_forge_r2.topology import (
    FilterReason,
    TemperatureBounds,
    classify_event,
    filter_temp_positive,
    is_business_valid_temperature,
    process_event,
    transform_to_validated_event,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def make_event(temp: float, truck_id: str = "truck-0001", source: str = "unit-test") -> TelemetryEventV1:
    return TelemetryEventV1(
        truck_id=truck_id,
        temperature_c=temp,
        timestamp_ms=int(time.time() * 1000),
        source=source,
    )


# ---------------------------------------------------------------------------
# Week 1 regression
# ---------------------------------------------------------------------------

class TestWeek1Regression:
    def test_celsius_to_fahrenheit_conversion(self) -> None:
        out = process_event(make_event(10.0))
        assert out is not None
        assert out.temperature_f == 50.0

    def test_topology_stage_is_validated(self) -> None:
        out = process_event(make_event(10.0))
        assert out is not None
        assert out.topology_stage == "validated"

    def test_physical_bounds_filter_still_applied(self) -> None:
        # 121 °C is above the default 120 °C ceiling
        out = process_event(make_event(121.0), TemperatureBounds(min_c=-50, max_c=120))
        assert out is None


# ---------------------------------------------------------------------------
# Week 2 — filter_temp_positive gate
# ---------------------------------------------------------------------------

class TestFilterTempPositive:
    def test_positive_temp_passes(self) -> None:
        assert filter_temp_positive(make_event(0.1)) is True

    def test_zero_temp_rejected(self) -> None:
        assert filter_temp_positive(make_event(0.0)) is False

    def test_negative_temp_rejected(self) -> None:
        assert filter_temp_positive(make_event(-1.0)) is False

    def test_large_positive_passes(self) -> None:
        assert filter_temp_positive(make_event(119.9)) is True


# ---------------------------------------------------------------------------
# Week 2 — physical bounds gate (edge cases)
# ---------------------------------------------------------------------------

class TestPhysicalBoundsEdgeCases:
    def test_exactly_at_min_bound_passes(self) -> None:
        bounds = TemperatureBounds(min_c=-50.0, max_c=120.0)
        assert is_business_valid_temperature(make_event(-50.0), bounds) is True

    def test_exactly_at_max_bound_passes(self) -> None:
        bounds = TemperatureBounds(min_c=-50.0, max_c=120.0)
        assert is_business_valid_temperature(make_event(120.0), bounds) is True

    def test_just_below_min_rejected(self) -> None:
        bounds = TemperatureBounds(min_c=-50.0, max_c=120.0)
        assert is_business_valid_temperature(make_event(-50.01), bounds) is False

    def test_just_above_max_rejected(self) -> None:
        bounds = TemperatureBounds(min_c=-50.0, max_c=120.0)
        assert is_business_valid_temperature(make_event(120.01), bounds) is False

    def test_custom_bounds_respected(self) -> None:
        narrow = TemperatureBounds(min_c=10.0, max_c=30.0)
        assert is_business_valid_temperature(make_event(5.0), narrow) is False
        assert is_business_valid_temperature(make_event(20.0), narrow) is True


# ---------------------------------------------------------------------------
# Week 2 — FilterReason classification (edge-case diagnostics)
# ---------------------------------------------------------------------------

class TestClassifyEvent:
    def test_passing_event_classified_as_pass(self) -> None:
        assert classify_event(make_event(25.0)) == FilterReason.PASS

    def test_above_max_bounds_classified_as_out_of_bounds(self) -> None:
        assert classify_event(make_event(121.0)) == FilterReason.OUT_OF_BOUNDS

    def test_below_min_bounds_classified_as_out_of_bounds(self) -> None:
        assert classify_event(make_event(-51.0)) == FilterReason.OUT_OF_BOUNDS

    def test_zero_temp_classified_as_non_positive(self) -> None:
        assert classify_event(make_event(0.0)) == FilterReason.NON_POSITIVE

    def test_negative_temp_within_bounds_classified_as_non_positive(self) -> None:
        # -10 is within physical bounds (-50..120) but fails positivity gate
        assert classify_event(make_event(-10.0)) == FilterReason.NON_POSITIVE

    def test_boundary_max_positive_classified_as_pass(self) -> None:
        assert classify_event(make_event(120.0)) == FilterReason.PASS

    def test_custom_bounds_used_in_classification(self) -> None:
        narrow = TemperatureBounds(min_c=10.0, max_c=30.0)
        # 5.0 is positive but below narrow min → OUT_OF_BOUNDS, not NON_POSITIVE
        assert classify_event(make_event(5.0), narrow) == FilterReason.OUT_OF_BOUNDS


# ---------------------------------------------------------------------------
# Week 2 — Map / transform stage
# ---------------------------------------------------------------------------

class TestTransformToValidatedEvent:
    def test_fahrenheit_formula_correct(self) -> None:
        out = transform_to_validated_event(make_event(0.0))
        assert out.temperature_f == 32.0

    def test_temperature_rounded_to_two_decimal_places(self) -> None:
        out = transform_to_validated_event(make_event(37.123456))
        assert out.temperature_c == 37.12
        assert out.temperature_f == round((37.123456 * 9 / 5) + 32, 2)

    def test_truck_id_propagated(self) -> None:
        out = transform_to_validated_event(make_event(20.0, truck_id="truck-XYZ"))
        assert out.truck_id == "truck-XYZ"

    def test_source_propagated(self) -> None:
        out = transform_to_validated_event(make_event(20.0, source="integration-test"))
        assert out.source == "integration-test"

    def test_topology_stage_tag(self) -> None:
        out = transform_to_validated_event(make_event(20.0))
        assert out.topology_stage == "validated"


# ---------------------------------------------------------------------------
# Week 2 — process_event composition (both gates + map)
# ---------------------------------------------------------------------------

class TestProcessEventComposition:
    def test_valid_event_passes_both_gates_and_is_mapped(self) -> None:
        out = process_event(make_event(50.0))
        assert out is not None
        assert out.temperature_c == 50.0

    def test_zero_temp_dropped_by_positivity_gate(self) -> None:
        out = process_event(make_event(0.0))
        assert out is None

    def test_negative_temp_within_physical_bounds_dropped(self) -> None:
        # -10 satisfies physical bounds but fails positivity gate
        out = process_event(make_event(-10.0))
        assert out is None

    def test_above_max_bounds_dropped(self) -> None:
        out = process_event(make_event(200.0))
        assert out is None

    def test_custom_bounds_override_default(self) -> None:
        narrow = TemperatureBounds(min_c=10.0, max_c=30.0)
        assert process_event(make_event(25.0), narrow) is not None
        assert process_event(make_event(5.0), narrow) is None
        assert process_event(make_event(35.0), narrow) is None

    def test_exactly_at_lower_positive_boundary(self) -> None:
        # 0.001 is the smallest float > 0 that clears the positivity gate
        out = process_event(make_event(0.001))
        assert out is not None

    def test_multiple_trucks_processed_independently(self) -> None:
        events = [make_event(t, truck_id=f"truck-{i:04d}") for i, t in enumerate([5.0, 0.0, -5.0, 80.0])]
        results = [process_event(e) for e in events]
        assert results[0] is not None   # 5.0  → pass
        assert results[1] is None       # 0.0  → dropped (non-positive)
        assert results[2] is None       # -5.0 → dropped (non-positive)
        assert results[3] is not None   # 80.0 → pass
