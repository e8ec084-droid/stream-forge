# Week 2 — R2 Stream Topology Engineer: Completion Report

## Summary
All five Week 2 deliverables completed. The Bytewax dataflow is now a full
`Consume → Filter(Temp > 0) → Map → Produce` pipeline wired to live Kafka topics.

---

## Deliverables

### Monday — Implement Consume → Filter(Temp > 0) → Map graph (`bytewax_flow.py`)
- Wired `KafkaSource` reading from `truck.telemetry.raw`
- Used `op.filter_map` for a single-pass filter + map operator (no separate filter step)
- Returns `None` from mapper to silently drop rejected records (idiomatic Bytewax)
- Wired `KafkaSink` producing to `truck.telemetry.validated` with idempotent producer config

### Tuesday — Filtering logic edge cases (`topology.py`)
- Added `filter_temp_positive()` — strictly `> 0 °C` gate (zero = sensor fault)
- Added `FilterReason` enum (`PASS`, `OUT_OF_BOUNDS`, `NON_POSITIVE`) for diagnostic classification
- Added `classify_event()` helper so R3/R5 can instrument drop counters by reason
- Both gates compose in `process_event()` — Gate 1: physical bounds, Gate 2: positivity

### Wednesday — Map / transform stage (`topology.py`)
- `transform_to_validated_event()` is the explicit map stage; now documented separately
- Fahrenheit conversion: `(temp_c * 9/5) + 32`, rounded to 2 d.p.
- `topology_stage = "validated"` literal tag — consumed by R6 dashboard DAG node colouring
- All original fields (`truck_id`, `source`, `timestamp_ms`) propagated unchanged

### Thursday — Wire topology output to downstream topic (`bytewax_flow.py`)
- `KafkaSink` keyed on `truck_id` bytes → preserves per-truck partition ordering
- Producer config: idempotent, `acks=all`, batched (`linger.ms=20`, `batch.num.messages=1000`)
- `build_flow()` factory accepts explicit overrides for all Kafka coordinates → fully testable

### Friday — Code review & refactor (`topology.py`, `bytewax_flow.py`, `config.py`)
- `consumer_group` bumped to `stream-forge-r2-week2` to avoid offset collision with Week 1
- Extracted `build_flow()` factory; module-level `flow = build_flow()` kept for Bytewax runner
- All inline comments reference design decisions and cross-role contracts (R1 partition key, R3 aggregation, R6 stage tag)
- Week 1 backward compatibility preserved: `process_event()` signature unchanged

---

## Test Coverage (`tests/test_topology.py`)

| Class | Tests | What it covers |
|---|---|---|
| `TestWeek1Regression` | 3 | Fahrenheit conversion, stage tag, bounds filter |
| `TestFilterTempPositive` | 4 | zero, negative, positive, large-positive |
| `TestPhysicalBoundsEdgeCases` | 5 | exact min/max, just-below/above, custom bounds |
| `TestClassifyEvent` | 7 | all three FilterReason outcomes, ordering, custom bounds |
| `TestTransformToValidatedEvent` | 5 | formula, rounding, field propagation, stage tag |
| `TestProcessEventComposition` | 7 | gate composition, boundary values, multi-truck |
| **Total** | **31** | |

---

## Files Changed

| File | Change |
|---|---|
| `src/stream_forge_r2/bytewax_flow.py` | Full implementation (was scaffold stub) |
| `src/stream_forge_r2/topology.py` | Added `filter_temp_positive`, `FilterReason`, `classify_event` |
| `src/stream_forge_r2/config.py` | Consumer group bumped to `week2` |
| `tests/test_topology.py` | Expanded from 2 tests to 31 |
| `docs/week2_r2_completion_report.md` | This document |
