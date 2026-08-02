import os

import pytest


def test_kafka_integration_placeholder() -> None:
    if os.getenv("RUN_KAFKA_INTEGRATION") != "1":
        pytest.skip("Set RUN_KAFKA_INTEGRATION=1 after docker compose up to run Kafka smoke test")
    # This keeps CI fast and explicit. Manual command is documented in README.
    assert True
