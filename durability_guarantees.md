# Stream Forge: Kafka Durability Guarantees
**Role:** Role 1 (Kafka Infrastructure Lead)
**Phase:** Week 3 (Stateful Recovery & Chaos Testing)

## 1. Architecture Enhancements
To ensure strict zero-data-loss guarantees for the Stream Forge pipeline, the following configurations were successfully applied to the Kafka infrastructure:

* **Topic-Level Durability:** The `truck_telemetry` topic was updated to enforce `min.insync.replicas=1`. This guarantees that the broker must explicitly acknowledge writing the data to its log before accepting new messages.
* **Producer-Level Acknowledgments:** The producer was upgraded with `acks=all`. This forces the producer to wait for full confirmation from the broker, ensuring data is fully committed.
* **Network Fault Tolerance:** Implemented a `retries=5` policy with exponential backoff.

## 2. Validation of Broker Restart (No Data Loss)
During active telemetry ingestion, the Kafka broker was intentionally shut down (simulating a severe node crash) and subsequently restarted. 

**Results:**
* The producer immediately detected the broken connection and entered a safe retry state.
* **Zero data was dropped** during the outage window.
* Upon broker restart, the producer successfully re-established the connection and flushed all pending telemetry data to the topic.
* Validation confirmed complete data integrity and continuity.