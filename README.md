 # Stream Forge, R2 Week 1
Project: Stream Forge  
Domain: Distributed Systems and Big Data  
Stack focus: Kafka, Bytewax, JSON schemas, serializers, streaming worker scaffold

## What this delivers

Week 1 R2 tasks completed:

| Day | Assigned task | Deliverable |
|---|---|---|
| Monday | Evaluate Faust vs Bytewax and select framework | ADR selecting Bytewax with tradeoff notes |
| Tuesday | Scaffold streaming worker app and config | Python package, config layer, Docker Compose, Makefile |
| Wednesday | Define topic schemas and serializers | Versioned telemetry schema, strict validation, JSON serializers |
| Thursday | Build basic consumer connected to Kafka | Kafka consumer with validation and clean shutdown |
| Friday | Integration test consumer against producer | Unit tests plus optional Kafka smoke test |

## Architecture

```text
mock producer / R1 generator
        |
        v
Kafka topic: truck.telemetry.raw
        |
        v
R2 streaming worker
  1. deserialize JSON
  2. validate event schema
  3. filter invalid business values
  4. normalize into topology event
        |
        v
Kafka topic: truck.telemetry.validated
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
pytest
```

## Run Kafka locally

```bash
docker compose up -d
make create-topics
make produce-samples
make consume
```

## Run quality checks

```bash
make lint
make typecheck
make test
```

## Files to show in review

- `docs/adr/0001-select-bytewax.md`
- `docs/topic_schema.md`
- `docs/week1_completion_report.md`
- `src/stream_forge_r2/consumer.py`
- `src/stream_forge_r2/topology.py`
- `tests/`

## R4 State Store

The R4 state store uses RocksDB to persist the latest state for each truck.
The `RocksDBStore` provides persistent local state storage for stream
processing and supports recovery through a Kafka changelog.

### State Store Operations

- `put(state)` stores or updates a truck's current state.
- `get(truck_id)` retrieves the persisted state for a truck.
- `delete(truck_id)` removes a truck's persisted state.
- `put_window_result(...)` stores window-processing results.
- `write_changelog(state)` creates a changelog record for state recovery.
- `get_changelog(key)` retrieves a previously written changelog record.

### State Recovery

State changes are recorded in the Kafka changelog so that persisted state
can be reconstructed after a failure.

The recovery flow is:

Kafka changelog → `ChangelogRestorer` → `RocksDBStore` → restored state.

The changelog records support `upsert` and `delete` operations. The recovery
consumer reads records from the beginning of the changelog and applies them
to the RocksDB state store.

### Fault Tolerance

RocksDB provides local persistent state storage while the Kafka changelog
provides a recovery mechanism. This allows the state store to be rebuilt
from changelog records when required.