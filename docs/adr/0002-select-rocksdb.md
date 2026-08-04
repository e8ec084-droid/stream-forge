# ADR 0002 - Select RocksDB for Local State Storage

## Status

Accepted

---

## Context

Role 4 (State & Fault-Tolerance Engineer) requires persistent local state storage for processing truck telemetry events.

The state store must:

- Persist data across application restarts
- Support fast key-value lookups
- Scale to large numbers of truck records
- Be embeddable inside a Python application
- Require minimal runtime infrastructure

---

## Options Considered

### Option 1 - RocksDB

**Pros**

- High-performance embedded key-value database
- Excellent write throughput
- Persistent storage
- Widely used in streaming systems
- Good fit for stateful event processing

**Cons**

- Python bindings may require native compilation on some platforms.

---

### Option 2 - SQLite

**Pros**

- Easy to install
- Built into Python
- Persistent

**Cons**

- Relational database
- Less suitable for very high write throughput
- Not designed specifically for streaming state

---

### Option 3 - Redis

**Pros**

- Very fast
- Easy API

**Cons**

- Requires running a separate server
- Primarily in-memory
- Adds operational complexity

---

## Decision

RocksDB is selected because it provides durable embedded key-value storage with high write performance and minimal runtime dependencies.

Its architecture aligns well with stateful stream processing and fault-tolerant event pipelines.

---

## Consequences

### Advantages

- Persistent local state
- Fast reads and writes
- Supports crash recovery

### Trade-offs

- Python bindings can be platform dependent.
- Requires additional setup compared with SQLite.

---

## Owner

Role 4 — State & Fault-Tolerance Engineer