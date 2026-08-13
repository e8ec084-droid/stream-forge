from unittest.mock import patch

from stream_forge_r5.chaos import (
    run_chaos_test,
    verify_state_recovered,
    wait_for_partition_rebalance,
)


class FakeRegistry:
    """Reports worker-5 as the owner from the very first poll — rebalance already happened."""

    def owner_of(self, partition: int) -> str:
        return "worker-5"


class NeverRebalancingRegistry:
    def owner_of(self, partition: int) -> str:
        return "worker-4"


def test_wait_for_partition_rebalance_detects_immediate_success() -> None:
    rebalanced, elapsed = wait_for_partition_rebalance(
        FakeRegistry(), partition=3, expected_owner="worker-5"
    )

    assert rebalanced is True
    assert elapsed >= 0


def test_wait_for_partition_rebalance_times_out() -> None:
    with patch("stream_forge_r5.chaos.chaos_test.sleep", lambda seconds: None):
        rebalanced, _ = wait_for_partition_rebalance(
            NeverRebalancingRegistry(),
            partition=3,
            expected_owner="worker-5",
            timeout_seconds=0.0,
            poll_interval_seconds=0.0,
        )

    assert rebalanced is False


def test_verify_state_recovered_within_tolerance() -> None:
    assert verify_state_recovered(before=72.5, after=72.6, tolerance=0.01) is True


def test_verify_state_recovered_outside_tolerance() -> None:
    assert verify_state_recovered(before=72.5, after=90.0, tolerance=0.01) is False


def test_run_chaos_test_end_to_end() -> None:
    with (
        patch("stream_forge_r5.chaos.chaos_test.subprocess.run"),
        patch("stream_forge_r5.chaos.chaos_test.sleep", lambda seconds: None),
    ):
        result = run_chaos_test(
            registry=FakeRegistry(),
            target_pid=1234,
            target_worker="worker-4",
            failover_worker="worker-5",
            partition=3,
            rolling_average_before=72.5,
            rolling_average_after_recovery=72.6,
        )

    assert result.rebalanced is True
    assert result.state_recovered is True
    assert result.partition == 3
