# Stream Forge, R2 Week 1

Professional intern deliverable for **R2: Stream Topology Engineer**.

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
