"""Bytewax topology scaffold for Week 2 expansion.

Week 1 requires selecting the framework and scaffolding the worker. This file keeps the
Bytewax dataflow shape ready for the Week 2 Consume -> Filter -> Map work.
"""

from bytewax.dataflow import Dataflow

flow = Dataflow("stream-forge-r2-topology")

# The KafkaSource/KafkaSink wiring is intentionally completed in Week 2 after R1 finalizes
# partition count, producer contract, and target throughput. The pure topology logic is already
# implemented and tested in topology.py so it can be reused here without changing business logic.
