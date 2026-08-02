# Local runbook

## 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 2. Start Kafka

```bash
docker compose up -d
```

## 3. Create topics

```bash
make create-topics
```

## 4. Produce sample events

```bash
make produce-samples
```

## 5. Start consumer

```bash
make consume
```

## 6. Troubleshooting

| Issue | Check |
|---|---|
| Consumer cannot connect | Confirm `docker ps` shows `stream-forge-kafka` |
| Topic not found | Run `make create-topics` |
| No messages consumed | Run `make produce-samples` again |
| Import errors | Run commands with `PYTHONPATH=src` or install with `pip install -e .` |
