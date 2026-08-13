# Metrics Taxonomy

Defined once in `src/stream_forge_r5/metrics.py`, reused everywhere else.

| Metric | Type | Labels | What it tells you |
|---|---|---|---|
| `stream_forge_events_produced_total` | Counter | `topic` | Successful producer deliveries |
| `stream_forge_events_consumed_total` | Counter | `topic` | Events a worker pulled off Kafka |
| `stream_forge_events_invalid_total` | Counter | `topic`, `reason` | Schema/JSON failures |
| `stream_forge_events_filtered_total` | Counter | `topic` | Events dropped by business rules |
| `stream_forge_consumer_lag` | Gauge | `topic`, `partition` | High watermark − committed offset |
| `stream_forge_broker_up` | Gauge | `bootstrap_server` | 1/0 broker reachability |
| `stream_forge_produce_latency_seconds` | Histogram | `topic` | produce() → delivery callback time |

## Why these seven and not more

Each metric maps to one specific audit or chaos-test requirement in the
workload chart (throughput target, lag threshold, broker health check,
rejection rate). Metrics that don't back a concrete alert or audit weren't
added — an unused metric is a maintenance cost with no payoff.

## Why Counter vs Gauge vs Histogram

- **Counter**: only ever goes up (events produced, consumed, rejected) —
  matches Prometheus's counter semantics exactly, so `rate()` works for free.
- **Gauge**: can go up or down (lag shrinks and grows, broker flips up/down).
- **Histogram**: `produce_latency_seconds` needs percentiles, not just a
  sum — that's what histograms are for.
