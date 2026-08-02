.PHONY: install test lint typecheck format create-topics produce-samples consume run-bytewax clean

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src tests scripts

typecheck:
	mypy src tests

format:
	ruff format src tests scripts
	ruff check --fix src tests scripts

create-topics:
	docker exec -it stream-forge-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic truck.telemetry.raw --partitions 6 --replication-factor 1
	docker exec -it stream-forge-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic truck.telemetry.validated --partitions 6 --replication-factor 1

produce-samples:
	PYTHONPATH=src python scripts/produce_sample_events.py --count 20

consume:
	PYTHONPATH=src python -m stream_forge_r2.consumer

run-bytewax:
	PYTHONPATH=src python -m bytewax.run stream_forge_r2.bytewax_flow:flow

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
