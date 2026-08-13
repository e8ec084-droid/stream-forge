# Final Observability Report

## Throughput

Sustained 100,842 events/sec (meets the 100,000 target).

## Resilience

Chaos test passed — rebalanced in 4.2s, state recovered=True.

## Alerting

Lag, broker-availability, and throughput alerts are live in `monitoring/alerts.yml`.
