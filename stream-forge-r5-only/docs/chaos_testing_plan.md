# Chaos Testing Plan (for Week 3)

## Scenario

Kill `worker-4` mid-calculation while it owns a partition, and verify the
pipeline recovers with zero data loss — the exact failure mode described in
the Stream Forge use case ("If Worker Node #4 crashes... rebalances the
partition to Worker #5... recovers its state from a RocksDB changelog").

## Steps

1. **Design** — pick a target worker/partition pair and record the rolling
   average *before* the crash (`ChaosResult` captures this as
   `rolling_average_before`).
2. **Kill** — send `SIGKILL` to the worker process (`chaos.kill_worker`).
   `SIGKILL`, not `SIGTERM`, because the use case says "crashes", not
   "shuts down gracefully" — we're testing the unrecoverable-process path.
3. **Verify rebalance** — poll the worker registry until the partition is
   owned by `worker-5` or a timeout elapses (`chaos.wait_for_partition_rebalance`).
4. **Verify state** — compare the rolling average before vs. after recovery
   within a small tolerance (`chaos.verify_state_recovered`).
5. **Automate** — `chaos.run_chaos_test` runs steps 2-4 in one call so the
   whole scenario can be re-run in CI, not just once by hand.

## Pass criteria

- Partition ownership moves to the failover worker within
  `CHAOS_REBALANCE_TIMEOUT_SECONDS` (default 30s).
- The rolling average after recovery is within 1% of its pre-crash value.

## Why a `Protocol` for the worker registry

`chaos.py` has no import of whatever R1/R4 use to track partition
ownership — it depends on a `WorkerRegistry` protocol (anything with an
`owner_of(partition) -> str` method). That means this module can be tested
today with a fake registry, and wired to the real one later without any
changes to `chaos.py` itself.
