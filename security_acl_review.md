# Stream Forge: Kafka ACL Security Review
**Role:** Role 1 (Kafka Infrastructure Lead)
**Phase:** Week 4 (Production Readiness)

## 1. Current State Audit
The current local KRaft cluster is operating in `PLAINTEXT` mode for development and load-testing purposes. While optimal for benchmarking maximum throughput, this lacks the required Access Control Lists (ACLs) for a multi-tenant production environment.

## 2. Production ACL Requirements
To secure the `truck_telemetry` topic before cloud handoff, the following ACL bindings must be strictly enforced:

* **Producer Nodes (IoT Trucks):**
  * Allowed Operation: `WRITE`
  * Resource: Topic `truck_telemetry`
  * Network: Restricted to verified Edge Gateway IP ranges.
  
* **Stream Topology Workers (Role 2):**
  * Allowed Operation: `READ`
  * Resource: Topic `truck_telemetry`
  * Group ID: `stream-forge-consumer-group`

## 3. Security Recommendations
Before final deployment, the cluster must be upgraded from `PLAINTEXT` to `SASL_SSL`. This will encrypt the data in transit and allow us to enforce the ACLs using SCRAM-SHA-256 authentication for all connected truck producers.