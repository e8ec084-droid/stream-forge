# Topic schema contract

## Input topic

`truck.telemetry.raw`

Owned by R1 producer. Consumed by R2 stream topology worker.

```json
{
  "schema_version": "1.0",
  "truck_id": "truck-0001",
  "temperature_c": 21.5,
  "timestamp_ms": 1722297600000,
  "source": "mock-generator"
}
```

### Field rules

| Field | Type | Rule |
|---|---|---|
| schema_version | string | Must be `1.0` |
| truck_id | string | 3 to 64 chars, letters, numbers, `_`, `-` only |
| temperature_c | float | Hard schema range: -100 to 200 |
| timestamp_ms | integer | Epoch milliseconds, after 2020-01-01 |
| source | string | Producer/source name |

## Output topic

`truck.telemetry.validated`

Produced by R2. Consumed by R3/R4 in later weeks.

```json
{
  "schema_version": "1.0",
  "truck_id": "truck-0001",
  "temperature_c": 21.5,
  "temperature_f": 70.7,
  "timestamp_ms": 1722297600000,
  "source": "mock-generator",
  "topology_stage": "validated"
}
```

## Business filter

Default R2 filter keeps events where:

```text
-50 <= temperature_c <= 120
```

Anything outside this range is treated as business-invalid and dropped from the validated output topic.
