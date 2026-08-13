"""Chaos-testing toolkit (Week 3): kill a worker and verify the pipeline self-heals.

The Week 3 tasks are four small steps that only make sense run in order —
design, verify rebalance, verify recovery, automate — so they're modeled as
four small functions plus one ``run_chaos_test`` that composes them. That
keeps each step independently testable while still giving you one call for
the automated version (Thursday's deliverable).

``WorkerRegistry`` is a ``Protocol`` rather than a concrete class so this
module has zero dependency on however R1/R4 actually track partition
ownership — any object with an ``owner_of`` method works, real or fake.
"""

import subprocess
from dataclasses import dataclass
from time import perf_counter, sleep
from typing import Protocol


class WorkerRegistry(Protocol):
    """Anything that can report which worker currently owns a partition."""

    def owner_of(self, partition: int) -> str: ...


@dataclass(frozen=True)
class ChaosResult:
    target_worker: str
    failover_worker: str
    partition: int
    rebalanced: bool
    state_recovered: bool
    rebalance_seconds: float


def kill_worker(pid: int) -> None:
    """Sends SIGKILL to simulate a hard crash, per the 'Worker #4 crashes' scenario."""
    subprocess.run(["kill", "-9", str(pid)], check=True)


def wait_for_partition_rebalance(
    registry: WorkerRegistry,
    partition: int,
    expected_owner: str,
    timeout_seconds: float = 30.0,
    poll_interval_seconds: float = 1.0,
) -> tuple[bool, float]:
    """Polls until the partition moves to ``expected_owner``, or the timeout is hit."""
    started_at = perf_counter()
    while perf_counter() - started_at < timeout_seconds:
        if registry.owner_of(partition) == expected_owner:
            return True, perf_counter() - started_at
        sleep(poll_interval_seconds)
    return False, perf_counter() - started_at


def verify_state_recovered(before: float, after: float, tolerance: float = 0.01) -> bool:
    """Confirms the rolling average survived the crash within a small floating-point tolerance."""
    return after == 0 if before == 0 else abs(after - before) / before <= tolerance


def run_chaos_test(
    registry: WorkerRegistry,
    target_pid: int,
    target_worker: str,
    failover_worker: str,
    partition: int,
    rolling_average_before: float,
    rolling_average_after_recovery: float,
    timeout_seconds: float = 30.0,
) -> ChaosResult:
    """Runs the full scenario end to end: kill -> wait for rebalance -> verify state.

    This is the automated version of the Monday-Thursday tasks: design lives
    in the function signature (which worker, which partition, what to
    verify), execution is the body, and the result is what Friday's report
    documents.
    """
    kill_worker(target_pid)
    rebalanced, rebalance_seconds = wait_for_partition_rebalance(
        registry, partition, failover_worker, timeout_seconds
    )
    state_recovered = verify_state_recovered(rolling_average_before, rolling_average_after_recovery)
    return ChaosResult(
        target_worker=target_worker,
        failover_worker=failover_worker,
        partition=partition,
        rebalanced=rebalanced,
        state_recovered=state_recovered,
        rebalance_seconds=rebalance_seconds,
    )
